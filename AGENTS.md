# AGENTS.md

This file provides guidance to AI coding agents when working with code in this repository.

## 项目概述

AIO Life — All-in-One 人生管理系统，记录、统计、分析个人生活数据。本仓库保存项目文档、编排配置和开发入口，Web、后端和移动端由独立 Git 仓库维护。

## 目录结构

```
aio-life/
├── aio-life-front/    # 独立前端仓库（主仓库不跟踪）
├── aio-life-server/   # 独立后端仓库（主仓库不跟踪）
├── aio-life-mobile/   # 独立 uni-app x Vapor 客户端仓库（主仓库不跟踪）
└── docs/              # 需求/技术方案文档（数据库表结构见 `aio-life-server/docs/数据库表结构.md`）
```

## 独立仓库操作

```bash
./scripts/setup-repositories.sh   # 缺失时克隆 Web、后端和移动端仓库
./scripts/pull-latest-main.sh     # 一键快进拉取三个仓库最新 main
```

三个目录各自拥有独立的 Git 历史。代码修改必须在对应仓库内提交和推送；主仓库不记录子仓库 commit 指针。

## Web 与移动端共同规范

- 同一业务在菜单、首页卡片、首页卡片设置和快捷导航中的图标与颜色，统一引用对应菜单配置，不得分别硬编码。业务关联与公共降级集中维护，图标资产生成同步；具体规则与实现入口见 `docs/图标与颜色统一规则.md`。

- 卡片（包括首页目标、纪念日、闪念等）及其他异步内容区域的 loading 占位高度必须尽可能接近加载后的实际展示高度，避免状态切换推动后续内容、造成页面跳动。首次加载按对应内容布局预留空间；刷新保留已有内容（包括空态）及高度，局部 loading 提示不得额外占用布局空间。不能用统一骨架行数或任意大高度套用所有卡片，也不能靠永久留白或裁切内容实现高度一致。
- 修改相关布局时，需对比 loading、有内容、空态、错误重试及已有内容刷新时的区域高度和后续内容位置，覆盖手机、平板、桌面及深浅主题。具体实现与验收见 `aio-life-front/AGENTS.md` 和 `aio-life-mobile/AGENTS.md` 的“Loading 高度与布局稳定（必须遵守）”。

## 移动端 — aio-life-mobile

uni-app x Vapor 独立客户端，入口为 `src/main.ts`，页面使用 `.uvue` 和组合式 API。

```bash
cd aio-life-mobile
npm ci
npm run dev            # Web 预览，默认 5180，代理本地后端 45678
npm run build          # Web 构建
npm run build:weixin   # 微信小程序构建
npm test              # API 契约测试
npm run test:e2e       # Web 登录与布局测试
npm run test:commit    # 提交前统一验证（单元、H5 E2E、微信构建与包体）
```

移动端采用“开发过程中按需验证、提交前统一测试”：日常修改不默认运行全量测试或双端构建；仅在定位问题或用户要求时运行相关检查。准备提交最终改动时，在移动仓库执行一次 `npm run test:commit`，E2E 已包含 H5 构建，不再额外重复构建。相同代码已通过的检查不重复执行；后续修改只重跑受影响的检查，影响不明确时重新全量验证。具体执行与日志规则见移动仓库 `AGENTS.md`。

App 使用匹配版本的 HBuilderX，具体要求与验证边界见移动仓库 README。凭据、Token、签名文件不得提交。

微信主包工程预算为 1600 KB，每包硬上限 2048 KB。业务专属服务、解析器和重量 npm 依赖必须归入对应分包，不能仅登记页面分包却把依赖留在公共目录。共享小工具独立提取，禁止跨业务分包同步导入；依赖归属与预算统一维护在移动仓库 `scripts/weixin-package-policy.json`。排查读取 `artifacts/weixin-size/` 的文件、模块体积报告，具体机制见移动仓库 `AGENTS.md` 的“避免主包再次超限”。

移动端间距唯一配置为 `aio-life-mobile/src/styles/spacing.json`，页面和组件必须引用生成的 SCSS 变量或公共类，不能复制数值。页面边距只能由一层容器提供，避免 `MobilePage` 与业务页面重复 padding；具体规范及生成/验收命令见 `aio-life-mobile/AGENTS.md` 的“统一间距与视觉验收”。

## 前端 — aio-life-front

基于 **Vue Vben Admin v5.5.9** 的 Ant Design Vue 版本，pnpm monorepo（Turborepo 编排）。

```bash
cd aio-life-front
pnpm run dev            # 启动 web-antd 开发服务器（默认）
pnpm run dev:antd       # 同上，显式指定
pnpm run build          # 生产构建
pnpm run lint           # ESLint 检查
pnpm run format         # Prettier 格式化
pnpm run test:unit      # Vitest 单元测试
pnpm run check          # 全量检查（循环依赖 + 依赖 + 类型 + 拼写）
```

详细架构、编码规范见 `aio-life-front/AGENTS.md`。

### 关键约定

- 后端返回的 ID 是 **string** 类型
- 响应格式 `{ code: 0, message: null, data: ... }`，成功码为 `0`
- 适配暗色模式，以及手机、平板和桌面端；响应式布局不能只验证手机和电脑，还需检查平板等中间宽度，避免移动端规则在平板上产生过宽、过疏或比例失衡的问题
- 界面尽可能简洁，Web 和移动端均遵循：能用图标清楚表达的操作或状态，只展示图标，不再配可见文字或重复说明；图标含义不明确时才保留必要的简短文字。图标按钮必须提供可访问名称（如 `aria-label`）。确需解释时，优先通过问号图标按需展示简短提示，不常驻铺开文字，也不为无歧义的内容额外添加问号。减少不必要的边框、分隔线和层级，具体见前端 `AGENTS.md` 的“界面表达规范”
- 移动端滚动列表统一触底自动加载下一页，禁止常驻“继续加载 / 加载更多 / 下一页”分页按钮。`MobilePage` 页面监听 `reachbottom`，自有 `scroll-view` 监听 `scrolltolower`；公共 `LoadMore` 只展示加载状态及失败重试。请求中不得重复发起分页；刷新、筛选和离页后的旧响应不得覆盖新状态；到末页或返回空页必须停止。分页失败保留已有列表和页码，仅在列表底部重试失败页，不得重置到第一页。新增或修改分页时须验证实际滚动触发、去重、末页停止和失败恢复。
- 接口调用必须有 loading 效果
- 编辑弹窗上下居中，可无 title；确认弹窗在按钮旁弹出
- 别名 `#` 指向 `apps/web-antd/src/`

## 后端 — aio-life-server

Spring Boot 3.5.16 + Java 21 + MyBatis Plus + MySQL 8.x + Redis + Sa-Token + MinIO。

```bash
cd aio-life-server
mvn spring-boot:run              # 启动（端口 45678，context-path /api）
mvn test                         # 运行测试
mvn package -DskipTests          # 打包
```

管理端点运行在 **45679** 端口（Prometheus、Health、Info）。日志含 traceId/spanId（Micrometer + Brave）。

### 模块分层

源码包结构 `top.aiolife.<module>`，按业务领域垂直拆分：

| 模块 | 职责 |
|---|---|
| `sso` | 登录认证，Sa-Token JWT + Redis，邮件验证码，用户绑定 |
| `system` | 系统管理（用户、菜单、字典） |
| `record` | 核心记录引擎：时迹、目标、待办、理财、荣誉、备忘、消息通知、第三方同步（LeetCode/CSDN/GitHub） |
| `wardrobe` | 衣柜管理 |
| `membership` | 会员维护：会员记录、统计 |
| `feedback` | 用户反馈：反馈提交、评论、管理端处理 |
| `relationship` | 人际关系图谱（Neo4j），可通过 `AIO_LIFE_NEO4J_ENABLED` 开关 |
| `llm` | 历史会话、消息及模型密钥配置管理；不提供大模型调用 |
| `mcp` | MCP 协议支持（自定义注解驱动的 Tool 注册），含认证层 |

### 技术要点

- MySQL 业务数据访问统一使用 MyBatis-Plus / MyBatis Mapper；禁止生产业务代码使用 `JdbcTemplate`、`NamedParameterJdbcTemplate`、`JdbcClient` 或直接 JDBC，禁止在 Service / Guard 内嵌 SQL。联表、行锁和特殊更新放入 Mapper，具体规则与自动检查见 `aio-life-server/AGENTS.md` 的“数据库访问规范（强制）”。
- 逻辑删除：MyBatis Plus 全局配置 `is_deleted` 字段
- 对象映射：MapStruct，Lombok 配合 `lombok-mapstruct-binding`
- 环境变量：数据库密码、Redis、MinIO、邮件等敏感配置通过 `AIO_LIFE_*` 环境变量注入
- 邮件验证码有频率限制（单IP/单邮箱/全局，配置在 `aio.life.server.auth.code.*`）
- 定时任务：`@EnableScheduling`，LeetCode 同步 cron 可配
