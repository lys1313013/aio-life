# Mobile 公共组件契约

所有组件位于 `aio-life-mobile/src/components/<名称>.uvue`，保留 uni-app x Vapor，组合式 API，使用跨端内置组件和现有 `themeClass`。业务页控制请求和表单，组件不包含业务 API。

| 组件 | Props | Events / Slots |
| --- | --- | --- |
| MobileButton | `label: string` 必填，`icon?: string`、`loading?: boolean`、`disabled?: boolean`、`danger?: boolean`、`variant?: 'primary' \| 'quiet'` | `click`；default slot 可替换文字；icon 存在时只显示图标，label 始终为可访问名称 |
| ConfirmAction | `label: string`、`message?: string`、`action: () => Promise<unknown>`、`icon?: string`（默认 ×）、`danger?: boolean` | `success(result)`；异步 action 失败保留确认与错误，成功关闭；同一时刻只允许一次执行 |
| FormField | `label: string`、`modelValue?: string`、`kind?: 'text' \| 'textarea' \| 'date' \| 'time' \| 'selector'`、`options?: string[]`、`error?: string`、`disabled?: boolean`、`placeholder?: string`、`password?: boolean`、`inputType?: string`（number/digit 等）；`kind='password'` 自动隐藏 | `update:modelValue(string)`；default slot 可替换内置输入（数字、复杂选择器等），校验错误由业务页提供 |
| PageState | `loading?: boolean`、`error?: string`、`empty?: boolean`、`emptyText?: string` | `retry`；default slot 始终保留，加载/失败不清空已有数据 |
| MobilePage | `refreshing?: boolean` | `refresh`；default 为滚动内容，`fixed` slot 为不随列表滚动的悬浮操作；业务 finally 必须结束 refreshing |
| LoadMore | `loading?: boolean`、`hasMore?: boolean` | `load`；使用点击继续加载，无悬停依赖 |
| MetricCard | `label: string`、`value: string \| number`、`unit?: string` | 简单指标，无图表库依赖 |
| AdaptiveModal | 兼容 `label`、`busy?`、`maxWidth?`、`contentKey?`；新增 `showClose?`（默认 true） | `close`；default 内容；busy 禁止关闭，内部滚动并扣除键盘、安全区 |

`src/services/mobile-ui.ts` 提供 `createLatestTask`：每次请求使用 token，仅当前 token 能应用结果；`invalidate()` 在离页或卸载时使旧结果失效。`createAsyncAction(reactive({loading:false,error:''}))` 防重复操作并暴露 loading/error，失败不修改表单。调用方仍负责业务数据和权限。

确认操作直接位于触发按钮下方，同处卡片/行容器，宽度受可用窗口约束，未使用浏览器 DOM。按钮至少 44px；长内容由 MobilePage 和 AdaptiveModal 滚动。深浅色通过主题类，桌面内容最大宽度 960px，中间宽度平板连续适配。状态栏与微信胶囊继续由现有 PageHeader 负责，避免重复占位。

验证边界：本契约不等于微信或 App 真机验收。Web、微信编译和真机应分别记录；MiniChart 已接入时间、财务、运动与衣柜统计，参见下方契约。

MobilePage 挂载由主 Agent 提供的 SecondaryUnlock；继续复用现有 useRefreshTheme。

本批验证：`node --test aio-life-mobile/tests/ui-contract.test.mjs`，4 项通过，覆盖离页竞态、重复点击、失败重试和 picker/安全区。SFC 检查不替代 Vapor 构建和真机。

AttachmentField：`files:any[]`、`uploadPath:string`、`formData?:Record<string,string>`、`disabled?:boolean`；`update:files` 输出完整附件对象列表。`v-model:files` 保留原附件；移除只更新待提交关联，不立即删除服务端文件。支持已有附件鉴权预览、图片上传、局部 loading/错误/再次操作；通用文档选择通过 native-files 适配 Web/微信/App，App 文件系统分支仍待真机。原生 Office/PDF 使用 openDocument，Web 条件编译打开下载的临时地址；真机待验。

MiniChart：`label:string`、`labels:string[]`、`series:{name:string;color?:string;values:number[]}[]`、`kind?:'line'|'bar'`、`unit?:string`。纯view线段/点/分组柱图，支持负数、零基线、图例开关和picker查询每点各序列数值。分类构成使用bar，月/日趋势使用line。长度/有限数字严格校验，缺失值由业务明确处理，不在公共组件默默填零。Time dashboard已复用；records/finance按契约接入。

补充：MobileButton添加role/aria-disabled并保留暗色危险色；FormField Web原生内部input/textarea需条件编译同步aria-label，因为uni组件外壳属性不会自动传给实际控件；blur同步最新值修复快速保存。MobilePage初始鉴权用onMounted，401由request统一处理，避免子组件onShow/onHide不触发；requiresAuth=false用于匿名页面。AttachmentField已支持Web/MP“添加文件”（chooseAndUploadDocument），App 已接系统文档选择及沙盒复制，尚待真机；readonly与busy-change已提供。
