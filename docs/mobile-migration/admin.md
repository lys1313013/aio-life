# Mobile 分类与管理端操作盘点及实现

Web 证据：`views/time/time-tracker/{category-config,admin}`、`views/config-management/{sysDictType,sysDictData}`、`views/system/{user,menu,user-dict,feedback,config,operation-log,access-log}`，及相应 `api/core`、`api/system`；后端 Controller 再核对管理员角色、排序、批量 action。

| 任务 | 操作与字段 | 原生入口 / API |
| --- | --- | --- |
| TIME-03 | 列表、父子展开、个人新增/编辑/删除、公共覆盖、隐藏/恢复、卡片统计、同级排序；父分类、名称、颜色、图标、描述、时间类型 | `/pages/categories/index`；`/timeTrackerCategory/list,hidden`，POST/PUT 根资源，DELETE /{id}，POST /reSort |
| TIME-04 | 公共分类 CRUD、启用、统计、子分类、排序、图标颜色、描述、时间类型 | `/pages/categories/index?admin=1`；`/timeTrackerCategory/admin/list` 和 POST /admin、PUT/DELETE /admin/{id} |
| CONFIG-01 | 字典类型查询/分页、新增/编辑/删除；dictName/dictType/remark | `/pages/admin/index?kind=dict-types`；`/sysDictType/query`，POST 根资源，PUT/DELETE /{dictId} |
| CONFIG-02 | 字典数据类型/名称筛选、分页、CRUD；dictId/dictValue/dictLabel/dictSort/remark，状态展示 | `kind=dict-data`；`/sysDictData/query`，POST 根资源，PUT/DELETE /{dictCode} |
| ADMIN-01 | 用户关键词/分页、CRUD；username/nickname/role/email，在线与最近活动展示 | `kind=users`；`/user-center/list`，POST/PUT 根资源，DELETE /{id} |
| ADMIN-02 | 菜单树、展开、搜索、CRUD、子菜单、排序和启用；name/path/parentId/component/redirect/roles/meta/title/icon，保留未知 meta；保护 /system、/system/menu | `kind=menus`；`/menu/admin/tree,role-options`、POST /admin、PUT/DELETE /admin/{id}、PUT /{id}/status,sort |
| ADMIN-03 | 基础字典类型/名称/状态筛选、分页、CRUD、只读、图标颜色、同类型相邻排序；只编辑 userId=0 | `kind=user-dict`；`/userDictData/admin/query`、POST /admin、PUT/DELETE /admin/{id}、POST /admin/reSort；`/userDictType/dictTypeEnum` |
| ADMIN-04 | 反馈类型/状态/关键词筛选、分页、详情、评论与附件、管理员回复、变更状态、批量关闭 | `kind=feedback`；`/feedback/admin/list,{id},{id}/reply,{id}/status,batch`，批量 action=CLOSE、ID string；附件共用鉴权 preview 与上传 |
| ADMIN-05 | 配置列表和编辑保存，BOOLEAN/NUMBER/STRING/JSON；通知接收管理员多选 | `kind=config`；`/system-config/list`、PUT /system-config/{key}；`/feedback/admin/admin-users` |
| ADMIN-06/07 | 操作/访问日志用户名和日期筛选、分页、CSV 导出 | `kind=operation/access`；`/system/logs/{type}`、`/{type}/export` |

请求筛选平铺 URL，不能把 condition 包进 GET 请求体。客户端保留原数据和表单，成功后更新列表，失败提供重试。分类排序采用点击上/下替代拖拽，且仅同级；用户字典排序使用服务端定位协议。管理员身份来自后端 roles，服务端继续强制鉴权。

后续实现和验证记录追加于此。主 Agent 注册页面、导航和权限入口；本批不改共享文件及总台账。

## 本批结果与验证边界

已落地 `src/pages/categories/index.uvue`（个人/管理员 query 分支）、`src/pages/admin/index.uvue`（9 个 kind）、`src/services/admin/{contract,specs,index,categories,export}.ts`。复用公共组件；ID 严格 string，菜单未知 meta 保留，核心管理路径和启用保护，分类公共覆盖保留模板引用且未改父级不提交覆盖值，用户基础字典以 userId='0' 为边界。

`node --test aio-life-mobile/tests/admin-contract.test.mjs aio-life-mobile/tests/ui-contract.test.mjs`：10 项通过，含 mock request CRUD、批量关闭、个人/管理员分类路由、长 ID、同级排序、核心菜单保护、JSON 配置、竞态与失败恢复。3 个新增页面/附件组件通过 Vue SFC parse/compileScript/compileTemplate；这不是 Vapor 构建或真机验证。

明确待验与差异：

- Web/微信全构建和手机/平板/桌面深浅 UI 由主 Agent 集成检查；真实后端、微信和 App 真机尚未验证。
- 日志 CSV：Web 条件编译下载；微信写文件并 shareFileMessage；App downloadFile/saveFile。微信分享能力、App 保存路径可达性与文件系统兼容必须真机核验。
- 反馈新附件选择目前复用图片 helper；已有 Office/PDF 原生 openDocument 预览和 Web 临时地址打开仍需平台核验，任意文档新上传尚未完成，不能称全类型附件闭环。
- 字典类型/数据支持已加载数据字段升降序，等同 Web 表格本地排序；后端 CommonQuery 不含全量排序协议。用户字典/菜单/分类仍使用业务排序接口。
- 图标选择使用已存在本地 catalog；任意未收录图标可保存字符串但预览会退为色点，不能称覆盖 Web 在线图标全集。
- 系统配置失败保留本地输入；刷新不覆盖已输入配置值，以防丢失未保存编辑。成功后该字段应以本地提交值展示。

实际 Web 模拟专项 `tests/admin-web.mjs` 通过：390/768/1440 深浅主题分类编辑失败保留及重试、字符串长 ID/原字段保留；菜单未知 meta/keepAlive 保留；403 保持登录，401 清会话并统一跳登录。截图保存在 `aio-life-mobile/test-results/admin/`。此证据使用模拟 API，不代表真实后端或真机验收。
