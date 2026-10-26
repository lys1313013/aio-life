# AGENTS.md

- 系统尚未正式上线，只维护当前数据结构和接口契约；不保留旧数据格式、旧客户端、旧参数或旧缓存的兼容分支，也不维护历史升级链。结构变更同步全量初始化、实体和两端调用方。

AIO Life — All-in-One 人生管理系统。本仓库保存项目文档、编排配置和开发入口；Web、后端和移动端各自使用独立 Git 仓库。

## 沟通与工作方式

- 默认中文回复，代码、命令、变量名和文件路径保持英文。结论先行、简洁直接；发现方案问题或更好的做法时直接说明。
- 修改前确认所属仓库，阅读其 `AGENTS.md` 及目标目录内适用的规范。本文维护跨仓库约定，各端实现细节见下方入口。
- 保留已有未提交修改，只调整任务相关文件。提交和推送在改动所属仓库内执行；主仓库不跟踪三个子仓库，也不记录其 commit 指针。
- 文档分类入口见 [docs/README.md](docs/README.md)。当前契约集中维护，需求草案与历史验收注明日期和适用范围；不要把历史测试结果改写为当前验证。
- 验证范围与改动匹配；纯文档修改检查差异和引用，无需运行业务测试或构建。交付说明改动、实际验证结果及未验证项。
- 凭据、Token、证书和签名文件不得提交。

## 仓库与规范入口

| 路径 | 职责与技术 | 详细规范 |
| --- | --- | --- |
| `aio-life-front/` | Web：Vue Vben Admin v5.5.9、Ant Design Vue、pnpm monorepo、Turborepo | [Web AGENTS.md](aio-life-front/AGENTS.md) |
| `aio-life-server/` | 后端：Spring Boot 3.5.16、Java 21、MyBatis Plus、MySQL（117 库为 5.7.44）、Redis、Sa-Token、MinIO | [Server AGENTS.md](aio-life-server/AGENTS.md) |
| `aio-life-mobile/` | 移动端：uni-app x Vapor，入口 `src/main.ts`，`.uvue` 页面与组合式 API | [Mobile AGENTS.md](aio-life-mobile/AGENTS.md) |
| `docs/` | 需求与技术方案 | 数据库表结构见 [数据库表结构.md](aio-life-server/docs/数据库表结构.md) |

以下脚本在主仓库执行；各端开发命令必须在对应仓库执行。

```bash
./scripts/setup-repositories.sh   # 克隆缺失的 Web、后端和移动端仓库
./scripts/pull-latest-main.sh     # 快进拉取三个仓库的 origin/main
```

拉取脚本要求子仓库处于 `main` 且工作区干净；不满足时先处理当前工作，不为拉取而丢弃修改。

## 跨端 API 契约

- 业务后端 HTTP 响应为 `{ code: 0, message: null, data: ... }`，成功码是整数 `0`；不能仅凭 HTTP 200 判断业务成功。独立 Query 服务及 MCP 工具的协议差异见 [API 参数规范](docs/API参数规范.md)和 [MCP 接口范围](docs/需求/MCP接口需求方案.md)，不能机械套用。
- ID 全程使用 **string**，包括接口、路由、表单、组件 key、比较与提交；禁止转为数字，避免大整数精度丢失。
- 后端未覆盖序列化器的 `Long/long` 响应字段默认输出字符串；`Integer/int` 输出数字。`PageResp.total` 使用字段级 `CountSerializer`，返回 `number | null`，不能仅凭字段名推断类型。
- 前端类型按实际 JSON 声明。按当前契约返回的字符串数值在读取边界解析，不能用真假值判断数量；TypeScript 类型断言不会转换运行时值。细节见 Web 规范“Long 响应与数值判断”。
- 分页新请求统一使用 `page/pageSize`，页码从 1 开始，公共每页上限 200；业务接口可采用更小上限。请求仅使用规范参数名；需要完整列表时逐页获取，不能用超大页大小绕过分页。
- 本地日期使用 `yyyy-MM-dd`，本地日期时间使用 `yyyy-MM-dd HH:mm:ss`；时迹的 `startTime/endTime` 仍为当天分钟数。请求必填、可空和范围限制以服务端 DTO 的有效校验为准，路径 ID 必须显式必填。完整约定见 [API 参数规范](docs/API参数规范.md)。
- 请求 DTO 调整后运行 `python3 scripts/generate-api-contracts.py` 同步 Web、移动端类型与字段白名单，再运行 `python3 scripts/generate-api-contracts.py --check`；禁止手改生成文件。
- 多仓库交付先在各仓库提交业务改动，再使用 `python3 scripts/push-repositories.py`：推送前自动生成并提交两端契约，所有仓库推送成功后才执行联合检查。不得以分别手动推送代替统一入口而漏同步；用户明确不测试时使用 `--skip-hooks`。入口不自动提交业务文件，前置条件和恢复方式见 [本地统一推送与联合检查](docs/API参数规范.md#本地统一推送与联合检查)。

## Web 与移动端共同 UI 规范

### 图标、表达与交互

- 同一业务在菜单、首页卡片、卡片设置和快捷导航中的图标与颜色统一引用菜单配置，禁止分别硬编码；业务关联、公共降级和图标资产同步规则见 [图标与颜色统一规则.md](docs/图标与颜色统一规则.md)。
- 含义清楚的操作或状态只展示图标，图标按钮提供可访问名称（如 `aria-label`）；含义不明确时保留必要短文案。说明优先通过问号图标按需展示，无歧义的内容不额外加问号。减少不必要的边框、分隔线和层级，保留用户需要的业务数据。
- 接口调用必须有可感知的 loading，绑定到受影响的最小 UI 单元；局部操作成功后优先更新局部状态，避免无必要的整页刷新。
- 编辑弹窗上下居中，可无 title；确认弹窗在触发按钮旁弹出。
- 适配手机、平板、桌面及深浅主题；检查平板等中间宽度，避免移动端规则造成过宽、过疏或比例失衡。

### 首页卡片跨端契约

- 首页卡片目录、配置、刷新周期、点击与导航规则统一维护在 [首页功能说明.md](docs/首页功能说明.md)，时迹设计见 [今日时迹卡片设计.md](docs/今日时迹卡片设计.md)。两端规范引用共同文档，不另写互相冲突的业务需求。
- 实现差异和未完成项见 [首页卡片核查与补齐清单](docs/mobile-migration/home-card-audit.md)；返回时效检查、本地分钟时钟和前台数据定时刷新是不同能力，不能相互替代或仅凭迁移状态判断对齐。

### Loading 高度与布局稳定

- 首页目标、纪念日、闪念等卡片及其他异步区域，首次 loading 按实际内容结构预留空间，高度尽可能接近展示态；不能统一套用骨架行数或任意大高度，也不能靠永久留白、裁切内容实现一致。
- 刷新、重试或后台更新时保留已有内容（包括空态）及高度；局部 loading 不参与布局，不增加行、不挤动标题与操作入口。
- 修改相关布局时，对比 loading、有内容、空态、错误重试和已有内容刷新时的区域高度及后续内容位置；覆盖空数据、单条、多条、长文本、三类视口及深浅主题。
- 具体实现和动态验收见 Web、Mobile 规范的“Loading 高度与布局稳定（必须遵守）”。

## Web — aio-life-front

```bash
cd aio-life-front
pnpm run dev:antd       # 启动 web-antd 开发服务器
pnpm run dev            # monorepo 开发入口
pnpm run build          # 生产构建
pnpm run lint           # 代码检查
pnpm run format         # 格式化
pnpm run test:unit      # Vitest 单元测试
pnpm run check          # 循环依赖、依赖、类型、拼写检查
```

- 别名 `#` 指向 `apps/web-antd/src/`。
- 架构、请求客户端、附件、路由权限及界面实现细节见 Web `AGENTS.md`。

## 移动端 — aio-life-mobile

```bash
cd aio-life-mobile
npm ci
npm run dev            # H5 预览：5180，代理本地后端 45678
npm run build          # H5 构建
npm run build:weixin   # 微信构建及包体检查
npm test               # 单元与 API 契约等检查
npm run test:e2e       # H5 登录与布局测试
npm run test:commit    # 提交前统一验证
```

### 开发与验证

- 页面开发和调整先查看现有 Web 实现，以业务逻辑、接口契约、信息层级及操作入口为基准，再适配移动端；具体对照验收见 Mobile 规范。
- 保持 uni-app x Vapor；App 使用匹配版本的 HBuilderX，版本要求与验证边界见移动仓库 README。
- 开发过程中按需验证，不默认运行全量测试或双端构建。准备提交最终改动时执行一次 `npm run test:commit`；纯文档、注释修改按 Mobile 规范只检查差异。
- `test:commit` 包含单元检查、完整 H5 E2E、微信构建与包体检查；E2E 已包含 H5 构建，不额外重复构建。同一代码与相关环境未变时不重复已通过检查；修复后只重跑受影响阶段，影响不明确时重新全量验证。执行与日志规则见 Mobile 规范“测试执行时机与成本”。
- 分别报告 H5、微信编译、模拟器、真机、App 和发布结果；上传成功不代表体验版、审核通过或正式发布。

### 分页与样式

- 滚动列表统一触底自动加载下一页，禁止常驻“继续加载 / 加载更多 / 下一页”按钮。`MobilePage` 监听 `reachbottom`，自有 `scroll-view` 监听 `scrolltolower`；公共 `LoadMore` 只展示加载状态和失败重试。
- 请求中不重复分页；刷新、筛选、离页后的旧响应不得覆盖新状态；到末页或返回空页时停止。分页失败保留列表和页码，在底部重试失败页，不重置到第一页；验证实际滚动触发、去重、末页停止和失败恢复。
- 间距唯一来源为 `src/styles/spacing.json`，页面和组件引用生成的 SCSS 变量或公共类，禁止复制数值。页面边距只有一个所有者，避免 `MobilePage` 与业务页重复 padding。
- 排版唯一来源为 `src/styles/typography.json`，使用语义角色，禁止业务页另建字号等数值配置。生成与验收规则见 Mobile 规范“统一间距与视觉验收”和“统一排版”。

### 微信包体

- 主包工程预算 **1800 KB**，每包硬上限 **2048 KB**。预算与重量依赖归属统一维护在 `scripts/weixin-package-policy.json`。
- 业务专属服务、解析器、资源和重量 npm 依赖必须归入对应分包，不能只登记页面分包而把依赖留在公共目录。共享小工具独立提取，禁止跨业务分包同步导入。
- 排查读取 `artifacts/weixin-size/` 的文件与模块体积报告；不能通过上调预算、删除检查或业务功能、关闭 Vapor 绕过限制。具体机制见 Mobile 规范“避免主包再次超限”。

## 后端 — aio-life-server

```bash
cd aio-life-server
mvn spring-boot:run              # API：45678，context-path /api
mvn test                         # 测试
mvn package -DskipTests          # 打包，跳过测试
```

管理端点运行在 **45679**（Prometheus、Health、Info）；日志含 `traceId` / `spanId`（Micrometer + Brave）。

### 业务模块

源码包结构为 `top.aiolife.<module>`，按业务领域垂直拆分：

| 模块 | 职责 |
| --- | --- |
| `sso` | Sa-Token JWT + Redis 认证、邮件验证码、用户绑定 |
| `system` | 用户、菜单、字典 |
| `record` | 时迹、目标、待办、理财、荣誉、备忘、通知及 LeetCode/CSDN/GitHub 同步 |
| `wardrobe` | 衣柜管理 |
| `membership` | 会员记录与统计 |
| `feedback` | 反馈提交、评论和管理端处理 |
| `relationship` | Neo4j 人际关系图谱，通过 `AIO_LIFE_NEO4J_ENABLED` 开关控制 |
| `mcp` | 自定义注解驱动的 MCP Tool 注册与认证 |

LLM 会话、消息和模型密钥业务接口、数据表及实体 Mapper 已移除。

### 数据与配置约束

- SQL 脚本遵循 [SQL 脚本规范](aio-life-server/docs/SQL脚本规范.md)：表及每个字段必须有中文 `COMMENT`，包括 ID、版本、审计和逻辑删除字段；索引、约束及迁移执行条件必须说明。
- MySQL 业务访问统一使用 MyBatis-Plus / MyBatis Mapper。禁止生产业务代码使用 `JdbcTemplate`、`NamedParameterJdbcTemplate`、`JdbcClient` 或直接 JDBC；禁止在 Service / Guard 内嵌 SQL。联表、行锁、特殊更新放入 Mapper；规则与自动检查见 Server 规范“数据库访问规范（强制）”。
- 逻辑删除使用全局配置字段 `is_deleted`；对象映射使用 MapStruct，Lombok 配合 `lombok-mapstruct-binding`。
- 数据库、Redis、MinIO、邮件等敏感配置通过 `AIO_LIFE_*` 环境变量注入。
- 邮件验证码保留单 IP、单邮箱及全局频率限制，配置前缀为 `aio.life.server.auth.code.*`。
- 定时任务使用 `@EnableScheduling`，LeetCode 同步 cron 可配置。
