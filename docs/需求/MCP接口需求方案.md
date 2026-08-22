# MCP 接口需求方案

## 一、概述

AIO Life 通过 **MCP（Model Context Protocol）** 向 AI 客户端暴露内部业务能力，使大模型可读取、写入用户的人生数据（时迹、任务、想法、仪表盘等），当前能力集中覆盖 `record` 业务域。

### 连接信息

| 项目 | 说明 |
|---|---|
| 传输协议 | `streamable-http`（WebMvc Streamable Server Transport） |
| 端点 | `/api/mcp` |
| 认证 | 复用 Sa-Token：`Authorization: Bearer <token>`，从请求上下文提取 `loginId` |
| 能力声明 | `tools: true`（当前仅暴露 Tools，未声明 resources / prompts） |
| 服务信息 | `aio-life-server-mcp` / `1.0.0` |
| 实现 | `top.aiolife.mcp`（注解驱动注册）+ `top.aiolife.record.mcp`（业务 Tool） |

### 开发约定

- Tool 提供者类标注 `@McpToolProvider`，方法标注 `@Tool("中文功能描述")`
- 请求参数用带 `@Description` 注解的 DTO（Req），由 LangChain4j 生成参数 Schema 描述
- 所有 Tool 在当前登录用户上下文内执行，自动隔离用户数据
- 数据访问均复用现有 Controller / Service，保证权限与业务一致性

### 状态语义规范

**给 AI 的「多值」状态字段一律用中文语义标签，不暴露 0/1/2/3 等裸枚举数字**（大模型无法理解无上下文的数字，容易乱猜）。由后端负责「中文标签 ↔ 存储枚举」的转换：

| 业务字段 | 中文标签 | 说明 |
|---|---|---|
| 阅读状态 `status` | `未开始` / `进行中` / `已完成` / `搁置` | 对应存储 0/1/2/3 |
| 观影状态 `status` | `想看` / `在看` / `看过` / `搁置` | 对应存储 0/1/2/3 |
| 任务明细 `priority` | `高` / `中` / `低` | 对应存储 1/10/20，默认 `中` |
| 时迹 `relateType` | `阅读` / `观影` | 对应存储 1/2 |
| 分类 `timeType` | `必须` / `积极` / `休闲` | 对应存储 1/2/3 |

> 例外：二值 0/1 布尔字段（`isCompleted`、`isPinned`、`isStarred` 等）语义自明，无需转换，保持数字并带字段说明即可。
>
> 另外，查询工具的 `status` **筛选参数**（如 `read_record_query` / `movie_query`）直接传数字枚举（0/1/2/3），参数说明已自带映射；响应字段仍返回中文标签。

---

## 二、现有 Tool 接口

共 9 个，定义于 `RecordMcpTools`、`DashboardMcpTools`、`ReadRecordMcpTools` 与 `MovieMcpTools`。

### 2.1 time_record_queryByDateRange — 查询时间记录

**用途**：查询指定日期范围内的所有时间记录，含分类名称与运动明细（仅运动名称和次数）。

**请求参数**

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| startDate | string | 是 | 开始日期，`yyyy-MM-dd` |
| endDate | string | 是 | 结束日期，`yyyy-MM-dd` |

**响应**（`TimeRecordDateRangeVO[]`，按日期+开始时间倒序）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | long | 记录 ID |
| categoryId | long | 分类 ID |
| date | date | 日期 |
| startTime | int | 开始分钟（0–1439） |
| endTime | int | 结束分钟（0–1439） |
| title | string | 标题（空串转为 null） |
| categoryName | string | 分类名称 |
| exercises | [{ name: string, count: int }] | 运动明细（运动名称 + 次数） |

### 2.2 time_record_save — 保存时间记录

**用途**：新增一条时间记录。时间段由后端自动推导，AI 无需纠结具体时刻。

**请求参数**（`TimeRecordSaveMcpReq`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| categoryId | string | 是 | 分类 ID（应优先通过 `time_tracker_category_list` 获取） |
| date | string | 否 | 日期 `yyyy-MM-dd`，默认当天 |
| title | string | 否 | 标题 |
| description | string | 否 | 描述 |

**时间段推导规则**：
- 开始时间 = 当天最后一条记录的结束时间 + 1（当天无记录则为 00:00）
- 结束时间 = 当前时刻；若结束 < 开始则结束 = 开始
- 时间限制在 0–1439 分钟内

**响应**：文案字符串，如 `保存成功！开始时间：09:30，结束时间：10:00，持续时长：31分钟`

### 2.3 thought_save — 保存想法

**用途**：保存一条想法，可附带多个关联事件。

**请求参数**（`ThoughtSaveReq`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| content | string | 否 | 想法内容 |
| isPinned | int | 否 | 是否置顶（0/1） |
| events | [{ content: string }] | 否 | 关联事件列表 |

**响应**：`true`

### 2.4 time_tracker_category_list — 查询时迹分类

**用途**：获取当前用户的全部时迹分类（含合并的公共分类），用于拿到分类 ID 供保存记录时使用。

**请求参数**：无

**响应**（`TimeTrackerCategoryMcpVO[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | long | 分类 ID |
| name | string | 分类名称 |

### 2.5 task_list — 查询任务列表

**用途**：查询所有任务及明细，用于获取任务 ID 以便后续录入明细。

**请求参数**：无

**响应**（`TaskMcpVO[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | long | 任务 ID |
| content | string | 任务内容 |
| details | [{ id, content, isCompleted }] | 明细列表（isCompleted: 0未完成/1已完成） |

### 2.6 task_detail_save — 录入任务明细

**用途**：向某主任务下新增一条明细，并校验任务归属当前用户。

**请求参数**（`TaskDetailSaveMcpReq`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| taskId | long | 是 | 主任务 ID（须属于当前用户） |
| content | string | 是 | 明细内容 |
| priority | string | 否 | 优先级：高 / 中 / 低，默认 中 |
| isStarred | int | 否 | 是否关注：0-未关注，1-已关注，默认 0 |

**响应**：`true`

### 2.7 dashboard_cards — 读取仪表盘卡片

**用途**：读取当前用户仪表盘可见卡片，返回类型、标题、当前值、总量。

**请求参数**：无

**响应**（`DashboardCardMcpVO[]`）

| 字段 | 类型 | 说明 |
|---|---|---|
| type | string | 卡片类型标识 |
| title | string | 卡片标题 |
| value | string | 当前值 |
| totalTitle | string | 总量标题 |
| totalValue | string | 总量值 |

### 2.8 read_record_query — 查询阅读记录

**用途**：分页/按条件查询阅读记录，供 AI 主动感知读书进度。

**请求参数**（`ReadRecordQueryMcpReq`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | 否 | 书名模糊搜索 |
| status | int | 否 | 状态筛选：0未开始，1进行中，2已完成，3搁置 |
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页条数，默认 10，最大 100 |

**响应**（`ReadRecordPageMcpVO`，分页）

| 字段 | 类型 | 说明 |
|---|---|---|
| records | [] | 记录列表（字段见下） |
| total | long | 总条数 |

`records[]` 元素（`ReadRecordMcpVO`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | long | 阅读记录 ID |
| title | string | 书名 |
| author | string | 作者 |
| type | int | 类型 |
| status | string | 状态（中文）：未开始 / 进行中 / 已完成 / 搁置 |
| totalProgress | int | 总进度 |
| currentProgress | int | 当前进度 |
| startTime | datetime | 开始时间 |
| finishTime | datetime | 完成时间 |
| remark | string | 备注 |

### 2.9 movie_query — 查询观影记录

**用途**：分页/按条件查询观影记录，供 AI 主动感知观影进度。字段结构与阅读一致，`author` 换为 `director`（导演）。

**请求参数**（`MovieQueryMcpReq`）

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| title | string | 否 | 片名模糊搜索 |
| director | string | 否 | 导演搜索 |
| status | int | 否 | 状态筛选：0想看，1在看，2看过，3搁置 |
| page | int | 否 | 页码，默认 1 |
| size | int | 否 | 每页条数，默认 10，最大 100 |

**响应**（`MoviePageMcpVO`，分页）

| 字段 | 类型 | 说明 |
|---|---|---|
| records | [] | 记录列表（字段见下） |
| total | long | 总条数 |

`records[]` 元素（`MovieMcpVO`）：

| 字段 | 类型 | 说明 |
|---|---|---|
| id | long | 观影记录 ID |
| title | string | 片名 |
| director | string | 导演 |
| type | int | 类型 |
| status | string | 状态（中文）：想看 / 在看 / 看过 / 搁置 |
| totalProgress | int | 总进度 |
| currentProgress | int | 当前进度 |
| startTime | datetime | 开始时间 |
| finishTime | datetime | 完成时间 |
| remark | string | 备注 |

---

## 三、待新增 Tool 接口

以下接口基于现有业务规划，请求参数遵循现有 `@Description` DTO 约定。

### 3.1 时迹扩展（推荐）

#### time_record_save 参数增强（关联业务）

在现有 `TimeRecordSaveMcpReq` 基础上新增两个**可选**字段，使 AI 可以一次完成「记录时间 + 关联读书/观影」：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| relateType | string | 否 | 关联类型：阅读 / 观影 |
| relateId | long | 否 | 关联业务记录 ID |

> 保存时后端沿用现有「状态联动」逻辑：若关联业务为「未开始/想看」则自动置为「进行中/在看」。

#### time_record_recommend — 推荐时间块与分类

**用途**：AI 在不确定用户当前在干什么/应推荐什么分类时，由后端依据历史记录推荐；复用 `recommendNext` + `recommendType` 的能力。

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| date | string | 否 | 日期 `yyyy-MM-dd`，默认当天 |

**响应**

| 字段 | 类型 | 说明 |
|---|---|---|
| startTime | int | 推荐开始分钟 |
| endTime | int | 推荐结束分钟 |
| categoryId | long | 推荐分类 ID（可能为空） |

#### time_record_update / time_record_delete — 时间记录编辑与删除

**用途**：允许 AI 修正错误记录（改分类/改时间、删除单条/当天）。

| 名称 | 参数 | 说明 |
|---|---|---|
| time_record_update | id: long 必填；startTime/endTime/categoryId/title/description 可选 | 按需更新字段，校验重叠 |
| time_record_delete | id: long 必填 | 删除单条时间记录 |

## 四、实现建议

1. **新增工具组织**：按「阅读」「观影」业务域隔离为 `ReadRecordMcpTools` 与 `MovieMcpTools`，避免 `RecordMcpTools` 过度膨胀
2. **入参校验**：复用现有 Controller 的 `@Valid`/业务校验；`movie/read` 的 `save`/`update` 直接透传已有 `ReadRecordReq` / `MovieReq`
3. **响应收敛**：MCP Tool 返回尽量精简字段（顶层用 VO），避免把创建时间等系统字段暴露给模型
4. **注册即生效**：`McpToolRegistry` 自动扫描 `@McpToolProvider`，新增 Tool 无需改配置，发版即自动暴露