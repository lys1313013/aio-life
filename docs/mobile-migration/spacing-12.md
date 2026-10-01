# 12 首页、时迹与生活最终视觉复验

2026-10-01，H5 模拟接口；未进行真实业务写入。未改业务样式、共享组件或配置。

## 覆盖与入口

- 首页、时迹、生活：390、768、1440，浅色与深色。模拟登录后使用原生底栏真实点击。
- 首页新增时迹、时迹新增：同上六种组合，顶部与底部截图。
- 时间看板：生活菜单真实点击进入，六种组合；模拟学习60分钟、运动30分钟数据。
- 兼容时迹编辑路由：390、768浅深四种组合。仅该无菜单页使用 `uni.navigateTo`。
- 首页“管理快捷导航”真实跳转生活常用功能编辑弹窗，六种组合。
- 阅读关联选择与运动8行长编辑器：390浅色；长表单内部滚动，顶部日期与底部保存取消均可访问。

菜单 fixture 使用与候选 ID 匹配的有效 `menus` 树，避免将“暂无可用功能”误当视觉验证。全部接口在浏览器截获，仅模拟登录写入，无真实业务写入。

## 测量与原图判断

- 首页内容层 `dashboard-content ui-page-inset` padding 12px；390时 overview-grid x8、margin左右-4px，cell padding4px，第一张卡片x12、末张右缘378，净外缘12px。卡片 padding12px，标题从x24起，无24+12二次页面缩进。
- 768与1440保留四列概览；区块按断点双列/三列，运动每条记录独立可扫读，手机单列。桌面主体最大宽度居中属于容器几何约束，内部仍使用12px边距。
- 生活内容层 padding12px，搜索及菜单起点x12；时间看板MobilePage单层padding12px，统计卡片内边距12px。
- 390标准编辑器 panel x16、width358、y164、height572，content padding16px；form-card无二次padding，字段区块margin-bottom12px。
- 390八行运动长编辑器限高约832px，内部滚动；底部按钮保持在可视范围。原生底栏未盖住表单操作。
- 已通过 `view_image` 查看390浅首页、深时迹编辑器、768浅首页、390关联、深生活编辑、1440深看板、390真实形态统计、长表单顶部/底部及八图拼图。文本对比可读，无水平溢出；未发现本范围间距缺陷。

## 证据与验证

- 独立测试：`aio-life-mobile/tests/e2e/spacing-12.spec.js`。
- 最终完整验证：`npx playwright test tests/e2e/spacing-12.spec.js --workers=1 --output=artifacts/spacing-audit/12/final2-run`，8/8通过（34.4秒）。随后顶部截图显式复位scrollTop，长表单专项再次通过。
- 原图及逐图JSON：`aio-life-mobile/artifacts/spacing-audit/12/`，`contact-sheet.png`为整体拼图。
- 边界：该报告确认H5模拟接口下的视觉及交互，不代表真实后端、微信编译/模拟器/真机或App Vapor真机验证。
