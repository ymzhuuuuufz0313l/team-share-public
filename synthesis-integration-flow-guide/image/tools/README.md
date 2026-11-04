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

## 入库边界（重要）

- 仓库根 `.gitignore` 本就排除 `synthesis-integration-flow-guide/script/`（"服务器脚本原始包与解压内容（含内部路径/项目名），不入库"）。
- 本站新增站点级 `.gitignore`：`image/tools/*.py` 不入库——`_gen_be_review_images.py` 与 `gen_clkperiod_image.py` 含 HV2M23 内部工程路径（`E:/project/HV2M23/...`），公开共享仓库不得暴露；其余脚本为相对路径或本站绝对路径，敏感性低，但为与既有排除口径一致统一本地化。
- 本 README（`image/tools/README.md`）入库，作为每组图来源的唯一事实源；若日后要公布脚本，先清除 HV2M23 内部路径再移除 `.gitignore` 对应行。

<!-- ymzhu 2026-11-04 15:54 -->
