# AIO Life

All-in-One 人生管理系统，记录、统计、分析个人生活数据。本仓库维护跨端需求、技术方案、编排配置和开发脚本；各客户端与服务使用独立 Git 仓库。

## 仓库与文档

| 仓库 | 职责 | 开发入口 |
| --- | --- | --- |
| [aio-life-front](https://github.com/lys1313013/aio-life-front) | Vue Vben Admin 5.5.9、Ant Design Vue、pnpm monorepo | [README](https://github.com/lys1313013/aio-life-front/blob/main/README.md)、[开发规范](https://github.com/lys1313013/aio-life-front/blob/main/AGENTS.md) |
| [aio-life-server](https://github.com/lys1313013/aio-life-server) | Spring Boot 3.5.16、Java 21、MyBatis-Plus、MySQL、Redis、MinIO | [README](https://github.com/lys1313013/aio-life-server/blob/main/README.md)、[开发规范](https://github.com/lys1313013/aio-life-server/blob/main/AGENTS.md) |
| [aio-life-mobile](https://github.com/lys1313013/aio-life-mobile) | uni-app x Vapor，H5、微信小程序与 App | [README](https://github.com/lys1313013/aio-life-mobile/blob/main/README.md)、[开发规范](https://github.com/lys1313013/aio-life-mobile/blob/main/AGENTS.md) |
| [aio-life-query](https://github.com/lys1313013/aio-life-query) | Java 21、Hasura v3、MySQL Connector，只读查询 | [README](https://github.com/lys1313013/aio-life-query/blob/main/README.md) |
| [aio-life-chrome-plugin](https://github.com/lys1313013/aio-life-chrome-plugin) | B 站进度、豆瓣书影与购物页面采集 | [README](https://github.com/lys1313013/aio-life-chrome-plugin/blob/main/README.md) |

查找需求、API 契约、上线步骤与历史验收，先看[文档目录](docs/README.md)。跨仓库约定见 [AGENTS.md](AGENTS.md)。表结构、迁移兼容性及配置默认值分别以后端 SQL、升级计划和 `application.yml` 为准。

## 初始化与启动

```bash
git clone https://github.com/lys1313013/aio-life.git
cd aio-life
./scripts/setup-repositories.sh
```

脚本通过 SSH 克隆 Web、后端和移动端，需要可用的 GitHub SSH 授权。查询服务与浏览器插件按上表单独克隆到同名目录；初始化和更新脚本不包含它们。主仓库不跟踪子仓库文件或提交指针。

先按[后端 README](https://github.com/lys1313013/aio-life-server/blob/main/README.md)准备数据库、Redis、环境变量及业务库结构，再在独立终端分别启动。以下命令均从主仓库目录开始执行：

```bash
# 后端：API 45678，context-path /api；管理端点 45679
cd aio-life-server
mvn spring-boot:run
```

```bash
# Web：使用仓库固定的 pnpm 10.22.0，Node 版本见 Web README
cd aio-life-front
corepack enable
pnpm install --frozen-lockfile
pnpm run dev:antd
```

```bash
# 移动端 H5：5180，默认代理本地后端 45678
cd aio-life-mobile
npm ci
# 仅首次创建；已有 .env.local 时保留原配置
cp .env.example .env.local
npm run dev
```

敏感配置通过 `AIO_LIFE_*` 环境变量注入。Maven 不自动加载 `.env`；移动端 `VITE_*` 配置会进入客户端包，不能存放密钥。微信上传、App 工具链及平台验证见各端 README。

## 更新与交付

```bash
./scripts/pull-latest-main.sh
```

此入口只更新三个业务子仓库，要求它们处于 `main` 且工作区干净，使用 `git pull --ff-only`。主仓库自身、查询服务和插件需在各自仓库更新；不要为拉取代码丢弃未提交修改。

先在所属仓库审查并提交改动，再从主仓库执行：

```bash
python3 scripts/push-repositories.py
```

入口先生成并自动提交 Web、移动端契约，再推送后端、Web、移动端及主仓库；全部成功后检查契约并触发只读联合 CI。需要 Web 依赖、Git 授权和已登录的 GitHub CLI，不会自动提交业务修改，也不处理查询服务或插件。明确跳过 Git hooks 时使用 `--skip-hooks`，详见[统一推送前提与失败恢复](docs/API参数规范.md#本地统一推送与联合检查)。纯文档改动检查差异和引用，无需业务构建。

## 功能全景

![AIO Life 功能全景：时间任务、生活记录、财务管理、物品订阅、成长沉淀与连接管理](docs/architecture/feature-overview.png)

## 系统架构

![系统架构：Web、Mobile、浏览器插件与 MCP 客户端连接统一业务后端、数据存储、第三方数据来源及通知渠道](docs/architecture/system-architecture.png)

查询服务目前开放时迹、运动、阅读、影视、视频、演出六个数据集，提供 REST、GraphQL HTTP 和 MCP，支持时迹分类关系；通过原后端校验 Token／API Key。具体范围及部署限制见[查询服务说明](https://github.com/lys1313013/aio-life-query/blob/main/README.md)，图示不代表目标环境已部署全部可选服务。

## 目录结构

```text
aio-life/
├── aio-life-front/          # 独立 Web 仓库
├── aio-life-server/         # 独立后端仓库
├── aio-life-mobile/         # 独立移动端仓库
├── aio-life-query/          # 可选只读查询服务，单独克隆
├── aio-life-chrome-plugin/  # 可选浏览器插件，单独克隆
├── docs/                   # 跨端需求、方案与历史记录
└── scripts/                # 初始化、更新、契约生成与统一推送
```
