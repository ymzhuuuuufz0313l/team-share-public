# 20261117/1117v1 — 1117 代功耗图新版入档（3 张站点图 + 1 张三档表格图，共 11 份 + README）

日期 = 2026-11-17；版本标签 = **1117v1**；上一代同名快照 = 上层 `../` 的 `_1117v0`（数据 1015 口径 / 图版 1028）。
本子目录只收**本次新采纳**的新版；旧版快照与上层 README 原样保留，图永不删除。

数据口径：1117 新包 PowerPro，三档 total 取 `hier_pwr_detail.csv` 第 389 行（`L389`）逐字原值：
**3G 18474.63 µW = 18.47 mW / 4G 24153.53 µW = 24.15 mW / 4.46G 27044.19 µW = 27.04 mW**
（4.46G 即报告里写作 4.5G 的那一档；本站产物一律用 `4.46G` 标签，不出现 `4.5G`/`4g5`）。
模块级 8 组映射（@4.46G）：SHORT 10763.34 / DTCTL 4874.10 / PANEL_CTRL 3127.70 / BUFFER_I 2505.31 /
CONFIG 1600.46 / ANCTL 1260.73 / LONG 885.54 / CLKGEN 526.81，其他小模块 1500.20（= 旧 416 + 未分配残差 ≈1084 合并，
口径合并非新增功耗），差额 0.00。

**本目录当前入档的是 DPLC 18.087 修订后的终态字节**（2026-11-17 15:44~15:56 定稿的静态源与 PNG，t16/t19 结项后取）；
本轮先前的中间态字节（3G DPLC 留 `-`、3tier 五列、donut PNG 中心 25.65、module_compare 静态残留动画）均未作为最终归档保留。

## 0. 入档清单（11 份 + README，逐项状态）

| # | 文件 | 类型 | 状态 |
|---|---|---|---|
| 1 | `power_composition_donut_1v11_1v22_1117v1.svg` | 静态 SVG | ✅ 终态（1200×578，sha256 c8f8cda3…，无 `animation:`/@keyframes，1V22 8 段 cx=870 与 1117v0 逐行相同，中心 27044 µW） |
| 2 | `power_composition_donut_1v11_1v22_1117v1_anim.svg` | 动画 SVG | ✅ 终态（1200×578，sha256 8a01cef3…，md5 39aebe3b…，t23 复跑，扇区几何与静态逐值相同） |
| 3 | `power_composition_donut_1v11_1v22_1117v1.png` | PNG | ✅ 终态（md5 096370f3…，中心 27.04 mW，1V22 环 35.4/18.2/12.2/4.0/3.3/3.7 不变） |
| 4 | `power_module_compare_1v11_1v22_1117v1.svg` | 静态 SVG | ✅ 终态（1260×688，1V11 侧 11 组新值、峰值标签 10763.34，静态源已去残留动画） |
| 5 | `power_module_compare_1v11_1v22_1117v1_anim.svg` | 动画 SVG | ✅ 终态（1260×688，md5 0dc9bae4…，含峰值标签 10763.34） |
| 6 | `power_module_compare_1v11_1v22_1117v1.png` | PNG | ✅ 终态（md5 1d769422…，标签已固定两位小数 10763.34/4874.10/3127.70/2505.31…，与静态 SVG 写法一致） |
| 7 | `power_compare_hk11_1117v1.svg` | 静态 SVG | ✅ 终态（605×510，18→20 行；1117 代 3G 18.47 / 4G 24.15 / 4.46G 27.04 相邻升序紫色高亮；3G 行 **DPLC = 18.087**） |
| 8 | `power_compare_hk11_1117v1_anim.svg` | 动画 SVG | ✅ 终态（605×510，md5 38f8942f…，含 3G DPLC 18.087 与三档 18.47/24.15/27.04） |
| 9 | `power_compare_hk11_1117v1.png` | PNG | ✅ 终态（md5 06c28d6a…） |
| 10 | `power_1117_3tier_1117v1.png` | PNG | ✅ 终态（md5 44a11b97…，六列版面重出版） |
| 11 | `power_1117_3tier_1117v1.svg` | 静态 SVG | ✅ 终态（1494×641 **六列**，含 `<title>`，XML 合法；sha256 与 `back_ppt/power_1117_3tier.svg` 一致） |

## 1. 站点图（ch08 / §4.2 引用，3 张，各静态 + 动画 + PNG）

- **① 功耗组成环形图 §4.5.1** → 主名 `images/power_composition_donut_1v11_1v22.svg` / `images/anim/` 同名 / `images/png_preview/` 同名。
  1V11 侧 9 组新值合计 27044.19 µW（中心 27.04 mW，SVG 中心 27044 µW）；1V22 环 7 组数值与扇区几何**逐值不变**
  （6389/4196/3294/2201/727/588/674 µW，dasharray 与 1117v0 完全相同）。静态源不含任何动画声明（用户要求 1V22 环不得自己扫入/脉冲）。
- **② 模块级对比条形图 §4.5.1** → 主名 `images/power_module_compare_1v11_1v22.svg` / `images/anim/` 同名 / `images/png_preview/` 同名。
  1V11 侧 11 组换新值（标签保留源 2 位小数），画布 1200→1260 容纳峰值标签 10763.34；1V22 侧不动；静态源无残留 `animation:`。
- **③ 功耗一览表图 §4.2** → 主名 `images/power_compare_hk11.svg` / `images/anim/` 同名 / `images/png_preview/` 同名。
  相对 1117v0 补入 1117 代 3G 18.47 与 4.46G 27.04 两行（与 4G 24.15 相邻升序、紫色高亮），既有 18 行零改动；
  **1117-3G 行 DPLC 列 = 18.087 mW**（用户新增数据，不新开行）。

## 2. 仅留档、不挂站的第四张图（1 张）

- `power_1117_3tier_1117v1.png` + `power_1117_3tier_1117v1.svg` — 「HK1V11 (1117) 三档功耗」表格图，**三行六列**：
  Clk 145 / Process 310144 / Area 310144 / Lane 1L / Normal (mW) 18.47·24.15·27.04 / **DPLC (mW) 18.087·`-`·`-`**（3G 有值，4G/4.46G 为 `-`）。
  源 = `E:\project\HK1V11\back_ppt\power_1117_3tier.png|.svg`（t16 后六列终版），本目录副本 sha256 与源逐字节一致
  （png 7bf0b3fd… / svg 680f7f10…）。
  **本站任何页面都不引用它**（`grep -rn 3tier --include=*.html` 零命中），纯图版留档；PNG 只进日期夹，不落站点根。

## 3. 归档规矩（本轮执行情况）

- 只新增：本子目录为新建；上层 `20261117/` 的 11 份 `_1117v0` 文件 md5 前后逐一不变（`V0_UNCHANGED`），
  它们是本轮"1V22 侧逐字节不变"比对的事实源。
- 站点根无 PNG（本站 PNG 只进 `images/archive/<日期>/`；`images/png_preview/` 为预览中间区）。
- 主名 SVG（`images/*.svg`、`images/anim/*.svg`）由作图/动画成员写，本子目录只做快照，不回写主名。
- 中间态处置：donut / module_compare / power_compare_hk11 的动画 SVG 曾于 15:28~15:41 取过一版，
  因 t18 复跑生成器、字节必变，已按 captain 指示撤出（未作为 1117v1 归档留存）；
  最终三份动画 SVG 于 t18 定稿后重取（md5 9cfc0647… / 0dc9bae4… / 38f8942f…，与 svg-anim 两轮幂等值一致），静态与 PNG 亦按终态字节重新覆盖同名归档文件。
  另：`power_module_compare` 的 PNG 因标签小数位与静态源不一致（`4874.1` vs `4874.10`），按 captain 指示等 t20 重出后再取（终版 md5 1d769422…，PNG 标签固定两位小数）。
- donut 副标题随 1117 数据修正（1V11 已含全部分类；1V22 未含未分类 ~0.9 mW）：
  文案由「…（top-N+其他，未含未分类 ~1.0 mW）」改为「…（top-N+其他；1V11 已含全部分类，1V22 未含未分类 ~0.9 mW）」。
  2026-11-17 16:18 静态源（t21）与 16:22 动画产物（t23）重取；与上一版快照逐行 diff **只有这一行副标题**，
  环形 dasharray 几何、图例位置、中心 27044 µW / 27.04 mW、九组数值与顺序、1V22 环 8 段 cx=870 均未变（1V22 与 1117v0 逐行相同）；
  PNG 不受影响（副标题只在 SVG 内，donut PNG 仍 md5 096370f3…）。
- 字节溯源核对（captain 问及 `images/power_module_compare_1v11_1v22.svg` mtime 15:56 晚于 t19 的 15:53）：
  本目录归档副本 sha256 = `b02cbd8a83adfa60919ecf71e5384c98e3d09baf70a66e2cd51a151e0eeebb93`，
  与当前工作区 `images/power_module_compare_1v11_1v22.svg`（9559B，mtime 2026-11-17 15:56）**逐字节相同**；
  该文件无残留 `animation:`、viewBox 1260×688、标签两位小数，与 t20 产出的 PNG 标签口径一致，故归档即最终字节。
- 计数：`images/archive` 93（改动前）→ **105**（11 份图 + README，+12）；`find images/archive -type f | wc -l` = 105。

## 4. 入档 sha256（终态，取 2026-11-17 15:44~15:56 源）

| 文件 | sha256 |
|---|---|
| `power_composition_donut_1v11_1v22_1117v1.svg` | c8f8cda38e53b7f543fcadc19d89a1ae98a205d53f4b2739aa539d2ef9d50e43 |
| `power_composition_donut_1v11_1v22_1117v1.png` | 76342a1e049f3a1aeea9161751992e16f2a2e43370be40a25c04d9916787d7d8 |
| `power_module_compare_1v11_1v22_1117v1.svg` | b02cbd8a83adfa60919ecf71e5384c98e3d09baf70a66e2cd51a151e0eeebb93 |
| `power_module_compare_1v11_1v22_1117v1.png` | c89af8da3490f6a31d19b82147d9e5b4ebdc8962de88e704303da96190e9156e |
| `power_compare_hk11_1117v1.svg` | 7e0ac04084f4aed90dfdde4295444293f254cc4119130d01e3eff39890a09c31 |
| `power_compare_hk11_1117v1.png` | 1f971ee27b670a10f174bcba78e581ceda159fbdcdaf96fe004ea87a480f1b90 |
| `power_1117_3tier_1117v1.svg` | 680f7f1028402a7b224bc13cf522cdcaf6ff1a7acaf6ad5621ba0fe86b698387 |
| `power_1117_3tier_1117v1.png` | 7bf0b3fdeaffdf428c2e4b6d78d479d752763c1d6a30ef989f5acce84a7f4013 |
| `power_module_compare_1v11_1v22_1117v1.png` | 5b783553088af6b3585074c636d8235e657ed0b2decc6b6ea3f4687e81143af9 |
| `power_composition_donut_1v11_1v22_1117v1_anim.svg` | 8a01cef381adc9f083291d5319395f0de3ae1b795392ac91149c2e6d6ab0031b |
| `power_module_compare_1v11_1v22_1117v1_anim.svg` | a3ebadcd0ce3b7eff66706d3b09d39ab38e229f732525ac1d736ff0198047a03 |
| `power_compare_hk11_1117v1_anim.svg` | 4c100f3e78eba7a325bbf5e56c7273197bfbd2465c67deeeb34e204ae3755ccd |

<!-- ymzhu 2026-11-17 16:28 -->
