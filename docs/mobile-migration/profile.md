# 个人设置、密码库与共享集成

负责人：主 Agent。日期：2026-10-01。此表为源码与本地模拟验证记录，不表示真实后端或真机验收。

| 功能 | Mobile | 已接入操作及接口 |
|---|---|---|
| 修改密码 | `pages/profile/preferences?section=password` | 旧密码、新密码、确认；POST `/auth/change-password`；保留密码原始空白，失败保留表单 |
| 菜单显示 | `preferences?section=menus` | 层级隐藏继承、显示开关、保存、确认恢复默认；GET/PUT/DELETE `/menu/preferences`；大整数ID始终字符串 |
| 菜单锁 | `pages/profile/security` | 菜单树与锁、设置/修改二级密码、邮件验证码找回；`/auth/secondary-password`、`/auth/secondary-lock/menus`、`/auth/reset-secondary-password`；真实业务2001触发居中解锁，成功原请求只重试一次 |
| API Key | `preferences?section=keys` | 列表掩码、备注、有效期生成、一次性完整密钥复制、确认删除；`/api-key/list`、`generate`、`/{id}`；离页清除生成密钥 |
| 大模型 | `preferences?section=llm` | 预设与自定义、模型、接口、密钥、新建/编辑/删除/设为默认；`/llm/key`；编辑密钥为空时省略字段保留原值 |
| 通知 | `pages/profile/notifications` | 业务渠道偏好、飞书配置、启停、接收人、测试与删除；`/notification/preferences`、`/notification/channels/feishu`；隐藏业务偏好随保存保留，凭证留空不覆盖 |
| 系统 | `preferences?section=system` | 跟随系统/浅色/深色、确认清缓存并返回首页；保留登录与主题 |
| 密码库 | `pages/vault/index` | 列表/搜索/分类、解锁/手动锁定、详情、加密CRUD、收藏、复制/显示、密码生成器；`/password/list`、`categories`、`/{id}`；离页和切换账号清除内存明文，闲置30分钟锁定 |
| 关于 | `pages/about/index` | 客户端名称、用途、实际包版本；无需登录 |
| 管理目录 | `pages/admin/directory` | 从服务端授权菜单形成入口；我的仅管理员展示管理目录；后端继续鉴权 |

## 兼容性及安全状态

- 密码库派生与 Web 既有格式兼容：PBKDF2 SHA256、100000 轮、16字节、32字节salt；SM4通过同一gm-crypto库和参数读写。库对模式参数的实际行为依赖原格式，不能把参数文字 `GCM` 当作已提供认证加密的证明，本次未迁移既有密文格式。
- Web Crypto和微信安全随机数用于新salt和密码生成；缺少安全随机数的平台明确拒绝生成，不降级为Math.random。已补Android SecureRandom与iOS SecRandomCopyBytes的UTS桥接源码；仍须匹配HBuilderX验证App联编和真机。
- 菜单锁只在服务端返回2001、且账号未切换时恢复同一请求；普通网络失败不会自动重发写操作。
- 附件使用Authorization header，保留已绑定ID；Web/微信分别选择文档，App文档选择器尚未接入。图片选择各端使用uni.chooseImage。选择器返回前切换账号会拒绝上传。
- `HOME-02` Web 工作台源码为Vben静态演示项目/动态/待办数据，无业务读写API，移动端映射到实际首页；不向生产界面添加示例业务记录。
- 首页补关注待办完成/取消完成及编辑、置顶闪念编辑、运动快捷新增；复用业务页查询参数及接口，未另造一套表单。消息入口在生活授权目录和我的均可进入。

## 验证

- `npm test` 中 preferences 2 项及 vault-crypto 3 项通过；密码密文与Node PBKDF2/Web gm-crypto对照，UTF8中文/emoji/代理项与TextEncoder一致。
- `tests/e2e/preferences.spec.js`：9 项已分批通过，含390/768/1440深浅主题居中弹窗、密码校验/失败保留/重试、LLM空密钥保留、菜单锁2001解锁重试、长ID保存、通知凭证保留。
- `tests/e2e/vault.spec.js`：1 项通过，使用明确模拟密文，验证解密、编辑失败恢复、密文提交、离页重新锁定。
- 未向真实账号修改密码、生成密钥、发送通知或保存密码库记录；真实后端、微信/App设备的功能验证单独记账。

菜单锁收尾：统一导航及 App 隐藏取消等待，旧页面锁响应不跨页重新弹出；弹窗隐藏、换账号或卸载清除二级密码。新增离页/返回回归通过。附件上传/下载 401 返回登录，离页后的锁失败不打开新页面弹窗。
