# MCP 接口范围与需求

2026-10-23 按工具提供者源码核对。业务后端 `/api/mcp` 提供读写工具；独立查询服务的 `/mcp` 仅提供只读查询，两者工具、协议响应与权限链路分别维护。连接和调试步骤见[后端接入说明](../../aio-life-server/docs/mcp/streamable-http.md)。

## 当前工具目录

源码当前注册 16 个工具，分布于 `top.aiolife.record.mcp` 的 8 个 `@McpToolProvider`。部署后的目录及字段以实际 `tools/list` 为准；本文数量仅表示本次源码盘点，未调用运行环境。

| 工具 | 能力 | 主要参数／限制 |
| --- | --- | --- |
| `time_record_queryByDateRange` | 读取日期范围时迹，含分类和精简运动明细 | `startDate`、`endDate`，日期字符串 |
| `time_record_save` | 新增一段时迹 | `categoryId`、可选 `date/title/description`；起止分钟由后端计算 |
| `thought_save` | 新增闪念及关联事件 | `content`、`events[].content` |
| `time_tracker_category_list` | 当前用户可见时迹分类 | 无参数 |
| `task_list` | 待办主任务及明细 | 无参数，供后续选择真实 ID |
| `task_detail_save` | 新增待办明细 | `taskId`、`content`、可选 `priority/isStarred` |
| `task_detail_update` | 修改现有待办明细 | 字符串 `id`；`priority/isStarred/isCompleted` 至少一项 |
| `dashboard_cards` | 当前用户仪表盘卡片 | 无参数 |
| `read_record_query` | 分页阅读记录 | `title/status/page/size` |
| `movie_query` | 分页观影记录 | `title/status/page/size` |
| `goal_query` | 分页目标、进度及子目标统计 | `type/status/keyword/year/month/page/size` |
| `goal_progress_update` | 修改目标值或状态 | `goalId`，`currentValue/status` 至少一项 |
| `anniversary_query` | 纪念日／倒数日 | `type/withinDays` |
| `b_video_query` | 分页 B 站学习视频 | `title/status/page/size` |
| `b_video_statistics` | B 站学习时长与状态统计 | 无参数 |
| `douban_wishlist_add` | 按豆瓣书籍／影视地址录入想读／想看 | 请求模型及重复条目行为以工具 Schema 为准 |

## 参数与结果边界

- 用户身份来自 Bearer 登录态／API Key，不接受工具参数指定所属用户。菜单二级锁仍适用；不能因 AI 发起调用而跳过业务权限。
- 日期使用 `yyyy-MM-dd`。时迹分钟为闭区间，时长为 `endTime - startTime + 1`。
- `time_record_save` 从所选日期最后一条记录的结束分钟加一开始，结束分钟取服务端当前时间，并裁到当天范围；不接受任意 `startTime/endTime`、阅读／观影关联或运动明细。日期省略时为服务端今天。需要显式时间和附属记录时使用现有 REST 接口。
- `task_detail_update` 只更新非 `null` 字段，数字 `0` 仍表示明确修改；须修改已有且属于当前用户的明细，不会隐式新增。
- 阅读、观影、目标和视频查询的状态筛选使用 `not_started/in_progress/completed/on_hold`。响应展示中文业务标签，各模块文案可不同。
- 目标类型为 `GoalTypeEnum` 的 1–10；目标进度更新的 `status` 当前使用中文“进行中／已完成／搁置”，不能照搬查询的英文筛选值。
- 纪念日查询 `type` 当前使用“纪念日／倒数日”；纪念日距离按下一次发生日期计算，倒数日按实际目标日期计算。
- 优先级为 `1/10/20`（高／中／低），二值字段 `isStarred/isCompleted` 使用数字 0／1。不要把这些业务数量改成字符串 ID。

## 与 REST 规范的现存差异

这些是当前实现事实，不能只改文档就声称接口已统一：

| 项目 | 当前 MCP 行为 |
| --- | --- |
| 分页 | 阅读、观影、目标、视频工具仍使用 `page/size`，默认 1／10，最多 100；不是 REST 新请求的 `page/pageSize` |
| 分页返回 | 各工具 VO 保留 `records/total`，不按 REST 的 `items/total` 解析 |
| ID 入参 | `categoryId`、待办更新 `id` 为字符串；部分历史 DTO 的 `Long` 入参（如 `taskId/goalId`）仍生成 integer Schema，存在客户端大整数精度边界 |
| 结果包装 | MCP `tools/call` 返回 `content` 与 `isError`；业务值在文本内容中，不统一套用 HTTP `{ code, message, data }` |

客户端不得把大整数 ID 经 JavaScript `Number` 转换后再提交；无法无损满足旧 integer Schema 的工具，暂用支持字符串 ID 的对应 REST 入口。后续契约调整须同时修改 DTO、Schema 与调用方，并单独验证，不能只替换本文类型或分页名。

## 尚未注册的扩展需求

- `time_record_recommend`：推荐时间段与分类。
- `time_record_update`、`time_record_delete`：编辑或删除时迹。
- `time_record_save` 的阅读／观影关联、运动明细增强。
- 独立里程碑工具：不能把里程碑当作目标的子任务。

这些名称不在当前目录中，不向客户端伪装成可调用工具。原方案列为“待新增”的目标、纪念日和 B 站工具现已实现，以上表为准。

## 维护与验证

新增工具在 `@McpToolProvider` 类中定义 `@Tool` 方法，复用 Service／业务规则；注册器当前支持零参或单 DTO 参数，参数说明使用 `@Description`。不要照搬早期 Controller 加 `@McpOperation` 的草案。

实际调用按“发现目录 → 读取 inputSchema → 只读核对目标 → 明确写入 → 检查 isError 与业务内容”进行；工具返回字符串不能只凭 HTTP 200 判定成功。测试覆盖用户隔离、二级锁、长 ID、零值、分页及写入失败恢复。源码目录和测试结果、真实客户端、生产部署分别报告。
