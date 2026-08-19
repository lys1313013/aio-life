# GraphQL 引入方案（aio-life）

> 本文件用于在 aio-life 项目中评估并落地 GraphQL，重点回答：要不要做、怎么和现有栈（Spring Boot 3 + MyBatis-Plus + Sa-Token + vben-admin）适配、如何渐进式迁移。

---

## 1. 背景与目标

### 1.1 真实动机：自定义看板卡片
希望用户（或管理员）可以在前端自由拼装看板：选择"看什么指标 / 看哪类实体 / 按什么维度切片 / 用什么图表展现"，每张卡片自带数据查询逻辑。新增卡片类型时，理想情况下不需要后端为每张卡片新增接口。

引入 GraphQL 的最初想法是：把卡片配置变成一段 GraphQL 查询，前端按需取数。

### 1.2 但 GraphQL **不是**看板场景的最优解（重要）
看板卡片的难点不是字段选择，而是**聚合表达力**——COUNT、SUM、AVG、GROUP BY、时间分桶、Top N。这些 GraphQL **不会让它变简单**：

- GraphQL 的核心能力是"按需选择实体字段、嵌套关联"。看板需要的是"对一批行做聚合"
- 无论用不用 GraphQL，你都得在后端写聚合 resolver（`recordCountByDay`、`wardrobeStatsByCategory` 等），GraphQL 只是把它们包了一层 schema
- 真正能让用户"配出新卡片不改后端"的是**通用聚合 DSL**（类似 PromQL / Cube.js），而不是 GraphQL

### 1.3 看板卡片场景的真实拆解

| 子诉求 | 谁定义 | 最适合的方案 |
|--------|--------|--------------|
| 内置卡片库（用户从清单里选并配参数） | 后端开发 | **REST 指标目录**——每张卡片对应一个 `/dashboard/metric/{name}` 端点 |
| 实体明细式卡片（最近 5 条记录、Top 10 衣物） | 用户选实体 + 字段 + 过滤 | **GraphQL** 能发挥价值（self-describing schema 让卡片配置 UI 可基于内省渲染） |
| 自由聚合（自选维度 + 度量 + 时间窗） | 用户/管理员 | **聚合 DSL / 轻量 OLAP**（DuckDB / Cube.js / 自研），GraphQL 帮不上忙 |
| 跨模块聚合卡片（衣柜 + 记录 + 关系） | 后端开发 | GraphQL 的聚合 query 或 BFF 都行，差别不大 |

### 1.4 推荐路径：**REST 指标目录优先，GraphQL 作为补充**

阶段性选择：

- **第一阶段（P0–P1）**：先用 REST 实现"指标目录 + 卡片配置存储"模式
  - 后端维护一份指标清单（`metric_catalog` 表 + `@MetricHandler` 注解扫描）
  - 每个指标固定输入/输出，前端卡片配置只存 `{metricName, params, viewType}`
  - **不需要 GraphQL，2 周可上线**，覆盖 80% 看板需求
- **第二阶段（P2，可选）**：当出现"用户想看实体明细+自选字段"的卡片类型时，再引入 GraphQL
  - 此时 GraphQL 只服务于"实体型卡片"这一个子集，schema 范围可控
  - 走的就是本文档第 5–9 节的方案

### 1.5 目标
- 第一阶段：落地 REST 指标目录（不在本文档详述，需另写设计文档）
- 第二阶段（本文档主要内容）：当指标目录无法满足实体明细型卡片时，作为补充引入 GraphQL
  - 在保留全部现有 REST 接口的前提下，引入 `/graphql` 端点
  - 复用 Sa-Token 认证 / 权限体系，不引入 Spring Security
  - 解决 MyBatis-Plus 下 GraphQL 的 N+1 与 resolver 编写规范
  - 提供查询安全护栏（深度 / 复杂度 / 字段黑名单 / introspection 开关，看板场景**必须 persisted query**）
  - 前端（vben-admin / web-antd）客户端选型与 codegen 方案
  - 可回滚的试点路径

---

## 2. 项目现状

| 维度 | 现状 |
|------|------|
| 后端框架 | Spring Boot 3.3.10 / Java 21 |
| ORM | **MyBatis-Plus 3.5.11**（非 Spring Data JPA） |
| 认证 | Sa-Token 1.40.0（`SaTokenConfig` 已配置 `SaTokenContextForThreadLocal` 作为 second context） |
| 鉴权粒度 | 拦截器级别（`ApiKeyInterceptor` + `SaInterceptor` + `UserLastActiveInterceptor`） |
| 数据库 | MySQL（Druid 连接池） + Redis + Neo4j |
| 缓存 | Spring Cache（Caffeine 本地 + Redis 分布式） |
| 监控 | Actuator + Prometheus + Micrometer Tracing（Brave） |
| 对象存储 | MinIO |
| AI / 流式 | LangChain4j + MCP（部分场景需 SSE / 流式输出） |
| 响应封装 | `top.aiolife.core.resq.ApiResponse<T>` |
| 包结构 | `top.aiolife.{module}.{api,service,mapper,pojo,...}` |
| 前端 | vben-admin monorepo（`apps/web-antd`，Vue 3 + Ant Design Vue + axios） |

---

## 3. 看板卡片实现方案对比

针对 §1.1 的"自定义看板卡片"动机，三种实现路径横向对比：

| 维度 | A. REST 指标目录 | B. GraphQL with aggregation | C. 聚合 DSL / OLAP |
|------|------------------|----------------------------|---------------------|
| **配置存储** | `{metricName, params, viewType}` | 整段 GraphQL query 字符串 | DSL 表达式（如 `count(record) where ts > now()-7d group by day`） |
| **新增卡片类型** | 后端加一个 `@MetricHandler` | 后端加 resolver / 前端写新 query | 通常无需改后端 |
| **聚合表达力** | 由每个 handler 自由定义（最强） | 中等（需自己设计 aggregation schema） | 强（DSL 内置） |
| **实体明细型卡片** | 弱（每种都得写端点） | **强**（GraphQL 强项） | 弱 |
| **安全攻防面** | 小（接口固定） | 中（必须 persisted query） | 大（DSL 注入、跨用户数据） |
| **性能可控性** | 强（每个查询独立优化） | 中（依赖 DataLoader / 复杂度限制） | 弱（用户表达式可能拖垮库） |
| **工期** | 1–2 周可上线 | 4–6 周（含护栏 + 前端 codegen） | 8 周+（DSL 设计 + 引擎） |
| **可回滚** | 强 | 中 | 弱（DSL 用户数据沉淀后难退） |

### 3.1 推荐：先 A，必要时叠加 B

**第一阶段（推荐先做）**：纯 REST 指标目录，可独立覆盖 80% 看板需求。

简要架构（详细设计另立文档）：

```
metric_catalog (DB)               dashboard_card (DB)
├─ name: "record.count.byDay"     ├─ user_id
├─ category: "record"             ├─ layout: {x, y, w, h}
├─ paramSchema: JSON              ├─ metric_name → metric_catalog.name
├─ resultSchema: JSON             ├─ params: JSON
└─ requiredPerm: "record:read"    └─ view_type: "line" | "pie" | ...

后端：
  @MetricHandler(name = "record.count.byDay")
  public MetricResult handle(MetricContext ctx) { ... }

前端：
  GET  /dashboard/metrics                    # 指标清单（含 paramSchema 让 UI 自动渲染表单）
  GET  /dashboard/cards                      # 当前用户的卡片
  POST /dashboard/cards                      # 保存卡片
  POST /dashboard/metric/{name}/execute      # 执行（参数在 body）
```

新增卡片类型 = 后端加一个 `@MetricHandler`。指标的 `paramSchema` 是 JSON Schema，前端基于它自动渲染配置表单，无需为每个指标写专属 UI。

**第二阶段（可选）**：当出现「用户想看某实体的明细列表 / 自选字段」类卡片时（例如"显示我最近添加的 5 件衣物的名称、品牌、分类"），再为这一子集引入 GraphQL。此时 schema 范围小、可控，§5–§9 的方案完全适用。

### 3.2 如果走 GraphQL，看板场景的特殊约束

| 约束 | 原因 |
|------|------|
| **必须 persisted query**（仅允许 hash 白名单查询） | 卡片查询是用户配置出来的，不能让前端送任意字符串 |
| **必须 introspection 在生产关闭** | 否则攻击者可枚举 schema 找越权字段 |
| **必须按 userId 隔离结果缓存** | 否则用户 A 的卡片可能命中用户 B 的缓存 |
| **每张卡片查询超时 < 3 秒** | 看板加载是一组并发请求，单点慢拖累整体 |
| **复杂度上限调低**（推荐 100） | 比通用 GraphQL 接口更严 |

---

## 4. 引入 GraphQL 的收益与代价（仅针对第二阶段）

| 维度 | 收益 | 代价 |
|------|------|------|
| 客户端取数 | 按需字段、单次请求拿到聚合数据 | 后端需写 resolver 拆分逻辑，N+1 风险大 |
| 类型系统 | Schema 即契约，前端 codegen 自动生成 TS 类型 | 多一层 schema 维护成本 |
| 缓存 | 可在 field/resolver 粒度缓存 | HTTP 层缓存失效（统一 POST `/graphql`） |
| CDN / 网关 | 几乎无法做 URL 维度缓存与限流 | 需在 operationName / persisted query 维度重做 |
| 监控 | 可按 operation / field 埋点 | Druid SQL 监控、Brave 链路要按 resolver 重新接入 |
| 安全 | Schema 显式定义可见字段 | 任意查询带来深度炸弹、复杂度炸弹、字段越权风险 |
| 上传 / 流式 | 有 graphql-multipart-request-spec | 不如 REST 自然，建议保留 REST |

**结论**：仅在第一阶段 REST 指标目录无法满足实体明细型卡片需求时，作为补充引入。CRUD 后台、文件上传、AI 流式输出仍应留在 REST。

---

## 5. 技术选型

### 5.1 服务端框架

| 方案 | 风格 | 与现有栈契合度 | 推荐 |
|------|------|----------------|------|
| **`spring-boot-starter-graphql`** | Schema-First（`.graphqls` + `@SchemaMapping`） | 官方 starter，与 Spring Boot 3.x 深度集成 | **推荐** |
| DGS（Netflix） | Code-First | 与 spring-graphql 已大量重合，社区重心在迁移 | 不推荐 |
| graphql-java-tools | Schema-First（老） | 不再积极维护 | 不推荐 |

> 注：`spring-graphql` 默认是 **Schema-First**——SDL 写在 `src/main/resources/graphql/*.graphqls`，Java 侧用 `@QueryMapping` / `@MutationMapping` / `@SchemaMapping` 绑定。这与原方案表述相反，原方案需修正。

依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-graphql</artifactId>
</dependency>
<!-- 可选：开发期 GraphiQL -->
<!-- application.yml: spring.graphql.graphiql.enabled=true -->
```

### 5.2 前端客户端

| 候选 | 体积 | 缓存 | Codegen 配套 | 与 vben-admin 契合 |
|------|------|------|---------------|--------------------|
| **graphql-request + @tanstack/vue-query** | 小 | 由 vue-query 接管 | graphql-codegen + typed-document-node | **推荐**：最贴近现有 axios 风格，可逐步替换 |
| villus | 中 | 内置 | 良好 | 可选 |
| Apollo Client | 大 | 强大但复杂 | 良好 | 不推荐：缓存模型与 vben-admin 现有 store 冲突 |
| urql | 中 | 内置 | 良好 | 可选 |

**推荐方案**：`graphql-request` 作为最薄的传输层 + `graphql-codegen` 生成 TS 类型与 typed document，与现有 axios 请求并存。后续若需要 normalized cache 再升级到 urql / Apollo。

### 5.3 Codegen

`@graphql-codegen/cli` + 以下插件：
- `typescript`
- `typescript-operations`
- `typed-document-node`（或 `typescript-graphql-request`）

输出位置约定：`apps/web-antd/src/api/graphql/__generated__/`。

---

## 6. 与 MyBatis-Plus 的适配规范（核心）

MyBatis-Plus 是 SQL-first，**没有 JPA 的 lazy association**。这是 GraphQL 在本项目落地最关键的一节，原方案完全没有覆盖。

### 6.1 默认假设
- 每个 `@SchemaMapping(typeName, field)` 都是一次独立 SQL
- 不做约束的话，N+1 是**默认行为**，不是"可能"发生

### 6.2 三条强制规范

**规范 1：主资源在 root resolver 里 join 一次取够**

对于固定要返回的核心字段，直接在 `@QueryMapping` 里通过 MyBatis-Plus 的 `selectJoinList` / 自定义 mapper 一次性 join 完成，**不要**拆到 field resolver。

**规范 2：可选的跨表字段才用 DataLoader**

只有"不是每次都要、要的时候批量取"的关联字段，才放到 field resolver + DataLoader。

```java
// 注册 BatchLoader
@Configuration
public class WardrobeDataLoaders {
    @Bean
    public BatchLoaderRegistrar categoryBatchLoader(IWardrobeCategoryService categoryService) {
        return registry -> registry.forTypePair(Long.class, CategoryVO.class)
                .registerMappedBatchLoader((Set<Long> ids, BatchLoaderEnvironment env) ->
                        Mono.fromCallable(() -> categoryService.mapByIds(ids))
                );
    }
}

// 在 WardrobeItem 类型上挂载 category 字段
@Controller
public class WardrobeItemResolver {
    @SchemaMapping(typeName = "WardrobeItem", field = "category")
    public CompletableFuture<CategoryVO> category(WardrobeItemVO source, DataLoader<Long, CategoryVO> loader) {
        return loader.load(source.getCategoryId());
    }
}
```

> 注意 field resolver 的第一个入参是**父对象**（`WardrobeItemVO source`），不是当前登录用户。原方案的 DataLoader 示例从 `StpUtil` 取 userId，是错误的。

**规范 3：禁止在 field resolver 里直接调 `service.findById`**

否则一个返回 100 条的列表会触发 100 次单条查询。Code Review 时这是 blocking issue。

### 6.3 分页约定
GraphQL 官方推荐 Relay Cursor 连接（`edges` / `pageInfo`）。对于后台管理，offset/limit 已足够，先**沿用 MyBatis-Plus 的 `IPage`**，只是在 schema 中显式定义：

```graphql
type WardrobeItemPage {
  records: [WardrobeItem!]!
  total: Int!
  current: Int!
  size: Int!
}
```

后续若做公开 API，再迁移到 cursor 分页。

---

## 7. 权限与安全

### 7.1 把 Sa-Token 接入 GraphQL 请求上下文

`SaTokenConfig` 已注册 `SaTokenContextForThreadLocal` 作为 second context，这是 Sa-Token 在 GraphQL 异步 resolver 中能用的前提（DataLoader 回调会切线程，必须有 ThreadLocal 兜底）。

通过 `WebGraphQlInterceptor` 把登录态塞进 GraphQLContext，resolver 里就能直接拿：

```java
@Component
public class SaTokenGraphQlInterceptor implements WebGraphQlInterceptor {
    @Override
    public Mono<WebGraphQlResponse> intercept(WebGraphQlRequest request, Chain chain) {
        // /graphql 端点本身已被 SaInterceptor 拦截，这里能拿到登录态
        Long userId = StpUtil.isLogin() ? StpUtil.getLoginIdAsLong() : null;
        request.configureExecutionInput((execInput, builder) ->
                builder.graphQLContext(ctx -> ctx.put("userId", userId)).build());
        return chain.next(request);
    }
}
```

### 7.2 方法级鉴权（推荐复用 Sa-Token 注解）

`@SaCheckLogin` / `@SaCheckRole` / `@SaCheckPermission` 通过 Sa-Token 内置 AOP 生效，**在 `@QueryMapping` / `@MutationMapping` 方法上可以直接用**，无需额外切面：

```java
@Controller
public class WardrobeQueryResolver {

    @QueryMapping
    @SaCheckLogin
    public WardrobeItemPage wardrobeItems(@Argument WardrobeQuery query) {
        Long userId = StpUtil.getLoginIdAsLong();
        return wardrobeItemService.pageItems(userId, query);
    }

    @MutationMapping
    @SaCheckPermission("wardrobe:item:delete")
    public Boolean deleteWardrobeItem(@Argument Long id) {
        wardrobeItemService.removeItem(id, StpUtil.getLoginIdAsLong());
        return true;
    }
}
```

### 7.3 字段级权限

**反对**逐字段加注解（数量爆炸、易遗漏）。改为三层：

1. **Schema 白名单**：敏感字段（`password`、`apiSecret`、`internalRemark`）**不出现在 schema** 中——根本不返回的字段不需要鉴权
2. **类型分裂**：同一实体对外有 `User`（公共字段）和 `UserPrivate`（自己可见的字段），不同 Query 返回不同类型
3. **必要时**自定义 `Instrumentation` 在 `beginFieldExecution` 阶段做字段拦截，用于按角色屏蔽少数字段

> 原方案中的 `@Include(if = true)` 不存在——`@include` / `@skip` 是 GraphQL 客户端在查询里写的指令，与服务端鉴权无关。

### 7.4 查询安全护栏（必须配置，原方案缺失）

允许"自定义查询" = 接受来源可控性较低的输入。必须设：

| 限制 | 推荐值 | 实现 |
|------|--------|------|
| **最大查询深度** | 10 | `MaxQueryDepthInstrumentation` |
| **最大查询复杂度** | 200 | `MaxQueryComplexityInstrumentation` |
| **最大别名数** | 15 | 自定义 Instrumentation |
| **introspection** | prod 关闭或仅管理员可用 | Spring Boot 无现成配置项，需在 `GraphQlSourceBuilderCustomizer` 中为 graphql-java 设置 `NoIntrospectionGraphqlFieldVisibility`（可按 profile/角色开关） |
| **单请求 body 大小** | 256KB | Tomcat / Spring 配置 |
| **persisted query**（二期） | 仅允许白名单 hash | Apollo APQ 兼容 |

```java
@Configuration
public class GraphQlSecurityConfig {
    @Bean
    GraphQlSourceBuilderCustomizer hardening() {
        return builder -> builder.configureRuntimeWiring(w -> { /* ... */ })
                .configureGraphQl(g -> g.instrumentation(new ChainedInstrumentation(List.of(
                        new MaxQueryDepthInstrumentation(10),
                        new MaxQueryComplexityInstrumentation(200)
                ))));
    }
}
```

### 7.5 与现有拦截器的关系
- `/graphql` 端点本身仍走 `ApiKeyInterceptor` + `SaInterceptor`，确保未登录用户连请求都进不来
- `UserLastActiveInterceptor` 同样生效，不需要改动
- **`SaTokenConfig.addInterceptors` 不必为 `/graphql` 排除**，方法级注解会兜底所有更细的鉴权

---

## 8. 与现有基础设施的集成

### 8.1 缓存
- 现有 `@Cacheable` 加在 service 层，**继续生效**，因为 resolver 最终还是调 service
- 不要在 resolver 方法上加 `@Cacheable`——参数中包含 `DataFetchingEnvironment` 等不可序列化对象
- 二期可考虑在 root query 维度按 `(operationName, variables hash, userId)` 做 Redis 缓存

### 8.2 监控与链路
- **Druid SQL 监控**：不受影响，仍按 SQL 维度展示
- **Prometheus**：注册 `GraphQlObservationInstrumentation`（spring-graphql 自带），按 `operationName` / `outcome` 出指标
- **Brave tracing**：同上，spring-graphql 已与 Micrometer Observation 集成。需注意 DataLoader 跨线程时 trace context 通过 Brave 的 `CurrentTraceContext` 传播
- **日志**：在 interceptor 里把 operationName 写入 MDC，便于按业务定位

### 8.3 文件上传 / 下载
**保留 REST**。现有 `FileController` + MinIO 不迁移。GraphQL 仅在需要返回文件元数据时返回 URL。

### 8.4 LangChain4j / MCP / SSE
**保留 REST**。流式输出走 SSE 或 WebFlux，不走 GraphQL Query。若未来需要订阅式推送，再单独评估 GraphQL Subscription（WebSocket）。

### 8.5 Neo4j
图查询是 GraphQL 的天然适配场景，可优先在关系图谱模块（`top.aiolife.relationship`）试点。

---

## 9. 前端集成（vben-admin / web-antd）

### 9.1 目录约定
```
apps/web-antd/src/api/
├── *.ts                       # 现有 REST，保留
└── graphql/
    ├── client.ts              # graphql-request 客户端 + 拦截器
    ├── operations/            # 业务侧 .graphql 文件
    └── __generated__/         # codegen 输出，不提交修改（CI 校验）
```

### 9.2 客户端封装要点
- 复用 vben-admin 的 token 注入逻辑（`Authorization` / Sa-Token header）
- 复用统一错误处理：把 GraphQL `errors[]` 映射到现有 `ApiResponse` 的错误码体系
- 与 `@tanstack/vue-query` 集成，复用现有的 loading / retry / 缓存策略

### 9.3 Codegen 流水线
- 本地：`pnpm graphql:codegen --watch`
- CI：`pnpm graphql:codegen && git diff --exit-code` 防止漂移

---

## 10. 渐进式落地路径（围绕"自定义看板卡片"）

### 10.1 阶段划分

| 阶段 | 范围 | 交付物 | 退出条件 |
|------|------|--------|---------|
| **P0 指标目录骨架（必做）** | REST 指标目录基础设施 | `metric_catalog` / `dashboard_card` 表、`@MetricHandler` 注解扫描、3 个示例指标（如 `record.count.byDay`、`wardrobe.count.byCategory`、`relationship.top.byScore`）、卡片配置 UI | 看板页能拖拽配置出这 3 类卡片 |
| **P1 指标库扩展（必做）** | 把现有报表/统计页面拆成可复用指标 | 覆盖现有所有内置看板的指标 | 老看板用新机制重写一遍，行为一致 |
| **P2 评估 GraphQL（可选）** | 如果出现实体明细型卡片需求，引入 GraphQL | `/graphql` 端点、护栏配置、persisted query 白名单机制、relationship 或 record 模块的只读 schema | 至少 2 个真实卡片场景必须用 GraphQL 才能优雅实现 |
| **P3 GraphQL 试点（条件触发）** | 真正接入 GraphQL 到看板 | 一组只读 Query + 前端 codegen | staging 跑稳 2 周，性能不劣化 |
| **P4 复盘** | — | 决定是否继续推广 GraphQL | 看板团队反馈 + 性能数据 + 安全审计 |

**注意**：P2 是一个**评估关卡**，不是默认推进。如果指标目录已经能覆盖所有需求，就不引入 GraphQL。

### 10.2 P2 触发条件（什么时候才需要 GraphQL）

只在出现以下场景之一时启动 P2：
- 用户想做"看某实体的明细列表 + 自选展示字段 + 自选过滤条件"的卡片，且字段组合数量太多以至于 REST 指标目录会膨胀失控
- 出现需要深度嵌套关联（≥2 层）才能展示的卡片
- 第三方/移动端需要消费同一套看板数据，但取数粒度不同

### 10.3 GraphQL 试点模块选择（仅 P3 阶段适用）

- **关系图谱模块**（`top.aiolife.relationship` + Neo4j）—— 图查询天然契合
- **记录详情聚合页**（`top.aiolife.record`）—— 多关联表、字段需求多变

### 10.4 写操作（Mutation）的态度
**默认不做**。看板卡片本身的增删改走普通 REST（`POST /dashboard/cards` 等），不进 GraphQL。Mutation 相比 REST 没有明显优势，反而丢失了 HTTP 语义和现有工具链。

### 10.5 回滚标准
出现任一情况即下线 `/graphql` 端点回退到指标目录方案：
- 出现一次因 GraphQL 引入的安全事件（越权 / 拒绝服务 / 跨用户缓存命中）
- 看板单卡片 P95 延迟相比 REST 指标目录劣化 > 50%
- 新增卡片类型的开发效率未改善

---

## 11. 决策清单

落地前需要明确回答的问题：

- [ ] 「自定义看板卡片」的定义是：用户从内置卡片清单中选，还是允许任意自由组合？（决定 §3 选 A 还是 A+B）
- [ ] 接受「P0/P1 先做 REST 指标目录，P2 才评估 GraphQL」的分阶段路径吗？
- [ ] 内置卡片清单 V1 大约需要多少种？（指标目录的初始工作量参考）
- [ ] 卡片配置的存储归属：每个用户私有，还是有"公共看板模板"概念？
- [ ] 看板加载性能目标：整页 P95 < ?秒，单卡片 P95 < ?秒
- [ ] 若进入 P3：是否接受看板 GraphQL 查询**必须 persisted query**（前端不可发任意 query）？
- [ ] 若进入 P3：introspection 在生产是否完全关闭？
- [ ] 若进入 P3：前端是否接受引入 graphql-codegen 流水线？

回答完前 5 项即可进入 P0。后 3 项推迟到 P2 评估时再回答。

---

## 附录 A：原方案中的错误修正

| 原方案表述 | 问题 | 修正 |
|-----------|------|------|
| spring-graphql 是 Code-First | 事实错误 | spring-graphql 是 **Schema-First** |
| 支持 `@Projection` 等 Spring Data 特性 | 本项目用 MyBatis-Plus，不适用 | 删除该理由 |
| `@Include(if = true)` 指令控制字段可见性 | 该注解不存在；`@include` 是客户端指令 | 用 Schema 白名单 / 类型分裂 / Instrumentation 代替 |
| DataLoader 示例从 `StpUtil.getLoginIdAsLong()` 取 id | 会让所有字段都返回当前登录人的数据 | field resolver 第一个入参应为父对象 |
| "N+1 用 DataLoader 解决" 一笔带过 | 严重低估了 MyBatis-Plus 下的工作量 | 见第 6 节"三条强制规范" |
| 未提查询深度 / 复杂度 / introspection | 自定义查询的核心攻防面缺失 | 见第 7.4 节护栏配置 |
| 未提前端客户端 / codegen / vben-admin 改造 | 工程量被低估 | 见第 5.2、5.3、9 节 |
