# module_compare 4g5 格式收口前快照（N-7 / N-8，2026-11-18）

本目录保存 `power_module_compare` 链在「格式收口」**之前**的线上字节，供追溯。
收口动作：让生成器成为唯一权威，把 4g5 静态件按生成器统一规范格式重生成，并重建动画版。

## 静态件（结构与手写基线同名同内容 → 复用，不重复归档）

- 收口前在网静态件：`images/power_module_compare_1v11_1v22.svg`
- md5：`a8bca20b724087dbeb24ebd34ec8efea`（9559 B，LF）
- 该字节已完整保存在
  `images/archive/20261117/power_module_compare_1v11_1v22_handwritten/power_module_compare_1v11_1v22.svg`
  （t29 归档，md5 相同）。故本目录**不再新建同名快照**，直接以 20261117 归档为收口前基线。

## 动画版（本次新归档）

- 收口前在网动画版：`images/anim/power_module_compare_1v11_1v22.svg`
- 本目录副本：`power_module_compare_1v11_1v22_anim.svg`
- md5：`0dc9bae49b400c03ea679a00f5a89cc9`（13870 B，LF）
- 该动画版由 `images/anim/make_anim_power_module_compare_1v11_1v22.py` 读静态件生成；
  静态件重生成后动画版同步重生成，故先归档原字节。

## 收口后的口径（摘要）

- N-7：几何数字统一「一位小数、整数去尾 .0」（`389.0→389`、`280.0→280`）；
  数值标签整数不补小数尾巴（`8590.00→8590`）。
- N-8：箭头 `↔`/`→` 纯 unicode 直出，由站点既有 `font-family` 渲染；
  `tspan class="mono"` 只给纯 ASCII 标识符，不再复刻手写件的 mono 分支（6 处差异归零）。
- 3G 档（`_3g` 两件）历史即生成器产物、逐字节一致，本次不动。

<!-- ymzhu 2026-11-18 09:40 -->
