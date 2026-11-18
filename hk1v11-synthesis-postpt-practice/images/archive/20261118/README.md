# 20261118 图版归档 — power_compare_hk11（版本标签 canon1）

采纳日期 = 2026-11-18；版本标签 = **canon1**；被替换的上一版 = **1117v0/1117v1/1117v2 线**
（同图，见 `images/archive/20261117/`）。依据 `images/tools/README.md` 图版标准：
主名 = 当前采纳版；被替换版本快照进 `<采纳日期>/` 带版本标签；图永不删除。

## 为什么改（口径收口，非数据变更）

用户 2026-11-18 裁示消除本图内的三处「历史口径例外」，目标是让生成器
`script/_chapter_viz/gen_power_compare_hk11_svg.py` 从零重生成的产物与线上文件逐字节一致，
且生成器里不再有硬编码例外。三处：

1. **N-4 条形宽**：`_BAR_W_OVERRIDE` 撤除。HK1V11 (1117) 4G 条宽由历史手工 30px 回归公式
   `round(24.15 × 1.16) = 28`，与相邻 24.42 → 28 单调一致。唯一可见几何变化（2px）。
2. **N-6 y 整数格式**：`Y_INT_FROM_ROW` 撤除。r11..r20 的 `y="309"` 类整数复刻统一改为
   规范 `%.1f`，共 80 处纯格式 diff、零视觉变化。
3. **`_LABEL_OVERRIDE` 硬编码**：字典撤除，改为通用显示格式函数 `_disp_num()`。
   21 行 × 3 个数值列共 63 格逐格比对，**显示串零变化**：`13.65` / `16.3` / `16.3`
   三格仍由数据源 `13.650` / `16.30` / `16.30` 推导得出；`17.00` 等小数部分全零的
   两位整值保持原样。

## 归档文件（改前原字节，`cp -p` 语义，未改一字节）

| 文件 | 原主名 | md5 | 大小 |
|---|---|---|---|
| `power_compare_hk11_canon1.svg` | `images/power_compare_hk11.svg` | `0e6203b0f90ee39ea27fabeba4cc100c` | 26912 B |
| `power_compare_hk11_canon1_anim.svg` | `images/anim/power_compare_hk11.svg` | `90001e1bfe4110fc32d0f539933b3948` | 34416 B |

改后主名 md5（供复跑核对）：

- `images/power_compare_hk11.svg` → `138493527a7c3be0b3fbf4751545e3bb`（27072 B，LF）
- `images/anim/power_compare_hk11.svg` → `2b4a847579c004acfcf3f90bf618d627`（34576 B，LF）

## 复跑方式（从零复现，两次 md5 恒定）

```bash
cd E:/project/HK1V11
python script/_chapter_viz/gen_power_compare_hk11_svg.py --out /e/tmp/fixA   # 两次 → md5 恒定
python script/_chapter_viz/gen_power_compare_hk11_svg.py                     # 覆盖主名
python script/_chapter_viz/gen_power_compare_hk11_svg.py                     # 再跑 → SKIPPED（幂等）
cd E:/project/team-share-public/hk1v11-synthesis-postpt-practice/images/anim
python make_anim_power_compare_hk11.py                                       # 动画版派生，RESULT: PASS
```

## PNG 说明

`images/png_preview/power_compare_hk11.png`（2427×2073）是 **back_ppt 表格版 PNG** 的
站点预览副本（= `back_ppt/power_compare_hk11.png` 逐字节同源），由
`back_ppt/gen_power_compare_hk11_site.py` 生成，**不从本 SVG 派生**，本图几何/格式调整
不影响它，故本次未重生成、未归档。

## 引用

站点引用 `ch08-powerpro.html` 的 `./images/anim/power_compare_hk11.svg`，
缓存查询串由 `?v=20261117b` 升为 `?v=20261118a`（仅防缓存，路径不变）。

<!-- ymzhu 2026-11-18 09:36 -->
