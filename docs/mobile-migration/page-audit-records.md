# A组移动页面逐项UI验收

本轮从模拟登录后的原生生活tab点击各功能入口；运动分类从运动页面“分类配置”进入。没有直接goto业务路由。16物理页面、18业务模式，覆盖390/768/1440深浅6布局共108页面布局；主矩阵36项、二级2项、13模式编辑恢复集中1项、延迟详情2项、交叉布局72项，加手机主页面筛选18项，共131个独立测试名称，均有最终通过结果。

## 命令与结果

主矩阵最终运行41项：39通过，纪念日2项因测试未先关闭更多菜单失败。修正真实菜单点击顺序后，最终补跑纪念日2项与72交叉布局；结果见完整日志。不是将上一轮作者报告作为通过依据。

```bash
npx playwright test tests/e2e/qa-records-all-pages.spec.js --workers=1 --output=test-results/page-audit/records-run --reporter=line
npx playwright test tests/e2e/qa-records-all-pages.spec.js --workers=1 --output=test-results/page-audit/records-run --reporter=line --grep "点击验收 anniversary|交叉布局"
npx playwright test tests/e2e/qa-records-all-pages.spec.js --workers=1 --output=test-results/page-audit/records-run --reporter=line --grep 首页筛选弹层
```

日志：`/tmp/qa-records-complete.log`、`/tmp/qa-records-layout-final.log`、`/tmp/qa-records-filters-final.log`。最终74项和补充筛选18项全部通过。主41项日志是在追加布局/筛选测试之前执行该文件的结果。全部fixture ID为字符串，包括`9223372036854775807`。

## 已修复

- 本组15个有max-width与margin:auto的业务根容器补width:100%和border-box，修平板内容缩窄。
- exercise/categories/activity/video/weread通用page类改为业务独立根类，防App全局.page浅色背景与flex/min-height污染，特别修复运动和分类配置的暗色浅底。
- 待办/反馈详情保留一个关闭入口，移除默认重复关闭。
- 待办/反馈/微信读书详情绑定contentKey；与主Agent的AdaptiveModal ResizeObserver共同修复异步详情测高。延迟800ms返回后，待办358px、反馈504px，390及768均断言>350。
- 主Agent修复共享图标水平居中；本组实际截图复核。纪念日新卡片/更多菜单/浮动新增来自其他授权并发修改，本组保留并适配UI流程。

## 每页模式/主要弹窗覆盖

| 模式 | 源码页 | 6布局 | 主要证据数 | 状态 |
|---|---|---:|---:|---|
| /pages/tasks/todo | `src/pages/tasks/todo.uvue` | 6 | 48 | passed-ui |
| /pages/tasks/goals | `src/pages/tasks/goals.uvue` | 6 | 52 | passed-ui |
| /pages/records/notes?kind=think | `src/pages/records/notes.uvue` | 6 | 26 | passed-ui |
| /pages/records/notes?kind=memo | `src/pages/records/notes.uvue` | 6 | 26 | passed-ui |
| /pages/records/anniversary | `src/pages/records/anniversary.uvue` | 6 | 40 | passed-ui |
| /pages/records/milestones | `src/pages/records/milestones.uvue` | 6 | 42 | passed-ui |
| /pages/records/honor | `src/pages/records/honor.uvue` | 6 | 44 | passed-ui |
| /pages/records/feedback | `src/pages/records/feedback.uvue` | 6 | 29 | passed-ui |
| /pages/records/library?kind=movie | `src/pages/records/library.uvue` | 6 | 52 | passed-ui |
| /pages/records/library?kind=read | `src/pages/records/library.uvue` | 6 | 44 | passed-ui |
| /pages/records/exercise | `src/pages/records/exercise.uvue` | 6 | 40 | passed-ui |
| /pages/records/categories | `src/pages/records/categories.uvue` | 6 | 31 | passed-ui |
| /pages/records/activity | `src/pages/records/activity.uvue` | 6 | 39 | passed-ui |
| /pages/records/video | `src/pages/records/video.uvue` | 6 | 39 | passed-ui |
| /pages/records/weread | `src/pages/records/weread.uvue` | 6 | 22 | passed-ui |
| /pages/goods/devices | `src/pages/goods/devices.uvue` | 6 | 43 | passed-ui |
| /pages/goods/wardrobe | `src/pages/goods/wardrobe.uvue` | 6 | 35 | passed-ui |
| /pages/member/index | `src/pages/member/index.uvue` | 6 | 52 | passed-ui |

待办二级：编辑任务、新增明细、编辑明细、删除明细确认；衣柜分类：新增、编辑、删除确认；微信读书：书架详情、跳转笔记和划线关联想法。390及768均真实按钮操作。

13模式保存失败恢复：目标、闪念、笔记、纪念日、里程碑、荣誉、观影、阅读、运动、活动、视频、设备、会员。失败保留输入，成功关闭，断言string ID与parentId/events/hiddenContent/note/end_date/issuer/doubanSubjectId/timeId/orderNumber/pagesInfo/spec/autoRenew等原关联字段。详见`save-recovery.json`。

18模式主页面所有30个picker（筛选、日期和图表查看选择器）已逐个打开、截图、取消；取消后值不变。无picker的页面明确记录0。

## 每个截图/弹出层证据

| 模式 | 精准测试名称 | 层/位置 | 截图 |
|---|---|---|---|
| todo | 点击验收 todo 390 light | 页面 | [todo-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-0-页面.png) |
| todo | 点击验收 todo 390 light | 新增列 | [todo-390-light-1-新增列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-1-新增列.png) |
| todo | 点击验收 todo 390 light | 新增列选择器0 | [todo-390-light-2-新增列选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-2-新增列选择器0.png) |
| todo | 点击验收 todo 390 light | 新增列底部 | [todo-390-light-3-新增列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-3-新增列底部.png) |
| todo | 点击验收 todo 390 light | 新增任务 | [todo-390-light-4-新增任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-4-新增任务.png) |
| todo | 点击验收 todo 390 light | 新增任务选择器0 | [todo-390-light-5-新增任务选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-5-新增任务选择器0.png) |
| todo | 点击验收 todo 390 light | 新增任务选择器1 | [todo-390-light-6-新增任务选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-6-新增任务选择器1.png) |
| todo | 点击验收 todo 390 light | 新增任务底部 | [todo-390-light-7-新增任务底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-7-新增任务底部.png) |
| todo | 点击验收 todo 390 light | 编辑列 | [todo-390-light-8-编辑列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-8-编辑列.png) |
| todo | 点击验收 todo 390 light | 编辑列选择器0 | [todo-390-light-9-编辑列选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-9-编辑列选择器0.png) |
| todo | 点击验收 todo 390 light | 编辑列底部 | [todo-390-light-10-编辑列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-10-编辑列底部.png) |
| todo | 点击验收 todo 390 light | 删除列 | [todo-390-light-11-删除列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-11-删除列.png) |
| todo | 点击验收 todo 390 light | 删除列底部 | [todo-390-light-12-删除列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-12-删除列底部.png) |
| todo | 点击验收 todo 390 light | 任务详情 | [todo-390-light-13-任务详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-13-任务详情.png) |
| todo | 点击验收 todo 390 light | 任务详情选择器0 | [todo-390-light-14-任务详情选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-14-任务详情选择器0.png) |
| todo | 点击验收 todo 390 light | 任务详情底部 | [todo-390-light-15-任务详情底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-15-任务详情底部.png) |
| todo | 点击验收 todo 390 light | 删除任务 | [todo-390-light-16-删除任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-16-删除任务.png) |
| todo | 点击验收 todo 390 light | 删除任务底部 | [todo-390-light-17-删除任务底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-390-light-17-删除任务底部.png) |
| todo | 交叉布局 todo 390 dark | 页面 | [cross-todo-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-390-dark-页面.png) |
| todo | 交叉布局 todo 390 dark | 主弹窗顶部 | [cross-todo-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-390-dark-主弹窗顶部.png) |
| todo | 交叉布局 todo 390 dark | 主弹窗底部 | [cross-todo-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-390-dark-主弹窗底部.png) |
| todo | 交叉布局 todo 768 light | 页面 | [cross-todo-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-768-light-页面.png) |
| todo | 交叉布局 todo 768 light | 主弹窗顶部 | [cross-todo-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-768-light-主弹窗顶部.png) |
| todo | 交叉布局 todo 768 light | 主弹窗底部 | [cross-todo-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-768-light-主弹窗底部.png) |
| todo | 点击验收 todo 768 dark | 页面 | [todo-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-0-页面.png) |
| todo | 点击验收 todo 768 dark | 新增列 | [todo-768-dark-1-新增列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-1-新增列.png) |
| todo | 点击验收 todo 768 dark | 新增列选择器0 | [todo-768-dark-2-新增列选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-2-新增列选择器0.png) |
| todo | 点击验收 todo 768 dark | 新增列底部 | [todo-768-dark-3-新增列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-3-新增列底部.png) |
| todo | 点击验收 todo 768 dark | 新增任务 | [todo-768-dark-4-新增任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-4-新增任务.png) |
| todo | 点击验收 todo 768 dark | 新增任务选择器0 | [todo-768-dark-5-新增任务选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-5-新增任务选择器0.png) |
| todo | 点击验收 todo 768 dark | 新增任务选择器1 | [todo-768-dark-6-新增任务选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-6-新增任务选择器1.png) |
| todo | 点击验收 todo 768 dark | 新增任务底部 | [todo-768-dark-7-新增任务底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-7-新增任务底部.png) |
| todo | 点击验收 todo 768 dark | 编辑列 | [todo-768-dark-8-编辑列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-8-编辑列.png) |
| todo | 点击验收 todo 768 dark | 编辑列选择器0 | [todo-768-dark-9-编辑列选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-9-编辑列选择器0.png) |
| todo | 点击验收 todo 768 dark | 编辑列底部 | [todo-768-dark-10-编辑列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-10-编辑列底部.png) |
| todo | 点击验收 todo 768 dark | 删除列 | [todo-768-dark-11-删除列.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-11-删除列.png) |
| todo | 点击验收 todo 768 dark | 删除列底部 | [todo-768-dark-12-删除列底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-12-删除列底部.png) |
| todo | 点击验收 todo 768 dark | 任务详情 | [todo-768-dark-13-任务详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-13-任务详情.png) |
| todo | 点击验收 todo 768 dark | 任务详情选择器0 | [todo-768-dark-14-任务详情选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-14-任务详情选择器0.png) |
| todo | 点击验收 todo 768 dark | 任务详情底部 | [todo-768-dark-15-任务详情底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-15-任务详情底部.png) |
| todo | 点击验收 todo 768 dark | 删除任务 | [todo-768-dark-16-删除任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-16-删除任务.png) |
| todo | 点击验收 todo 768 dark | 删除任务底部 | [todo-768-dark-17-删除任务底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/todo-768-dark-17-删除任务底部.png) |
| todo | 交叉布局 todo 1440 light | 页面 | [cross-todo-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-light-页面.png) |
| todo | 交叉布局 todo 1440 light | 主弹窗顶部 | [cross-todo-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-light-主弹窗顶部.png) |
| todo | 交叉布局 todo 1440 light | 主弹窗底部 | [cross-todo-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-light-主弹窗底部.png) |
| todo | 交叉布局 todo 1440 dark | 页面 | [cross-todo-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-dark-页面.png) |
| todo | 交叉布局 todo 1440 dark | 主弹窗顶部 | [cross-todo-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-dark-主弹窗顶部.png) |
| todo | 交叉布局 todo 1440 dark | 主弹窗底部 | [cross-todo-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-todo-1440-dark-主弹窗底部.png) |
| goals | 首页筛选弹层 goals 390 | 类型 | [filter-goals-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-goals-0.png) |
| goals | 首页筛选弹层 goals 390 | 状态 | [filter-goals-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-goals-1.png) |
| goals | 点击验收 goals 390 light | 页面 | [goals-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-0-页面.png) |
| goals | 点击验收 goals 390 light | 新增目标 | [goals-390-light-1-新增目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-1-新增目标.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器0 | [goals-390-light-2-新增目标选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-2-新增目标选择器0.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器1 | [goals-390-light-3-新增目标选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-3-新增目标选择器1.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器2 | [goals-390-light-4-新增目标选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-4-新增目标选择器2.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器3 | [goals-390-light-5-新增目标选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-5-新增目标选择器3.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器4 | [goals-390-light-6-新增目标选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-6-新增目标选择器4.png) |
| goals | 点击验收 goals 390 light | 新增目标选择器5 | [goals-390-light-7-新增目标选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-7-新增目标选择器5.png) |
| goals | 点击验收 goals 390 light | 新增目标底部 | [goals-390-light-8-新增目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-8-新增目标底部.png) |
| goals | 点击验收 goals 390 light | 编辑目标 | [goals-390-light-9-编辑目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-9-编辑目标.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器0 | [goals-390-light-10-编辑目标选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-10-编辑目标选择器0.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器1 | [goals-390-light-11-编辑目标选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-11-编辑目标选择器1.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器2 | [goals-390-light-12-编辑目标选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-12-编辑目标选择器2.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器3 | [goals-390-light-13-编辑目标选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-13-编辑目标选择器3.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器4 | [goals-390-light-14-编辑目标选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-14-编辑目标选择器4.png) |
| goals | 点击验收 goals 390 light | 编辑目标选择器5 | [goals-390-light-15-编辑目标选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-15-编辑目标选择器5.png) |
| goals | 点击验收 goals 390 light | 编辑目标底部 | [goals-390-light-16-编辑目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-16-编辑目标底部.png) |
| goals | 点击验收 goals 390 light | 删除目标 | [goals-390-light-17-删除目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-17-删除目标.png) |
| goals | 点击验收 goals 390 light | 删除目标底部 | [goals-390-light-18-删除目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-390-light-18-删除目标底部.png) |
| goals | 交叉布局 goals 390 dark | 页面 | [cross-goals-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-390-dark-页面.png) |
| goals | 交叉布局 goals 390 dark | 主弹窗顶部 | [cross-goals-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-390-dark-主弹窗顶部.png) |
| goals | 交叉布局 goals 390 dark | 主弹窗底部 | [cross-goals-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-390-dark-主弹窗底部.png) |
| goals | 交叉布局 goals 768 light | 页面 | [cross-goals-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-768-light-页面.png) |
| goals | 交叉布局 goals 768 light | 主弹窗顶部 | [cross-goals-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-768-light-主弹窗顶部.png) |
| goals | 交叉布局 goals 768 light | 主弹窗底部 | [cross-goals-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-768-light-主弹窗底部.png) |
| goals | 点击验收 goals 768 dark | 页面 | [goals-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-0-页面.png) |
| goals | 点击验收 goals 768 dark | 新增目标 | [goals-768-dark-1-新增目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-1-新增目标.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器0 | [goals-768-dark-2-新增目标选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-2-新增目标选择器0.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器1 | [goals-768-dark-3-新增目标选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-3-新增目标选择器1.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器2 | [goals-768-dark-4-新增目标选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-4-新增目标选择器2.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器3 | [goals-768-dark-5-新增目标选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-5-新增目标选择器3.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器4 | [goals-768-dark-6-新增目标选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-6-新增目标选择器4.png) |
| goals | 点击验收 goals 768 dark | 新增目标选择器5 | [goals-768-dark-7-新增目标选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-7-新增目标选择器5.png) |
| goals | 点击验收 goals 768 dark | 新增目标底部 | [goals-768-dark-8-新增目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-8-新增目标底部.png) |
| goals | 点击验收 goals 768 dark | 编辑目标 | [goals-768-dark-9-编辑目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-9-编辑目标.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器0 | [goals-768-dark-10-编辑目标选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-10-编辑目标选择器0.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器1 | [goals-768-dark-11-编辑目标选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-11-编辑目标选择器1.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器2 | [goals-768-dark-12-编辑目标选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-12-编辑目标选择器2.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器3 | [goals-768-dark-13-编辑目标选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-13-编辑目标选择器3.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器4 | [goals-768-dark-14-编辑目标选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-14-编辑目标选择器4.png) |
| goals | 点击验收 goals 768 dark | 编辑目标选择器5 | [goals-768-dark-15-编辑目标选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-15-编辑目标选择器5.png) |
| goals | 点击验收 goals 768 dark | 编辑目标底部 | [goals-768-dark-16-编辑目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-16-编辑目标底部.png) |
| goals | 点击验收 goals 768 dark | 删除目标 | [goals-768-dark-17-删除目标.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-17-删除目标.png) |
| goals | 点击验收 goals 768 dark | 删除目标底部 | [goals-768-dark-18-删除目标底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/goals-768-dark-18-删除目标底部.png) |
| goals | 交叉布局 goals 1440 light | 页面 | [cross-goals-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-light-页面.png) |
| goals | 交叉布局 goals 1440 light | 主弹窗顶部 | [cross-goals-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-light-主弹窗顶部.png) |
| goals | 交叉布局 goals 1440 light | 主弹窗底部 | [cross-goals-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-light-主弹窗底部.png) |
| goals | 交叉布局 goals 1440 dark | 页面 | [cross-goals-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-dark-页面.png) |
| goals | 交叉布局 goals 1440 dark | 主弹窗顶部 | [cross-goals-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-dark-主弹窗顶部.png) |
| goals | 交叉布局 goals 1440 dark | 主弹窗底部 | [cross-goals-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-goals-1440-dark-主弹窗底部.png) |
| think | 点击验收 think 390 light | 页面 | [think-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-0-页面.png) |
| think | 点击验收 think 390 light | 新增闪念 | [think-390-light-1-新增闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-1-新增闪念.png) |
| think | 点击验收 think 390 light | 新增闪念底部 | [think-390-light-2-新增闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-2-新增闪念底部.png) |
| think | 点击验收 think 390 light | 编辑闪念 | [think-390-light-3-编辑闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-3-编辑闪念.png) |
| think | 点击验收 think 390 light | 编辑闪念底部 | [think-390-light-4-编辑闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-4-编辑闪念底部.png) |
| think | 点击验收 think 390 light | 删除闪念 | [think-390-light-5-删除闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-5-删除闪念.png) |
| think | 点击验收 think 390 light | 删除闪念底部 | [think-390-light-6-删除闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-390-light-6-删除闪念底部.png) |
| think | 交叉布局 think 390 dark | 页面 | [cross-think-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-390-dark-页面.png) |
| think | 交叉布局 think 390 dark | 主弹窗顶部 | [cross-think-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-390-dark-主弹窗顶部.png) |
| think | 交叉布局 think 390 dark | 主弹窗底部 | [cross-think-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-390-dark-主弹窗底部.png) |
| think | 交叉布局 think 768 light | 页面 | [cross-think-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-768-light-页面.png) |
| think | 交叉布局 think 768 light | 主弹窗顶部 | [cross-think-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-768-light-主弹窗顶部.png) |
| think | 交叉布局 think 768 light | 主弹窗底部 | [cross-think-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-768-light-主弹窗底部.png) |
| think | 点击验收 think 768 dark | 页面 | [think-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-0-页面.png) |
| think | 点击验收 think 768 dark | 新增闪念 | [think-768-dark-1-新增闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-1-新增闪念.png) |
| think | 点击验收 think 768 dark | 新增闪念底部 | [think-768-dark-2-新增闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-2-新增闪念底部.png) |
| think | 点击验收 think 768 dark | 编辑闪念 | [think-768-dark-3-编辑闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-3-编辑闪念.png) |
| think | 点击验收 think 768 dark | 编辑闪念底部 | [think-768-dark-4-编辑闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-4-编辑闪念底部.png) |
| think | 点击验收 think 768 dark | 删除闪念 | [think-768-dark-5-删除闪念.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-5-删除闪念.png) |
| think | 点击验收 think 768 dark | 删除闪念底部 | [think-768-dark-6-删除闪念底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/think-768-dark-6-删除闪念底部.png) |
| think | 交叉布局 think 1440 light | 页面 | [cross-think-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-light-页面.png) |
| think | 交叉布局 think 1440 light | 主弹窗顶部 | [cross-think-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-light-主弹窗顶部.png) |
| think | 交叉布局 think 1440 light | 主弹窗底部 | [cross-think-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-light-主弹窗底部.png) |
| think | 交叉布局 think 1440 dark | 页面 | [cross-think-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-dark-页面.png) |
| think | 交叉布局 think 1440 dark | 主弹窗顶部 | [cross-think-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-dark-主弹窗顶部.png) |
| think | 交叉布局 think 1440 dark | 主弹窗底部 | [cross-think-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-think-1440-dark-主弹窗底部.png) |
| memo | 点击验收 memo 390 light | 页面 | [memo-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-0-页面.png) |
| memo | 点击验收 memo 390 light | 新增笔记 | [memo-390-light-1-新增笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-1-新增笔记.png) |
| memo | 点击验收 memo 390 light | 新增笔记底部 | [memo-390-light-2-新增笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-2-新增笔记底部.png) |
| memo | 点击验收 memo 390 light | 编辑笔记 | [memo-390-light-3-编辑笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-3-编辑笔记.png) |
| memo | 点击验收 memo 390 light | 编辑笔记底部 | [memo-390-light-4-编辑笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-4-编辑笔记底部.png) |
| memo | 点击验收 memo 390 light | 删除笔记 | [memo-390-light-5-删除笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-5-删除笔记.png) |
| memo | 点击验收 memo 390 light | 删除笔记底部 | [memo-390-light-6-删除笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-390-light-6-删除笔记底部.png) |
| memo | 交叉布局 memo 390 dark | 页面 | [cross-memo-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-390-dark-页面.png) |
| memo | 交叉布局 memo 390 dark | 主弹窗顶部 | [cross-memo-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-390-dark-主弹窗顶部.png) |
| memo | 交叉布局 memo 390 dark | 主弹窗底部 | [cross-memo-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-390-dark-主弹窗底部.png) |
| memo | 交叉布局 memo 768 light | 页面 | [cross-memo-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-768-light-页面.png) |
| memo | 交叉布局 memo 768 light | 主弹窗顶部 | [cross-memo-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-768-light-主弹窗顶部.png) |
| memo | 交叉布局 memo 768 light | 主弹窗底部 | [cross-memo-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-768-light-主弹窗底部.png) |
| memo | 点击验收 memo 768 dark | 页面 | [memo-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-0-页面.png) |
| memo | 点击验收 memo 768 dark | 新增笔记 | [memo-768-dark-1-新增笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-1-新增笔记.png) |
| memo | 点击验收 memo 768 dark | 新增笔记底部 | [memo-768-dark-2-新增笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-2-新增笔记底部.png) |
| memo | 点击验收 memo 768 dark | 编辑笔记 | [memo-768-dark-3-编辑笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-3-编辑笔记.png) |
| memo | 点击验收 memo 768 dark | 编辑笔记底部 | [memo-768-dark-4-编辑笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-4-编辑笔记底部.png) |
| memo | 点击验收 memo 768 dark | 删除笔记 | [memo-768-dark-5-删除笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-5-删除笔记.png) |
| memo | 点击验收 memo 768 dark | 删除笔记底部 | [memo-768-dark-6-删除笔记底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/memo-768-dark-6-删除笔记底部.png) |
| memo | 交叉布局 memo 1440 light | 页面 | [cross-memo-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-light-页面.png) |
| memo | 交叉布局 memo 1440 light | 主弹窗顶部 | [cross-memo-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-light-主弹窗顶部.png) |
| memo | 交叉布局 memo 1440 light | 主弹窗底部 | [cross-memo-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-light-主弹窗底部.png) |
| memo | 交叉布局 memo 1440 dark | 页面 | [cross-memo-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-dark-页面.png) |
| memo | 交叉布局 memo 1440 dark | 主弹窗顶部 | [cross-memo-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-dark-主弹窗顶部.png) |
| memo | 交叉布局 memo 1440 dark | 主弹窗底部 | [cross-memo-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-memo-1440-dark-主弹窗底部.png) |
| anniversary | 点击验收 anniversary 390 light | 页面 | [anniversary-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-0-页面.png) |
| anniversary | 点击验收 anniversary 390 light | 更多操作菜单 | [anniversary-390-light-1-更多操作菜单.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-1-更多操作菜单.png) |
| anniversary | 点击验收 anniversary 390 light | 编辑纪念日 | [anniversary-390-light-2-编辑纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-2-编辑纪念日.png) |
| anniversary | 点击验收 anniversary 390 light | 编辑纪念日选择器0 | [anniversary-390-light-3-编辑纪念日选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-3-编辑纪念日选择器0.png) |
| anniversary | 点击验收 anniversary 390 light | 编辑纪念日选择器1 | [anniversary-390-light-4-编辑纪念日选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-4-编辑纪念日选择器1.png) |
| anniversary | 点击验收 anniversary 390 light | 编辑纪念日选择器2 | [anniversary-390-light-5-编辑纪念日选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-5-编辑纪念日选择器2.png) |
| anniversary | 点击验收 anniversary 390 light | 编辑纪念日底部 | [anniversary-390-light-6-编辑纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-6-编辑纪念日底部.png) |
| anniversary | 点击验收 anniversary 390 light | 删除纪念日 | [anniversary-390-light-7-删除纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-7-删除纪念日.png) |
| anniversary | 点击验收 anniversary 390 light | 删除纪念日底部 | [anniversary-390-light-8-删除纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-8-删除纪念日底部.png) |
| anniversary | 点击验收 anniversary 390 light | 新增纪念日 | [anniversary-390-light-9-新增纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-9-新增纪念日.png) |
| anniversary | 点击验收 anniversary 390 light | 新增纪念日选择器0 | [anniversary-390-light-10-新增纪念日选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-10-新增纪念日选择器0.png) |
| anniversary | 点击验收 anniversary 390 light | 新增纪念日选择器1 | [anniversary-390-light-11-新增纪念日选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-11-新增纪念日选择器1.png) |
| anniversary | 点击验收 anniversary 390 light | 新增纪念日选择器2 | [anniversary-390-light-12-新增纪念日选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-12-新增纪念日选择器2.png) |
| anniversary | 点击验收 anniversary 390 light | 新增纪念日底部 | [anniversary-390-light-13-新增纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-390-light-13-新增纪念日底部.png) |
| anniversary | 交叉布局 anniversary 390 dark | 页面 | [cross-anniversary-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-390-dark-页面.png) |
| anniversary | 交叉布局 anniversary 390 dark | 主弹窗顶部 | [cross-anniversary-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-390-dark-主弹窗顶部.png) |
| anniversary | 交叉布局 anniversary 390 dark | 主弹窗底部 | [cross-anniversary-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-390-dark-主弹窗底部.png) |
| anniversary | 交叉布局 anniversary 768 light | 页面 | [cross-anniversary-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-768-light-页面.png) |
| anniversary | 交叉布局 anniversary 768 light | 主弹窗顶部 | [cross-anniversary-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-768-light-主弹窗顶部.png) |
| anniversary | 交叉布局 anniversary 768 light | 主弹窗底部 | [cross-anniversary-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-768-light-主弹窗底部.png) |
| anniversary | 点击验收 anniversary 768 dark | 页面 | [anniversary-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-0-页面.png) |
| anniversary | 点击验收 anniversary 768 dark | 更多操作菜单 | [anniversary-768-dark-1-更多操作菜单.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-1-更多操作菜单.png) |
| anniversary | 点击验收 anniversary 768 dark | 编辑纪念日 | [anniversary-768-dark-2-编辑纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-2-编辑纪念日.png) |
| anniversary | 点击验收 anniversary 768 dark | 编辑纪念日选择器0 | [anniversary-768-dark-3-编辑纪念日选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-3-编辑纪念日选择器0.png) |
| anniversary | 点击验收 anniversary 768 dark | 编辑纪念日选择器1 | [anniversary-768-dark-4-编辑纪念日选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-4-编辑纪念日选择器1.png) |
| anniversary | 点击验收 anniversary 768 dark | 编辑纪念日选择器2 | [anniversary-768-dark-5-编辑纪念日选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-5-编辑纪念日选择器2.png) |
| anniversary | 点击验收 anniversary 768 dark | 编辑纪念日底部 | [anniversary-768-dark-6-编辑纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-6-编辑纪念日底部.png) |
| anniversary | 点击验收 anniversary 768 dark | 删除纪念日 | [anniversary-768-dark-7-删除纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-7-删除纪念日.png) |
| anniversary | 点击验收 anniversary 768 dark | 删除纪念日底部 | [anniversary-768-dark-8-删除纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-8-删除纪念日底部.png) |
| anniversary | 点击验收 anniversary 768 dark | 新增纪念日 | [anniversary-768-dark-9-新增纪念日.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-9-新增纪念日.png) |
| anniversary | 点击验收 anniversary 768 dark | 新增纪念日选择器0 | [anniversary-768-dark-10-新增纪念日选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-10-新增纪念日选择器0.png) |
| anniversary | 点击验收 anniversary 768 dark | 新增纪念日选择器1 | [anniversary-768-dark-11-新增纪念日选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-11-新增纪念日选择器1.png) |
| anniversary | 点击验收 anniversary 768 dark | 新增纪念日选择器2 | [anniversary-768-dark-12-新增纪念日选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-12-新增纪念日选择器2.png) |
| anniversary | 点击验收 anniversary 768 dark | 新增纪念日底部 | [anniversary-768-dark-13-新增纪念日底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/anniversary-768-dark-13-新增纪念日底部.png) |
| anniversary | 交叉布局 anniversary 1440 light | 页面 | [cross-anniversary-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-light-页面.png) |
| anniversary | 交叉布局 anniversary 1440 light | 主弹窗顶部 | [cross-anniversary-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-light-主弹窗顶部.png) |
| anniversary | 交叉布局 anniversary 1440 light | 主弹窗底部 | [cross-anniversary-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-light-主弹窗底部.png) |
| anniversary | 交叉布局 anniversary 1440 dark | 页面 | [cross-anniversary-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-dark-页面.png) |
| anniversary | 交叉布局 anniversary 1440 dark | 主弹窗顶部 | [cross-anniversary-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-dark-主弹窗顶部.png) |
| anniversary | 交叉布局 anniversary 1440 dark | 主弹窗底部 | [cross-anniversary-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-anniversary-1440-dark-主弹窗底部.png) |
| milestones | 首页筛选弹层 milestones 390 | 类型 | [filter-milestones-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-milestones-0.png) |
| milestones | 首页筛选弹层 milestones 390 | 标签 | [filter-milestones-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-milestones-1.png) |
| milestones | 首页筛选弹层 milestones 390 | 开始日期 | [filter-milestones-2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-milestones-2.png) |
| milestones | 首页筛选弹层 milestones 390 | 结束日期 | [filter-milestones-3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-milestones-3.png) |
| milestones | 点击验收 milestones 390 light | 页面 | [milestones-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-0-页面.png) |
| milestones | 点击验收 milestones 390 light | 新增里程碑 | [milestones-390-light-1-新增里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-1-新增里程碑.png) |
| milestones | 点击验收 milestones 390 light | 新增里程碑选择器0 | [milestones-390-light-2-新增里程碑选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-2-新增里程碑选择器0.png) |
| milestones | 点击验收 milestones 390 light | 新增里程碑选择器1 | [milestones-390-light-3-新增里程碑选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-3-新增里程碑选择器1.png) |
| milestones | 点击验收 milestones 390 light | 新增里程碑选择器2 | [milestones-390-light-4-新增里程碑选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-4-新增里程碑选择器2.png) |
| milestones | 点击验收 milestones 390 light | 新增里程碑底部 | [milestones-390-light-5-新增里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-5-新增里程碑底部.png) |
| milestones | 点击验收 milestones 390 light | 编辑里程碑 | [milestones-390-light-6-编辑里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-6-编辑里程碑.png) |
| milestones | 点击验收 milestones 390 light | 编辑里程碑选择器0 | [milestones-390-light-7-编辑里程碑选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-7-编辑里程碑选择器0.png) |
| milestones | 点击验收 milestones 390 light | 编辑里程碑选择器1 | [milestones-390-light-8-编辑里程碑选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-8-编辑里程碑选择器1.png) |
| milestones | 点击验收 milestones 390 light | 编辑里程碑选择器2 | [milestones-390-light-9-编辑里程碑选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-9-编辑里程碑选择器2.png) |
| milestones | 点击验收 milestones 390 light | 编辑里程碑底部 | [milestones-390-light-10-编辑里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-10-编辑里程碑底部.png) |
| milestones | 点击验收 milestones 390 light | 删除里程碑 | [milestones-390-light-11-删除里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-11-删除里程碑.png) |
| milestones | 点击验收 milestones 390 light | 删除里程碑底部 | [milestones-390-light-12-删除里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-390-light-12-删除里程碑底部.png) |
| milestones | 交叉布局 milestones 390 dark | 页面 | [cross-milestones-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-390-dark-页面.png) |
| milestones | 交叉布局 milestones 390 dark | 主弹窗顶部 | [cross-milestones-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-390-dark-主弹窗顶部.png) |
| milestones | 交叉布局 milestones 390 dark | 主弹窗底部 | [cross-milestones-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-390-dark-主弹窗底部.png) |
| milestones | 交叉布局 milestones 768 light | 页面 | [cross-milestones-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-768-light-页面.png) |
| milestones | 交叉布局 milestones 768 light | 主弹窗顶部 | [cross-milestones-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-768-light-主弹窗顶部.png) |
| milestones | 交叉布局 milestones 768 light | 主弹窗底部 | [cross-milestones-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-768-light-主弹窗底部.png) |
| milestones | 点击验收 milestones 768 dark | 页面 | [milestones-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-0-页面.png) |
| milestones | 点击验收 milestones 768 dark | 新增里程碑 | [milestones-768-dark-1-新增里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-1-新增里程碑.png) |
| milestones | 点击验收 milestones 768 dark | 新增里程碑选择器0 | [milestones-768-dark-2-新增里程碑选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-2-新增里程碑选择器0.png) |
| milestones | 点击验收 milestones 768 dark | 新增里程碑选择器1 | [milestones-768-dark-3-新增里程碑选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-3-新增里程碑选择器1.png) |
| milestones | 点击验收 milestones 768 dark | 新增里程碑选择器2 | [milestones-768-dark-4-新增里程碑选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-4-新增里程碑选择器2.png) |
| milestones | 点击验收 milestones 768 dark | 新增里程碑底部 | [milestones-768-dark-5-新增里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-5-新增里程碑底部.png) |
| milestones | 点击验收 milestones 768 dark | 编辑里程碑 | [milestones-768-dark-6-编辑里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-6-编辑里程碑.png) |
| milestones | 点击验收 milestones 768 dark | 编辑里程碑选择器0 | [milestones-768-dark-7-编辑里程碑选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-7-编辑里程碑选择器0.png) |
| milestones | 点击验收 milestones 768 dark | 编辑里程碑选择器1 | [milestones-768-dark-8-编辑里程碑选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-8-编辑里程碑选择器1.png) |
| milestones | 点击验收 milestones 768 dark | 编辑里程碑选择器2 | [milestones-768-dark-9-编辑里程碑选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-9-编辑里程碑选择器2.png) |
| milestones | 点击验收 milestones 768 dark | 编辑里程碑底部 | [milestones-768-dark-10-编辑里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-10-编辑里程碑底部.png) |
| milestones | 点击验收 milestones 768 dark | 删除里程碑 | [milestones-768-dark-11-删除里程碑.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-11-删除里程碑.png) |
| milestones | 点击验收 milestones 768 dark | 删除里程碑底部 | [milestones-768-dark-12-删除里程碑底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/milestones-768-dark-12-删除里程碑底部.png) |
| milestones | 交叉布局 milestones 1440 light | 页面 | [cross-milestones-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-light-页面.png) |
| milestones | 交叉布局 milestones 1440 light | 主弹窗顶部 | [cross-milestones-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-light-主弹窗顶部.png) |
| milestones | 交叉布局 milestones 1440 light | 主弹窗底部 | [cross-milestones-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-light-主弹窗底部.png) |
| milestones | 交叉布局 milestones 1440 dark | 页面 | [cross-milestones-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-dark-页面.png) |
| milestones | 交叉布局 milestones 1440 dark | 主弹窗顶部 | [cross-milestones-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-dark-主弹窗顶部.png) |
| milestones | 交叉布局 milestones 1440 dark | 主弹窗底部 | [cross-milestones-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-milestones-1440-dark-主弹窗底部.png) |
| honor | 首页筛选弹层 honor 390 | 分类 | [filter-honor-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-honor-0.png) |
| honor | 首页筛选弹层 honor 390 | 级别 | [filter-honor-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-honor-1.png) |
| honor | 点击验收 honor 390 light | 页面 | [honor-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-0-页面.png) |
| honor | 点击验收 honor 390 light | 新增荣誉 | [honor-390-light-1-新增荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-1-新增荣誉.png) |
| honor | 点击验收 honor 390 light | 新增荣誉选择器0 | [honor-390-light-2-新增荣誉选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-2-新增荣誉选择器0.png) |
| honor | 点击验收 honor 390 light | 新增荣誉选择器1 | [honor-390-light-3-新增荣誉选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-3-新增荣誉选择器1.png) |
| honor | 点击验收 honor 390 light | 新增荣誉选择器2 | [honor-390-light-4-新增荣誉选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-4-新增荣誉选择器2.png) |
| honor | 点击验收 honor 390 light | 新增荣誉选择器3 | [honor-390-light-5-新增荣誉选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-5-新增荣誉选择器3.png) |
| honor | 点击验收 honor 390 light | 新增荣誉底部 | [honor-390-light-6-新增荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-6-新增荣誉底部.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉 | [honor-390-light-7-编辑荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-7-编辑荣誉.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉选择器0 | [honor-390-light-8-编辑荣誉选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-8-编辑荣誉选择器0.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉选择器1 | [honor-390-light-9-编辑荣誉选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-9-编辑荣誉选择器1.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉选择器2 | [honor-390-light-10-编辑荣誉选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-10-编辑荣誉选择器2.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉选择器3 | [honor-390-light-11-编辑荣誉选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-11-编辑荣誉选择器3.png) |
| honor | 点击验收 honor 390 light | 编辑荣誉底部 | [honor-390-light-12-编辑荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-12-编辑荣誉底部.png) |
| honor | 点击验收 honor 390 light | 删除荣誉 | [honor-390-light-13-删除荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-13-删除荣誉.png) |
| honor | 点击验收 honor 390 light | 删除荣誉底部 | [honor-390-light-14-删除荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-390-light-14-删除荣誉底部.png) |
| honor | 交叉布局 honor 390 dark | 页面 | [cross-honor-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-390-dark-页面.png) |
| honor | 交叉布局 honor 390 dark | 主弹窗顶部 | [cross-honor-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-390-dark-主弹窗顶部.png) |
| honor | 交叉布局 honor 390 dark | 主弹窗底部 | [cross-honor-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-390-dark-主弹窗底部.png) |
| honor | 交叉布局 honor 768 light | 页面 | [cross-honor-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-768-light-页面.png) |
| honor | 交叉布局 honor 768 light | 主弹窗顶部 | [cross-honor-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-768-light-主弹窗顶部.png) |
| honor | 交叉布局 honor 768 light | 主弹窗底部 | [cross-honor-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-768-light-主弹窗底部.png) |
| honor | 点击验收 honor 768 dark | 页面 | [honor-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-0-页面.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉 | [honor-768-dark-1-新增荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-1-新增荣誉.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉选择器0 | [honor-768-dark-2-新增荣誉选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-2-新增荣誉选择器0.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉选择器1 | [honor-768-dark-3-新增荣誉选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-3-新增荣誉选择器1.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉选择器2 | [honor-768-dark-4-新增荣誉选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-4-新增荣誉选择器2.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉选择器3 | [honor-768-dark-5-新增荣誉选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-5-新增荣誉选择器3.png) |
| honor | 点击验收 honor 768 dark | 新增荣誉底部 | [honor-768-dark-6-新增荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-6-新增荣誉底部.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉 | [honor-768-dark-7-编辑荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-7-编辑荣誉.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉选择器0 | [honor-768-dark-8-编辑荣誉选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-8-编辑荣誉选择器0.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉选择器1 | [honor-768-dark-9-编辑荣誉选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-9-编辑荣誉选择器1.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉选择器2 | [honor-768-dark-10-编辑荣誉选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-10-编辑荣誉选择器2.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉选择器3 | [honor-768-dark-11-编辑荣誉选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-11-编辑荣誉选择器3.png) |
| honor | 点击验收 honor 768 dark | 编辑荣誉底部 | [honor-768-dark-12-编辑荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-12-编辑荣誉底部.png) |
| honor | 点击验收 honor 768 dark | 删除荣誉 | [honor-768-dark-13-删除荣誉.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-13-删除荣誉.png) |
| honor | 点击验收 honor 768 dark | 删除荣誉底部 | [honor-768-dark-14-删除荣誉底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/honor-768-dark-14-删除荣誉底部.png) |
| honor | 交叉布局 honor 1440 light | 页面 | [cross-honor-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-light-页面.png) |
| honor | 交叉布局 honor 1440 light | 主弹窗顶部 | [cross-honor-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-light-主弹窗顶部.png) |
| honor | 交叉布局 honor 1440 light | 主弹窗底部 | [cross-honor-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-light-主弹窗底部.png) |
| honor | 交叉布局 honor 1440 dark | 页面 | [cross-honor-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-dark-页面.png) |
| honor | 交叉布局 honor 1440 dark | 主弹窗顶部 | [cross-honor-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-dark-主弹窗顶部.png) |
| honor | 交叉布局 honor 1440 dark | 主弹窗底部 | [cross-honor-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-honor-1440-dark-主弹窗底部.png) |
| feedback | 首页筛选弹层 feedback 390 | 状态 | [filter-feedback-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-feedback-0.png) |
| feedback | 点击验收 feedback 390 light | 页面 | [feedback-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-0-页面.png) |
| feedback | 点击验收 feedback 390 light | 提交反馈 | [feedback-390-light-1-提交反馈.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-1-提交反馈.png) |
| feedback | 点击验收 feedback 390 light | 提交反馈选择器0 | [feedback-390-light-2-提交反馈选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-2-提交反馈选择器0.png) |
| feedback | 点击验收 feedback 390 light | 提交反馈底部 | [feedback-390-light-3-提交反馈底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-3-提交反馈底部.png) |
| feedback | 点击验收 feedback 390 light | 反馈详情 | [feedback-390-light-4-反馈详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-4-反馈详情.png) |
| feedback | 点击验收 feedback 390 light | 反馈详情底部 | [feedback-390-light-5-反馈详情底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-5-反馈详情底部.png) |
| feedback | 点击验收 feedback 390 light | 撤销反馈 | [feedback-390-light-6-撤销反馈.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-6-撤销反馈.png) |
| feedback | 点击验收 feedback 390 light | 撤销反馈底部 | [feedback-390-light-7-撤销反馈底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-390-light-7-撤销反馈底部.png) |
| feedback | 交叉布局 feedback 390 dark | 页面 | [cross-feedback-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-390-dark-页面.png) |
| feedback | 交叉布局 feedback 390 dark | 主弹窗顶部 | [cross-feedback-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-390-dark-主弹窗顶部.png) |
| feedback | 交叉布局 feedback 390 dark | 主弹窗底部 | [cross-feedback-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-390-dark-主弹窗底部.png) |
| feedback | 交叉布局 feedback 768 light | 页面 | [cross-feedback-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-768-light-页面.png) |
| feedback | 交叉布局 feedback 768 light | 主弹窗顶部 | [cross-feedback-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-768-light-主弹窗顶部.png) |
| feedback | 交叉布局 feedback 768 light | 主弹窗底部 | [cross-feedback-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-768-light-主弹窗底部.png) |
| feedback | 点击验收 feedback 768 dark | 页面 | [feedback-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-0-页面.png) |
| feedback | 点击验收 feedback 768 dark | 提交反馈 | [feedback-768-dark-1-提交反馈.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-1-提交反馈.png) |
| feedback | 点击验收 feedback 768 dark | 提交反馈选择器0 | [feedback-768-dark-2-提交反馈选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-2-提交反馈选择器0.png) |
| feedback | 点击验收 feedback 768 dark | 提交反馈底部 | [feedback-768-dark-3-提交反馈底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-3-提交反馈底部.png) |
| feedback | 点击验收 feedback 768 dark | 反馈详情 | [feedback-768-dark-4-反馈详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-4-反馈详情.png) |
| feedback | 点击验收 feedback 768 dark | 反馈详情底部 | [feedback-768-dark-5-反馈详情底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-5-反馈详情底部.png) |
| feedback | 点击验收 feedback 768 dark | 撤销反馈 | [feedback-768-dark-6-撤销反馈.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-6-撤销反馈.png) |
| feedback | 点击验收 feedback 768 dark | 撤销反馈底部 | [feedback-768-dark-7-撤销反馈底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/feedback-768-dark-7-撤销反馈底部.png) |
| feedback | 交叉布局 feedback 1440 light | 页面 | [cross-feedback-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-light-页面.png) |
| feedback | 交叉布局 feedback 1440 light | 主弹窗顶部 | [cross-feedback-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-light-主弹窗顶部.png) |
| feedback | 交叉布局 feedback 1440 light | 主弹窗底部 | [cross-feedback-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-light-主弹窗底部.png) |
| feedback | 交叉布局 feedback 1440 dark | 页面 | [cross-feedback-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-dark-页面.png) |
| feedback | 交叉布局 feedback 1440 dark | 主弹窗顶部 | [cross-feedback-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-dark-主弹窗顶部.png) |
| feedback | 交叉布局 feedback 1440 dark | 主弹窗底部 | [cross-feedback-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-feedback-1440-dark-主弹窗底部.png) |
| movie | 首页筛选弹层 movie 390 | 类型 | [filter-movie-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-movie-0.png) |
| movie | 首页筛选弹层 movie 390 | 状态 | [filter-movie-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-movie-1.png) |
| movie | 点击验收 movie 390 light | 页面 | [movie-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-0-页面.png) |
| movie | 点击验收 movie 390 light | 新增观影 | [movie-390-light-1-新增观影.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-1-新增观影.png) |
| movie | 点击验收 movie 390 light | 新增观影选择器0 | [movie-390-light-2-新增观影选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-2-新增观影选择器0.png) |
| movie | 点击验收 movie 390 light | 新增观影选择器1 | [movie-390-light-3-新增观影选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-3-新增观影选择器1.png) |
| movie | 点击验收 movie 390 light | 新增观影选择器2 | [movie-390-light-4-新增观影选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-4-新增观影选择器2.png) |
| movie | 点击验收 movie 390 light | 新增观影选择器3 | [movie-390-light-5-新增观影选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-5-新增观影选择器3.png) |
| movie | 点击验收 movie 390 light | 新增观影选择器4 | [movie-390-light-6-新增观影选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-6-新增观影选择器4.png) |
| movie | 点击验收 movie 390 light | 新增观影底部 | [movie-390-light-7-新增观影底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-7-新增观影底部.png) |
| movie | 点击验收 movie 390 light | 豆瓣导入 | [movie-390-light-8-豆瓣导入.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-8-豆瓣导入.png) |
| movie | 点击验收 movie 390 light | 豆瓣导入底部 | [movie-390-light-9-豆瓣导入底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-9-豆瓣导入底部.png) |
| movie | 点击验收 movie 390 light | 编辑记录 | [movie-390-light-10-编辑记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-10-编辑记录.png) |
| movie | 点击验收 movie 390 light | 编辑记录选择器0 | [movie-390-light-11-编辑记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-11-编辑记录选择器0.png) |
| movie | 点击验收 movie 390 light | 编辑记录选择器1 | [movie-390-light-12-编辑记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-12-编辑记录选择器1.png) |
| movie | 点击验收 movie 390 light | 编辑记录选择器2 | [movie-390-light-13-编辑记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-13-编辑记录选择器2.png) |
| movie | 点击验收 movie 390 light | 编辑记录选择器3 | [movie-390-light-14-编辑记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-14-编辑记录选择器3.png) |
| movie | 点击验收 movie 390 light | 编辑记录选择器4 | [movie-390-light-15-编辑记录选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-15-编辑记录选择器4.png) |
| movie | 点击验收 movie 390 light | 编辑记录底部 | [movie-390-light-16-编辑记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-16-编辑记录底部.png) |
| movie | 点击验收 movie 390 light | 删除记录 | [movie-390-light-17-删除记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-17-删除记录.png) |
| movie | 点击验收 movie 390 light | 删除记录底部 | [movie-390-light-18-删除记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-390-light-18-删除记录底部.png) |
| movie | 交叉布局 movie 390 dark | 页面 | [cross-movie-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-390-dark-页面.png) |
| movie | 交叉布局 movie 390 dark | 主弹窗顶部 | [cross-movie-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-390-dark-主弹窗顶部.png) |
| movie | 交叉布局 movie 390 dark | 主弹窗底部 | [cross-movie-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-390-dark-主弹窗底部.png) |
| movie | 交叉布局 movie 768 light | 页面 | [cross-movie-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-768-light-页面.png) |
| movie | 交叉布局 movie 768 light | 主弹窗顶部 | [cross-movie-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-768-light-主弹窗顶部.png) |
| movie | 交叉布局 movie 768 light | 主弹窗底部 | [cross-movie-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-768-light-主弹窗底部.png) |
| movie | 点击验收 movie 768 dark | 页面 | [movie-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-0-页面.png) |
| movie | 点击验收 movie 768 dark | 新增观影 | [movie-768-dark-1-新增观影.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-1-新增观影.png) |
| movie | 点击验收 movie 768 dark | 新增观影选择器0 | [movie-768-dark-2-新增观影选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-2-新增观影选择器0.png) |
| movie | 点击验收 movie 768 dark | 新增观影选择器1 | [movie-768-dark-3-新增观影选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-3-新增观影选择器1.png) |
| movie | 点击验收 movie 768 dark | 新增观影选择器2 | [movie-768-dark-4-新增观影选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-4-新增观影选择器2.png) |
| movie | 点击验收 movie 768 dark | 新增观影选择器3 | [movie-768-dark-5-新增观影选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-5-新增观影选择器3.png) |
| movie | 点击验收 movie 768 dark | 新增观影选择器4 | [movie-768-dark-6-新增观影选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-6-新增观影选择器4.png) |
| movie | 点击验收 movie 768 dark | 新增观影底部 | [movie-768-dark-7-新增观影底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-7-新增观影底部.png) |
| movie | 点击验收 movie 768 dark | 豆瓣导入 | [movie-768-dark-8-豆瓣导入.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-8-豆瓣导入.png) |
| movie | 点击验收 movie 768 dark | 豆瓣导入底部 | [movie-768-dark-9-豆瓣导入底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-9-豆瓣导入底部.png) |
| movie | 点击验收 movie 768 dark | 编辑记录 | [movie-768-dark-10-编辑记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-10-编辑记录.png) |
| movie | 点击验收 movie 768 dark | 编辑记录选择器0 | [movie-768-dark-11-编辑记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-11-编辑记录选择器0.png) |
| movie | 点击验收 movie 768 dark | 编辑记录选择器1 | [movie-768-dark-12-编辑记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-12-编辑记录选择器1.png) |
| movie | 点击验收 movie 768 dark | 编辑记录选择器2 | [movie-768-dark-13-编辑记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-13-编辑记录选择器2.png) |
| movie | 点击验收 movie 768 dark | 编辑记录选择器3 | [movie-768-dark-14-编辑记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-14-编辑记录选择器3.png) |
| movie | 点击验收 movie 768 dark | 编辑记录选择器4 | [movie-768-dark-15-编辑记录选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-15-编辑记录选择器4.png) |
| movie | 点击验收 movie 768 dark | 编辑记录底部 | [movie-768-dark-16-编辑记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-16-编辑记录底部.png) |
| movie | 点击验收 movie 768 dark | 删除记录 | [movie-768-dark-17-删除记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-17-删除记录.png) |
| movie | 点击验收 movie 768 dark | 删除记录底部 | [movie-768-dark-18-删除记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/movie-768-dark-18-删除记录底部.png) |
| movie | 交叉布局 movie 1440 light | 页面 | [cross-movie-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-light-页面.png) |
| movie | 交叉布局 movie 1440 light | 主弹窗顶部 | [cross-movie-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-light-主弹窗顶部.png) |
| movie | 交叉布局 movie 1440 light | 主弹窗底部 | [cross-movie-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-light-主弹窗底部.png) |
| movie | 交叉布局 movie 1440 dark | 页面 | [cross-movie-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-dark-页面.png) |
| movie | 交叉布局 movie 1440 dark | 主弹窗顶部 | [cross-movie-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-dark-主弹窗顶部.png) |
| movie | 交叉布局 movie 1440 dark | 主弹窗底部 | [cross-movie-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-movie-1440-dark-主弹窗底部.png) |
| read | 首页筛选弹层 read 390 | 类型 | [filter-read-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-read-0.png) |
| read | 首页筛选弹层 read 390 | 状态 | [filter-read-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-read-1.png) |
| read | 点击验收 read 390 light | 页面 | [read-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-0-页面.png) |
| read | 点击验收 read 390 light | 新增阅读记录 | [read-390-light-1-新增阅读记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-1-新增阅读记录.png) |
| read | 点击验收 read 390 light | 新增阅读记录选择器0 | [read-390-light-2-新增阅读记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-2-新增阅读记录选择器0.png) |
| read | 点击验收 read 390 light | 新增阅读记录选择器1 | [read-390-light-3-新增阅读记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-3-新增阅读记录选择器1.png) |
| read | 点击验收 read 390 light | 新增阅读记录选择器2 | [read-390-light-4-新增阅读记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-4-新增阅读记录选择器2.png) |
| read | 点击验收 read 390 light | 新增阅读记录选择器3 | [read-390-light-5-新增阅读记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-5-新增阅读记录选择器3.png) |
| read | 点击验收 read 390 light | 新增阅读记录底部 | [read-390-light-6-新增阅读记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-6-新增阅读记录底部.png) |
| read | 点击验收 read 390 light | 编辑记录 | [read-390-light-7-编辑记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-7-编辑记录.png) |
| read | 点击验收 read 390 light | 编辑记录选择器0 | [read-390-light-8-编辑记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-8-编辑记录选择器0.png) |
| read | 点击验收 read 390 light | 编辑记录选择器1 | [read-390-light-9-编辑记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-9-编辑记录选择器1.png) |
| read | 点击验收 read 390 light | 编辑记录选择器2 | [read-390-light-10-编辑记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-10-编辑记录选择器2.png) |
| read | 点击验收 read 390 light | 编辑记录选择器3 | [read-390-light-11-编辑记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-11-编辑记录选择器3.png) |
| read | 点击验收 read 390 light | 编辑记录底部 | [read-390-light-12-编辑记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-12-编辑记录底部.png) |
| read | 点击验收 read 390 light | 删除记录 | [read-390-light-13-删除记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-13-删除记录.png) |
| read | 点击验收 read 390 light | 删除记录底部 | [read-390-light-14-删除记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-390-light-14-删除记录底部.png) |
| read | 交叉布局 read 390 dark | 页面 | [cross-read-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-390-dark-页面.png) |
| read | 交叉布局 read 390 dark | 主弹窗顶部 | [cross-read-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-390-dark-主弹窗顶部.png) |
| read | 交叉布局 read 390 dark | 主弹窗底部 | [cross-read-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-390-dark-主弹窗底部.png) |
| read | 交叉布局 read 768 light | 页面 | [cross-read-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-768-light-页面.png) |
| read | 交叉布局 read 768 light | 主弹窗顶部 | [cross-read-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-768-light-主弹窗顶部.png) |
| read | 交叉布局 read 768 light | 主弹窗底部 | [cross-read-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-768-light-主弹窗底部.png) |
| read | 点击验收 read 768 dark | 页面 | [read-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-0-页面.png) |
| read | 点击验收 read 768 dark | 新增阅读记录 | [read-768-dark-1-新增阅读记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-1-新增阅读记录.png) |
| read | 点击验收 read 768 dark | 新增阅读记录选择器0 | [read-768-dark-2-新增阅读记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-2-新增阅读记录选择器0.png) |
| read | 点击验收 read 768 dark | 新增阅读记录选择器1 | [read-768-dark-3-新增阅读记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-3-新增阅读记录选择器1.png) |
| read | 点击验收 read 768 dark | 新增阅读记录选择器2 | [read-768-dark-4-新增阅读记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-4-新增阅读记录选择器2.png) |
| read | 点击验收 read 768 dark | 新增阅读记录选择器3 | [read-768-dark-5-新增阅读记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-5-新增阅读记录选择器3.png) |
| read | 点击验收 read 768 dark | 新增阅读记录底部 | [read-768-dark-6-新增阅读记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-6-新增阅读记录底部.png) |
| read | 点击验收 read 768 dark | 编辑记录 | [read-768-dark-7-编辑记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-7-编辑记录.png) |
| read | 点击验收 read 768 dark | 编辑记录选择器0 | [read-768-dark-8-编辑记录选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-8-编辑记录选择器0.png) |
| read | 点击验收 read 768 dark | 编辑记录选择器1 | [read-768-dark-9-编辑记录选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-9-编辑记录选择器1.png) |
| read | 点击验收 read 768 dark | 编辑记录选择器2 | [read-768-dark-10-编辑记录选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-10-编辑记录选择器2.png) |
| read | 点击验收 read 768 dark | 编辑记录选择器3 | [read-768-dark-11-编辑记录选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-11-编辑记录选择器3.png) |
| read | 点击验收 read 768 dark | 编辑记录底部 | [read-768-dark-12-编辑记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-12-编辑记录底部.png) |
| read | 点击验收 read 768 dark | 删除记录 | [read-768-dark-13-删除记录.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-13-删除记录.png) |
| read | 点击验收 read 768 dark | 删除记录底部 | [read-768-dark-14-删除记录底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/read-768-dark-14-删除记录底部.png) |
| read | 交叉布局 read 1440 light | 页面 | [cross-read-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-light-页面.png) |
| read | 交叉布局 read 1440 light | 主弹窗顶部 | [cross-read-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-light-主弹窗顶部.png) |
| read | 交叉布局 read 1440 light | 主弹窗底部 | [cross-read-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-light-主弹窗底部.png) |
| read | 交叉布局 read 1440 dark | 页面 | [cross-read-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-dark-页面.png) |
| read | 交叉布局 read 1440 dark | 主弹窗顶部 | [cross-read-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-dark-主弹窗顶部.png) |
| read | 交叉布局 read 1440 dark | 主弹窗底部 | [cross-read-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-read-1440-dark-主弹窗底部.png) |
| exercise | 首页筛选弹层 exercise 390 | 运动类型 | [filter-exercise-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-0.png) |
| exercise | 首页筛选弹层 exercise 390 | 开始日期 | [filter-exercise-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-1.png) |
| exercise | 首页筛选弹层 exercise 390 | 结束日期 | [filter-exercise-2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-2.png) |
| exercise | 首页筛选弹层 exercise 390 | 查看数值 | [filter-exercise-3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-3.png) |
| exercise | 首页筛选弹层 exercise 390 | 查看数值 | [filter-exercise-4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-4.png) |
| exercise | 首页筛选弹层 exercise 390 | 查看数值 | [filter-exercise-5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-exercise-5.png) |
| exercise | 点击验收 exercise 390 light | 页面 | [exercise-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-0-页面.png) |
| exercise | 点击验收 exercise 390 light | 新增运动 | [exercise-390-light-1-新增运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-1-新增运动.png) |
| exercise | 点击验收 exercise 390 light | 新增运动选择器0 | [exercise-390-light-2-新增运动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-2-新增运动选择器0.png) |
| exercise | 点击验收 exercise 390 light | 新增运动选择器1 | [exercise-390-light-3-新增运动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-3-新增运动选择器1.png) |
| exercise | 点击验收 exercise 390 light | 新增运动底部 | [exercise-390-light-4-新增运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-4-新增运动底部.png) |
| exercise | 点击验收 exercise 390 light | 编辑运动 | [exercise-390-light-5-编辑运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-5-编辑运动.png) |
| exercise | 点击验收 exercise 390 light | 编辑运动选择器0 | [exercise-390-light-6-编辑运动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-6-编辑运动选择器0.png) |
| exercise | 点击验收 exercise 390 light | 编辑运动选择器1 | [exercise-390-light-7-编辑运动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-7-编辑运动选择器1.png) |
| exercise | 点击验收 exercise 390 light | 编辑运动底部 | [exercise-390-light-8-编辑运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-8-编辑运动底部.png) |
| exercise | 点击验收 exercise 390 light | 删除运动 | [exercise-390-light-9-删除运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-9-删除运动.png) |
| exercise | 点击验收 exercise 390 light | 删除运动底部 | [exercise-390-light-10-删除运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-390-light-10-删除运动底部.png) |
| exercise | 交叉布局 exercise 390 dark | 页面 | [cross-exercise-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-390-dark-页面.png) |
| exercise | 交叉布局 exercise 390 dark | 主弹窗顶部 | [cross-exercise-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-390-dark-主弹窗顶部.png) |
| exercise | 交叉布局 exercise 390 dark | 主弹窗底部 | [cross-exercise-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-390-dark-主弹窗底部.png) |
| exercise | 交叉布局 exercise 768 light | 页面 | [cross-exercise-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-768-light-页面.png) |
| exercise | 交叉布局 exercise 768 light | 主弹窗顶部 | [cross-exercise-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-768-light-主弹窗顶部.png) |
| exercise | 交叉布局 exercise 768 light | 主弹窗底部 | [cross-exercise-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-768-light-主弹窗底部.png) |
| exercise | 点击验收 exercise 768 dark | 页面 | [exercise-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-0-页面.png) |
| exercise | 点击验收 exercise 768 dark | 新增运动 | [exercise-768-dark-1-新增运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-1-新增运动.png) |
| exercise | 点击验收 exercise 768 dark | 新增运动选择器0 | [exercise-768-dark-2-新增运动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-2-新增运动选择器0.png) |
| exercise | 点击验收 exercise 768 dark | 新增运动选择器1 | [exercise-768-dark-3-新增运动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-3-新增运动选择器1.png) |
| exercise | 点击验收 exercise 768 dark | 新增运动底部 | [exercise-768-dark-4-新增运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-4-新增运动底部.png) |
| exercise | 点击验收 exercise 768 dark | 编辑运动 | [exercise-768-dark-5-编辑运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-5-编辑运动.png) |
| exercise | 点击验收 exercise 768 dark | 编辑运动选择器0 | [exercise-768-dark-6-编辑运动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-6-编辑运动选择器0.png) |
| exercise | 点击验收 exercise 768 dark | 编辑运动选择器1 | [exercise-768-dark-7-编辑运动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-7-编辑运动选择器1.png) |
| exercise | 点击验收 exercise 768 dark | 编辑运动底部 | [exercise-768-dark-8-编辑运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-8-编辑运动底部.png) |
| exercise | 点击验收 exercise 768 dark | 删除运动 | [exercise-768-dark-9-删除运动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-9-删除运动.png) |
| exercise | 点击验收 exercise 768 dark | 删除运动底部 | [exercise-768-dark-10-删除运动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/exercise-768-dark-10-删除运动底部.png) |
| exercise | 交叉布局 exercise 1440 light | 页面 | [cross-exercise-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-light-页面.png) |
| exercise | 交叉布局 exercise 1440 light | 主弹窗顶部 | [cross-exercise-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-light-主弹窗顶部.png) |
| exercise | 交叉布局 exercise 1440 light | 主弹窗底部 | [cross-exercise-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-light-主弹窗底部.png) |
| exercise | 交叉布局 exercise 1440 dark | 页面 | [cross-exercise-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-dark-页面.png) |
| exercise | 交叉布局 exercise 1440 dark | 主弹窗顶部 | [cross-exercise-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-dark-主弹窗顶部.png) |
| exercise | 交叉布局 exercise 1440 dark | 主弹窗底部 | [cross-exercise-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-exercise-1440-dark-主弹窗底部.png) |
| categories | 首页筛选弹层 categories 390 | 分类类型 | [filter-categories-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-categories-0.png) |
| categories | 点击验收 categories 390 light | 页面 | [categories-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-0-页面.png) |
| categories | 点击验收 categories 390 light | 新增分类 | [categories-390-light-1-新增分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-1-新增分类.png) |
| categories | 点击验收 categories 390 light | 新增分类选择器0 | [categories-390-light-2-新增分类选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-2-新增分类选择器0.png) |
| categories | 点击验收 categories 390 light | 新增分类底部 | [categories-390-light-3-新增分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-3-新增分类底部.png) |
| categories | 点击验收 categories 390 light | 编辑分类 | [categories-390-light-4-编辑分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-4-编辑分类.png) |
| categories | 点击验收 categories 390 light | 编辑分类选择器0 | [categories-390-light-5-编辑分类选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-5-编辑分类选择器0.png) |
| categories | 点击验收 categories 390 light | 编辑分类底部 | [categories-390-light-6-编辑分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-6-编辑分类底部.png) |
| categories | 点击验收 categories 390 light | 删除分类 | [categories-390-light-7-删除分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-7-删除分类.png) |
| categories | 点击验收 categories 390 light | 删除分类底部 | [categories-390-light-8-删除分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-390-light-8-删除分类底部.png) |
| categories | 交叉布局 categories 390 dark | 页面 | [cross-categories-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-390-dark-页面.png) |
| categories | 交叉布局 categories 390 dark | 主弹窗顶部 | [cross-categories-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-390-dark-主弹窗顶部.png) |
| categories | 交叉布局 categories 390 dark | 主弹窗底部 | [cross-categories-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-390-dark-主弹窗底部.png) |
| categories | 交叉布局 categories 768 light | 页面 | [cross-categories-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-768-light-页面.png) |
| categories | 交叉布局 categories 768 light | 主弹窗顶部 | [cross-categories-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-768-light-主弹窗顶部.png) |
| categories | 交叉布局 categories 768 light | 主弹窗底部 | [cross-categories-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-768-light-主弹窗底部.png) |
| categories | 点击验收 categories 768 dark | 页面 | [categories-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-0-页面.png) |
| categories | 点击验收 categories 768 dark | 新增分类 | [categories-768-dark-1-新增分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-1-新增分类.png) |
| categories | 点击验收 categories 768 dark | 新增分类选择器0 | [categories-768-dark-2-新增分类选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-2-新增分类选择器0.png) |
| categories | 点击验收 categories 768 dark | 新增分类底部 | [categories-768-dark-3-新增分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-3-新增分类底部.png) |
| categories | 点击验收 categories 768 dark | 编辑分类 | [categories-768-dark-4-编辑分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-4-编辑分类.png) |
| categories | 点击验收 categories 768 dark | 编辑分类选择器0 | [categories-768-dark-5-编辑分类选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-5-编辑分类选择器0.png) |
| categories | 点击验收 categories 768 dark | 编辑分类底部 | [categories-768-dark-6-编辑分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-6-编辑分类底部.png) |
| categories | 点击验收 categories 768 dark | 删除分类 | [categories-768-dark-7-删除分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-7-删除分类.png) |
| categories | 点击验收 categories 768 dark | 删除分类底部 | [categories-768-dark-8-删除分类底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/categories-768-dark-8-删除分类底部.png) |
| categories | 交叉布局 categories 1440 light | 页面 | [cross-categories-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-light-页面.png) |
| categories | 交叉布局 categories 1440 light | 主弹窗顶部 | [cross-categories-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-light-主弹窗顶部.png) |
| categories | 交叉布局 categories 1440 light | 主弹窗底部 | [cross-categories-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-light-主弹窗底部.png) |
| categories | 交叉布局 categories 1440 dark | 页面 | [cross-categories-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-dark-页面.png) |
| categories | 交叉布局 categories 1440 dark | 主弹窗顶部 | [cross-categories-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-dark-主弹窗顶部.png) |
| categories | 交叉布局 categories 1440 dark | 主弹窗底部 | [cross-categories-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-categories-1440-dark-主弹窗底部.png) |
| activity | 首页筛选弹层 activity 390 | 类型 | [filter-activity-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-activity-0.png) |
| activity | 点击验收 activity 390 light | 页面 | [activity-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-0-页面.png) |
| activity | 点击验收 activity 390 light | 新增活动 | [activity-390-light-1-新增活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-1-新增活动.png) |
| activity | 点击验收 activity 390 light | 新增活动选择器0 | [activity-390-light-2-新增活动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-2-新增活动选择器0.png) |
| activity | 点击验收 activity 390 light | 新增活动选择器1 | [activity-390-light-3-新增活动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-3-新增活动选择器1.png) |
| activity | 点击验收 activity 390 light | 新增活动选择器2 | [activity-390-light-4-新增活动选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-4-新增活动选择器2.png) |
| activity | 点击验收 activity 390 light | 新增活动底部 | [activity-390-light-5-新增活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-5-新增活动底部.png) |
| activity | 点击验收 activity 390 light | 编辑活动 | [activity-390-light-6-编辑活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-6-编辑活动.png) |
| activity | 点击验收 activity 390 light | 编辑活动选择器0 | [activity-390-light-7-编辑活动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-7-编辑活动选择器0.png) |
| activity | 点击验收 activity 390 light | 编辑活动选择器1 | [activity-390-light-8-编辑活动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-8-编辑活动选择器1.png) |
| activity | 点击验收 activity 390 light | 编辑活动选择器2 | [activity-390-light-9-编辑活动选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-9-编辑活动选择器2.png) |
| activity | 点击验收 activity 390 light | 编辑活动底部 | [activity-390-light-10-编辑活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-10-编辑活动底部.png) |
| activity | 点击验收 activity 390 light | 删除活动 | [activity-390-light-11-删除活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-11-删除活动.png) |
| activity | 点击验收 activity 390 light | 删除活动底部 | [activity-390-light-12-删除活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-390-light-12-删除活动底部.png) |
| activity | 交叉布局 activity 390 dark | 页面 | [cross-activity-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-390-dark-页面.png) |
| activity | 交叉布局 activity 390 dark | 主弹窗顶部 | [cross-activity-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-390-dark-主弹窗顶部.png) |
| activity | 交叉布局 activity 390 dark | 主弹窗底部 | [cross-activity-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-390-dark-主弹窗底部.png) |
| activity | 交叉布局 activity 768 light | 页面 | [cross-activity-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-768-light-页面.png) |
| activity | 交叉布局 activity 768 light | 主弹窗顶部 | [cross-activity-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-768-light-主弹窗顶部.png) |
| activity | 交叉布局 activity 768 light | 主弹窗底部 | [cross-activity-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-768-light-主弹窗底部.png) |
| activity | 点击验收 activity 768 dark | 页面 | [activity-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-0-页面.png) |
| activity | 点击验收 activity 768 dark | 新增活动 | [activity-768-dark-1-新增活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-1-新增活动.png) |
| activity | 点击验收 activity 768 dark | 新增活动选择器0 | [activity-768-dark-2-新增活动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-2-新增活动选择器0.png) |
| activity | 点击验收 activity 768 dark | 新增活动选择器1 | [activity-768-dark-3-新增活动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-3-新增活动选择器1.png) |
| activity | 点击验收 activity 768 dark | 新增活动选择器2 | [activity-768-dark-4-新增活动选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-4-新增活动选择器2.png) |
| activity | 点击验收 activity 768 dark | 新增活动底部 | [activity-768-dark-5-新增活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-5-新增活动底部.png) |
| activity | 点击验收 activity 768 dark | 编辑活动 | [activity-768-dark-6-编辑活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-6-编辑活动.png) |
| activity | 点击验收 activity 768 dark | 编辑活动选择器0 | [activity-768-dark-7-编辑活动选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-7-编辑活动选择器0.png) |
| activity | 点击验收 activity 768 dark | 编辑活动选择器1 | [activity-768-dark-8-编辑活动选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-8-编辑活动选择器1.png) |
| activity | 点击验收 activity 768 dark | 编辑活动选择器2 | [activity-768-dark-9-编辑活动选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-9-编辑活动选择器2.png) |
| activity | 点击验收 activity 768 dark | 编辑活动底部 | [activity-768-dark-10-编辑活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-10-编辑活动底部.png) |
| activity | 点击验收 activity 768 dark | 删除活动 | [activity-768-dark-11-删除活动.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-11-删除活动.png) |
| activity | 点击验收 activity 768 dark | 删除活动底部 | [activity-768-dark-12-删除活动底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/activity-768-dark-12-删除活动底部.png) |
| activity | 交叉布局 activity 1440 light | 页面 | [cross-activity-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-light-页面.png) |
| activity | 交叉布局 activity 1440 light | 主弹窗顶部 | [cross-activity-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-light-主弹窗顶部.png) |
| activity | 交叉布局 activity 1440 light | 主弹窗底部 | [cross-activity-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-light-主弹窗底部.png) |
| activity | 交叉布局 activity 1440 dark | 页面 | [cross-activity-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-dark-页面.png) |
| activity | 交叉布局 activity 1440 dark | 主弹窗顶部 | [cross-activity-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-dark-主弹窗顶部.png) |
| activity | 交叉布局 activity 1440 dark | 主弹窗底部 | [cross-activity-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-activity-1440-dark-主弹窗底部.png) |
| video | 首页筛选弹层 video 390 | 状态 | [filter-video-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-video-0.png) |
| video | 点击验收 video 390 light | 页面 | [video-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-0-页面.png) |
| video | 点击验收 video 390 light | 新增视频 | [video-390-light-1-新增视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-1-新增视频.png) |
| video | 点击验收 video 390 light | 新增视频选择器0 | [video-390-light-2-新增视频选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-2-新增视频选择器0.png) |
| video | 点击验收 video 390 light | 新增视频选择器1 | [video-390-light-3-新增视频选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-3-新增视频选择器1.png) |
| video | 点击验收 video 390 light | 新增视频选择器2 | [video-390-light-4-新增视频选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-4-新增视频选择器2.png) |
| video | 点击验收 video 390 light | 新增视频底部 | [video-390-light-5-新增视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-5-新增视频底部.png) |
| video | 点击验收 video 390 light | 编辑视频 | [video-390-light-6-编辑视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-6-编辑视频.png) |
| video | 点击验收 video 390 light | 编辑视频选择器0 | [video-390-light-7-编辑视频选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-7-编辑视频选择器0.png) |
| video | 点击验收 video 390 light | 编辑视频选择器1 | [video-390-light-8-编辑视频选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-8-编辑视频选择器1.png) |
| video | 点击验收 video 390 light | 编辑视频选择器2 | [video-390-light-9-编辑视频选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-9-编辑视频选择器2.png) |
| video | 点击验收 video 390 light | 编辑视频底部 | [video-390-light-10-编辑视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-10-编辑视频底部.png) |
| video | 点击验收 video 390 light | 删除视频 | [video-390-light-11-删除视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-11-删除视频.png) |
| video | 点击验收 video 390 light | 删除视频底部 | [video-390-light-12-删除视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-390-light-12-删除视频底部.png) |
| video | 交叉布局 video 390 dark | 页面 | [cross-video-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-390-dark-页面.png) |
| video | 交叉布局 video 390 dark | 主弹窗顶部 | [cross-video-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-390-dark-主弹窗顶部.png) |
| video | 交叉布局 video 390 dark | 主弹窗底部 | [cross-video-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-390-dark-主弹窗底部.png) |
| video | 交叉布局 video 768 light | 页面 | [cross-video-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-768-light-页面.png) |
| video | 交叉布局 video 768 light | 主弹窗顶部 | [cross-video-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-768-light-主弹窗顶部.png) |
| video | 交叉布局 video 768 light | 主弹窗底部 | [cross-video-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-768-light-主弹窗底部.png) |
| video | 点击验收 video 768 dark | 页面 | [video-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-0-页面.png) |
| video | 点击验收 video 768 dark | 新增视频 | [video-768-dark-1-新增视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-1-新增视频.png) |
| video | 点击验收 video 768 dark | 新增视频选择器0 | [video-768-dark-2-新增视频选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-2-新增视频选择器0.png) |
| video | 点击验收 video 768 dark | 新增视频选择器1 | [video-768-dark-3-新增视频选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-3-新增视频选择器1.png) |
| video | 点击验收 video 768 dark | 新增视频选择器2 | [video-768-dark-4-新增视频选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-4-新增视频选择器2.png) |
| video | 点击验收 video 768 dark | 新增视频底部 | [video-768-dark-5-新增视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-5-新增视频底部.png) |
| video | 点击验收 video 768 dark | 编辑视频 | [video-768-dark-6-编辑视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-6-编辑视频.png) |
| video | 点击验收 video 768 dark | 编辑视频选择器0 | [video-768-dark-7-编辑视频选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-7-编辑视频选择器0.png) |
| video | 点击验收 video 768 dark | 编辑视频选择器1 | [video-768-dark-8-编辑视频选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-8-编辑视频选择器1.png) |
| video | 点击验收 video 768 dark | 编辑视频选择器2 | [video-768-dark-9-编辑视频选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-9-编辑视频选择器2.png) |
| video | 点击验收 video 768 dark | 编辑视频底部 | [video-768-dark-10-编辑视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-10-编辑视频底部.png) |
| video | 点击验收 video 768 dark | 删除视频 | [video-768-dark-11-删除视频.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-11-删除视频.png) |
| video | 点击验收 video 768 dark | 删除视频底部 | [video-768-dark-12-删除视频底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/video-768-dark-12-删除视频底部.png) |
| video | 交叉布局 video 1440 light | 页面 | [cross-video-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-light-页面.png) |
| video | 交叉布局 video 1440 light | 主弹窗顶部 | [cross-video-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-light-主弹窗顶部.png) |
| video | 交叉布局 video 1440 light | 主弹窗底部 | [cross-video-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-light-主弹窗底部.png) |
| video | 交叉布局 video 1440 dark | 页面 | [cross-video-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-dark-页面.png) |
| video | 交叉布局 video 1440 dark | 主弹窗顶部 | [cross-video-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-dark-主弹窗顶部.png) |
| video | 交叉布局 video 1440 dark | 主弹窗底部 | [cross-video-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-video-1440-dark-主弹窗底部.png) |
| weread | 首页筛选弹层 weread 390 | 页面 | [filter-weread-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-weread-0.png) |
| weread | 首页筛选弹层 weread 390 | 周期 | [filter-weread-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-weread-1.png) |
| weread | 首页筛选弹层 weread 390 | 统计日期 | [filter-weread-2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-weread-2.png) |
| weread | 首页筛选弹层 weread 390 | 查看数值 | [filter-weread-3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-weread-3.png) |
| weread | 点击验收 weread 390 light | 页面 | [weread-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-390-light-0-页面.png) |
| weread | 点击验收 weread 390 light | 连接设置 | [weread-390-light-1-连接设置.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-390-light-1-连接设置.png) |
| weread | 点击验收 weread 390 light | 连接设置底部 | [weread-390-light-2-连接设置底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-390-light-2-连接设置底部.png) |
| weread | 交叉布局 weread 390 dark | 页面 | [cross-weread-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-390-dark-页面.png) |
| weread | 交叉布局 weread 390 dark | 主弹窗顶部 | [cross-weread-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-390-dark-主弹窗顶部.png) |
| weread | 交叉布局 weread 390 dark | 主弹窗底部 | [cross-weread-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-390-dark-主弹窗底部.png) |
| weread | 交叉布局 weread 768 light | 页面 | [cross-weread-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-768-light-页面.png) |
| weread | 交叉布局 weread 768 light | 主弹窗顶部 | [cross-weread-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-768-light-主弹窗顶部.png) |
| weread | 交叉布局 weread 768 light | 主弹窗底部 | [cross-weread-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-768-light-主弹窗底部.png) |
| weread | 点击验收 weread 768 dark | 页面 | [weread-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-768-dark-0-页面.png) |
| weread | 点击验收 weread 768 dark | 连接设置 | [weread-768-dark-1-连接设置.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-768-dark-1-连接设置.png) |
| weread | 点击验收 weread 768 dark | 连接设置底部 | [weread-768-dark-2-连接设置底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/weread-768-dark-2-连接设置底部.png) |
| weread | 交叉布局 weread 1440 light | 页面 | [cross-weread-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-light-页面.png) |
| weread | 交叉布局 weread 1440 light | 主弹窗顶部 | [cross-weread-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-light-主弹窗顶部.png) |
| weread | 交叉布局 weread 1440 light | 主弹窗底部 | [cross-weread-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-light-主弹窗底部.png) |
| weread | 交叉布局 weread 1440 dark | 页面 | [cross-weread-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-dark-页面.png) |
| weread | 交叉布局 weread 1440 dark | 主弹窗顶部 | [cross-weread-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-dark-主弹窗顶部.png) |
| weread | 交叉布局 weread 1440 dark | 主弹窗底部 | [cross-weread-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-weread-1440-dark-主弹窗底部.png) |
| devices | 首页筛选弹层 devices 390 | 类型 | [filter-devices-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-devices-0.png) |
| devices | 点击验收 devices 390 light | 页面 | [devices-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-0-页面.png) |
| devices | 点击验收 devices 390 light | 新增设备 | [devices-390-light-1-新增设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-1-新增设备.png) |
| devices | 点击验收 devices 390 light | 新增设备选择器0 | [devices-390-light-2-新增设备选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-2-新增设备选择器0.png) |
| devices | 点击验收 devices 390 light | 新增设备选择器1 | [devices-390-light-3-新增设备选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-3-新增设备选择器1.png) |
| devices | 点击验收 devices 390 light | 新增设备选择器2 | [devices-390-light-4-新增设备选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-4-新增设备选择器2.png) |
| devices | 点击验收 devices 390 light | 新增设备选择器3 | [devices-390-light-5-新增设备选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-5-新增设备选择器3.png) |
| devices | 点击验收 devices 390 light | 新增设备底部 | [devices-390-light-6-新增设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-6-新增设备底部.png) |
| devices | 点击验收 devices 390 light | 编辑设备 | [devices-390-light-7-编辑设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-7-编辑设备.png) |
| devices | 点击验收 devices 390 light | 编辑设备选择器0 | [devices-390-light-8-编辑设备选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-8-编辑设备选择器0.png) |
| devices | 点击验收 devices 390 light | 编辑设备选择器1 | [devices-390-light-9-编辑设备选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-9-编辑设备选择器1.png) |
| devices | 点击验收 devices 390 light | 编辑设备选择器2 | [devices-390-light-10-编辑设备选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-10-编辑设备选择器2.png) |
| devices | 点击验收 devices 390 light | 编辑设备选择器3 | [devices-390-light-11-编辑设备选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-11-编辑设备选择器3.png) |
| devices | 点击验收 devices 390 light | 编辑设备底部 | [devices-390-light-12-编辑设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-12-编辑设备底部.png) |
| devices | 点击验收 devices 390 light | 删除设备 | [devices-390-light-13-删除设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-13-删除设备.png) |
| devices | 点击验收 devices 390 light | 删除设备底部 | [devices-390-light-14-删除设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-390-light-14-删除设备底部.png) |
| devices | 交叉布局 devices 390 dark | 页面 | [cross-devices-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-390-dark-页面.png) |
| devices | 交叉布局 devices 390 dark | 主弹窗顶部 | [cross-devices-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-390-dark-主弹窗顶部.png) |
| devices | 交叉布局 devices 390 dark | 主弹窗底部 | [cross-devices-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-390-dark-主弹窗底部.png) |
| devices | 交叉布局 devices 768 light | 页面 | [cross-devices-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-768-light-页面.png) |
| devices | 交叉布局 devices 768 light | 主弹窗顶部 | [cross-devices-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-768-light-主弹窗顶部.png) |
| devices | 交叉布局 devices 768 light | 主弹窗底部 | [cross-devices-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-768-light-主弹窗底部.png) |
| devices | 点击验收 devices 768 dark | 页面 | [devices-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-0-页面.png) |
| devices | 点击验收 devices 768 dark | 新增设备 | [devices-768-dark-1-新增设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-1-新增设备.png) |
| devices | 点击验收 devices 768 dark | 新增设备选择器0 | [devices-768-dark-2-新增设备选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-2-新增设备选择器0.png) |
| devices | 点击验收 devices 768 dark | 新增设备选择器1 | [devices-768-dark-3-新增设备选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-3-新增设备选择器1.png) |
| devices | 点击验收 devices 768 dark | 新增设备选择器2 | [devices-768-dark-4-新增设备选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-4-新增设备选择器2.png) |
| devices | 点击验收 devices 768 dark | 新增设备选择器3 | [devices-768-dark-5-新增设备选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-5-新增设备选择器3.png) |
| devices | 点击验收 devices 768 dark | 新增设备底部 | [devices-768-dark-6-新增设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-6-新增设备底部.png) |
| devices | 点击验收 devices 768 dark | 编辑设备 | [devices-768-dark-7-编辑设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-7-编辑设备.png) |
| devices | 点击验收 devices 768 dark | 编辑设备选择器0 | [devices-768-dark-8-编辑设备选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-8-编辑设备选择器0.png) |
| devices | 点击验收 devices 768 dark | 编辑设备选择器1 | [devices-768-dark-9-编辑设备选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-9-编辑设备选择器1.png) |
| devices | 点击验收 devices 768 dark | 编辑设备选择器2 | [devices-768-dark-10-编辑设备选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-10-编辑设备选择器2.png) |
| devices | 点击验收 devices 768 dark | 编辑设备选择器3 | [devices-768-dark-11-编辑设备选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-11-编辑设备选择器3.png) |
| devices | 点击验收 devices 768 dark | 编辑设备底部 | [devices-768-dark-12-编辑设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-12-编辑设备底部.png) |
| devices | 点击验收 devices 768 dark | 删除设备 | [devices-768-dark-13-删除设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-13-删除设备.png) |
| devices | 点击验收 devices 768 dark | 删除设备底部 | [devices-768-dark-14-删除设备底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/devices-768-dark-14-删除设备底部.png) |
| devices | 交叉布局 devices 1440 light | 页面 | [cross-devices-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-light-页面.png) |
| devices | 交叉布局 devices 1440 light | 主弹窗顶部 | [cross-devices-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-light-主弹窗顶部.png) |
| devices | 交叉布局 devices 1440 light | 主弹窗底部 | [cross-devices-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-light-主弹窗底部.png) |
| devices | 交叉布局 devices 1440 dark | 页面 | [cross-devices-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-dark-页面.png) |
| devices | 交叉布局 devices 1440 dark | 主弹窗顶部 | [cross-devices-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-dark-主弹窗顶部.png) |
| devices | 交叉布局 devices 1440 dark | 主弹窗底部 | [cross-devices-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-devices-1440-dark-主弹窗底部.png) |
| wardrobe | 首页筛选弹层 wardrobe 390 | 筛选分类 | [filter-wardrobe-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-wardrobe-0.png) |
| wardrobe | 点击验收 wardrobe 390 light | 页面 | [wardrobe-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-0-页面.png) |
| wardrobe | 点击验收 wardrobe 390 light | 新增衣物 | [wardrobe-390-light-1-新增衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-1-新增衣物.png) |
| wardrobe | 点击验收 wardrobe 390 light | 新增衣物选择器0 | [wardrobe-390-light-2-新增衣物选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-2-新增衣物选择器0.png) |
| wardrobe | 点击验收 wardrobe 390 light | 新增衣物选择器1 | [wardrobe-390-light-3-新增衣物选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-3-新增衣物选择器1.png) |
| wardrobe | 点击验收 wardrobe 390 light | 新增衣物底部 | [wardrobe-390-light-4-新增衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-4-新增衣物底部.png) |
| wardrobe | 点击验收 wardrobe 390 light | 编辑衣物模拟衣物 | [wardrobe-390-light-5-编辑衣物模拟衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-5-编辑衣物模拟衣物.png) |
| wardrobe | 点击验收 wardrobe 390 light | 编辑衣物模拟衣物选择器0 | [wardrobe-390-light-6-编辑衣物模拟衣物选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-6-编辑衣物模拟衣物选择器0.png) |
| wardrobe | 点击验收 wardrobe 390 light | 编辑衣物模拟衣物选择器1 | [wardrobe-390-light-7-编辑衣物模拟衣物选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-7-编辑衣物模拟衣物选择器1.png) |
| wardrobe | 点击验收 wardrobe 390 light | 编辑衣物模拟衣物底部 | [wardrobe-390-light-8-编辑衣物模拟衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-8-编辑衣物模拟衣物底部.png) |
| wardrobe | 点击验收 wardrobe 390 light | 删除衣物模拟衣物 | [wardrobe-390-light-9-删除衣物模拟衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-9-删除衣物模拟衣物.png) |
| wardrobe | 点击验收 wardrobe 390 light | 删除衣物模拟衣物底部 | [wardrobe-390-light-10-删除衣物模拟衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-390-light-10-删除衣物模拟衣物底部.png) |
| wardrobe | 交叉布局 wardrobe 390 dark | 页面 | [cross-wardrobe-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-390-dark-页面.png) |
| wardrobe | 交叉布局 wardrobe 390 dark | 主弹窗顶部 | [cross-wardrobe-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-390-dark-主弹窗顶部.png) |
| wardrobe | 交叉布局 wardrobe 390 dark | 主弹窗底部 | [cross-wardrobe-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-390-dark-主弹窗底部.png) |
| wardrobe | 交叉布局 wardrobe 768 light | 页面 | [cross-wardrobe-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-768-light-页面.png) |
| wardrobe | 交叉布局 wardrobe 768 light | 主弹窗顶部 | [cross-wardrobe-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-768-light-主弹窗顶部.png) |
| wardrobe | 交叉布局 wardrobe 768 light | 主弹窗底部 | [cross-wardrobe-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-768-light-主弹窗底部.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 页面 | [wardrobe-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-0-页面.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 新增衣物 | [wardrobe-768-dark-1-新增衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-1-新增衣物.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 新增衣物选择器0 | [wardrobe-768-dark-2-新增衣物选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-2-新增衣物选择器0.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 新增衣物选择器1 | [wardrobe-768-dark-3-新增衣物选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-3-新增衣物选择器1.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 新增衣物底部 | [wardrobe-768-dark-4-新增衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-4-新增衣物底部.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 编辑衣物模拟衣物 | [wardrobe-768-dark-5-编辑衣物模拟衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-5-编辑衣物模拟衣物.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 编辑衣物模拟衣物选择器0 | [wardrobe-768-dark-6-编辑衣物模拟衣物选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-6-编辑衣物模拟衣物选择器0.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 编辑衣物模拟衣物选择器1 | [wardrobe-768-dark-7-编辑衣物模拟衣物选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-7-编辑衣物模拟衣物选择器1.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 编辑衣物模拟衣物底部 | [wardrobe-768-dark-8-编辑衣物模拟衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-8-编辑衣物模拟衣物底部.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 删除衣物模拟衣物 | [wardrobe-768-dark-9-删除衣物模拟衣物.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-9-删除衣物模拟衣物.png) |
| wardrobe | 点击验收 wardrobe 768 dark | 删除衣物模拟衣物底部 | [wardrobe-768-dark-10-删除衣物模拟衣物底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/wardrobe-768-dark-10-删除衣物模拟衣物底部.png) |
| wardrobe | 交叉布局 wardrobe 1440 light | 页面 | [cross-wardrobe-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-light-页面.png) |
| wardrobe | 交叉布局 wardrobe 1440 light | 主弹窗顶部 | [cross-wardrobe-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-light-主弹窗顶部.png) |
| wardrobe | 交叉布局 wardrobe 1440 light | 主弹窗底部 | [cross-wardrobe-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-light-主弹窗底部.png) |
| wardrobe | 交叉布局 wardrobe 1440 dark | 页面 | [cross-wardrobe-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-dark-页面.png) |
| wardrobe | 交叉布局 wardrobe 1440 dark | 主弹窗顶部 | [cross-wardrobe-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-dark-主弹窗顶部.png) |
| wardrobe | 交叉布局 wardrobe 1440 dark | 主弹窗底部 | [cross-wardrobe-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-wardrobe-1440-dark-主弹窗底部.png) |
| member | 首页筛选弹层 member 390 | 分类 | [filter-member-0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-member-0.png) |
| member | 首页筛选弹层 member 390 | 状态 | [filter-member-1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/filter-member-1.png) |
| member | 点击验收 member 390 light | 页面 | [member-390-light-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-0-页面.png) |
| member | 点击验收 member 390 light | 新增会员 | [member-390-light-1-新增会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-1-新增会员.png) |
| member | 点击验收 member 390 light | 新增会员选择器0 | [member-390-light-2-新增会员选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-2-新增会员选择器0.png) |
| member | 点击验收 member 390 light | 新增会员选择器1 | [member-390-light-3-新增会员选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-3-新增会员选择器1.png) |
| member | 点击验收 member 390 light | 新增会员选择器2 | [member-390-light-4-新增会员选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-4-新增会员选择器2.png) |
| member | 点击验收 member 390 light | 新增会员选择器3 | [member-390-light-5-新增会员选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-5-新增会员选择器3.png) |
| member | 点击验收 member 390 light | 新增会员选择器4 | [member-390-light-6-新增会员选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-6-新增会员选择器4.png) |
| member | 点击验收 member 390 light | 新增会员选择器5 | [member-390-light-7-新增会员选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-7-新增会员选择器5.png) |
| member | 点击验收 member 390 light | 新增会员底部 | [member-390-light-8-新增会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-8-新增会员底部.png) |
| member | 点击验收 member 390 light | 编辑会员 | [member-390-light-9-编辑会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-9-编辑会员.png) |
| member | 点击验收 member 390 light | 编辑会员选择器0 | [member-390-light-10-编辑会员选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-10-编辑会员选择器0.png) |
| member | 点击验收 member 390 light | 编辑会员选择器1 | [member-390-light-11-编辑会员选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-11-编辑会员选择器1.png) |
| member | 点击验收 member 390 light | 编辑会员选择器2 | [member-390-light-12-编辑会员选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-12-编辑会员选择器2.png) |
| member | 点击验收 member 390 light | 编辑会员选择器3 | [member-390-light-13-编辑会员选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-13-编辑会员选择器3.png) |
| member | 点击验收 member 390 light | 编辑会员选择器4 | [member-390-light-14-编辑会员选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-14-编辑会员选择器4.png) |
| member | 点击验收 member 390 light | 编辑会员选择器5 | [member-390-light-15-编辑会员选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-15-编辑会员选择器5.png) |
| member | 点击验收 member 390 light | 编辑会员底部 | [member-390-light-16-编辑会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-16-编辑会员底部.png) |
| member | 点击验收 member 390 light | 删除会员 | [member-390-light-17-删除会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-17-删除会员.png) |
| member | 点击验收 member 390 light | 删除会员底部 | [member-390-light-18-删除会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-390-light-18-删除会员底部.png) |
| member | 交叉布局 member 390 dark | 页面 | [cross-member-390-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-390-dark-页面.png) |
| member | 交叉布局 member 390 dark | 主弹窗顶部 | [cross-member-390-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-390-dark-主弹窗顶部.png) |
| member | 交叉布局 member 390 dark | 主弹窗底部 | [cross-member-390-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-390-dark-主弹窗底部.png) |
| member | 交叉布局 member 768 light | 页面 | [cross-member-768-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-768-light-页面.png) |
| member | 交叉布局 member 768 light | 主弹窗顶部 | [cross-member-768-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-768-light-主弹窗顶部.png) |
| member | 交叉布局 member 768 light | 主弹窗底部 | [cross-member-768-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-768-light-主弹窗底部.png) |
| member | 点击验收 member 768 dark | 页面 | [member-768-dark-0-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-0-页面.png) |
| member | 点击验收 member 768 dark | 新增会员 | [member-768-dark-1-新增会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-1-新增会员.png) |
| member | 点击验收 member 768 dark | 新增会员选择器0 | [member-768-dark-2-新增会员选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-2-新增会员选择器0.png) |
| member | 点击验收 member 768 dark | 新增会员选择器1 | [member-768-dark-3-新增会员选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-3-新增会员选择器1.png) |
| member | 点击验收 member 768 dark | 新增会员选择器2 | [member-768-dark-4-新增会员选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-4-新增会员选择器2.png) |
| member | 点击验收 member 768 dark | 新增会员选择器3 | [member-768-dark-5-新增会员选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-5-新增会员选择器3.png) |
| member | 点击验收 member 768 dark | 新增会员选择器4 | [member-768-dark-6-新增会员选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-6-新增会员选择器4.png) |
| member | 点击验收 member 768 dark | 新增会员选择器5 | [member-768-dark-7-新增会员选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-7-新增会员选择器5.png) |
| member | 点击验收 member 768 dark | 新增会员底部 | [member-768-dark-8-新增会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-8-新增会员底部.png) |
| member | 点击验收 member 768 dark | 编辑会员 | [member-768-dark-9-编辑会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-9-编辑会员.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器0 | [member-768-dark-10-编辑会员选择器0.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-10-编辑会员选择器0.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器1 | [member-768-dark-11-编辑会员选择器1.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-11-编辑会员选择器1.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器2 | [member-768-dark-12-编辑会员选择器2.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-12-编辑会员选择器2.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器3 | [member-768-dark-13-编辑会员选择器3.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-13-编辑会员选择器3.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器4 | [member-768-dark-14-编辑会员选择器4.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-14-编辑会员选择器4.png) |
| member | 点击验收 member 768 dark | 编辑会员选择器5 | [member-768-dark-15-编辑会员选择器5.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-15-编辑会员选择器5.png) |
| member | 点击验收 member 768 dark | 编辑会员底部 | [member-768-dark-16-编辑会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-16-编辑会员底部.png) |
| member | 点击验收 member 768 dark | 删除会员 | [member-768-dark-17-删除会员.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-17-删除会员.png) |
| member | 点击验收 member 768 dark | 删除会员底部 | [member-768-dark-18-删除会员底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/member-768-dark-18-删除会员底部.png) |
| member | 交叉布局 member 1440 light | 页面 | [cross-member-1440-light-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-light-页面.png) |
| member | 交叉布局 member 1440 light | 主弹窗顶部 | [cross-member-1440-light-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-light-主弹窗顶部.png) |
| member | 交叉布局 member 1440 light | 主弹窗底部 | [cross-member-1440-light-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-light-主弹窗底部.png) |
| member | 交叉布局 member 1440 dark | 页面 | [cross-member-1440-dark-页面.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-dark-页面.png) |
| member | 交叉布局 member 1440 dark | 主弹窗顶部 | [cross-member-1440-dark-主弹窗顶部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-dark-主弹窗顶部.png) |
| member | 交叉布局 member 1440 dark | 主弹窗底部 | [cross-member-1440-dark-主弹窗底部.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/cross-member-1440-dark-主弹窗底部.png) |
| 二级 | nested-390-light | 任务详情 | [nested-390-light-任务详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-任务详情.png) |
| 二级 | nested-390-light | 编辑任务 | [nested-390-light-编辑任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-编辑任务.png) |
| 二级 | nested-390-light | 新增明细 | [nested-390-light-新增明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-新增明细.png) |
| 二级 | nested-390-light | 编辑明细 | [nested-390-light-编辑明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-编辑明细.png) |
| 二级 | nested-390-light | 删除明细 | [nested-390-light-删除明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-删除明细.png) |
| 二级 | nested-390-light | 新增衣柜分类 | [nested-390-light-新增衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-新增衣柜分类.png) |
| 二级 | nested-390-light | 编辑分类模拟衣柜分类 | [nested-390-light-编辑分类模拟衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-编辑分类模拟衣柜分类.png) |
| 二级 | nested-390-light | 删除分类模拟衣柜分类 | [nested-390-light-删除分类模拟衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-删除分类模拟衣柜分类.png) |
| 二级 | nested-390-light | 书籍详情 | [nested-390-light-书籍详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-书籍详情.png) |
| 二级 | nested-390-light | 书籍笔记 | [nested-390-light-书籍笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-390-light-书籍笔记.png) |
| 二级 | nested-768-dark | 任务详情 | [nested-768-dark-任务详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-任务详情.png) |
| 二级 | nested-768-dark | 编辑任务 | [nested-768-dark-编辑任务.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-编辑任务.png) |
| 二级 | nested-768-dark | 新增明细 | [nested-768-dark-新增明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-新增明细.png) |
| 二级 | nested-768-dark | 编辑明细 | [nested-768-dark-编辑明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-编辑明细.png) |
| 二级 | nested-768-dark | 删除明细 | [nested-768-dark-删除明细.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-删除明细.png) |
| 二级 | nested-768-dark | 新增衣柜分类 | [nested-768-dark-新增衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-新增衣柜分类.png) |
| 二级 | nested-768-dark | 编辑分类模拟衣柜分类 | [nested-768-dark-编辑分类模拟衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-编辑分类模拟衣柜分类.png) |
| 二级 | nested-768-dark | 删除分类模拟衣柜分类 | [nested-768-dark-删除分类模拟衣柜分类.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-删除分类模拟衣柜分类.png) |
| 二级 | nested-768-dark | 书籍详情 | [nested-768-dark-书籍详情.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-书籍详情.png) |
| 二级 | nested-768-dark | 书籍笔记 | [nested-768-dark-书籍笔记.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/nested-768-dark-书籍笔记.png) |
| 延迟详情 | async-390 | 待办 height=358 | [async-待办-390.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/async-待办-390.png) |
| 延迟详情 | async-390 | 反馈 height=504 | [async-反馈-390.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/async-反馈-390.png) |
| 延迟详情 | async-768 | 待办 height=358 | [async-待办-768.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/async-待办-768.png) |
| 延迟详情 | async-768 | 反馈 height=504 | [async-反馈-768.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/async-反馈-768.png) |

## 验证边界与缺口

- 仅localhost mock；外部请求全部拦截；不代表真实后端、微信或App真机通过
- 主要新增弹窗打开/取消；并未逐页执行新增成功及删除成功闭环
- 未逐页覆盖空数据与加载失败重试
- 附件原生文件选择面板、真实上传、第三方解析/导入执行未验
- JavaScript pageerror主36矩阵断言通过；并未将所有console.error列为独立断言

## 实际视觉查看记录

通过view_image查看390主要页面/新增/编辑/删除确认的13张联系表（73个原始截图），768暗色主要页面/弹窗/底部的15张联系表（85个原始截图），以及修复后的异步待办390、反馈390/768原图。后续最终六布局联系表见visual-reviewed.json，未将只生成截图等同已视觉查看。

本组证据即时备份 `/tmp/qa-records-evidence/`，最终恢复至 `aio-life-mobile/artifacts/page-audit/records/`。仅本组目录操作，不清理其他组证据。

最终冻结：131个不同测试名称均有通过结果；主页面30个picker完整打开/取消。最终18张六布局联系表（216个原始弹窗顶部/底部截图）和5张筛选联系表（30个截图）全部通过view_image实际查看，具体清单见visual-reviewed.json。页面证据704张，加二级/异步额外证据另列。报告所引用截图存在性检查通过。

## 图标替换后代表性复核

20:53–20:55共享AppIcon/action-icons替换后，仅补390light设备页真实生活叶子入口→新增/关闭→编辑/关闭→删除确认/取消。测试`新SVG设备代表性复核 390 light`通过（1 passed，3.9s）；新增、编辑、删除和关闭按钮的SVG承载图像中心偏差均<2px，点击区44px，关闭/取消正常。四张原图已通过view_image实际查看，详见svg-devices.json。旧131项全页测试与全页截图属于本次图标替换前，不代表新图标全矩阵复验。最终132个不同测试有通过结果（131原矩阵+1代表性）。

```bash
npx playwright test tests/e2e/qa-records-all-pages.spec.js --workers=1 --output=test-results/page-audit/records-run --reporter=line --grep '新SVG设备代表性'
```

- [svg-devices-新增设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/svg-devices-新增设备.png)
- [svg-devices-编辑设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/svg-devices-编辑设备.png)
- [svg-devices-删除设备.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/svg-devices-删除设备.png)
- [svg-devices-关闭返回.png](/Users/hurry/Documents/GitHub/lys1313013/aio-life/aio-life-mobile/artifacts/page-audit/records/svg-devices-关闭返回.png)
