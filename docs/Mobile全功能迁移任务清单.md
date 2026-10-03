# Mobile 全功能迁移任务清单

本清单跟踪 AIO Life Web 全功能向独立 Mobile 仓库的迁移，覆盖业务菜单、个人设置、管理员功能、公共组件和跨端验证。主 Agent 负责维护清单、派发、审查与集成；子 Agent 统一使用 `gpt-6.1-sol`。功能按移动端交互实现，保留 uni-app x Vapor 和 `.uvue`。

创建及最近更新日期：2026-10-01。当前阶段：三名 GPT-6.1 sol 子 Agent 已完成分批实现，业务源码已冻结，主 Agent 已完成源码及本地统一验收。已知菜单均有客户端路由；Web 构建、小程序构建、模拟交互、真实后端及真机各自记账。

## 任务管理规则

- 状态只使用：待核验、待派发、进行中、待审查、返工中、受阻、已完成。
- 派发前填写负责人、Agent 标识、任务编号、允许修改的文件范围、依赖与验收条件；不得仅在聊天中口头派发。
- 子 Agent 开始、回报、失败、受阻和结束时，主 Agent 同步更新本清单。恢复会话先读本文件，再核对工作区与 Agent 状态。
- 子 Agent 回报完成后先置为“待审查”。主 Agent 审查代码、功能和验证证据后才置为“已完成”。仅有入口、静态展示、Web 跳转或构建成功不算业务完成。
- 新发现的页面内操作、隐藏入口、权限差异和平台限制追加任务或子项，不得静默删减。取消或调整范围必须记录原因及用户决定。
- 当前最多同时运行 3 个子 Agent，由主 Agent 滚动派发。并行任务按业务目录隔离；共享文件同一时间仅指定一名写入者。
- `pages.json`、公共导航、公共组件、主题、请求层和依赖锁文件由主 Agent 或明确指定的公共基础负责人统一修改。业务 Agent 提交接入需求，避免相互覆盖。
- 所有仓库已有未提交改动必须保留。派发前记录基线及文件范围；提交与推送按各独立仓库分别处理。
- 阻塞必须写清原因、影响任务和下一步；停止的 Agent 所持任务必须重新排队。未经验证的真机和发布项目保持未完成，不用 Web 测试替代。

## 范围和证据来源

- Web 路由：`aio-life-front/apps/web-antd/src/router/routes/modules/`。
- 实际菜单机制：`aio-life-front/apps/web-antd/src/router/access.ts` 使用后端菜单；静态路由不是完整的线上菜单清单。
- 菜单种子：`aio-life-server/sql/2_ini_data/2_menu.sql`，以及微信读书、银行卡、操作日志与访问日志的增量 SQL。
- Web 业务页面：`aio-life-front/apps/web-antd/src/views/`。下文“Web 页面”均相对于此目录。
- 个人设置：`aio-life-front/apps/web-antd/src/views/_core/profile/index.vue`。
- Mobile 现状：`aio-life-mobile/src/pages.json`、`src/services/life-catalog.ts`、`src/services/navigation.ts`。
- 当前核对基于本地代码和初始化脚本，尚未读取线上菜单配置。脚本中仪表盘及时间看板停用；迁移与入口启用分开处理，保留服务端开关和权限。
- 密码管理、关系图谱等历史路径按页面功能去重，保留有效路径映射。观影与视频观看、阅读记录与微信读书分别迁移。

## 盘点和公共基础

| 编号 | 任务及验收目标 | 状态 | 负责人 |
|---|---|---|---|
| INV-01 | 核对前端、后端、移动端工作区基线及各级 AGENTS.md，记录已有改动和共享文件写入者 | 已完成 | 主 Agent |
| INV-02 | 交叉核对动态菜单、页面源码与隐藏入口，补全路径别名、权限及开关矩阵 | 已完成 | 主 Agent |
| INV-03 | 逐页列出操作、字段、API、附件、统计、导入导出及关联行为；形成可勾选的操作级子清单 | 已完成 | 主 Agent |
| BASE-01 | 在现有 AdaptiveModal 上统一编辑弹窗，覆盖居中、内容滚动、键盘、安全区、关闭及忙碌状态 | 已完成 | /root/mobile_foundation |
| BASE-02 | 复用普通按钮、图标按钮和悬浮按钮，统一 loading、禁用、防重复提交及可访问名称 | 已完成 | /root/mobile_foundation |
| BASE-03 | 统一确认弹窗，靠近触发按钮且不超出屏幕，覆盖取消、提交中、失败和再次操作 | 已完成 | /root/mobile_foundation |
| BASE-04 | 统一表单字段、校验、日期时间 picker、选择器、搜索筛选和分页或继续加载交互 | 已完成 | /root/mobile_foundation |
| BASE-05 | 统一局部加载、空状态、错误重试及下拉刷新；失败保留原数据、离页旧请求不覆盖新状态 | 已完成 | /root/mobile_foundation |
| BASE-06 | 统一鉴权、请求及错误处理；ID 为 string，成功码为 '0'，错误字段为 result | 已完成 | 主 Agent |
| BASE-07 | 统一附件上传、鉴权预览、绑定保留和删除；按业务专属接口处理平台差异 | 已完成 | 主 Agent |
| BASE-08 | 统一主题、安全区、状态栏和微信胶囊适配；手机、平板、桌面布局及至少 44px 点击区域 | 已完成 | /root/mobile_foundation |
| BASE-09 | 实现业务原生路由映射及回跳，兼容路径别名，联动菜单权限、隐藏设置和菜单锁 | 已完成 | 主 Agent |
| BASE-10 | 盘点图表和统计展示的公共需求，建立跨端复用方案，避免各模块重复实现 | 已完成 | /root/mobile_foundation |

业务任务依赖 INV-01 至 INV-03，以及实际需要的 BASE 子项。盘点可与公共组件设计并行；未确定组件接口和文件边界前，不派发相互依赖的页面实现。

## 业务页面

“待核验”表示已有移动端实现或映射，不代表与 Web 功能对齐。每一行均需满足后文统一验收条件；操作级子清单由 INV-03 补齐后再进入开发。

| 编号 | 菜单或功能 | Web 页面 | 状态 | 负责人 |
|---|---|---|---|---|
| HOME-01 | 主页 | dashboard/home/index.vue | 已完成 | 主 Agent |
| HOME-02 | 仪表盘工作台，当前仅映射到移动首页 | dashboard/workspace/index.vue | 已完成 | 主 Agent |
| TASK-01 | 待办 | task-center/todo/index.vue | 已完成 | /root/mobile_records |
| TASK-02 | 目标管理 | task-center/goal/index.vue | 已完成 | /root/mobile_records |
| TIME-01 | 时迹 | time/time-tracker/index.vue | 已完成 | 主 Agent |
| TIME-02 | 时间看板 | time/dashboard/index.vue | 已完成 | /root/mobile_foundation |
| TIME-03 | 我的分类 | time/time-tracker/category-config/index.vue | 已完成 | /root/mobile_foundation |
| TIME-04 | 分类管理，管理员 | time/time-tracker/admin/index.vue | 已完成 | /root/mobile_foundation |
| REC-01 | 运动 | my-hub/exercise/index.vue | 已完成 | /root/mobile_records |
| REC-02 | 运动分类配置 | my-hub/exercise/category-config/index.vue | 已完成 | /root/mobile_records |
| REC-03 | 视频观看 | my-hub/videoWatch/index.vue | 已完成 | /root/mobile_records |
| REC-04 | 观影 | my-hub/movie/index.vue | 已完成 | /root/mobile_records |
| REC-05 | 阅读记录 | my-hub/read-record/index.vue | 已完成 | /root/mobile_records |
| REC-06 | 微信读书 | my-hub/weread/index.vue | 已完成 | /root/mobile_records |
| REC-07 | 闪念 | my-hub/think/index.vue | 已完成 | /root/mobile_records |
| REC-08 | 笔记 | my-hub/memo/index.vue | 已完成 | /root/mobile_records |
| REC-09 | 活动 | my-hub/performance/index.vue | 已完成 | /root/mobile_records |
| REC-10 | 里程碑 | my-hub/milestone/index.vue | 已完成 | /root/mobile_records |
| REC-11 | 纪念日 | my-hub/anniversary/index.vue | 已完成 | /root/mobile_records |
| REC-12 | 荣誉中心 | my-hub/honor/index.vue | 已完成 | /root/mobile_records |
| REC-13 | 反馈中心 | my-hub/feedback/index.vue | 已完成 | /root/mobile_records |
| REL-01 | 关系图谱 | relationship/index.vue | 已完成 | /root/mobile_finance |
| SEC-01 | 密码管理 | password-manager/index.vue | 已完成 | 主 Agent |
| CODE-01 | GitHub | coding/github/index.vue | 已完成 | /root/mobile_finance |
| CODE-02 | LeetCode | coding/leetcode/index.vue | 已完成 | /root/mobile_finance |
| CODE-03 | CSDN | coding/csdn/index.vue | 已完成 | /root/mobile_finance |
| FIN-01 | 财务概览 | my-hub/finance-dashboard/index.vue | 已完成 | /root/mobile_finance |
| FIN-02 | 收入 | my-hub/income/index.vue | 已完成 | /root/mobile_finance |
| FIN-03 | 支出 | my-hub/expense/index.vue | 已完成 | /root/mobile_finance |
| FIN-04 | 账单导入 | my-hub/expense/import.vue | 已完成 | /root/mobile_finance |
| FIN-05 | 银行卡 | bank-card/index.vue | 已完成 | /root/mobile_finance |
| GOODS-01 | 设备墙 | my-hub/device/index.vue | 已完成 | /root/mobile_records |
| GOODS-02 | 衣柜 | wardrobe/index.vue | 已完成 | /root/mobile_foundation |
| MEMBER-01 | 会员 | membership/index.vue | 已完成 | /root/mobile_records |
| MSG-01 | 消息中心 | message/index.vue | 已完成 | /root/mobile_finance |
| MCP-01 | MCP 工具列表 | mcp/tools/index.vue | 已完成 | /root/mobile_finance |
| CONFIG-01 | 字典类型，管理员 | config-management/sysDictType/index.vue | 已完成 | /root/mobile_foundation |
| CONFIG-02 | 字典数据，管理员 | config-management/sysDictData/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-01 | 用户中心 | system/user/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-02 | 菜单管理 | system/menu/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-03 | 用户字典管理 | system/user-dict/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-04 | 反馈管理 | system/feedback/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-05 | 系统配置 | system/config/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-06 | 操作日志 | system/operation-log/index.vue | 已完成 | /root/mobile_foundation |
| ADMIN-07 | 访问日志 | system/access-log/index.vue | 已完成 | /root/mobile_foundation |
| ABOUT-01 | 关于，按移动端项目适配 | _core/about/index.vue | 已完成 | 主 Agent |

管理员功能遵守后端角色权限，在移动端提供合适的管理入口，不直接塞入所有用户的个人生活目录。入口组织调整不等于删减功能。

## 我的和全局功能

| 编号 | 功能与核对范围 | Web 参照 | 状态 | 负责人 |
|---|---|---|---|---|
| ME-01 | 基本设置 | _core/profile/base-setting.vue | 已完成 | 主 Agent |
| ME-02 | 账号绑定 | _core/profile/user-bind.vue | 已完成 | 主 Agent |
| ME-03 | 修改密码 | _core/profile/password-setting.vue | 已完成 | 主 Agent |
| ME-04 | 菜单显示 | _core/profile/menu-display-setting.vue | 已完成 | 主 Agent |
| ME-05 | 菜单锁 | _core/profile/secondary-password-setting.vue | 已完成 | 主 Agent |
| ME-06 | API Key | _core/profile/api-key-setting.vue | 已完成 | 主 Agent |
| ME-07 | 大模型配置 | _core/profile/llm-setting.vue | 已完成 | 主 Agent |
| ME-08 | MBTI 测试 | _core/profile/mbti-setting.vue | 已完成 | /root/mobile_foundation |
| ME-09 | CBTI 测试 | _core/profile/cbti-setting.vue | 已完成 | /root/mobile_foundation |
| ME-10 | 通知设置 | _core/profile/notification-setting.vue | 已完成 | 主 Agent |
| ME-11 | 系统设置，已有主题切换需核对其他项 | _core/profile/system-setting.vue | 已完成 | 主 Agent |
| GLOBAL-01 | 生活目录、搜索、常用功能编辑；业务入口替换为原生路由 | Mobile life 页面及 Web 快捷导航 | 已完成 | 主 Agent |
| GLOBAL-02 | 登录、验证码、注册与密码找回等实际认证入口，逐项核对现有 Mobile 登录页 | Web core 路由与认证页面，具体差异由 INV-03 确认 | 已完成 | /root/mobile_foundation |
| GLOBAL-03 | 登录态过期、退出登录、跨账号缓存隔离、权限拒绝和菜单锁回跳 | Web 认证、请求层、路由守卫及 Mobile session | 已完成 | 主 Agent |
| GLOBAL-04 | 首页快捷录入、计时、通知入口等非菜单操作的完整性 | Web 首页、布局与全局组件，具体子项由 INV-03 确认 | 已完成 | 主 Agent |

## 统一验收条件

以下条件应用于每个业务任务。不适用项必须说明原因；不能为了方便给原本可编辑的业务只做只读页面。

- [ ] 与 Web 操作级子清单逐项对齐，包括列表、搜索、筛选、排序、分页、详情、新增、编辑、删除，以及该页面实际存在的统计、导入导出、附件、批量操作和同步功能。
- [ ] API、字段、字符串 ID、权限、菜单锁、状态枚举和关联数据一致；更新不丢失附属字段。
- [ ] 按触屏组织页面，使用统一弹窗、按钮、确认、表单与加载组件；无依赖悬停或鼠标拖拽的唯一操作方式。
- [ ] 局部 loading、防重复提交、失败保留表单、错误重试、刷新结束和请求竞态处理正确。
- [ ] 手机、平板、桌面和深浅主题均检查；覆盖安全区、键盘遮挡、长内容滚动、弹窗关闭及至少 44px 点击区域。
- [ ] 必要的契约或回归测试通过，记录命令、结果和验证范围；仅使用明确的模拟数据。
- [ ] 主 Agent 审查通过，记录变更文件、证据及未解决问题。

时迹另需保留分钟闭区间、时间轴、日周月、分类层级、阅读与观影关联、运动明细，以及边界、重叠、全天已满、跨日期和跨月校验，遵循 Mobile AGENTS.md。

## 集成验证

| 编号 | 验证任务 | 状态 | 负责人 |
|---|---|---|---|
| QA-01 | 全量菜单与操作清单复核，确认无遗漏、占位页或以 Web 跳转冒充完成 | 已完成 | 主 Agent |
| QA-02 | 公共组件复用和文件变更审查，消除重复实现与交叉覆盖 | 已完成 | 主 Agent |
| QA-03 | 运行 npm test，核对契约及失败恢复回归 | 已完成 | 主 Agent |
| QA-04 | 运行 npm run test:e2e，覆盖关键流程、真实手势事件与响应式深浅主题 | 已完成 | 主 Agent |
| QA-05 | 运行 npm run build，验证 Web 构建 | 已完成 | 主 Agent |
| QA-06 | 运行 npm run build:weixin，验证微信小程序构建 | 已完成 | 主 Agent |
| QA-07 | 真实后端联调，使用明确授权的测试环境及数据，记录与模拟测试的区别 | 进行中 | 主 Agent |
| QA-08 | 微信开发者工具验证及平台差异复核 | 进行中 | 主 Agent |
| QA-09 | 微信真机验证，记录设备及结果 | 受阻 | 主 Agent |
| QA-10 | App Vapor 真机验证，记录 HBuilderX 版本、设备及结果 | 受阻 | 主 Agent |
| QA-11 | 核对原生入口、使用说明及 README；检查凭据、Token、真实 AppID 和用户截图未进入提交范围 | 已完成 | 主 Agent |
| QA-12 | 汇总各仓库改动、剩余问题与验收结果；提交、推送和发布状态分别报告 | 已完成 | 主 Agent |

编译、Web 模拟接口测试、真实后端联调、开发者工具、微信真机、App 真机、上传及发布分别记账。缺设备或环境时记录具体阻塞，不声称已通过。

## 批次和依赖安排

1. 盘点批次：INV-01 至 INV-03，核对已有实现，细化操作级清单。
2. 基础批次：优先 BASE-01 至 BASE-09，确定组件契约和导航接入方式；图表方案按相关模块需求同步推进。
3. 生活业务批次：按任务、记录、财务、物品、关系、编程等领域滚动派发，每次最多 3 个子 Agent；依赖共享能力时先完成对应基础任务。
4. 补齐批次：个人设置、管理端、消息、MCP，以及主页和时迹差异；菜单锁等被前序业务依赖的能力提前安排。
5. 集成批次：QA-01 至 QA-12；发现问题回到原任务置为“返工中”，修复后重新验收受影响范围。

## 派发与验收记录

第一批派发已登记，详见下表。每次派发按下面模板追加，任务总表同步更新。执行证据保留在本文件或链接到具体的仓库文档及测试产物，不依赖聊天记忆。

```text
派发编号：
关联任务编号：
负责人和 Agent 标识：
模型：gpt-6.1-sol
状态：
派发时间和最近更新时间：
依赖任务及其状态：
工作区基线和已有改动：
允许修改的目录或文件：
共享文件接入需求：
Web 操作与 API 子清单：
本次验收条件：
变更文件和验证命令：
验证结果及证据路径：
阻塞或剩余问题：
主 Agent 审查结论：
下一步：
```

## 更新记录

- 2026-10-01：建立迁移任务台账，纳入此前列出的业务菜单和 11 项个人设置，补充盘点、公共基础、全局功能、集成验证及派发记录模板。原有实现统一标为待核验；尚未派发开发或声称业务验收完成。

### 第一批派发

基线：[工作区基线](./mobile-migration/baseline.md)。所有子 Agent 使用 gpt-6.1-sol，主 Agent 统一维护总表及 pages.json、导航、请求层和全局样式。

| 派发编号 | Agent 标识 | 任务范围 | 允许修改范围 | 依赖与验收 | 状态 |
|---|---|---|---|---|---|
| W1-A | /root/mobile_foundation | BASE-01 至 BASE-05、BASE-08，公共组件与使用契约 | Mobile src/components 下公共组件、src/services/mobile-ui.ts、tests/ui-contract.test.mjs；docs/mobile-migration/components.md | 先公布组件契约，再实现，保持现有组件兼容；可编译、响应式、主题与忙碌行为 | 进行中 |
| W1-B | /root/mobile_records | INV-03 中记录、任务、物品和会员部分；盘点后开始 REC、TASK、GOODS、MEMBER | Mobile src/pages/records、src/pages/tasks、src/pages/goods、src/pages/member、src/services/records、对应测试；docs/mobile-migration/records.md | 先交操作清单与接口，按 W1-A 组件契约开发；每页完整业务闭环 | 进行中 |
| W1-C | /root/mobile_finance | INV-03 中财务、编程、关系、消息和 MCP；盘点后开始 FIN、CODE、REL、MSG、MCP | Mobile src/pages/finance、src/pages/coding、src/pages/relationship、src/pages/messages、src/pages/mcp、src/services/domains、对应测试；docs/mobile-migration/domains.md | 先交操作清单与接口，按 W1-A 组件契约开发；敏感和复杂接口不得猜测 | 进行中 |

主 Agent 同时盘点个人设置、密码管理、管理端、认证与已有页面差异，补齐共享请求、附件、导航并运行基线验证。

### 第二批预登记

W2-A：/root/mobile_foundation 完成公共基础后接续 CONFIG-01/02、ADMIN-01 至 ADMIN-07、TIME-03/04。仅写 Mobile pages/admin、pages/categories、services/admin、tests/admin* 和 docs/mobile-migration/admin.md。先盘点各页操作/API，再实现，优先分类与字典。共享导航仍由主 Agent 集成。未开始项保持待派发。

### 首轮基线验证

- 2026-10-01：npm test 29 项通过。既有 Web E2E 正在运行，已发现 navigation.spec.js 和 time.spec.js 的失败，待读取完整报告后归因，不将基线称为全通过。

### 第三批派发

W3-A：/root/mobile_foundation 接续 ME-08/09、GLOBAL-02、TIME-02；独占 pages/personality、pages/auth、pages/time/dashboard.uvue、services/personality、tests/personality*、docs/mobile-migration/personality.md。MBTI/CBTI 包含历史、详情、分享和管理员人格配置，不能只做问卷入口；注册和找回密码按Web现有契约补齐。模型继续 gpt-6.1-sol。

### 开发中验证和新发现

- 原有 E2E 首跑 69 通过、2 失败；导航用例依赖并发请求顺序，时迹用例文本定位重复。已改为选中日期和弹窗作用域断言，定向两项复跑通过。首跑结束清理等待过长由主Agent中断，未伪称进程退出成功。
- 首轮接入待办、目标、财务五页及个人设置后 Web 构建通过；当时契约测试 40 项通过。后续代码仍需重新验证受影响范围。
- 待办删列不级联删任务，保留未归类入口；闪念关联事件缺少服务端删除接口，列为需处理差异。
- 消息中心含私聊和 AI 会话；CBTI 含管理员人格管理和分享海报，补充到操作级清单。
- 文件上传以当前源码为准：全局 /file/upload 已存在，支持 bizType；旧 AGENTS 描述与代码不一致。
- 页面交回不等于验收完成。个人设置 E2E 正在排查直接路由访问与测试夹具，结果未通过项保持进行中。

- 2026-10-01：个人设置 8 个模拟接口 E2E 用例已分批通过（六尺寸/主题组合、锁重试、密码失败保留及 LLM 密钥留空保留）；任务模块 7 个 E2E 经 scope 修改后正在复测。后端最小契约修复已授权，涉及闪念子事件同步删除和反馈查询参数绑定，37 个 Maven 定向测试通过；仍无真实环境写入验证。

### 第四批派发

W4-A：/root/mobile_foundation 接续 BASE-10 公共图表与 GOODS-02 衣柜。records 已确认衣柜未开始，所有权转交；独占 Mobile pages/goods/wardrobe.uvue、services/wardrobe、对应测试、docs/mobile-migration/wardrobe.md。设备墙仍由 records 维护。图表组件直接协调 finance 接入，避免重复实现；模型 gpt-6.1-sol。

- 开发中复测：68 项 npm test 全通过；个人设置 8 项 E2E 全通过；密码库兼容 Web 密文、失败恢复和离页锁定 E2E 通过。这些结果仅对应模拟 API 和本地代码，无生产数据写入。

### 集成检查记录

- 主 Agent 个人设置/密码库/共享接入的操作清单与证据：[profile.md](./mobile-migration/profile.md)。
- 第二次全量 E2E 105 项：93 通过、12 失败；全部12份失败上下文均包含MiniChart尚未落盘导致的Vite错误遮罩，影响了财务及同时打开的其他页面。构建同样定位为该缺失依赖。组件已补齐，待稳定代码复跑；测试清理阶段等待过长，由主Agent向自己启动的Playwright进程SIGINT退出，退出码130，不记为完整通过。
- 随后微信小程序构建通过，当前输出总计1,888,698字节，尚未计入后续剩余页面；需要继续检查分包和最终体积。
- 原生安全随机数补UTS插件：Android SecureRandom、iOS SecRandomCopyBytes；Swift系统实现经本机编译与合法/非法长度校验通过。UTS桥接及App运行仍未验证。

- 活动附件同步补充授权：原后端更新只追加绑定、无法删除或清空附件，records负责PerformanceController最小契约修正（未传保留、[]清空、归属与事务），加定向测试；无真实数据写入。

- 本机环境实测：HBuilderX 5.26.2026091802（README旧记载4.87已校正），微信开发者工具2.01.2510290，完整Xcode与simctl不可用，adb不在PATH。当前编译器5.31 Alpha，App联编/真机缺匹配环境；微信开发者工具验证继续尝试，只做编译/只读页面，不执行真实业务写入。

- 所有基线业务菜单和别名均已有注册的客户端页面，新增 `migration-routes.test.mjs` 检查映射、注册、文件存在、分包与底栏。当前 `npm test` 78 项通过。首页快捷操作及密码库6项E2E复跑通过；衣柜与记录新批次专项仍在执行，未提前验收。

## 统一验收收尾记录（2026-10-01）

业务与基础条目的“已完成”表示源码迁移、主审及已记录的本地验证完成；真实后端写操作、外部服务、微信/App 真机仍由 QA-07 至 QA-10 跟踪，不因业务行完成而自动通过。

- 三个工作 Agent 均使用 `gpt-6.1-sol`，完成按域派发、主审返工及源码冻结。完整操作/API/字段清单见 [records](mobile-migration/records.md)、[domains](mobile-migration/domains.md)、[admin](mobile-migration/admin.md)、[personality](mobile-migration/personality.md)、[wardrobe](mobile-migration/wardrobe.md)、[profile](mobile-migration/profile.md)；组件见 [components](mobile-migration/components.md)。
- 已补回的收尾项：财务趋势及关系图谱、鉴权图片缓存/重试、基本设置跨账号隔离、菜单解锁离页取消、CBTI 海报二维码、AI Markdown 横向表格、Web/微信/App 共用文档选择及导入。
- 服务端四处最小闭环：闪念关联事件删除同步、反馈筛选参数绑定、活动附件关联同步、观影评分显式 null 清空。省略字段仍保留，所有更新遵守资源归属，46 项定向模拟测试通过；未执行真实账号写入。
- 微信开发工具实际发现 `objectWithoutPropertiesLoose` helper 缺失；已通过微信独立 ES2017 编译目标及移除时迹创建对象 rest 修复。最终平台复验结果见验收报告。构建通过不替代模拟器运行。
- HOME-02 的 Web 工作台是 Vben 静态演示，没有独立业务数据；移动端使用真实首页。衣柜源系统没有穿搭实体/API，未编造穿搭功能。这两项是源码核对结论，不是漏迁移。
- QA-07：微信开发工具已有账号只读加载首页和授权生活目录；新增编辑、删除、密码修改、消息发送、上传/绑定等均仅做模拟测试，尚未形成全量真实后端写入验收。
- QA-09：没有本轮微信真机扫码及设备操作记录，保持受阻。
- QA-10：本机 HBuilderX 5.26.2026091802 与项目固定 5.31 Alpha npm 编译器不匹配；无完整 Xcode/simctl 和可用 Android 调试设备证据。App 文件选择、分块流、UTS 安全随机数与 Vapor 页面需要匹配环境真机验收。
- 所有已有未提交改动保留；未提交、未推送、未上传或发布。开发工具中原有“上传成功”提示属于此前状态，不是本轮发布证据。

最终结果：88/88 契约、121/121 Web E2E（2.2 分钟，exit 0）、46/46 后端定向测试，以及 Web/微信构建通过。主清单当前 **82 项完成、2 项进行中、2 项受阻**；详情与可复现命令见 [迁移验收记录](mobile-migration/acceptance.md)。

QA-08 补充：最终实际打开衣柜新增弹窗并确认默认关闭按钮可取消；反复编译后的分包导航曾出现 `navigateTo:fail timeout`，清除编译缓存后恢复，未删会话/业务数据。全量平台验收仍保留进行中，详见验收报告。

## 系统管理补充迁移（2026-10-03）

本批基线：Mobile 工作区干净；用户明确授权两个智能体并行。Web 和后端仅对照，主 Agent 独占 `pages.json`、`life-catalog.ts`、路由测试与本清单；不自动提交。

| 编号 | 功能与文件范围 | 状态 | 负责人 | 验收条件 |
|---|---|---|---|---|
| ADMIN-10 | 公共银行卡卡面；`pages/admin/bank-card-covers.uvue`、专属服务/组件及测试 | 已完成 | /root/bank_card_covers | Web 卡面查询筛选、上传、新增编辑、启停删除；权限及错误恢复；移动端布局 |
| ADMIN-11 | 对象存储；`pages/admin/storage.uvue`、专属服务/组件及测试 | 已完成 | /root/object_storage | 单桶目录/前缀浏览、预览下载、受保护删除；触底游标分页、失败恢复、防陈旧响应 |
| ADMIN-12 | 菜单路由接入、源码审查和集成检查 | 已完成 | 主 Agent | 授权菜单原生入口、菜单锁、分包归属；明确本地与真机验证边界 |

- Web 实际页面：已查看登录后的卡面列表和编辑弹窗，确认引用数量、禁删和银行/类型禁改；从菜单进入对象存储并打开 `system/` 目录。Web 对象预览和删除确认仅对照源码，未操作真实对象删除。
- Mobile 已改、已看图、交互已验证：卡面 10 项、对象存储 9 项 H5 模拟接口用例通过（复用 5180 开发服务的定向验证，非生产构建或真实后端写操作）；覆盖 PNG 文件选择、960×605 画布处理及 multipart 上传、新增编辑、引用限制、图片失败重试、启停删除失败恢复、非管理员拒绝请求、实际滚动分页、去重、末页停止、同游标重试和切目录陈旧响应。
- 已查看 390/768/1440 深浅色列表、编辑/预览/确认截图；发现并修正长文件名两端截断、按钮角色、本地缺失图标、错误间距变量及图片重试事件冒泡。截图保存在 Mobile 忽略目录 `artifacts/bank-card-covers-admin/`、`artifacts/storage-admin/`。
- 15/15 定向契约与路由/菜单锁测试通过；`spacing:check`、`typography:check` 和 `git diff --check` 通过。未执行全量 `test:commit`，留待准备提交时统一验证。
- 最终代码微信构建及官方本地包体检查通过：主包 1132.83 KB（工程预算 1600 KB），admin 分包 139.65 KB；专属服务和组件均归 admin 分包，无新增 npm 依赖。日志在 `artifacts/admin-migration/`，体积报告在 `artifacts/weixin-size/`。
- 验证边界：未进行真实后端上传/写入、微信模拟器交互、微信/App 真机；未上传微信代码、设置体验版、提审或发布。未 Git 提交或推送。本批结果不沿用历史通过记录。
