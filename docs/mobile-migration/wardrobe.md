# 衣柜操作盘点与移动端契约

证据：Web `views/wardrobe/index.vue`、`components/{ItemForm,FilterBar,ItemCard}.vue`、`api/wardrobe/index.ts`；后端 `wardrobe/api/WardrobeController.java` 与分类服务。

迁移衣物列表/详情/新增/编辑/删除，分类、季节、名称/颜色/品牌筛选；衣物数量、总价值、均价与季节/分类统计；鉴权照片展示/预览/上传替换/移除。衣物完整字段为 name/categoryId/color/brand/season/purchaseDate/price/fileId/size/memo，ID 全程 string。`/wardrobe/items` GET/POST、`/items/{id}` GET/PUT/DELETE、`/stats` GET。

分类接口 `/wardrobe/categories` GET/POST、`/{id}` PUT/DELETE。Web未提供可见分类管理，Mobile补齐个人分类 name/icon/parentId/sort 管理；系统 categoryType=0 为只读，后端强制该边界。分类删除前提示先处理子分类/衣物，避免孤立关联。

没有找到穿搭/搭配实体、Web操作或API，因此不创建虚构穿搭数据。此项需主台账记录为源系统未提供。

页面 `/pages/goods/wardrobe` 复用 MobilePage、PageState、FormField、MobileButton、ConfirmAction、AdaptiveModal、MetricCard、MiniChart。上传照片使用 `/file/upload` 的 `bizType=wardrobe_item`；局部loading、失败保留表单、保存期间禁止关闭，图片未保存不会自动修改关联。

真机、真实后端验证及图片格式/尺寸后端限制待实测；模拟证据与构建分别记录。

## 本批验证

`tests/wardrobe-contract.test.mjs` 3项通过：完整衣物字段、字符串长ID、非负价格/季节校验、分类树/系统预设保护、复合筛选。Vue SFC parse/compileScript/compileTemplate 通过。

`tests/wardrobe-web.mjs` Chrome模拟API实际交互6/6通过：390/768/1440深浅主题，编辑失败保留输入并可重试、完整字段和季节数组/长categoryId提交、系统预设分类没有编辑入口、无横向溢出。截图 `aio-life-mobile/test-results/wardrobe/`。尚未模拟上传照片与真实删除/新增分类全流程，真实后端/微信/App仍待集成验收，不把上述源码和模拟证据称为全部平台闭环。

主审后补验：模拟 `/file/preview/999` 返回真实PNG，6组合均断言原生图片完成blob加载且naturalWidth>0，编辑提交保留fileId，失败可重试。鉴权下载仅在异步photo函数执行，模板绑定已完成下载的string缓存；onHide/token变化清缓存及表单并使旧回调失效；父分类排除所有后代，选择标签为完整父路径+[完整字符串ID]，避免同名映射。手机深色弹窗截图已人工查看，控件/错误/图片均可辨识。
