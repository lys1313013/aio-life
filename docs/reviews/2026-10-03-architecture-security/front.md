# Front 架构审查（2026-10-03）

结论：整体分层合理，保留 Vben monorepo、应用 adapter、业务 API 层和按领域组织的页面即可，不需要重写。近期公共弹窗统一、请求字段白名单、对象存储的异步状态保护方向正确。当前风险主要在跨组件契约没有端到端收口、菜单初始化存在多个实现、部分新页面缺少竞态保护，以及已有测试未进入远端交付门禁。发现 3 个 P2 功能缺陷和 1 个 P2 验证门禁缺口；本专项没有确认 P1。安全专项独立审查，本文不把客户端问题等同于服务端越权。

## 基线与审查范围

- 仓库：`/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front`。
- 启动与收尾 HEAD：`6e54d52564753207ee51274ef57d1a5c6f3908b1`，业务仓库工作区均干净。
- 近期窗口：2026-09-28 至审查时；比对前基线 `83460793eea09692d3ee95dbd5e6e7fedfc0e704`；范围累计 192 文件、9,424 行新增、2,336 行删除。
- 阅读仓库 AGENTS.md，结合 git log/diff/blame 检查近期最小字段契约、公共弹窗与回车保存、首页迁移、菜单颜色、时迹、公共卡面和对象存储变更，并追踪关联状态/路由实现。
- 仅只读业务源码；没有修复、提交、推送、部署、读取真实凭据或调用真实业务写接口。

## P2-1：字符串菜单 ID 迁移未贯通二级锁调用端

**证据**

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/store/secondary-lock.ts:35`：接口 ID 用 `String` 装入 `Set<string>`；54–55 行以 `String(menuId)` 查找。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/router/guard.ts:104` 与 `:159`：调用前仍执行 `Number(menuId)`。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/views/_core/profile/secondary-password-setting.vue:60`、`:69`、`:75`：菜单树、已选项、保存参数均转换为 Number。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/api/core/auth.ts:193` 附近的锁菜单响应仍声明 `number[]`；`packages/@core/base/typings/src/menu-record.ts:54` 附近仍将 menuId 声明为 number。

**触发与影响**：当菜单 ID 超过 JavaScript 安全整数范围且不可精确表示时，例如 `9007199254740993`，路由守卫检查的是 `9007199254740992`，已锁菜单不能在页面进入之前被正确识别；设置页也可能把取整后的错误菜单 ID 发给后端。正常小 ID 不触发。服务端另有按用户及路径的二级锁校验，因此不能据此宣称 API 鉴权绕过；前端缓存页/提示行为及配置正确性仍受影响。

**本地复现**：从现有 store 源文件抽取并执行真实 `isMenuLocked` 函数，以 `Set(['9007199254740993'])` 初始化；直接字符串传入返回 true，使用守卫现有 Number 转换后返回 false。无生产数据。

**建议**：统一 API 响应、MenuRecordRaw、route meta、Tree key 和保存参数为 string；去掉整条菜单链路的 Number 转换。给守卫与二级锁设置页增加同一大整数 ID 的完整往返测试。

**近期新增性/置信度**：高。Number 转换是 2026-07/08 的既有代码；`b07947d72`（2026-10-02）将 store 改为精确字符串后，旧调用端与新 store 的不一致是近期回归；设置页取整是历史遗留。现有 `router/guard.test.ts:50–54` 把 `isMenuLocked` 固定 mock 为 false，因此首页迁移测试无法发现该问题。

## P2-2：菜单修改后的路由重建遗漏偏好处理，失败时先破坏现有路由

**证据**

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/views/system/menu/index.vue:295–307`：先 resetRoutes，再等待 generateAccess，随后直接发布 accessibleMenus。
- 同文件 `:422`、`:437`、`:507`、`:529`：保存、状态切换、排序、删除都会执行这条刷新链路。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/router/guard.ts:123–147`：正常初始化还会加载显示偏好、附加二级锁标记并 filterVisibleMenus。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/views/_core/profile/menu-display-setting.vue:118–133`：偏好修改处又维护一份菜单重建逻辑。

**触发与影响**：管理员隐藏部分菜单后修改任一菜单，管理页会用未经偏好过滤的完整菜单覆盖导航，原先隐藏项重新出现，锁图标也丢失。若 mutation 成功，但接着 `/menu/all` 请求失败，动态路由已被删除，`isAccessChecked` 仍为 true，后续导航不会走首次加载分支来自愈，可能落入 404，需刷新恢复。

**本地复现**：直接抽取现有 `refreshAccessibleMenus` 执行，模拟 generateAccess 拒绝后，结果为 routes=[]、旧 menus 保留、checked=true；成功路径直接保存 raw menus，未应用任何显示偏好或锁标记。此为源函数级状态复现，未运行浏览器集成场景。

**建议**：应用层建立唯一的导航刷新函数，覆盖首次初始化、管理修改及偏好修改：先读取所需远端数据和偏好，生成可用快照，再替换路由及 store；失败保留旧快照。不要把业务偏好塞入框架通用 generateAccessible。补充菜单修改后隐藏偏好保持、刷新失败路由仍可用两类回归。

**近期新增性/置信度**：历史遗留，高。refreshAccessibleMenus 经 blame 溯源为 2026-04-30；近期菜单颜色/导航变更继续复用该分叉链路，并非这几天新增的代码行。

## P2-3：公共卡面管理旧列表响应可覆盖刚完成的删除或状态修改

**证据**

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/src/views/system/bank-card-covers/index.vue:91–101`：load 等待两项 Promise.all 后无版本检查地整体替换 items。
- 同文件 `:137–151`：toggle/remove 在独立忙状态下更新本地 items；`:196` 刷新按钮不考虑这些 mutation 的 busy 状态。
- 作为对照，`apps/web-antd/src/views/system/storage/index.vue:62–89` 已用 generation 和 deletionVersions 处理同一类陈旧响应，且已有对应测试。

**触发与影响**：删除请求发出后点击刷新，GET 得到删除前快照，但其响应（或同时请求的银行列表）延迟；删除先成功并移除卡片，稍后的旧列表又把已删除卡面显示出来。切换启停状态也会被旧快照回滚展示，用户可能据过期状态继续操作。服务端数据并未复活，是客户端状态与真实数据不一致。

**本地复现**：直接抽取当前 load/remove 函数，以延迟 Promise 模拟旧列表；删除后 items=[]，放行旧列表后 items=['A']。没有改动源码，也没有真实删除对象。

**建议**：复用对象存储的请求代数和 mutation 版本模式，或在 mutation 成功时使此前读取失效，并确保冲突查询可恢复；只使用一个 loading 布尔值不能解决读写并发。至少补删除/启停与刷新交错的延迟响应测试。

**近期新增性/置信度**：近期新增，高；此页面由 `e06535b9b`（2026-10-02）引入。

## P2-4：远端交付链路没有执行已有单测、类型与契约检查

**证据**

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/.github/workflows/docker.yml:52–66`：安装依赖后直接 build，并准备推送镜像；当前 `.github/workflows/` 仅此工作流。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/apps/web-antd/package.json:19`：build 是 Vite build；`:24` 的 vue-tsc 为独立 typecheck 脚本。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/turbo.json:16` 附近：build 只依赖 ^build，不依赖 typecheck/test。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-front/lefthook.yml:4–7`：pre-push 仅本地 typecheck，没有单测；且本地 hook 不能作为 GitHub PR 的统一验证门禁。
- 合同生成检查位于主仓库 `/Users/hurry/Documents/GitHub/lys1313013/aio-life/scripts/generate-api-contracts.py`，需要三个仓库与前端工具链，当前 front 单仓 CI 不会自动执行。

**触发与影响**：这几天新增的弹窗、路由、契约和存储回归测试即使失败，现有 CI 仍可能成功构建和推送镜像。三个独立仓库的契约也可能在各自成功构建后发生漂移。这里是可确认的验证架构缺口，并非断言当前远端构建失败或线上已出现问题。

**建议**：front PR 工作流必须执行应用 typecheck 与受影响/关键单测；将契约 check 放到能显式 checkout 三端固定 revision 的整合工作流，或发布版本化 schema，再让消费仓校验其锁定版本。避免在单仓 CI 隐式依赖开发者机器上的相邻目录。

**近期新增性/置信度**：历史门禁缺口，高；docker workflow 最近相关提交为 2026-09-12，近期大批增改扩大了未受门禁保护的范围。

## 分层评价与后续重构范围

- **保留现有 monorepo**：应用业务主要位于 apps/web-antd；此次 packages 修改集中在通用菜单显示、Enter 提交、弹窗和路由挂载。未发现仅因近期改动而必须拆仓/换框架的证据。
- **公共 UI 边界可继续使用**：AppModal 管理 busy、关闭、回车与 footer；应用 useVbenModal adapter 保留 Vben 生命周期并统一默认值，避免每页重写交互。48 项定向测试包含这部分现有行为，结果见下。
- **API 方向正确但还不是完整静态契约**：pickPayload 递归白名单保留 null、false、0、[]，本次生成结果与后端一致。生成器目前把所有请求字段都生成为 optional/null，Query 和多处响应仍存在 any，类型检查不能独立证明必填参数、VO 字段和全部 ID 链路。建议逐步从后端校验注解生成必填属性及查询/响应类型；优先改近期活跃模块，不必一次重命名所有 Entity 类型。
- **业务逻辑只在有共享语义时提取**：优先提取导航刷新、请求竞态保护和实体更新规则；不以 TimeSlotEditForm 或其他页面行数长为由硬拆文件。当前时迹数据加载/编辑已有领域 types/utils/category-tree，可沿现有边界演进。
- **缓存/资源治理有可复用实践**：对象存储 generation、删除版本和卸载资源清理，鉴权图片缓存的并发合并及退出清理值得继续复用；本报告没有据此宣称所有 KeepAlive/真实设备路径已验证。

建议顺序：先修 P2-1～3 并建立对应回归；紧接着补 P2-4 的 CI 门禁；之后按领域增量完善 Req/Query/VO 类型和导航服务边界。无需开展大范围架构迁移。

## 执行验证与边界

执行命令：

```sh
# front 仓库，定向测试；没有全量测试或构建
pnpm exec vitest run \
  apps/web-antd/src/api/payload.test.ts \
  apps/web-antd/src/router/guard.test.ts \
  apps/web-antd/src/components/app-modal/AppModal.test.ts \
  apps/web-antd/src/views/system/storage/index.test.ts \
  apps/web-antd/src/views/time/time-tracker/components/TimeSlotEditForm.test.ts

# 主仓库，只检查，不改文件
python3 scripts/generate-api-contracts.py --check
```

结果：5 个测试文件、48 项测试全部通过；契约检查报告 `117 request models, 134 body routes, 144 GET routes`，`Contracts match backend.`。另外通过 Node + TypeScript transpile + vm 执行源文件抽取函数，用纯内存 mock 复现 P2-1～3 的关键状态。现有测试通过不覆盖上述新增复现路径。

未执行：全量 lint/typecheck/build、真实浏览器交互、线上 API/数据联调、远端 CI 状态检查、部署或微信真机登录。因此这是当前源码与定向本地测试层面的架构审查，不是线上全系统验收。
