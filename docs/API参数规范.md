# API 参数规范

本文适用于 `aio-life-server` 的 HTTP 业务接口及 Web、Mobile、浏览器插件调用。MCP 历史工具仍有 `page/size` 和 integer ID Schema，见[接口范围](需求/MCP接口需求方案.md)。独立 `aio-life-query` 的 REST 响应仍使用 `rscode/result/data`，GraphQL 使用 `data/errors/extensions`，分页使用 `limit/offset`；以其 [README](../aio-life-query/README.md) 为准，不套用业务后端协议。

本规范适用于 Web、移动端与后端的业务接口。系统尚未正式上线，接口仅接受当前规范格式，两个客户端同步更新，不保留旧参数或旧响应兼容。

## ID 与基本类型

- 业务 ID 在 JSON、路由、查询参数、表单和组件 key 中始终使用十进制字符串，不经 `Number`、`parseInt` 或一元 `+` 转换。
- 必须定位已有资源的路径 ID 为必填，不能构造 `/undefined` 或空路径。创建请求不携带系统生成的 ID、用户归属或审计字段。
- 第三方协议的数字字段、题目序号和业务数量不机械改成字符串。金额按接口声明使用十进制字符串或数字，不能把类型断言当作运行时转换。

## 分页与筛选

- 页码分页统一使用 `page/pageSize`：`page >= 1`，`1 <= pageSize <= 200`。消息用户页上限 50，卡面及活动日志等已有更严格上限继续保留。
- 游标分页仍使用业务游标和 `pageSize`，例如对象存储 `cursor/pageSize`，不能把游标伪装成页码。
- 仅接受 `page/pageSize`，不接收 `current/size/get/perPage` 别名。游标接口使用 `cursor/pageSize`。
- GET 筛选字段与分页参数平铺在 URL 中；数组使用重复参数，不发送 GET 请求体或嵌套 `condition`。
- 完整列表通过逐页收集获得；不能使用负数、零或超大页大小取消分页。失败保留已加载内容和失败页，重试不能跳页；有明确总数时按总数判断结束，无总数时按空页或短页判断。
- 分页查询必须具有稳定顺序，业务排序字段相同时追加唯一 ID；偏移使用不会溢出的计算，超末页返回空列表，不构造空 `IN` 查询。

## 日期与时间

- 日期：`2026-10-22`，格式 `yyyy-MM-dd`。
- 本地日期时间：`2026-10-22 10:30:00`，格式 `yyyy-MM-dd HH:mm:ss`。客户端不要对本地时间自动添加时区或转成 UTC。
- 待办日期时间严格使用空格格式，不接收 ISO 本地时间或带时区格式。
- 时迹的 `startTime/endTime` 是从当天零点起的分钟数，沿用闭区间语义，不适用日期时间字符串格式。

## 必填、可空与校验

- 创建 DTO 对实际业务必填字段执行非空、非空白校验；更新 DTO 保留局部修改语义，不因复用创建模型而要求重传全部字段。
- `undefined` 或字段缺失表示未提交，显式 `null` 仅在接口支持清空时使用，空数组表示明确提交空集合。前后端都不能将三者混为一谈。
- 可选数值仍需范围校验。例如运动数量允许不填，但传入值必须非负；关联 ID 必须有效，不能靠数据库异常代替参数检查。
- 校验必须在 HTTP 入参边界生效；嵌套对象和列表需要级联校验，公共分页也必须检查范围，不能只有未被触发的注解。
- 参数格式、类型、缺失或范围错误使用参数错误业务码和可读提示，客户端仍须检查业务码，不能仅判断 HTTP 状态。

## 契约生成与验证

`scripts/generate-api-contracts.py` 从后端请求模型生成 Web、移动端字段白名单及 TypeScript 类型。默认校验组中的 `@NotNull/@NotBlank/@NotEmpty` 对应必填、不可空字段；有默认值的字段可省略但不能显式置空。无条件必填与仅限特定校验组的限制不能混淆。

```bash
python3 scripts/generate-api-contracts.py
python3 scripts/generate-api-contracts.py --check
python3 -m unittest discover -s scripts -p 'test_api_contracts.py'
```

生成的类型不替代后端运行时校验，字段白名单也不执行数值转换。动态 JSON 接口保留其专有校验，不生成空 DTO 丢弃输入。

### 本地统一推送与联合检查

先在对应仓库审查并提交业务修改，再在主仓库执行：

```bash
python3 scripts/push-repositories.py
# 明确要求跳过 Git hooks 时使用；脚本本身不运行业务测试或构建。
python3 scripts/push-repositories.py --skip-hooks
```

- 入口要求三个业务仓库位于 `main` 且工作区干净，主仓库的生成器、推送入口和工作流修改也必须先提交。已有未提交修改会保留，不自动暂存、清理或提交业务文件。
- 使用 `git pull --ff-only` 更新仓库，然后生成 Web `apps/web-antd/src/api/payload.ts` 和 Mobile `src/services/api-payload.ts`；只自动提交这两个生成文件，没有差异时不创建提交。需要预先安装 Web 依赖及 GitHub CLI，并完成本机 Git、`gh` 登录。
- 推送后端、Web、移动端和主仓库，确认远端 `main` 与本次提交一致后，才执行本地 `--check` 并触发只读 CI。任一推送失败或远端版本改变都会停止，不强推、不回滚已推送提交；处理后可重跑入口。
- CI 仅通过 `workflow_dispatch` 接收本次四个完整 commit SHA，按固定版本检出并检查，运行摘要保留版本记录；不会在各仓库尚未推送完成时抢先检查，也不会因为重跑而改读最新 `main`。
- 云端只使用 `contents: read` 的内置 Token，不生成提交、不推送代码、不需要跨仓库写入密钥。联合检查仅证明生成契约一致，不替代各端业务验证或部署。
