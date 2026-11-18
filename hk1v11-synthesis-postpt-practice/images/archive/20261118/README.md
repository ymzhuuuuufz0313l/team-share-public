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

## t11→t19 换版快照（2026-11-18 动态列宽改造前）

§4.2 主图/精简图改「列宽按内容动态计算 + 画布加宽」前的改前字节快照（t19，标签
`1118t11pre`；`_9aa17f` 后缀为 anim 版防重名指纹）：

| 文件 | 原主名 | md5 |
|---|---|---|
| `power_compare_hk11_1118t11pre.svg` | `images/power_compare_hk11.svg` | `ae234c50d6b807b5f981dce10e8e0172` |
| `power_compare_hk11_1118t11pre_9aa17f.svg` | `images/anim/power_compare_hk11.svg` | （指纹后缀见文件名） |
| `power_compare_hk11_slim_1118t11pre.svg` | `images/power_compare_hk11_slim.svg` | `f51d3376f302f1be32105a92f0ed53db` |
| `power_compare_hk11_slim_1118t11pre.png` | `images/power_compare_hk11_slim.png` | — |
| `power_compare_hk11_1118t11pre.png` | back_ppt 主 PNG 快照 | — |

改后（t19 动态列宽版）主名 md5：`power_compare_hk11.svg` = 随内容推导（当前
`e4c4e05b712a84f75104bda292c158ac`，pad=10 与 PIL 同口径）；ch08 引用 `?v=20261118e`。

## §4.7 两图首版归档登记（R9，2026-11-18）

`power_module_compare_long_short` / `power_composition_donut_long_short`（静态 + anim + PNG，
tools/gen_long_short_charts.py 产出）为**首版即当前采纳版**（无被替换前身，不产生快照文件），
此处登记在案：生成器含 `--check` 幂等门与 Σ片==中心断言，尾签名动态时刻（F8）。

| 文件 | md5（2026-11-18 11:46 实测） |
|---|---|
| `images/power_module_compare_long_short.svg` | `dadf828a87ee0a9a471f74898ca2201c` |
| `images/anim/power_module_compare_long_short.svg` | `8e5b0a02ff4db6d63c5ba62bc0aa1a18` |
| `images/power_composition_donut_long_short.svg` | `681426f0592e4c7753269410d588f726` |
| `images/anim/power_composition_donut_long_short.svg` | `c4fb15d1d64b747210746b586197974f` |
| 生成器 `images/tools/gen_long_short_charts.py` | `5fe63e8d3ed52c91a5a0a4f9bf6f85ab` |

## slim 备用件标注（R10，2026-11-18）

`power_compare_hk11_slim.{svg,png}`（back_ppt + 站点 images）为**仓库备选件**：
仅入库备查，**未接入 ch08 正文、无 anim 版、不进搜索索引**；采纳与否由用户后续拍板，
如转正须补 MOTION_KIT 登记与 `?v=` 缓存串。

## 4K180 峰值高亮徽章删除前快照（标签 `1118peakfixpre`，2026-11-18）

用户 2026-11-18 报障：4K180 行「功耗数值上的高亮串行了」。根因是生成器在
`x=474 y=344 w=48 h=18` 画的一枚琥珀色悬浮药丸（`class="peakglow"`，外裹 `maxpulse`），
它落在 `-` 与 DPLC 数值列之间的**空白区**，无文字承托，判读时被当成下一列被高亮。
本次只删该悬浮装饰（峰值三角 `tri` 与脉动动效保留），并给 1118 长编码两行补青绿扫光。

改前原字节快照（`git show HEAD~1:` 取出，未改一字节）：

| 文件 | 原主名 | md5 | 大小 |
|---|---|---|---|
| `power_compare_hk11_1118peakfixpre.svg` | `images/power_compare_hk11.svg` | `c6f1f9c4b966f7a7238b4ec877274049` | 31726 B |
| `power_compare_hk11_1118peakfixpre_anim.svg` | `images/anim/power_compare_hk11.svg` | `c2f087576b6ee5e6f1246f075a535130` | 39556 B |

改后主名 md5（636×572 / 23 行）：

- `images/power_compare_hk11.svg` → `a91c9f92b991138f6f8d9bbf99898ca6`（31580 B）
- `images/anim/power_compare_hk11.svg` → `62df7d0eb3c81c1d8a351174a44b4396`（RESULT: PASS：
  `row_g=23 cellwave=32 purpband=3 cmpband3=2 pulse=5`）

ch08 引用缓存串升为 `?v=20261118g`（路径不变）。PNG 侧 `back_ppt/power_compare_hk11*.png`
由 PIL 生成、从未包含该药丸，本次未重生成。

<!-- ymzhu 2026-11-18 18:20 -->
