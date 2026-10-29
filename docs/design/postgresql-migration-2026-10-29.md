# PostgreSQL 改造范围与迁移方案

日期：2026-10-29。状态：源码盘点完成，方案待实施；不代表数据库、应用或部署已切换。

本轮仅读取本地源码、配置和公开技术资料，新增本方案及文档索引。未连接现有业务库，未读取业务数据，未执行 DDL、DML、Flyway、应用启动、容器启动或部署。后续读取业务库、备份、停写及正式切换均不包含在本轮执行范围内。

## 1. 决策与边界

目标是将 AIO Life 的关系型业务存储统一迁移至 PostgreSQL，保留 Spring Boot、MyBatis-Plus、独立 Flyway 工具及 Hasura v3/DDN 查询架构。应用最终只支持 PostgreSQL，不维护长期双库分支、双写或旧客户端兼容层。

建议以 PostgreSQL 18 作为目标大版本；实施时锁定当时受支持的补丁版本与镜像 digest，并验证 pgJDBC、Flyway、Druid 和所选 Hasura Connector 的组合。当前官方资料确认 PostgreSQL 18 受支持、Flyway 提供 PostgreSQL 模块，MyBatis-Plus 提供 PostgreSQL 方言；这些资料不等于项目已完成联调。[版本政策](https://www.postgresql.org/support/versioning/)、[Flyway PostgreSQL](https://documentation.red-gate.com/flyway/reference/database-driver-reference/postgresql-database)、[MyBatis-Plus 支持范围](https://baomidou.com/introduce/)。

采用“隔离开发与迁移演练 → 业务停写 → 一次性复制 → 对账与验收 → 切换”的路线。停写时长必须由实际数据规模和演练测量确定；本轮没有业务库数据，不能给出可靠分钟数。如果演练时长超过可接受窗口，再单独设计 CDC，不预先引入双写复杂度。

本次不合并 RLS、pgvector、PostGIS、全量 Boolean 化或业务字段重构。Redis、MinIO、Neo4j 继续各自承担原职责。数据库迁移不自动替代图数据库或对象存储。

外部契约保持：ID 为 string，金额精度不变，本地日期 yyyy-MM-dd、本地日期时间 yyyy-MM-dd HH:mm:ss，时迹开始/结束仍为当天分钟；分页 page/pageSize 和总数类型不变。Query 的 REST、GraphQL、MCP 各自保留现有协议。

## 2. 盘点依据与已知限制

本轮基于工作区文件，主仓库 HEAD 为 2dac559，Server 为 31a173a，Query 为 82939e6；三个仓库均存在已有未提交修改，因此不能仅按 HEAD 复现本次快照。Server 的迁移工具、首页/理财 Mapper、导出代码及 Query 的 Connector 补丁有并行修改。实施前重新核对差异，不覆盖或回退这些工作。

| 范围 | 本轮静态盘点 | 含义与限制 |
| --- | --- | --- |
| Server SQL | 2 个 B、29 个 V，共 31 个 SQL 文件 | 历史文件不能重写；新目标结构需从完整迁移结果生成，不能只翻译 B |
| 业务表 | 当前冻结基线声明 72 张，V 中未发现额外业务 CREATE TABLE | 这是源码表目录，不是现有业务库实测表数；后续要在隔离 MySQL 执行完整链确认 |
| 实体映射 | 73 个含 TableName 的 Java 文件，对应上述 72 个表名 | time_record 在 TimeRecordEntity 和 TimeRecordReq 中重复声明；不能按实体文件数推断表数 |
| Mapper | 84 个 mapper 目录 Java 文件、3 个 Mapper XML | 还包括动态 SQL provider、Wrapper 片段和字段映射 |
| 测试 | 32 个测试文件匹配 H2/JDBC/MySQL 模式标记；47 个匹配 MySQL 相关标记 | 只是静态命中文件，范围重叠，不能相加或视为需重写的测试数 |
| Query | 6 个主数据集、111 个字段；1 个时迹分类派生关系 | 必须保持字段白名单、聚合、关联权限与精度 |
| Web | 发现直连 MySQL 的图标检查脚本 | Web 页面本身不直接依赖数据库驱动 |
| 移动端/插件 | 本轮相关脚本扫描未发现数据库直连依赖 | 仍需覆盖 API 消费和真实业务回归，不表示完全免验收 |

[当前数据库初始化文档](../../aio-life-server/docs/数据库初始化与验证.md)记录：历史接入版本为 20261028.06，20261029.01 采集来源修复已执行；还记录了历史备份表、停用 LLM 表及其他结构差异。这些是仓库记录，**本轮没有重新验证业务库版本、结构、数据量或迁移历史**，不得把该记录当作实际迁移清单。

## 3. 按仓库划分的完整工作包

| 工作包 | 主要入口 | 必须交付的变化 |
| --- | --- | --- |
| Server 连接与方言 | pom.xml、src/main/resources/application.yml、config/MybatisPlusConfig.java、core/query/BoundedPaginationInnerInterceptor.java | pgJDBC、PostgreSQL URL/参数、POSTGRE_SQL 方言；保留 JDBC 主事务管理器，避免与 Neo4j 冲突 |
| Server SQL 与映射 | 全部 Mapper、3 个 XML、动态 provider、相关实体与服务 Wrapper | 方言替换、显式字段类型、空值/大小写/排序语义和受影响事务 |
| Server 结构与种子 | sql/migrations/、scripts/generate_regions.py、scripts/generate_bank_dictionary.py | PostgreSQL 新库路径、后续 V、中文 COMMENT、索引/约束、离线种子生成器 |
| Flyway/预检 | tools/flyway/pom.xml 与 migration 包下 5 个工具类 | PostgreSQL 模块、驱动、精确迁移目录、pg_catalog 结构采集、契约格式升级、安全回调与隔离集成测试 |
| 一次性搬迁工具 | 建议新增 tools/database-transfer/ | 显式源/目标、只读源、分表字段映射、全量复制、断点与摘要、异常报告、复核；不进入业务应用 |
| Server 测试/CI | src/test/、tools/flyway/src/test/、.github/workflows/docker-publish.yml | 真实 PostgreSQL 初始化/升级/并发/业务测试；替换 H2 MySQL 方言夹具；发布前门禁 |
| Query Connector | connector/、deploy/connector.Dockerfile、scripts/build_connector.sh、scripts/build_engine.sh | 选定 PostgreSQL NDC、固定来源/版本/镜像、协议兼容、认证与只读限制；复核是否还需要定制补丁 |
| Query 元数据与输出 | scripts/build_metadata.py、datasets.json、relationships.json、QueryDatasets/QueryCompiler/QueryService | 类型/操作符/聚合映射、分类派生查询、精度与时间输出、发布版本指纹 |
| Query 部署与测试 | deploy/compose.yml、readonly-account.sql.example、scripts/test_e2e.sh、test_category_relationship.py、tests/、src/test/、CI | PostgreSQL 权限示例、连接配置、真实引擎链测试及 Connector 构建发布能力 |
| Web | scripts/icons/check_database.py 及依赖/说明 | 替换 PyMySQL 与 MySQL 元数据查询；仍为受控只读检查，不随构建自动连接业务库 |
| 主仓库编排与交付 | docker-compose.yml、scripts/push-repositories.py、.github/workflows/api-contracts.yml、部署说明 | PostgreSQL 实例/外部实例接入方案、统一交付覆盖 Query、固定版本组合、契约联合检查 |
| 文档与规范 | 各仓库 AGENTS/README、数据库初始化/表结构/SQL规范、Query 部署和来源文档 | 实施后更新当前技术栈，保留历史记录的日期与边界；本轮不提前改成“已迁移” |
| API 消费端 | Web、Mobile、Chrome 插件、API Skill、Query/MCP 使用方 | 原则上不改对外接口；通过真实后端回归确认。DTO 真有变化时走生成脚本，不手改生成文件 |

路径中的 Java 包均位于 Server 的 src/main/java/top/aiolife/ 下。关键源码入口和表目录见附录。

### 3.1 已确认的 SQL 改造点

| 文件/位置 | 当前实现 | 目标处理与验收 |
| --- | --- | --- |
| BoundedPaginationInnerInterceptor | 固定 DbType.MYSQL | 改 POSTGRE_SQL，验证分页 count、上限、空页和排序 |
| IMovieMapper、ReadRecordMapper、IBVideoMapper.xml | FIELD(status, ...) | 改参数绑定的 CASE 顺序，明确未知状态位置、日期 NULL 排序和 ID 兜底 |
| IBVideoMapper.findOwnedByBvid | CAST(... AS BINARY(20)) | PostgreSQL 下按大小写敏感的精确规则比较，验证大小写不同 BV 号及尾随空格；不要机械换 BYTEA |
| DeviceExpenseMapper.bind | ON DUPLICATE KEY UPDATE | ON CONFLICT(expense_id) DO UPDATE；保持复用原关联 ID/创建审计、用户归属、软删除后重新绑定；核对 affected rows 语义 |
| WereadServiceImpl | JSON_REMOVE、JSON_SET、JSON_EXTRACT/UNQUOTE 以及 Wrapper 内 SQL | JSONB 删除/更新/提取操作移入 Mapper；保留 connectionVersion 并发条件，旧同步响应不得覆盖新连接 |
| UserMapper、AccountErasureMapper、各类用户锁 Mapper | user 表和反引号 | 目标物理表建议命名 sys_user，统一更新 TableName、外键、手写 SQL、白名单和迁移映射；对外用户 API 不变 |
| SqlDatasetDefinition.identifier、ExportDatasetSql | 动态标识符返回反引号 | 改 PostgreSQL 标识符引用；继续仅接受发布白名单、绑定值参数；不能引入用户可控表名 |
| ExportDatasetMapper/SqlExportDataset | Map 结果和字符串游标 | 核对 bigint 游标的 JDBC 绑定、JSONB 的 PGobject、bytea、timestamp、别名大小写；保持 Excel 单元格和快照格式 |
| PublicImageMapper、ExportSecurityMapper 等 | 其他反引号 | 逐个改写并回归权限、归属和文件引用，不只处理 user 表 |
| 所有 ORDER BY 与 Wrapper 排序 | 部分可空时间/排序字段依赖数据库默认行为 | 对可空字段明确 NULLS FIRST/LAST，分页必须有稳定兜底；首页最近项、阅读/影视、消费日历、Query 一起验收 |
| 所有锁查询与事务 | FOR UPDATE、主表/用户行锁、条件更新 | 保留锁顺序及禁止缓存要求；空结果不等于锁住将来的插入，需由现有父行锁/唯一约束保护并发不变量 |
| 所有统计/结果映射 | COUNT/SUM、数值比较、SQL 别名 | 核对 count/sum 的 bigint/numeric、NULL 聚合、Integer 溢出、Map 别名折叠；金额不用浮点类型 |

LIMIT、COALESCE、CASE 和普通 JOIN 等很多语法可直接保留，不应为迁移无故重写。PostgreSQL 的默认 NULL 排序与现有 MySQL 行为可能不同，应显式定义。[排序规则](https://www.postgresql.org/docs/18/queries-order.html)。

### 3.2 驱动、连接池与事务

- 将 MySQL 驱动换为 org.postgresql:postgresql；驱动与服务端版本在隔离环境锁定。Druid 先保留，验证连接校验、连接断开恢复、批处理、SQL 解析与超时；不同时更换连接池。
- 连接环境变量采用明确的 JDBC URL、用户名和密码分离注入；更新全部 README、CI、Compose 和本地启动说明。去掉 useSSL、serverTimezone、allowPublicKeyRetrieval、autoReconnect 等 MySQL 参数。
- pgJDBC 的 connectTimeout/socketTimeout 单位为秒，不能直接照搬当前 10000/30000 毫秒数值；保留连接、语句、锁等待和事务各自的时限，生产使用验证证书与主机名的 TLS。[驱动配置](https://jdbc.postgresql.org/documentation/use/)。
- 明确应用连接的 TimeZone、search_path 和事务隔离级别，不依赖数据库或主机默认值。建议 schema 使用固定 public 并收紧 CREATE 权限；部署中的公共扩展或其他应用不得共享业务写权限。
- PostgreSQL READ COMMITTED 作为普通事务目标；ExportSnapshotService 保留明确的 REPEATABLE_READ 一致快照。捕获后的文件写出、上传仍在事务外；核验 checkpoint 等调用的事务传播。
- 复核 PostgreSQL 错误后事务进入失败状态的行为；不能在同一失败事务中捕获唯一冲突后继续查询/写入。幂等插入优先使用明确冲突目标；必须重试的死锁/序列化失败在完整事务边界有限重试，外部通知不得重复发送。[事务隔离](https://www.postgresql.org/docs/current/transaction-iso.html)。

## 4. 结构和字段映射规则

目标以**隔离库执行完整现有迁移链后的结构 + 当前实体/接口契约**为设计依据，再与将来授权获得的实际源库结构逐表比对。当前 B 含随后被 V 修改的自增、字段命名与审计定义，不以单个 B 为最终结构。

| 源字段/机制 | 目标规则 | 必须核对 |
| --- | --- | --- |
| bigint ID、用户归属 | bigint，应用雪花 ID 生成，保留原值 | 不能重新编号；ID 在 API 中仍为字符串；Java String 绑定 bigint 的地方显式转换/映射 |
| varchar ID、文件 ID、时迹 ID 等 | 保留现有文本类型与语义 | 不强行把全部 ID 改 bigint；检查每个引用字段和索引类型一致 |
| 自增列 | 按当前完整迁移结果判断是否仍需 identity | 不根据旧 B 恢复已取消自增；确需 identity 时导入后校准 sequence，并测试下一次插入 |
| tinyint、状态/逻辑删除 | smallint 或合适整数类型，保留 0/1 和枚举值 | 对纯 0/1 字段加 CHECK；多值状态不能加布尔约束；现有 Java Boolean 字段需显式 type handler/转换测试 |
| smallint unsigned | 按实际范围选择 smallint/integer 并加 CHECK | 时迹分钟和时长按现行 DTO/业务规则，不能照旧注释把上限机械设为 1440 |
| decimal(p,s) | numeric(p,s) | 金额、评分和身体数据保留每列精度、scale、NULL；汇总使用 BigDecimal |
| varchar/char/text/mediumtext/longtext | 保留必要长度，长文本用 text；逐列评估 char 空格语义 | NULL 与空字符串不同；不能静默截断、去空格或把代码字符串数值化 |
| JSON | jsonb，保留原有 API 表示 | 字符串实体使用字段级 JSONB TypeHandler，结果仍按现有接口返回；验证 SQL NULL、JSON null、字符串、数组和对象；不全局设置 stringtype=unspecified 绕过绑定 |
| BINARY(32) 指纹 | bytea + octet_length(...)=32 约束 | byte[] 保持原始字节；密文、指纹和密钥版本不重算、不转普通字符串 |
| DATETIME / LocalDateTime | timestamp without time zone，精度按当前列约定 | 保持业务墙上时间；不自动转 UTC、不整体改 OffsetDateTime |
| MySQL TIMESTAMP | 逐列核对绝对时间语义与读取时区后映射 | 对 last_active_at、login_log.created_at 等明确源会话时区，必要时用 timestamptz 并在 API 边界转换；禁止整库统一偏移 8 小时 |
| DATE、时迹分钟 | date、整数分钟 | 保留本地日期及含首尾分钟的 duration 规则，不借迁移改时间业务算法 |
| ON UPDATE CURRENT_TIMESTAMP | 优先由现有应用审计填充和 Mapper 显式更新覆盖所有写路径 | 不无条件批量加 trigger；核对导入/修复路径、NOW 的事务起点语义，必要时使用 statement_timestamp；复制保留旧审计值 |
| active_flag 生成列 | 对 user、membership_provider 使用等价的部分唯一索引 | 与原软删除及 NULL 语义对照；不要把其他全行唯一索引一律改成仅有效行唯一 |
| 索引、外键、CHECK、注释 | 明确重建；表/列使用 COMMENT ON | 索引名在 schema 内冲突、63 字节标识符限制、复合列顺序、条件、外键动作必须纳入检查 |

device_expense.expense_id 当前要求**含已解绑记录也唯一**，迁移时继续全行唯一，不能为了应用部分索引而改变绑定规则。

数据迁移先保留所有当前业务表的逻辑删除行。过去取消的 LLM 表、迁移备份表及其他未知表只登记到源库排除/归档清单，不初始化到目标业务 schema，不删除源表；必须查清是否存在有效业务引用，未分类的表/列会阻止切换。

JSONB 支持与日期类型依据：[JSON 类型](https://www.postgresql.org/docs/current/datatype-json.html)、[日期时间](https://www.postgresql.org/docs/18/datatype-datetime.html)、[部分索引](https://www.postgresql.org/docs/current/indexes-partial.html)。

### 4.1 排序规则不能做字符串替换

MySQL utf8mb4_unicode_ci、ascii_bin、utf8mb4_bin 不存在可机械替换的完全等价 PostgreSQL 名称。为每个标识/搜索/排序字段记录：大小写、重音、尾随空格、Unicode 规范化、唯一性及 LIKE 行为。

- 手机号/微信 ID、BV 号、对象键、订单号和密码学指纹采用各自业务明确的精确比较；文件对象键保持字节内容。
- 登录名、邮箱、平台编码、字典名称等先从现行代码和测试确定规则，再选择归一化表达式索引或 ICU collation；不能假设 LOWER/ILIKE 就等同于旧 collation。
- 普通关键词查询保留既有大小写行为；对中文、拉丁大小写、重音、Emoji、空格编写样例。选择 ICU 时固定镜像中的相关版本，记录升级后重新验证/重建索引的要求。
- 目标唯一规则下存在重复数据时，输出受控冲突清单并阻止搬迁完成，不自行合并或删除用户数据。

[PostgreSQL collation 说明](https://www.postgresql.org/docs/18/collation.html)。

## 5. Flyway 与历史脚本的衔接

MySQL 到 PostgreSQL 是跨引擎数据搬迁，不能写一个 ALTER 脚本在原库内“升级为 PostgreSQL”。两个数据库必须有独立且真实的迁移历史。

建议目录方案：保留现有 sql/migrations/ 根层 MySQL B/V 原内容和校验和，在其下新增 postgresql/ 作为唯一 PostgreSQL 迁移位置。旧根层仅用于一次性源结构参考和回退版本追溯，不继续开发 MySQL 运行时兼容。**源工具不能递归扫描包含 PostgreSQL 文件的新目录**：演练源参考结构使用冻结的 MySQL 修订及独立工作目录，目标工具只指向 postgresql/。这仍统一位于 sql/migrations/，不另建历史 SQL 执行目录。

该目录变化需要同步修改 MigrationProject 对路径后缀的校验、sources 摘要采集及安全回调；不能只改 POM。当前 migrations 目录及源码摘要格式不可直接复用为目标结构契约。

目标从新的 V 初始化结构开始，后续 V 补种子和升级，**本轮不生成新 B，也不改写任何已有 B/V**。正式版本号在实施时按项目日期序列选定且唯一，本文不提前占号。未来用户选定合并节点后，才生成 PostgreSQL 的完整 B。

两条初始化路径必须明确：

1. **全新空库**：V 结构 → V 缺省种子 → 后续 V，建立真实 PostgreSQL flyway_schema_history。
2. **从 MySQL 搬迁**：V 结构 → 复制既有数据 → V 缺省种子（仅补缺、不得复活软删除或覆盖配置）→ 后续 V。迁移工具使用明确 target 停在结构版本，导入成功后再前进。结构变更应在导入版本设计中确定，不能在现场猜测执行顺序。

种子不能先插入再用 ON CONFLICT DO NOTHING 直接吞掉源业务数据：系统菜单/字典等必须区分“相同业务键不同 ID”“相同 ID 不同业务键”，维护原有 ID 与引用；无法无损合并则失败。data_export_coordinator 等运行基础行也纳入规则。

源 MySQL 的 flyway_schema_history 只随受控备份留存，不复制到 PostgreSQL 历史表、不登记相同的虚假 BASELINE、不运行 repair 掩盖差异。

SchemaSnapshot/SchemaContract/SchemaTool/MigrationGuard/MigrationProject 要覆盖 PostgreSQL 的 schema、表、字段/类型/精度/默认值/可空、identity、生成表达式、索引条件/表达式、唯一约束、外键、CHECK、COMMENT 及 collation。保留禁 clean、禁自动 baseline、禁乱序、禁跳过执行和非空未知库拒绝迁移；格式升级后旧契约明确拒绝，实际结构预检与 flyway validate 仍分别执行。

## 6. Hasura / Query 专项方案

### 6.1 连接器选择和协议配对

使用 PostgreSQL NDC，继续 Hasura v3/DDN，暂不改成 Hasura v2。官方存在 [PostgreSQL Connector](https://hasura.io/connectors/postgres) 和 [ndc-postgres 仓库](https://github.com/hasura/ndc-postgres)，但具体生产组合尚未验证。

当前 MySQL Connector 基于 ndc-jvm-mono 7ea80f966e7abfeaba56957291ff555649e21809，NDC 0.1.6；引擎源码构建脚本固定 graphql-engine 45729d9437d93a2b54fc592a10e29e8267d4dfa7。选定 PostgreSQL Connector 后，先核对实际 /schema、/capabilities 和配置规范，验证现有引擎可用；若需要升级引擎，则把引擎、Connector、OpenDD 元数据作为同一发布组合测试和锁定，不能只替换镜像名。

必须核验所选 commit/镜像的许可证、生产运行条件、平台架构和供应来源。当前仓库已有 Connector 授权未完成确认的记录，不能据“官方支持 PG”宣布原有许可问题已解决；此处是发布依赖核验，不是本轮联网或操作业务库的理由。

### 6.2 保留的行为

- 6 个数据集：time_record、exercise_record、read_record、movie、b_video、performance；共 111 个字段，不扩大到全库自动公开。
- time_record.category 派生关系：公共分类加当前用户覆盖，最大有效覆盖 ID 优先；每条时迹最多一个分类；停用历史分类可读，删除/缺失/其他用户私有分类不可读。
- 派生关系优先使用受控静态 native query；若所选 Connector 不支持同等行为，则由后端迁移维护专用视图，限制 SELECT 列并验证视图所有者与调用者权限，不能绕过行过滤。
- ModelPermissions 的可信 userId 与 is_deleted=0 过滤、二级锁、字段白名单、一次性执行票据、请求上限、超时、审计及错误拒绝返回行为全部保留。
- PostgreSQL 只读角色仅有 CONNECT、schema USAGE 和白名单列 SELECT，无表/函数创建、写入、DDL、可写函数执行权限；默认只读事务作为附加措施。Connector 服务鉴权、禁止请求覆盖连接串、mutation/explain 的原有限制要逐项验收。不能仅因元数据不显示 mutation 就认定底层不可写。
- 大整数、decimal、sum/count、SQL NULL/JSON null、日期与时间在 Query 网关归一化；对外 ID 始终字符串，原有数值/字符串输出契约不随 NDC scalar 改变。未加引号别名被折叠的情况也要验证。
- 发布指纹同时包含数据集/关系、生成器与 Connector 映射版本，不能误用旧元数据或旧执行票据。

需要重写 build_metadata.py 中 MySQL JDBC 配置、INT8/INT64/BIGDECIMAL 等映射及固定 capabilities，不能把 PostgreSQL 的 /schema 结果假定成当前手工构造的 NDC 结构。

当前 scripts/test_e2e.sh 仍引用旧 sql/1_init_table/2026-08-18_init_all_tables.sql 路径；迁移时一并接入后端唯一 Flyway 初始化入口。当前 Query CI 主要验证网关/元数据/运行镜像，须增加真正的 PostgreSQL → Connector → Hasura → 网关集成链，并记录源码引擎与本地开发镜像的区别。

## 7. 一次性数据搬迁设计

建议用独立 Java 21 工具读取明确授权的 MySQL 源、通过 PostgreSQL COPY FROM STDIN 或参数批量写入预先建好的目标表。该工具属于离线迁移，不进入业务 Service；不能为业务代码引入直接 JDBC 例外。COPY 支持显式列与格式，需严格区分 NULL、空串、换行与二进制，禁止错误跳过。[COPY 官方说明](https://www.postgresql.org/docs/18/sql-copy.html)。

不采用“自动推断表结构后直接导入”的黑盒流程。每张表维护一条迁移映射，包括：源/目标名、列名与顺序、类型/转换、主键和稳定分批键、依赖、是否复制逻辑删除行、特殊值策略、核验规则。映射覆盖附录 72 表，并要求所有源额外对象有明确去向。

### 7.1 源数据获取前的门禁

以下均是后续步骤，本轮未执行：

1. 在隔离环境证明工具只能读源库、只能写指定的新目标；要求源目标明确区分，拒绝相同实例/库和非空未知目标，日志隐藏凭据及业务正文。
2. 获得后续业务库访问授权后，用只读账号获取实际服务器版本、引擎、字符集/collation、时区、SQL mode、DDL、约束/索引/触发器/视图、Flyway 历史、行数/容量；不可为了预检先“修复”源库。
3. 输出源结构差异及字段映射清单。扫描目标约束冲突、孤儿引用、缺失必填、零日期/非法日期、越界整数、非法 JSON、文本 NUL、长度/编码和二进制长度；错误需要明确处理规则，默认遇错停止。
4. 不执行过去登记之前的迁移，不把实际源库伪装成新库结构。缺字段只能按经审阅的映射给目标补默认/NULL；无法可靠转换的数据阻止切换。

### 7.2 复制与恢复

- 本轮演练先用合成数据和本地隔离 MySQL 完整迁移链；实际数据演练只能在获得相应授权后使用受控备份恢复出的隔离副本。
- 正式复制在所有写入来源停止后，建立一致快照。多个独立只读连接不能被视为天然同一个快照；通过停写后冻结源数据或一个明确共享的一致快照策略保证跨表一致。
- 复制所有需要保留的业务行，包括逻辑删除、管理员配置、已停用的业务预设和业务审计；源库仍完整保留。
- 优先按外键拓扑顺序导入。若存在循环外键，使用正式迁移支持的“先结构、后约束”路径，导入后全部验证；不长期禁约束，不使用全局禁触发器的权限绕过。
- 每批记录运行 ID、映射版本、源快照标识、主键范围、行数和摘要。断点续跑只允许同一源快照/映射；目标已存在行必须核验一致性，不能覆盖不同内容或跳过冲突。
- 失败时目标不对外服务；优先新建另一个隔离目标重新导入，不能对业务连接运行 clean/自动 truncate。原失败目标保留报告后按明确范围清理。
- 导入后完成序列校准（若有）、索引/约束验证、ANALYZE 和种子补缺。临时 staging 表放在隔离 schema，并在验收前清理或禁止应用访问；结构检查不扩大业务表豁免范围。

### 7.3 核验标准

按表、用户和逻辑删除状态核对计数；比较主键集合、空值分布、金额总和、时迹分钟和、文件引用、关系数量。逐行按主键分块生成规范化摘要：decimal 保留精度，JSON 对象规范化但数组保序，timestamp 按明确规则转换，bytea 按字节比较；不能比较两个数据库各自非等价的 CHECKSUM 函数。

映射引起的表名/生成列/缺省种子变化与原始业务列分开对账，只有白名单内的预期差异可以通过。用户数、数据归属、密文/指纹、软删除状态、未迁移行数等必须零非预期差异。不得以抽样一致代替全量计数、主键和分块摘要校验。

MinIO 对象不搬迁，但 file、storage_object、封面/导出产物引用及权限需要检查；银行卡和通知密钥保持可用且不写入报告。Redis 会话、分布式锁、任务去重和缓存分别处理，不进行全库 FLUSHALL。Neo4j 图数据不变，但与关系库用户 ID 的关联需回归。

## 8. 测试与验收矩阵

数据库相关测试使用真实 PostgreSQL。纯逻辑单测继续快速执行；CurrentSchema 的 MySQL DDL 拼接/H2 改写不作为 PostgreSQL 兼容证明，受影响持久化测试统一用共享隔离容器与正式 Flyway 脚本，避免逐类启动容器增加成本。

| 层级 | 必须覆盖 | 通过标准 |
| --- | --- | --- |
| 结构 | 空库初始化、导入路径、后续 V、重复 migrate、checksum、未知非空库拒绝、COMMENT、部分唯一索引、CHECK、外键、collation | 正式脚本原样执行；新库和搬迁库在预期数据差异之外结构一致 |
| 实体 | 全部业务表的 BaseMapper 全字段读写、nullable 清空、ID、JSONB、布尔映射、bytea、日期 | PhysicalTableEntitySelectIntegrationTest 改造后覆盖全部目标表，不能跳表掩盖问题 |
| 并发 | 时迹与运动联动、分类/字典/用户行锁、采集去重、设备消费重绑、银行卡排序/引用、任务租约、导出额度、账号注销 | 同用户竞争不破坏不变量，不跨用户影响；测试真实锁等待、失败事务与重试 |
| 业务 | 登录/微信/API Key、菜单权限、时迹目标待办、财务、会员衣柜、阅读影视视频、备忘闪念、身体足迹、文件/银行卡、通知/任务/导出 | 原有成功/错误语义、字段类型和权限保持，测试外部系统使用受控桩 |
| Query | 6 数据集明细/聚合、分类关系取数/筛选/排序、越权/软删除、ID>2^53、精度、空结果、超时/取消、权限拒绝和审计 | REST/GraphQL/MCP 均经过真实 Hasura/Connector；只读账号写入/DDL/非白名单读取均失败 |
| 数据搬迁 | NULL/空串、Emoji、Unicode、大小写、非法值、重复唯一键、日期边界、密文、二进制、重跑/断点/失败 | 无静默丢失、覆盖或截断；异常有明确报告；可证明完整性 |
| Web/移动/插件 | 登录、列表分页/筛选、首页卡片、财务、读写与上传、采集预览/确认、Query 消费 | API 不变；分别记录 Web、H5、微信编译、App/真机的实际覆盖 |
| 性能/恢复 | 代表性首页/列表/统计/Query/导出数据集；备份恢复、服务重启、连接中断 | 同数据与硬件对比 p50/p95、执行计划、CPU/IO；上线门槛基于演练基线制定，不凭数据库品牌承诺加速 |

实施时依次运行受影响单测、Flyway verify、后端完整测试、Query Java/Python 测试与全链 E2E；契约生成检查运行 python3 scripts/generate-api-contracts.py --check，只有 DTO 确有调整才先运行生成。移动端有最终代码提交时按规范执行一次 npm run test:commit；没有修改也要记录受迁移影响的联调范围。禁止把 H2、Mock、编译或 HTTP 200 当成真实数据库业务验收。

CI：Server 的 MySQL 8.0/8.4 运行矩阵改为选定 PostgreSQL 发布版本；一次性源转目标测试保留隔离 MySQL 夹具，仅验证搬迁，不承诺旧运行时支持。Query 发布门禁增加 PostgreSQL 全链检查。主仓库统一推送目前未包含 aio-life-query，需要扩展统一入口/联合发布清单后再交付本次多仓库变更，不能漏掉 Query 版本。

## 9. 部署、切换与回退

部署角色分为 schema owner/migrator、应用 DML、Query 列级只读、备份/监控；应用和 Query 不持有 superuser、建表和角色管理权限。收紧 public schema CREATE、固定 search_path、限制网络入口并验证 TLS。PostgreSQL 不必放进现有根 Compose；若使用独立实例，应明确持久卷、资源、备份、监控与升级责任。

PostgreSQL 备份恢复需验证 pg_dump/pg_restore；根据最终 RPO 决定 WAL 归档/PITR。监控连接池、慢查询、锁等待、死锁、磁盘/WAL、长事务和 autovacuum；不能只看健康端点。[维护说明](https://www.postgresql.org/docs/current/routine-vacuuming.html)。

### 9.1 正式切换顺序（后续需单独确认执行）

1. 固定源应用/数据库备份及目标镜像、迁移、映射、契约、Hasura/Connector 元数据版本；实测一次恢复，明确停写窗口和失败负责人。
2. 关闭所有写入入口并等待在途请求：Web/Mobile/插件/API/MCP 写操作、定时同步、通知 worker、封面/图片任务、导出 worker、账号注销与最后活跃时间刷新均须停止；不能只在网页放维护提示。
3. Drain 或明确冻结运行中的任务和租约，确保目标端不会同时发送旧通知、删除对象或重复上传；本地/其他实例也不得仍连接旧库写入。
4. 最终一致备份和源结构/数据清单生成后，按第 7 节创建全新的 PostgreSQL 目标并导入。此阶段旧 MySQL 保持停写，目标应用/worker 不开放。
5. 完成全量核验、种子和约束、结构契约检查；使用只读接口完成登录之外的可行检查。登录或访问日志等隐含写入也视为目标写入，不能声称它们仍在“零写入”阶段。
6. 先确认是否正式接受目标写入，再一次性切换后端与 Query 数据源、元数据和流量，重启应用清除本地缓存；按需失效相关 Redis 缓存及短期 Query 票据，避免大范围清会话。
7. 记录第一笔目标业务写入时间，执行受控读写冒烟和跨端检查，按顺序恢复 worker/定时任务；监控数据差异、错误率和任务重复。
8. 旧库保持冻结和受控访问，保存完整备份与回退镜像。保留周期在正式切换前确定，验证稳定后另行决定下线；不在迁移脚本中删除旧库。

### 9.2 回退边界

| 阶段 | 允许的处理 |
| --- | --- |
| 目标尚未接受任何业务写入 | 停止目标发布，核对旧库仍为冻结时状态后，用旧镜像/配置恢复原库服务；检查外部任务未重复执行 |
| PostgreSQL 已接受写入或产生外部副作用 | 不允许直接把连接串切回旧 MySQL；先停写并保存 PostgreSQL 新增/修改/删除及外部副作用清单，优先前向修复。确需回切时另行制定反向数据同步和逐项核验方案 |
| 导入失败/结构不符 | 保持目标不服务、旧库不变，保留失败证据；修正方案并重演练，不能跳过失败表、禁约束或伪造迁移历史 |

本方案不承诺“开放写入后随时零损失一键回退”。RPO/RTO、停写窗口和旧库保留期需要实际演练与用户业务要求共同确定。

## 10. 实施顺序与交付门槛

| 阶段 | 产物 | 完成条件 |
| --- | --- | --- |
| P0 本轮 | 范围盘点、方案、风险和待核验清单 | 文档与源码引用检查；不接触业务库 |
| P1 兼容性样板 | PostgreSQL 18 + pgJDBC + MyBatis-Plus + Flyway + Hasura PostgreSQL Connector 的隔离闭环 | 登录表、JSONB、时迹聚合与分类关系、ID/decimal、只读限制、锁和 NULL 排序实测通过；固定版本组合 |
| P2 结构与后端 | 全部目标表/索引/注释、V 链、结构工具、SQL/映射修复 | 全表实体检查和核心后端集成测试通过；全新与搬迁目标两条路径成立 |
| P3 Query 与外围 | 连接器、元数据、权限、测试、部署、Web 脚本和文档 | 六数据集全链通过；统一交付含 Query，API 契约不漂移 |
| P4 搬迁与演练 | 逐表映射、复制/核验工具、异常报告、完整运行手册、备份恢复证据 | 合成数据演练通过；取得后续授权后，实际源快照演练达到数据/性能/时间门槛 |
| P5 正式切换 | 经核验的版本清单、停写/切换/恢复清单、结果报告 | P1–P4 完成且明确确认正式业务库操作后执行 |

P2 的后端和结构、P3 的 Query 可以在接口契约固定后分工实施，但必须以同一目标结构和版本清单联调。阶段交付只按实际完成状态报告，不用“驱动替换完成”代表迁移完成。

当前待核验项：实际业务库结构/补丁版本/数据规模和历史差异；字段级时间与 collation 语义；PostgreSQL Connector 与现有引擎的具体版本组合及生产条件；目标机器资源与备份位置；可接受停写窗口、RPO/RTO 和旧库保留期。前四阶段中不依赖业务库的工作可在后续实施任务中先完成；不得以这些未知项为理由猜测业务数据或直接连库。

## 附录 A：业务表覆盖目录

以下来自当前冻结基线的 72 个表名，用于防漏。正式目标结构必须合并全部 V 并与当前实体核对；除 user → sys_user 的明确建议外，名称原则上保持。表目录不包含源库的历史额外表，后续必须另行分类。

| 领域 | 表 |
| --- | --- |
| 用户与访问 | user、user_bind、password_vault、user_secondary_lock_menu、user_menu_hidden、user_quick_nav、api_key、api_key_log、login_log、mail_log |
| 系统配置 | sys_work_calendar、sys_activity_log、sys_menu、sys_dict_type、sys_dict_data、user_dict_data、user_dict_type、enum_type、system_config |
| 反馈 | feedback、feedback_comment |
| 时迹与任务目标 | time_tracker_category、time_record、task、task_column、task_detail、goal |
| 荣誉与纪念 | honor_category、honor_record、anniversary_record、milestone |
| 内容 | memo、thought、thought_rela_event、record_article、record_article_annotation |
| 财务与银行卡 | expense、income、bank_card、bank_card_tag_rel、bank_card_cover_template、device_expense |
| 运动与文娱 | exercise_record、read_record、movie、b_video、performance |
| 设备会员与衣柜 | device、membership_provider、membership_record、wardrobe_category、wardrobe_item |
| 消息通知 | message、notification_channel_config、notification_preference、notification_delivery |
| 测评 | mbti_result、cbti_personality、cbti_result |
| 文件与异步图片 | file、storage_object、image_import_task |
| 首页/身体/足迹 | user_home_card_preference、user_body_profile、life_footprint、system_region |
| 数据导出 | data_export_audit_event、data_export_coordinator、data_export_grant、data_export_job |
| 定时任务 | sys_scheduled_job、sys_scheduled_job_log |

## 附录 B：优先核查的源码入口

- [分页方言](../../aio-life-server/src/main/java/top/aiolife/core/query/BoundedPaginationInnerInterceptor.java)、[MyBatis 配置](../../aio-life-server/src/main/java/top/aiolife/config/MybatisPlusConfig.java)、[基础实体](../../aio-life-server/src/main/java/top/aiolife/core/pojo/entity/BaseEntity.java)。
- [影视排序](../../aio-life-server/src/main/java/top/aiolife/record/mapper/IMovieMapper.java)、[阅读排序](../../aio-life-server/src/main/java/top/aiolife/record/mapper/ReadRecordMapper.java)、[视频精确比较](../../aio-life-server/src/main/java/top/aiolife/record/mapper/IBVideoMapper.java)、[视频 XML](../../aio-life-server/src/main/resources/mapper/IBVideoMapper.xml)。
- [设备消费 upsert](../../aio-life-server/src/main/java/top/aiolife/record/mapper/DeviceExpenseMapper.java)、[微信读书 JSON](../../aio-life-server/src/main/java/top/aiolife/record/service/impl/WereadServiceImpl.java)、[绑定 JSON 字符串实体](../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/UserBindEntity.java)。
- [个人导出动态标识符](../../aio-life-server/src/main/java/top/aiolife/export/mapper/SqlDatasetDefinition.java)、[导出 SQL](../../aio-life-server/src/main/java/top/aiolife/export/mapper/ExportDatasetSql.java)、[导出快照事务](../../aio-life-server/src/main/java/top/aiolife/export/service/ExportSnapshotService.java)、[账号注销 SQL](../../aio-life-server/src/main/java/top/aiolife/sso/mapper/AccountErasureMapper.java)。
- [结构快照](../../aio-life-server/tools/flyway/src/main/java/top/aiolife/migration/SchemaSnapshot.java)、[迁移目录和摘要](../../aio-life-server/tools/flyway/src/main/java/top/aiolife/migration/MigrationProject.java)、[H2 结构适配器](../../aio-life-server/src/test/java/top/aiolife/support/CurrentSchema.java)、[全表实体验证](../../aio-life-server/src/test/java/top/aiolife/database/PhysicalTableEntitySelectIntegrationTest.java)。
- [Query 数据集](../../aio-life-query/src/main/resources/datasets.json)、[关系](../../aio-life-query/src/main/resources/relationships.json)、[元数据生成](../../aio-life-query/scripts/build_metadata.py)、[分类派生 SQL](../../aio-life-query/connector/time-record-category.sql)、[只读授权示例](../../aio-life-query/deploy/readonly-account.sql.example)、[Connector 来源](../../aio-life-query/connector/UPSTREAM.md)。
- [Web 数据库图标检查](../../aio-life-front/scripts/icons/check_database.py)、[统一推送](../../scripts/push-repositories.py)、[Server CI](../../aio-life-server/.github/workflows/docker-publish.yml)、[Query CI](../../aio-life-query/.github/workflows/docker-publish.yml)。

## 本轮验证记录

- 已完成：源码与配置静态检索、SQL/实体/Query 数据集计数、关键映射和迁移/测试/部署入口人工核对、官方数据库/驱动/框架文档核对。
- 文档验证：29 个本地相对链接均存在；附录的 72 张表与冻结基线表名集合一致且无重复；代码围栏、索引引用和 Git 差异检查通过。检查结果仅覆盖文档，不代表迁移可执行性已验证。
- 未执行：数据库连接、真实结构/数据读取、业务测试、容器/构建、迁移脚本、数据复制、部署或性能测试。本文件所有 P1–P5 项均为计划，不是已完成结果。
