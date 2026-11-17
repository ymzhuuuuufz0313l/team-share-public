# images/tools/ — 图生成与校验脚本

本目录存放站点图的生成脚本与校验工具。每个脚本头部标注其生成的图组。

## 生成脚本（anim/ 动画版 SVG）

| 脚本 | 生成目标 |
|------|---------|
| `make_anim_8b10b_vs_420b.py` | `images/anim/8b10b_vs_420b_architecture.svg` |
| `make_anim_longcode_verification_architecture.py` | `images/anim/longcode_verification_architecture.svg` |
| `make_anim_pydec_tx_rx_structure.py` | `images/anim/pydec_tx_rx_structure.svg` |
| `make_anim_spec_bit_order.py` | `images/anim/spec_bit_order.svg` |
| `make_anim_spec_blanking_idle.py` | `images/anim/spec_blanking_idle.svg` |
| `make_anim_spec_dummy_70b.py` | `images/anim/spec_dummy_70b.svg` |
| `make_anim_spec_frame_flow.py` | `images/anim/spec_frame_flow.svg` |
| `make_anim_spec_lsp_kcode.py` | `images/anim/spec_lsp_kcode.svg` |
| `make_anim_spec_scramble_rolling.py` | `images/anim/spec_scramble_rolling.svg` |
| `make_anim_spec_tag_replacement.py` | `images/anim/spec_tag_replacement.svg` |

> 静态版（事实源）为同站点 `images/` 下同名 SVG（十图统一由仓库根
> `scripts/generate_longcode_report_svgs.py` 生成，1105 起输出目录已对齐
> `images/`）；动画版在 `images/anim/`。
> 生成器确定性幂等：只读静态版，零第三方依赖，重跑输出字节一致。

## 校验脚本

| 脚本 | 用途 |
|------|------|
| `validate_kit_v4.py` | MOTION_KIT v4 规范校验（**当前唯一应使用**） |
| `validate_kit_v2.py` | MOTION_KIT v2 规范校验（**DEPRECATED**，仅溯源保留，文件头有横幅） |
| `check_overlap.py` | 无头 Chrome 几何/墨迹重叠检测（逐图出 full/F00x 截图 + json/md 报告） |
| `site_paths.py` | 路径解析 helper：`site_base()` / `src_base()` / `write_svg()`（统一 LF、`newline=""`、禁 CRLF；**覆盖前自动归档旧版**）/ `load_facts()` / `file_lines()` |
| `extract_facts.py` | 从 case 源统计业务数字 → `data/facts.json`（唯一事实源） |
| `check_facts.py` | **一致性闸门**：facts.json ↔ 生成器产物 ↔ 页面文字，出站数字漂移即报红；§5 专管行数族 `file_lines` |
| `check_archive.py` | **归档闸门**：相对 `--base` 被改动的每张图，必须有 LF 归一化 md5 相等的归档快照，缺一即 FAIL（连手改也能抓） |

### 一条命令跑交付自检

```bash
python images/tools/check_facts.py            # 业务数字一致性（快，先跑这个）
python images/tools/check_archive.py --base <rev>  # 被替换图版是否都留了快照
python images/tools/validate_kit_v4.py <name...>   # 动效规范
python scripts/check_anim_pairs.py            # 静/动配对完整性（数字以输出为准）
python images/tools/check_overlap.py          # 版式重叠（慢，需 Chrome）
```

## 归档目录说明（2026-11-17）

| 目录 | 内容 | 备注 |
|------|------|------|
| `images/archive/20260717/` | `0717_longcode_pydec_ok.jpg`（历史证据截图） | 已归档，页面引用已改向归档路径 |
| `images/archive/20260720/` | 0720 代际 3 组被替换图版（static + anim + 旧生成器） | 已归档；2026-11-17 仅统一换行为 LF，内容未改 |
| `images/archive/20261117/` | 1105 更新漏归档的 7 个版本 + `fx_phases` 重复视口截图去重 | 清单与逐文件 md5 见该目录 `README.md` |
| `images/archive/qa/` | **空目录** | **不是仓库缺陷（F11 已降级）**：`git ls-files` 下无任何文件，是本地未跟踪残留；git 不记录空目录，删留都不影响仓库。此处仅备案，本轮不处理 |

## 引用替换清单（2026-11-05 图版更新 · 依据 HK1V11_longcode_420b_delta_audit_20261105.md §6）

> HTML 引用一律指向 `images/anim/<name>.svg`；本次更新**沿用全部原文件名**，
> 除 JPG 外**页面引用零改动**。旧版按「归档日期=内容日」入 `images/archive/`。

| 页面 | 旧图 | 新图 / 去留 | 归档路径 |
|------|------|------------|---------|
| index / architecture | `longcode_verification_architecture.svg`（0720v1 组件框） | **重绘**：192 case 维度矩阵 + chpi_training_packet_sequence + BCC（monitor/scoreboard）+ BOE 回放 + MULTI_CHIP/multi4 + EOL/unlock 故障注入与 send_recovery_image + C-model golden 闭环（dplc.pl）+ RTL 编码 TX 通路（LONG_ENCODING_ALIGN/ERROR_CTRL/OUTPUT）+ decode_ignore 已修/K3 延 4 拍/44-bit 缓冲 + checker_420b 遗留改造警示 + 版本基线条（0721→1028 → HEAD a7130ba7） | `archive/20260720/{longcode_verification_architecture_0720.svg, anim/…, make_anim_…_0720.py}` |
| architecture / decoder | `pydec_tx_rx_structure.svg` | **微调**：TX dump 盒补日志族（kcode_seq/rawbyte/pkt20/diag_debug/kcode_drv，0807+）；RTL 不看盒注记更新为「decode_ignore 已修（6-bit {0,63}）· tag_value 待最新波形」；离线比对区三盒等距布局（v4.3 手改回填生成器） | `archive/20261117/{pydec_tx_rx_structure_pre1105.svg, anim/…}` |
| index / comparison | `8b10b_vs_420b_architecture.svg` | **微调**：右列 Test Layer 改 192 case 命名族；DUT 盒补 K3 复位延 4 拍；对照表 +2 行（CTRL_F 加扰差异、DUT 编码 TX 通路）并注 K3 边界复位 0XFFFF（13→15 行） | `archive/20261117/{8b10b_vs_420b_architecture_pre1105.svg, anim/…}` |
| frame | `spec_frame_flow.svg`（0717「Config Line 单独成行」） | **重绘**：帧 0 配置行 → 每帧 VBP → Active（统一 K2 结尾·首行 FSYNC=1）→ **VFP 第 0 行 = 下一帧配置行（K4+CTRL_F+Dmy+K3|K2）** → 其余 VFP 行同 VBP；帧内不加行；底部 K3/SCREN 注记 | `archive/20260720/{spec_frame_flow_0720.svg, anim/…, make_anim_…_0720.py}` |
| encoding | `spec_scramble_rolling.svg`（全 payload 加扰画法） | **重绘**：① Active/VBK 加扰域（SCREN 门控）+ 行间 LFSR 顺承；② Config 行 CTRL_F **恒不加扰·不推 SCR_KEY**（灰条静止 vs 绿条滚动的视觉对照）；③ K3 边界盒（TX lfsr=0XFFFF / RX 锁 SCREN + 复位 0XFFFF · K3_FIND_rp_d[3] 延 4 拍） | `archive/20260720/{spec_scramble_rolling_0720.svg, anim/…, make_anim_…_0720.py}` |
| encoding | `spec_dummy_70b.svg` | **微调**：Config 行 Before/After 行尾 K2 → K3|K2；注记补 0825「Dmy 补齐到整行 raw 长度」与 1010「DPLC_GROUP=1 时 subpix_cnt +3→+6（CH_SEL 表）」 | `archive/20261117/{spec_dummy_70b_pre1105.svg, anim/…}` |
| frame | `spec_lsp_kcode.svg` | **微调**：底部新增 K3 语义注记（SCREN=1 行尾 K3 → 锁存 SCREN + key 复位 0XFFFF · RX 延 4 拍；SCREN=0 → K2）；字节序 EA→ED 已是 0720 修正后画法，维持 | `archive/20261117/{spec_lsp_kcode_pre1105.svg, anim/…}` |
| frame | `spec_blanking_idle.svg` | **微调**（t1 判定「保留」，实施时补正 2 处过时语义）：标题与底注「Config Line 单独成行（VACT 后）」→「第一条 VFP 行承载（0924）」；VBP 首行行样 K2 → K3|K2（IDLE 列随动 +20px） | `archive/20261117/{spec_blanking_idle_pre1105.svg, anim/…}` |
| encoding | `spec_bit_order.svg` | **保留不动**（位序规则 HEAD 一致） | — |
| encoding | `spec_tag_replacement.svg` | **保留不动**（tag 跳过 0/63 语义 HEAD 一致） | — |
| debug-log | `0717_longcode_pydec_ok.jpg`（0717 pydec 全对证据截图） | **归档**（历史证据，debug-log 章节引用需改指向归档路径；图注建议补「后续 decode_ignore 已修」） | `archive/20260717/0717_longcode_pydec_ok.jpg` |

**归档规范（2026-11-17 起强制）**：图版更新**不允许**再写「（原地更新，未归档）」。
任何被替换的版本必须在同一提交内用 `git show <上一版 rev>:<path>` 取出，落到
`images/archive/<更新日期YYYYMMDD>/`，并在本表登记归档路径与 md5。
`20261117/` 这批即补掉 1105 更新漏归档的 7 个版本（上表 5 张微调图 static+anim，
外加 `kcode_bitrev_compare.svg` 被 `053c875` 与 `b063c7f` 连续两次修改所未留的 2 版）；
完整清单与逐文件 md5 见 `images/archive/20261117/README.md`。

**writer 需落引用的唯一 HTML 改点**：`debug-log.html` 中
`images/0717_longcode_pydec_ok.jpg` → `images/archive/20260717/0717_longcode_pydec_ok.jpg`
（其余页面图版引用路径与文件名均未变）。

**校验记录（2026-11-05）**：`validate_kit_v4.py` 对上表 8 张改动图全 PASS
（动效不变量：text 多重集 / svg 开标签 / 稳态 ≥2 族 / 列车 ≥2.4s / kit 签名 /
reduced-motion）；静态 + 动画全部生成器复跑字节一致（幂等）。

> **自检入口勘误（2026-11-17，F12）**：配对自检脚本在**仓库根 `scripts/`** 下
> （不是仓库根目录直下），且计数随图版增加而变，**不要写死数字**。
> 正确用法：`python scripts/check_anim_pairs.py`；
> 2026-11-17 实测输出 `anim svg total: 75` /
> `RESULT: OK — all 75 anim svgs have static counterparts`。
> 原文 `63/63`（本节）与 `65/65`（下文 1105 对比组）均为过期计数。

## 基线 vs 现状前后对比组图（delta_* · 2026-11-05 新增，comparator）

> 与上表「沿用原文件名」的既有图更新不同：本组为**全新对比图**（基线 07-13
> 66ecf97d vs 现状 a7130ba7 左右对照 + 变化高亮），生成器**同时产静/动两版**
> （scene 单源渲染，text 多重集与 `<svg>` 开标签两版逐字节一致，写盘前强制断言）。
> 事实源：`HK1V11_longcode_420b_delta_audit_20261105.md` + DV_TCON_C/top/tests
> 直读实测（192 目录 / 维度计数 / cfg 字段并集 2026-11-05 复核）。

| 脚本 | 生成目标（静态 + 动画双版） | 内容与稳态动效 |
|------|---------------------------|----------------|
| `make_anim_delta_frame_structure.py` | `images/delta_frame_structure.svg` + `images/anim/…` | 帧结构演进：①Config Line VACT 后单独成行→首条 VFP 行承载（帧内不加行）②行尾 K2→K3（SCREN=1 锁存+key 复位 0XFFFF）｜K2 ③CTRL_F 随域加扰→恒不加扰·不推 SCR_KEY；cellwave/pulse 族+主箭头列车（3 族） |
| `make_anim_delta_case_matrix.py` | `images/delta_case_matrix.svg` + `images/anim/…` | case 规模与维度：1（cfg 4 字段）→192（0924 +189 · 1022 +2）；分辨率 ×6 条形（47/52/6/18/10/59）+FPS ×8+PORT ×4+维度族 chips；cfg 字段 4→18（实测并集，t1 摘要口径 17 不计 BYTE0_BIT3_0 特例）；cellwave/pulse 族+列车（3 族） |
| `make_anim_delta_env_components.py` | `images/delta_env_components.svg` + `images/anim/…` | 激励源组件三色标注：灰=未变（含 checker_420b 77 行零变更）/琥珀=已变（sequence 1456→1865、driver+222、ref model 0807 三修…）/青=新增（训练包/BCC/BOE/MULTI_CHIP/故障恢复/auto_script+dplc.pl）；中列 8 波次时间线 + 底部 RTL 联动带；step 接力/cellwave/pulse-t/列车（4 族） |

**校验记录（2026-11-05 11:38）**：`validate_kit_v4.py` 三图全 PASS（稳态族
3/3/4 ≤4，列车 2.6s ≥2.4s，一次性 delay ≤2.1s）；三生成器复跑字节一致（幂等）；
布局 QA（CJK/ASCII 宽度包络估算 × 区域包含）零越界。配对自检见上文勘误
（`python scripts/check_anim_pairs.py`，数字以脚本输出为准，2026-11-17 实测 75/75）。引用落点建议见 t5 任务 output（index 版本区 /
frame · encoding · cases · architecture · debug-log 变更史）。
<!-- ymzhu 2026-11-17 20:35 -->
