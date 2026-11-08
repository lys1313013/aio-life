# AIO Life 数据库设计审查（2026-11-06）

> 审查日期：2026-11-06；文档整理：2026-11-08。本文保留审查时的发现与验证边界，不代表后续版本的实时缺陷清单，也不代表整改已实施。
>
> 原审查在本机临时空库执行过迁移；未连接或修改目标业务库。本文的索引、约束与清理建议均未执行。涉及结构的整改须按[SQL 脚本规范](../../../aio-life-server/docs/SQL脚本规范.md)新增 Flyway `V` 迁移，不能改写已执行脚本。

阅读入口：[结论](#一结论) · [证据范围](#二审查范围与方法) · [P1 问题](#四p1上线前必须处理) · [P2 问题](#五p2一致性与维护性) · [P3 观察项](#六p3清理项与观察项) · [整改顺序](#八建议的整改顺序) · [验证边界](#九验证边界与未覆盖项)。字段语义与治理规则仍以[后端字段规范](../../../aio-life-server/docs/数据库设计审查与字段规范.md)为维护入口，本文仅保存本次审查快照。

## 一、结论

**总体方向合理，审查时的实现仍有需要在上线前处理的正确性与查询性能问题。**

合理之处：按业务域垂直拆表、个人数据统一 `user_id` 归属、金额使用 `DECIMAL`、全库 InnoDB/utf8mb4、表和字段中文注释完整、逻辑删除已收紧为 `NOT NULL`、迁移由 Flyway 管理并在空库和 MySQL 8.0/8.4 上验证、敏感字段（卡号、飞书密钥、导出票据）有加密或摘要设计。**不需要推翻重建。**

审查发现以下 5 类问题，建议在正式上线前处理：

1. **热点查询缺少匹配索引**：72 张业务表中 17 张没有任何二级索引；`time_record` 只有单列 `date` 索引；临时空库的代表查询出现全表扫描计划，实际业务耗时仍需有数据量的验证。
2. **核心唯一性只靠“先查再写”**：`user.username`、`user.email`、`user_bind(user_id, platform)`、两张通知配置表、`system_config.config_key`、`api_key.api_key` 都没有数据库唯一约束，并发下重复后 `selectOne/getOne` 会抛 `TooManyResultsException`。
3. **时迹分类的逻辑删除实际失效**：`TimeTrackerCategoryEntity` 重新声明了 `isDeleted`，遮蔽父类 `BaseEntity` 的 `@TableLogic`；运行时 `TableInfo` 中 `logic=false`，`removeById` 变成物理删除，并且删除公共分类时会把用户覆盖记录一并物理删除，可能留下 `time_record.category_id` 孤儿。
4. **结构收紧后留下了不可用的查询**：`expense.exp_time`、`income.inc_date` 已是 `NOT NULL`，但查询仍保留 `undated=true → isNull(...)` 分支；前端财务日历在无日期区间时正好发送 `undated: true`，该分支永远返回空。`likeRight(year)` 生成 `LIKE '2025%'`，时间列隐式转字符串，补索引也用不上。
5. **软删除与唯一键的冲突没有统一策略**：`sys_menu.path`、`cbti_personality.code` 等唯一键没有排除已删除行；删除后再创建同路径/同编码会触发唯一键冲突，HTTP 返回行为尚未复现。只有 `user`、`membership_provider` 使用了 `active_flag` 生成列模式。

此外还有若干 P2/P3：主键生成策略与 `AUTO_INCREMENT` 不一致、公共字段空值/默认值不统一、文件元数据双份、死表和死列、日志无保留策略、时区配置需要核验、明文 API Key/第三方 Token 等。详见下文。

## 二、审查范围与方法

- **有效结构**：原审查在本机临时 MySQL 8.0.40 空库上执行 `B20261028_00_001` + 截至 `V20261103_01` 的 `V` 迁移，得到 72 张业务表和 `flyway_schema_history`，共 1037 个业务列、106 个二级索引（87 个非唯一索引、19 个唯一索引）、30 个 CHECK、1 个外键。业务统计均排除 Flyway 历史表，唯一索引不重复计入总数。
- **代码**：后端 906 个 Java 文件中的实体、Mapper、Controller、Service、MCP 查询路径；3 个 Mapper XML；Web/移动端与字典、财务日历相关的调用。
- **数据库**：原审查记录为对 61 条代表性查询执行 `EXPLAIN`，对 72 个实体用 MyBatis-Plus 3.5.11 初始化 `TableInfo`，核对 `@TableLogic`、`IdType` 和列映射；本次文档整理未重跑这些验证。
- **文档**：比对后端[数据库表结构](../../../aio-life-server/docs/数据库表结构.md)与[字段规范 D01–D09](../../../aio-life-server/docs/数据库设计审查与字段规范.md)；覆盖范围见第九节。
- **边界**：**未连接 117 业务库**，未读取真实数据、未做并发复现、未做有数据量的执行计划对比；`EXPLAIN` 只采信 `type`/`key`/`possible_keys`/`Extra` 等计划形状，不据此断言实际耗时。下文“可清理”均以库内存量数据另行核实为前提。

2026-11-08 整理时对照的本地版本为后端 `d251042`、Web `a3adf4cf2`、移动端 `2ad3bf3`；这些版本用于定位源码，不追认原审查运行环境。抽查了分类字段遮蔽、字典 ID 类型及逻辑删除配置，未重新完成全量代码审查。

本机 `output/db-review/` 为忽略目录，不随仓库提交；保留了结构导出 `schema.sql`、表/列/索引/约束 TSV 和结构统计。2026-11-08 已按 TSV 重新核算上述结构数量，修正原稿索引总数；现存 `explain.sql` 仅有 6 条查询，未提供完整的 61 条查询及运行时初始化日志，因此这些原始验证记录无法仅凭干净克隆复现。后续复核应先按[数据库初始化与验证](../../../aio-life-server/docs/数据库初始化与验证.md)重建临时库，再保存查询、计划、实体初始化结果和版本信息；目标库仍需单独只读预检。

## 三、做得合理、应保留的部分

| 设计 | 评价 |
| --- | --- |
| 按业务域垂直拆表（record、wardrobe、membership、bankcard、feedback、sso、system、scheduling、export） | 域边界清楚，72 张表数量偏多但可解释；不建议为“表多”整体重构 |
| 个人数据统一 `user_id`，日志/公共表用 NULL 或 0 区分 | 49 张表有 `user_id`，归属语义基本一致；NULL/0 的公共分类约定已在文档记录 |
| 全库 InnoDB、utf8mb4/utf8mb4_unicode_ci；标识字段按需 ascii_bin | 与规范一致；未发现 MyISAM、latin1 或排序规则混用 |
| 表和每个业务字段都有中文 `COMMENT` | 1037 个业务列 0 缺失，表注释 0 缺失（仅 Flyway 基础设施表例外） |
| `is_deleted` 全库 `NOT NULL DEFAULT 0` | 原 26 张可空表已收紧；查询不会遇到“既非有效也非删除”的 NULL 状态 |
| 金额 `DECIMAL`、坐标 `DECIMAL`、卡号密文、HMAC 指纹 | 方向正确；银行卡模块的安全设计明显好于其他模块 |
| `active_flag` 生成列 + 唯一键 | `user` 手机号/微信、`membership_provider` 已用该模式解决“软删除后仍要保留历史行”的唯一性；应推广到其他业务唯一键 |
| 导出模块的一次性票据、摘要、租约、审计 | 4 张导出表看起来多，但职责分离合理，属于安全敏感链路的必要复杂度 |
| Flyway 基线/增量、结构契约、迁移守卫 | 工程化程度高于一般个人项目；空库重建和 8.0/8.4 双版本验证链完整 |

## 四、P1：上线前必须处理

### P1-1 热点查询缺少索引，多个主流程是全表扫描

有效结构中有 **17 张业务表没有任何二级索引**（仅主键）：`exercise_record`、`expense`、`income`、`login_log`、`memo`、`notification_channel_config`、`notification_preference`、`record_article`、`sys_dict_data`、`sys_dict_type`、`sys_work_calendar`、`system_config`、`task_detail`、`thought`、`thought_rela_event`、`user_bind`、`wardrobe_category`。列数不能说明数据量，是否构成瓶颈还需结合行数、查询频率和执行计划判断。

原审查记录的执行计划（MySQL 8.0.40，空表只用于看计划形状；完整原始输出未保留）：

| 查询 | 入口 | 计划 |
| --- | --- | --- |
| 支出列表：`user_id + is_deleted + exp_time 范围 + ORDER BY exp_time DESC, id DESC` | [ExpController.java:72-91](../../../aio-life-server/src/main/java/top/aiolife/record/api/ExpController.java#L72-L91) | `type=ALL, key=NULL, Using filesort` |
| 收入列表：`user_id + inc_date 范围 + ORDER BY inc_date DESC, id DESC` | [IncomeController.java:62-74](../../../aio-life-server/src/main/java/top/aiolife/record/api/IncomeController.java#L62-L74) | `type=ALL, key=NULL, Using filesort` |
| 视频列表：`user_id + is_deleted + ORDER BY update_time` | [BVideoController.java:68-78](../../../aio-life-server/src/main/java/top/aiolife/record/api/BVideoController.java#L68-L78) | `type=ALL, key=NULL, Using filesort` |
| 第三方绑定：`user_id + platform` | [UserBindServiceImpl.java:25-28](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/UserBindServiceImpl.java#L25-L28) | `type=ALL` |
| 通知偏好：`user_id`、`user_id + biz_type + channel` | [FeishuNotificationServiceImpl.java:432-441](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/FeishuNotificationServiceImpl.java#L432-L441) | `type=ALL` |
| 时迹按日：`user_id + date + ORDER BY update_time` | [TimeRecordServiceImpl.java:74-81](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeRecordServiceImpl.java#L74-L81) | `ref(idx_time_record_date)` 仅按 `date`，回表过滤用户 + `Using filesort` |
| 目标非置顶列表：`user_id + is_deleted + ORDER BY create_time` | [GoalController.java:59-86](../../../aio-life-server/src/main/java/top/aiolife/record/api/GoalController.java#L59-L86) | 命中 `idx_home_pinned` 索引但 `Using filesort`（排序键不匹配） |

首页卡片与列表频繁按用户查询，索引应匹配用户隔离、筛选和排序条件。`b_video` 已有 `idx_status`、`idx_bvid`、`idx_aid`、`idx_title(100)` 四个索引，却没有一个以 `user_id` 开头；现有索引不能有效支撑这里列出的用户范围查询。

**建议**（列顺序按“等值列在前、范围/排序列在后”，需在有数据量环境复核）：

| 表 | 建议索引 | 对应查询 |
| --- | --- | --- |
| `time_record` | `(user_id, is_deleted, date, update_time, id)`，替换现有 `(date)` | 按日/周、推荐、写入合并 |
| `expense` | `(user_id, is_deleted, exp_time, id)`；`(user_id, transaction_id)` 用于导入查重 | 列表、统计、批量导入 |
| `income` | `(user_id, is_deleted, inc_date, id)` | 列表、统计 |
| `b_video` | `(user_id, is_deleted, update_time, id)`；确认后删除 `idx_status`/`idx_aid`/`idx_title` | 列表、状态计数、时长统计 |
| `exercise_record` | `(user_id, is_deleted, exercise_date, id)`；`(user_id, time_id)` | 列表、看板、按时间反查 |
| `memo` | `(user_id, is_deleted, update_time, id)` | 列表、首页 |
| `thought` | `(user_id, is_deleted, update_time, id)` | 列表、看板 |
| `thought_rela_event` | `(thought_id, id)` | 批量装配/删除 |
| `task_detail` | `(task_id, user_id, is_completed, sort_order, id)`；`(user_id, is_starred, is_completed, priority, sort_order, id)` | 任务明细、关注列表 |
| `task` | `(user_id, is_deleted, sort_order, id)` | 看板列表 |
| `device` | `(user_id, is_deleted, purchase_date, id)` | 设备列表 |
| `performance` | `(user_id, is_deleted, performance_date, id)` | 演出列表 |
| `goal` | `(user_id, is_deleted, create_time, id)`；`(parent_id, is_deleted, status)` | 列表、父子统计 |
| `user_bind` | 先按 P1-2 建唯一 `(user_id, platform, active_flag)`；另补 `platform` 供定时任务全量扫描 | 绑定读取、LeetCode 同步 |
| `notification_channel_config` | 唯一 `(user_id, channel, active_flag)` | 配置读取 |
| `notification_preference` | 唯一 `(user_id, biz_type, channel, active_flag)` | 偏好读取 |
| `notification_delivery` | 唯一/普通 `(user_id, channel, dedup_key)`；重试扫描改 `(channel, status, next_retry_time, create_time, id)` | 去重、重试 |
| `wardrobe_category` | `(user_id, parent_id)` | 分类列表 |
| `sys_dict_data` | `(dict_id)` | 按类型查字典项 |
| `sys_dict_type` | `(dict_type)` | 按类型查字典 |
| `login_log` | `(user_id, created_at)`（若管理端需要列表，再补 `(created_at)`） | 注销清理、未来查询 |

> 候选索引不承诺同时消除所有范围查询和排序成本。例如 `date` 为范围条件时，后续 `update_time` 通常不能直接满足跨日期排序；`LIKE` 写法也应改成日期范围（见 P1-4）。`bank_card` 已有 6 个二级索引，新增前先按真实查询复核，避免写放大。

### P1-2 核心业务唯一键缺失，重复数据会让读取接口直接报错

| 业务唯一键 | 当前 DDL | 读取路径 | 风险 |
| --- | --- | --- | --- |
| `user.username` | 只有主键，无唯一索引/普通索引 | [UserServiceImpl.java:97-99](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L97-L99) 登录 `selectOne`；注册 [537-545](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L537-L545) 先 `selectCount` | 并发注册产生同名用户后，登录 `selectOne` 抛 `TooManyResultsException`，该账号无法登录 |
| `user.email` | 无唯一索引/普通索引 | 找回密码 [514-515](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L514-L515) `selectOne`；注册先查 | 同上；邮箱重复后无法重置密码 |
| `user_bind(user_id, platform)` | 无索引，仅主键 | [UserBindServiceImpl.java:25-28](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/UserBindServiceImpl.java#L25-L28) `getOne` | 首页每张卡片都会查询；重复绑定后 `getOne` 抛异常，首页卡片不可用 |
| `notification_channel_config(user_id, channel)` | 无索引，仅主键 | [FeishuNotificationServiceImpl.java:432-434](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/FeishuNotificationServiceImpl.java#L432-L434) `selectOne` | 并发首次保存产生两条后，通知配置读取失败 |
| `notification_preference(user_id, biz_type, channel)` | 无索引，仅主键 | [FeishuNotificationServiceImpl.java:438-441](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/FeishuNotificationServiceImpl.java#L438-L441) `selectOne` | 同上；通知偏好不可用 |
| `system_config.config_key` | 列注释写“唯一”，实际无唯一索引 | [SystemConfigServiceImpl.java:120](../../../aio-life-server/src/main/java/top/aiolife/system/service/impl/SystemConfigServiceImpl.java#L120) 等 4 处 `selectOne` | 重复配置后读取抛异常；配置服务不可用 |
| `api_key.api_key` | 无唯一索引，仅主键 | [ApiKeyServiceImpl.java:67-70](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/ApiKeyServiceImpl.java#L67-L70) `getOne` | 重复/碰撞后 API 认证失败；当前每次请求还全表扫 |
| `bank_card(user_id, card_no_fingerprint)` | 只有普通索引 `(user_id, fingerprint, is_deleted)` | 服务层先查后写 | 同一张卡重复录入；统计和余额重复计算 |
| `b_video(user_id, bvid)` | 只有 `idx_bvid`，无唯一约束 | [IBVideoMapper.java:27-37](../../../aio-life-server/src/main/java/top/aiolife/record/mapper/IBVideoMapper.java#L27-L37) 按 BV 号取一条 | 同一用户同一视频可重复标记，状态/时长重复累计 |

**建议统一复用 `active_flag` 模式**：`active_flag` 由 `is_deleted=0` 派生为 1、删除后为 NULL，再与业务唯一键组合。MySQL 唯一索引允许可空列出现多个 NULL，因此可以保留多条已删除历史记录；不要简单改成 `(业务键, is_deleted)`，否则第二条同键删除记录仍会冲突。

| 表 | 候选有效记录唯一键 | 迁移前提 |
| --- | --- | --- |
| `user` | `(username, active_flag)`、`(email, active_flag)` | 复用已有生成列，先确认有效账号无重复 |
| `user_bind` | `(user_id, platform, active_flag)` | 新增带中文注释的生成列，先核验重复与删除值 |

这里只记录设计，正式 DDL 应在后端 `sql/migrations/` 中交付，并包含执行条件和数据核查；不把本文当作迁移脚本。

同样的模式可用于 `notification_channel_config`、`notification_preference`、`system_config`、`bank_card`、`b_video`、`sys_menu.path`、`cbti_personality.code` 等需要“删除后重建”的业务键。认证凭据和导出幂等键应先确定是否要求跨删除历史仍然唯一，不能机械套用。执行前必须逐表查出有效重复与异常删除值，不能自动删数据；字符串比较规则（大小写、首尾空格）也要先定。

### P1-3 时迹分类的逻辑删除实际失效（数据会被物理删除）

[TimeTrackerCategoryEntity.java:69](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/TimeTrackerCategoryEntity.java#L69) 重新声明了：

```java
private Integer isDeleted;
```

它遮蔽了父类 [BaseEntity.java:24-25](../../../aio-life-server/src/main/java/top/aiolife/core/pojo/entity/BaseEntity.java#L24-L25) 上的 `@TableLogic`。原审查记录：以项目 `target/classes` 和 MyBatis-Plus 3.5.11 初始化后，`TableInfo` 中该表的 `logic=false`；原因是 `ReflectionKit.excludeOverrideSuperField` 剔除了被覆盖的父类字段。原初始化日志未随文档保存，以下为该结果与调用路径推导的后果，尚未通过实际删除复现：

- [TimeTrackerCategoryServiceImpl.java:490](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeTrackerCategoryServiceImpl.java#L490) 的 `removeById` 变成 **物理 DELETE**；`:493` 的覆盖记录删除同样是物理删除。
- `adminDeleteCategory` 只对公共分类 ID 调 `ensureNoRecords`，随后删除所有 `template_id=公共分类` 的用户覆盖记录；如果用户已用这些覆盖记录写了时迹，`time_record.category_id` 会变成孤儿（没有外键，不会报错）。
- `ensureNoChildren` 只按 `parent_id` 计数，不过滤 `is_deleted`；如果有历史软删除子分类，父分类可能永远删不掉。
- `listUserHiddenCategories` 没有过滤 `is_deleted`，已删除的分类仍可能出现在“隐藏分类”中。

**修复**：删除子类的 `isDeleted` 字段，让 `BaseEntity` 的 `@TableLogic` 生效；或在子类字段上补 `@TableLogic`。同时修正上述查询的删除过滤，并明确 `adminDeleteCategory` 是否允许删除仍被用户覆盖记录/时迹引用的公共分类。

另外，`application.yml` 的全局配置写的是 `logic-delete-field: is_deleted`，而 MyBatis-Plus 比较的是 Java 属性名（`isDeleted`），该全局配置实际匹配不到任何字段；目前多数实体靠显式 `@TableLogic` 工作。建议改成 `isDeleted` 或删除该配置，避免继续产生“以为全局生效、实际没有”的实体。

### P1-4 结构收紧后留下不可用查询：`undated` 死分支与 `likeRight(year)`

`expense.exp_time`、`income.inc_date` 在有效结构中都是 `NOT NULL`，但查询仍保留：

- [ExpController.java:85](../../../aio-life-server/src/main/java/top/aiolife/record/api/ExpController.java#L85)：`isNull(undated, ExpenseEntity::getExpTime)`
- [IncomeController.java:71](../../../aio-life-server/src/main/java/top/aiolife/record/api/IncomeController.java#L71)：`isNull(undated, IncomeEntity::getIncDate)`

`isNull` 在 `NOT NULL` 列上恒为假。前端财务日历在缺少日期区间时正好发送 `undated: true`（[finance-calendar.ts:78-82](../../../aio-life-front/apps/web-antd/src/api/core/finance-calendar.ts#L78-L82)），所以“未填写日期”桶永远为空。需要二选一：让日期列可空并明确业务含义，或删除 `undated` 参数和前端分支；不能继续保留一个永不命中的条件。

`likeRight(year)` 是另一个问题：

- [ExpController.java:80-81](../../../aio-life-server/src/main/java/top/aiolife/record/api/ExpController.java#L80-L81)
- [IncomeController.java:67](../../../aio-life-server/src/main/java/top/aiolife/record/api/IncomeController.java#L67)

它生成 `exp_time LIKE '2025%'` / `inc_date LIKE '2025%'`，把时间列隐式转成字符串比较。原审查记录中，`WHERE date LIKE '2026%'` 未选择已有日期索引。建议改成 `>= '2025-01-01' AND < '2026-01-01'` 这样的半开范围，使日期条件可用于索引范围访问；优化器最终是否选用索引仍需在代表数据上验证。

### P1-5 软删除与唯一键冲突：删除后无法重建

| 唯一键 | 删除方式 | 重建路径 | 结果 |
| --- | --- | --- | --- |
| `sys_menu.path` (`uk_sys_menu_path`) | [MenuServiceImpl.java:224-226](../../../aio-life-server/src/main/java/top/aiolife/system/service/impl/MenuServiceImpl.java#L224-L226) 逻辑删除 | `create` 只查有效行 [125-131](../../../aio-life-server/src/main/java/top/aiolife/system/service/impl/MenuServiceImpl.java#L125-L131) | 删除 `/test` 后重建 `/test` 会触发唯一键冲突；HTTP 行为未复现 |
| `cbti_personality.code` (`uk_cbti_personality_code`) | [CbtiAdminController.java:145-159](../../../aio-life-server/src/main/java/top/aiolife/record/api/CbtiAdminController.java#L145-L159) 软删除 | `existsCode` 只查有效行 | 删除某人格 code 后新增同 code 撞唯一键 |
| `user_body_profile.user_id` (`uk_body_profile_user`) | 当前无删除入口 | `save` 前置查询 | 若未来提供删除，会同样冲突；需提前定策略 |
| `data_export_job(user_id, request_key)` | 任务可能有软删除/过期 | 同 request_key | 低概率但同型问题 |

**建议**：需要保留删除历史且允许重建的业务键采用 `active_flag`；要求永久唯一的键则保留原约束，并返回明确的业务冲突。先确定产品规则，再同步约束和写入路径，不为绕过唯一键直接物理删除历史。

## 五、P2：一致性与维护性

### P2-1 公共字段没有真正统一

V20261028_02 统一了 `sort_order`、`remark`、`is_enabled` 的**命名**，但没有统一**空值、默认值和类型**。当前有效结构：

- `create_time`：**45/69 张有该列的表可空**，其中 32 张无默认值（如 `goal`、`honor_record`、`wardrobe_item`、`user_body_profile`）。应用漏填时行会得到 NULL，审计链断裂。
- `update_time`：**43/67 张有该列的表可空**，32 张无默认值，部分没有 `ON UPDATE CURRENT_TIMESTAMP`。
- `is_enabled`：`sys_dict_data`、`sys_dict_type`、`user_dict_data`、`user_dict_type` 允许 NULL，注释写“NULL 表示未设置”；查询按 `is_enabled=1` 时 NULL 行会被静默排除。
- `is_deleted`：9 张表是 `int`，其余是 `tinyint`/`tinyint(1)`；MyBatis-Plus 能工作，但违反“统一 `is_deleted`”的声明，也让磁盘/索引口径不一致。
- 布尔表达混用：`tinyint(1)`、`tinyint`、`int`、`char(1) 'Y'/'N'`（`sys_dict_data.is_default`、`user_dict_data.is_readonly`）、Java `Long`（`time_record.is_manual`）。
- `timestamp` 与 `datetime` 混用：`user.last_active_at`、`login_log.created_at` 是 `timestamp`，其余审计时间基本是 `datetime`。

**建议**：把“公共字段”从命名统一提升为契约统一，按业务表和日志表分别确定适用范围，再交付增量迁移：

| 字段 | 候选契约 | 需先确认 |
| --- | --- | --- |
| `create_time` | `DATETIME NOT NULL`，默认当前时间 | 历史空值的可信回填来源 |
| `update_time` | `DATETIME NOT NULL`，默认当前时间 | 由应用还是数据库负责更新，避免双重维护 |
| `is_enabled` | `TINYINT NOT NULL DEFAULT 1` | 原 NULL 是否具有“未设置/继承”的业务含义 |
| `is_deleted` | `TINYINT NOT NULL DEFAULT 0` | 历史值是否合法、实体逻辑删除映射是否一致 |

`bank_card` 的 `create_user/update_user NOT NULL` 与其他表可空也不一致，需要按“系统操作是否允许”统一。不要为了迁移成功盲目补 0 或空字符串。

### P2-2 约束覆盖不足，很多业务规则只靠应用

72 张表只有 **19 个唯一约束、30 个 CHECK、1 个外键**；CHECK 集中在 `life_footprint`、`user_body_profile`、`goal`、银行卡等较新的表。以下高风险规则没有数据库约束：

| 规则 | 现状 | 建议 |
| --- | --- | --- |
| `expense.amt`、`income.amt` 非负 | 无 CHECK；`ExpenseCreateReq`/`IncomeCreateReq` 也没有 `@DecimalMin` | 加 `CHECK (amt >= 0)`；先确认退款/冲正是否允许负数 |
| `bank_card.statement_day`/`repayment_day` 1–31 | 只有 DTO `@Min/@Max`；列是 `tinyint unsigned`，可存 0/32–255 | 加 CHECK；`expiry_month` 只存每月 1 日也应有 CHECK |
| `bank_card.card_type`/`status` 枚举 | 无 CHECK | 明确取值后加 CHECK |
| `goal.end_date >= start_date` | 无 CHECK | 加 CHECK；日期/年月日双套时间维度另见 D08 |
| `membership_record.expiry_date >= start_date` | 无 CHECK | 加 CHECK |
| `device.end_date >= purchase_date` | 无 CHECK | 加 CHECK |
| `milestone.end_date >= date` | 无 CHECK | 加 CHECK |
| `time_record.start_time <= end_time <= 1439` | 只有应用校验；列是 `smallint unsigned` | 加 CHECK；同时修正注释里的 0–1440 |
| `b_video.watched_duration <= duration` | 无 CHECK | 按业务确认后加 |
| `income.tax <= amt` | 无 CHECK | 按业务确认后加 |

不建议把每个 `status` 都做成 CHECK；枚举会随业务变化，维护成本高。但金额、日期顺序、卡号月份这类稳定不变量适合下沉到数据库。

另外，`ExpenseCreateReq`、`IncomeCreateReq` 缺少对应的 `@NotNull`/`@DecimalMin` 等校验；缺失值若进入无默认值的必填列，将由数据库拒绝，而不是在请求边界给出字段错误。具体 HTTP 状态未复现。数据库约束收紧后，DTO 校验必须同步，不能把“数据库会拦住”当成接口契约。

外键只有 `user.avatar_file_id -> file.id` 一个。其余关系（`user_id`、`file.biz_id`、`task_detail.task_id`、`thought_rela_event.thought_id` 等）由应用维护，数据库外键不会阻止这些关系产生孤儿行。原审查记录账户注销清单覆盖了 49 张含 `user_id` 的表，但新增表仍可能遗漏。建议保留“应用维护关系”的决策，并自动检查新增用户归属表是否已登记注销处理策略（清理、匿名化或保留）；新增业务关联列也应提供孤儿检查或说明。

### P2-3 主键与关联 ID 类型不统一

- 24 张表声明 `AUTO_INCREMENT`，但对应实体大多继承 `BaseEntity`（`@TableId(type = ASSIGN_ID)`）或显式 `ASSIGN_ID`，实际写入雪花 ID；`AUTO_INCREMENT` 形同虚设。`user`、`api_key`、`api_key_log`、`login_log` 甚至没有写 `@TableId`，靠 MyBatis-Plus 默认 `ASSIGN_ID`。两套 ID 空间混用会让手写 SQL、迁移导入、`LAST_INSERT_ID()` 和“小整数 ID”假设全部不可靠。
- `time_record.id`、`file.id` 是 `varchar(32)`，其余业务主键基本是 `bigint`；`file.biz_id` 是 `bigint`，因此不能反向关联 `time_record.id` 或 `file.id`。当前没有实际附件需求使用这条关系（文档已记录边界），但一旦要把时迹/文件接入统一附件模型就会卡住。
- `wardrobe_item.file_id` 是 `varchar(50)`，而 `file.id` 是 `varchar(32)`；`device`/`movie`/`read_record`/`honor_record` 是 `varchar(32)`。宽度不一致，容易让人误以为可以存外部 URL。
- [SysDictDataVO.java:16](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/vo/SysDictDataVO.java#L16) 的 `id` 是 `Integer`，而 `sys_dict_data.dict_code` 是雪花 `Long`；MapStruct 生成的 `.intValue()` 会截断。前端类型写的是 `id: string`，契约已经不一致。

**建议**：先定“新表统一雪花 bigint、API 输出字符串”；对 24 张 `AUTO_INCREMENT` 表二选一：删掉 `AUTO_INCREMENT`（保留现有 ID）或把实体改成 `@TableId(AUTO)`。不要继续保留“表自增 + 实体雪花”。`time_record.id` 是否迁移为 `bigint` 需要单独评估（涉及 `exercise_record.time_id`、导出和 Query 服务），至少要在文档中明确“不可接入 `file.biz_id`”。`SysDictDataVO.id` 改为 `Long`/`String` 并与两端契约同步。

### P2-4 死表、死列与只写不读的日志

审查时的代码引用情况（不等同于目标库中无有效数据）：

| 对象 | 状态 | 证据 | 建议 |
| --- | --- | --- | --- |
| `record_article`、`record_article_annotation` | 死表：无 Controller/Service/MCP/前端入口；仅 Mapper、注销 SQL、导出目录引用 | `IRecordArticleMapper.java`、`IRecordArticleAnnotationMapper.java`；[AccountErasureMapper.java:60-63](../../../aio-life-server/src/main/java/top/aiolife/sso/mapper/AccountErasureMapper.java#L60-L63)；`export/datasets.json:1639-1705` | 确认库内无有效数据后整表删除，同批改注销 SQL、导出目录、实体/Mapper、文档 |
| `enum_type` | 死表：只有实体/Mapper，无注入/调用、无种子 | `IEnumTypeMapper.java`、`EnumTypeEntity.java` | 确认 `COUNT(*)=0` 后删表、实体、Mapper、文档 |
| `sys_dict_data.dict_type` | 死列：实体 `exist=false`，无写入，Controller 从 `sys_dict_type` 回填 | `SysDictDataEntity.java:42-43`、`SysDictDataController.java:95-101` | 可删列；先查 `dict_type <> ''` 的存量 |
| `honor_record.file_id` | 只读（导出）：实体无映射，多附件走 `file.biz_type='honor_record'` | `HonorRecordEntity.java:44-48`、`HonorRecordController.java:101-109`、`datasets.json:1360` | 先核验旧单列图片是否已转入 file 关系，再删列/导出 |
| `device.purchase_company` | 只读（导出）：实体无映射，采购只写 `purchase_place` | `DeviceEntity.java`、`datasets.json:2156` | 确认“购买公司”是否独立业务，再删或补映射 |
| `time_tracker_category.code` | 只读（导出）：实体无 `code`，索引和导出仍引用 | `TimeTrackerCategoryEntity.java`、`datasets.json:774` | 确认外部是否把 code 当稳定标识，再删列/索引/导出 |
| `login_log`、`api_key_log`、`mail_log` | 只写不读、无保留策略 | 写入见 `UserServiceImpl.java`、`ApiKeyInterceptor.java`、`MailServiceImpl.java`；无 SELECT/清理任务 | 定保留期并加清理；不建议直接删表 |
| `export/excluded-tables.json` 的 `llm_key`/`conversation`/`chat_message` | 配置残留，表已不存在 | `export/excluded-tables.json:19-21` | 删除配置 |

**注意**：`record_article` 的导出条目指向不存在的 `/my-hub/article`，导出面板会过滤，但 `ExportDatasetRegistryTest` 仍要求登记。删表必须和导出目录、注销 SQL、测试同批处理，不能只 `DROP TABLE`。

### P2-5 文件元数据双份，单附件列与附件关系并存

- `file` 保存 `file_name`（对象键）、`file_size`、`file_type`、`hash_value`，`storage_object` 又保存 `object_key`、`file_size`、`content_type`、`sha256`；`file.storage_object_id` 把两套记录连起来，但普通上传仍可能只写 `file` 不写 `storage_object`（[FileServiceImpl.java:119,179](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/FileServiceImpl.java#L119)）。
- 业务表同时存在单附件列（`movie.file_id`、`read_record.file_id`、`device.file_id`、`honor_record.file_id`）和 `file.biz_type/biz_id` 多附件关系。`honor_record` 已经以多附件为准，单列成为死列。
- `file.file_name` 是对象键，`data_export_job.file_name` 是下载文件名；同名不同义。

**建议**：明确“物理对象”和“业务附件”的唯一来源：要么 `file` 作为投影、`storage_object` 作为唯一物理对象；要么合并重复列。单附件列在迁移到 `file` 关系后删除。短期至少加一条契约测试：新上传必须同时写 `storage_object`，`file` 的 key/size/MIME 必须与 `storage_object` 一致。

### P2-6 时区配置需要核验

应用镜像设置 `TZ=Asia/Shanghai`（`Dockerfile:27-30`），很多注释写“上海时区”；但 JDBC URL 固定 `serverTimezone=UTC`（[application.yml:51](../../../aio-life-server/src/main/resources/application.yml#L51)），且没有设置连接会话时区。`DATETIME` 不存时区，`CURRENT_TIMESTAMP` 使用 MySQL 会话时区；如果数据库服务器是 UTC，而应用用 `LocalDateTime.now()` 写上海时间，两种来源会相差 8 小时。

这不是必然发生的 bug，但必须核验：`SELECT @@global.time_zone, @@session.time_zone, NOW(), UTC_TIMESTAMP();`，并与 117 库实际配置、应用 JVM 时区对照。建议统一为一种策略：数据库会话固定 `+08:00`（`connectionTimeZone=Asia/Shanghai&forceConnectionTimeZoneToSession=true` 或 `sessionVariables=time_zone='+08:00'`），或全链路 UTC + 展示层转换；不要继续“应用写上海、数据库默认可能是 UTC”。

### P2-7 敏感数据与日志生命周期

- `api_key.api_key` 明文保存，且无唯一索引/普通索引；每次 API 请求按明文全表查（[ApiKeyServiceImpl.java:67-70](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/ApiKeyServiceImpl.java#L67-L70)）。建议只存 SHA-256（或带前缀的哈希），创建时返回一次原文；若坚持明文，至少要加唯一索引并限制展示。
- `user_bind.access_token` 是 `TEXT` 明文，承载 GitHub/LeetCode/微信读书等第三方凭证；文档也写明微信读书“直接保存 Key”。建议加密（应用层 AES-GCM，密钥走环境变量）或至少改为加密列 + 密钥轮换方案。
- `password_vault.username` 是明文 `TEXT`，而密码/备注是客户端密文；Web 端明文提交（`PasswordModal.vue:193`），移动端加密提交（`pages/vault/index.uvue:259`），两端读取用 32+ hex 启发式判断。应先统一两端加密契约，再更新列注释；否则导出会把移动端密文原样带出。
- 日志表没有保留策略：`login_log`、`api_key_log`、`mail_log` 只写不读；`sys_activity_log`、`sys_scheduled_job_log`、`notification_delivery` 持续增长。建议定 90/180 天保留期，增加按时间的清理任务；量级上来后按月分区。不要在没有备份/审计要求的情况下无限保留。

### P2-8 三套字典/枚举并存

- `sys_dict_type`/`sys_dict_data`：管理端字典；
- `user_dict_type`/`user_dict_data`：用户覆盖；
- `enum_type`：死表；
- 代码里还有大量硬编码枚举（`ProgressStatusEnum`、`NotificationChannel`、`BankCardStatus` 等）。

`sys_dict_data.dict_type` 与父表 `sys_dict_type.dict_type` 重复；`sys_dict_type.dict_type` 没有唯一约束；`user_dict_type` 没有 `(user_id, dict_type)` 唯一约束；`sys_dict_data.dict_id` 没有索引。建议保留两套“系统字典 + 用户覆盖”，删除 `enum_type`，把 `dict_type` 收敛到父表，给常用查找补索引/唯一约束。硬编码枚举可以保留，但要在文档中说明哪些是契约、哪些只是内部状态。

### P2-9 其他一致性问题

- `performance` 分页没有 `ORDER BY`（[PerformanceRecordService.java:26-34](../../../aio-life-server/src/main/java/top/aiolife/record/service/PerformanceRecordService.java#L26-L34)），跨页顺序无定义；加 `performance_date DESC, id DESC`。
- `message.sender_id` 是 `NOT NULL`，系统通知写死 `senderId=1L`（[SystemNotificationSender.java:33](../../../aio-life-server/src/main/java/top/aiolife/record/notification/SystemNotificationSender.java#L33)），但用户 ID 实际由雪花生成，1 不一定是有效账号。建议改为可空 + `type=0`，或建专用系统账号；至少文档化伪发送者。
- `performance.performance_date` 是 `datetime NOT NULL`，实体是 `LocalDate`；`milestone.date`/`end_date` 是 `date`，实体是 `String`；`time_record.is_manual` 是 `tinyint`，实体是 `Long` 且全仓无写入。类型放宽会掩盖语义，建议改回 `LocalDate`/`Integer` 并明确字段是否仍需保留。
- `time_record` 的 `start_time/end_time` 注释仍写“0-1440”，业务有效区间是 0–1439。D02 已修复应用局部更新时的时长重算，现行方案保留物理 `duration` 列；存量一致性仍需巡检。若后续改为生成列，应单独评估所有写入、导出与 Query 路径，并同步迁移，不能把该候选方案写成已采纳规则。
- `time_record.id`、`file.id` 的 `varchar(32)` 与其他 `bigint` 主键混用，见 P2-3。

## 六、P3：清理项与观察项

| 项 | 说明 |
| --- | --- |
| 候选冗余索引 | `anniversary_record.idx_user_id`、`goal.idx_user_id`、`wardrobe_item.idx_user_id` 与更长索引的最左前缀重复；删除前比较索引宽度、覆盖查询和真实计划 |
| 候选低收益索引 | `b_video.idx_title(100)` 不能为 `LIKE '%x%'` 提供前缀范围定位；`idx_aid`、`honor_record.idx_honor_date`/`idx_category_id`、`anniversary_record.idx_target_date` 在已审查查询中未见筛选引用；`b_video.idx_status` 曾出现全索引扫描，但不能仅凭扫描类型认定为负收益 |
| `SELECT *` | `IBVideoMapper` 的列表/锁查询、`ActivityLogMapper` 导出查询等；`b_video` 含 `description/pages_info`，走二级索引会回表读大字段 |
| N+1 | `HonorRecordController` 每条记录查一次 `fileService.getByBiz`；`PerformanceRecordService` 每条记录查一次附件。改为 `biz_id IN (...)` 批量取回 |
| 深分页 | `page` 只限制 `>=1`，无上限；`expense`/`b_video` 这类 `ALL + filesort` 计划会随页码线性恶化。列表加 `id` 唯一键兜底，深分页改游标 |
| 排序表达式 | `ORDER BY FIELD(status, ...)` 天然阻断索引排序；单用户量级可接受，量级上来可加 `status_sort` 生成列 |
| 文档漂移 | `docs/数据库表结构.md` 的 `login_log.ip_address` 仍写“创建时间”（应为“IP地址”）；`user` 索引清单漏 `idx_user_erasure_retry`、`idx_user_avatar_file`、`fk_user_avatar_file`；`bank_card_cover_template` 索引/约束清单不完整；`record_article` 标题“文章记录表” vs 表注释“收藏文章表”；`time_record` 注释 0–1440 vs 业务 0–1439 |
| 文档状态需区分范围 | D03 的文章表无主业务入口但仍被导出/注销引用；D06 索引、D01 唯一性、D05 文件职责和 D08 单位问题在审查时仍存在。D02 已修复应用写入，D04 仅排序/备注/启用命名统一，D07 已提供约束及注释增量；这些均不代表业务库已执行或全部子项完成 |
| 请求 DTO 注解 | `TimeRecordReq` 上有 `@TableName("time_record")` 和 `@TableId`，但它不是实体，容易被误用于 MP 查询/更新 |
| 逻辑删除约定 | `GoalEntity` 不继承 `BaseEntity`、无 `@TableLogic`，目前所有查询手工带 `is_deleted`；任何新增查询漏写就会读到已删目标 |
| 布尔/枚举表达 | `is_default`/`is_readonly` 用 `char(1) Y/N`，其他布尔用 `tinyint`/`int`；`status` 大小写和长度不统一（`PENDING` vs `not_started`） |
| 日期/时间命名 | `income.inc_date` 是 DATE，`expense.exp_time` 是 DATETIME；`goal.start_date/end_date` 是 DATETIME，`life_footprint` 是 DATE；命名不能掩盖精度差异 |
| 金额精度 | `expense/income/price` 多为 `decimal(10,2)`，`bank_card.balance` 是 `decimal(18,2)`，`goal.target_value` 是 `decimal(14,2)`；不是错误，但应在字段字典中说明各域上限 |
| 日志保留 | `sys_activity_log` 三个同前缀索引写放大；日志表没有分区/清理，见 P2-7 |

## 七、分域判断

| 业务域 | 结论 | 主要问题 |
| --- | --- | --- |
| 用户/认证 | 基础模型合理，安全字段设计部分到位 | username/email 唯一性；`user` 自增与雪花混用；`api_key` 明文；`user_bind` 无索引/唯一 |
| 时迹 | 核心模型（日期 + 分钟区间 + 分类）合理 | `time_record` 索引错误；分类逻辑删除失效；`duration` 派生值；`is_manual` 死字段 |
| 财务 | 收支分表、金额 DECIMAL、分类/支付方式字典合理 | 无用户时间索引；`likeRight(year)`/`undated` 死分支；金额缺少非负 CHECK；`inc_date` 与 `exp_time` 粒度/命名不一致 |
| 目标 | 进度模式（手动/GraphQL）设计清楚 | 索引不匹配排序；`year/month/day` 与 `start_date/end_date` 双套维度；`target/current` 派生一致性 |
| 阅读/影视/演出 | 业务字段清晰，状态枚举统一 | 进度单位“页数或百分比”“集数或时长”未拆列；`performance` 无排序分页；`performance_date` 类型 |
| 银行卡 | 安全设计最好：密文、指纹、末四位、模板 | 唯一性/检查约束不足；6 个索引需复核；`expiry_month` 用 DATE 存月首日 |
| 衣柜/设备 | 采集来源字段统一，订单索引方向正确 | 订单索引不是唯一，幂等只能靠应用；`wardrobe_category` 无索引；死列 `purchase_company` |
| 通知 | 投递状态机、重试、加密载荷设计合理 | 配置/偏好缺唯一键和索引；`dedup_key` 无唯一约束；重试索引首列不是 `channel` |
| 个人数据导出 | 4 张表职责清楚，票据/摘要/租约/审计完整 | `request_key` 唯一键与软删除；`data_export_grant` 无 `user_id` 索引（按 token 查询可接受） |
| 系统/字典/日志 | 菜单、字典、定时任务、日志分表清楚 | 三套字典/枚举；菜单 path 唯一 + 软删除；日志无保留；文档漂移 |

## 八、建议的整改顺序

### 阶段 0：先做数据核查，不碰结构

1. 查有效重复：`user.username`、`user.email`、`user_bind`、`notification_*`、`system_config`、`api_key`、`bank_card`、`b_video`、`sys_menu.path`、`cbti_personality.code`。
2. 查删除值：各表 `is_deleted` 是否只有 0/1，`is_enabled` 是否有 NULL，`create_time/update_time` 是否有 NULL。
3. 查孤儿：`time_record.category_id`、`file.biz_id`、`task_detail.task_id`、`thought_rela_event.thought_id`。
4. 查时区：`@@global.time_zone`、`@@session.time_zone`、`NOW()`、`UTC_TIMESTAMP()` 与应用日志时间对照。
5. 对 117 库做结构预检，确认本文所述有效结构与实际库差异。

### 阶段 1：P1（上线前）

1. 修 `TimeTrackerCategoryEntity` 的 `isDeleted` 遮蔽，补删除过滤；确认公共分类删除不会留下孤儿覆盖记录。
2. 修 `likeRight(year)` → 日期范围；决定 `undated` 是删除还是让日期列可空。
3. 新增索引迁移（先在有数据量环境 `EXPLAIN` 验证），优先 `time_record`、`expense`、`income`、`b_video`、`user_bind`、`notification_*`、`memo`、`thought`、`exercise_record`、`task_detail`。
4. 先核查存量重复与唯一性规则，再新增约束，并将数据库冲突转换为明确的业务错误；普通索引仅改善读取性能，不能解决并发重复。
5. 修 `sys_menu.path`、`cbti_personality.code` 的软删除唯一冲突。

### 阶段 2：P2（上线前或上线后第一批）

1. 公共字段统一：`create_time/update_time` NOT NULL + 默认值，`is_enabled` NOT NULL，`is_deleted` 统一 `tinyint`。
2. 主键策略统一：24 张 `AUTO_INCREMENT` 表二选一；修 `SysDictDataVO.id` 截断；明确 `time_record.id`/`file.id` 的边界。
3. 死表死列清理：`record_article*`、`enum_type`、四个死列；同批改注销/导出/实体/Mapper/文档。
4. 文件模型收敛：`file`/`storage_object` 单一来源；单附件列迁移后删除。
5. 日志保留、敏感字段加密、时区统一。
6. 字典/枚举收敛，删除 `enum_type`，补 `sys_dict_data.dict_id` 索引。

### 阶段 3：P3（持续治理）

1. 删除冗余/未使用索引，补 `performance` 排序，减少 `SELECT *`/N+1。
2. 文档修正：`login_log.ip_address`、user 索引清单、`bank_card_cover_template`、`record_article` 状态、`time_record` 0–1440。
3. 加契约测试：实体全字段查询已有；建议增加
   - `SchemaContractTest`：唯一键/索引存在性；
   - `SoftDeleteUniqueTest`：删除后重建菜单/人格/分类；
   - `AccountErasureCoverageTest`：含 `user_id` 的表均登记注销策略，并验证对应处理；
   - `AuditFieldContractTest`：按表职责验证必需审计字段非空，保留明确的日志表例外；
   - `TimezoneContractTest`：数据库会话时区与应用时区一致。

## 九、验证边界与未覆盖项

- **未连接 117 业务库**：所有“存量重复/孤儿/时区”结论都需要在目标库用只读 SQL 核实；本文不把源码推断写成目标库事实。
- **未做并发复现**：唯一性冲突、`TooManyResultsException`、分类物理删除是基于 DDL + 调用链 + MyBatis-Plus 运行时 `TableInfo` 的静态/初始化验证，未启动服务做 HTTP/DB 写入。
- **EXPLAIN 无数据量**：只证明计划形状（`ALL`/`key=NULL`/`Using filesort`），不证明实际耗时；建议索引未做 A/B 实测。
- **未运行全量测试/构建**：本次为只读审查，未执行 `mvn test`、Flyway 预检、客户端构建或真实导出。
- **未覆盖**：Neo4j 关系模型、Redis 缓存命中率、MCP 工具权限、Chrome 插件采集行为、Mac 端；数据库备份/恢复演练也不在本次范围。
- **文档比对**：覆盖 70/72 张表；`user_body_profile` 为人工核对，列注释逐字校对为抽样，不是 1037 列全量语义审计。
- **2026-11-08 文档整理**：仅重新统计已有结构 TSV、抽查上述源码、检查文档引用与格式；未重新执行迁移、`EXPLAIN`、实体初始化或业务测试。原始记录未完整保存的验证已在第二节注明。
