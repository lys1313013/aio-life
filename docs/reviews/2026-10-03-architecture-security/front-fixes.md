# Front 架构审查问题修复记录

2026-10-03。上轮 Front 四项已完成本地修复及验证，保留现有 Vben monorepo 和应用 adapter 分层；未提交、推送或部署。

## 修复内容

1. **菜单 ID 全链路保留字符串**
   - API 锁菜单响应、MenuRecordRaw、RouteMeta、二级锁 store 和设置页 Tree key/选中项/保存体统一为 string。
   - 去掉两个路由守卫的 Number(menuId) 转换，设置页不再将雪花 ID 取整。
   - 锁列表获取失败不再永久标记 loaded，后续刷新可重试。
   - 关键文件：`aio-life-front/apps/web-antd/src/api/core/auth.ts`、`store/secondary-lock.ts`、`router/guard.ts`、`views/_core/profile/secondary-password-setting.vue`、`packages/@core/base/typings/src/menu-record.ts` 与 `vue-router.d.ts`。

2. **应用导航统一准备快照后发布**
   - 新增 `aio-life-front/apps/web-antd/src/router/navigation.ts`。首次初始化与菜单管理页修改后刷新使用相同入口。
   - 在独立 memory router 上调用原有 generateAccess / Vben generateAccessible；异步远端操作完成后，再同步替换实际路由和 access store。远端菜单或偏好请求失败不会先清空旧路由。
   - 首次登录仍允许显示偏好读取失败时回退到默认导航；已经可用的导航刷新则保留原快照。
   - 新增 `utils/navigation-menus.ts` 统一隐藏菜单过滤和二级锁标记；个人中心修改显示偏好也使用它。业务偏好仍在应用层，未侵入框架 generateAccessible。
   - 并发刷新仅允许最新请求发布，避免慢响应覆盖新导航。隔离 router 使用静态路由的深拷贝，防止生成过程污染原始配置。

3. **公共卡面管理保护读写交错**
   - `aio-life-front/apps/web-antd/src/views/system/bank-card-covers/index.vue` 增加请求代数、成功写入版本和卸载标记。
   - 慢列表完成时合并其发出之后成功的删除/保存/启停结果，避免删除项复活或状态回滚。
   - 过期列表错误不覆盖新查询的成功状态；列表失败保留已有卡面；启停/删除请求按 ID 去重。

4. **PR 与发布进入相同验证门禁**
   - `.github/workflows/docker.yml` 在 build 和镜像推送之前执行应用 typecheck 与 `pnpm run test:critical`；现有 pull_request、main/tag push 和 workflow_dispatch 入口均覆盖。
   - `package.json` 新增 test:critical，覆盖 API 请求边界、导航、二级锁、菜单偏好/管理、卡面竞态、对象存储、弹窗和时迹编辑。
   - Front 工作流只依赖自己的 checkout，不引用相邻 server/mobile 目录。跨仓固定 revision 的契约验证由主任务单独收口，本修改不声称已建立跨仓门禁。

## 新增回归与验证

- `router/navigation.test.ts`：使用真实 Vue Router 和 Vben generateAccessible 验证隐藏偏好、锁标记、删除旧授权路由、请求失败保留旧路由/store、首次偏好失败回退、并发只发布最新快照。
- `router/guard.test.ts`：首次直达与已初始化导航两条分支都保留 `9007199254740993`，触发正确锁弹窗。
- `store/secondary-lock.test.ts`：相邻大整数 ID 的加载/查询/去重保存不碰撞；失败加载可重试。
- `views/_core/profile/secondary-password-setting.test.ts`：实际组件的 Tree key、选中值和保存参数完成大整数往返。
- `views/system/bank-card-covers/index.test.ts`：实际组件中删除与刷新交错、启停与刷新交错、过期查询失败、失败保留列表和重复删除去重。
- 现有菜单显示、菜单管理、弹窗、对象存储等关键测试也包含在本次门禁执行中。

执行结果：

```text
pnpm run test:critical
14 test files passed; 89 tests passed

pnpm --filter @vben/web-antd typecheck
通过（vue-tsc --noEmit --skipLibCheck）

pnpm exec eslint --fix <本次变更的 TS/Vue 文件>
通过

git diff --check
通过
```

初次 typecheck 发现现有 `views/my-hub/weread/book-link.test.ts:60` 的 `get(...).exists()` 不符合 Vue Test Utils 类型（get 保证存在，因此省略 exists 方法）。改为 `find(...).exists()`；该文件额外 8 项测试通过。此为接入类型门禁的既有阻塞修复，没有修改微信读书业务逻辑。

关键测试输出仍含 Vitest workspace 弃用提示和原有菜单 shallow stub 的 Vue DOM 属性警告，但最终无测试失败或 unhandled error。未运行全量构建、真实浏览器/线上 API/微信真机，也没有执行远端 GitHub Actions；本地验证通过不能替代远端 CI 执行结果。

工作区仅包含上述代码、测试、CI 与本报告修改；启动基线 `6e54d52564753207ee51274ef57d1a5c6f3908b1`，未创建提交。
