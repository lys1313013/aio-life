# aio-life

AIO Life — All-in-One 人生管理系统，记录、统计、分析个人生活数据。本仓库保存项目文档、编排配置和开发入口；前后端使用独立 Git 仓库维护。

## 技术栈

- **前端 aio-life-front**：Vue Vben Admin v5.5.9（Ant Design Vue），pnpm monorepo + Turborepo
- **后端 aio-life-server**：Spring Boot 3.3 + Java 21 + MyBatis Plus + MySQL 8.x + Redis + Sa-Token + MinIO

## 本地启动

```bash
# 前端（web-antd 开发服务器）
cd aio-life-front && pnpm run dev

# 后端（端口 45678，context-path /api；管理端点 45679）
cd aio-life-server && mvn spring-boot:run
```

数据库、Redis、MinIO、邮件等敏感配置通过 `AIO_LIFE_*` 环境变量注入。全量表结构见 `aio-life-server/docs/数据库表结构.md`。

## 初始化

```bash
git clone https://github.com/lys1313013/aio-life.git
cd aio-life
./scripts/setup-repositories.sh
```

初始化脚本会将前后端仓库克隆到本仓库目录下，但主仓库不会跟踪它们的提交指针。

## 更新前后端

```bash
./scripts/pull-latest-main.sh
```

更新脚本只允许在前后端仓库工作区干净且位于 `main` 分支时执行，使用 fast-forward 拉取，避免覆盖本地修改或意外合并。

## 目录结构

```
aio-life/
├── aio-life-front/    # 独立前端仓库（本仓库不跟踪）
├── aio-life-server/   # 独立后端仓库（本仓库不跟踪）
├── docs/              # 需求与技术方案
└── scripts/           # 前后端仓库初始化与更新脚本
```
