# 移动端间距复验 10：编程、社交、消息、MCP、密码库

2026-10-01 完成 H5 模拟接口复验。7 个物理页面，20 个页面/宽度/主题组合通过；另有 GitHub 密集热力图、关系详情空字段修复、消息按钮对齐 3 项定向复验通过。

## 覆盖

| 页面 | 390 | 768 | 1440 | 操作 |
| --- | --- | --- | --- | --- |
| coding/github | 深、浅 | — | — | 仓库多行描述、提交记录、52周贡献数据 |
| coding/leetcode | 深、浅 | — | — | 统计、热力图、多条每日题与通过题 |
| coding/csdn | 深、浅 | — | — | 统计与文章卡片 |
| relationship/index | 深、浅 | 浅 | 深 | 新增人物、详情、编辑人物、新增/编辑关系；长弹窗滚到底后关闭 |
| messages/index | 深、浅 | 浅 | 深 | 消息/私聊/管理/AI，发送弹窗与会话重命名弹窗打开关闭 |
| mcp/index | 深、浅 | — | — | 参数弹窗打开、滚底、关闭，不调用工具 |
| vault/index | 深、浅 | 浅 | 深 | 已有模拟密文主密码解锁、解锁后卡片、新增/编辑弹窗打开关闭 |

入口均为账号密码表单实际登录→原生生活Tab→完整模拟菜单树对应入口点击；业务页未使用直接 goto。模拟Token和密码不对应真实账号；state.calls为空，无真实业务写入。

## 修改与测量

- 关系详情卡片内操作栏从 ui-toolbar 改为 ui-row，去除重复的区块底间距。
- 关系详情过滤没有内容的可选字段，避免6个空text的padding累计形成48px无内容留白。
- 消息筛选按钮不齐由主任务修复共享 ConfirmAction；本组仅验证。390浅色筛选输入、全部已读、发送消息底边均为212px，差值0。
- JSON证据记录各页面根、卡片及工具栏的rect/padding/gap/margin；ui-card内边距为12px。MobilePage负责单层页面12px内边距，1440宽内容外缘为252px（960px内容容器包含左右12px）。

## 实际视觉复查证据

产物位于 `aio-life-mobile/artifacts/spacing-audit/10/`，测试为 `aio-life-mobile/tests/e2e/spacing-10.spec.js`。使用view_image查看contact-0至contact-7，覆盖编程、MCP、四消息模式和关系各宽度的页面与弹窗；另逐张查看下列原图：

- coding-github-390-light-page.png：52周热力图、仓库长描述、双列筛选。
- relationship-index-390-light-人物详情.png：过滤空字段后紧凑详情。
- relationship-index-390-dark-新增人物-bottom.png：长表单底部保存按钮可见。
- messages-index-390-light-消息.png：输入框与两个操作按钮底边对齐。
- messages-index-768-light-发送消息-top.png：居中弹窗与左右内缘。
- vault-index-390-light-unlocked.png、vault-index-768-light-unlocked.png、vault-index-1440-dark-unlocked.png：解锁后卡片与三宽度内容边缘。
- vault-index-390-light-新增密码-top.png、vault-index-390-dark-编辑密码-bottom.png：字段边缘对齐与底部操作可见。

完整矩阵日志由主任务执行记录于 `/tmp/spacing-10-retry.log`（2 passed）及 `/tmp/spacing-10-final.log`（18 passed）；定向补验日志为产物目录 `recheck.log`（2 passed）及 `message-recheck.log`（1 passed）。按钮测量见 `messages-button-bottom.json`。

截图使用fullPage选项；uni-app内部scroll-view的可滚区域仍以当前视口显示，长弹窗另有顶部和滚底截图。个别初始模式截图曾捕获选择器退出动画，定向消息复验改为等待550ms稳定后采图；最终390浅色消息四模式证据已覆盖为稳定截图。

仅证明H5模拟接口下布局、登录导航及上述弹窗交互，不代表真实后端、微信模拟器、App/微信真机验证。
