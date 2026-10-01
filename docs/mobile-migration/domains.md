# W1-C 操作级迁移清单

最近更新：2026-10-01。以下 `[x]` 仅表示已实现，**未替代主 Agent 验收**。真实后端、微信/App真机与发布均未验证。全部修改限于已派发目录，已有改动保留，无提交推送。

## 来源与公共约定

参照 Web `api/core/{income,expense,message,mcp,github,csdn,llm,user-bind}.ts`、`api/{bank-card,relationship}/index.ts` 与对应 views；复杂契约核对后端 `IncomeController`、`ExpController`、`LLMController`、各实体/query。收入实际主键为 `id`，兼容旧 Web `incomeId`，所有 ID 保留字符串。GET query 参数平铺；收入与支出无附件。复用 MobilePage/MobileButton/ConfirmAction/FormField/PageState/AdaptiveModal/MetricCard/LoadMore；页面上下拉刷新，局部提交失败保留表单。

`services/domains/session-guard.ts` 在API完成后校验Token；`page-session.ts` 在 onShow 恢复session/登录检查并加载，在 onHide/onUnload 失效请求和清理业务数据。银行卡完整卡号、GitHub Token、聊天内容与账单预览离页清空；页面级请求代次阻止旧结果覆盖新状态。

## FIN-02 收入 `/pages/finance/income`

- [x] 分页继续加载、年份/类型/日期范围筛选、日期/金额排序、已加载金额汇总。
- [x] 新增、编辑、删除；amt/incTypeId/incDate/remark真实表单；更新保留 tax 等已有字段；后端返回false拒绝假成功。
- [x] 页面内年度/月度按类型统计；切换周期和失败重试。
- [x] API：GET `/income/query`、POST `/income`、PUT/DELETE `/income/{id}`、GET `/income/statisticsByYear|statisticsByMonth`；字典 `income_type`。
- [x] 统计类别按钮定位对应年月/类别并查询记录。

## FIN-03 支出 `/pages/finance/expense`

- [x] 分页、年份/类型/支付方式/日期/备注/交易对方/交易描述筛选、日期与金额排序、金额汇总。
- [x] CRUD、选中批量删除、连续录入；transactionAmt与amt联动；日期/时间原生picker；更新保留transactionId/status/merchantOrderNo等导入字段。
- [x] 年度/月度类型统计与账单导入入口。
- [x] API：GET `/expense/query`、POST/PUT `/expense`、DELETE `/expense/{id}`、POST `/expense/deleteBatch` `{idList}`、GET `/expense/statisticsByYear|statisticsByMonth`；字典 `exp_type/pay_type`。
- [x] 统计类别按钮定位对应年月/类别并查询记录。

## FIN-01 概览 `/pages/finance/index`

- [x] 年份筛选、收入/支出/结余、月度收支与累计结余、收入/支出类型构成条形展示、年度比较；统计取两个 `/statisticsByMonth`。
- [x] 收入、支出、银行卡入口；无本页修改或附件API。
- [x] 复用公共MiniChart：月度收入/支出/结余、累计结余折线，年度对比/分类金额及比例柱形，支持负数与触屏数值选择；可开关图例。

## FIN-04 导入 `/pages/finance/import`

- [x] 移植 Web 完整 `importParser.ts`：支付宝电脑CSV/手机CSV/微信xlsx；分精度退款扣减、自动类型与支付匹配、交易明细保留。
- [x] Web选择CSV/ZIP/xlsx、微信 chooseMessageFile 与本地读取；所有平台提供CSV粘贴入口；ZIP用jszip、xlsx用同Web版本解析。
- [x] 预览/金额/类型/支付/备注编辑、原交易分类筛选/分类汇总、日期/金额排序、全选与取消、选中删除、批量设置、POST `/expense/saveBatch`；用户级交易号验重错误保留预览，预览自身重复交易号禁止提交。
- [x] App 原生文档选择源码接入官方uni.chooseFile，CSV/ZIP/xlsx选择后读ArrayBuffer进入完整解析；真机验证另列。
- [x] 原生GBK解码复用xlsx既有cpexcel codepage936，UTF8增量/GBK模拟测试通过；微信真机验收另列。
- [ ] 微信ZIP/xlsx真机兼容、Web ZIP与微信xlsx文件选择E2E仍待验证；已有纯CSV测试不能替代。

## FIN-05 银行卡 `/pages/finance/cards`

- [x] 搜索、银行/类型/状态/标签筛选、sortOrder排序；CRUD、完整卡号按需POST显示/隐藏/复制；离页清理敏感值。
- [x] 完整字段：bankId/customBankName/cardName/alias/cardType/cardNo/branchName/status/openedDate/expiryMonth/creditLimit/statementDay/repaymentDay/coverColor/coverSourceUrl/sortOrder/remark/tagIds/coverFileIds；编辑空卡号省略，保留已有封面。
- [x] 封面上传 `/file/upload` `{bizType:'bank_card_cover'}`、鉴权预览、移除/颜色/来源URL；标签CRUD及0/1状态。GET `/bank-cards|banks|tags`、POST/PUT/DELETE `/bank-cards/{id?}`、POST `/bank-cards/{id}/number`、POST/PUT/DELETE `/bank-cards/tags/{id?}`。
- [x] 额度非负、账单/还款日1..31、有效月转换后端LocalDate；标签中文状态与可见名称。
- [ ] 封面上传/真实图片/完整卡号失败恢复真实平台验收。

## MSG-01 消息 `/pages/messages/index`

- [x] 消息列表/未读筛选、单条/全部已读、删除；私聊发送、按会话用户筛选与会话删除；GET `/message/list`、PUT `/message/read/{id}|read-all`、POST `/message`、DELETE `/message/{id}`。
- [x] 管理员独立频道、用户ID筛选、分页、发送和删除；按 `roles.includes('admin')` 提供入口，后端继续鉴权；`/message/admin/list|send|{id}`。
- [x] 隐藏AI功能：会话CRUD/标题、历史/清空、发送、Web SSE流式、单条本地隐藏（Web也无单条AI删除API，不能宣称服务端删除）。API `/llm/sessions/{id?}`、`/llm/chat/history?conversationId`、`/llm/chat/stream`。
- [x] Web与原生统一 `/llm/chat/stream`，原生uni.request enableChunked/onChunkReceived增量UTF8与SSE处理；无分块回调平台解析同次请求完整响应，不重复发消息；错误保留输入、离页abort。
- [ ] 微信/App真机分块回调、UTF8分块与取消验收；依赖支持request chunk的匹配HBuilderX运行环境。
- [x] 私聊会话昵称/头像（GET `/user/{id}/basic`）、未读数与切换标读；AI安全Markdown rich-text、外链/复制、滚动到底。Markdown支持标题/强调/代码/列表/引用；表格纯view分块支持表头/对齐/转义竖线/代码/横向scroll-view，不依赖rich-text的table支持。

## MCP-01 `/pages/mcp/index`

- [x] 查询/搜索、schema字段和说明、必填/数字校验、enum/boolean选择、复杂参数输入、主动POST执行、结果与isError显示；GET `/mcp/tools`、POST `/mcp/tools/call` `{name,arguments}`。
- [x] 本地 `$ref` 解析、递归必填/类型/enum/范围/长度/pattern/additionalProperties校验。
- [x] 复杂对象/数组在字段内输入JSON，与Web `views/mcp/tools/index.vue:142,184` 等价；没有用通用JSON替代业务表单。完整JSONSchema组合关键字不属于Web现有交互。

## CODE-01..03

- [x] GitHub `/pages/coding/github`：账号绑定入口、GraphQL贡献/今日/连续/活跃/365天热力信息、最近提交分页外链；仓库搜索/原创Fork/排序、语言/Star/Fork/本人提交/来源Star统计。后端 `/github/recent-commits`；`/userbinds/list?includeToken=true` 仅临时内存凭证，官方REST/GraphQL请求，不写储存或日志。
- [x] LeetCode `/pages/coding/leetcode`：账号绑定、档案排名、竞赛分数/全球全国排名/参赛统计、难度解题进度、日历与连续活跃、每日题、近期AC/题目外链。Web沿用官方GraphQL代理 `/leetcode-api/graphql|graphql/noj-go/`，原生直连 `https://leetcode.cn`；Web该页没有可调用的后端同步操作，不造同步API。
- [x] CSDN `/pages/coding/csdn`：绑定入口、浏览/原创/排名/粉丝/点赞/评论统计、文章内容与外链；`/csdn/stats|articles`。
- [ ] 外部API真实联调、部署环境LeetCode代理、微信域名白名单与原生外链验证；GitHub详细统计会受官方限流，保留单仓库错误状态。

## REL-01 `/pages/relationship/index`

- [x] 图谱数据、触屏人物/关系列表、搜索与分类；人物CRUD/详情（name/avatar/category/description/tags/birthday/phone/email/school/socialLinks/notes）保留字段；关系CRUD/目标/类型/方向/说明/标签。
- [x] GET `/relationships/graph`、`persons/search?keyword`、`persons/{id}`；POST/PUT/DELETE `/relationships/persons/{id?}`、POST/PUT `/relationships/{id?}`、DELETE `/relationships` body保留源/目标/类型；后端继续负责用户隔离与Neo4j开关。
- [x] 纯view触屏拓扑、节点连线/拖动/缩放/复位/点击详情；长姓名单行截断且按钮可访问名称保留全名；同名选择显示ID。
- [ ] 原生图谱手势真机验收；头像沿用WebURL字段，无新增上传API。

## 验证记录

- `node --test aio-life-mobile/tests/domains-*.test.mjs`：16/16通过，新增模拟xlsx退款、大交易号、GBK、SSE、跨块中文emoji、schema引用与嵌套、账户切换响应失效、Markdown转义。
- 12个 `.uvue` 的Vue SFC专用检查已通过；Vapor全端构建由主Agent统一执行。
- 最新 `domains.spec.js` + `domains-pages.spec.js`：17/17通过（`test-results/domains-freeze-run`）。包括390/768/1440深浅编辑弹窗、真实表单CRUD失败恢复、银行卡留空卡号保留封面、人物附属字段、MCP参数类型、CSV后端重复失败恢复；共享ConfirmAction fixed定位后删除实际点击通过。
- 图表/拓扑截图：`test-results/domains-finance-{390,768,1440}-{light,dark}.png` 与 `domains-relationship-...`，实际逐张查看；模拟包含负结余、长姓名和连线。首次查看发现长名换行撑高与图系列容器裁剪，均已修；最终6种视口主题重跑6/6通过（`domains-visual-final`），12张截图重新逐张查看，负结余零基线和节点连线可见。
- E2E只拦截精确 `http://127.0.0.1:5180/api/**` 和明确模拟官方域名，避免拦截uni样式。无真实生产写入、凭据、提交或推送。
- 未验证：真实后端、外部API部署代理/白名单、HBuilderX App/微信真机；这些未完成项不能由H5模拟测试替代。

## 授权收尾补修

- [x] `profile/settings.uvue`：onShow重新加载，onHide/onUnload清空缓存与代次失效；Token同步清空表单；头像选择/上传、加载、保存完成后同时检查Token/代次/可见状态。
- [x] `profile-scope.spec.js` 2/2实际回归：A未保存表单切B后加载B并验证写入B数据；A延迟请求离页后，返回加载B，待A响应实际完成仍不覆盖。证据 `test-results/profile-scope-final3`。
- [x] 关系搜索输入与按钮同排对齐，分类另行160px；受影响6种布局和人物失败恢复7/7通过（`domains-relationship-final`），关系六张截图重新逐张查看。
- [x] 银行卡封面按卡显示错误与独立重试，读取/上传/预览每次await后校验生命周期；离页清空预览，切换编辑草稿也拒绝旧上传回写。封面失败→重试实际图片与银行卡更新恢复2/2通过（`domains-cover-final`）。

## App 文档与 Markdown 最后补齐

- [x] 共用 `services/native-files.ts`：`chooseDocument({extensions?,maxBytes?}) -> {name,path,size,temporary?}`；`readDocument(file,binary=true)`；`releaseDocument(file)`。账单已接，Douban由records接，共用AttachmentField开放App“添加文件”；不新增UTS插件。
- [x] H5 uni.chooseFile + fetch，MP保持wx.chooseMessageFile + fs.readFile；App uni.chooseFile(type:all)返回后校验扩展名，再异步copyFile到CACHE_PATH。Android content://不假造物理路径；finally清理自有缓存。上传保持二级解锁重试与Token校验，选择完成后再次校验Token。
- [x] 16MiB仅用于账单/Douban整文件导入内存保护，通用附件选择不新增限制；后端application.yml当前multipart单文件/请求10MB，部署配置可能不同，交给服务器返回实际错误。
- [x] Markdown表格安全分块，纯view列宽160px可横向滚动，标题与单元格复用转义/inline格式；围栏内不误识别表格。新增解析/路径大小/模拟App复制读取清理测试。
- [ ] App匹配工具链原生编译与真机验收：本机HBuilderX **5.26.2026091802**；仓库CLI **3.0.0-alpha-5030120260930001** 不匹配，未宣称实际运行通过。

官方依据：[chooseFile](https://doc.dcloud.net.cn/uni-app-x/api/choose-file.html) Android4.51/iOS4.61起支持；App不支持extension、Android返回content协议。[FileSystemManager](https://doc.dcloud.net.cn/uni-app-x/api/get-file-system-manager.html) copyFile官方含content示例、异步readFile可返回ArrayBuffer；[5.26发布记录](https://doc.dcloud.net.cn/uni-app-x/release.html)新增Android content读取；[uni.env](https://doc.dcloud.net.cn/uni-app-x/api/env.html)定义CACHE_PATH。与Vapor配套版本验证由主Agent统一，不升级现有依赖。

最后证据：领域纯测试 **19/19**；新增App分支模拟选择→content URI复制沙盒→ArrayBuffer读取→finally清理、取消与扩展/大小拒绝。`domains-markdown-final5` **2/2** 深浅主题真实水平wheel操作后scrollLeft>0，显式direction=horizontal保证Vapor横向滚动；`test-results/domains-markdown-table-{light,dark}.png`最终截图已逐张查看，滚动后的第三列及转义文本可读。此前未完成的滚轮选择器测试与滚动方向检查已修，不将早期失败记录视为通过。源码/测试冻结，原生编译与真机仍未验。
