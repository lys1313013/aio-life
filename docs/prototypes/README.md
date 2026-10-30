# 页面参考与原型维护

当前不维护独立运行的 UI 原型。开发先核对用户本次要求、[共同契约](../README.md)和各端运行页面及源码；不能根据历史候选稿恢复旧布局或增加尚未实现的业务字段。

## 当前实现入口

| 主题 | 规则与源码 |
| --- | --- |
| 首页 | [共同规则](../首页功能说明.md)、[Web](../../aio-life-front/apps/web-antd/src/views/dashboard/home/home-content.vue)、[Mobile](../../aio-life-mobile/src/pages/home/index.uvue) |
| 时迹 | [共同规则](../今日时迹卡片设计.md)、[Web 编辑器](../../aio-life-front/apps/web-antd/src/views/time/time-tracker/components/TimeSlotEditForm.vue)、[Mobile 编辑器](../../aio-life-mobile/src/components/TimeRecordEditor.uvue) |
| 任务管理 | [Web](../../aio-life-front/apps/web-antd/src/views/task-center/todo/index.vue)、[Mobile](../../aio-life-mobile/src/pages/tasks/todo.uvue)；按当前接口管理列与任务，不套用旧示例的固定列和 localStorage 数据模型 |
| 微信读书 | [当前入口说明](weread/开发需求.md) |
| 生活足迹 | [现行需求与契约](../需求/生活足迹需求方案.md)、[Web](../../aio-life-front/apps/web-antd/src/views/my-hub/life-footprints/index.vue)、[Mobile](../../aio-life-mobile/src/pages/life-footprints/index.uvue) |

移动端 H5 默认开发地址为 `http://127.0.0.1:5180/#/`，启动与端口以[Mobile README](../../aio-life-mobile/README.md)为准。该地址运行正式客户端源码，不是原型服务。

## 已清理的资料

2026-10-30 删除未采用或已被正式实现替代的任务候选 HTML 与预览、生活足迹静态示意图，以及微信读书的独立 HTML／Python 代理。保留的阅读说明已改为现行实现索引，不再维护独立代理、凭证或待确认的旧开发范围。旧稿仅可在 Git 历史中追溯。

`artifacts/`、`test-results/` 中的截图来自指定代码版本、测试数据、路由、尺寸和主题，属于本地验收产物。时迹新增与编辑、普通分类与运动分类、有无阅读／观影关联等场景使用同一编辑器，但可见字段不同。不能把测试场景差异误认为不同产品原型，也不能把历史测试结果视作当前验证。

后续原型只有在用户需要方案讨论时建立：注明状态、对应实现、差异和待确认项；差异很小且仍有讨论价值时同步修订，未采纳或被实现替代后删除，并更新引用。长期验收证据放入 `docs/reviews/`，保留日期与验证边界，不作为新的 UI 规范。
