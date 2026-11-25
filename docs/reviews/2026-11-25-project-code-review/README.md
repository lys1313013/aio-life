# 项目代码评审（2026-11-25）

建议在正式上线前先解决后台建号的固定密码、委托凭据的签发权限，以及密码库和重登录的账号隔离。性能方面，消息、待办、Query 目录和附件回收都有能直接从代码数出来的额外调用。接口方面，反馈附件从上传、回复到预览有两个独立故障点，需要两端一起验收。

三个子智能体并行评审后端、Web 和移动端。主审覆盖主仓库、浏览器插件与 Query，并交叉核对客户端调用、后端实现和测试。记录 10 组 P1、14 组 P2。P1 建议在相关功能对外开放前解决，P2 按用户影响和数据规模排期。性能耗时与容量仍需目标环境测量。

## 范围与版本

| 仓库 | 版本 | 重点阅读 |
| --- | --- | --- |
| aio-life | `2b68305` | 部署编排、联合契约检查、类型生成 |
| aio-life-server | `2a17f83` | 鉴权、账号、反馈、附件、消息与后台任务 |
| aio-life-front | `44bf0bf` | 请求与路由、会话、密码库、消息、MBTI、反馈、荣誉 |
| aio-life-mobile | `ab27a72` | 多平台登录与缓存、密码库、管理回复与待办分页 |
| aio-life-chrome-plugin | `3792137` | 连接配置、认证请求、B 站处理、豆瓣队列与测试 |
| aio-life-query | `61441f3` | 数据集与授权、查询执行、请求边界、并发限制与审计 |

独立 Query 使用主 README 指向仓库的 main 临时检出，其余仓库使用当时工作区版本。此评审采用跨仓库重点路径抽查，未连接生产环境。

## P1 上线前优先处理

### P1-01 后台创建的账号共享固定初始密码

Web 建号表单只收集账号、昵称、角色和邮箱，角色包括管理员。服务端给空密码设置同一个固定值，哈希后存储，普通登录流程可直接接受该密码。 [建号入口](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/system/user/form-modal.vue#L88) · [默认密码分支](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L333) · [登录校验](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L88)

建议改为一次性、限时的激活设密。在完成设密前禁止密码登录，处理已由此入口创建且仍使用初始密码的账号。

### P1-02 短期 API Key 可以签发独立的长期 Key

当用户未给密钥菜单设置二级锁时，凭据管理只取当前用户身份。API Key 认证可以提供该身份，签发逻辑又允许无到期时间。原 Key 被撤销或到期后，新 Key 仍单独有效。 [凭据身份](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/interceptor/ApiKeyInterceptor.java#L63) · [签发入口](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/api/ApiKeyController.java#L45) · [有效期](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/ApiKeyServiceImpl.java#L68)

建议将凭据管理限定为真实登录会话，分别覆盖登录会话、API Key 和启用菜单锁时的管理行为。

### P1-03 API Key 和 Web 生成的密码使用普通随机源

服务端用 Hutool 的 fastSimpleUUID 生成持有即可使用的 Key。核对当前 5.8.36 依赖字节码，随机字节来自 ThreadLocalRandom。Web 密码库的生成按钮使用 Math.random 选取和排列字符，还从累计字符池抽取各类别的必选字符，不能保证勾选的每类都出现。 [Key 生成](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/ApiKeyServiceImpl.java#L64) · [密码生成](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/utils/crypto.ts#L138) · [Web 入口](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/PasswordModal.vue#L123) · [移动端取样](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/vault/services/vault-crypto.ts#L59)

建议服务端用 SecureRandom 生成密钥并安排已有 Key 轮换。Web 用平台密码学随机源，分别从每个选中字符组取样，再安全打乱。移动端已有按字符组取样的实现可参考。

### P1-04 密码库两端的密文缺少完整性保护

Web 和移动端均传入 GCM，当前 gm-crypto 实际回退到 ECB，忽略 IV，也不产生认证标签。两端还以解密未抛错判断主密码正确。数据库里的密文被改动时，客户端无法可靠识别。 [Web 加密](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/utils/crypto.ts#L60) · [移动端加密](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/vault/services/vault-crypto.ts#L29) · [解锁判定](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/index.vue#L213) · [已记录的依赖限制](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/docs/password-manager/requirement.md#L30)

建议统一认证加密的密文格式，每次加密使用独立 nonce，认证成功后再显示明文。已有数据需要用户提供主密码才能重加密，迁移前后验证两端互读，失败时保留原数据。

### P1-05 Web 将原始密码库主密码保存在 sessionStorage

用户输入的主密码直接写入可跨刷新保留的同源存储。同一标签页的同源脚本可以读取它。页面挂载时先加载记录，超时由之后的定时检查处理，过期解锁状态也有被继续使用的窗口。 [存储介质](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/store/password-vault.ts#L8) · [原始输入](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/index.vue#L224) · [挂载与定时检查](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/index.vue#L341)

建议主密码限于内存，页面恢复和解密前先判断期限。锁定、退出、换号时同步清除密钥和已经解密的字段。

### P1-06 移动端“记住密码”将可复用的登录密码写入普通存储

主动勾选后，登录页把原始密码和账号一起交给 uni.setStorageSync。普通退出只清 token，下次打开登录页仍可恢复密码。能读取该存储的一方因此也能得到账号密码。 [登录成功处理](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/login/index.uvue#L172) · [存储](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/login/services/remembered-login.ts#L16) · [退出清理](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/session.ts#L36)

建议只在普通存储记账号，密码交给系统密码管理器。更新时清除已保存的 password 字段。

### P1-07 Web 过期重登录可以把上一账号的页面留给下一账号

默认弹窗重认证允许换用户名。成功后更新 token、用户资料和权限码，但仍显示原路由，只关闭弹窗。已打开的业务组件和内存缓存继续存在，例如仍在解锁期限内的密码库页面可保留 A 的记录，B 登录后仍能看到。 [过期入口](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/api/request.ts#L49) · [弹窗成功分支](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/store/auth.ts#L84) · [页面生命周期](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/index.vue#L341) · [显示字段](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/password-manager/index.vue#L521)

建议续用页面前核对重认证用户 ID。账号变化时先清理旧视图、路由、Store 和图片缓存，再为新账号挂载页面。验证同账号恢复、跨账号和仍有旧请求在途三种情况。

### P1-08 二级密码失败次数在并发时会漏记

校验流程先取 Redis 计数，完成密码匹配后再覆盖写回。重叠失败可以写回同一个数，服务端实际允许的尝试次数超过配置。最短允许四位数字的菜单锁尤其依赖这一限制。 [读取与校验](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L524) · [覆盖写回](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java#L533) · [密码规则](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/util/SecondaryPasswordPolicy.java#L5)

建议在验证前原子领取次数，验证后按结果结算；覆盖并发失败、成功与失败交错、计数过期。

### P1-09 浏览器插件切换服务地址会沿用旧服务的 Token

用户修改 API 域名、授予新域名权限并留空 Token 后，配置只更新地址。下一次认证请求将旧服务凭据发送给新地址。B 站功能还分别读取认证头和请求地址，在切换配置时可能使用不同版本。 [保存表单](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/popup.js#L58) · [只更新非空 Token](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/shared/config.js#L23) · [请求配置](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/shared/api.js#L13) · [独立读取认证头](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/bilibili/background.js#L116)

建议按 origin 绑定凭据。跨 origin 保存时清除旧 Token 或要求为新地址输入凭据；单次请求的地址和认证头从同一份配置生成。

### P1-10 MBTI 未完成测试缺少账号归属

Web 用同源单键持久化待完成测试。共享浏览器上 A 发起后退出，B 可恢复 A 的测试。后端创建和轮询未关联发起人，完成时前端又以当前账号自动保存，可能泄露测试结果并写错历史。 [待完成缓存](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/_core/profile/mbti-setting.vue#L40) · [自动保存](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/_core/profile/mbti-setting.vue#L125) · [创建与轮询](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/api/MbtiController.java#L41) · [保存归属](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/service/impl/MbtiResultServiceImpl.java#L185)

建议创建时绑定测试与发起用户，轮询和保存都校验归属；前端按账号保存待办，换号时取消旧轮询。

## P2 功能、架构与规模问题

### P2-01 MBTI 结果作为 HTML 插入主站页面

第三方返回的 matches 原样进入结果，可保存到历史；Web 用 v-html 渲染每项。供应商返回带活动内容的标记时，该内容进入查看者页面的 HTML 上下文。 [第三方字段](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/service/impl/MbtiResultServiceImpl.java#L132) · [HTML 渲染](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/_core/profile/mbti-setting.vue#L480)

建议优先按文本或结构化字段展示。确实需要富文本时限定允许的标签、属性和链接协议。

### P2-02 管理端口默认发布到宿主机所有接口

主 Compose 发布 45679 到所有接口，服务端在该端口启用 health、info、prometheus。未配置外层防火墙或受信网络时，可达宿主机端口的一方可以读取运行指标。实际部署的公网可达性未测。 [端口映射](https://github.com/lys1313013/aio-life/blob/2b683054d24e212da62042f8e774094347023443/docker-compose.yml#L11) · [暴露端点](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/resources/application.yml#L130) · [鉴权排除](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/config/SaTokenConfig.java#L116)

建议默认只在监控网络内提供管理服务，或使用回环地址绑定，远程采集显式指定受信接口或代理。

### P2-03 活跃时间同步在数据库成功前就移除待处理项

任务从 Redis 弹出整批用户后才读时间并逐人写库。数据库在中途失败时，剩余用户已出队，仅记录日志；若用户没有再次访问，最后活跃时间可能长期错误。 [领取](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/autotask/UserLastActiveSyncTask.java#L46) · [写入与错误处理](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/autotask/UserLastActiveSyncTask.java#L73)

建议用可恢复的领取与确认机制，提交后确认，超时重新投递，并以时间单调更新避免旧批次覆盖新值。

### P2-04 附件回收成本跟对象总数一起增长

任务默认每小时递归遍历整个 objects/。超过七天且名称匹配的对象，即使有效，也各自开启事务、持 Redis 锁、查数据库；单个对象抛错会结束本轮扫描。 [对象扫描](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/autotask/AttachmentCollectionTask.java#L35) · [持锁复核](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/service/AttachmentCollectionService.java#L25)

建议持久化游标并限制每批数量，批量查出已登记对象，只对候选孤儿持锁复核；单项失败可重试。用对象数、数据库往返数、扫描进度验证改善。

### P2-05 消息页一次读全历史，整段会话操作按消息逐条写

Web 打开页面直接取当前用户全部收发消息，后端列表无行数上限。标记已读、删除会话按符合条件的消息各发一次请求。删除请求部分成功时，Promise.all 失败，页面仍显示旧列表。 [首屏](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/message/index.vue#L139) · [查询](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/sso/service/impl/MessageServiceImpl.java#L28) · [会话已读](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/message/index.vue#L75) · [会话删除](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/message/index.vue#L349)

建议接口分成分页会话摘要和按会话分页的消息，增加限定当前用户的会话级已读、删除操作；允许安全重试。

### P2-06 移动端待办为每个清单另发一次明细请求

进入或刷新先遍历列表分页，再用四个并发工作循环逐清单读明细。N 个清单增加 N 次网络往返，编辑清单的可用性还取决于整个批次结束。 [逐清单加载](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/tasks/todo.uvue#L119) · [整批完成](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/tasks/todo.uvue#L126) · [编辑入口](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/tasks/todo.uvue#L265)

建议首屏返回分页摘要，按可见清单或展开动作批量读明细，让已加载清单独立恢复编辑。

### P2-07 独立 Query 的目录要串行请求业务后端八次

无指定名称的完整目录请求先校验目录权限，再依次校验七个数据集。正常完成时共八次跨服务 HTTP 鉴权；每次调用重新发出，只要某项发生依赖故障就无法返回完整目录。 [目录鉴权](https://github.com/lys1313013/aio-life-query/blob/61441f3130463fbb07463008e0ab5e3c9a0db4b1/src/main/java/top/aiolife/query/QueryService.java#L34) · [数据集循环](https://github.com/lys1313013/aio-life-query/blob/61441f3130463fbb07463008e0ab5e3c9a0db4b1/src/main/java/top/aiolife/query/QueryService.java#L42) · [发出 HTTP](https://github.com/lys1313013/aio-life-query/blob/61441f3130463fbb07463008e0ab5e3c9a0db4b1/src/main/java/top/aiolife/query/AccessClient.java#L25) · [发布目录](https://github.com/lys1313013/aio-life-query/blob/61441f3130463fbb07463008e0ab5e3c9a0db4b1/src/main/resources/datasets.json#L1)

建议增加批量授权判定，一次返回每个数据集的可见性；保留请求时的用户状态、二级锁和凭据有效期校验。验收比较一次完整目录的鉴权调用数。

### P2-08 移动端管理员带图回复会拒绝合法附件

上传成功得到 UUIDv4，回复函数却用只接受十进制数字的记录 ID 规则处理附件键。在模拟传输下，无附件回复发出一次 POST；带合法 UUIDv4 时在客户端报错，零次 POST。 [回复载荷](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/pages/admin/services/index.ts#L41) · [ID 校验](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/admin/contract.ts#L3) · [后端规则](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/feedback/pojo/req/FeedbackCommentCreateReq.java#L28)

建议将反馈主键和附件键分开校验，在回复用例中使用与真实上传响应形状相同的 UUIDv4。

### P2-09 反馈提出者无法预览管理员回复的私有附件

回复详情返回管理员上传的附件，但预览守卫仅允许上传者或管理员读取反馈附件。因此普通提出者可以看到回复和附件条目，读取图片却被拒绝。修好移动端提交并不能解决接收方的读取问题。 [回复附件](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/feedback/service/impl/FeedbackServiceImpl.java#L445) · [读取授权](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/service/FilePreviewGuard.java#L125)

建议沿附件绑定的回复找到反馈，验证当前用户是该反馈的提出者或获准管理员，并保留菜单锁、绑定和删除状态检查。回归覆盖提出者、回复者、无关第三人。

### P2-10 反馈列表每条补查关联数据，Web 只显示前 50 条

后端组装每条摘要时分别取昵称、附件和评论数，页越大数据库往返越多。Web 我的反馈固定请求第一页 50 条，同一筛选下更早的反馈无法在该列表翻到。 [摘要组装](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/feedback/service/impl/FeedbackServiceImpl.java#L396) · [附件与评论数](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/feedback/service/impl/FeedbackServiceImpl.java#L402) · [固定第一页](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/my-hub/feedback/index.vue#L124)

建议后端按当页 ID 批量查关联数据并聚合评论数；Web 提供翻页或继续加载，并用超过 50 条的数据验证最后一页。

### P2-11 接口生成检查能通过错误的响应类型

文档接口 OperationPage.total 用 CountSerializer 输出 JSON 数字。生成器把 long 统一映射成 string，两个客户端因此都声明 total: string；items 的具体类型也退化为 Array<unknown>。当前 --check 通过，只能说明两份输出与生成器一致。 [字段声明](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/docs/pojo/vo/DocumentationVO.java#L20) · [JSON 数字](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/core/json/CountSerializer.java#L14) · [类型映射](https://github.com/lys1313013/aio-life/blob/2b683054d24e212da62042f8e774094347023443/scripts/generate-api-contracts.py#L208) · [Web 输出](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/api/payload.ts#L4162) · [移动输出](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/api-payload.ts#L4162)

建议从实际序列化元数据识别字段级序列化器及同一外部类中的嵌套模型。在 CI 增加真实响应与生成类型的对照用例，修生成器后重新生成两端。

### P2-12 H5 旧标签页可能清除新登录的持久会话

各标签只在初始化时读共享 token；处理 401 时只比较本标签内存。另一个标签退出旧账号并登录新账号后，旧标签的过期响应仍会无条件删掉共享 token，新标签刷新后需要重登。 [恢复](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/session.ts#L7) · [过期处理](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/api.ts#L89) · [删除存储](https://github.com/lys1313013/aio-life-mobile/blob/ab27a72b5c6428322ccf0579cb4ee06a487824ee/src/services/session.ts#L36)

建议按请求所属 token 条件清理存储，同时同步跨标签登录状态，丢弃已切换账号的在途请求结果。

### P2-13 Web 荣誉列表等待所有附件下载后才展示

页面同时为所有记录创建图片请求，等待 Promise.all 后才写入荣誉列表。冷启动时任何一张图片失败都会阻断已经取得的文字记录；大量屏外图片也会占用首屏网络。 [发起附件请求](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/my-hub/honor/index.vue#L159) · [整批等待](https://github.com/lys1313013/aio-life-front/blob/44bf0bf614ac624d6702aabd09681cb3f45d2141/apps/web-antd/src/views/my-hub/honor/index.vue#L165)

建议先渲染记录和分类，图片按可见范围加载并独立处理失败；用单图不可用和多图弱网验证文字可用时间。

### P2-14 插件回归仍断言旧版视频时长字段

四个标记用例和一个进度用例断言旧字段 duration、watchedDuration。本次实际请求使用 durationSeconds、watchedDurationSeconds，与后端 DTO 对齐。现有错误断言使插件回归持续报错，干扰新回归的判断。 [标记断言](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/tests/bilibili-tag.test.cjs#L60) · [进度断言](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/tests/sync-progress.test.cjs#L70) · [实际请求](https://github.com/lys1313013/aio-life-chrome-plugin/blob/3792137b566616ed7d57334ea541afece158f243/bilibili/background.js#L86) · [后端 DTO](https://github.com/lys1313013/aio-life-server/blob/2a17f83985b178d9347c0ea2ee26844341d087f0/src/main/java/top/aiolife/record/pojo/req/BVideoProgressReq.java#L32)

建议按现行 DTO 更新 fixture，并让插件的独立 CI 验证其使用的跨仓库字段，避免再次脱节。

## 本次验证结果

| 范围 | 实际执行与结果 |
| --- | --- |
| 主仓库契约 | 生成器 11 项单测通过。运行 `python3 -B scripts/generate-api-contracts.py --check` 通过，覆盖 143 个请求模型、159 个响应模型、165 条请求体路由及 191 条 GET 路由。P2-11 的字段级序列化差异也通过了这项检查。 |
| 业务后端 | `PasswordLoginCompatibilityTest` 11 项、`AccountErasureMapperTest` 1 项通过。附件回收集成夹具需要 Docker，本机不可用，初始化失败，未验证其 PostgreSQL 行为。 |
| Web | `pnpm run test:critical` 121 项通过。`pnpm run test:unit` 中 141 个文件通过、2 个文件失败。已收集用例中 942 项通过、2 项失败，另有 2 个未处理拒绝。个人设置测试缺少 `createRouter` mock，首页阅读与观影编辑测试找不到状态控件，同时出现相同 mock 错误。需修复测试后再判断对应页面。 |
| 移动端 | 管理契约、记录与待办、菜单缓存、可空总数分页四组共 42 项通过。额外用模拟传输调用实际管理员回复函数，验证了 P2-08 的附件失败和纯文本对照。 |
| 插件 | 临时副本按锁文件安装依赖后执行 `npm test`，97 项中 92 项通过、5 项失败，均为 P2-14 的旧字段断言。 |
| Query | `LifeDatasetCompilerTest` 和 `FullFieldQueryTest` 各 8 项通过，合计 16 项。未启动完整 Hasura、Connector 和数据库链路。 |

未执行全量后端测试、浏览器端到端验证、移动 H5／微信／App 构建与真机验证、部署或负载测试。未核查目标库已有多少账号或密钥受影响。安全结论基于当前源码、依赖和调用链。

## 整改顺序与验收

1. **账号和凭据。** 后台建号走独立激活，凭据管理限定登录会话，插件换域时清理旧授权。验收覆盖已有账号和密钥的处置。
2. **换号和密码库。** 用两个测试账号覆盖同账号重认证、跨账号登录、H5 双标签、闲置超时和跨端密文迁移。验证认证失败时不会交付明文。
3. **反馈完整流程。** 使用真实形状的附件键，覆盖管理员上传、带图回复、提出者预览和无关账号被拒绝。为字段级序列化补上真实 JSON 对照。
4. **规模验证。** 消息、待办和 Query 目录记录首屏请求数与 P95。附件回收记录每批对象数、数据库往返与断点恢复位置。在同一数据集上比较改动前后结果。
