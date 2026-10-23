# 2026-10-03 架构与安全审查索引

本目录是指定日期、指定源码基线的历史记录。原始发现保留问题出现时的状态；修复是否完成及验证范围，应结合修复记录和当前源码判断，不能只读原始报告或汇总中的单一状态。

| 阶段 | 文档 |
| --- | --- |
| 原始审查 | [汇总](summary.md)、[Web](front.md)、[Server](server.md)、[Mobile](mobile.md)、[安全专项](security.md) |
| 任务 | [审查任务](tasks.md)、[修复任务](fix-tasks.md) |
| 修复与验证 | [修复汇总](fix-summary.md)、[Web](front-fixes.md)、[Server](server-fixes.md)、[Mobile](mobile-fixes.md)、[数据库与跨仓契约](database-and-contract-fixes.md) |

这些记录中的测试、工作区状态和未完成项只属于对应批次。本机 `artifacts/`、测试日志和截图不随仓库提供；发布、真实服务及设备验收只能依据各记录明确写出的证据。现行开发要求见[跨仓库规范](../../../AGENTS.md)。
