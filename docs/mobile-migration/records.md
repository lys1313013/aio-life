# W1-B：任务、记录、物品和会员迁移

负责人 `/root/mobile_records`。2026-10-01。仅修改 Mobile `src/pages/{tasks,records,goods,member}`、`src/services/records`、对应测试和本文件。现有未提交改动保留，未提交/推送；总台账、导航、公共组件由主 Agent 管理。

## 逐页操作子清单

勾选表示代码实现和契约检查，仍须主 Agent UI/构建审查；未勾选保留原范围。列表 API 均已通过本地 Web API 与服务端 Controller 核对。业务权限由服务端当前用户归属约束，MobilePage 复用菜单锁；无管理员权限扩张。

### TASK-01 待办

证据：Web `views/task-center/todo/index.vue`、`task-edit-drawer.vue`；Server `record/api/{TaskColumn,Task,TaskDetail}Controller.java`。路由 `/pages/tasks/todo`。

- [x] 列查询、新增、标题/背景编辑、删除、触屏前后排序；`GET /taskColumn/query`，`POST /taskColumn`，`PUT/DELETE /taskColumn/{id}`，`POST /taskColumn/reSort` 数组。
- [x] 任务查询、搜索、新增、内容/说明/截止日期时间编辑、删除、跨列移动、上下排序；`GET /tasks?get=1&pageSize=100`，`POST /tasks`，`PUT/DELETE /tasks/{id}`，`POST /tasks/reSort` 数组。
- [x] 明细查询/新增/编辑/删除、完成切换、优先级 `1/10/20`、起止日期时间、关注切换、上下排序；`/taskDetails` GET/POST/PUT，DELETE `/{id}`，POST `/reSort`、`/star/{id}`、`/unstar/{id}`。
- [x] 请求失败保留列表/表单，详情错误禁新增，旧详情请求隔离；字符串 ID，明细关联/星标/状态保留。
- [ ] 手机/平板/桌面深浅主题、弹窗键盘及手势 E2E。

实际服务端删除列只删列，Web确认文案错误声称级联删除。Mobile 将此列原任务放入“未归类”，避免无声隐藏；不改变后端删除语义。

### TASK-02 目标

证据：Web `views/task-center/goal/index.vue`、`api/core/goal.ts`；Server `GoalController`、`GoalEntity`、`GoalTypeEnum`。路由 `/pages/tasks/goals`。

- [x] 全部目标/关键词/周期/状态筛选，数量/完成数量及进度。
- [x] 新增/详情编辑/删除；GET/POST/PUT `/goals`，POST `/goals/batchDelete {idList}`。
- [x] 标题、10类周期（日/周/月/季度/半年/年度/三年/五年/十年/终生）、四状态、目标值/当前值、起止日期时间、描述、行动计划、标签；类型改变自动计算周期。
- [x] 编辑保留 `parentId`、完成时间等附属字段；字符串 ID、非负整数、日期顺序校验。
- [x] UI 与保存失败恢复 E2E（目标390/768/1440深浅主题）。

控制器旧注释写1..3，实际 GoalTypeEnum 与 Web 都为1..10，Mobile以真实枚举为准。

### REC-07 闪念

证据：Web `my-hub/think/{index,ThinkModal}.vue`；Server `ThoughtController`、`ThoughtSaveReq`。路由 `/pages/records/notes?kind=think`。

- [x] 分页查询、内容搜索、新增/编辑/删除；GET `/thought/query`，POST `/thought`，PUT `/thought/{id}`，POST `/thought/batchDelete`。
- [x] 看板置顶与隐藏内容切换，保留事件 ID；关联事件新增/编辑。
- [x] 已持久化关联事件删除：本批最小修复服务端完整列表保存，旧 ID 不变，新事件生成 ID；未传列表保留，空列表清空，仅当前已验证用户归属的闪念可清理。
- [x] 模拟API编辑失败保留/重试 E2E，附属字段保留。

`POST /thought` 返回 Boolean，不返回 ID且忽略 hiddenContent。Mobile新建不显示隐藏开关；创建后重新查询，已创建但读取失败时仅重试读取，防止重复创建。

### REC-08 笔记

证据：Web `my-hub/memo/index.vue`；Server `MemoController`。路由 `/pages/records/notes?kind=memo`。

- [x] 分页查询、内容搜索、标题/内容新增编辑、隐藏内容切换、删除；GET `/memo/query`，POST `/memo`，PUT/DELETE `/memo/{id}`。
- [x] 保留隐藏状态、长内容；失败保留表单；Boolean新增响应后读取失败不重复创建。
- [x] 模拟API编辑失败保留/重试 E2E，附属字段保留。

### REC-10 里程碑

证据：Web `my-hub/milestone/index.vue`；Server `MilestoneController`、`MilestoneEntity`。

- [x] 查询/新增/编辑/批删；GET/POST/PUT `/milestones`，POST `/milestones/batchDelete`。
- [x] 标题/描述/日期/结束日期 `end_date`/类型（work/study/life/other）/标签。
- [x] 类型/标签/日期范围筛选、日期倒序/年份分组时间线。

### REC-11 纪念日

证据：Web `my-hub/anniversary/index.vue`；Server `AnniversaryRecordController`。

- [x] GET/POST/PUT `/anniversaryRecords`、POST `/anniversaryRecords/batchDelete`。
- [x] 标题/目标日/备注/渐变颜色/图标、根据目标日自动纪念日或倒计时类型、天数展示。

### REC-12 荣誉中心

证据：Web `my-hub/honor/index.vue`、`api/core/honor.ts`；Server `HonorRecordController`、`HonorCategoryController`。

- [x] 记录列表/详情编辑/新增/编辑/单条删除（调用批删API）；`/honorRecords`，`/{id}`，`/batchDelete`。
- [x] 标题/描述/日期/颁发机构/级别/分类/自定义分类/标签/置顶/公开字段。
- [x] 分类列表 `/honorCategories`、置顶 `/honorRecords/toggleTop/{id}`、关键词/分类/级别筛选、数量与置顶统计（与实际 Web 筛选一致）。
- [x] 荣誉附件上传/鉴权预览/绑定/删除，更新保留 `files/fileIds`。依赖主 Agent BASE-07。

### REC-01 / REC-02 运动与分类

证据：Web `my-hub/exercise/index.vue`、category-config及编辑组件；Server `ExerciseRecordController`、`UserDictDataController`、`UserDictDataServiceImpl`。

- [x] 运动完整分页读取、类型/日期筛选、新增/编辑/单删/批删；`/exerciseRecord/query`、根POST、`/{id}` PUT、`/deleteBatch` POST。
- [x] 真实字段：exerciseTypeId/exerciseDate/exerciseCount/description，编辑保留 timeId；本模块实体没有重量/组数/时长，不增加虚构字段。
- [x] 按日期×类型去重次数、每月次数、类型分布；每类型独立每日运动量 MiniChart；全类型不混合单位汇总运动量。
- [x] 所有用户字典类型的分类 CRUD/状态/名称/标识/颜色/图标/排序；只读公共分类只能停启，公共删除为当前用户停用；排序逐项PUT保留模板字段，失败后重读可恢复。bank_tag 使用专属银行卡入口，本页不开放。
- [x] 首页 `/pages/records/exercise?create=1` 自动新增。

服务端 `/statistics`、`/statistics/light` 最多1000条，`/query` 的日期条件未启用。Mobile完整分页后本地日期过滤及统计，避免部分数据伪装全量；`/dashboardSummary`用于主Agent首页，不重复修改首页。

### REC-03 视频观看

证据：Web `my-hub/videoWatch/index.vue`、`api/core/bilibili-video.ts`；Server `BVideoController`。

- [x] `/b-video/query` 完整分页/状态筛选、全量本地关键词过滤、根POST、`/{id}` PUT/DELETE。
- [x] 封面/标题/URL/bvid/aid/UP主/分P/总时长/已学时长/集数/笔记/观看日期时间/四状态；分P选择累加已学时长，保留 pagesInfo。
- [x] `/getStatusCount`、`/statistics` 四状态与时长统计；官方JSONP（Web）/官方uni.request（App/MP）解析；失败可手动填写，未触真实第三方数据。

`/tagVideo`、`/syncProgress` 为浏览器脚本记录同步入口，Web本页也不调用；移动编辑通过相同实体PUT完成进度保存。小程序外部api.bilibili.com域名、App第三方访问须实际平台验收。

### REC-04 观影

证据：Web `my-hub/movie/index.vue`与详情/导入组件；Server `MovieController`、`MovieServiceImpl`。

- [x] GET `/movie/page` 分页/标题/类型/状态筛选；根POST/PUT；GET/DELETE `/{id}`；详情新增编辑字段与附属关联保留。
- [x] GET `/movie/parse-douban`、POST `/movie/import/douban/preview`、`/movie/import/douban`；Excel _Meta/Movies严格解析/文件预览/重复跳过或覆盖/结果；接入共享 native-files 官方跨端选文档/read/release，16MiB限制，App缓存文件在读取后释放；文本粘贴与剪贴板作为可用补充。
- [x] 评分1..5及显式未评分清空：第4处最小后端契约修复区分未传/空值；保存后重新读取详情，防止本地状态与持久化状态不一致。

### REC-05 阅读记录

证据：Web `my-hub/read-record/index.vue`与详情组件；Server `ReadRecordController`、`ReadRecordEntity`。

- [x] GET `/read-record/page` 分页/标题/类型/状态筛选；根POST/PUT；GET/DELETE `/{id}`。
- [x] 豆瓣解析 GET `/read-record/parse-douban`；真实字段标题/type/author/url/fileId/status/totalProgress/currentProgress/startTime/finishTime/remark完整编辑，图片上传预览；实体没有出版/ISBN/评分，不添加虚构字段。

### REC-06 微信读书

证据：Web `my-hub/weread/{index,dashboard,shelf,notes}.vue`、`api/core/weread.ts`；Server `WereadController`。

- [x] GET/POST `/weread/connection` 绑定/更换 API Key；POST `/disconnect` 确认；Key只在当前输入内，关闭/离页清空，不展示保存凭据或写日志。
- [x] POST `/sync?mode&baseTime`、GET `/stats?mode&baseTime` 周/月/年/累计与日期选择、时长/日数/已读完/日均/排名/趋势；失败保留已读数据并恢复上次周期选择。
- [x] 书架关键词/已读/未读/有笔记筛选、最近阅读/书名排序；GET `/progress?bookId` 详情及原平台打开。
- [x] GET `/notes?bookId` 笔记本、划线/想法/书评、章节/时间/关联想法、内容搜索/复制；快速切换与离页旧请求隔离。

读取沿用公共request，sync/notes最长120秒，连接/stats30秒；跨端复制使用uni.setClipboardData。Web实际源为趋势图而非热图，迁移使用共享MiniChart。

### REC-09 活动

证据：Web `my-hub/performance/index.vue`与编辑组件；Server `PerformanceController`、`PerformanceEntity`。

- [x] GET/POST/PUT `/performance`、DELETE `/{id}`；完整分页读取/活动类型/关键词筛选、总票价统计。
- [x] performanceName/performer/performanceType/performanceDate/city/venue/ticketPrice/seatInfo/duration/rating/review/purchasePlatform/orderNumber、字典/附件预览上传/完整绑定列表。
- [x] 第3处后端兼容修复恢复附件替换/清空闭环：未传保留、[]解绑而不删文件；所有绑定ID校验当前用户上传归属，已验证活动归属后事务内同步。

### REC-13 反馈中心

证据：Web `my-hub/feedback/index.vue`；Server `feedback/api/FeedbackController`。

- [x] POST `/feedback` 提交标题/内容/类型/附件；GET `/feedback/my` 分页/状态筛选。
- [x] GET `/feedback/my/{id}` 详情与回复；POST `/feedback/{id}/comment` 评论/附件。
- [x] DELETE `/feedback/{id}` 撤销，保留服务端可撤销状态限制；未开放管理员处理。

### GOODS-01 设备墙

证据：Web `my-hub/device/index.vue`、`api/core/device.ts`；Server `DeviceController`。

- [x] GET `/device/query`、POST根、PUT/DELETE `/{id}`；名称/spec/type/status/purchaseDate/endDate/purchasePrice/purchasePlace/remark/fileId完整编辑。
- [x] 用户与系统字典、分类筛选、累计价值/使用天数、附件图片上传预览绑定。

### GOODS-02 衣柜（已转交 mobile_foundation，本文不宣称交付）

证据：Web `wardrobe/index.vue`及编辑/分类组件；Server `WardrobeController`。

- [ ] `/wardrobe/items` GET/POST，`/items/{id}` GET/PUT/DELETE；名称/分类/品牌/颜色/季节/尺寸/购买/价格/状态/穿搭次数等。
- [ ] `/wardrobe/stats` 统计、分类/季节/状态筛选；图片上传/鉴权预览/保留。
- [ ] `/wardrobe/categories` GET/POST，`/categories/{id}` PUT/DELETE；分类维护。

### MEMBER-01 会员

证据：Web `membership/index.vue`、`api/membership/index.ts`；Server `membership/api/MembershipController`。

- [x] GET `/membership/list`、`/stats`、`/{id}`，根POST/PUT，DELETE `/{id}`。
- [x] 名称/平台/种类/开始结束/价格/计费周期/自动续费/状态/备注等完整字段。
- [x] 状态/分类/关键词筛选、有效/即将到期/过期与月费统计、编辑保留状态及关联字段。

## 后端最小契约修复

主 Agent 已明确扩展 W1-B 范围，四处契约缺口仅修改对应文件，不触生产数据：

- `aio-life-server/src/main/java/top/aiolife/record/api/ThoughtController.java`：旧逻辑只插入/修改事件，遗漏项不删除。新增完整事件列表的删除同步，条件限定 thoughtId；已验证更新成功才处理，删除前完成各事件归属校验，事务防止部分更新。未传/空/旧ID/新ID/跨闪念ID均有模拟回归。
- `aio-life-server/src/main/java/top/aiolife/feedback/api/FeedbackController.java`：旧 GET 忽略平铺过滤条件；`listMy` 添加 `@QueryParams`，沿用现有泛型DTO URL绑定器。
- `aio-life-server/src/main/java/top/aiolife/record/api/PerformanceController.java`：完整附件列表同步，新增/更新事务，当前用户文件归属校验，未传保留/空列表解除。新增 `PerformanceFilesContractTest` 5项覆盖。
- `aio-life-server/src/main/java/top/aiolife/record/pojo/req/MovieReq.java`及`record/service/impl/MovieServiceImpl.java`：JsonSetter只标记实际rating入参，显式null通过用户/记录限定wrapper更新；省略不生成rating更新，未改全局字段策略。新增 `MovieRatingContractTest` 4项覆盖省略/null/数值/非法/外人记录。
- 测试：新增 `ThoughtEventsContractTest.java`；扩展 `QueryHttpContractTest.java`，用 MockMvc 检查 `/feedback/my?page=3&pageSize=20&status=PENDING&feedbackType=BUG` 实际泛型绑定。

## 请求生命周期

本Agent全部原生页面全部复用业务目录内 `services/records/page-scope.ts`。每次读取、详情和 mutation 都比对请求 token 与页面 revision；离页关闭编辑/详情，回页新请求与旧请求隔离，跨账号清空业务列表/附件/表单。无真实用户数据缓存。

## 本批验证

- `node --test aio-life-mobile/tests/records*.test.mjs`：10/10通过，纯模拟。覆盖目标长ID/关联、周期边界、校验、待办排序与实际请求方法/路径/分页参数。
- `npx playwright test tests/e2e/records-tasks.spec.js --workers=1 --reporter=line --output=test-results/records-run`：7/7通过，模拟API。目标390/768/1440深浅布局、保存失败保留与重试、父目标/行动计划/ID保留；待办明细完成/关注与关联保留。
- 新增 `records-more.spec.js`：运动390/768/1440深浅布局与关联/失败恢复；设备、电影、活动、视频、闪念、笔记、纪念日、里程碑、荣誉、会员编辑保存及原关联保留；微信读书picker真实操作、详情进度、划线与关联想法。
- `mvn test -Dtest=MovieRatingContractTest,PerformanceFilesContractTest,ThoughtEventsContractTest,QueryHttpContractTest -q`：46项通过，退出0，定向Mock/MockMvc，不连数据库。
- 全部所辖页面常规SFC parse/compileScript/compileTemplate 已通过；简单类选择器检查已通过；整仓Vapor构建由主 Agent统一；后端联调、微信模拟器/真机、App Vapor真机未验证。

## 本批原生路由

`/pages/tasks/todo`、`/pages/tasks/goals`、`/pages/records/notes?kind=think|memo`、`/pages/records/anniversary`、`/pages/records/milestones`、`/pages/records/honor`、`/pages/records/feedback`、`/pages/member/index`。

新增：`/pages/records/exercise`、`/pages/records/categories`、`/pages/records/video`、`/pages/records/library?kind=movie|read`、`/pages/records/weread`、`/pages/records/activity`、`/pages/goods/devices`。以上待主 Agent统一Vapor构建与全平台验收；衣柜由foundation单独交付。

## 验证边界与明确残项

- 15个所辖 .uvue 页面 SFC解析/script/template检查通过；Web API模拟测试不等于实际后端联调。
- 真文件上传/鉴权文件预览、真实豆瓣服务解析/真实B站官方第三方解析、微信读书真实账号同步均未连生产测试；后续使用隔离测试账号验收。
- App xlsx通过官方uni.chooseFile与content URI缓存复制实现，项目CLI 5.30 alpha与本机HBuilderX5.26不匹配；App Vapor真机/文件选择、微信模拟器/真机/合法域名需主Agent发布前验证。
- Web真手机键盘、安全区与弹窗手势、跨平台图标和图表还需平台验收；本批不把常规SFC编译报告为App/WX已通过。
- 所有用户分类排序非后端原子批量：逐项PUT，失败保留错误及已加载数据并重读；只读公共分类不能移动，符合服务端仅能修改状态约束。
- 衣柜范围已交 mobile_foundation，本文未代填其完成结果。

最终专项合跑：`npx playwright test tests/e2e/records-tasks.spec.js tests/e2e/records-more.spec.js --workers=1 --reporter=line --output=test-results/records-final-run`，**16/16通过，46.2秒**。所有用例均模拟API，未写真实数据。业务源码已通知主Agent冻结，未提交或推送。
