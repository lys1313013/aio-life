# 作品、外部资源与榜单设计

**实现日期**　2026-11-18。方案覆盖观影、阅读、共享封面及榜单，沿用现有远程图片缓存。[现行数据库结构](../../aio-life-server/docs/数据库表结构.md)

## 整体结构

**`creative_work` 保存作品详情和封面来源 URL，`external_resource` 沿用现有设计管理图片下载与缓存。** 影视和阅读入口先查本地作品，再用 `cover_url` 推导图片缓存键。详情已就绪时，重复解析始终走本地，封面缓存未命中时也能返回作品详情。

| 对象 | 保存位置 | 职责 |
| --- | --- | --- |
| 作品 | `creative_work` | 保存外部条目标识、本地详情和封面来源 URL |
| 图片来源 | `external_resource` | 管理图片标识、下载状态和本地对象 |
| 图片对象 | `storage_object` | 保存本地对象的位置、摘要和文件属性 |
| 榜单 | `ranking_list`、`ranking_list_item` | 保存榜单期次、入选关系和可选名次 |
| 个人记录 | `movie`、`read_record` | 保存用户自己的进度、日期、评分和备注，按外部平台和条目 ID 查找榜单和默认封面 |

```text
creative_work.cover_url → 本地解析图片缓存键 → external_resource
                                               └─ storage_object_id → storage_object

movie / read_record: url → 存储生成列 platform、external_key → creative_work
ranking_list ──← ranking_list_item ── creative_work_id ──→ creative_work
```

## 核心表结构

类型按 PostgreSQL 18+ 列出。`—` 表示无列默认值。业务主键由应用生成，关联由应用校验。时间字段沿用本地日期时间约定，更新时由应用维护审计时间。[SQL 脚本规范](../../aio-life-server/docs/SQL脚本规范.md#5-字段与约束设计)

### 1. `creative_work` 作品

每行是一部电影、一部剧集，或一个可独立识别的图书版本。每行最多保存一组外部条目标识。手工建立的作品可留空。

| 字段 | 类型 | 可空 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | 否 | — | 作品主键，由应用生成雪花 ID |
| `kind` | `varchar(16)` | 否 | — | 作品类型，首期为 `film`、`series`、`book` |
| `title` | `varchar(255)` | 否 | — | 作品显示名称，允许同名 |
| `director` | `varchar(100)` | 是 | — | 影视导演，优先保存来源提供的主要导演，供现有表单回填 |
| `cast_names` | `jsonb` | 是 | — | 影视演员姓名数组，按来源顺序保存，未取得时为空 |
| `author` | `varchar(100)` | 是 | — | 图书作者，供现有表单回填 |
| `duration_minutes` | `integer` | 是 | — | 电影总时长，单位为分钟 |
| `episode_count` | `integer` | 是 | — | 剧集总集数 |
| `page_count` | `integer` | 是 | — | 该图书版本的总页数 |
| `platform` | `varchar(32)` | 是 | — | 外部系统，例如 `douban` |
| `resource_type` | `varchar(32)` | 是 | — | 外部条目类型，例如 `movie_subject`、`book_subject` |
| `external_key` | `varchar(255)` | 是 | — | 外部作品条目 ID，按字符串保存 |
| `cover_url` | `varchar(1000)` | 是 | — | 校验后的原始封面 URL，用于服务端推导图片缓存键 |
| `metadata_ready_time` | `timestamp(0) without time zone` | 是 | — | 详情确认并保存的时间。仅有榜单基础资料时为空 |
| `create_user` | `bigint` | 是 | — | 创建操作者 ID，系统任务可留空 |
| `create_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 创建时间 |
| `update_user` | `bigint` | 是 | — | 最后更新操作者 ID，系统任务可留空 |
| `update_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 最后更新时间 |
| `is_deleted` | `smallint` | 否 | `0` | 逻辑删除标记，`0` 有效，`1` 已删除 |

| 类型 | 字段或表达式 | 用途 |
| --- | --- | --- |
| 主键 | `(id)` | 标识作品 |
| 唯一索引 | `(platform, resource_type, external_key) WHERE external_key IS NOT NULL` | 外部条目标识唯一，覆盖有效行和已删除行 |
| `CHECK` | `num_nonnulls(platform, resource_type, external_key) IN (0, 3)` | 三个外部标识字段同时填写或同时为空 |
| `CHECK` | `duration_minutes > 0`、`episode_count > 0`、`page_count > 0` | 三条独立约束，各字段为空时表示未知，有值时使用正整数 |
| `CHECK` | `jsonb_typeof(cast_names) = 'array'` | 提供演员资料时保存为 JSON 数组，元素由应用校验为非空姓名 |
| `CHECK` | `is_deleted IN (0, 1)` | 校验逻辑删除标记 |

`kind` 表达 AIO Life 的作品类型。豆瓣电影和剧集共用 `movie_subject`，本地分别保存为 `film` 和 `series`。图书按平台可识别的版本保存，同名作品或不同译本按来源身份分别确认。

### 2. `ranking_list` 榜单

每行代表一份榜单的一期。电影和读书 Top 250 各有一行，年度榜按期次分别保存。

| 字段 | 类型 | 可空 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | 否 | — | 榜单主键，由应用生成雪花 ID |
| `name` | `varchar(120)` | 否 | — | 前端直接显示的榜单名称，可以改名 |
| `publisher_code` | `varchar(32) COLLATE "C"` | 否 | — | 发布方编码，例如 `douban` |
| `list_key` | `varchar(64) COLLATE "C"` | 否 | — | 发布方下的稳定榜单标识，例如 `movie_top250`、`book_top250` |
| `edition_key` | `varchar(32) COLLATE "C"` | 否 | — | 榜单期次，滚动榜显式填 `current`，年度榜可填 `2026` |
| `source_url` | `varchar(1000)` | 是 | — | 对应期次的原始榜单页面 |
| `last_sync_time` | `timestamp(0) without time zone` | 是 | — | 最近一次完整同步成功的时间，尚未同步时为空 |
| `create_user` | `bigint` | 是 | — | 创建操作者 ID，系统任务可留空 |
| `create_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 创建时间 |
| `update_user` | `bigint` | 是 | — | 最后更新操作者 ID，系统任务可留空 |
| `update_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 最后更新时间 |
| `is_deleted` | `smallint` | 否 | `0` | 逻辑删除标记，`0` 有效，`1` 已删除 |

约束为 `PRIMARY KEY (id)`、`UNIQUE (publisher_code, list_key, edition_key)` 和 `CHECK (is_deleted IN (0, 1))`。同一榜单改名或恢复时沿用原 ID。同一榜单也可以混合收录影视和书籍，条目类型从作品读取。

### 3. `ranking_list_item` 榜单条目

每行代表一部作品在某一期榜单中的入选关系。

| 字段 | 类型 | 可空 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | 否 | — | 榜单条目主键，由应用生成雪花 ID |
| `ranking_list_id` | `bigint` | 否 | — | 关联 `ranking_list.id` |
| `creative_work_id` | `bigint` | 否 | — | 关联入榜作品 `creative_work.id` |
| `rank` | `integer` | 是 | — | 正整数名次，允许并列。空值表示只入选 |
| `sort_order` | `integer` | 否 | — | 从 `0` 开始的来源顺序，用于并列和无名次条目 |
| `create_user` | `bigint` | 是 | — | 创建操作者 ID，系统任务可留空 |
| `create_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 创建时间 |
| `update_user` | `bigint` | 是 | — | 最后更新操作者 ID，系统任务可留空 |
| `update_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 最后更新时间 |
| `is_deleted` | `smallint` | 否 | `0` | 逻辑删除标记，`0` 有效，`1` 已掉榜或已移出 |

约束和索引如下。

| 类型 | 字段或表达式 | 用途 |
| --- | --- | --- |
| 主键 | `(id)` | 标识榜单条目 |
| 唯一索引 | `(ranking_list_id, creative_work_id)` | 一部作品在同一期只保存一条关系，重新入榜时恢复原行 |
| `CHECK` | `rank IS NULL OR rank > 0` | 有名次时使用正整数 |
| `CHECK` | `sort_order >= 0` | 来源顺序从 `0` 开始 |
| `CHECK` | `is_deleted IN (0, 1)` | 校验逻辑删除标记 |
| 有效记录索引 | `(ranking_list_id, rank ASC NULLS LAST, sort_order, id)` | 榜单详情排序，先按名次，再按来源顺序和 ID |
| 有效记录索引 | `(creative_work_id, ranking_list_id)` | 由观影或阅读记录反查所有所属榜单 |

有效记录索引以 `is_deleted = 0` 为条件。唯一索引覆盖有效行和已删除行。

## 个人记录如何查作品

| 个人记录 | 链接示例 | 在 `creative_work` 中查找的外部标识 |
| --- | --- | --- |
| `movie.url` | `https://movie.douban.com/subject/1300267/` | `douban / movie_subject / 1300267` |
| `read_record.url` | `https://book.douban.com/subject/1007305/` | `douban / book_subject / 1007305` |

两张个人记录表各保存 `platform varchar(32)`（外部系统编码，例如 `douban`）和 `external_key varchar(255)`（外部条目 ID）。数据库从 `url` 计算并持久化两列。已有链接在迁移时自动补齐，清空链接或换成不支持的链接时两列都为空。两张表都为有效记录建立 `(user_id, platform, external_key)` 索引。

列表与详情直接按两列查共享作品。观影使用 `movie_subject`，阅读使用 `book_subject`，再由作品主键查询榜单明细。作品尚未登记时个人记录正常显示，之后入榜可直接查到排名。[外部标识迁移](../../aio-life-server/sql/migrations/V20261119_02__store_record_external_identity.sql)

## 统一的本地优先流程

1. **解析身份。** 从链接提取 `(platform, resource_type, external_key)`。影视和阅读入口共用本地查找和保存逻辑，按平台与条目类型选择详情解析器。
2. **本地命中。** 按三字段查 `creative_work`。`metadata_ready_time` 有值时返回本地详情，并用 `cover_url` 只读查询封面缓存。导演、集数、页数或封面为空时直接返回已有资料。
3. **首次补取。** 无本地详情时按外部条目标识合并并发获取，获取前复查本地。复用榜单登记的基础作品，或创建新作品。详情确认后，在同一事务保存已取得的字段、校验通过的 `cover_url` 和 `metadata_ready_time`。
4. **封面获取。** 首次补取详情拿到封面地址时，通过现有图片下载流程复用或下载封面。下载失败也保留详情和 `cover_url`。用户显式重试时直接使用已保存的 `cover_url`，作品详情继续读本地。

| 情况 | 外部请求 |
| --- | --- |
| 已保存详情和封面 | 0 次。返回本地资料和图片 |
| 已保存详情，封面缺失或失败 | 0 次。返回本地资料，封面可为空 |
| 只有榜单带来的基础资料 | 在首次主动解析时补取详情。首次已知封面可按图片来源获取 |
| 详情已保存，用户显式重试封面 | 使用已保存的 `cover_url` 查缓存或下载图片 |

作品资料回填时，电影用 `duration_minutes`、剧集用 `episode_count`、书籍用 `page_count` 生成现有表单的总进度。已保存的个人记录保留用户填过的值。

## 封面读取与归属

- `creative_work.cover_url` 保存校验后的原始封面 URL。服务端复用现有身份解析逻辑，从 URL 及作品类型推导 `(platform, resource_type, external_key, variant)`，按这组键查 `external_resource`。比如影视海报使用 `movie_poster`，书籍封面使用 `book_cover`。两张表通过这个查找过程解耦。[封面身份解析](../../aio-life-server/src/main/java/top/aiolife/record/service/ExternalResourceService.java) · [资源键查询](../../aio-life-server/src/main/java/top/aiolife/record/mapper/ExternalResourceMapper.java)
- 普通解析的本地命中路径只查缓存。图片来源为 `READY` 时通过 `storage_object_id` 读取对象，再由 AIO Life 的鉴权地址提供给前端。缓存未命中或本地对象不可用时封面留空。原始 URL 只供服务端解析和下载，前端携带登录凭据读取本地图片。
- `attachment` 保存个人记录上的自选封面。展示优先使用个人封面，其次用作品的共享封面。有效的 `external_resource` 本身会保护已保存的对象免于回收。[现行对象回收查询](../../aio-life-server/src/main/java/top/aiolife/system/mapper/StorageObjectMapper.java)

### 现有表 `external_resource` 图片来源

沿用现有字段和约束。每行对应一个远程图片及规格，下载就绪后关联本地对象。[建表迁移](../../aio-life-server/sql/migrations/V20261116_11__attachment_sources_and_jobs.sql)

| 字段 | 类型 | 可空 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| `id` | `bigint` | 否 | — | 来源主键，由应用生成雪花 ID |
| `platform` | `varchar(32)` | 否 | — | 平台编码，`douban`、`bilibili`、`jd`、`taobao` |
| `resource_type` | `varchar(32)` | 否 | — | 资源类型，例如 `movie_poster`、`book_cover`、`video_cover`、`product_image` |
| `external_key` | `varchar(255)` | 否 | — | 平台图片标识，例如豆瓣的 `p…` 或 `s…` |
| `variant` | `varchar(128)` | 否 | `''` | 图片规格，例如 `l`、`s_ratio_poster` |
| `source_url` | `varchar(1000)` | 否 | — | 原始下载地址，用于首次下载、失败重试和追溯 |
| `storage_object_id` | `bigint` | 是 | — | 本地图片对象 ID，下载成功后有值 |
| `state` | `varchar(16)` | 否 | `'PENDING'` | 下载状态，`PENDING`、`RUNNING`、`READY`、`FAILED` |
| `attempts` | `integer` | 否 | `0` | 本轮尝试次数，范围 `0` 到 `5` |
| `next_attempt_at` | `timestamp(0) without time zone` | 是 | — | 退避后的下次可尝试时间 |
| `lease_token` | `varchar(32)` | 是 | — | 下载执行者的租约令牌 |
| `lease_until` | `timestamp(0) without time zone` | 是 | — | 下载租约到期时间 |
| `error_code` | `varchar(64)` | 是 | — | 最近一次下载失败码 |
| `fetched_at` | `timestamp(0) without time zone` | 是 | — | 成功下载时间 |
| `create_user` | `bigint` | 是 | — | 创建操作者 ID，仅用于审计 |
| `create_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 创建时间 |
| `update_user` | `bigint` | 是 | — | 最后更新操作者 ID，仅用于审计 |
| `update_time` | `timestamp(0) without time zone` | 否 | `CURRENT_TIMESTAMP` | 最后更新时间 |
| `is_deleted` | `smallint` | 否 | `0` | 当前约束要求恒为 `0` |

| 类型 | 名称或定义 | 用途 |
| --- | --- | --- |
| 主键 | `(id)` | 标识图片来源 |
| 唯一索引 | `uk_external_resource_identity (platform, resource_type, external_key, variant)` | 查找同一图片及规格 |
| 索引 | `idx_external_resource_object (storage_object_id)` | 对象回收时反查来源引用 |
| 索引 | `idx_external_resource_due (state, next_attempt_at, lease_until)` | 查找可下载或租约到期的来源 |
| `CHECK` | `ck_external_resource_platform` | 校验平台编码 |
| `CHECK` | `ck_external_resource_state` | 状态限定为四个定义值 |
| `CHECK` | `ck_external_resource_object` | `READY` 时 `storage_object_id` 必填，其他状态为空 |
| `CHECK` | `ck_external_resource_lease` | `RUNNING` 时两列租约必填，其他状态两列均为空 |
| `CHECK` | `ck_external_resource_attempts` | `attempts BETWEEN 0 AND 5` |
| `CHECK` | `ck_external_resource_active` | `is_deleted = 0` |

## 更新和展示

- 同一榜单串行刷新。确认整份数据拉取完整且条目标识已解析，再在一个事务内更新或恢复入榜条目、将本次缺席的条目标记为掉榜，并更新 `last_sync_time`。拉取不完整时保留上一次完整结果。
- 观影、阅读列表按当前用户查询。选定榜单时，分页前用 `EXISTS` 筛选有效入榜关系。当前页去重已保存的外部标识，批量查本地作品，再按作品主键批量取榜单名称和名次，因此一部作品可以显示多个榜单标签。
- 标签有名次时显示 `No.34 豆瓣电影 Top 250`。`rank` 为空时只显示榜单名称，例如「年度推荐书单」。接口中的内部 ID 序列化为字符串，名次序列化为数字或 `null`。[API 参数规范](../API参数规范.md)

## 两份 Top 250 的维护

电影和读书各保留一份 `current` 榜。初始快照含 500 条公开条目，图书按豆瓣版本 ID 匹配。榜单只提供标题、来源身份、封面来源和名次，作品的 `metadata_ready_time` 在主动解析详情后填写。Web 和移动端把金色标签放在海报下方，按榜单筛选时使用内部榜单 ID。

维护人员运行生成器读取两份官方榜单，校验每页 25 条、页码、条目身份唯一及名次连续，生成一个新的数据迁移文件。已有目标文件会被拒绝覆盖。Flyway 在一个事务中合并两份榜单，恢复重新入榜的关系，移除已掉榜的关系，并保留用户保存的作品和个人记录。[数据快照](../../aio-life-server/sql/migrations/V20261118_14__douban_top250.sql) · [刷新命令](../../aio-life-server/sql/README.md#豆瓣榜单)

历史记录和新增记录使用同一套链接匹配规则，榜单刷新只更新作品和榜单。用户自行修改的片名、书名、作者和进度始终属于个人记录。首次主动解析由服务端填充作品详情。对已就绪作品，重复解析、列表、编辑和普通保存均使用本地数据。已有个人附件优先显示。共享封面缺失时，可在表单点「重试封面」单独下载。
