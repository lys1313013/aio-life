# Mobile 迁移与验收目录

本目录保留迁移、逐页对照和视觉验收记录。页面数量、测试结果、包体与截图属于对应批次；当前命令和平台要求见[移动端 README](../../aio-life-mobile/README.md)及[开发规范](../../aio-life-mobile/AGENTS.md)。不能用 H5 模拟接口结果代替真实后端、微信或 App 验收。

## 总览与仍需核验的项目

- [全功能迁移清单](../Mobile全功能迁移任务清单.md)、[待办](../待办任务.md)、[验收及未完成项](acceptance.md)。
- [首页核查与修复记录](home-card-audit.md)：按日期记录追加变更；共同业务规则见[首页功能说明](../首页功能说明.md)。历史包体预算按当时版本解读，现行预算见移动端配置。

## 按业务查找

| 范围 | 迁移记录 |
| --- | --- |
| 公共基础 | [工作区基线](baseline.md)、[组件契约](components.md) |
| 任务、生活记录、物品、会员 | [操作级清单](records.md)、[衣柜](wardrobe.md) |
| 财务、编程、关系、消息、MCP | [领域清单](domains.md) |
| 个人设置、密码库 | [个人设置](profile.md) |
| 人格测试、认证、时间看板 | [人格与认证](personality.md) |
| 分类与管理端 | [管理端](admin.md) |

## Web 对照与逐页检查

- [Web 对照总表](web-parity.md)、[菜单点击清单](web-menu-checklist.md)。
- [任务与时间](web-parity-tasks-records.md)、[活动等生活记录](web-parity-records.md)、[财务与资产](web-parity-finance-assets.md)、[关系与密码库](web-parity-social.md)、[平台与设置](web-parity-platform.md)。
- [逐页检查总表](page-audit.md)、[记录组](page-audit-records.md)、[领域组](page-audit-domains.md)、[平台组](page-audit-platform.md)。

## 间距与视觉复验

- [统一间距整改汇总](spacing-audit.md)。
- [06 目标与待办](../../aio-life-mobile/docs/mobile-migration/spacing-06.md)、[07 记录](spacing-07.md)、[08 物品与会员](../../aio-life-mobile/docs/mobile-migration/spacing-08.md)。
- [09 财务](spacing-09.md)、[10 编程与社交](spacing-10.md)、[11 设置与管理](spacing-11.md)、[12 首页与时迹](spacing-12.md)。

06、08 两份报告保存在移动端独立仓库；其余报告保存在主仓库。截图和 JSON 证据通常位于移动端忽略目录 `artifacts/`，不随 Git 克隆提供。保留各报告中的失败与未验证项，不能仅按“代码完成”判断验收完成。
