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

## 被替换快照 1117v0（ch08 §4.5.1 两张功耗组成图，改主名前快照）

采纳日期 = 2026-11-17；版本标签 = **1117v0**；对象 = `power_composition_donut_1v11_1v22`（双环形图）
与 `power_module_compare_1v11_1v22`（模块对比双条图）。快照在 chart-render 改写主名前一刻取，按
「图永不删除」只新增：`images/` 与 `images/anim/` 主名未动、既有归档文件未动。

来源版本口径（逐项可查，不混代）：
- **数据 1015 口径**：1V11 侧 = 1015V3 `rep_dir/`（Top 25645.40 µW），1V22 侧 = 1015V1
  `rep_1lane_4p5g_dir/`（18969 µW），同日 2026-10-15 同工具（PowerPro 2024.2_1）/同库 PowerPro Initial
  4.46G；硬编码在 `E:\project\HK1V11\back_ppt\gen_power_composition_charts.py`（v2，2026-10-21，
  站点暖纸皮肤版），可逐 µW 由 CSV 层级子树 total 复算。
- **图版 1028 口径**：静态 SVG 落盘 2026-10-28 15:37 / 18:55；动画版 = Motion Kit **v4**
  （用户 2026-10-28 验收：donut 去掉行进列车、bar 去掉整区扫光），落盘 2026-10-28 19:22，
  生成器 `images/anim/make_anim_power_composition_donut_1v11_1v22.py` /
  `make_anim_power_module_compare_1v11_1v22.py`。
- 与 **1027 口径**（`power_compare_hk11` 的 1015/1027 系列、`images/archive/20261027/`）**不同图不同代**，
  本次不与之混用；本目录上半部分的 `power_compare_hk11` 1117v0 是另一张图，见上节。

文件（sha256 已与源逐字节比对一致）：
- `power_composition_donut_1v11_1v22_1117v0.svg` — 替换前静态源 1200×578（= 原 `images/power_composition_donut_1v11_1v22.svg`，1200×578）
- `power_module_compare_1v11_1v22_1117v0.svg` — 替换前静态源（= 原 `images/power_module_compare_1v11_1v22.svg`，1200×688）
- `power_composition_donut_1v11_1v22_1117v0_anim.svg` — 替换前动画产物 v4（= 原 `images/anim/power_composition_donut_1v11_1v22.svg`，ch08 §4.5.1 引用路径）
- `power_module_compare_1v11_1v22_1117v0_anim.svg` — 替换前动画产物 v4（= 原 `images/anim/power_module_compare_1v11_1v22.svg`）
- `power_composition_donut_1v11_1v22_1117v0.png` — 站点版 PNG 快照 1200×578（原 `images/png_preview/power_composition_donut_1v11_1v22.png`，2026-10-26）
- `power_module_compare_1v11_1v22_1117v0.png` — 站点版 PNG 快照 1200×688（原 `images/png_preview/power_module_compare_1v11_1v22.png`，2026-10-26）

PNG 口径：本站根无 PNG（依图版标准 PNG 只进日期夹）；上述两份为 `images/png_preview/` 站点预览副本的 1×（= viewBox 尺寸）快照。
`images/archive/20261028/` 内另有同两张图的 2.2× 高分辨 PNG（2664×1284 / 2756×1580），按「不删除、不改动」原样保留，本次未触碰。

替换原因：新 1117 包（`rep_dir_1lane_4g_1117/` 等 3G / 4G / 4.46G 三档，4.46G 真值 27044.19 µW，
报告名作 4.5G）重生成这两张图；旧 1015 口径 + 1028 图版作为历史留档快照入库，主名由新版覆盖，
引用路径不变（动画 SVG 走 ch08 §4.5.1）。

<!-- ymzhu 2026-11-17 15:10 -->

