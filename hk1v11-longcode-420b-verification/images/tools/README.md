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
| `validate_kit_v2.py` | MOTION_KIT v2 规范校验（历史） |
| `validate_kit_v4.py` | MOTION_KIT v4 规范校验（当前） |

## 引用替换清单（2026-11-05 图版更新 · 依据 HK1V11_longcode_420b_delta_audit_20261105.md §6）

> HTML 引用一律指向 `images/anim/<name>.svg`；本次更新**沿用全部原文件名**，
> 除 JPG 外**页面引用零改动**。旧版按「归档日期=内容日」入 `images/archive/`。

| 页面 | 旧图 | 新图 / 去留 | 归档路径 |
|------|------|------------|---------|
| index / architecture | `longcode_verification_architecture.svg`（0720v1 组件框） | **重绘**：192 case 维度矩阵 + chpi_training_packet_sequence + BCC（monitor/scoreboard）+ BOE 回放 + MULTI_CHIP/multi4 + EOL/unlock 故障注入与 send_recovery_image + C-model golden 闭环（dplc.pl）+ RTL 编码 TX 通路（LONG_ENCODING_ALIGN/ERROR_CTRL/OUTPUT）+ decode_ignore 已修/K3 延 4 拍/44-bit 缓冲 + checker_420b 遗留改造警示 + 版本基线条（0721→1028 → HEAD a7130ba7） | `archive/20260720/{longcode_verification_architecture_0720.svg, anim/…, make_anim_…_0720.py}` |
| architecture / decoder | `pydec_tx_rx_structure.svg` | **微调**：TX dump 盒补日志族（kcode_seq/rawbyte/pkt20/diag_debug/kcode_drv，0807+）；RTL 不看盒注记更新为「decode_ignore 已修（6-bit {0,63}）· tag_value 待最新波形」；离线比对区三盒等距布局（v4.3 手改回填生成器） | （原地更新，未归档） |
| index / comparison | `8b10b_vs_420b_architecture.svg` | **微调**：右列 Test Layer 改 192 case 命名族；DUT 盒补 K3 复位延 4 拍；对照表 +2 行（CTRL_F 加扰差异、DUT 编码 TX 通路）并注 K3 边界复位 0XFFFF（13→15 行） | （原地更新，未归档） |
| frame | `spec_frame_flow.svg`（0717「Config Line 单独成行」） | **重绘**：帧 0 配置行 → 每帧 VBP → Active（统一 K2 结尾·首行 FSYNC=1）→ **VFP 第 0 行 = 下一帧配置行（K4+CTRL_F+Dmy+K3|K2）** → 其余 VFP 行同 VBP；帧内不加行；底部 K3/SCREN 注记 | `archive/20260720/{spec_frame_flow_0720.svg, anim/…, make_anim_…_0720.py}` |
| encoding | `spec_scramble_rolling.svg`（全 payload 加扰画法） | **重绘**：① Active/VBK 加扰域（SCREN 门控）+ 行间 LFSR 顺承；② Config 行 CTRL_F **恒不加扰·不推 SCR_KEY**（灰条静止 vs 绿条滚动的视觉对照）；③ K3 边界盒（TX lfsr=0XFFFF / RX 锁 SCREN + 复位 0XFFFF · K3_FIND_rp_d[3] 延 4 拍） | `archive/20260720/{spec_scramble_rolling_0720.svg, anim/…, make_anim_…_0720.py}` |
| encoding | `spec_dummy_70b.svg` | **微调**：Config 行 Before/After 行尾 K2 → K3|K2；注记补 0825「Dmy 补齐到整行 raw 长度」与 1010「DPLC_GROUP=1 时 subpix_cnt +3→+6（CH_SEL 表）」 | （原地更新，未归档） |
| frame | `spec_lsp_kcode.svg` | **微调**：底部新增 K3 语义注记（SCREN=1 行尾 K3 → 锁存 SCREN + key 复位 0XFFFF · RX 延 4 拍；SCREN=0 → K2）；字节序 EA→ED 已是 0720 修正后画法，维持 | （原地更新，未归档） |
| frame | `spec_blanking_idle.svg` | **微调**（t1 判定「保留」，实施时补正 2 处过时语义）：标题与底注「Config Line 单独成行（VACT 后）」→「第一条 VFP 行承载（0924）」；VBP 首行行样 K2 → K3|K2（IDLE 列随动 +20px） | （原地更新，未归档） |
| encoding | `spec_bit_order.svg` | **保留不动**（位序规则 HEAD 一致） | — |
| encoding | `spec_tag_replacement.svg` | **保留不动**（tag 跳过 0/63 语义 HEAD 一致） | — |
| debug-log | `0717_longcode_pydec_ok.jpg`（0717 pydec 全对证据截图） | **归档**（历史证据，debug-log 章节引用需改指向归档路径；图注建议补「后续 decode_ignore 已修」） | `archive/20260717/0717_longcode_pydec_ok.jpg` |

**writer 需落引用的唯一 HTML 改点**：`debug-log.html` 中
`images/0717_longcode_pydec_ok.jpg` → `images/archive/20260717/0717_longcode_pydec_ok.jpg`
（其余页面图版引用路径与文件名均未变）。

**校验记录（2026-11-05）**：`validate_kit_v4.py` 对上表 8 张改动图全 PASS
（动效不变量：text 多重集 / svg 开标签 / 稳态 ≥2 族 / 列车 ≥2.4s / kit 签名 /
reduced-motion）；仓库根 `check_anim_pairs.py` 63/63 配对完整（含归档 anim 副本）；
静态 + 动画全部生成器复跑字节一致（幂等）。

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
3/3/4 ≤4，列车 2.6s ≥2.4s，一次性 delay ≤2.1s）；`check_anim_pairs.py`
65/65 配对完整；三生成器复跑字节一致（幂等）；布局 QA（CJK/ASCII 宽度包络
估算 × 区域包含）零越界。引用落点建议见 t5 任务 output（index 版本区 /
frame · encoding · cases · architecture · debug-log 变更史）。

<!-- ymzhu 2026-11-05 11:38 -->
