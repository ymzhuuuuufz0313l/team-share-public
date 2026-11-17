# 20261117 图版归档 — power_compare_hk11（版本 1117v0）

采纳日期 = 2026-11-17；版本标签 = **1117v0**；被替换的上一版 = **1027v0**
（依据 `images/tools/README.md` 头部图版标准：主名 = 当前采纳版；被替换套图快照进 `<采纳日期>/` 带版本标签；PNG 只进日期夹；图永不删除。）

## 本次采纳 1117v0（新增 HK1V11 (1117) 4G 行：Area 310144 / Normal 24.15，紫色高亮）
- `power_compare_hk11_1117v0.svg` — 静态源，18 行，viewBox 0 0 605 466（= 主名 `images/power_compare_hk11.svg`）
- `power_compare_hk11_1117v0_anim.svg` — 动画产物，18 行，605×466（= 主名 `images/anim/power_compare_hk11.svg`）
- `power_compare_hk11_1117v0.png` — 站点版 PNG 快照 2427×1809（`gen_power_compare_hk11_site.py` 产物，原站点根 `power_compare_hk11.png` 移入）
- `power_compare_hk11_1117v0_anim.png` — 动画 SVG 无头 Edge 渲染快照 1210×940（DPR2，window 605×470）
- `power_compare_hk11_1117v0_flattable.svg` — 2427px 纯平表矢量版（`gen_power_compare_hk11_static_svg.py` 产物，原站点根 `power_compare_hk11_static.svg` 移入；无 html 引用、非本站主名，保留不删）

## 上一版快照 1027v0（17 行，取自 git HEAD = commit 247b1b1）
- `power_compare_hk11_1027v0.svg` — 修改前静态源，17 行，605×444
- `power_compare_hk11_1027v0_anim.svg` — 修改前动画产物，17 行，605×444

替换关系：`images/` 与 `images/anim/` 两份主名的 1027v0 内容由 1117v0 替换升为当前采纳版；站点根两份无主副本（PNG、flat SVG）归入本日期夹，不再占站点根。

## 补丁前快照 1102v2（三张表图动画 SVG，取自修复前 git HEAD）
原因是这三份动画产物里有多条 `animation:` 引用了**文件内从未定义的 `@keyframes`**（GLOW/BREATH 类装饰
动效），浏览器一律按无效动画处理，等于永远不动。修复方式：只补 CSS `@keyframes`（不动文字/数字/几何），
并清掉三份静态源里同名的死 `animation:` 声明。修复前后图像素差证据见 t18 验收记录。

- `delay_skew_14vs12_1102v2.svg` — 修复前动画产物（= 修复前 `images/anim/delay_skew_14vs12.svg`）
- `dc_area_evolution_table_1102v2.svg` — 修复前动画产物（= 修复前 `images/anim/dc_area_evolution_table.svg`）
- `dc_gen_summary_table_1102v2.svg` — 修复前动画产物（= 修复前 `images/anim/dc_gen_summary_table.svg`）

替换关系：三份主名内容由 1102v2 替换为 1117 版（补 keyframes 后重跑生成器），旧版只进本日期夹，不删除。

<!-- ymzhu 2026-11-17 14:12 -->

