# MCP 接口范围与需求

2026-10-29 按当前工具契约核对。业务后端 `/api/mcp` 提供读写工具；独立查询服务的 `/mcp` 仅提供只读查询，两者工具、协议响应与权限链路分别维护。连接和调试步骤见[后端接入说明](../../aio-life-server/docs/mcp/streamable-http.md)。

## 当前工具目录

源码当前注册 16 个工具，分布于 `top.aiolife.record.mcp` 的 8 个 `@McpToolProvider`。部署后的目录及字段以实际 `tools/list` 为准；本文数量仅表示本次源码盘点，未调用运行环境。

| 工具 | 能力 | 主要参数／限制 |
| --- | --- | --- |
| `time_record_queryByDateRange` | 读取日期范围时迹，含分类和精简运动明细 | `startDate`、`endDate`，日期字符串 |
| `time_record_save` | 新增一段时迹 | 可选 `categoryId/date/title/description/startTime/endTime`；显式起止须成对提供 |
| `thought_save` | 新增闪念及关联事件 | `content`、`events[].content` |
| `time_tracker_category_list` | 当前用户可见时迹分类 | 无参数 |
| `task_list` | 待办主任务及明细 | 可选 `page/pageSize`，返回 `items/total`，供逐页选择真实 ID |
| `task_detail_save` | 新增待办明细 | `taskId`、`content`、可选 `priority/isStarred` |
| `task_detail_update` | 修改现有待办明细 | 字符串 `id`；`priority/isStarred/isCompleted` 至少一项 |
| `dashboard_cards` | 当前用户仪表盘卡片 | 无参数 |
| `read_record_query` | 分页阅读记录 | `title/status/page/pageSize` |
| `movie_query` | 分页观影记录 | `title/status/page/pageSize` |
| `goal_query` | 分页目标、进度及子目标统计 | `type/status/keyword/year/month/page/pageSize` |
| `goal_progress_update` | 修改目标值或状态 | `goalId`，`currentValue/status` 至少一项 |
| `anniversary_query` | 纪念日／倒数日 | `type/withinDays` |
| `b_video_query` | 分页 B 站学习视频 | `title/status/page/pageSize` |
| `b_video_statistics` | B 站学习时长与状态统计 | 无参数 |
| `douban_wishlist_add` | 按豆瓣书籍／影视地址录入想读／想看 | 请求模型及重复条目行为以工具 Schema 为准 |

## 参数与结果边界

- 用户身份来自 Bearer 登录态／API Key，不接受工具参数指定所属用户。菜单二级锁仍适用；不能因 AI 发起调用而跳过业务权限。
- 日期使用 `yyyy-MM-dd`。时迹分钟为闭区间，时长为 `endTime - startTime + 1`。
- `time_record_save` 可显式指定闭区间分钟 `startTime/endTime`（0–1439，结束不早于开始）。省略两者时，只允许今天，从最后一条结束分钟加一追加到当前分钟；不存在可追加时段时拒绝，不裁剪成重复记录。非今天的记录必须提供起止时间。阅读／观影关联及运动明细使用现有 REST 接口。
- `task_detail_update` 只更新非 `null` 字段，数字 `0` 仍表示明确修改；须修改已有且属于当前用户的明细，不会隐式新增。
- 阅读、观影、目标和视频查询的状态筛选使用 `not_started/in_progress/completed/on_hold`。响应展示中文业务标签，各模块文案可不同。
- 目标类型为 `GoalTypeEnum` 的 1–10；目标进度更新的 `status` 使用 `in_progress/completed/on_hold`，与查询使用同一状态代码。
- 纪念日查询 `type` 当前使用“纪念日／倒数日”；纪念日距离按下一次发生日期计算，倒数日按实际目标日期计算。
- 优先级为 `1/10/20`（高／中／低），二值字段 `isStarred/isCompleted` 使用数字 0／1。不要把这些业务数量改成字符串 ID。

## 参数与结果契约

- ID 入参统一使用字符串，禁止经过 JavaScript Number 转换；必填、正整数 ID 格式、分页和数值范围会进入 inputSchema，工具执行时也进行 Bean Validation。
- 阅读、观影、目标和视频查询使用 `page/pageSize`，默认 1／10，最多 100；`task_list` 同样支持分页。旧 `size` 不再接受。
- `task_list` 返回 `items/total`；阅读、观影、目标和视频工具的分页结果仍为 `records/total`。应根据具体工具结果读取，不混用。
- `task_detail_update` 至少提供一个非 null 的更新字段，`goal_progress_update` 至少提供 `currentValue/status` 中的一项；这些跨字段规则见工具说明，服务端也会校验。可选字段不能自动填成枚举第一项。
- MCP `tools/call` 返回 `content` 与 `isError`，业务值在文本内容中，不套用 HTTP `{ code, message, data }`。工具接入与业务 REST 共用 Bearer 用户身份及二级锁。

## 尚未注册的扩展需求

- `time_record_recommend`：推荐时间段与分类。
- `time_record_update`、`time_record_delete`：编辑或删除时迹。
- `time_record_save` 的阅读／观影关联、运动明细增强（显式起止时间已经支持）。
- 独立里程碑工具：不能把里程碑当作目标的子任务。

这些名称不在当前目录中，不向客户端伪装成可调用工具。原方案列为“待新增”的目标、纪念日和 B 站工具现已实现，以上表为准。

## 维护与验证

新增工具在 `@McpToolProvider` 类中定义 `@Tool` 方法，复用 Service／业务规则；注册器当前支持零参或单 DTO 参数，参数说明使用 `@Description`。不要照搬早期 Controller 加 `@McpOperation` 的草案。

实际调用按“发现目录 → 读取 inputSchema → 只读核对目标 → 明确写入 → 检查 isError 与业务内容”进行；工具返回字符串不能只凭 HTTP 200 判定成功。测试覆盖用户隔离、二级锁、长 ID、零值、分页及写入失败恢复。源码目录和测试结果、真实客户端、生产部署分别报告。
