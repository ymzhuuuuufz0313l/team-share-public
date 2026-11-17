# image/tools/ — 图版生成脚本归拢（2026-11-04 起执行的图版标准）

> 本目录是本站（synthesis-integration-flow-guide，2M23 指南站）**图生成脚本的唯一归拢位置**（图版归档标准：主名 = 当前采纳版；被替换套图快照进 `image/archive/<日期>/` 永不删除；图永不删除）。
> 本站沿用既有 `image/`（单数）目录惯例，未改名 `images/`；新增 `image/archive/`（含 `qa/`）与 `image/tools/` 骨架。
> 2026-11-04 自 `script/` 迁入 7 个生成脚本（`git mv` 不适用——`script/` 本就被仓库根 `.gitignore` 排除，见下方「入库边界」）。

## 脚本清单（每个脚本生成哪组图）

| 脚本 | 生成物 | 说明 |
|---|---|---|
| `_gen_be_review_images.py` | `image/01..17`、`24..27`、`30..31`（setup/hold/trans/physkew PNG）、`32`、`35`、`36`、`37`、`38`、`39`、`40`、`41`、`42`、`43` 等 PNG（BE Review 全套结果图） | **PIL 2x 超采样绘制器**（代码片段图 + 表格图两类渲染器）；数据源 = `server-reports/`（入库）+ HV2M23/SYNTHESIS 本机真实报告（内部路径，仅本机可跑）；幂等 |
| `_gen_flow_svg.py` | `image/script-flow-overview.svg`（静态主名位，事实源） | 脚本调用关系总图（style-1 flat icon）静态版生成器；迁入后 `..` 相对 `__file__` 恰解析到静态主名位；`image/anim/script-flow-overview.svg`（动画版）由 `make_flow_anim.py` 从本静态源生成 |
| `gen_clkperiod_image.py` | `image/26_clk_period.png` | 从真实 `clk_period.tcl`（HV2M23 本机路径）取行 → 复用 `_gen_be_review_images.py` 渲染器出代码片段图；与本目录 `_gen_be_review_images.py` 同目录 import |
| `gen_postpt_tables_anim.py` | `image/anim/30_postpt_{setup,hold,trans}_{2p,1p}.svg` + `image/anim/31_postpt_{setup,hold,trans}_1p.svg` | postPT 四指标表（2P/1P）动画 SVG 确定性生成器：直读 `server-reports/postpt_summary/POST_PT_{2P,1P}/report_*.csv`；内置六项校验（XML/无 script/keyframes/转录逐值/行数/幂等）；用法 `--metric setup|hold|trans --mode 2P|1P` |
| `gen_postpt_skew_tables_anim.py` | `image/anim/30_postpt_{trans,physkew}_{2p,1p}.svg`、`image/anim/31_postpt_physkew_1p.svg`、`image/anim/33_postpt_sdskew_margin_2p.svg`、`image/anim/34_postpt_sdskew_margin_1p.svg` | postPT trans/physkew/sdskew-margin 六张表动画 SVG 生成器（同上六项校验）；用法 `--all` 或 `--metric trans|physkew|sdskew --mode 2P|1P` |
| `gen_buf_type_anim.py` | `image/anim/38_buf_type.svg` | IO 首/末级 buffer type 统计双栏表动画 SVG 生成器：直读 `server-reports/{input,output}_port_{first,last}_buf_type.tsv`；幂等 |
| `make_flow_anim.py` | `image/anim/script-flow-overview.svg`（动画版） | 从静态主名 `image/script-flow-overview.svg` 确定性重建动画版（flowdot 装饰 + 虚线 dash march）；幂等，md5 可复验 |
| `gen_power_compare_descramble.py` | `image/power_compare_descramble_1106.png` | descramble/noscramble 2lane 1.6G 单独对比图（1106，teal 6 列同款模板）；**数值从 `image/tools/data/descramble_power.json` 读取**（与页面表格同源）；4x 超采样 + 单字体整串 + ascent 居中（pil-table-render teal 节合规） |
| `gen_descramble_power_table.py` | `memory-power.html` 的 `AUTO-GEN:descramble_power` 块 | 把 `image/tools/data/descramble_power.json`（含 provenance / 原始报告缺失标记）渲染成页面 markdown 表格；`--check` 用于 QA 一致性校验 |
| `archive_history.py` | `image/archive/<日期>/…` + `image/archive/MANIFEST.md` | 把 `image/` 下每张图在 git 历史里的每个不同版本导出成可浏览快照；`--check` / `--apply` |
| `_archive.py` | 被生成脚本调用的归档动作 | `snapshot(path)`：覆盖前把磁盘旧版存进 `image/archive/<今天>/<stem>_<HEAD7>.ext`（同内容不重复存） |
| `normalize_kit_v4.py` | `image/anim/*.svg`、`image/script-flow-overview.svg` | Kit v4 幂等修正：删游离 CSS 残片、补 `prefers-reduced-motion`、根元素 `pt`→px；`--check` / `--apply` |
| `validate_kit_v4.py` | 只看不写 | Kit v4 机器校验：XML 良构 / 无 `<script>` / 无外链 / keyframes / reduced-motion 唯一 / 单位 / 与静态版几何+文字一致 |

## 复跑（在站点根目录下）

```bash
cd E:/project/team-share-public/synthesis-integration-flow-guide
P=script/.venv/Scripts/python.exe   # 虚拟环境仍在 script/.venv（含 PIL 等）

$P image/tools/_gen_be_review_images.py      # BE Review 全套 PNG（含 HV2M23 本机数据源，仅本机可跑）
$P image/tools/_gen_flow_svg.py              # 静态主名 script-flow-overview.svg
$P image/tools/make_flow_anim.py             # 动画版（从静态主名重建）
$P image/tools/gen_postpt_tables_anim.py --metric setup --mode 2P   # ×4 组合
$P image/tools/gen_postpt_skew_tables_anim.py --all
$P image/tools/gen_buf_type_anim.py
$P image/tools/gen_clkperiod_image.py        # 含 HV2M23 本机数据源，仅本机可跑
```

换版纪律（图版标准 5 条）：产物覆盖 `image/`、`image/anim/` 主名前，被替换套图先快照进 `image/archive/<采纳日期>/`（文件名带版本标签，如 `_1104v0`）；PNG/位图只进日期夹；QA 截图进 `image/archive/qa/<日期>/`；任何图永不删除。

## 不归拢的脚本（备案）

- `image/anim/make_static_30_postpt_physkew_1p.py`、`image/anim/make_static_30_postpt_trans_1p.py`：动画版 → 静态版的一次性提取器，**生成器与输出同目录**（practice 站 anim 惯例，位置即约定），留 `image/anim/`；相对路径自洽（只读 `./<NAME>.svg`，写 `../<NAME>.svg`）。
- `script/_check_glossary.js`：glossary 内容校验器，非图生成器，留 `script/`。
- `script/` 下 `.venv/`、`extracted_1..4/`、`script_*_ppchen.tar.gz`、`__pycache__/`、`.notes_scripts.md`：服务器脚本原始包/运行环境/笔记，本就被仓库根 `.gitignore` 排除（含内部路径/项目名），不动。

## 入库边界（2026-11-17 修正）

- 仓库根 `.gitignore` 排除的是 `synthesis-integration-flow-guide/script/`（"服务器脚本原始包与解压内容（含内部路径/项目名），不入库"）、`后端/`、`*.docx`、`*.pptx`、`pptimage/`。
- **`image/tools/*.py` 实际上是入库的**（`git ls-files image/tools` 可查）。此前本 README 写的是"站点级 `.gitignore` 排除 `image/tools/*.py`"——**该站点级 .gitignore 从未存在，属过期说明，已删除**。
- 因此脚本入库的前提是**脚本本身不携带内部路径**：`_gen_be_review_images.py` 的数据源根目录改为环境变量 `HV_ROOT` 注入（默认按站点相对位置推断，找不到就报错退出），`gen_clkperiod_image.py` 复用同一变量；库内不再出现内部工程绝对路径。
- 换版快照与 Kit 契约分列两处事实源：`image/archive/README.md`（归档规则/覆盖更正）与 `image/anim/MOTION_KIT.md`（动效契约）。本 README 只负责"哪个脚本生成哪张图"。

## 数据源被 `.gitignore` 吞掉的部分（M4，2026-11-17 记录，不搬文件）

以下数据源在 `.gitignore` 排除的 `script/`（约 394MB）里，仓库内**没有**副本；对应的图/表只能复现"结论数值"，不能在本仓库内一键重跑：

| 图/表 | 数据源（仓库外） | 现状 | 处理 |
|---|---|---|---|
| `image/power_compare_vertical.png` | `HV2M23/back_ppt/gen_power_compare_vertical.py` + 0720~0814 报表 Excel 汇总 | 脚本与 Excel 均不在库内 | 数值已在页面 §2.3/§2.4 写明，出处标注到脚本名；不搬 394MB |
| `image/power_compare_descramble_1106.png` | 1106 PTPX 后仿 VCD（`t_8b2lane_descramble*`），原始报告未归档 | 报告缺失 | 已建站内轻量数据源 `image/tools/data/descramble_power.json`（数值 + provenance + `source_status: missing`） |
| 脚本字典页的时钟表 | `script/extracted_4/…/sdc_pr/HV2M23_digital_top.tcl` | 从服务器包里抽取的 tcl | 页面只保留结论，源文件不入库（含内部路径） |
| `image/26_clk_period.png` | `SYNTHESIS/common/tcl_dir/common/clk_period.tcl` | 仓库外 | 通过 `HV_ROOT` 注入路径运行 |
| BE Review 全套 PNG | `server-reports/`（入库）+ `HV2M23/SYNTHESIS/`（仓库外） | 部分入库 | 已入库部分可复现；仓库外部分仅本机可跑 |
| **0826 PowerPro 六组**（`powerpro.html` §3.1/§4.1、`image/42_powerpro_6mode_0826.png`、`43_powerpro_compare_0826.png`） | `HV2M23/back_ppt/` 的 0826 tar（`PACK_TAR_0826V0` 解压后 `rep_dir_*_1800/_0900` 的 `hier_pwr_detail.csv` total 块） | **仓库外缺失**（`source_status: external-missing`） | 数值 11.387 / 11.838 / 11.836、6.399 / 6.619 / 7.427、10.54、12.66、LVT 12.503 / 6.229 / 8.91 已登记进站内 `image/tools/data/powerpro_0826.json`（含出处与缺失状态）；页面 bullet 由 `gen_param_blocks.py` 从该 JSON 渲染，不再手写；找回 tar 后把 `source_status` 改 `ok` |

> 结论：这 6 类是"数据源在库外"，不是"图缺归档"。图本身全部在 `image/` 且有历史快照（见 `image/archive/README.md` 覆盖率表）。

<!-- ymzhu 2026-11-17 20:50 -->
