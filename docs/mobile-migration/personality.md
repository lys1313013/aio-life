# Mobile 人格测试、认证与时间看板迁移

## 操作盘点

- MBTI：POST `/mbti/test` 创建 devil.ai 外部测试；GET `/mbti/test/{testId}` 检查，测试完成 POST `/mbti/result` 自动保存（失败手动重试）；GET `/mbti/results` 历史、GET/DELETE `/mbti/result/{id}` 详情/删除；预测、意识/影子特质顺序、匹配与原结果页完整展示。未完成测试按账号ID保存，离页暂停轮询，返回继续检查。此测试源是外部网站，不能伪造本地问卷。
- CBTI：GET `/cbti/questions,personalities`；每题选择、前后切换/题号跳转、完整回答校验，隐藏题 drink=coffee 时出现 drinkAttitude，POST `/cbti/test`；结果人格/相似度/15维和匹配详情、文字分享、海报；历史详情/删除、人格库浏览。
- CBTI 管理：GET/POST `/cbti/admin/personalities`、PUT/DELETE `/{id}`；code/name/motto/color/vector/description/strengths/weaknesses/techStack/spirit/isSpecial/imageObject；15项向量0/1/2 L/M/H、JSON编辑；POST `/{code}/image` 图片上传，该接口返回 imageObject/imageUrl，无file.id，不能复用统一附件上传契约。
- 注册：POST `/auth/sendEmailCode`、POST `/auth/register`（username/password/email/code）。找回：POST `/auth/sendResetPasswordCode`、POST `/auth/resetPassword`（email/password/code）。密码隐藏、确认相等、验证码等待、局部busy/失败保留；不自动登录。
- 时间看板：日/周/月与前后时段、日期picker、分类多选/父子匹配；本期和前期同类总分钟对比、卡片统计、分类/类型/每日/趋势复用 TimeStatistics；分类含隐藏数据供历史分类匹配，隐藏分类不做追踪卡片。

入口：`pages/personality/mbti`、`cbti`、`external`，`pages/auth/index?mode=register|reset`，`pages/time/dashboard`。页面登记和导航由主Agent负责。

海报使用 uni-app x CanvasContext API，依据 [createCanvasContextAsync](https://doc.dcloud.net.cn/uni-app-x/api/create-canvas-context-async.html) 与 [canvasToTempFilePath 兼容表](https://doc.dcloud.net.cn/uni-app-x/api/canvas-to-temp-file-path.html)；App 无 canvasToTempFilePath，使用 CanvasContext.toDataURL 后写图片。平台构建与真机分别核验。

## 验证结果与边界

`tests/personality-contract.test.mjs` 6项通过（字符串ID、MBTI结果、完整CBTI/咖啡隐藏题、15维向量、认证、分享与上传响应）。`tests/personality-web.mjs` 实际 Chrome 模拟 API 专项通过：390/768/1440 深浅主题 CBTI 答题、隐藏题、完整提交、结果、Canvas 海报生成；找回密码不一致拒绝发送、失败保留与快速修改确认密码提交。截图在 `aio-life-mobile/test-results/personality/`，已检查手机深色、平板浅色和桌面深色结果布局。

MBTI 外部 devil.ai 实际连通、内嵌 WebView 与微信业务域名白名单未验证；CBTI 管理上传/真实后端权限及App/微信海报保存仍需实测。海报已保留人格图片、15维、匹配度与文字；二维码补齐记录见下文。时间看板复用既有统计和新增 MiniChart，真实时区边界仍由集成验收核对。以上模拟证据不等同真机或真实后端验收。


## CBTI海报二维码补齐

对照Web `cbti-setting.vue:getSiteUrl`，内容为分享站点 origin + `/profile?tab=cbti`，不编码人格结果/用户信息。`CbtiPoster` 统一该链接；Web使用传入当前origin，原生使用 `VITE_WEB_SITE_URL` 或项目已有站点 `https://aiolife.top`。可配置站点必须实际部署Web该路径。

复用项目已安装 `qrcode-terminal` 的 MIT QRCode for JavaScript 编码器，整理为自包含 `services/personality/poster-qr.ts` 并保留授权，无新增包、Node/DOM/网络依赖。M级纠错、UTF8 URL百分号编码、四模块静区、整数模块、Web相同橙色；直接Canvas绘制，海报高度1250px以保留独立扫码区域与提示。

`tests/poster-qr.test.mjs` 3项通过：链接一致与非法地址拒绝、不同长度/中文URL矩阵与既有标准编码逐点一致、绘制像素及静区。CbtiPoster SFC 编译通过，personality-web重新执行6种布局生成海报和认证流程全部通过。App/微信二维码海报保存仍需真机核验。

额外真实解码证据：模拟交互导出原始Canvas PNG `test-results/personality/390-light-poster.png`，macOS系统 Vision `VNDetectBarcodesRequest(.qr)` 解码得到 `http://127.0.0.1:5180/profile?tab=cbti`，与Web算法的当前origin内容一致。无需安装识别依赖；这验证了二维码实际可读，不仅矩阵源码一致。
