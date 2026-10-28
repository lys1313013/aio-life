# 手机端设计提示词

使用内置 imagegen，以三版桌面稿为参考生成静态手机端对比图。

Use case: ui-mockup.
Create a polished high-resolution comparison board showing THREE mobile homepage designs of the Chinese personal life management application AIO-LIFE, corresponding to the desktop directions in reference images. Each of the three columns must show a complete flat front-on mobile viewport, approximately 390 by 844 logical pixels, rendered at high resolution. No physical phone mockups or perspective. Neutral light gray surrounding canvas, generous even gutters. Small editorial labels above columns: "01 深色极简", "02 暖白简洁 · 推荐", "03 柔和彩色". Three equally sized mobile screenshots, not desktop layouts shrunk down. This is a responsive design concept with exceptionally legible Simplified Chinese. Use consistent content and arrangement across the three for fair comparison.
Reference images 1, 2, 3: desktop brand and visual style references only, respectively dark, warm white, soft color. Preserve the AIO-LIFE logo.
MOBILE INFORMATION ARCHITECTURE:
- No desktop sidebar, no browser chrome, no desktop multi-tab row.
- Slim mobile header includes small AIO-LIFE logo and wordmark at left; search and notification icon buttons at right, adequately sized tap targets.
- Under header a modest "今日" title, small "9月27日 周日" date and icon-only page settings.
- Compact daily overview surface with FIVE equal mini-columns for 每日一题 / GitHub / 运动 / 单词 / 阅读. Each has a tiny recognizable simple icon, short label and value: 待完成 / 0 / 0 / 待打卡 / 0分钟. Use neutral or muted amber pending states, never bright red. No tiny multi-line secondary streak text on mobile. All five must fit elegantly across width without overflow.
- Primary full-width 时迹 card, approx 170 logical px tall. Header 时迹 with a small chevron. Content has a modest delicate empty ring on left, 0h 00m and 今日暂无记录 at right, clear modest "开始记录" button. Small quiet 0—6—12—18—24 time strip at bottom. NO enormous empty donut, NO fake progress data.
- Immediately a compact full-width 待办 card, small count 1, plus button. Exactly one unchecked task "skillhub 文档优化代码提交" wrapping naturally to max 2 lines if needed, tiny subdued AI badge. Do not add dummy tasks or motivational subtitles.
- Compact 快捷导航 section: FOUR equal touch-friendly icons in a single row with short labels 闪念 / 目标 / 支出 / 更多. 更多 represents the full module menu, no attempt to cram all 11 desktop shortcuts into the initial mobile screen.
- A compact 闪念 preview below with two notes "思之所至，行之所达" and "完成 > 完美", tiny pin icons, no dates needed here. Optional top edge of next "运动" section near viewport bottom signals vertical scrolling; exercise and GitHub commit feed are BELOW THE FOLD, do not attempt to show every dashboard section at once.
- Persistent bottom navigation aligned at same height in all three screenshots, five targets: 主页, 时迹, central circular plus action with no text, 待办, 我的. Home selected. Minimum 44px touch targets and iOS safe area with home indicator below. Bottom nav must not obscure content; visible content ends above it. All mobile cards use ~16px outer margin, 12px gaps. Crisp consistent outline icons, correct simple legible Chinese typography.
STYLE 1 dark: graphite #111315 background, #1b1e23 surfaces, warm white text, slate secondary text, restrained lavender selected navigation and button, subtle boundaries, zero neon/glow.
STYLE 2 warm: warm offwhite #f6f5f1 canvas, white surfaces, ink type, muted forest green actions and active nav. Elegant calm and readable, subtle corners and almost no shadow, airy but not wasteful.
STYLE 3 soft color: pale cool gray canvas, white surfaces, gentle lavender 时迹 card, pale cream note preview, restrained violet actions, subtle mint accent icons. Sophisticated not toy-like.
Avoid: verbose explanatory copy, decorative slogans, big illustrations, tiny text, horizontal scrolling screenshot, split desktop columns within mobile, unrelated finance metrics, fake successful daily stats, duplicated navigation items, gigantic headings. Design must be immediately plausible to implement as an actual Vue responsive page.
