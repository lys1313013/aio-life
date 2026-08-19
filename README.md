# aio-life

AIO Life — All-in-One 人生管理系统，记录、统计、分析个人生活数据。Monorepo 以前后端两个 git 子模块组成。

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

## 克隆

```bash
git clone --recursive https://github.com/lys1313013/aio-life.git
```

## 更新子模块

```bash
git submodule update --remote
```

## 提交子模块更新

```bash
git add .
git commit -m "update"
git push origin main
```

## 目录结构

```
aio-life/
├── aio-life-front/    # 前端项目
└── aio-life-server/   # 后端项目
```
