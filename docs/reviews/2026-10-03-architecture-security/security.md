# 系统安全专项审查（2026-10-03）

结论：微信登录新增链路有比较完整的服务端身份交换、单次票据、账号冲突与首次设密保护，未发现“提交任意手机号/openid 即接管账号”的证据。但系统仍有必须优先修复的安全问题，集中在密码库实际加密模式、通用日志、文件预览、服务端抓取及账户撤销。不能据微信单元测试通过认定系统整体安全。

## 范围与证据边界

- 审查 server `e579153`、front `6e54d5256`、mobile `5c711d9` 的当前工作区，重点看 2026-09-28 以来变化，并纳入 server 银行卡/对象存储未提交重构、mobile 服务分包移动等未提交内容。工作区有并行开发，行号以本次读取快照为准。
- 只读业务代码；本报告是唯一写入文件。未操作生产、真实账号、数据库、Redis、MinIO 或微信服务；未读取被忽略的本地凭据配置。不是完整依赖漏洞扫描、生产渗透或真机认证验收。
- 运行隔离测试：`mvn -Dtest=WechatAuthServiceTest,WechatMiniClientTest,WechatRequestLogTest test`，**20 通过，0 失败，0 错误，0 跳过**。这三个类使用 Mockito/MockRestServiceServer，无真实微信/DB/Redis 连接。日志 `/tmp/aio-security-wechat-tests-20261003.log`。
- 本地 Node 使用锁定的 `gm-crypto@0.1.12` 和合成明文验证 ECB 回退与密文篡改，不涉及真实密码。

## 需优先处理的问题

### SEC-01 / P1：密码库声称使用 GCM，实际静默使用 ECB，密文无完整性保护

- 位置：`aio-life-mobile/src/pages/vault/services/vault-crypto.ts:29,33`；`aio-life-front/apps/web-antd/src/utils/crypto.ts:60-85`。
- 证据：两端传 `mode: 'GCM'`，Web 还用 `as any` 绕开类型。锁定依赖实际只有数值常量 ECB=1、CBC=2，只有 `mode === 2` 才使用 IV，其余回退 ECB。[上游文档](https://github.com/byte-fe/gm-crypto#sm4)亦只列 ECB/CBC。
- 最小复现结果：相同密钥下 `'GCM'` 与显式 ECB 密文相等；更换 IV 不改变密文；重复的 16 字节块产生重复密文。把合成 `AAAAAAAAAAAAAAAABBBBBBBBBBBBBBBB` 的两个密文块交换，解密成功返回 `BBBBBBBBBBBBBBBBAAAAAAAAAAAAAAAA`，没有认证失败。
- 前提与影响：能取得密文可观察同一密钥内重复块；能修改存储/传输中的密文则可替换或重排块而不被加密层拒绝。没有证明可凭此直接恢复任意密码，不能称为“密码已泄漏”。
- 来源：Web 既有缺陷（文件历史至少追溯至 2026-05-01），近期 Mobile 继承；当前未提交文件移动并非根因。
- 建议：两端共同引入带版本的 AEAD 格式（nonce、密文、认证标签和关联数据），旧格式只用于兼容解密并在用户解锁后迁移。不能直接把旧调用改为另一模式，否则历史记录无法读取。增加跨端互通、错误密码和篡改必拒绝测试。

### SEC-02 / P1：通用请求日志仍记录真实密码、二级密码与验证码

- 位置：`aio-life-server/src/main/java/top/aiolife/record/aop/LogAspect.java:44-56`；`sso/api/AuthController.java:81-94`；`sso/api/UserController.java:52-57,145-149`；`sso/pojo/req/RegisterReq.java`、`ResetPasswordReq.java`、`ChangePasswordReq.java`、`SecondaryVerifyReq.java`、`SetSecondaryPasswordReq.java`。
- 证据：日志只排除名为 `login` 的方法、微信控制器及银行卡控制器，其余入参由 fastjson 完整序列化。上述 DTO 的密码/验证码是普通可序列化字段，因此注册、修改/重置密码、验证/修改二级密码进入 INFO 日志。微信入口的专门脱敏没有覆盖这些认证入口。
- 前提与影响：日志读取者或获得日志备份的人可获得有效新密码、旧密码、二级密码及短期验证码。无需认证绕过即可在正常用户操作时产生泄漏。
- 来源：既有通用日志设计；近期新增 DTO 契约仍未形成敏感字段默认禁止规则。
- 建议：认证与凭据接口采用日志字段白名单；统一处理 password/newPassword/oldPassword/code/loginTicket/token 等字段，禁止全量 DTO 序列化。增加每个敏感控制器入口的日志断言。此项不同于源码标注“有意保留”的失败登录密码本；即使保留后者，也不能把成功修改的新密码写普通日志。

### SEC-03 / P1：公开头像上传可承载 HTML/SVG，同源预览可执行脚本

- 位置：`aio-life-server/src/main/java/top/aiolife/record/service/impl/FileServiceImpl.java:54-83`；`record/enums/FileBizType.java:16`；`record/api/SysFileController.java:75-78,108-137`；`record/service/FilePreviewGuard.java:98-99`。
- 证据：只有银行卡卡面经过真实图片解码校验；`bizType=avatar` 使用客户端声明的 `MultipartFile.getContentType()` 入库并标记公开。`GET /file/preview/{id}` 将该类型原样作为响应 Content-Type，预览无 attachment，非银行卡响应无 CSP sandbox。
- 前提与影响：普通登录用户上传声明为 `text/html` 的内容后，获得公开按 ID 预览地址。受害者直接打开该地址时内容在 API origin 执行；若此 origin 带业务 Cookie，可借受害者身份调用接口；若与 Web 同源还涉及 Web 存储。仅把 SVG 放入 `<img>` 不等于脚本执行，利用需要直接打开/嵌入活动文档或其他允许脚本的上下文。未进行在线上传或浏览器攻击。
- 来源：既有通用上传/预览缺陷，近期银行卡的严格校验没有扩展到头像及其他文件。
- 建议：头像只接收经解码重编码的允许图片；通用附件按不可信内容下载或使用无业务 Cookie 的独立域，并加正确的 `nosniff`/CSP。不能只依赖文件后缀、前端 accept 或随机文件 ID。

### SEC-04 / P1：影视/阅读封面字段可驱动服务端访问任意 URL（SSRF）

- 位置：`aio-life-server/src/main/java/top/aiolife/record/api/MovieController.java:42-51`；`record/service/impl/MovieServiceImpl.java:87-90,108-114,330-335`；`ReadRecordServiceImpl.java:87,107,266-271`；`FileServiceImpl.java:98-120`。
- 证据：用户可写的 `MovieCreateReq.coverImgUrl` / `MovieReq.coverImgUrl`、阅读同类字段在缺少 fileId 时直接流向 `HttpRequest.get(imageUrl).execute()`。目标协议、地址、内网 IP、DNS 解析和重定向均没有目标校验。Content-Type 校验发生在请求已经发出、响应已经读取之后。影视更新甚至在检查记录归属之前发起抓取。
- 前提与影响：普通已登录账号可使服务器向其能访问的内网地址发 GET；即使目标返回非图片，服务端请求也已经发生。能否读取元数据/敏感正文取决于目标协议、响应类型和网络拓扑，本次没有向内网发送探测请求。
- 来源：既有自动上传封面功能；近期最小 DTO 仍保留可控字段。
- 建议：优先仅允许已知图片来源；否则统一实现安全远程资源抓取器，校验协议、解析后 IP、每次重定向、端口、响应长度和超时，并将网络出口限制为外部资源。更新先做资源归属校验。

### SEC-05 / P1：删除账号不撤销已有 Token/API Key，密码重置也不撤销会话

- 位置：`aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java:281-285,168-184,442-456`；`sso/util/RequestLoginContext.java:16-20`；`sso/interceptor/ApiKeyInterceptor.java:54-72`；`sso/service/impl/ApiKeyServiceImpl.java:69-72`。
- 证据：删除只做逻辑删除与 userInfo 缓存清理；请求校验只检查 Sa-Token 会话，API Key 只检查自己的删除/过期字段后 `switchTo(userId)`，不检查所属用户是否仍有效。修改/重置密码只更新哈希。当前 Token 配置最长 30 天，API Key 可没有过期时间。
- 前提与影响：被删除用户持有的旧凭据可继续访问仅按 userId 过滤的业务接口；被盗 Token 不会因找回密码而自动失效。角色查询可能令某些管理员入口失效，这不等于全部业务凭据撤销。
- 来源：既有账号生命周期缺陷，微信签发的 Token 同受影响。微信登录查询和绑定锁行均排除逻辑删除用户，因此不能误述成“微信可以直接登录已删除记录”。代码无独立 disabled/status 用户字段；生成列 active_flag 表示未逻辑删除，并非额外的封禁开关。
- 建议：删除/禁用时撤销会话、API Key 及关联认证缓存；新请求校验用户有效性；修改/重置密码明确撤销其他会话策略。增加删除前后旧 Token/API Key 的真实拦截器回归。

### SEC-06 / P2：账号密码登录没有应用级失败限速，微信原账号绑定继承此入口

- 位置：`aio-life-server/src/main/java/top/aiolife/sso/service/impl/UserServiceImpl.java:84-117`；`aio-life-mobile/src/services/wechat-auth.ts:45-52`。
- 证据：密码登录直接查用户、计算 MD5、落登录日志，无账号/IP 尝试计数、退避或锁定；微信绑定先调用同一 `/auth/login`。微信专用 `bind` 每 IP 10 次/分钟并不能保护前置密码验证入口。
- 前提与影响：若部署网关未另有限速，匿名请求可持续猜测密码/撞库并放大数据库日志写入。未声称网关当前一定没有额外防护，也未执行撞库测试。
- 来源：既有密码登录缺陷，近期微信绑定新增了复用路径。
- 建议：账号与可信客户端 IP 联合限速，分级退避与异常监控，避免简单永久锁定被利用为拒绝服务。代理地址必须来自受信代理处理，不直接相信任意 X-Forwarded-For。

### SEC-07 / P2：二级锁缓存失效丢失时，旧的未锁定状态可保留五小时

- 位置：`aio-life-server/src/main/java/top/aiolife/core/cache/MenuDataCache.java:26,48-68`；`sso/service/impl/UserServiceImpl.java:580-609`。与 server 架构报告同一问题，不重复计数。
- 条件与证据：添加锁之前已缓存空锁列表；DB 提交后只执行一次 Redis version SET。若此时 Redis 短暂失败，或进程在提交后/失效前退出，持久化锁配置与缓存分离。Redis 恢复后旧版本空数组继续命中，直到 5 小时 TTL，读取链没有配置版本核验。
- 影响：仅在上述故障窗口成立时，持有主登录会话者可绕过新配置的二级锁。正常提交并成功失效时不存在此问题，不能称无条件鉴权绕过。
- 来源：近期 `80e333b` 缓存改动。
- 建议：安全配置使用持久化版本/事务 outbox 保证失效可补偿；设置锁失败时界面及接口应明确失败并采用保守保护，避免长 TTL 作为安全配置唯一收敛手段。

## 微信新增链路已确认的保护

- `WechatAuthRequests` 只接收 loginCode、phoneCode、loginTicket、密码；openid/手机号由服务端交换结果取得，客户端不能直接声明。
- `WechatMiniClient` 固定微信域名，AppSecret 仅服务端配置；身份、手机号格式和手机号水印 AppID/时间校验存在；上游错误不透传 URL、正文、session_key，且手机号 code 不自动重试。
- `WechatTicketStore` 使用 SecureRandom 32 字节票据，Redis 保存摘要键、5 分钟 TTL，`getAndDelete` 原子消费；绑定用途票据不能再用于注册。真实 Redis 版本/部署行为本次未验证。
- 账号手机号匹配不自动合并或登录旧账号；绑定要求已登录业务会话、原密码和微信票据，且拒绝 API Key；首次设密要求新鲜微信 loginCode 与当前用户 openid 一致，不覆盖已有密码。
- `WechatAccountService` 绑定/设密使用事务及 `FOR UPDATE`；注册依赖手机号+active_flag、openid+active_flag 唯一索引。脚本具有大小写敏感 openid 与逻辑删除后释放唯一性设计，实际生产迁移/唯一索引安装尚未验证。
- 微信接口按真实 `request.getRemoteAddr()` 做 Redis 原子限速；比直接相信请求头更安全，但若部署反代且没有可信代理转换，会把整站用户集中到代理 IP 额度，导致可用性问题。未核实生产代理配置。
- Mobile 只在 `LOGGED_IN` 保存业务 Token；临时票据不落为 Token；绑定临时 Token 最终注销。server `is-share: false`，该清理不会因为同账号登录而必然注销新签发 Token。
- 官方微信资料访问尝试失败，本报告没有据第三方摘要推断最新微信收费/准入/手机号与 openid 对应规则；真实微信 code 生命周期、手机号授权、目标 MySQL 并发和真机流程仍需隔离环境专项验收。

## 其他明确风险与生产待核实项

- **已有明确安全债**：`sso/util/PasswordUtil.java:14-16` 使用一次 MD5(password+salt)，不具备现代慢哈希抗离线猜测能力；微信首次设密复用它。建议版本化迁移 Argon2id/bcrypt/scrypt 等合适密码哈希，旧密码验证成功后升级。
- **有意保留但仍有风险**：`UserServiceImpl.java:98-111` 将失败登录的明文密码写 `login_log.password`，源码标注既有产品决定。正常用户的拼写错误、旧密码、其他站点密码也会进入该表。此次不修改、不把“有意保留”解释为没有安全风险。
- **API Key 日志**：`ApiKeyInterceptor.java:57,63` 记录完整无效/过期 Key。应只记录指纹；这些分支不是成功鉴权分支，不能据此断言全部有效 Key 都被日志泄漏。
- **跨域/Cookie**：`CorsConfig.java:19-28` 为任意 Origin + credentials；`LoginSessionService.java:31-35` 手工添加业务 Cookie 未在调用处指定 Secure/HttpOnly/SameSite。跨站可利用性取决于浏览器 SameSite、API/Web 域名和代理覆写，不能未经浏览器验证声称任意站点必然读到数据。建议明确允许来源、明确 Cookie 属性，减少同时存在的 Token/Cookie 鉴权模式。
- **部署**：跟踪的 `docker-compose.yml:8` 映射管理端口，`application.yml:106-141` 无管理端口 bind-address 且有开发 JWT 默认值。生产防火墙、网络绑定、JWT 强制覆盖及对象存储 ACL 本次未查；不是“当前生产默认密钥泄漏”的结论。
- **历史文件兼容入口**：`sso/api/FileController.java:87-105` 对找不到文件记录的旧对象仍允许任意登录用户读取。需盘点是否存在私密孤儿对象及对象路径暴露，再清除该默认放行；目前未读取实际桶，因此作为条件风险。
- **对象存储新增管理入口**：控制器有 admin 角色约束，卡面/存储删除有归属与引用守卫；未发现这轮 mapper 重构移除这些检查。未以此替代真实 MySQL/MinIO 权限验收。

## 建议顺序

先处理 SEC-02/03/04 的直接泄漏与跨边界入口，紧接 SEC-01 密码库版本化升级和 SEC-05 凭据撤销，再补 SEC-06/07。微信新增主体无需推翻重写；继续保留当前票据、原账号验证、单独首次设密和唯一索引设计，把真实 Redis/MySQL/微信验收作为上线前独立关卡。
