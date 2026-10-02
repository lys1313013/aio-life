# Server 架构问题修复记录

日期：2026-10-03。修复基线：server `7fdd5c1`。保持 Spring Boot 模块化单体，不新增服务、业务表或数据库迁移。S4 升级链路由主任务处理，本记录只覆盖 S1–S3 与 S2 必要关联入口。

## 已实现

### S1：菜单与二级锁读取权威配置

- `MenuDataCache` 保留类名以减小调用迁移，但移除 Redis 读取、5 小时 TTL 和提交后失效回调；菜单和用户锁配置直接由两个专用 Mapper 查询读取。
- `UserSecondaryLockMenuMapper.selectForAccessControl` 与 `ISysMenuMapper.selectEnabledForAccessControl` 使用明确 SQL、绑定参数、逻辑删除条件，并设置 `useCache=false, flushCache=TRUE`，避免 MyBatis 一级/二级查询缓存成为新的旧授权来源。
- 删去服务层无意义的缓存失效调用及旧 Redis TTL 测试；数据库失败向上传播，不能回退为“没有锁”。
- 取舍：每次读取会增加小配置表数据库查询，换取消除“数据库已提交而 Redis 失效永久丢失”窗口；没有引入持久版本表或重试队列。旧 Redis 数据无需主动扫描清理，原数据键自然过期，旧版本键不再参与请求。

关键源码：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/core/cache/MenuDataCache.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/sso/mapper/UserSecondaryLockMenuMapper.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/mapper/ISysMenuMapper.java`

验证中发现：仅覆盖 MyBatis-Plus 的 `BaseMapper.selectList` 并加 `@Options`，实际注入 SQL 未按期望刷新一级缓存。新增同一 `SqlSession` 的真实 H2 测试先复现了旧值，改为专用注解查询后通过；没有将注解存在等同于实际有效。

### S2：对象上传与管理员删除共用互斥协议

- 新增 `StorageObjectLock`，以无歧义编码后的 `(bucket,key)` 为 Redis 锁键，复用现有 Redisson，未指定固定租期，由 watchdog 续期。
- 普通上传、公共卡面上传与 URL 上传在写 MinIO 前拿锁；锁延续到数据库事务 `afterCompletion`。没有真实事务时拒绝执行上传。
- 回滚对象清理回调显式排在锁释放前，避免数据库回滚期间管理员删除与清理并行。
- 管理员删除在同一对象锁内重新检查引用并执行删除；遇到上传持锁返回 409，拿锁失败不继续修改对象。没有用单纯“对象年龄门槛”冒充原子协调。
- 追踪所有直接 MinIO 写入口后，补齐 CBTI：管理员图片上传与手动图片初始化都使用同一对象锁；`StorageFileReferenceMapper` 同时检查 `cbti_personality.image_object`（包含软删除引用），并按 CBTI 自定义桶配置区分引用。CBTI 图片原来不写 `file` 表，单查该表会漏掉已被使用的图片。

关键源码：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/core/lock/StorageObjectLock.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/service/impl/FileServiceImpl.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/service/StorageAdminService.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/service/StorageFileReferenceGuard.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/system/mapper/StorageFileReferenceMapper.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/api/CbtiAdminController.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/config/CbtiImageInitUtil.java`

### S3：闪念主从创建统一事务与校验

- 新增 `ThoughtCreationService`，Controller 只转交当前用户与请求；主记录和全部关联事件在同一事务内插入，写入失败直接抛出异常回滚。
- 服务内执行 Bean Validation，HTTP 与 MCP 经 Controller 调用服务时都得到相同校验；正文、事件内容不能为空，列表不能包含 null 事件，置顶值限制为 0/1。
- 新增事件同时补齐创建/更新审计字段。更新、查询接口保持原有行为，此次未做全量 Controller 搬迁。

关键源码：

- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/service/ThoughtCreationService.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/api/ThoughtController.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/pojo/req/ThoughtSaveReq.java`
- `/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-server/src/main/java/top/aiolife/record/pojo/req/ThoughtSaveEventReq.java`

## 验证结果

使用 `JAVA_HOME=/opt/homebrew/opt/openjdk@21`。15 个相关测试类的最终报告共 **73 项通过，0 失败、0 错误、0 跳过**；采用按改动重跑受影响类，不把不同运行的重复用例累计成通过数量。

主要新增回归：

- `MenuDataCacheTest`：提交后不运行任何 Redis 回调，另一实例也能读到新锁；菜单路径变更立即影响锁范围；数据库失败拒绝继续使用旧授权。
- `MenuAuthorityPersistenceTest`：同一 MyBatis SqlSession 连续读取，独立连接提交新配置，第二次查询实际返回新配置。
- `StorageUploadCoordinationTest`：真实 Spring 事务代理 + H2 Mapper；另一个线程在普通/URL上传未提交时删除被拒绝；提交后引用继续保护；失败回滚清理期间锁仍被持有且最终释放；CBTI上传中用锁保护、上传后用引用保护；未经过事务代理的上传协调调用被拒绝。
- `StorageDeleteTest`：原有 16 项路径/归属/软删除/查库失败检查继续通过，新增 CBTI 软删除图片引用保护，共 17 项。
- `ThoughtCreationTransactionTest`：第二个事件数据库约束失败后主体与第一个事件都回滚；成功时写入完整主从与审计数据；直接调用服务也拒绝无效嵌套事件。
- 其余覆盖接口契约、二级锁边界、MCP、文件服务、公共卡面、荣誉附件与持久层架构规则。

执行命令记录：

```bash
JAVA_HOME=/opt/homebrew/opt/openjdk@21 mvn -q -Dtest=MenuDataCacheTest,SecondaryLockBoundaryTest,StorageUploadCoordinationTest,StorageDeleteTest,StorageAdminServiceTest,ThoughtCreationTransactionTest,ThoughtEventsContractTest,FileServiceImplTest,BankCardTemplateUploadTest,HonorAttachmentPersistenceTest,RecordMcpToolsTest,RecordMcpE2ETest,ApiBoundaryContractTest,PersistenceArchitectureTest test
JAVA_HOME=/opt/homebrew/opt/openjdk@21 mvn -q -Dtest=MenuAuthorityPersistenceTest,MenuDataCacheTest,SecondaryLockBoundaryTest,StorageUploadCoordinationTest,StorageDeleteTest,PersistenceArchitectureTest test
git diff --check
```

首轮新增并发测试的代理类型配置错误已修正；第二轮同 SqlSession 测试发现实际一级缓存问题并推动修复。最终受影响测试通过，最新运行日志 `/tmp/aio-server-architecture-fixes-tests-3.log`；前两轮诊断日志为相同前缀的 `tests.log`、`tests-2.log`。`git diff --check` 通过。测试后仅整理了 Java import 和空行，没有行为变化。

## 边界

- 存储测试的数据库与 Spring 事务是真实执行；Redis 锁使用线程互斥替身，MinIO 使用 Mock。没有把这轮结果称为真实 Redis watchdog、网络分区、真实 MinIO 或生产 MySQL并发验收。
- 新协议需要相关上传/删除实例同时使用本版代码；旧版实例不持锁，混合版本滚动期间不能依赖新锁保护其上传。部署时应同步升级或暂时禁用管理员清理。
- 未提交、推送、部署，未访问或修改生产服务；未新增数据库结构。安全专项对同一工作区的凭据撤销等修改保留，未在本记录冒充本专项成果。
