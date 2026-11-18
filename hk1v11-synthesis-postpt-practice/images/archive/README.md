# images/archive/ — 图版快照与重复对账

> 规则：图**永不删除**；主名 = 当前采纳版；被替换/发布过的版本快照进 `<采纳日期>/`（PNG 只进日期夹）。
> 本文件由 `images/tools/archive_snapshot.py` 在生成器收尾时自动维护「快照登记」表；
> 「同 md5 快照对账」由 2026-11-17 审计 A6-2 补入（人工核对，结论见下）。

## 一、同 md5 快照对账（A6-2，2026-11-17 全树扫描）

扫描范围 `images/archive/` 全树 119 个文件，命中 **11 组 md5 重复**，逐组给「保留的规范件」与重复关系。
**本次未删除、未移动任何一个文件**：重复件本来就全部已经位于 `images/archive/` 内（不存在"主名位置也有重复件"的情况），再搬一次不会带来任何收益，且与"图永不删除"规则冲突；根治手段是让生成器收尾自动快照并做 md5 去重（`images/tools/archive_snapshot.py`，同 md5 台账已存在则跳过拷贝）。

| # | md5 | 规范件（保留） | 重复件 | 关系说明 |
|---|---|---|---|---|
| 1 | `b1894312…` | `20261117/1117v1/power_composition_donut_1v11_1v22_1117v1.svg` | `20261117/v22label1/power_composition_donut_1v11_1v22_v22label1.svg` | F1 只改 1V22 环末组标签文案（静态 SVG），几何/数据未变 → 与 1117v1 **字节相同** |
| 2 | `39aebe3b…` | `20261117/1117v1/…_1117v1_anim.svg` | `20261117/v22label1/…_v22label1_anim.svg` | 同上（动画版） |
| 3 | `096370f3…` | `20261117/1117v1/…_1117v1.png` | `20261117/v22label1/…_v22label1.png` | 同上（PNG 快照） |
| 4 | `a57a524e…` | `20261117/3gv1/power_composition_donut_1v11_1v22_3g_3gv1.svg` | `20261117/v22label1/…_3g_v22label1.svg` | F1 只改 4.46G 环末组标签，3G 环未触及 → v22label1 的 3G 件与 **3gv1** 字节相同 |
| 5 | `836300c0…` | `20261117/3gv1/…_3g_3gv1_anim.svg` | `20261117/v22label1/…_3g_v22label1_anim.svg` | 同上（动画版） |
| 6 | `0c334c82…` | `20261117/3gv1/…_3g_3gv1.png` | `20261117/v22label1/…_3g_v22label1.png` | 同上（PNG 快照） |
| 7 | `98f9b6c1…` | `20261117/1117v1/power_compare_hk11_1117v1.svg` | `20261117/1117v2/power_compare_hk11_1117v1.svg` | `1117v2/` 夹内文件**连版本标签都写着 v1**，内容与 1117v1 字节相同 → 该夹无独有内容 |
| 8 | `38f8942f…` | `20261117/1117v1/…_1117v1_anim.svg` | `20261117/1117v2/…_1117v1_anim.svg` | 同上（动画版） |
| 9 | `06c28d6a…` | `20261117/1117v1/…_1117v1.png` | `20261117/1117v2/…_1117v1.png` | 同上（PNG 快照） |
| 10 | `089b6641…` | `20261028/power_compare_hk11.png` | `20261027/power_compare_hk11_1027v0.png` | 1027v0 快照与次日归档的 1028 主件字节相同（同一份 1027 代交付图，隔日重复留档） |
| 11 | `7f8d82f0…` | `qa/20261104/_ch09_full.png` | `qa/20261104/_ch09_live.png` | QA 截图 `full`/`live` 两态同图（`qa/` 为质检产物夹，非正式图版） |

补充说明：
* 第 1–6 组共 **6 件** 就是审计 A6-2 报告的 `v22label1` 冗余（3 件对 1117v1、3 件对 3gv1）；第 7–9 组（`1117v2` 夹装 v1 内容）与第 10、11 组为 2026-11-17 交叉复核（N3）补报的漏项。
* 各组「规范件」的选法：同内容取**更早采纳 / 语义更好的那个标签**（1117v1 与 3gv1 是当时的采纳版；1028 主件是采纳日）。
* 后续如需清理重复件，**只能**在用户明确同意后做"移动进 `_dup/` 子夹 + 保 md5 台账"，不得删除。

## 二、快照登记（自动追加）

| 日期 | 文件 | md5 | 大小 | 说明 |
|---|---|---|---|---|
| 20261102 | `skew_probe_audit_1028_static.svg` | `41239d5c418cc0afef3b3ca28685af09` | 30763 B | skew_probe_audit_1028 静态版（A9-1 自动化归档） |
| 20261102 | `skew_probe_audit_1028_anim.svg` | `c12c933d3c1604bfcae67847d2acd452` | 34715 B | skew_probe_audit_1028 动画版（A9-1 自动化归档） |

| 20261118 | `power_compare_hk11_canon1.svg` | `0e6203b0f90ee39ea27fabeba4cc100c` | 26912 B | 改前静态源（21 行，条形宽 30px 例外 / y 整数格式 / 3 处显示串硬编码）；N-4+N-6+标签例外收口前快照 |
| 20261118 | `power_compare_hk11_canon1_anim.svg` | `90001e1bfe4110fc32d0f539933b3948` | 34416 B | 改前动画产物（由改前静态源派生，21 行）；N-4+N-6+标签例外收口前快照 |
| 20261118 | `power_composition_donut_1v11_1v22_canon2.svg` | `7ad2cfd443fde919ed78623db82c16d7` | 16118 B | 改前静态源（7 片环形、中心 18970、片和 18069 缺口 901 µW 未成片、百分比按 18069 分母）；N-5+A0-7 残差成片 + 分母改中心前快照 |
| 20261118 | `power_composition_donut_1v11_1v22_canon2_anim.svg` | `d879486d13b1a9b96d134b452862c112` | 22301 B | 改前动画产物（由改前静态源派生，7 片）；同上快照 |
| 20261118 | `power_composition_donut_1v11_1v22_canon2.png` | `b2c97face80d0741b6bf75d645355afa` | 291478 B | 改前 PNG 预览（7 片）；同上快照 |
<!-- ymzhu 2026-11-18 09:56 -->
| 20261104 | `51_signoff_setup_hk11_1104v2.svg` | `82ac123013352aa19b3ed25f16de2399` | 55395 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `51_signoff_setup_hk11_1104v2_anim.svg` | `2411d9da232f879ef1133f7766d86722` | 55797 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `52_signoff_hold_hk11_1104v2.svg` | `8f7c96bb72f1d8ebb4eb2fff1f37724d` | 52367 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `52_signoff_hold_hk11_1104v2_anim.svg` | `b17f304fc965187ab2feeea2cf87f953` | 52769 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `53_signoff_trans_hk11_1104v2.svg` | `88f8c432872008e8a826be945f48a0dd` | 9790 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `53_signoff_trans_hk11_1104v2_anim.svg` | `278a353c25068f679b937aa4b40beef9` | 10786 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `54_signoff_physkew_hk11_1104v2.svg` | `80308fef3f1b283ead5f205b18d1fb81` | 19269 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `54_signoff_physkew_hk11_1104v2_anim.svg` | `4dd74a004db527606ae44d8f39374271` | 20265 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `55_signoff_sdskew_margin_hk11_1104v2.svg` | `31f2ee121be0b61f9b888acccf32c2d8` | 29054 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `55_signoff_sdskew_margin_hk11_1104v2_anim.svg` | `833fbe5b33a8619eab44bdd1782409bc` | 30050 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `56_signoff_shift_window_hk11_1104v2.svg` | `2d6185a55704e1aa88a70e1477374f15` | 10607 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261104 | `56_signoff_shift_window_hk11_1104v2_anim.svg` | `6ea50adf643f7046c6791dc5280bcec3` | 11538 B | 被 1118V1 换版替换（1104V2 代主名快照） |
| 20261118 | `51_signoff_setup_hk11_1118v1.png` | `4d4e1aebd63014661bd1c2aaa2805186` | 646781 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `52_signoff_hold_hk11_1118v1.png` | `b90db526a8f0e0719582251de6afe41e` | 592137 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `53_signoff_trans_hk11_1118v1.png` | `6f8ddd4412306c790a987b2c31d95ae9` | 95446 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `54_signoff_physkew_hk11_1118v1.png` | `c5bc25d609c564fe58778b323f79d993` | 202074 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `55_signoff_sdskew_margin_hk11_1118v1.png` | `cfc9dac88efc594a94a00dda15677840` | 311494 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `56_signoff_shift_window_hk11_1118v1.png` | `9bbb8efcd35f01a23fc674345dd9ed51` | 219114 B | 1118V1 新代 DPR2 PNG 快照（render_png_1118v1.py，verify 全过） |
| 20261118 | `ch09-to-signoff_1104v2.html` | `7392aa53ba4d3a961cab73b4e12a8764` | 21382 B | 被 1118V1 页面换版替换（1104V2 canonical 整页快照：含 1029V0/1008V3/0918V2 对比卡、V0↔V2 对比段与逐角换算表——历史段落可追溯入口） |
