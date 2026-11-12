# AIO Life 数据库设计复审（2026-11-12）

> 复审日期：2026-11-12。对象为后端仓库当前工作树的 PostgreSQL V 迁移链（`V20261110_01` 至 `V20261112_05`，其中 `V20261112_01` 至 `V20261112_05` 为未提交改动）、实体 / Mapper 注解 SQL、导出配置；对照 [2026-11-06 数据库设计审查](../2026-11-06-database-design/README.md)。
>
> 本次在隔离 PostgreSQL 18 容器中按顺序执行全部 18 个迁移，并用项目 classpath 初始化 MyBatis-Plus `TableInfo`、实测 `ON CONFLICT` 推断和排序规则。未连接业务库（含 117），未在真实数据量上执行 `EXPLAIN`，未启动应用或做并发复现。
>
> **整改状态**：本文所列 P1 已在 2026-11-12 同日处理，具体变更与验证结果见[文末整改记录](#九整改记录2026-11-12)；正文保留复审时的发现与证据。

阅读入口：[结论](#一结论) · [复审范围](#二复审范围与方法) · [已整改](#三已整改应保留的部分) · [P1](#四p1升级已有库前必须处理) · [P2](#五p2一致性与契约) · [P3](#六p3清理项与观察项) · [整改顺序](#七建议的整改顺序) · [验证边界](#八验证边界与未覆盖项)

## 一、结论

**上次审查的整改覆盖了大部分唯一键与结构清理，但热点索引和时迹分类逻辑删除仍未处理；本次整改还引入了两个可复现的运行时缺陷，必须在升级任何已有库前修复。**

- 18 个迁移在 PostgreSQL 18 空库上全部执行成功，结构本身自洽；当前 68 张业务表、32 个非主键唯一索引、31 个 CHECK、0 个外键。
- 上次 P1-2（核心唯一键）、P1-4（财务 `undated` / `likeRight`）、P1-5（软删除后重建唯一键）基本完成；**P1-1（热点查询索引）完全未处理，P1-3（时迹分类逻辑删除）未修复**。
- 新增 P1：
  1. **`ON CONFLICT` 与部分唯一索引谓词不匹配**，定时任务注册和 B 站视频导入在真实 PostgreSQL 上报错（已实测）。
  2. **个人数据导出目录仍指向已删除的 `user_dict_type`**，按该 key 导出会生成不存在的表查询。
  3. **基础迁移 `V20261110_01` 被就地改写**，任何已执行旧版本的库都会 Flyway 校验失败。
  4. **删除四张表和三个列的迁移没有数据预检**，有直接丢数风险。
- 系统尚未上线，若确认所有环境都未执行过旧版 `V20261110_01` 且业务数据为空，第 3、4 项可在记录确认后放行；否则必须先修正。

## 二、复审范围与方法

- **迁移实测**：在隔离 `postgres:18-alpine` 容器按 `sql/migrations/` 文件名顺序执行 18 个脚本，全部成功。
- **结构统计**：68 张业务表；32 个非主键唯一索引；31 个 CHECK；**0 个外键**；`create_time` 42 张表可空、`update_time` 40 张表可空、`is_enabled` 3 张表可空。
- **索引覆盖**：按 `pg_index` 统计，10 张表只有主键：`exercise_record`、`expense`、`income`、`login_log`、`memo`、`sys_work_calendar`、`task_detail`、`thought`、`thought_rela_event`、`wardrobe_category`。其中 `sys_work_calendar` 以 `calendar_date` 为主键，按日期查询本身走主键，不属于缺索引问题。
- **运行时初始化**：用项目 `target/classes` 与 Maven 依赖 classpath 调用 `TableInfoHelper.initTableInfo`，结果为 `TimeTrackerCategoryEntity logicDelete=false`、`GoalEntity logicDelete=false`、`ExpenseEntity logicDelete=true`。
- **SQL 行为实测**：在迁移后的库上执行 `IBVideoMapper` / `ScheduledJobMapper` 的 upsert、菜单路径插入和 `aio_unicode_ci` 等值比较。
- **未覆盖**：业务库存量重复 / 孤儿 / 时区、数据量级执行计划、`mvn test`、Flyway `verify`、应用启动、HTTP 并发、Web / 移动端实际导出。

## 三、已整改、应保留的部分

| 整改 | 结果 |
| --- | --- |
| 核心业务唯一键改为部分唯一索引（`WHERE is_deleted = 0`） | `user`、`user_bind`、`notification_*`、`system_config`、`api_key`、`b_video`、字典、银行卡指纹与标签关联均已覆盖；`ON CONFLICT` 之外还需见 P1-1 |
| 软删除后重建菜单 / 人格 / 地区 / 定时任务 / 导出任务 | `sys_menu.path`、`cbti_personality.code`、`system_region.code`、`sys_scheduled_job.job_code`、`data_export_job(user_id, request_key)` 已改部分唯一，[V20261112_01:122-141](../../../aio-life-server/sql/migrations/V20261112_01__p1_unique_constraints_and_collations.sql#L122-L141) |
| 财务日期查询修复 | `undated` / `likeRight(year)` 已移除，改为半开区间；[ExpController.java:82-96](../../../aio-life-server/src/main/java/top/aiolife/record/api/ExpController.java#L82-L96)、[IncomeController.java:73-80](../../../aio-life-server/src/main/java/top/aiolife/record/api/IncomeController.java#L73-L80) |
| 时迹时间语义与约束 | `start_minute` / `end_minute` / `duration_minutes` 命名明确；`ck_time_record_time_range` 已校验范围、顺序和时长派生，[V20261112_04:136-139](../../../aio-life-server/sql/migrations/V20261112_04__remaining_constraints_and_cleanup.sql#L136-L139)。实测列重命名后约束定义已自动跟随 |
| 死表死列清理 | `record_article*`、`enum_type`、`user_dict_type`、`device.purchase_company`、`time_tracker_category.code`、`honor_record.file_id` 已删除，[V20261112_04:142-151](../../../aio-life-server/sql/migrations/V20261112_04__remaining_constraints_and_cleanup.sql#L142-L151)；`CurrentSchema` 测试辅助同步登记 |
| 同名不同单位列显式化 | 时迹、视频、演出时长列已重命名并同步实体、查询、导出与文档，[V20261112_05](../../../aio-life-server/sql/migrations/V20261112_05__rename_duration_units.sql) |
| `user` 保留字处理 | 表已重命名为 `sys_user`，[V20261112_03](../../../aio-life-server/sql/migrations/V20261112_03__rename_user_table.sql)；实体与手写 SQL 已同步，未发现残留 `FROM "user"` |
| 注册并发冲突 | `UserServiceImpl` 已捕获 `DuplicateKeyException` 并转为业务错误，[UserServiceImpl.java:552-577](../../../aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L552-L577) |

## 四、P1：升级已有库前必须处理

### P1-1 `ON CONFLICT` 与部分唯一索引谓词不匹配（本次新引入）

`V20261112_01` 把定时任务和 B 站视频的唯一索引改成了部分唯一，但两个 upsert 没有同步谓词：

- [ScheduledJobMapper.java:14](../../../aio-life-server/src/main/java/top/aiolife/scheduling/mapper/ScheduledJobMapper.java#L14)：`ON CONFLICT (job_code) DO NOTHING`，对应索引是 `WHERE is_deleted = 0`，[V20261112_01:127-129](../../../aio-life-server/sql/migrations/V20261112_01__p1_unique_constraints_and_collations.sql#L127-L129)。
- [IBVideoMapper.java:55](../../../aio-life-server/src/main/java/top/aiolife/record/mapper/IBVideoMapper.java#L55)：`ON CONFLICT (user_id, bvid) WHERE is_deleted = 0 DO NOTHING`，对应索引谓词还包含 `bvid IS NOT NULL AND bvid <> ''`，[V20261112_01:119](../../../aio-life-server/sql/migrations/V20261112_01__p1_unique_constraints_and_collations.sql#L119)。

在迁移后的 PostgreSQL 18 上实测：

```text
-- 定时任务注册
ERROR: there is no unique or exclusion constraint matching the ON CONFLICT specification
-- B 站导入（当前代码写法）
ERROR: there is no unique or exclusion constraint matching the ON CONFLICT specification
-- 把谓词补全后
INSERT 0 1
```

影响：`ScheduledJobService.seed()` 在启动 / 注册任务时直接失败，[ScheduledJobService.java:54](../../../aio-life-server/src/main/java/top/aiolife/scheduling/service/ScheduledJobService.java#L54)；B 站视频导入的 `insertIgnoreActive` 失败。

修复二选一：

1. 让 upsert 谓词与索引完全一致：`ON CONFLICT (job_code) WHERE is_deleted = 0`、`ON CONFLICT (user_id, bvid) WHERE is_deleted = 0 AND bvid IS NOT NULL AND bvid <> ''`。
2. 或调整索引谓词，让它成为 upsert 谓词的逻辑推论。

必须补一个真实 PostgreSQL 的 Mapper upsert 回归测试；当前单测主要覆盖 Service，未覆盖这类索引推断错误。

另外 [V20261111_01:42](../../../aio-life-server/sql/migrations/V20261111_01__query_workspace_menus.sql#L42) 的 `ON CONFLICT (path)` 在新库中先于部分索引执行，因此空库链能通过；任何后续种子或人工重放都必须带上 `WHERE is_deleted = 0`。本次实测该写法在迁移后的库上同样会报错。

### P1-2 热点查询索引仍未补（上次 P1-1 未处理）

除新增的唯一索引外，业务流程的查询索引没有变化。10 张只有主键的表中，以下属于高频路径：

| 表 | 当前索引 | 现存查询 / 问题 | 候选索引 |
| --- | --- | --- | --- |
| `expense` | 无 | 列表按 `user_id + is_deleted + exp_time 范围 + ORDER BY exp_time DESC, id DESC`，[ExpController.java:96](../../../aio-life-server/src/main/java/top/aiolife/record/api/ExpController.java#L96) | `(user_id, is_deleted, exp_time, id)` |
| `income` | 无 | 同上，`inc_date` 排序，[IncomeController.java:80](../../../aio-life-server/src/main/java/top/aiolife/record/api/IncomeController.java#L80) | `(user_id, is_deleted, inc_date, id)` |
| `time_record` | `(date)` | 按用户 + 日期查询，现有索引仅按日期，回表过滤用户 | `(user_id, is_deleted, date, start_minute)`，替换旧单列索引 |
| `b_video` | `status` / `bvid` / `aid` / `title` | 没有以 `user_id` 开头；列表按用户 + 更新时间 | `(user_id, is_deleted, update_time, id)`；复核后删除低收益索引 |
| `exercise_record` | 无 | 列表按用户 + 日期 | `(user_id, is_deleted, exercise_date, id)`；`(user_id, time_id)` |
| `memo` | 无 | 列表 / 首页按用户 + 更新时间 | `(user_id, is_deleted, update_time, id)` |
| `thought` | 无 | 看板 / 列表按用户 + 更新时间 | `(user_id, is_deleted, update_time, id)` |
| `thought_rela_event` | 无 | 按 `thought_id` 批量装配 / 删除 | `(thought_id, id)` |
| `task_detail` | 无 | 按 `task_id`、关注列表、排序 | `(task_id, user_id, is_completed, sort_order, id)`；`(user_id, is_starred, is_completed, priority, sort_order, id)` |
| `wardrobe_category` | 无 | 按用户 + 父分类 | `(user_id, parent_id)` |
| `login_log` | 无 | 注销按 `user_id` / `username + created_at` 清理 | `(user_id, created_at)`，必要时 `(created_at)` |
| `device` | 采集订单索引 | 列表按用户 + 购买日期 | `(user_id, is_deleted, purchase_date, id)` |
| `performance` | `(user_id, is_deleted, id)` | 缺少日期排序；分页无 `ORDER BY` | `(user_id, is_deleted, performance_date, id)` |

`notification_delivery` 的去重和重试索引也仍未按查询形态调整，见 P2-5。索引最终仍需在有数据量的 PostgreSQL 上 `EXPLAIN` 验证，本次只确认索引不存在。

### P1-3 时迹分类逻辑删除仍失效（上次 P1-3 未修复）

[TimeTrackerCategoryEntity.java:73](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/TimeTrackerCategoryEntity.java#L73) 仍重复声明 `private Integer isDeleted;`，且没有 `@TableLogic`，遮蔽了 `BaseEntity` 的注解字段。用项目 classpath 初始化 `TableInfo` 实测：

```text
TimeTrackerCategoryEntity logicDelete=false table=time_tracker_category
```

后果保持上次结论：

- [TimeTrackerCategoryServiceImpl.java:497](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeTrackerCategoryServiceImpl.java#L497) 的 `removeById` 为物理 DELETE；
- 同一方法 [500](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeTrackerCategoryServiceImpl.java#L500) 删除用户覆盖记录也是物理删除；
- [ensureNoChildren:61-66](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeTrackerCategoryServiceImpl.java#L61-L66) 统计子分类时包含已删除行；
- [listUserHiddenCategories:152-160](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/TimeTrackerCategoryServiceImpl.java#L152-L160) 可能返回已删除分类；
- `time_record.category_id` 没有外键，删除公共分类时仍可能留下孤儿。

`V20261112_04` 新增的 `uk_time_tracker_category_user_template` 依赖 `is_deleted` 的语义；逻辑删除不生效时，该索引无法阻止“软删除覆盖记录后重新创建”类问题，实际走的是物理删除。

修复：删除子类字段，或给子类字段补 `@TableLogic`。同时把 [application.yml:151](../../../aio-life-server/src/main/resources/application.yml#L151) 的 `logic-delete-field: is_deleted` 改为 Java 属性名 `isDeleted` 或直接删除；当前值与属性名不匹配，实际没有全局效果。修完后补删除 / 重建 / 覆盖记录级联测试。

### P1-4 导出目录仍引用已删除的 `user_dict_type`

复审时 [datasets.json](../../../aio-life-server/src/main/resources/export/datasets.json) 仍登记 `table: "user_dict_type"`，但该表已在 `V20261112_04` 删除；[excluded-columns.json](../../../aio-life-server/src/main/resources/export/excluded-columns.json) 也有残留。

导出注册表会登记 `datasets.json` 的全部条目，`resolve(keys)` 只检查 key 是否存在，不检查表是否仍存在；[ExportDatasetSql.java:24-28](../../../aio-life-server/src/main/java/top/aiolife/export/mapper/ExportDatasetSql.java#L24-L28) 直接拼 `FROM user_dict_type`。因此只要请求包含 `user_dict_type`，导出任务就会在真实 PostgreSQL 上失败，而不是在申请阶段被拒绝。

现有 [ExportDatasetRegistryTest](../../../aio-life-server/src/test/java/top/aiolife/export/ExportDatasetRegistryTest.java) 没有覆盖这个问题：第一项测试只遍历基线表并跳过已删表，第二项测试从基线 DDL 读取字段，无法发现“数据集指向已删表”。

修复：删除该数据集与排除项；把测试改为断言每个已登记数据集的表不在 `CurrentSchema.dropped()` 中且当前结构存在。文档 [数据库设计审查与字段规范.md:70](../../../aio-life-server/docs/数据库设计审查与字段规范.md#L70) 已写“导出配置同步清理”，与实际不符。

### P1-5 基础迁移 `V20261110_01` 被就地改写

工作树中的基础迁移改了两类内容（均为未暂存改动）：

- 10 张表的 `is_deleted` 从 `integer` 改为 `smallint`；
- `wardrobe_item.file_id` 从 `varchar(50)` 改为 `varchar(32)`，并改注释。

这违反 [数据库表结构.md:5](../../../aio-life-server/docs/数据库表结构.md#L5) 与仓库约定“已执行迁移不可改写”。只要有任何环境执行过已提交版本的 `V20261110_01`：

- Flyway `validate` 会因 checksum 不一致失败，后续 `V20261112_*` 无法迁移；
- 如果通过 `repair` 或跳过校验绕过，这些库仍是 `integer` / `varchar(50)`，与文档和新建库不一致，且不会被执行后续迁移修正。

处理方式：把基础文件恢复到已提交内容，新增更高版本 V 迁移，用 `ALTER TABLE ... ALTER COLUMN is_deleted TYPE smallint USING is_deleted::smallint` 和 `wardrobe_item.file_id` 长度变更（变更前检查超长值）。只有在确认 **没有任何环境执行过旧版基础迁移** 时，才可以保留就地修改，并在交付说明中明确该前提。

### P1-6 删除表 / 列的迁移没有数据预检

[V20261112_04:3](../../../aio-life-server/sql/migrations/V20261112_04__remaining_constraints_and_cleanup.sql#L3) 已声明“删除表列会丢弃其中数据”，但脚本直接执行 `DROP TABLE` / `DROP COLUMN`，没有像唯一键那样先检查存量：

- `record_article`、`record_article_annotation`、`enum_type`、`user_dict_type` 是否有数据；
- `honor_record.file_id` 是否有非空引用，是否需要先转入 `file` 关系；
- `device.purchase_company`、`time_tracker_category.code` 是否有需要保留的业务值；
- `user_dict_type` 是否承载过用户自定义字典类型的名称 / 图标 / 颜色。

建议在迁移开头增加 `DO $$` 预检：目标表有数据或目标列有非空值时 `RAISE EXCEPTION`，由人工确认、备份或迁移后再执行；不要依赖“系统未上线”作为默认前提。`V20261112_05` 的 `pages_info` 更新也声称“JSON 非数组不会静默跳过”，但实际 `WHERE jsonb_typeof(pages_info) = 'array'` 会静默跳过非数组行，需要同样预检或改写处理。

## 五、P2：一致性与契约

### P2-1 唯一冲突的写入口与文档描述不一致

[数据库设计审查与字段规范.md:51](../../../aio-life-server/docs/数据库设计审查与字段规范.md#L51) 写“写入口改为 `ON CONFLICT` 或明确的唯一冲突业务错误”，但实际：

- `ScheduledJobMapper`、`IBVideoMapper` 的 `ON CONFLICT` 已失效（P1-1）；
- `UserBindServiceImpl`、通知配置 / 偏好、`SystemConfigServiceImpl` 仍是“先查再写”，并发下由数据库唯一索引抛 `DuplicateKeyException`，接口层是否转成 4xx 未逐一确认；
- `ApiKeyServiceImpl.generateApiKey` 已捕获并重试，但注释假设 `save` 处于自动提交；一旦被外层事务调用，PostgreSQL 事务会进入 aborted 状态，重试不会成功。

建议逐写入口确认：要么数据库冲突转明确业务错误，要么使用与索引谓词一致的 `ON CONFLICT`；并在真实 PostgreSQL 上补并发冲突测试。

### P2-2 业务约束仍大量依赖应用

当前 31 个 CHECK 集中在生活足迹、身体档案、目标进度和时迹。以下稳定不变量仍无数据库约束：

| 规则 | 现状 |
| --- | --- |
| `expense.amt`、`income.amt` 非负 | 无 CHECK；DTO 也缺少 `@DecimalMin` |
| `bank_card.statement_day` / `repayment_day` 1–31 | 列可存 0 或 32–255 |
| `bank_card.expiry_month` 只存每月 1 日 | 无 CHECK |
| `goal.end_date >= start_date` | 无 CHECK |
| `membership_record.expiry_date >= start_date` | 无 CHECK |
| `device.end_date >= purchase_date` | 无 CHECK |
| `milestone.end_date >= date` | 无 CHECK |
| `income.tax <= amt` | 无 CHECK |
| `b_video.watched_duration_seconds <= duration_seconds` | 无 CHECK |

数据库约束收紧后必须同步 DTO 校验，不能把“数据库会拦住”当成接口契约。

### P2-3 公共字段契约仍未统一

- `create_time` 42 张表可空，`update_time` 40 张表可空；应用漏填时审计链断裂。
- `is_enabled` 3 张表可空（`sys_dict_data`、`sys_dict_type`、`user_dict_data`），按 `is_enabled = 1` 查询会静默排除 NULL 行。
- `is_deleted` 在新库中已全部 `smallint`，但该结果来自 P1-5 的就地修改；已执行旧基础迁移的库仍是 `integer`。
- 审计时间由应用显式维护，数据库无 `ON UPDATE`，需要确认所有写入路径都调用 `fillCreateCommonField` / `fillUpdateCommonField`。
- 0 个外键；`user_id`、`file.biz_id`、`task_detail.task_id`、`thought_rela_event.thought_id` 等关系没有数据库兜底。

建议按业务表 / 日志表分别确定 `create_time`、`update_time`、`is_enabled`、`is_deleted` 的 `NOT NULL`、默认值和维护方，再交付增量迁移；新增用户归属表必须登记注销策略并提供孤儿检查。

### P2-4 敏感字段仍是明文

- `api_key.api_key` 仍明文保存，登录时明文等值查询；唯一索引已补，但数据库备份 / 导出仍暴露原文。
- `user_bind.access_token` 是明文 `text`，承载 GitHub / LeetCode / 微信读书等第三方凭证。
- `password_vault.username` 是明文 `text`，密码 / 备注由客户端加密；两端加密契约仍需确认。

建议只存哈希或应用层密文，创建时返回一次原文；导出已排除这些字段，但不能替代静态加密。

### P2-5 通知去重与重试索引

[FeishuNotificationServiceImpl.java:449-474](../../../aio-life-server/src/main/java/top/aiolife/record/service/impl/FeishuNotificationServiceImpl.java#L449-L474) 用 Redisson 锁 + 先查后插实现去重，`notification_delivery` 没有 `(user_id, channel, dedup_key)` 唯一键或普通索引；当前只有 `(status, next_retry_time)`。去重查询会随表增长退化为顺序扫描，跨实例仍依赖锁而不是数据库约束。

建议：

- 去重永久有效时加唯一 `(user_id, channel, dedup_key)`；允许删除后重发时用 `WHERE is_deleted = 0` 部分唯一。
- 重试扫描按真实查询补 `(channel, status, next_retry_time, id)`，并明确按 `channel` 过滤。

### P2-6 日志保留与登录日志索引

`login_log` 没有二级索引，而注销清理按 `user_id` 或 `username + created_at` 删除；`api_key_log`、`mail_log`、`sys_activity_log`、`sys_scheduled_job_log`、`notification_delivery` 持续增长且无保留策略。建议确定 90 / 180 天保留期，增加按时间清理任务，量级上来后按月分区；`sys_activity_log` 三个同前缀索引也需要复核写放大。

### P2-7 文件模型仍是双份元数据

`file` 与 `storage_object` 都保存对象键、大小、MIME / 哈希；`file.storage_object_id` 可空，普通上传仍可能只写 `file`。业务表同时存在单附件列（`movie.file_id`、`read_record.file_id`、`device.file_id`、`wardrobe_item.file_id`）与 `file.biz_type/biz_id` 关系。建议明确唯一物理对象来源，单附件列迁移后删除，并加契约测试保证两表元数据一致。

### P2-8 ID 与字段类型契约

| 位置 | 问题 |
| --- | --- |
| `time_record.id` | `varchar(32)`，而 `file.biz_id` 是 `bigint`，不能反向关联；接入统一附件模型前需单独评估 |
| [SysDictDataVO.java:16](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/vo/SysDictDataVO.java#L16) | `id` 是 `Integer`，而 `sys_dict_data.dict_code` 是雪花 `bigint`，MapStruct 会截断 |
| [TimeRecordEntity.java:60](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/TimeRecordEntity.java#L60) | `isManual` 是 `Long`，列是 `smallint` |
| [MilestoneEntity.java:25](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/MilestoneEntity.java#L25) | `date` 是 `String`，列是 `date` |
| [PerformanceEntity.java:49](../../../aio-life-server/src/main/java/top/aiolife/record/pojo/entity/PerformanceEntity.java#L49) | `performanceDate` 是 `LocalDate`，列是 `timestamp(0)`，语义与精度不一致 |

建议按列语义改回正确 Java 类型，并在接口契约中保持 ID 字符串输出。

### P2-9 排序与分页

- [PerformanceRecordService.java:27](../../../aio-life-server/src/main/java/top/aiolife/record/service/PerformanceRecordService.java#L27) 分页没有 `ORDER BY`，跨页顺序未定义；应至少 `performance_date DESC, id DESC`。
- `expense` / `b_video` 等深分页仍是无上限页码；建议限制页码或改游标分页，并以唯一 ID 兜底。

### P2-10 排序规则范围需要逐列确认

`aio_unicode_ci` 使用 `und-u-ks-level1`，实测大小写、重音、全角 / 半角均视为相等：

```text
'a' = 'A' → true；'é' = 'e' → true；'Ａ' = 'A' → true
```

因此 `sys_menu.path` 的 `/Foo` 与 `/foo` 会触发唯一键冲突（已实测），字典值、`data_export_job.request_key` 等标识符也受同样影响。`V20261112_01` 已把 API Key、BV 号、对象键、外部订单号等改为 `COLLATE "C"`，但没有处理菜单路径和字典值。建议逐列判定：路径 / 机器标识使用确定性排序，展示文本保留 ICU 不区分大小写；判定结果写入字段规范。

### P2-11 死字段与迁移说明

- `sys_dict_data.dict_type` 仍是死列，文档已明确后续以 `dict_id` 关联为唯一来源，但尚未删列。
- `V20261112_05` 的头部说明与 `WHERE jsonb_typeof(pages_info) = 'array'` 行为不一致，见 P1-6。
- `UserDictTypeController` 仍保留“用户字典类型”命名，但已改为枚举 + `user_dict_data` 查询，不再依赖已删除表；接口命名是否保留需产品确认。

## 六、P3：清理项与观察项

| 项 | 说明 |
| --- | --- |
| 冗余索引 | `anniversary_record.idx_user_id`、`goal.idx_user_id`、`wardrobe_item.idx_user_id` 与更长索引最左前缀重复；`time_tracker_category_idx_category_user_template` 与新唯一索引重复 |
| 低收益索引 | `b_video.idx_status` / `idx_aid` / `idx_title`、`honor_record.idx_honor_date` / `idx_category_id` 在已审查查询中未见筛选引用，删除前复核 |
| `SELECT *` | `IBVideoMapper.findOwnedByBvid` / `lockOwned` 等；`b_video` 含大字段，二级索引回表成本高 |
| N+1 | `HonorRecordController`、`PerformanceRecordService` 每条记录查一次附件，改 `biz_id IN (...)` |
| 系统消息发送者 | `message.sender_id NOT NULL`，[SystemNotificationSender.java:33](../../../aio-life-server/src/main/java/top/aiolife/record/notification/SystemNotificationSender.java#L33) 写死 `1L`；用户 ID 由雪花生成，1 不一定是有效账号 |
| 目标逻辑删除 | `GoalEntity` 不继承 `BaseEntity`、无 `@TableLogic`，所有查询需手工带 `is_deleted` |
| 软删唯一键 | `user_body_profile(user_id)` 仍是全量唯一；新增删除入口前必须改部分唯一或物理删除 |
| 物理删除约定 | `user_home_card_preference`、`user_menu_hidden` 使用显式 `DELETE`，与全量唯一键一致；不要改成 `BaseMapper.remove` |
| 存储对象唯一键 | `storage_object(bucket, sha256)` 是全量唯一；若对象允许软删除，需要部分唯一或禁止软删 |
| 文档状态 | 字段规范第 51、70 行的完成度描述高于实际，需按本次复审更新 |
| 迁移可重复性 | `V20261112_02` 使用 `IF EXISTS`，其余新迁移依赖 Flyway 单次执行；不要手工重放 |

## 七、建议的整改顺序

1. **先修 P1-1、P1-4**：两个 `ON CONFLICT` 谓词和导出死表都是确定会失败的运行时缺陷；补真实 PostgreSQL 回归测试。
2. **确认 P1-5 前提**：查清是否有环境执行过旧版 `V20261110_01`。有则恢复基础文件并新增 `V` 迁移；无则在交付说明中记录“空库重建”前提。
3. **修 P1-3**：删除 `TimeTrackerCategoryEntity.isDeleted` 或补 `@TableLogic`，修 `application.yml` 全局字段名，补删除 / 重建 / 级联测试。
4. **补 P1-6 数据预检**：对四张表和三个列做行数 / 非空检查；`honor_record.file_id` 先确认是否需转入 `file` 关系。
5. **新增热点索引迁移**（P1-2）：优先 `expense`、`income`、`time_record`、`b_video`、`memo`、`thought`、`exercise_record`、`task_detail`、`wardrobe_category`、`login_log`、`notification_delivery`；在有数据量环境 `EXPLAIN` 后落地。
6. **P2 批量**：业务 CHECK 与 DTO 校验、公共字段 NOT NULL、敏感字段加密 / 哈希、日志保留、文件模型收敛、ID 类型、排序规则逐列确认。
7. **P3 持续治理**：删除冗余索引、减少 `SELECT *` / N+1、补 `performance` 排序、同步文档与导出目录。

## 八、验证边界与未覆盖项

- **未连接业务库**：所有存量重复、孤儿、时区和数据量结论仍需在目标库只读核实；本次“删除表列有数据”仅是风险判断，不是目标库事实。
- **未做并发复现**：唯一冲突、逻辑删除、截图中的运行时结论来自 DDL + 代码 + `TableInfo` 初始化，未启动服务做 HTTP / DB 写入。
- **未做数据量级执行计划**：本次只在空库确认索引存在 / 不存在，没有用 `EXPLAIN` 证明候选索引会被选中。
- **未运行测试 / 构建**：未执行 `mvn test`、Flyway `verify`、应用启动、Web / 移动端构建或真实导出。
- **覆盖范围**：迁移链、结构、实体 / Mapper 注解 SQL、导出配置；未覆盖 Neo4j、Redis 缓存、MCP 权限、Chrome 插件采集和备份恢复演练。
- **文档整理**：本次只记录复审发现与验证边界，不代表整改已实施；迁移脚本与代码仍需按仓库规范单独提交。

---

**复审版本**：后端工作树 `d62506f` + 未提交的 `V20261112_01` 至 `V20261112_05`；根仓库评审文档为本次新增。

## 九、整改记录（2026-11-12）

| 项 | 处理 | 验证 |
| --- | --- | --- |
| P1-1 | `ScheduledJobMapper` 与 `IBVideoMapper` 的 `ON CONFLICT` 谓词改为与部分唯一索引一致 | 隔离 PostgreSQL 18 上重复执行 upsert：首次插入 1、重复 0；`PostgresqlRegressionIntegrationTest` 新增用例通过 |
| P1-2 | 新增 `V20261112_07__hot_query_indexes.sql`，覆盖收支、时迹、视频、运动、备忘录、闪念、任务明细、衣柜分类、登录日志、设备和演出；`PerformanceRecordService` 补确定性排序 | 全链迁移成功，`pg_indexes` 确认索引存在 |
| P1-3 | 删除 `TimeTrackerCategoryEntity.isDeleted` 重复声明，改由 `BaseEntity` 的 `@TableLogic` 生效；删除 `application.yml` 中不匹配的全局字段名配置 | `TableInfo` 实测 `logicDelete=true`；新增真实 PostgreSQL 删除用例通过 |
| P1-4 | 从 `datasets.json` 与 `excluded-columns.json` 移除 `user_dict_type`；导出测试增加已删表断言 | `ExportDatasetRegistryTest` 3 项通过 |
| P1-5 | 回退 `V20261110_01` 就地修改；新增 `V20261112_06` 统一 `is_deleted` 为 `smallint`、收窄 `wardrobe_item.file_id` | 空库全链迁移成功；`information_schema` 确认无 `integer` 的 `is_deleted` |
| P1-6 | `V20261112_04` 增加待删表列存量预检；`V20261112_05` 增加 `pages_info` 非数组预检 | 空库执行成功；有数据时由 `DO` 块中止 |

```bash
mvn -o test -Dtest=PostgresqlRegressionIntegrationTest,ExportDatasetRegistryTest,TimeTrackerCategoryServiceImplTest,TimeCategoryHierarchyTest,TimeTrackerCategoryCacheInvalidationTest,ScheduledJobTest,PerformanceFilesContractTest
```

结果：64 项测试通过，0 失败。仓库自带 Flyway 校验 `mvn -f tools/flyway/pom.xml -o verify` 通过：24 项单元测试 + 4 项集成测试，空库执行 20 个迁移、重复迁移、增量升级、事务回滚与结构契约均通过。未覆盖：业务库存量、数据量级 `EXPLAIN`、应用启动、Web / 移动端实际页面。

**目标库执行记录（2026-11-12）**：确认实际结构已与目标一致后，对目标库依次执行 `flyway:repair`、`flyway:migrate`、`flyway:validate`；V20261112.05–08 应用成功，当前版本为 `20261112.08`。迁移前已做逻辑备份。复核结果：27 个用户、6581 条时迹、72 条视频记录保留；旧列名 0 个，新增的 16 个索引和更新后的 `ck_time_record_time_range` 均存在；审计字段已全部 `NOT NULL` 且有默认值，系统字典 `is_enabled` 为 `NOT NULL DEFAULT 1`，`user_dict_data` 保持 NULL 继承语义并通过 CHECK 约束。`20261110.01` 与 `20261112.04` 的历史校验和已按当前文件修复；其他执行过旧版基础迁移或旧版 04 的环境也需要同样的 repair 步骤。

### 后续字段优化（2026-11-12）

- `V20261112_08` 回填并收紧 `create_time` / `update_time`；系统字典 `is_enabled` 改为 `NOT NULL DEFAULT 1`；`user_dict_data` 保留 NULL=继承并增加 `CHECK (is_enabled IS NULL OR is_enabled IN (0,1))`。
- `TimeRecordEntity.isManual`、`TimeRecordListVO.isManual` 改为 `Integer`；`SysDictDataVO.id` 改为 `Long`，雪花 `dict_code` 不再被截断，接口按全局 Long 序列化为字符串。
- `UserDictDataServiceImpl` 把 NULL 显式视为“未停用/继承”，私有分类不再因 NULL 被过滤。
- 117 中 8 条 `file.biz_type='read_record'` 已在库内直接归一为 `read`；该修复未纳入 Flyway，重建库需单独执行 `UPDATE file SET biz_type='read' WHERE biz_type='read_record'`。

