# 09 财务间距视觉复验

范围：`finance/index`、`income`、`expense`、`import`、`cards` 五物理页；`income/expense` 共用 `ledger.uvue`。

模拟登录后从生活目录点击进入。五页覆盖 390 light/dark；支出和银行卡额外覆盖 768 light、1440 dark，共14场景。收入/支出/银行卡打开新增与编辑弹窗、滚至底部、删除确认取消；导入仅CSV解析预览和预览编辑关闭，不执行导入、保存或删除。银行卡使用3条模拟卡片，收支补充3条模拟记录。总览统计包含两月数据及多张图表。

证据：移动仓库 `artifacts/spacing-audit/09/` 的逐页截图、长弹窗顶部/底部、删除确认、滚动分屏截图及 JSON；`*-full-contact.png` 是真实滚动分屏接触拼图。独立测试为 `tests/e2e/spacing-09.spec.js`。

量化：390/768页面左右12px；1440内容最大宽度960，左右252px（其中内容容器页面内边距12）；业务根padding0。收支记录/银行卡padding12、卡间margin-bottom12、toolbar gap8；双列筛选宽度一致（误差小于1px），同排输入框底边齐。总览图表外缘x12、宽366，图表padding12、区块margin-bottom12；此次共享MiniChart从modal变量改为card变量由主任务处理。弹窗内容内边距16，银行卡长表单底部取消/保存可见且同排对齐。

已实际查看总览原图与全页拼图、收支多行原图、768支出、银行卡长弹窗底部、导入预览。页面和卡片外缘齐，图表没有挤出边界；桌面内容居中，平板双列不过度稀疏。未发现需要本组业务页面修复的明确间距问题。

复验命令：

```bash
npx playwright test tests/e2e/spacing-09.spec.js --output artifacts/spacing-audit/09/playwright --workers 1
```

测试过程中修正了测试夹具的三个问题：reload重新执行helper的清token初始化；Vapor自定义INPUT触发Playwright role递归异常（弹窗用CSS `[role=dialog]`）；uni保留旧页面scroll节点，滚动需选当前页面最后一个节点，query路由匹配需包含querystring。没有修改旧shared fixture。

结果仅代表H5模拟接口视觉与交互，未验证真实后端、微信模拟器/真机或App Vapor真机。没有安装、重启、提交，也没有写真实业务数据。
