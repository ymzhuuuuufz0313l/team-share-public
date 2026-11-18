# images/tools/ — 图版生成脚本归拢（2026-11-04 起执行的图版标准）

> 本目录是本站（hk1v11-synthesis-postpt-practice）**图生成脚本的唯一归拢位置**（图版归档标准：主名 = 当前采纳版；被替换套图快照进 `images/archive/<采纳日期>/` 带版本标签；PNG 只进日期夹；图永不删除）。
> 脚本内容为**生成当时的历史存档**；内部路径**随输出归位修正、以可复跑为准**（图版标准规则 4：历史图可复跑重造），数据源绝对路径以各脚本头部注释为准（指向 `E:\project\HK1V11\...` 与本站目录）。

## 脚本清单（每个脚本生成哪组图）

| 脚本 | 生成物 | 说明 |
|---|---|---|
| `gen_signoff_tables_hk1v11.py` | `images/5{1..5}_signoff_*.svg`（静态）+ `images/anim/` 同名（动画） | **1104V0 run 站点版生成器**（rev5 模板）：直读 HK1V11 `SYNTHESIS/top/sta/post/pt/summary/latest` csv，产出 51 setup / 52 hold / 53 trans / 54 physkew / 55 sdskew 五张表图双版；六项校验（XML/无 script/keyframes/转录逐值/行数/幂等）随生成自动跑 |
| `gen_shift_window_hk11.py` | `images/56_signoff_shift_window_hk11.svg`（静态） | **56 时钟偏移容限图站点版生成器**（v3）：phy csv `rx0_00_max/min` 两行直算左/右移容限（左 = max+0.7、右 = min+0.45），无硬编码；动画版生成器 = `anim/make_anim_shift_window_hk11.py`（MOTION_KIT 契约位置） |
| `gen_signoff_1104v2.py` | 1104V2 全套：6 图双版 SVG + `stats_1104v2.json` + 独立 `index.html` | **canonical 记录版（1104V2）唯一生成入口**，源目录 `E:\project\HK1V11\docs\to_signoff_1104v2\`；模板谱系 = 上两者（rev5 + v2），数据源换 PACK_TAR_1104V2 summary（只读）；幂等。本站 `images/` 主名 12 张即其产物（2026-11-04 换正升主名） |
| `render_png_1104v2.py` | `5{1..6}_signoff_*_hk11.png`（DPR2 快照） | 逐张 msedge 无头渲染（2×viewBox 宽度，PPT 缩放不糊）；PNG 只入 `images/archive/20261104/`，不占主名 |
| `verify_png_1104v2.py` | （校验，无图产物） | PNG 程序化验收：尺寸/标题条色/底缘无截断/红格全矩阵 vs csv 逐格比对（51/52/55 全量、54 无红底+浅蓝最紧格、56 三要素） |
| `gen_signoff_1118v1.py` | `images/5{1..6}_signoff_*.svg`（静态）+ `images/anim/` 同名（动画） | **1118V1 站点换版生成器（现役主名 12 张的来源，2026-11-18）**：逐字节抄 gen_signoff_1104v2.py，数据源 = 本地库 `SYNTHESIS/top/sta/post/pt/summary/latest`（PT 代 20261118_0）；写主名前自动把旧 1104V2 主名快照进 `archive/20261104/`（`_1104v2`/`_1104v2_anim` 标签）；hold 副标题带"全 0 违例·全局最小 +0.001875 @lt_cbest_m40（余量薄）"csv 直算提示；`--out DIR` 干跑、`--standalone` 兼收独立版产物 |
| `render_png_1118v1.py` | `5{1..6}_signoff_*_hk11.png`（DPR2 快照 → 临时目录） | 沿用 1104V2 渲染口径（Edge 无头 DPR2，一次一张），源 = 站点主名静态版；PNG 验毕入 `images/archive/20261118/`（`_1118v1` 标签），不占主名 |
| `verify_png_1118v1.py` | （校验，无图产物） | 1118V1 PNG 程序化验收：1104V2 版的全矩阵比对口径，行数改由 csv 行数直取；"无红底"改 ≥40px 连续实填判据（抗 ClearType 暖边误报，负控 51 实红图必报 True） |
| `archive_snapshot.py` | （无图产物；归档动作） | **图版归档自动化**（2026-11-17 审计 A9-1/A9-5）：`snapshot(src, date_tag, version_tag, note)` 把生成器产物快照进 `images/archive/<日期>/`，自动登记 `images/archive/README.md`，并对 archive 全树做 **md5 去重**（同 md5 已存在即跳过拷贝、同名不同 md5 拒绝覆盖）。调用方：`anim/make_anim_skew_probe_audit_1028.py`（动画版）、`E:/project/HK1V11/docs/skew_probe_audit_1028/gen_audit_diagram.py`（静态版 + 发布到本站） |

## 复跑（1104V2 记录版在 `E:\project\HK1V11\docs\to_signoff_1104v2\`，勿在本目录直跑）

```bash
cd E:\project\HK1V11\docs\to_signoff_1104v2
python gen_signoff_1104v2.py    # 51-56 SVG（静态+动画）+ stats + index.html
python render_png_1104v2.py     # PNG 快照（DPR2）
python verify_png_1104v2.py     # 程序化验收
```

## 复跑（1118V1 现役版，在本目录直跑）

```bash
cd <本站>\images\tools
python gen_signoff_1118v1.py     # 51-56 SVG 换版（自动先快照旧主名 → archive/20261104/，再覆盖主名）
python render_png_1118v1.py      # PNG 快照（DPR2 → %TEMP%\signoff_1118v1_png）
python verify_png_1118v1.py      # 程序化验收（全矩阵 vs csv）
# 验毕归档 PNG：archive_snapshot.snapshot(<png>, "20261118", version_tag="1118v1", note=...)
```

产物回站：静态/动画 SVG 覆盖 `images/`、`images/anim/` 主名（引用路径不变，`?v=` 递增）；PNG 移入当日 `images/archive/<日期>/`；被替换的主名内容先快照进同一日期夹（带版本标签）。

**归档已自动化（2026-11-17）**：生成器收尾调用 `images/tools/archive_snapshot.py` 完成快照 + 登记 + md5 去重，不再依赖人手 `cp`（此前正是人手 cp 导致 `skew_probe_audit_1028` 静态/动画版从未归档）。重复件的对账见 `images/archive/README.md`「同 md5 快照对账」。

## 不归拢的生成器（备案）

- `anim/make_anim_*.py`（功耗 3 张 + skew_probe + 56 动画版）与 `images/anim/make_anim_*.py`（表格 3 张动画版）：按 `anim/MOTION_KIT.md` v4 契约**生成器与输出同目录**，位置即约定，不移入本目录。
- 仓库根 `scripts/` 下其它站的生成器（search index / chip_sel 等）与 `synthesis-integration-flow-guide/script/`：非本站 signoff 图版体系，不在本目录范围。

<!-- ymzhu 2026-11-18 15:33 -->
