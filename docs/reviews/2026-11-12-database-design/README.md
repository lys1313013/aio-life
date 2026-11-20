# 数据库设计复审与整改历史证据（2026-11-12）

审查日期为 2026-11-12；2026-11-13 删除已经完成的逐项问题分析及过期整改顺序，保留原环境、验证结果和目标库执行记录。本文没有在 2026-11-13 重新执行测试或迁移。

当前优化待办仅见[数据库设计审查与字段规范](../../../aio-life-server/docs/数据库设计审查与字段规范.md)，实际结构见[数据库表结构](../../../aio-life-server/docs/数据库表结构.md)。原 P1 的 upsert 谓词、热点索引、时迹分类逻辑删除、导出死表引用，以及后续公共字段、ID 数值类型与排序规则问题已有整改，不再作为当前缺陷展开。该批发现与整改见下方历史记录。

## 迁移历史说明

原审查针对后端 `d62506f` 加当时工作区改动，最初测试的链为 18 个 SQL 文件；后续扩展、合并后文件数发生变化。`V20261111_01` 及 `V20261112_01`–`12` 的内容后续已按当时明确要求并入初始结构或公共种子，原文件不再位于当前目录。正文历史结果中的 13/20/25 等文件数只对应各次执行时的版本，不代表当前链。

下列 `repair` 是当时目标库在备份、实际结构核对与迁移后的历史对齐记录，不是其他环境可以直接照做的升级指引。日常只新增 V，不改写已执行迁移；当前操作入口以[数据库初始化与验证](../../../aio-life-server/docs/数据库初始化与验证.md)为准。历史测试无法证明其他业务库结构一致，也不能代替有数据量的 PostgreSQL 执行计划。

## 二、复审范围与方法

- **迁移实测**：在隔离 `postgres:18-alpine` 容器按 `sql/migrations/` 文件名顺序执行 18 个脚本，全部成功。
- **结构统计**：68 张业务表；32 个非主键唯一索引；31 个 CHECK；**0 个外键**；`create_time` 42 张表可空、`update_time` 40 张表可空、`is_enabled` 3 张表可空。
- **索引覆盖**：按 `pg_index` 统计，10 张表只有主键：`exercise_record`、`expense`、`income`、`login_log`、`memo`、`sys_work_calendar`、`task_detail`、`thought`、`thought_rela_event`、`wardrobe_category`。其中 `sys_work_calendar` 以 `calendar_date` 为主键，按日期查询本身走主键，不属于缺索引问题。
- **运行时初始化**：用项目 `target/classes` 与 Maven 依赖 classpath 调用 `TableInfoHelper.initTableInfo`，结果为 `TimeTrackerCategoryEntity logicDelete=false`、`GoalEntity logicDelete=false`、`ExpenseEntity logicDelete=true`。
- **SQL 行为实测**：在迁移后的库上执行 `IBVideoMapper` / `ScheduledJobMapper` 的 upsert、菜单路径插入和 `aio_unicode_ci` 等值比较。
- **未覆盖**：业务库存量重复 / 孤儿 / 时区、数据量级执行计划、`mvn test`、Flyway `verify`、应用启动、HTTP 并发、Web / 移动端实际导出。

## 九、整改记录（2026-11-12）

| 项 | 处理 | 验证 |
| --- | --- | --- |
| P1-1 | `ScheduledJobMapper` 与 `IBVideoMapper` 的 `ON CONFLICT` 谓词改为与部分唯一索引一致 | 隔离 PostgreSQL 18 上重复执行 upsert：首次插入 1、重复 0；`PostgresqlRegressionIntegrationTest` 新增用例通过 |
| P1-2 | 新增 `V20261112_07__hot_query_indexes.sql`，覆盖收支、时迹、视频、运动、备忘录、闪念、任务明细、衣柜分类、登录日志、设备和活动；`EventRecordService` 补确定性排序 | 全链迁移成功，`pg_indexes` 确认索引存在 |
| P1-3 | 删除 `TimeTrackerCategoryEntity.isDeleted` 重复声明，改由 `BaseEntity` 的 `@TableLogic` 生效；删除 `application.yml` 中不匹配的全局字段名配置 | `TableInfo` 实测 `logicDelete=true`；新增真实 PostgreSQL 删除用例通过 |
| P1-4 | 从 `datasets.json` 与 `excluded-columns.json` 移除 `user_dict_type`；导出测试增加已删表断言 | `ExportDatasetRegistryTest` 3 项通过 |
| P1-5 | 回退 `V20261110_01` 就地修改；新增 `V20261112_06` 统一 `is_deleted` 为 `smallint`、收窄 `wardrobe_item.file_id` | 空库全链迁移成功；`information_schema` 确认无 `integer` 的 `is_deleted` |
| P1-6 | `V20261112_04` 增加待删表列存量预检；`V20261112_05` 增加 `pages_info` 非数组预检 | 空库执行成功；有数据时由 `DO` 块中止 |
| P2-10 | 新增 `V20261112_12`（后续并入基线），把菜单路径、配置键、字典类型/键值、导出幂等键、平台/人格/定时任务/地区编码改为 `COLLATE "C"`；展示文本使用数据库默认确定性排序 | 当时 `mvn -o -f tools/flyway/pom.xml verify` 通过：25 个迁移、4 项集成测试；实测大小写变体可共存，等值与 `LIKE` 查询按字节匹配。合并后当前链为 13 个文件 |

```bash
mvn -o test -Dtest=PostgresqlRegressionIntegrationTest,ExportDatasetRegistryTest,TimeTrackerCategoryServiceImplTest,TimeCategoryHierarchyTest,TimeTrackerCategoryCacheInvalidationTest,ScheduledJobTest,EventRecordFilesContractTest
```

结果：64 项测试通过，0 失败。仓库自带 Flyway 校验 `mvn -f tools/flyway/pom.xml -o verify` 通过：24 项单元测试 + 4 项集成测试，当时空库执行 20 个迁移，重复迁移、增量升级、事务回滚与结构契约均通过。合并后当前链为 13 个文件。未覆盖：业务库存量、数据量级 `EXPLAIN`、应用启动、Web / 移动端实际页面。

**目标库执行记录（2026-11-12）**：确认实际结构已与目标一致后，对目标库依次执行 `flyway:repair`、`flyway:migrate`、`flyway:validate`；V20261112.05–12 应用成功，当前版本为 `20261112.12`（09–12 于同日稍后应用）。迁移前已做逻辑备份。

**目标库历史对齐（2026-11-12）**：对同一目标库执行 `flyway:repair`，标记已删除的 `V20261111_01` 与 `V20261112_01`–`12`，并把当前 13 个文件的 checksum 对齐；随后 `flyway:migrate` 应用 `V20261112_13`，`flyway:validate` 与结构预检均通过，当前版本 `20261112.13`。升级前已另做完整逻辑备份；复核保留 27 个用户、6589 条时迹、72 条视频，`user_quick_nav` 逻辑删除残留 0，Typesafe 配置 0。复核结果：27 个用户、6581 条时迹、72 条视频记录保留；旧列名 0 个，新增的 16 个索引和更新后的 `ck_time_record_time_range` 均存在；审计字段已全部 `NOT NULL` 且有默认值，系统字典 `is_enabled` 为 `NOT NULL DEFAULT 1`，`user_dict_data` 保持 NULL 继承语义并通过 CHECK 约束。`20261110.01` 与 `20261112.04` 的历史校验和已按当前文件修复；其他执行过旧版基础迁移或旧版 04 的环境也需要同样的 repair 步骤。

### 后续字段优化（2026-11-12）

- `V20261112_08` 回填并收紧 `create_time` / `update_time`；系统字典 `is_enabled` 改为 `NOT NULL DEFAULT 1`；`user_dict_data` 保留 NULL=继承并增加 `CHECK (is_enabled IS NULL OR is_enabled IN (0,1))`。
- `TimeRecordEntity.isManual`、`TimeRecordListVO.isManual` 改为 `Integer`；`SysDictDataVO.id` 改为 `Long`，雪花 `dict_code` 不再被截断，接口按全局 Long 序列化为字符串。
- `UserDictDataServiceImpl` 把 NULL 显式视为“未停用/继承”，私有分类不再因 NULL 被过滤。
- 117 中 8 条 `file.biz_type='read_record'` 已在库内直接归一为 `read`；该修复未纳入 Flyway，重建库需单独执行 `UPDATE file SET biz_type='read' WHERE biz_type='read_record'`。

