# 11 平台、设置与人格页面间距复验

验证日期：2026-10-01。环境：H5 开发服务器 127.0.0.1:5180，Chrome Playwright，所有 API 均由模拟接口拦截；不涉及生产写入、提交、微信或 App 真机。

## 范围与操作

独立测试：`aio-life-mobile/tests/e2e/spacing-11.spec.js`，证据：`aio-life-mobile/artifacts/spacing-audit/11/`（PNG 与同名几何 JSON）。

通过实际账号输入/登录、原生底栏“我的”与“生活”、业务菜单进入：profile/index、settings、bindings、preferences 五种模式（password/menu/keys/llm/system）、security、notifications、login、auth 注册/重置、categories 个人/管理、admin/directory、admin/index 九 kind、about、personality mbti/cbti/external，合计 15 物理页（共享 preferences、admin、auth、categories 按物理路由去重）。

390px 手机深浅交替；768px 与 1440px 额外覆盖 profile、preferences/API Key、admin/users 和代表弹窗。设置表单、管理新增/编辑、人格详情弹窗逐个进入、滚至底部并关闭/取消，未提交业务数据。

平台公共 fixture 的菜单树 ID 与生活候选 ID 不一致，导致生活“暂无可用功能”；仅在独立 spec 覆盖 `menu/preferences` 为与 candidates 匹配的有效树，未改公共 fixture。

## 观察与测量

已实际查看手机平台截图拼图，以及登录/注册、个人分类、CBTI 长详情底部、768 管理、1440 preferences 原图。表单和卡片内容未二次缩进；个人分类两张真实形态卡片间距清晰；管理筛选在手机保持纵向布局，日志日期双列均分；长菜单编辑和人格详情内部可滚动，关闭操作可正常执行。

- 手机内容外缘 x=12，width=366；卡片 padding=12px，卡片间纵向区块=12px。
- toolbar 与行 gap=8px；compact 筛选 FormField margin=0，未发现字段 margin 与行 gap 重叠。
- 模态内容 padding=16px；390 菜单编辑 panel x=16、width=358，height=852、顶部/底部各24px，内部内容可滚到底部。
- 768 模态 width=520、居中 x=124；1440 内容在公共宽度容器内，保留各侧12px内边距。
- 已采集 navigation-button 与 icon-button 点击区域均至少44px；所有截图入口无横向溢出。

外部测试 web-view 是第三方模拟 HTML，页面返回导航纳入检查；其内部内容不是本客户端间距约束。登录使用自己的绿色视觉主题，深浅模拟媒体切换下仍是该主题，不将文件名里的 dark 认作已呈现暗色登录。

## 结果与边界

首轮完整交互测试：3 passed（54.1s），83 张截图。随后增加 card/modal/compact/44px 数值断言的重跑曾遇机器 `ENOSPC` 截图写入失败；只删除本任务生成的临时拼图，并复用既有证据执行量化复验：3 passed（36.0s），卡片12、弹窗16、compact margin=0与44px点击区断言全部通过。业务源码未发现需要额外修改的间距问题。

复现命令：`npx playwright test tests/e2e/spacing-11.spec.js --workers=1`。低磁盘空间仅复用截图时可设置 `SPACING11_REUSE_EVIDENCE=1`；默认重新截图。

本报告确认 H5 模拟 API 页面视觉与交互；不代表真实后端联调、微信编译、微信模拟器、微信/App 真机或发布验收。
