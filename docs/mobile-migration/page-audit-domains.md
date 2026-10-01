# 领域页逐页与逐弹窗验收

日期：2026-10-01。所有账户、Token、记录、密码密文、银行账号、消息以及第三方响应都是明确的测试 fixture；无真实账号登录、消息发送、生产接口写入。

## 验收方法

从根地址进入模拟登录，点击首页的“生活” tab，再点击财务／编程功能组或目录业务入口。业务页没有直接 `goto`。逐项点击新增、编辑、详情、删除确认、选择器，保存弹窗顶部和内部滚动底部图片，检查关闭／取消后返回。390 为主验宽度，768 为中间宽度，1440 为桌面宽度，各含深浅主题；另使用真实下拉 TouchEvent 验证加载失败、重试和空结果。

原始图片在移动仓库 `artifacts/page-audit/domains/`，每次生成立即备份 `/tmp/qa-domains-evidence/`，最终由总验收归档到移动仓库 `artifacts/page-audit/domains/`。`domains-coverage.json` 逐条记录 route、variants、checks、evidence、status、issues，并在最终汇总时按物理页聚合。

Playwright 日期／时间控件在 768／1440 会使用 Chrome 原生 `input[type=date/time]`。测试实际点击再 Escape 关闭，并与 DCloud 自定义 selector 层区分；Chrome 原生日历弹层不在 DOM 截图内，不能把该截图当作日历内容的视觉验收。手机自定义 picker 则有可见弹层截图。

## 12 页与弹窗范围

| 物理页 | 实际点击的弹窗／确认层／选择器 |
|---|---|
| `finance/index` | 年份、统计图查看数值选择器；页面不提供编辑弹窗 |
| `finance/income` | 新增收入、编辑收入；类型与日期；删除确认／取消；查询筛选选择器、统计展开 |
| `finance/expense` | 新增支出、编辑支出；类型、支付方式、日期、时间；删除确认／取消；查询筛选选择器、统计展开 |
| `finance/import` | 完整支付宝 CSV、ZIP、微信 xlsx 文件选择／解析；导入记录编辑；类型、支付方式；退款预览、后端重复失败保留 |
| `finance/cards` | 新增银行卡、编辑银行卡长表单；银行卡相关选择器；新增／编辑标签；银行卡与标签删除确认／取消；完整卡号展示 |
| `coding/github` | 类型、排序；账号绑定入口。该页没有业务编辑弹窗 |
| `coding/leetcode` | 账号绑定入口。该页没有业务编辑弹窗 |
| `coding/csdn` | 账号绑定入口。该页没有业务编辑弹窗 |
| `relationship/index` | 新增／编辑人物长表单、人物详情、关联关系新增／编辑；关系类型、目标人物、方向；人物与关系删除确认；图谱放大／缩小／复位 |
| `messages/index` | 消息、私聊、AI、管理四种频道；通知／私聊／管理发送弹窗；AI改标题；全部已读、标已读、删消息、删会话、清历史、删私聊当前会话、管理员删除确认；筛选选择器 |
| `mcp/index` | 工具参数弹窗；必填参数，模拟执行失败保留、重试成功、结果展示 |
| `vault/index` | 首次解锁与确认主密码、已有记录解锁、新增／编辑记录、密码生成器；删除确认／取消；分类选择器；失败保留／密文保存／离页重新锁定 |

上述范围合计 **13 种业务弹窗结构、14 种确认层结构**；新增与编辑、通知与私聊与管理发送等不同状态分别实际点击。图片数量按最终 JSON 中仍然存在的独立 PNG 统计，不能把同名覆盖图重复计入。

## 发现与修复

| 问题 | 修改与复验 |
|---|---|
| 发送标题、AI 改名草稿与管理筛选用户离页未清理 | 本组仅在 `src/pages/messages/index.uvue` 的离页回调补清 `title`、`rename`、`adminUser`。回归通过发送弹窗填入模拟标题后返回目录再进入，确认标题为空；打开 AI 改名草稿时使用浏览器返回，再进入确认没有遗留弹窗或草稿 |
| DCloud 精确拖动一格后视觉选中项与提交值不一致 | 本组保留触摸复现，主组在 `scripts/patch-uni-h5-picker.cjs` 修复 `dist`／`dist-x`／`dist-x-vapor` 的精确格线 `onSnap` 通知。`hasTouch=false` 和 `hasTouch=true/isMobile=true` 都确认从消息切换到私聊；有 before、transform、after、CDP 坐标与事件 JSON |
| 选择器取消后立即卸载触发 `null.remove`，或立即重开被旧延迟回调移动 | 主组扩展同一持久补丁，保护已卸载 refs 并忽略重新打开后的旧回调。本组专门验证快速取消后立即关闭编辑弹窗，以及取消后立即重新打开选择器；没有用等待 260ms 掩盖问题 |
| 确认框为固定估算高度，距离原按钮过远 | 主组改为测量实际确认框高度。本组最终单独复拍 `finance/expense` 390 暗色、`finance/cards` 768 暗色确认层，旧图不作为修复后证据 |
| 异步详情内容变化后弹窗高度不更新；公共图标按钮内容贴左 | 主组修复 AdaptiveModal 内容测量与 MobileButton 居中。本组实际查看人物详情、MCP 参数／结果和长表单顶部／底部，检查图标、关闭按钮及保存按钮 |

## 执行记录

测试源：移动仓库 `tests/e2e/qa-domains-all-pages.spec.js`，辅助源均为 `qa-domains*`。本地导入 fixture 位于 `tests/e2e/qa-domains-fixtures/`。从既有 mock 定义复制数据形状后独立执行，本轮结论没有引用前轮作者的通过报告。

```bash
# 初次独立逐页实点矩阵：72 passed
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line

# 精确格线触摸与移动触屏上下文：两个 assert 通过
node tests/e2e/qa-domains-touch-repro.js

# 生命周期修复与收入 768 原生日期区分：2 passed
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line --grep '快速取消|finance/income 768 light'

# 最后仅复验增加选择器／确认层的页，以及 vault、导入文件、离页清理与错误恢复
# 保留已通过且未改变的 finance/index、CSDN、LeetCode、MCP 主链结果，避免反复重跑
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line --grep-invert '(finance/index|coding/csdn|coding/leetcode|mcp/index).*(390|768|1440) (light|dark)'
```

具体测试名包括 `逐页真实点击 <route> <width> <theme>`、`密码库已有记录逐弹窗与失败保留 <width> <theme>`、`账单完整本地文件选择 <file>`、`消息离页清理发送标题与AI重命名草稿`、`逐页下拉失败重试和空态 <route>`、`桌面选择器快速取消关闭与立即重开无生命周期异常`。最后一次结果与逐页证据表在下方最终汇总中填写。

## 验证边界与冻结

这是 Chromium Web 的完整 mock 验收。未验证真实后端权限、生产部署、第三方 GitHub／LeetCode／CSDN 联通、真实消息发送／AI 流式回答、微信模拟器与真机、App Vapor 真机或发布。图谱此次检查按钮缩放／复位与人物交互，不把按钮操作当作已完成真实多指缩放验收。没有 commit、push、安装依赖、关闭 Vapor 或修改其他组测试。

## 最终批次与并发变更

最终 69 项批次在第 51 项遭遇外部并发共享图标替换：`CategoryIcon.uvue` 引入的 `../services/icons/action-icons.json` 尚未生成，Vite overlay 阻挡操作。立即停止继续扩散，当次结果为 50 passed、7 环境失败、1 interrupted、11 未执行。这不是把环境错误当作业务通过；待文件生成且 overlay 消失后，单独重跑余下 19 项。

```bash
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line --grep '密码库已有记录逐弹窗与失败保留 768|账单完整本地文件选择|消息离页清理|逐页下拉失败重试和空态|快速取消'
```

最后的共享 SVG 图标替换只以支出 390 暗色、银行卡 768 暗色做代表性复核，其他图片对应替换前版本；不能据此声称所有页面的新 SVG 图标均重新视觉验收。支出确认框与银行卡两个确认框的最终定位由本组重拍及主组独立查看，按钮间距约 4–5px。

## 最终证据汇总

93 个不同测试项均有通过结果（分批执行），覆盖 12 物理页及 72 个宽度／主题主矩阵；另含 4 个已有密码、3 个完整文件、1 个消息清理、12 个失败恢复、1 个快速取消项。不是最后同一版本的一次93项全跑：首次72通过；最后69中50通过，外部编译中断后已有记录等7通过，授权目录fixture更新后12通过，导入实际问题修复后1通过。最后生命周期快速取消通过；精确34px触摸两个上下文assert均通过。

最终可机读JSON引用 914 张实际存在的独立PNG，包含 137 张弹窗内部底部、366 张选择器截图；两项触摸上下文另保留4张图。13种业务弹窗、14种确认结构是结构类型数，不能把截图数当作弹窗类型数。

|页面|测试项|存在PNG|弹窗底部|选择器|
|---|---:|---:|---:|---:|
|`coding/leetcode`|7|15|0|0|
|`coding/csdn`|7|15|0|0|
|`mcp/index`|7|27|6|0|
|`finance/index`|7|51|0|36|
|`finance/income`|8|94|12|48|
|`finance/expense`|7|124|12|78|
|`finance/import`|10|60|9|24|
|`finance/cards`|7|155|24|84|
|`coding/github`|7|27|0|12|
|`relationship/index`|7|147|30|66|
|`messages/index`|8|130|24|12|
|`vault/index`|11|69|20|6|

并发目录变更后，fixture明确提供授权树，生活目录直接点击实际叶子入口；此前完整矩阵的目录交互对应变更前的功能组入口，具有版本边界。导入页发现初始化失败不可重试，已补 `@refresh`／`@retry` 及新加载前清error，专项 `逐页下拉失败重试和空态 finance/import`：1 passed (11.7s)。

冻结：仅消息离页草稿与导入初始化恢复两处业务源码修复；不再增加测试。JSON及原始case副本在 `/tmp/qa-domains-evidence/domains-coverage.json`、`domains-cases.json`；触摸事件JSON由本组备份同目录。

```bash
# 授权菜单fixture更新后恢复／生命周期：12 passed，import专项修复后1 passed
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line --grep '逐页下拉失败重试和空态|快速取消'
npx playwright test tests/e2e/qa-domains-all-pages.spec.js --workers=1 --output=test-results/page-audit/domains-run --reporter=line --grep '逐页下拉失败重试和空态 finance/import'
# 新SVG仅两个页面、三个确认层代表性实点与截图
node tests/e2e/qa-domains-final-icons.js
```

代表性最终图：`finance-expense-390-dark-svg-final-confirm.png`、`finance-cards-768-dark-svg-final-confirm.png`、`finance-cards-768-dark-svg-final-tag-confirm.png`；均已通过实际 image 查看，图标居中，确认层紧邻触发按钮。精确触摸最后两个上下文结果仍为 before=消息、expected=私聊、after=私聊，事件及CDP坐标详见 `domains-touch-repro.json`。
