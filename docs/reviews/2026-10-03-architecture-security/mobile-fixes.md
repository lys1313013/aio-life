# Mobile 架构问题修复（2026-10-03）

已修复 mobile.md 的 M1/M2：账单删除后的分页遗漏，以及账单增删改/下拉刷新后的统计不同步。密码库协议不在本轮授权范围，没有修改。

## 范围及保留项

- 业务代码仅修改 `aio-life-mobile/src/pages/finance/ledger.uvue` 中加载、刷新、写入失效逻辑；仍由收入和支出共用。
- 新增 `aio-life-mobile/tests/finance-ledger-state.test.mjs` 和 `aio-life-mobile/tests/e2e/finance-ledger-consistency.spec.js`。
- 保持 Vapor、业务分包和现有 API，不新建聚合业务公共 service。
- 保留工作区已有 LedgerRow、FormActions、图表、表单、筛选/年份修改；这些并非本轮所写。未修改密码库、组件和无关页面，未提交/推送/部署。
- 对照 Web `apps/web-antd/src/views/my-hub/income/index.vue` 的删除/保存后 `gridApi.reload()` 与 `dashboardRef.refreshData()` 行为，移动端同样刷新列表及统计。

## 实现

1. 写入开始时统一作废旧列表与统计请求，阻止写入中分页/刷新建立旧快照。写入与请求序号分离，不再因为分页请求变化而忽略已经成功的写操作。
2. 新增、编辑、单删、批删成功后从第一页重新建立分页快照，同时刷新统计。删除后重查失败保留已有内容，提示错误；下次重试必须从第一页恢复，不能沿用失效的 offset。
3. 翻页合并按字符串账单 ID 去重，保留末页停止、防重入和失败页重试。
4. 月度概览始终更新；查看年度统计时同时查询年度数据，避免年度模式下概览永久过期。统计拥有独立 loading/error，统计失败不阻止列表更新；可单独重试。
5. 下拉刷新等待列表和统计完成后收起。组件卸载同时使两个请求通道及刷新收尾失效。
6. 写接口明确返回 `false` 时不当成功；写入失败保留表单及列表。

## 验证

### 定向 Node 回归：12 项通过

执行：

```sh
node --test tests/domains-finance.test.mjs tests/finance-ledger-state.test.mjs
```

包含 3 项现有财务契约测试及 9 项新增完整操作序列。新用例执行当前 Ledger 的真实 script，经 esbuild 转译，只替换网络和挂载事件，不复制分页实现：收入/支出删除第一页后继续翻页、批删、分页防重入、增改删与月/年度统计、失败保留和重试、旧分页/旧统计与写入交错、写入后旧响应迟到、离页、写失败及批删 false。

### H5 浏览器回归：3 项最终均通过

使用一次新的 H5 生产构建，临时预览端口 5187，未占用/停止现有 5180 开发服务。用例为：

- 支出删除第一页记录后，通过真实 wheel 滚动加载第二页，100 条剩余记录完整，包含此前遗漏的 ID 51，且无重复。
- 收入执行同一序列，验证两端共用 Ledger 的分页修复。
- 修改收入金额后总额实时更新；模拟外部新增后下拉刷新；统计请求失败保留原统计，单独重试后恢复正确金额。

初次用例把收入统计误定位到支出专有分布组件，之后又将数字输入误写为 textbox；均为测试定位错误，已按当前 DOM 修正为共享 `.summary-total .metric-number` 和 spinbutton。产品逻辑没有为这些错误做修改。只重跑受影响用例，未重复 H5 构建。

日志（Git 忽略目录）：

- `aio-life-mobile/artifacts/finance-ledger-fixes/e2e.log`：首次运行，包含新 H5 构建。
- `aio-life-mobile/artifacts/finance-ledger-fixes/e2e-final.log`：收入/支出两个删除与滚动用例通过；统计用例当时因数字输入角色定位失败。
- `aio-life-mobile/artifacts/finance-ledger-fixes/e2e-statistics.log`：修正定位后的统计用例通过（1 passed）。

临时 Playwright 配置仅用于隔离 5187 端口和复用本轮已验证构建，不进入生产代码。

## 快照与边界

H5 构建后及最终核对 Ledger SHA-256 一致：`c53c31db4ec665444806cbd63f5ecf3aeeecff55266e544b80ef92d06a575f94`。其他线程仍在修改工作区，因此此结果只对应本轮构建和测试读取的代码，不能泛化为之后所有未提交修改通过。

未执行全量单元/E2E、微信构建、test:commit、真实后端写入、微信/App 真机或发布。本轮没有准备提交，完整验证留待提交前统一执行。

### 汇总前追加复核

汇总时 Ledger 又被外部工作修改，当前 SHA-256 为 `40a79aa273be3bc61bd30df4d8fa863c939a3345e7084d6120ff7640ee47edbb`。已重新读取当前脚本并重跑上述 12 项 Node 测试，全部通过。本轮修改的统计、分页、refresh、mutate、保存、单删和批删逻辑及其行号保持不变（47、193、257、266、353、369、385）；相关模板的下拉/触底、列表、总额、表单操作绑定仍保留。

没有覆盖外部改动。由于未保存旧 `.uvue` 全文副本，不能仅凭旧哈希宣称逐字确认了所有外部变化；3 项 H5 E2E 仍明确属于 `c53c...` 的生产构建快照，当前 `40a7...` 已通过的是定向 Node 逻辑回归。未再次构建，也不将旧浏览器结果包装为最新文件的浏览器验证。
