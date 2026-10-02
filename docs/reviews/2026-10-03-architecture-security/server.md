# Server 架构审查

审查日期：2026-10-03（Asia/Shanghai）。结论：继续保持模块化单体合理，无需因为最近代码增长而拆微服务。Req/Query/VO 边界、微信认证职责拆分和当前 Mapper 收敛方向正确；需要优先补上跨存储一致性、事务完整性与数据库升级验证。以下是源码审查结论，不代表生产事故已经发生。

## 基线与范围

- 仓库：`/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server`。
- HEAD：`e579153`，最后提交时间 2026-10-02 23:49 +08:00。
- 2026-09-28 起共 14 次提交；窗口前基线 `64156465fe8eae58c79f21cd42153766358178f1`；累计 305 个文件变化，新增 11,787 行、删除 918 行。
- 同时检查当前未提交的银行卡 Mapper/实体/服务、文件引用 Guard 和测试。启动时 22 条 Git 状态；审查中另一个工作流加入 `AGENTS.md`、`README.md`、`PersistenceArchitectureTest.java`，末次状态为 25 条。没有修改这些业务文件。
- 已读取主仓库要求和 server `AGENTS.md`，并复核审查期间新增的数据库访问规范。当前生产源码应统一使用 MyBatis/MyBatis-Plus，报告不再把已删除的 `BankCardRepository` 当作当前问题。
- 关注最近 API 契约改造、微信登录、菜单缓存、公共卡面与对象存储；对相关存量调用路径作追踪，不宣称覆盖全部业务。

## 发现

### S1 · P2 · 二级锁缓存的提交后失效可能永久丢失，恢复后仍使用旧授权配置

**位置**：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/core/cache/MenuDataCache.java:62`（62–68），失效只有一次 `afterCommit` Redis 写入；49–58 读取版本及数据，TTL 为 5 小时。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java:579`（579–609），菜单锁数据库更新后注册缓存失效。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/core/cache/SecondaryLockMenuCache.java:45`（45–47），缓存为空时判定没有锁。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/sso/interceptor/SecondaryLockInterceptor.java:57`（57–59），未匹配到锁就放行。

**触发**：用户原来没有锁或锁范围较小，已有旧缓存；更新数据库成功后，进程在提交与回调之间退出，或回调的 Redis SET 短暂失败而旧 Redis 数据仍在。应用/Redis 连接恢复，后续请求继续命中旧版本、旧数据，直到其剩余 TTL 到期或另一次成功变更。

**影响**：数据库显示已增加的二级锁可能对已有登录会话暂不生效，最长接近 5 小时。Redis 失败时当前保存请求可能报错，但数据库无法因此回滚；不能认为请求报错就恢复了原状态。这是二级验证边界的一致性问题，不是匿名用户可以直接绕过登录。

**建议**：安全配置使用数据库持久版本，并把变更事件写入同一事务、由可重试消费更新缓存；在无法证明授权缓存版本有效时查询权威状态或拒绝受保护操作。仅在 `afterCommit` 中重试几次不能覆盖进程退出窗口，缩短 TTL 只能减小影响。

**验证/归因**：高置信度，依据完整读写调用链；近期 `80e333b` 引入。现有 `MenuDataCacheTest.java:102` 起覆盖正常提交、回滚、迟到查询，但没有提交后 SET 失败/进程恢复用例。本次未故障注入 Redis；安全专项已独立复核。由于需要数据库提交后的故障窗口，统一定为 P2，并保留其影响安全配置的高优先修复建议。

### S2 · P2 · 对象存储删除会把尚未提交文件记录的上传误判为孤立对象

**位置**：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/service/StorageAdminService.java:77`（77–85），查完 `file` 引用就立即删除对象，没有上传状态或对象年龄门槛。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/service/impl/FileServiceImpl.java:61`（61–90），先上传 MinIO，再插入 `file`，方法结束后提交数据库；URL 上传 123–139 同样顺序。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/service/StorageAdminService.java:45`（45–49），新对象可正常列出，并未排除刚上传对象。

**触发时序**：上传 A 完成 MinIO 写入，但 `file` 尚未插入或事务未提交；管理员在这个窗口列出并删除该对象；删除 B 查不到已提交引用，删除成功；A 随后提交，返回上传成功。需要管理员恰在该窗口操作，普通用户不能调用管理员清理入口。

**影响**：数据库留下有效文件记录，实际对象已经丢失，图片/附件打开失败。给删除方法单独加 `@Transactional` 不能覆盖另一个存储和上传事务。

**建议**：上传和删除按 `(bucket,key)` 使用同一互斥/持久文件状态协议，删除仅允许进入待清理状态的对象；可先增加最小对象年龄和二次核验作为保守缓解，但不能将年龄门槛当作严格原子性保证。

**验证/归因**：高置信度的源码时序推导；删除能力由近期 `4e09538` 加入。`StorageDeleteTest.java:126` 的“刚新增关联”是两次删除间顺序插入，未覆盖并发未提交上传。本次没有连接真实 MinIO，也没有执行删除。

### S3 · P2 · 闪念创建跨两张表写入，没有事务，事件失败后主体仍保存

**位置**：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/api/ThoughtController.java:98`（98–119），先插入 thought，再逐个插入事件，没有类级或方法级事务。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/sql/1_init_table/2026-08-18_init_all_tables.sql:629`（629–632），事件 `content` 非空。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/pojo/req/ThoughtSaveReq.java:14` 与 `ThoughtSaveEventReq.java:13`，没有事件内容约束及嵌套校验。

**触发**：请求包含有效闪念正文及 `events:[{"content":"有效事件"},{}]`，或保存后续事件时数据库失败。前面的 mapper 插入已分别提交，后续事件失败使请求报错。

**影响**：错误响应后仍残留主体及部分事件，用户重试可能产生重复闪念。近期更新接口在 122–169 已有事务和完整事件列表语义，创建接口却没有对应保障。

**建议**：将创建/更新闪念及事件归入同一应用服务事务；进入事务前做正文及事件嵌套校验。补充通过 Spring 代理、真实测试数据库验证“第二个事件失败，主体和第一个事件都回滚”的测试。仅 mock Mapper 无法验证事务回滚。

**验证/归因**：高置信度，源码和非空表约束已核对；`git blame` 证明创建路径源自 2026 年 4 月及更早，**不是这几天新增回归**。本次未执行有写入的真实数据库请求。

### S4 · P2 · 升级链路未纳入交付验证，新库测试不能保证已有数据库升级成功

**位置**：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/.github/workflows/docker-publish.yml:68`（68–84），只用最新全量建表及种子 SQL 创建新库后测试/打包。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/sql/1_init_table/2026-09-30_add_wechat_phone_login.sql:4`（4–20），需执行一次的 ALTER/唯一索引/约束升级。
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/docs/微信小程序登录.md:7`（7–8），明确要求先迁移再部署，新实体查询依赖新增字段。

**风险**：这次功能同时调整用户、银行卡和菜单结构。项目有人工升级说明，这是正面措施；但仓库未见迁移版本账本、启动结构校验或“上一版 schema + 本次增量”CI。漏执行或顺序错误时，镜像依然可能完成构建，而常规用户/菜单/银行卡查询运行时报缺表/缺字段。关闭微信功能也不能消除 `UserEntity` 普通查询对新列的依赖。

**建议**：保留新库初始化测试，新增上一发布版本数据快照经过增量迁移的 MySQL 测试；引入版本化迁移及发布前结构门禁。可使用独立发布迁移任务，不要求应用启动时自动改生产库。短期至少维护本次发布迁移清单、执行记录和只读 preflight。

**验证/归因**：这是高置信度的交付覆盖缺口，**没有检查生产迁移状态，也未发现某份迁移 SQL 已确定执行失败**。机制是存量缺口，近期 schema 变化扩大了影响。

## 架构整体判断

合理之处：

- 单个 Spring Boot 按领域组织，当前规模适合继续保持模块化单体。统计 695 个 Java 文件，`record` 401 个；这个数字用于定位边界压力，不作为“大文件/大模块就是缺陷”的证据。
- 请求/响应改成独立 Req/Query/VO，`RecordApiConvertor` 的响应映射使用 `ReportingPolicy.ERROR`，API 边界扫描递归检查实体泄露，方向正确。对字段缺省、显式 null、空列表的测试比单纯类型拆分更有价值。
- 微信新增逻辑拆成外部平台客户端、短期票据、账户事务和统一会话服务；注册/绑定依赖数据库唯一约束，平台网络请求与账户事务分开。单小程序阶段将身份列放 `user` 可以接受；未来多 AppID/OAuth 再考虑独立身份表。
- 当前未提交银行改造将 SQL 下沉 Mapper，保留用户锁/字典锁/模板锁、逻辑删除条件，nullable 清空采用字段级 `ALWAYS`。不能把迁移后的结果当成原来的 JDBC 绕过持久层问题。

仍需渐进改善：

- 61 个 API Controller 中有 24 个直接导入 Mapper。简单单表读取可以维持，但跨表写入/文件关联/排序等用例需要统一应用服务事务；S3 是这种职责分散已经造成的实际问题。
- `RecordMcpTools.java:38` 起直接依赖多个 REST Controller，甚至在 143 行从 Controller 获取 Mapper。将时迹、闪念、任务用例服务作为 HTTP/MCP 共同入口，避免两套入口各自补鉴权、校验与返回转换。这里不声称全部 MCP 都已存在可利用校验漏洞。
- `core/cache/MenuDataCache.java:9` 起依赖 `record` 工具和 `sso/system` Mapper，实际属于菜单/访问控制领域，不是通用基础设施。可将其移入访问控制模块，并将 Redis 抽象归入基础设施；无需一次移动整个项目。
- `record` 同时包含文件、字典、财务、时迹等边界。先提取共享文件与字典服务端口，再随功能迭代拆包，避免纯目录改名制造新的大批量 diff。

## 分阶段建议

1. 先修 S1，补提交后失败/恢复测试；S2 在管理员清理功能扩大使用前增加保护；S3 补创建事务和失败回滚用例。
2. 建立 S4 的升级验证和 preflight；以最近业务为单位补“真实 HTTP/数据库结果”，保留已有契约测试，不用一次全仓重写。
3. 随需求逐步把复杂 Controller 与 MCP 共用逻辑沉入用例服务；建立依赖规则，防止 `core` 再反向依赖业务模块。不要为这次审查直接拆微服务。

## 执行记录与验证边界

- 已执行只读命令：`git status --short`、`git log --since=2026-09-28`、`git diff HEAD --stat/--numstat`、`git blame`、`rg`/`nl` 源码链路检查，以及一个只读 Python 源码数量/Controller Mapper import 统计。
- `git diff --check` 无输出，退出码 0。这仅说明检查时工作区差异没有该命令可识别的空白错误。
- 未执行 Maven，以免与安全专项的隔离测试争用 `target`；未重新构建，未启动服务，未连接生产数据库、Redis、微信或 MinIO。现有测试内容已阅读，但没有将历史通过结果作为本轮通过证据。
- 未修改、提交、部署任何 server 业务代码。本报告列出可核实路径及明确触发条件，运行时故障注入与目标环境升级仍待后续修复验收。
