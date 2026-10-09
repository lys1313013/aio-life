# 首页卡片核查与修复记录

日期：2026-10-09。范围：Web、Mobile 工作区的首页代码、文档及模拟接口回归。首次核查发现的 HOME-R01～R04、HOME-I01～I03 已补齐；实现与平台实测分别记录。保留 Mobile 已有的时迹明细行高修改。

共同业务要求统一维护在 [首页功能说明](../首页功能说明.md)、[今日时迹卡片设计](../今日时迹卡片设计.md)、[五张业务卡片需求](../首页新增业务卡片需求.md)。各端文档引用根项目，不重复维护业务规格。

## 核查结论与修复

原有概览点击刷新、微信读书空白刷新、整页下拉、设置、排序、编辑和分页均已存在。缺口集中在持续停留时的数据调度、普通内容与五张业务卡片的正常头部空白刷新，以及标题导航、待办日期和 GitHub 访问。Web 快捷导航也缺少头部空白刷新，本轮同时补齐。

| 编号 | 实现 | 验证重点 |
| --- | --- | --- |
| HOME-R01 | 概览读取每次详情的 refreshInterval（秒）；无效／非正／缺失值关闭调度；更新间隔替换原任务 | 300／600 秒、动态间隔、请求未完成不重复、失败恢复、停用、旧 finally 不重建任务 |
| HOME-R02 | 时迹 300s、运动 600s、待办 1800s、闪念／最近提交 3600s；关闭、锁定或未绑定的区域不调度 | 可控时钟验证真实页面请求次数；本地分钟时钟与数据请求分开 |
| HOME-R03 | Mobile 普通内容与目标／纪念日／阅读／会员／观影使用 HomeCardHeader 空白刷新；Web 快捷导航使用 CardHeader | 单卡请求与失败重试只更新本卡；已有内容和高度保留；标题、加号、条目、完成、拖动互不触发；H5 Enter／Space |
| HOME-R04 | onHide／onUnload、H5 可见性和账号切换使旧请求失效；暂停调度，返回按到期、失败及 revision 补刷；锁过期清除敏感数据 | 隐藏无请求、恢复只补刷一次、短返回保留分页、写入后局部更新、旧响应不写回；后台请求不弹解锁窗口 |
| HOME-I01 | 普通标题进入时迹／待办／闪念／运动业务；最近提交标题访问公开绑定的 GitHub 主页 | 标题导航不先刷新首页，不绕过二级锁 |
| HOME-I02 | 待办显示起止时间，兼容空日期、单边日期和 ISO／空格格式 | 无日期／仅开始／仅结束／两者、长标题、手机／平板／桌面深浅主题 |
| HOME-I03 | 点击提交弹出完整摘要，有 commitUrl 时可访问提交；无链接时只查看摘要 | 模拟主页与单次提交访问；无链接降级；分页与排序误触回归 |

五张业务卡片、快捷导航与微信读书最近阅读没有新增周期：Web 原先也没有这些卡片的共同周期。它们继续使用首次加载、手动刷新、写入失效和返回时效检查，不能把“60 分钟返回时效”描述为前台定时查询。

Web 快捷导航的读取合并同一请求，失败保留已有导航，编辑／保存时禁用刷新；保存、清空和退出重置使旧读取失效，避免迟到响应覆盖新顺序或恢复旧账号数据。

## 实现注意事项

- 概览详情、内容区和分页使用页面 generation、区域版本与写入 revision；锁过期会撤下卡面数据与相关编辑内容。请求先检查首页及业务菜单锁，响应写回前再检查；后台读取使用静默锁处理。
- 顶部刷新没有常驻图标，使用独立空白按钮；标题与操作按钮位于其上层。普通标题按钮显式使用同行布局；刷新反馈不增加布局高度。
- GitHub 主页来自 userbinds/list 的公开用户名，没有读取平台凭据。外链按 H5 新窗口、微信复制链接、App 外部打开适配；平台验证边界见下表。
- 浏览器隐藏时目标编辑草稿保留，真正离页、账号变化和权限失效仍清除；其他业务编辑器的后台草稿行为未单独验收。
- H5 回归发现 uni scroll-view 挂载 nextTick 晚于卸载时会写空 DOM 引用。现有固定版本 H5 补丁脚本补上两个方向的空引用保护，并执行安装包真实函数回归；没有关闭 Vapor，也不提交 node_modules。
- 核查中保留了已有功能，未取消编辑、分页、固定排序或图表。时迹明细的已有行高调整保留。

## 本轮验证

| 范围 | 本轮结果 |
| --- | --- |
| Mobile 单元与契约 | npm test：294 项通过，含间距／排版、周期调度、真实 loadSection 竞态、单日查询静默锁与三个 H5 构建入口的滚动生命周期 |
| Mobile H5 模拟接口 | 本轮生产构建，四个首页专项文件合计 78 项通过；覆盖周期、恢复、单卡刷新、锁定／锁到期、访问、日期降级、编辑、分页、排序和高度 |
| Mobile 视觉 | 已查看 390／768／1440px 深浅主题的刷新与长文本截图，以及首次 loading → 内容、局部刷新；高度回归另覆盖 360／700px、空／多条、失败重试 |
| Web 组件与调度 | 快捷导航组件／store 5 项、业务卡片 12 项、首页调度 9 项，共 26 项通过；本轮改动文件 ESLint／格式检查通过 |
| 微信编译／包体 | 构建与官方本地编译体积检查通过；主包 1443.13 KB，低于 1600 KB 工程预算；各包均低于 2048 KB 硬上限 |
| 真实后端与外链服务 | 未联调；GitHub 访问使用模拟落地页，未将模拟结果当作线上服务验证 |
| 微信模拟器／真机、App | 未执行；微信复制链接和 App 外部打开仅有源码／编译检查 |
| 发布 | 未上传、未发布 |

所有 E2E 均使用明确的模拟数据、可控时钟和延迟／失败接口，没有向线上账户写测试数据。因 5180 已有服务，独立预览使用 5181；预览产物由本轮代码构建，临时配置、日志及截图只保存在忽略目录 artifacts/home-refresh/。修复后的相关阶段重新执行，没有把历史通过数当作当前证据。

初次键盘验证发现 uni 按钮不会自动将 Enter／Space 转成点击，已补显式处理并复验。Web 首页调度测试曾因未隔离微信读书组件而加载真实路由模块，已补齐组件替身；该卡自身能力仍由专用测试负责。实际查看运行中的 Web 首页及快捷导航编辑态后取消编辑，未保存线上修改。

提交前完整统一验证仍使用 Mobile 的 npm run test:commit。本轮没有提交、推送、上传或发布。

## 源码与回归入口

| 范围 | 入口 |
| --- | --- |
| Mobile 首页与接口 | [index.uvue](../../aio-life-mobile/src/pages/home/index.uvue)、[dashboard.ts](../../aio-life-mobile/src/services/dashboard.ts) |
| Mobile 周期与局部刷新 | [refresh-scheduler.ts](../../aio-life-mobile/src/pages/home/services/refresh-scheduler.ts)、[HomeCardHeader.uvue](../../aio-life-mobile/src/components/HomeCardHeader.uvue)、[DashboardSection.uvue](../../aio-life-mobile/src/components/DashboardSection.uvue) |
| Mobile 业务卡片与锁检查 | [BusinessCards.uvue](../../aio-life-mobile/src/pages/home/BusinessCards.uvue)、[WereadRecentCard.uvue](../../aio-life-mobile/src/pages/home/WereadRecentCard.uvue) |
| Mobile 页面回归 | [home-refresh-parity.spec.js](../../aio-life-mobile/tests/e2e/home-refresh-parity.spec.js)、[home-loading-height.spec.js](../../aio-life-mobile/tests/e2e/home-loading-height.spec.js)、[home-business-cards.spec.js](../../aio-life-mobile/tests/e2e/home-business-cards.spec.js)、[home-card-sort.spec.js](../../aio-life-mobile/tests/e2e/home-card-sort.spec.js) |
| Mobile 调度与请求竞争 | [home-refresh-scheduler.test.mjs](../../aio-life-mobile/tests/home-refresh-scheduler.test.mjs)、[home-section-refresh.test.mjs](../../aio-life-mobile/tests/home-section-refresh.test.mjs) |
| H5 组件生命周期 | [patch-uni-h5-picker.cjs](../../aio-life-mobile/scripts/patch-uni-h5-picker.cjs)、[uni-scroll-lifecycle.test.mjs](../../aio-life-mobile/tests/uni-scroll-lifecycle.test.mjs) |
| Web 周期基准 | [home-content.vue](../../aio-life-front/apps/web-antd/src/views/dashboard/home/home-content.vue) |
| Web 快捷导航 | [QuickNavSection.vue](../../aio-life-front/apps/web-antd/src/views/dashboard/home/components/QuickNavSection.vue)、[quick-nav.ts](../../aio-life-front/apps/web-antd/src/store/quick-nav.ts)、[QuickNavSection.test.ts](../../aio-life-front/apps/web-antd/src/views/dashboard/home/components/QuickNavSection.test.ts)、[quick-nav.test.ts](../../aio-life-front/apps/web-antd/src/store/quick-nav.test.ts) |

## 文档归属

共同今日时迹设计从 front 历史规格提取到根项目，旧路径保留索引。根项目维护业务范围、刷新、权限、布局和跨端验收；front、mobile 的 AGENTS.md／README 维护各自实现与构建入口。其他 front 专属文档不因目录位置而一律迁移。

