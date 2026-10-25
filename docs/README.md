# 文档目录

日常开发先读[主仓库 README](../README.md)及[跨仓库规范](../AGENTS.md)，再进入对应端的 README／AGENTS。本文用于查找文档，不代替接口、SQL 或实现。

## 共同契约与上线

| 主题 | 文档 |
| --- | --- |
| API 参数、分页、日期、契约生成与统一推送 | [API 参数规范](API参数规范.md)、[接口最小信息契约](接口最小信息契约.md) |
| 首页卡片目录、配置、刷新与操作 | [首页功能说明](首页功能说明.md)、[今日时迹卡片](今日时迹卡片设计.md)、[新增业务卡片](首页新增业务卡片需求.md) |
| 图标与颜色唯一来源 | [图标与颜色统一规则](图标与颜色统一规则.md) |
| 后端结构、迁移与兼容性 | [后端文档目录](../aio-life-server/docs/README.md)、[SQL 规范](../aio-life-server/docs/SQL脚本规范.md)、[数据库升级](../aio-life-server/docs/数据库升级验证.md) |
| Web 组件与开发说明 | [Web 文档目录](../aio-life-front/docs/README.md)、[Web 开发规范](../aio-life-front/AGENTS.md) |
| 移动端启动、平台构建与验收 | [Mobile README](../aio-life-mobile/README.md)、[迁移与验收目录](mobile-migration/README.md) |
| 只读查询服务 | [Query README](../aio-life-query/README.md)、[原始需求与现状对照](<需求/AIO Life Query 智能数据查询服务需求方案.md>) |
| 浏览器采集 | [插件 README](../aio-life-chrome-plugin/README.md)、[后端采集契约](../aio-life-server/docs/浏览器采集接口.md) |

上述相对路径适用于标准工作区；独立克隆某一子仓库时，其他仓库不会自动出现。仓库地址见[主 README](../README.md)。

## 业务需求与实现

| 主题 | 文档 |
| --- | --- |
| 时迹 | [需求方案](需求/时迹需求方案.md)、[二级分类](时迹二级分类实现.md)、[Jev 设计与实现入口](时迹分类预测与Jev接入方案.md) |
| 首页快捷导航 | [需求](首页快捷导航-需求方案.md)、[技术实现](首页快捷导航-技术方案.md) |
| 生活足迹 | [需求与历次调整](需求/生活足迹需求方案.md)、[腾讯地图代理](../aio-life-server/docs/腾讯地图代理接入.md) |
| 银行卡与公共卡面 | [银行卡模块](银行卡模块需求与实现.md)、[公共卡面清单](公共银行卡卡面开发清单.md) |
| 会员、衣柜与身体数据 | [会员维护](会员维护需求方案.md)、[衣柜](衣柜需求方案.md)、[身体数据](身体档案需求.md) |
| 反馈 | [用户反馈需求](用户反馈需求方案.md) |
| 菜单与二级锁 | [菜单锁](菜单锁需求方案.md)、[个人菜单显示](../aio-life-server/docs/个人菜单显示设置.md) |
| 定时任务管理 | [服务端与发布说明](../aio-life-server/docs/定时任务管理.md) |
| 操作与访问日志 | [需求](需求/操作日志需求方案.md)、[数据库设计](design/operation-log/database-design.md)、[服务端说明](../aio-life-server/docs/操作和访问日志.md) |
| 个人数据导出 | [需求与技术方案](需求/个人数据导出需求与技术方案.md)（设计草案：Excel、权限、次数与审计） |
| 通知渠道 | [微信订阅消息](微信小程序订阅消息接入.md)、[飞书通知](飞书通知渠道方案.md) |
| MCP | [接口需求](需求/MCP接口需求方案.md)、[后端接入](../aio-life-server/docs/mcp/streamable-http.md) |
| 视频封面 | [实施清单](视频封面内部存储实施清单.md)、[迁移操作](../aio-life-server/docs/视频封面迁移.md) |
| 阅读原型 | [开发需求](prototypes/weread/开发需求.md) |

## 迁移、审查与历史方案

- [待办总览](待办任务.md)、[Mobile 全功能迁移清单](Mobile全功能迁移任务清单.md)、[迁移与验收分类索引](mobile-migration/README.md)。
- [2026-10-03 架构与安全审查](reviews/2026-10-03-architecture-security/README.md)：原始发现、任务、修复和各阶段验证分别保留。
- [早期安全审查](安全与架构审查报告.md)、[2026-09-12 表结构与复用评估](表结构与代码复用重构评估-2026-09-12.md)：历史快照，不能直接作为当前缺陷清单。
- [GraphQL 早期评估](graphql-permission-design.md)：单体看板方案；当前独立 Hasura 查询服务见上方 Query 入口。
- [移动端概念方案](design/mobile-concept-2026-09-27/README.md)、[首页设计提示词](../output/homepage-designs-2026-09-27/prompts.md)、[手机设计提示词](../output/homepage-designs-2026-09-27/mobile-prompt.md)：设计探索，不能作为现行验收标准。

## 文档维护约定

- 当前使用说明写可执行步骤、前置条件及失败处理；需求／设计中的建议和未实现内容明确标注，不写成现有能力。
- 同一业务规则只在共同契约中维护一份，各端文档引用；命令、版本和默认值对照 `package.json`、lockfile、`pom.xml`、配置及脚本。
- 修改 DTO 后生成契约；不要手改生成的类型或将历史接口示例当作最新定义。SQL 文档引用正式脚本，不复制另一份可执行 DDL。
- 历史记录保留日期、版本、失败及平台边界；旧预算、测试数量和上传结果只属于当时版本。新增核验写明本次实际执行的范围。
- 相对链接从当前文件定位，不使用个人电脑绝对路径。`artifacts/`、`target/` 等忽略目录中的证据可能不存在；写清本机产物属性，不承诺干净克隆可打开。
- 纯文档调整检查差异、链接、锚点、代码围栏与示例格式，无需业务测试或构建。外部网站、真实平台及生产状态未经核验时不声称通过。
