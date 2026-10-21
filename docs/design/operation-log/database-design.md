# 操作日志数据库结构设计

日期：2026-10-21。状态：结构已实现，配套[操作日志需求方案](../../需求/操作日志需求方案.md)。

复用现有 `sys_activity_log`，为操作日志增加 HTTP 请求元数据和脱敏参数。保留现有 `ACCESS` 访问日志及历史数据，不另建 `oper_log` 或重复存储操作日志。

本目录 SQL 为结构摘录，不直接执行。部署使用[后端增量脚本](../../../aio-life-server/sql/1_init_table/2026-10-21_operation_log_request.sql)及升级计划；完整结构以[后端数据库表结构](../../../aio-life-server/docs/数据库表结构.md)和后端 SQL 为准。

## 一 字段设计

表使用 MySQL 8.x、InnoDB、`utf8mb4_unicode_ci`。继承 `BaseEntity` 的主键、审计字段和逻辑删除约定。除新增的 5 个字段及 1 个索引外，既有字段定义、默认值和索引保持不变。

| 字段 | 类型 | 可空 | 默认值 | 来源与用途 |
| --- | --- | --- | --- | --- |
| `id` | BIGINT | 否 | 无 | 既有；雪花 ID，历史导入保留原 ID；接口输出 string |
| `log_type` | VARCHAR(16) | 否 | 无 | 既有；`OPERATION` / `ACCESS` |
| `user_id` | BIGINT | 是 | NULL | 既有；服务端鉴权用户；ACCESS 失败登录允许为空 |
| `username` | VARCHAR(100) | 否 | `''` | 既有；操作时用户名快照 |
| `nickname` | VARCHAR(100) | 否 | `''` | 既有；操作时昵称快照，详情保留 |
| `ip_address` | VARCHAR(64) | 否 | `''` | 既有；可信解析后的请求 IP，兼容 IPv4 / IPv6 |
| `browser` | VARCHAR(100) | 否 | `''` | 既有；浏览器名称，详情保留 |
| `function_name` | VARCHAR(200) | 是 | NULL | 既有；菜单或接口功能名称快照 |
| `function_item` | VARCHAR(100) | 是 | NULL | 既有；查询、新增、修改、删除等操作类型 |
| `access_type` | VARCHAR(32) | 是 | NULL | 既有；ACCESS 的登录或登出类型 |
| `request_path` | VARCHAR(255) | 是 | NULL | 既有；去掉 `/api` context-path 的路由模板，如 `/todo/{id}` |
| `request_method` | VARCHAR(16) | 是 | NULL | **新增**；HTTP 方法大写 |
| `request_params` | JSON | 是 | NULL | **新增**；脱敏后参数对象，逻辑大小上限 32 KiB |
| `request_time` | DATETIME(3) | 是 | NULL | **新增**；服务端收到请求的时间，毫秒精度，`Asia/Shanghai` |
| `duration_ms` | INT | 是 | NULL | **新增**；单调时钟计算的处理耗时，范围 0–2147483647 ms，Java Integer，接口 number |
| `server_ip` | VARCHAR(64) | 是 | NULL | **新增**；处理请求的实例 IP，支持 IPv4 / IPv6 |
| `success` | TINYINT(1) | 否 | 1 | 既有；业务成功标记 |
| `create_user` | BIGINT | 是 | NULL | 既有；审计创建人 |
| `create_time` | DATETIME | 否 | CURRENT_TIMESTAMP | 既有；审计时间，历史日期与排序回退，不代表精确落库完成时间 |
| `update_user` | BIGINT | 是 | NULL | 既有；审计更新人 |
| `update_time` | DATETIME | 否 | CURRENT_TIMESTAMP | 既有；审计时间，不提供日志编辑入口 |
| `is_deleted` | TINYINT | 否 | 0 | 既有；逻辑删除标记，0 有效、1 已删除 |

新增字段均可空，兼容历史记录、旧版实例写入和访问日志。新版 `OPERATION` 正常应写入方法、路径、请求时间与耗时；参数按采集规则保存，服务器地址不可用时允许为空。耗时计算若异常或超过 INT 范围，保存 NULL 并告警，不截断、不溢出；正常的 0 ms 原样保存。

不为 `user_id`、功能或菜单增加外键、级联删除或唯一约束：一名用户可有任意多条日志，关联对象删除后仍保留操作快照。业务数据访问继续使用 MyBatis-Plus / Mapper，参数化 SQL；不使用 JDBC 或在 Service 中内嵌 SQL。

## 二 参数数据形态

| `request_params` | 含义 |
| --- | --- |
| 有内容的 JSON 对象 | 已执行白名单与脱敏的参数快照 |
| `{}` | 确认请求本身没有参数 |
| NULL | 历史未采集、规则跳过、超限或采集失败，页面统一展示「未采集」 |

参数按 `path`、`query`、`body` 分组，跳过未获准采集的字段与分组，不增加采集状态或省略标记。请求存在参数但均未获准采集时保存 NULL，不能用 `{}` 表示。任一大小、字符串长度、深度或节点限制超出时，整条参数快照保存 NULL，不存截断片段；其他日志字段正常保存。

示例为安全字段白名单生效后的快照：

```json
{
  "path": { "id": "9223372036854775806" },
  "query": { "page": ["1"], "pageSize": ["20"] },
  "body": { "status": "DONE" }
}
```

JSON 便于保留对象、数组和重复参数；本期不对参数正文建立索引，也不提供参数全文搜索。MySQL JSON 类型负责结构合法性，32 KiB 上限、遍历限制和脱敏由采集器写入前校验。缺失值使用 SQL NULL，不写字符串 `"null"` 或 JSON null 替代。

请求地址统一复用 `request_path` 展示接口路由模板，具体路径变量只在白名单脱敏后的参数快照中保存，不将实际变量值或查询串拼入路由模板。参数不得通过请求地址、错误日志或导出重新泄露。

## 三 索引与查询

| 索引 | 字段顺序 | 用途 |
| --- | --- | --- |
| `PRIMARY` | `id` | 详情及导出游标 |
| `idx_activity_type_time` | `log_type, is_deleted, create_time, id` | 保留；ACCESS 与历史日志日期查询 |
| `idx_activity_type_id` | `log_type, is_deleted, id` | 保留；固定最大 ID 的分批导出 |
| `idx_activity_type_req_time` | `log_type, is_deleted, request_time, id` | 新增；新版请求时间范围查询及排序 |

有效时间定义为 `COALESCE(request_time, create_time)`，用于混合数据展示排序。日期筛选必须处理两种分支：

- 新记录：`request_time IS NOT NULL`，在 `request_time` 上应用起止边界。
- 历史及旧实例记录：`request_time IS NULL`，在 `create_time` 上应用相同边界。

Mapper 可用互斥分支的 `UNION ALL` 或等价条件组合，两分支都必须约束 `log_type = 'OPERATION'`、`is_deleted = 0` 和相同筛选，不能漏掉权限、筛选或分页总数。合并后按有效时间和 ID 倒序，先统一排序与分页；不能把两个独立分页结果直接拼接。

`COALESCE` 混合排序及模糊匹配不保证走单一有序索引；实施前使用实际数据量执行 EXPLAIN 和性能验证。默认日期范围控制常见查询成本，全时间查询保留现有能力，本期保留日期和账号筛选，不增加其他筛选索引。

列表投影明确排除 `request_params`，避免分页读取 JSON 大字段。详情 Mapper 单条读取参数，条件同时包含日志类型、有效标记和 ID。导出按 ID 游标批量读取，沿用固定最大 ID 的上界；导出顺序可以与列表时间排序不同，应在接口说明中明确。

## 四 SQL 与部署迁移

- [create-table.sql](create-table.sql)：目标完整表结构，仅用于全新空表的设计核对，不是额外业务表。
- [upgrade.sql](upgrade.sql)：对现有 `sys_activity_log` 新增字段与索引；不改写或删除历史数据。

两份 SQL 是替代路径，不可在同一张已按目标结构创建的表上再次执行增量。草案不包含 DROP、TRUNCATE、登录日志回填、凭据或远程连接信息。MySQL DDL 不依赖业务事务回滚，执行前需确认实际结构、数据量和迁移窗口。

部署与维护顺序：

1. 后端 `sql/1_init_table/2026-10-21_operation_log_request.sql` 已纳入升级计划；新库只使用已合并的全量结构，不重复执行增量。
2. `sql/upgrade-plan.json`、脚本校验和及后端表结构文档已同步；部署按后端现有数据库升级验证流程执行结构预检。
3. 核对字段与索引是否已存在；增量只执行一次。中断或结果不明时先检查数据库，不盲目重放 ALTER。
4. 先执行结构迁移，再部署扩展 Entity、Mapper、采集器及接口；旧版本实例在混合部署期间继续写入原字段，新增字段为 NULL。
5. 前端按后端实际 JSON 契约更新，历史与过渡期记录按未采集展示。ACCESS 页面保持现有字段和查询行为；新增时间语义仅应用于 OPERATION。

禁止用现有 `create_time` 批量填入 `request_time` 来冒充真实接收时间，也不从当前实例推算历史服务器 IP。无需回填参数和耗时。

回退应用时保留新增可空列和索引，使旧版仍可运行，避免删除新版已采集日志。日志暂不清理；按 32 KiB 参数上限评估存储，容量随实际请求量增长，索引和备份空间另计。

## 五 实施验证要求

本地验证涵盖新库与存量库结构一致性、真实 MySQL Mapper 查询、历史数据回退、日志详情、导出及独立事务；`ActivityLogEntity` 与 Mapper 已同步。部署仍需检查实际已执行迁移记录，验证混合版本写入及回退兼容性。

参数安全、权限、耗时及 UI 验收按[需求验收标准](../../需求/操作日志需求方案.md#八-验收标准)执行；SQL 未执行前不能标记迁移或联调完成。
