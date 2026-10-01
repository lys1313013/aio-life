# Mobile 逐页点击与弹窗检查

日期：2026-10-01。本轮H5页面展示与弹窗验收完成：48个注册页面均有逐页证据，47个从业务入口进入、1个兼容路由单独验证。三组分批执行并修复所发现问题；后续并发目录/SVG改动的代表性复验范围另记。3,578条截图及JSON引用已校验，无缺失。

用户要求：从页面入口逐个点击，特别检查弹窗与图标的实际展示。真实后端写入与原生真机不属于本次通过结论。

## 执行约定

- 三个独立 GPT-6.1 sol 子 Agent 分组检查，主 Agent 复核截图、问题与遗漏。
- 从登录、底栏、生活目录、我的及管理入口真实点击进入；共享页面的 query 模式分别进入检查。
- 每页逐一打开新增、编辑、详情、筛选、选择器、确认、附件、导入等适用弹窗，记录入口路径、点击动作、截图和结果。
- 重点检查 390px 手机及 768px 平板、深浅主题：弹窗居中、屏幕边界、长内容内部滚动、底部按钮可达、键盘/底栏遮挡、关闭/取消/确认及错误提示。
- 每张关键截图实际打开检查，不能只断言 DOM 或几何尺寸。API 模拟仅提供安全测试数据，所有界面操作均通过页面点击完成；真实账号仅允许只读展示，不做写入。
- 发现问题按页面或公共组件归属修复并重新点击验证。微信/App 真机证据另记，不冒称全部平台已通过。

## 派发

| 分组 | Agent | 文件边界 | 状态 |
|---|---|---|---|
| A 记录与物品 | /root/qa_records_pages | tasks、records、goods、member；qa-records* 测试与独立报告 | 已完成 H5 展示检查 |
| B 财务与社交 | /root/qa_domains_pages | finance、coding、relationship、messages、mcp、vault；qa-domains* | 已完成 H5 展示检查 |
| C 基础与管理 | /root/qa_platform_pages | 首页/时迹/生活/我的/认证/分类/管理/人格/关于；qa-platform* | 已完成 H5 展示检查 |
| 统筹复核 | 主 Agent | 公共组件、测试证据覆盖、构建、此表 | 已完成 |

## 页面清单

以下48项为物理路由基线，共享页面的业务模式与弹窗在分组报告中展开。

| 页面 | 分组 | 点击检查状态 |
|---|---|---|
| `pages/home/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/time/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/life/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/time/edit` | C / qa_platform_pages | 已检查；无菜单的兼容路由，以 navigateTo 单独验证 |
| `pages/login/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/settings` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/bindings` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/preferences` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/security` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/profile/notifications` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/time/dashboard` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/tasks/todo` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/tasks/goals` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/finance/index` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/finance/income` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/finance/expense` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/finance/import` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/finance/cards` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/categories/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/admin/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/admin/directory` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/records/notes` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/anniversary` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/milestones` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/honor` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/feedback` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/library` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/exercise` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/categories` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/activity` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/video` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/records/weread` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/mcp/index` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/relationship/index` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/messages/index` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/vault/index` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/coding/github` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/coding/leetcode` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/coding/csdn` | B / qa_domains_pages | 已检查；6布局，见 B 组逐层证据 |
| `pages/member/index` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/about/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/personality/mbti` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/personality/cbti` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/personality/external` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/auth/index` | C / qa_platform_pages | 已检查；6布局，见 C 组逐层证据 |
| `pages/goods/devices` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |
| `pages/goods/wardrobe` | A / qa_records_pages | 已检查；6布局，见 A 组逐层证据 |

## 已发现问题与处理

| 问题 | 证据 | 处理状态 |
|---|---|---|
| 公共图标按钮内容贴左，关闭、添加、编辑和删除图标偏离按钮中心 | 主 Agent 从生活→设备实际点击新增及删除确认，观察修复前后；子 Agent 复查模拟数据截图 | 已修 `MobileButton.uvue` 的 flex 对齐，各组截图复查通过 |
| 返回箭头贴左 | `PageHeader` 截图及返回按钮几何检查 | 已修 flex 对齐，44×44 点击区内中心偏移为0 |
| 待办等平板内容区缩得过窄 | `records/todo-768-dark-8-删除列.png`，修复前主体约292px | 已修15页根容器宽度与盒模型，6布局复验通过 |
| 异步详情加载后仍保留加载时的小弹窗高度 | 延迟800ms的待办/反馈详情 | WEB观察内容尺寸，原生通过contentKey重新测高；修后分别358/504px |
| 注册/忘记密码在H5登录页缺少入口 | 从登录页无法点击进入，而路由存在 | 已移出微信条件块，实际入口点击复验 |
| 删除确认上浮过远 | 财务支出390与银行卡768截图，固定200px预估高度大于实际内容 | 测量实际高度贴近触发按钮；支出390深色及银行卡768深色截图复核，间距约4–5px |
| 触摸精确滑动整数格后，视觉值与确认值不同 | 消息频道滑动34px，视觉私聊，确认后仍消息 | 已为固定版本补齐snap通知，桌面和触摸模式实际回归通过 |
| 时迹编辑器删除图标纵向偏上11px | 手机编辑器图标与按钮几何 | 已补flex居中，修后dx=0、dy=0，六布局通过 |
| 选择器取消后迅速关闭父窗或重新打开会触发过期关闭回调 | 消息频道picker快速取消/关闭/重开 | 已补节点存在和可见状态检查，2个实际页面回归与6项运行时代码测试通过 |
| 深色页面受通用page类污染，详情出现重复关闭按钮 | 记录组深浅色截图 | 已收紧根节点类名并统一关闭入口，复验通过 |
| 管理配置无效JSON直接显示英文异常 | 系统配置输入非法JSON | 已改中文错误，6项管理契约测试通过 |
| 账单导入初始化失败后无有效重试入口 | B组读取失败恢复用例 | 已接入页面刷新与错误重试，开始初始化时清旧错误，专项复验见B组报告 |
| 离开消息页仍保留新建/重命名草稿与管理查询值 | B组离页返回回归 | 已在页面隐藏时清理相关状态，专项复验见B组报告 |
| 原生日历取消操作被误判为遮罩层级失败 | 点击原生日历后，脚本误操作残留的 uni picker 遮罩 | 已修测试流程，产品遮罩无需因此修改 |

以上记录本轮实测发现。图标位置、尺寸、点击区和重复关闭入口均纳入逐图检查。

## 结果索引

- [记录与物品报告](./page-audit-records.md)：16物理页、18模式，131个独立用例分批最终通过，另1项新SVG设备复核通过。
- [基础与管理报告](./page-audit-platform.md)：20物理页、34路由/query组合，53个独立用例分批最终通过，另1项新SVG代表性复核通过。
- [财务与社交报告](./page-audit-domains.md)：12物理页，93个独立用例分批最终通过，另两种触摸上下文断言通过。
- [可筛选截图图集](../../aio-life-mobile/artifacts/page-audit/index.html)：按分组、页面、宽度或主题筛选；包含过程截图和修复复验，结论以分组报告为准。
- 截图、覆盖JSON和验证日志归档到 Mobile Git 忽略目录 `artifacts/page-audit/`，避免被 Playwright 后续运行清理。旧迁移测试结果不替代本轮逐个点击检查。

## 并发修改与证据版本

20:53–20:55，共享工作区另有图标替换代码写入，统一改用AppIcon与SVG图标目录。资源落盘前曾出现action-icons.json导入失败，导致B组后续测试中断；资源创建后补跑受影响项目。同期生活目录授权读取与分组展示也有变化，补跑使用完整授权菜单树并点击当前生活叶子入口。原完整页面矩阵与大部分截图早于这批替换，替换后的代表性图标复核范围由各分组另记，不将旧截图冒称最终图标版本。根Agent已在资源就绪后重新运行94项测试、H5与微信构建，均通过。

## 构建与边界

- 最终 `npm test`：95/95通过；`npm run build` 和 `npm run build:weixin` 均构建成功；`git diff --check`通过。日志随图集归档。
- 实际点击在H5页面执行，后端与第三方使用模拟数据；真实账号只读复核，没有写入、删除或发送。
- 47个页面从业务入口点击；`pages/time/edit` 没有业务菜单，是兼容路由，单独直接导航测试。业务日常入口使用共享时迹弹窗，已从首页/时迹实际打开。
- 手机、平板、桌面宽度为390/768/1440，分别检查深浅主题。后续深层补漏和专项回归的宽度见分组报告，不宣称每一细项都跑满六布局。
- 微信构建成功不等同真机通过。本轮未完成微信/App真机、系统文件与相册面板、真实第三方集成，以及逐页所有CRUD和网络异常组合；各组保留未验项。
