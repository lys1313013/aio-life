# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目概述

AIO Life — All-in-One 人生管理系统，记录、统计、分析个人生活数据。Monorepo 包含前后端两个 git 子模块。

## 目录结构

```
aio-life/
├── aio-life-front/    # 前端（git submodule → aio-life-front 仓库）
├── aio-life-server/    # 后端（git submodule → aio-life-server 仓库）
└── docs/              # 需求/技术方案文档
```

## 子模块操作

```bash
git clone --recursive https://github.com/lys1313013/aio-life.git  # 克隆含子模块
git submodule update --remote   # 更新子模块到最新
```

提交子模块变更就是普通的 `git add . && git commit && git push`。

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
- 响应格式 `{ rscode: '0', data: ... }`，成功码为 `'0'`
- 适配暗色模式和移动端
- 接口调用必须有 loading 效果
- 编辑弹窗上下居中，可无 title；确认弹窗在按钮旁弹出
- 别名 `#` 指向 `apps/web-antd/src/`

## 后端 — aio-life-server

Spring Boot 3.3 + Java 21 + MyBatis Plus + MySQL 8.x + Redis + Sa-Token + MinIO。

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
| `relationship` | 人际关系图谱（Neo4j），可通过 `AIO_LIFE_NEO4J_ENABLED` 开关 |
| `llm` | LLM/AI 功能（LangChain4j + OpenAI），API Key 管理 |
| `mcp` | MCP 协议支持（自定义注解驱动的 Tool 注册），含认证层 |

### 技术要点

- 逻辑删除：MyBatis Plus 全局配置 `is_deleted` 字段
- 对象映射：MapStruct，Lombok 配合 `lombok-mapstruct-binding`
- 环境变量：数据库密码、Redis、MinIO、邮件等敏感配置通过 `AIO_LIFE_*` 环境变量注入
- 邮件验证码有频率限制（单IP/单邮箱/全局，配置在 `aio.life.serve.auth.code.*`）
- 定时任务：`@EnableScheduling`，LeetCode 同步 cron 可配
