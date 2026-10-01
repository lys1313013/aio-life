# 统一间距复验 07：记录模块

19/19 H5 模拟接口用例通过。覆盖11物理页13模式：notes think/memo、library movie/read、anniversary、milestones、honor、feedback、exercise、categories、activity、video、weread。

通过模拟登录后点击底栏「生活」和实际功能入口，categories 经运动「分类配置」进入，没有直接跳转业务页。390×900覆盖13模式浅深交替，每页截图、主编辑/新增/连接弹窗顶部及滚动底部、关闭取消；阅读、观影、纪念日追加768×900及1440×900。多记录列表使用三条模拟数据检验密度，所有业务写入数组为空。

测试：`aio-life-mobile/tests/e2e/spacing-07.spec.js`。证据：`aio-life-mobile/artifacts/spacing-audit/07`，包含57张原图、19份量化JSON及三张13模式拼图。实际通过view_image查看全部模式的页面/弹窗顶部/底部拼图，以及阅读平板/桌面、纪念日手机、视频长弹窗原图。

## 量化与视觉判断

MobilePage内容容器负责唯一页面内边距：390容器x=0、width=390、padding=12；业务根节点x=12、width=366、左右padding=0。1440容器x=240、width=960，业务根节点x=252、width=936，符合居中内容上限及单层12px页面边距。

纪念日卡片 `ui-pad-card` 内边距12px、网格gap12px；390两列、768/1440三列。阅读/观影海报390三列、768五列、1440七列，列间距12px，三条数据形成未填满的末行。搜索及筛选行与页面内缘对齐，没有双层padding或字段margin与gap叠加。弹窗内容内缘16px；视频、活动、荣誉、阅读/观影长弹窗可以滚动到底并取消；短弹窗按内容居中。无横向溢出。

修复library与anniversary网格宽度计算中的硬编码列间隙，统一为 `$space-section` 倍数，避免配置变动导致网格右缘漂移；library状态标签、anniversary菜单项padding使用语义变量；移除纪念日重复底部避让声明。保留海报比例、44px点击区、浮动按钮避让。未修改shared/config。

旧records spec提供空preferences.menus，当前生活目录已以菜单树为准；07脚本提供与候选入口一致的菜单树，保持真实入口流程。

仅验证H5模拟API及浏览器主题；未验证真实后端、微信模拟器/真机、App Vapor真机。本组没有重启服务、安装依赖或提交。
