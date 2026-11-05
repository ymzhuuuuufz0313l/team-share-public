# SVG 图版重叠扫描报告 20261105

- 工具：`images/tools/check_overlap.py`（真浏览器渲染度量，Chrome headless getExtentOfChar/getPointAtLength + CTM 归一）
- 运行：`python images/tools/check_overlap.py --anim`
- 浏览器：`C:\Program Files\Google\Chrome\Application\chrome.exe`
- 分级标准：**BLOCKER**＝文字语义被遮挡/不可读（两段文字墨迹深度互叠≥22% 且面积≥10%，或文字越出 viewBox >4px）；**HIGH**＝连线明显穿字（无标签底遮挡、侵入≥2.5px 或跨≥8px）、文字压组件边界/伸出组件盒（侵入≥6px 或骑跨≥2px 且盒内占比≥10%）、墨迹确有相交的文字对；**LOW**＝轻微擦边（em 盒交叠但墨迹未触、贴边框带<1.5px、被标签底有意遮断的连线），视觉可接受。
- 动画版说明：CSS 动画被冻结到布局终帧后度量；流光/呼吸类纯视觉动画不影响几何。
- 像素复核：对全部 BLOCKER/HIGH 发现做双掩膜渲染（只渲 A / 只渲 B，2x 缩放），PIL 统计墨迹像素交集（文字↔文字、文字↔连线）或边界带墨迹命中（文字↔组件）；几何判级与像素证据矛盾时自动降级为 LOW 并在明细中留痕。

## 汇总

| 文件 | 文字数 | BLOCKER | HIGH | LOW | 越界文字 | 空文本 |
|---|---|---|---|---|---|---|
| 8b10b_vs_420b_architecture.svg | 92 | 0 | 0 | 0 | 0 | 0 |
| delta_case_matrix.svg | 98 | 0 | 0 | 0 | 0 | 0 |
| delta_env_components.svg | 96 | 0 | 1 | 25 | 0 | 0 |
| delta_frame_structure.svg | 104 | 0 | 1 | 0 | 0 | 0 |
| longcode_verification_architecture.svg | 122 | 2 | 12 | 6 | 0 | 0 |
| pydec_tx_rx_structure.svg | 50 | 0 | 1 | 1 | 0 | 0 |
| spec_bit_order.svg | 64 | 0 | 1 | 0 | 0 | 0 |
| spec_blanking_idle.svg | 75 | 0 | 0 | 0 | 0 | 0 |
| spec_dummy_70b.svg | 48 | 0 | 0 | 0 | 0 | 0 |
| spec_frame_flow.svg | 58 | 0 | 0 | 0 | 0 | 0 |
| spec_lsp_kcode.svg | 50 | 0 | 0 | 0 | 0 | 0 |
| spec_scramble_rolling.svg | 45 | 0 | 4 | 0 | 0 | 0 |
| spec_tag_replacement.svg | 41 | 0 | 0 | 0 | 0 | 0 |
| anim/8b10b_vs_420b_architecture.svg | 92 | 0 | 0 | 0 | 0 | 0 |
| anim/delta_case_matrix.svg | 98 | 0 | 0 | 0 | 0 | 0 |
| anim/delta_env_components.svg | 96 | 0 | 1 | 25 | 0 | 0 |
| anim/delta_frame_structure.svg | 104 | 0 | 1 | 0 | 0 | 0 |
| anim/longcode_verification_architecture.svg | 122 | 2 | 11 | 7 | 0 | 0 |
| anim/pydec_tx_rx_structure.svg | 50 | 0 | 1 | 1 | 0 | 0 |
| anim/spec_bit_order.svg | 64 | 0 | 1 | 0 | 0 | 0 |
| anim/spec_blanking_idle.svg | 75 | 0 | 0 | 0 | 0 | 0 |
| anim/spec_dummy_70b.svg | 48 | 0 | 0 | 0 | 0 | 0 |
| anim/spec_frame_flow.svg | 58 | 0 | 0 | 0 | 0 | 0 |
| anim/spec_lsp_kcode.svg | 50 | 0 | 0 | 0 | 0 | 0 |
| anim/spec_scramble_rolling.svg | 45 | 0 | 4 | 0 | 0 | 0 |
| anim/spec_tag_replacement.svg | 41 | 0 | 0 | 0 | 0 | 0 |
| **合计** |  | **4** | **39** | **65** |  |  |

## 8b10b_vs_420b_architecture.svg

未检出重叠。✔

## delta_case_matrix.svg

未检出重叠。✔

## delta_env_components.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔连线 | 「波次 = 差异审计 §1 表」(463.3,656) 83.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,656.8→505,664.9 跨 8.1px，最大侵入 4.7px｜像素复核：ink-collision（墨迹交集 12px @2x） | `overlap_evidence_20261105/delta_env_components.svg.F001.png` |
| F002 | LOW | 文字↔连线 | 「0721v1 · 1b574b63」(463.3,160) 83.5×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,161→505,169.9 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F003 | LOW | 文字↔连线 | 「CONFIG_DATA 16→24bit」(456.3,176) 97.5×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,177.1→505,185.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F004 | LOW | 文字↔连线 | 「420b 编码链不受影响」(464.6,188) 80.8×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,188.8→505,196.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F005 | LOW | 文字↔连线 | 「0807v1 · 179486aa」(463.8,222) 82.4×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,222.8→505,231.8 跨 9px，最大侵入 5.3px，连线被不透明标签底遮断 | — |
| F006 | LOW | 文字↔连线 | 「全量替换 · ref model 三修入库」(448.3,238) 113.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,239→505,247 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F007 | LOW | 文字↔连线 | 「debug 日志族 · auto_script 起步」(445,250) 120×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,250.6→505,259.6 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F008 | LOW | 文字↔连线 | 「0825 · f54f8d67」(470.9,284) 68.1×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,284.7→505,294.6 跨 9.9px，最大侵入 5.2px，连线被不透明标签底遮断 | — |
| F009 | LOW | 文字↔连线 | 「相位感知 CTRL_L（VBP/VACT/VFP）」(432.3,300) 145.3×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,300.8→505,308.9 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F010 | LOW | 文字↔连线 | 「UTC 槽位 0-3 → 10-13」(461.8,312) 86.5×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,312.5→505,321.5 跨 9px，最大侵入 5px，连线被不透明标签底遮断 | — |
| F011 | LOW | 文字↔连线 | 「0924 · 44e48592」(469.1,346) 71.8×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,346.6→505,356.4 跨 9.9px，最大侵入 5.1px，连线被不透明标签底遮断 | — |
| F012 | LOW | 文字↔连线 | 「CTRL_F 不加扰 · VFP[0] 承载 · 训练包」(432,362) 145.9×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,362.7→505,370.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F013 | LOW | 文字↔连线 | 「EOL / 恢复 · case 1→190」(457,374) 96.1×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,374.4→505,383.3 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F014 | LOW | 文字↔连线 | 「1010 · 6f94d19f」(470.9,408) 68.1×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,408.4→505,418.3 跨 9.9px，最大侵入 5.2px，连线被不透明标签底遮断 | — |
| F015 | LOW | 文字↔连线 | 「MULTI_CHIP fork · CH_SEL subpix 表」(432.8,424) 144.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,424.6→505,433.6 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F016 | LOW | 文字↔连线 | 「drive_idle_ct」(481.1,436) 47.7×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,437.1→505,445.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F017 | LOW | 文字↔连线 | 「1013 / 1014」(479.9,470) 50.2×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,471.2→505,480.2 跨 9px，最大侵入 5.3px，连线被不透明标签底遮断 | — |
| F018 | LOW | 文字↔连线 | 「checker POST_SIM 桩」(462,486) 86×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,486.5→505,495.4 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F019 | LOW | 文字↔连线 | 「与 420b 激励无直接关系」(459.2,498) 91.6×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,499→505,507.1 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F020 | LOW | 文字↔连线 | 「1022 · 5bf35dcf」(470.7,532) 68.7×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,533.1→505,542 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F021 | LOW | 文字↔连线 | 「BCC 体系 · BOE 回放 · dplc.pl」(447.8,548) 114.3×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,549.2→505,557.3 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F022 | LOW | 文字↔连线 | 「case → 192」(482.3,560) 45.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,560.9→505,568.9 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F023 | LOW | 文字↔连线 | 「1028 · 08befa71」(469.9,594) 70.3×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,595→505,603.9 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F024 | LOW | 文字↔连线 | 「overlay：HDL 21 + DV 51 改 / 24 新」(437,610) 136×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,611.1→505,619.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F025 | LOW | 文字↔连线 | 「isptx_agent 内无 .sv 变更」(457.3,622) 95.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,622.7→505,630.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F026 | LOW | 文字↔组件 | 「基线 = HEAD 逐字节相同（零变更）」(668,428) 145.8×10 压 rect(656,404) 488×36 的 bottom 边框，侵入 0.4px | — |

- 字体审计：Helvetica Neue=可用

## delta_frame_structure.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「不变项：Active 行尾统一 K2 · LSB-first 位序 · LSP …」(56,747) 403.2×11 压 rect(40,680) 1120×76 的 bottom 边框，侵入 2px｜像素复核：ink-on-border（边界带墨迹 1173px @2x） | `overlap_evidence_20261105/delta_frame_structure.svg.F001.png` |

- 字体审计：Helvetica Neue=可用

## longcode_verification_architecture.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | BLOCKER | 文字↔文字 | 「dout_24b + 2-bit valid」(911.6,532.5) 112.8×12 ↔ 「灰框内：RTL 解码链 —— 离线验证不依赖」(879.3,539) 177.3×11；墨迹交叠 108.3×2px（面积 222px²，深度占小字高 30%，字符级互叠 32，em 盒交叠 620.3px²）｜像素复核：ink-collision（墨迹交集 212px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F001.png` |
| F002 | BLOCKER | 文字↔文字 | 「版本基线 · DV_TCON_C 主干 + 服务器包波次」(56,1060) 264.7×15 ↔ 「0721v1 CONFIG_DATA 24bit · 0807v1 ref mo…」(56,1065) 634.3×11；墨迹交叠 246.7×6.1px（面积 1505.1px²，深度占小字高 80%，字符级互叠 65，em 盒交叠 2647.2px²）｜像素复核：ink-collision（墨迹交集 1482px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F002.png` |
| F003 | HIGH | 文字↔连线 | 「MULTI_CHIP / multi4（1010）」(162.5,737.5) 153×12 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,738.2→204,748.7 跨 10.5px，最大侵入 5.7px｜像素复核：ink-collision（墨迹交集 26px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F003.png` |
| F004 | HIGH | 文字↔连线 | 「env.sv config_db 相对路径 · lane_delay_rever…」(143,755.5) 191.9×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,756.4→204,764.8 跨 8.4px，最大侵入 4.9px｜像素复核：ink-collision（墨迹交集 30px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F004.png` |
| F005 | HIGH | 文字↔连线 | 「fork 隔离 · CH_SEL→subpix_cnt 966/960/726/…」(129.9,771.5) 218.1×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,772.5→204,780.9 跨 8.4px，最大侵入 4.8px｜像素复核：ink-collision（墨迹交集 21px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F005.png` |
| F006 | HIGH | 文字↔连线 | 「DPLC_GROUP=1 时 subpix_cnt +3→+6」(158.3,787.5) 161.3×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,787.9→204,797 跨 9.1px，最大侵入 4.7px｜像素复核：ink-collision（墨迹交集 6px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F006.png` |
| F007 | HIGH | 文字↔连线 | 「接收端离线验证路径 · 不看 RTL 解码器（0717 建立 · 存续）」(56,852) 347.9×15 被 path(stroke=rgb(5, 150, 105), w=2) 穿过：179,852.7→179,866 跨 13.3px，最大侵入 7.3px｜像素复核：ink-collision（墨迹交集 16px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F007.png` |
| F008 | HIGH | 文字↔连线 | 「接收端离线验证路径 · 不看 RTL 解码器（0717 建立 · 存续）」(56,852) 347.9×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,852.4→204,866.4 跨 14px，最大侵入 7.4px｜像素复核：ink-collision（墨迹交集 53px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F008.png` |
| F009 | HIGH | 文字↔连线 | 「long_rtl_tap_debug.sv」(123,887.5) 112×12 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,888.1→204,898.6 跨 10.5px，最大侵入 5.8px｜像素复核：ink-collision（墨迹交集 22px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F009.png` |
| F010 | HIGH | 文字↔连线 | 「抓 DATA_ALIGN_PRE」(134.1,921.5) 89.7×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,922.4→204,930.8 跨 8.4px，最大侵入 4.9px｜像素复核：ink-collision（墨迹交集 4px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F010.png` |
| F011 | HIGH | 文字↔连线 | 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11 被 line(stroke=rgb(124, 58, 237), w=1.5) 穿过：360.8,984→565.9,984 跨 205.1px，最大侵入 5px｜像素复核：ink-collision（墨迹交集 466px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F011.png` |
| F012 | HIGH | 文字↔组件 | 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11 压 rect(566,960) 380×48 的 left 边框，侵入 206px｜像素复核：ink-on-border（边界带墨迹 58px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F012.png` |
| F013 | HIGH | 文字↔组件 | 「20-bit 包流 / 40-bit K 码 · 串行链路」(739,383.9) 11×152.3 压 rect(40,204) 700×352 的 right 边框，侵入 10px｜像素复核：ink-on-border（边界带墨迹 414px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F013.png` |
| F014 | HIGH | 文字↔组件 | 「tap DATA_ALIGN_PRE（每拍 20-bit 对齐数据）」(592.9,819) 214.1×11 压 rect(40,694) 1120×132 的 bottom 边框，侵入 4px｜像素复核：ink-on-border（边界带墨迹 1310px @2x） | `overlap_evidence_20261105/longcode_verification_architecture.svg.F014.png` |
| F015 | LOW | 文字↔文字 | 「long_pydec_report_lane0.md」(683.1,970) 145.9×12 ↔ 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11；墨迹交叠 140.1×0px（面积 0px²，深度占小字高 0%，字符级互叠 0，em 盒交叠 437.7px²） | — |
| F016 | LOW | 文字↔文字 | 「逐区域比对 verdict：LSP / CTRL_F / LINE 全对 ✅」(648.2,989) 215.6×11 ↔ 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11；墨迹交叠 179×0px（面积 0px²，深度占小字高 0%，字符级互叠 0，em 盒交叠 192.9px²） | — |
| F017 | LOW | 文字↔连线 | 「体系扩展（0924 ~ 1022）」(56,704) 150.7×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,704.6→204,718.6 跨 14px，最大侵入 2.7px｜像素复核：no-ink-collision（墨迹交集 0px @2x） | — |
| F018 | LOW | 文字↔连线 | 「bind 注入 KCODE_ALIGN · 零 RTL 修改」(98.7,905.5) 160.5×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,906.3→204,914.7 跨 8.4px，最大侵入 5px｜像素复核：no-ink-collision（墨迹交集 0px @2x） | — |
| F019 | LOW | 文字↔组件 | 「Transaction / Driver」(56,582) 121.4×15 压 rect(64,596) 300×64 的 left/top 边框，侵入 14px｜像素复核：no-border-ink（边界带墨迹 0px @2x） | — |
| F020 | LOW | 文字↔组件 | 「isptx_driver.sv（420b）」(498.8,597.5) 118.5×12 压 rect(404,596) 308×64 的 top 边框，侵入 0.9px | — |

- 字体审计：Helvetica Neue=可用

## pydec_tx_rx_structure.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔连线 | 「离线比对（脚本完成 · 不依赖 DUT 解码结果）」(56,490) 266.5×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：214,490.5→214,504.5 跨 14px，最大侵入 7.5px｜像素复核：ink-collision（墨迹交集 56px @2x） | `overlap_evidence_20261105/pydec_tx_rx_structure.svg.F001.png` |
| F002 | LOW | 文字↔组件 | 「TAP」(792.3,138) 17.3×10 压 rect(784,134) 34×16 的 bottom 边框，侵入 0.4px | — |

- 字体审计：Helvetica Neue=可用

## spec_bit_order.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「…」(309,237) 14×16 压 rect(246,240) 64×30 的 right/top 边框，侵入 13px｜像素复核：ink-on-border（边界带墨迹 9px @2x） | `overlap_evidence_20261105/spec_bit_order.svg.F001.png` |

- 字体审计：Helvetica Neue=可用

## spec_blanking_idle.svg

未检出重叠。✔

## spec_dummy_70b.svg

未检出重叠。✔

## spec_frame_flow.svg

未检出重叠。✔

## spec_lsp_kcode.svg

未检出重叠。✔

## spec_scramble_rolling.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「K2」(715.6,120.5) 12.8×11 压 rect(724,106) 40×40 的 left 边框，侵入 8.4px｜像素复核：ink-on-border（边界带墨迹 44px @2x） | `overlap_evidence_20261105/spec_scramble_rolling.svg.F001.png` |
| F002 | HIGH | 文字↔组件 | 「K5」(737.6,120.5) 12.8×11 压 rect(694,106) 56×40 的 right 边框，侵入 2.4px｜像素复核：ink-on-border（边界带墨迹 35px @2x） | `overlap_evidence_20261105/spec_scramble_rolling.svg.F002.png` |
| F003 | HIGH | 文字↔组件 | 「加扰区间（CTR_L ~ Dmy）· SCR_KEY update」(120,141) 198.8×11 压 rect(120,106) 90×40 的 right/bottom 边框，侵入 108.8px｜像素复核：ink-on-border（边界带墨迹 526px @2x） | `overlap_evidence_20261105/spec_scramble_rolling.svg.F003.png` |
| F004 | HIGH | 文字↔组件 | 「加扰区间（CTR_L ~ Dmy）· SCR_KEY update」(120,141) 198.8×11 压 rect(214,106) 416×40 的 left/bottom 边框，侵入 94px｜像素复核：ink-on-border（边界带墨迹 657px @2x） | `overlap_evidence_20261105/spec_scramble_rolling.svg.F004.png` |

- 字体审计：Helvetica Neue=可用

## spec_tag_replacement.svg

未检出重叠。✔

## anim/8b10b_vs_420b_architecture.svg

未检出重叠。✔

## anim/delta_case_matrix.svg

未检出重叠。✔

## anim/delta_env_components.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔连线 | 「波次 = 差异审计 §1 表」(463.3,656) 83.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,656.8→505,664.9 跨 8.1px，最大侵入 4.7px｜像素复核：ink-collision（墨迹交集 9px @2x） | `overlap_evidence_20261105/anim__delta_env_components.svg.F001.png` |
| F002 | LOW | 文字↔连线 | 「0721v1 · 1b574b63」(463.3,160) 83.5×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,161→505,169.9 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F003 | LOW | 文字↔连线 | 「CONFIG_DATA 16→24bit」(456.3,176) 97.5×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,177.1→505,185.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F004 | LOW | 文字↔连线 | 「420b 编码链不受影响」(464.6,188) 80.8×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,188.8→505,196.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F005 | LOW | 文字↔连线 | 「0807v1 · 179486aa」(463.8,222) 82.4×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,222.8→505,231.8 跨 9px，最大侵入 5.3px，连线被不透明标签底遮断 | — |
| F006 | LOW | 文字↔连线 | 「全量替换 · ref model 三修入库」(448.3,238) 113.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,239→505,247 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F007 | LOW | 文字↔连线 | 「debug 日志族 · auto_script 起步」(445,250) 120×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,250.6→505,259.6 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F008 | LOW | 文字↔连线 | 「0825 · f54f8d67」(470.9,284) 68.1×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,284.7→505,294.6 跨 9.9px，最大侵入 5.2px，连线被不透明标签底遮断 | — |
| F009 | LOW | 文字↔连线 | 「相位感知 CTRL_L（VBP/VACT/VFP）」(432.3,300) 145.3×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,300.8→505,308.9 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F010 | LOW | 文字↔连线 | 「UTC 槽位 0-3 → 10-13」(461.8,312) 86.5×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,312.5→505,321.5 跨 9px，最大侵入 5px，连线被不透明标签底遮断 | — |
| F011 | LOW | 文字↔连线 | 「0924 · 44e48592」(469.1,346) 71.8×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,346.6→505,356.4 跨 9.9px，最大侵入 5.1px，连线被不透明标签底遮断 | — |
| F012 | LOW | 文字↔连线 | 「CTRL_F 不加扰 · VFP[0] 承载 · 训练包」(432,362) 145.9×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,362.7→505,370.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F013 | LOW | 文字↔连线 | 「EOL / 恢复 · case 1→190」(457,374) 96.1×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,374.4→505,383.3 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F014 | LOW | 文字↔连线 | 「1010 · 6f94d19f」(470.9,408) 68.1×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,408.4→505,418.3 跨 9.9px，最大侵入 5.2px，连线被不透明标签底遮断 | — |
| F015 | LOW | 文字↔连线 | 「MULTI_CHIP fork · CH_SEL subpix 表」(432.8,424) 144.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,424.6→505,433.6 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F016 | LOW | 文字↔连线 | 「drive_idle_ct」(481.1,436) 47.7×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,437.1→505,445.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F017 | LOW | 文字↔连线 | 「1013 / 1014」(479.9,470) 50.2×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,471.2→505,480.2 跨 9px，最大侵入 5.3px，连线被不透明标签底遮断 | — |
| F018 | LOW | 文字↔连线 | 「checker POST_SIM 桩」(462,486) 86×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,486.5→505,495.4 跨 9px，最大侵入 4.9px，连线被不透明标签底遮断 | — |
| F019 | LOW | 文字↔连线 | 「与 420b 激励无直接关系」(459.2,498) 91.6×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,499→505,507.1 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F020 | LOW | 文字↔连线 | 「1022 · 5bf35dcf」(470.7,532) 68.7×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,533.1→505,542 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F021 | LOW | 文字↔连线 | 「BCC 体系 · BOE 回放 · dplc.pl」(447.8,548) 114.3×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,549.2→505,557.3 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F022 | LOW | 文字↔连线 | 「case → 192」(482.3,560) 45.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,560.9→505,568.9 跨 8.1px，最大侵入 4.6px，连线被不透明标签底遮断 | — |
| F023 | LOW | 文字↔连线 | 「1028 · 08befa71」(469.9,594) 70.3×11 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,595→505,603.9 跨 9px，最大侵入 5.4px，连线被不透明标签底遮断 | — |
| F024 | LOW | 文字↔连线 | 「overlay：HDL 21 + DV 51 改 / 24 新」(437,610) 136×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,611.1→505,619.2 跨 8.1px，最大侵入 4.7px，连线被不透明标签底遮断 | — |
| F025 | LOW | 文字↔连线 | 「isptx_agent 内无 .sv 变更」(457.3,622) 95.4×10 被 line(stroke=rgb(203, 213, 225), w=1.2) 穿过：505,622.7→505,630.8 跨 8.1px，最大侵入 4.8px，连线被不透明标签底遮断 | — |
| F026 | LOW | 文字↔组件 | 「基线 = HEAD 逐字节相同（零变更）」(668,428) 145.8×10 压 rect(656,404) 488×36 的 bottom 边框，侵入 0.4px | — |

- 字体审计：Helvetica Neue=可用

## anim/delta_frame_structure.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「不变项：Active 行尾统一 K2 · LSB-first 位序 · LSP …」(56,747) 403.2×11 压 rect(40,680) 1120×76 的 bottom 边框，侵入 2px｜像素复核：ink-on-border（边界带墨迹 1050px @2x） | `overlap_evidence_20261105/anim__delta_frame_structure.svg.F001.png` |

- 字体审计：Helvetica Neue=可用

## anim/longcode_verification_architecture.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | BLOCKER | 文字↔文字 | 「dout_24b + 2-bit valid」(911.6,532.5) 112.8×12 ↔ 「灰框内：RTL 解码链 —— 离线验证不依赖」(879.3,539) 177.3×11；墨迹交叠 108.3×2px（面积 222px²，深度占小字高 30%，字符级互叠 32，em 盒交叠 620.3px²）｜像素复核：ink-collision（墨迹交集 186px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F001.png` |
| F002 | BLOCKER | 文字↔文字 | 「版本基线 · DV_TCON_C 主干 + 服务器包波次」(56,1060) 264.7×15 ↔ 「0721v1 CONFIG_DATA 24bit · 0807v1 ref mo…」(56,1065) 634.3×11；墨迹交叠 246.7×6.1px（面积 1505.1px²，深度占小字高 80%，字符级互叠 65，em 盒交叠 2647.2px²）｜像素复核：ink-collision（墨迹交集 1240px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F002.png` |
| F003 | HIGH | 文字↔连线 | 「MULTI_CHIP / multi4（1010）」(162.5,737.5) 153×12 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,738.2→204,748.7 跨 10.5px，最大侵入 5.7px｜像素复核：ink-collision（墨迹交集 25px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F003.png` |
| F004 | HIGH | 文字↔连线 | 「env.sv config_db 相对路径 · lane_delay_rever…」(143,755.5) 191.9×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,756.4→204,764.8 跨 8.4px，最大侵入 4.9px｜像素复核：ink-collision（墨迹交集 9px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F004.png` |
| F005 | HIGH | 文字↔连线 | 「fork 隔离 · CH_SEL→subpix_cnt 966/960/726/…」(129.9,771.5) 218.1×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,772.5→204,780.9 跨 8.4px，最大侵入 4.8px｜像素复核：ink-collision（墨迹交集 21px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F005.png` |
| F006 | HIGH | 文字↔连线 | 「DPLC_GROUP=1 时 subpix_cnt +3→+6」(158.3,787.5) 161.3×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,787.9→204,797 跨 9.1px，最大侵入 4.7px｜像素复核：ink-collision（墨迹交集 8px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F006.png` |
| F007 | HIGH | 文字↔连线 | 「接收端离线验证路径 · 不看 RTL 解码器（0717 建立 · 存续）」(56,852) 347.9×15 被 path(stroke=rgb(5, 150, 105), w=2) 穿过：179,852.7→179,866 跨 13.3px，最大侵入 7.3px（含 3 条重合线，动画流光副本已归并）｜像素复核：ink-collision（墨迹交集 16px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F007.png` |
| F008 | HIGH | 文字↔连线 | 「接收端离线验证路径 · 不看 RTL 解码器（0717 建立 · 存续）」(56,852) 347.9×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,852.4→204,866.4 跨 14px，最大侵入 7.4px｜像素复核：ink-collision（墨迹交集 51px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F008.png` |
| F009 | HIGH | 文字↔连线 | 「long_rtl_tap_debug.sv」(123,887.5) 112×12 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,888.1→204,898.6 跨 10.5px，最大侵入 5.8px｜像素复核：ink-collision（墨迹交集 16px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F009.png` |
| F010 | HIGH | 文字↔连线 | 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11 被 line(stroke=rgb(124, 58, 237), w=1.5) 穿过：360.8,984→565.9,984 跨 205.1px，最大侵入 5px｜像素复核：ink-collision（墨迹交集 410px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F010.png` |
| F011 | HIGH | 文字↔组件 | 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11 压 rect(566,960) 380×48 的 left 边框，侵入 206px｜像素复核：ink-on-border（边界带墨迹 56px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F011.png` |
| F012 | HIGH | 文字↔组件 | 「20-bit 包流 / 40-bit K 码 · 串行链路」(739,383.9) 11×152.3 压 rect(40,204) 700×352 的 right 边框，侵入 10px｜像素复核：ink-on-border（边界带墨迹 354px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F012.png` |
| F013 | HIGH | 文字↔组件 | 「tap DATA_ALIGN_PRE（每拍 20-bit 对齐数据）」(592.9,819) 214.1×11 压 rect(40,694) 1120×132 的 bottom 边框，侵入 4px｜像素复核：ink-on-border（边界带墨迹 1255px @2x） | `overlap_evidence_20261105/anim__longcode_verification_architecture.svg.F013.png` |
| F014 | LOW | 文字↔文字 | 「long_pydec_report_lane0.md」(683.1,970) 145.9×12 ↔ 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11；墨迹交叠 140.1×0px（面积 0px²，深度占小字高 0%，字符级互叠 0，em 盒交叠 437.7px²） | — |
| F015 | LOW | 文字↔文字 | 「逐区域比对 verdict：LSP / CTRL_F / LINE 全对 ✅」(648.2,989) 215.6×11 ↔ 「日志族（0807+ · lane*.md）：diag_debug / kcode…」(360,979) 481.2×11；墨迹交叠 179×0px（面积 0px²，深度占小字高 0%，字符级互叠 0，em 盒交叠 192.9px²） | — |
| F016 | LOW | 文字↔连线 | 「体系扩展（0924 ~ 1022）」(56,704) 150.7×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,704.6→204,718.6 跨 14px，最大侵入 2.7px｜像素复核：no-ink-collision（墨迹交集 0px @2x） | — |
| F017 | LOW | 文字↔连线 | 「bind 注入 KCODE_ALIGN · 零 RTL 修改」(98.7,905.5) 160.5×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,906.3→204,914.7 跨 8.4px，最大侵入 5px｜像素复核：no-ink-collision（墨迹交集 0px @2x） | — |
| F018 | LOW | 文字↔连线 | 「抓 DATA_ALIGN_PRE」(134.1,921.5) 89.7×10 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：204,922.4→204,930.8 跨 8.4px，最大侵入 4.9px｜像素复核：no-ink-collision（墨迹交集 0px @2x） | — |
| F019 | LOW | 文字↔组件 | 「Transaction / Driver」(56,582) 121.4×15 压 rect(64,596) 300×64 的 left/top 边框，侵入 14px｜像素复核：no-border-ink（边界带墨迹 0px @2x） | — |
| F020 | LOW | 文字↔组件 | 「isptx_driver.sv（420b）」(498.8,597.5) 118.5×12 压 rect(404,596) 308×64 的 top 边框，侵入 0.9px | — |

- 字体审计：Helvetica Neue=可用

## anim/pydec_tx_rx_structure.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔连线 | 「离线比对（脚本完成 · 不依赖 DUT 解码结果）」(56,490) 266.5×15 被 path(stroke=rgb(124, 58, 237), w=1.5) 穿过：214,490.5→214,504.5 跨 14px，最大侵入 7.5px｜像素复核：ink-collision（墨迹交集 56px @2x） | `overlap_evidence_20261105/anim__pydec_tx_rx_structure.svg.F001.png` |
| F002 | LOW | 文字↔组件 | 「TAP」(792.3,138) 17.3×10 压 rect(784,134) 34×16 的 bottom 边框，侵入 0.4px | — |

- 字体审计：Helvetica Neue=可用

## anim/spec_bit_order.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「…」(309,237) 14×16 压 rect(246,240) 64×30 的 right/top 边框，侵入 13px｜像素复核：ink-on-border（边界带墨迹 9px @2x） | `overlap_evidence_20261105/anim__spec_bit_order.svg.F001.png` |

- 字体审计：Helvetica Neue=可用

## anim/spec_blanking_idle.svg

未检出重叠。✔

## anim/spec_dummy_70b.svg

未检出重叠。✔

## anim/spec_frame_flow.svg

未检出重叠。✔

## anim/spec_lsp_kcode.svg

未检出重叠。✔

## anim/spec_scramble_rolling.svg

| ID | 级别 | 类型 | 描述 | 证据 |
|---|---|---|---|---|
| F001 | HIGH | 文字↔组件 | 「K2」(715.6,120.5) 12.8×11 压 rect(724,106) 40×40 的 left 边框，侵入 8.4px｜像素复核：ink-on-border（边界带墨迹 39px @2x） | `overlap_evidence_20261105/anim__spec_scramble_rolling.svg.F001.png` |
| F002 | HIGH | 文字↔组件 | 「K5」(737.6,120.5) 12.8×11 压 rect(694,106) 56×40 的 right 边框，侵入 2.4px｜像素复核：ink-on-border（边界带墨迹 33px @2x） | `overlap_evidence_20261105/anim__spec_scramble_rolling.svg.F002.png` |
| F003 | HIGH | 文字↔组件 | 「加扰区间（CTR_L ~ Dmy）· SCR_KEY update」(120,141) 198.8×11 压 rect(120,106) 90×40 的 right/bottom 边框，侵入 108.8px｜像素复核：ink-on-border（边界带墨迹 472px @2x） | `overlap_evidence_20261105/anim__spec_scramble_rolling.svg.F003.png` |
| F004 | HIGH | 文字↔组件 | 「加扰区间（CTR_L ~ Dmy）· SCR_KEY update」(120,141) 198.8×11 压 rect(214,106) 416×40 的 left/bottom 边框，侵入 94px｜像素复核：ink-on-border（边界带墨迹 616px @2x） | `overlap_evidence_20261105/anim__spec_scramble_rolling.svg.F004.png` |

- 字体审计：Helvetica Neue=可用

## anim/spec_tag_replacement.svg

未检出重叠。✔

## 证据说明

- 证据目录：`overlap_evidence_20261105/`（本报告同级）。
- 每图一张 `<stem>.full.png`＝Chrome headless 1:1 全页渲染；每个 BLOCKER/HIGH 发现一张 `<stem>.F###.png`＝以发现坐标为中心放大裁剪（含上下文约 ±26px）。
- 复跑命令：`python images/tools/check_overlap.py --anim`（详见工具头部文档）。

## 门禁接入

```bash
# 生成图后强制校验：任何 BLOCKER/HIGH 直接失败
python images/tools/check_overlap.py --anim --gate-severity high
```

<!-- ymzhu 2026-11-05 16:05 -->

## 修复定位提示（供生成器修复阶段直查）

> 静态十图事实源：仓库根 `scripts/generate_longcode_report_svgs.py`；
> 动画版：`images/tools/make_anim_*.py`（delta_* 三组静/动同源生成）。
> 以下为 SVG 内源码行定位（文件:行号），供修生成器时对照。

| 问题簇 | 级别 | SVG 源码定位 | 症状 |
|---|---|---|---|
| longcode F001 | BLOCKER | `longcode_verification_architecture.svg:117`（dout_24b 标签 y=542.5）vs 相邻「灰框内：RTL 解码链…」标题行 | 两条基线仅差 ~6px，墨迹互叠 30% 字高 |
| longcode F002 | BLOCKER | `longcode_verification_architecture.svg:168-169`（y=1072 fs13 与 y=1074 fs10 基线距 2px） | 容器标题与正文几乎同基线，互叠 80% 字高 |
| longcode F003-F010 | HIGH | 时间线脊柱线 x=204（violet path）穿过左侧事件文字（y 737~930 一带）；x=179 绿线穿 F007 | 连线穿字（脊柱应从文字左缘外走或文字避开脊柱列） |
| longcode F011 | HIGH | `longcode_verification_architecture.svg`（line y=984 x360→566 横穿「日志族…」长标签） | 横线直接压在文字上 |
| longcode F012 | HIGH | 「日志族…」x=360 起的长标签侵入右侧 rect(566,960,380,48) 面板 206px | 文字压进相邻组件盒 |
| longcode F013 | HIGH | 竖排标签「20-bit 包流…」(739,384) 贴主面板右缘 rect(40,204,700,352) | 竖字骑面板右边框（边界带墨迹 414px） |
| longcode F014 | HIGH | 「tap DATA_ALIGN_PRE…」y=819 底行压 rect(40,694,1120,132) 底边 | 底注骑面板底框 |
| spec_scramble F001-F004 | HIGH | `spec_scramble_rolling.svg:24,26`（K2 x=722 / K5 x=744 anchor=middle 越入相邻 cell）+ `:36`（「加扰区间…」y=150 基线，cell 行底 y=146） | cell 标签越界互相压 + 注记行与 cell 行重叠 108px |
| pydec F001 | HIGH | `pydec_tx_rx_structure.svg:61`（「离线比对…」y=502 fs13，脊柱 path x=214 穿过） | 脊柱线穿节标题 |
| spec_bit_order F001 | HIGH | `spec_bit_order.svg:61`（"…" x=316 anchor=middle，cell rect 246..310） | 省略号越出 cell 右缘 13px |
| delta_env F001 | HIGH | `delta_env_components.svg:141`（「波次 = 差异审计 §1 表」x=505 y=664，中列时间线刻度线 x=505 穿过） | 刻度线穿注记（其余 24 处同构 LOW 为有标签底设计） |
| delta_frame F001 | HIGH | `delta_frame_structure.svg:243`（「不变项…」y=756 基线＝面板底 y=756） | 底注基线恰压面板底框（边界带墨迹 1173px） |

## 盲区核查结论

- **viewBox 越界 / 裁切**：26 图 0 处（audit.outOfViewbox 全空）。
- **clip-path**：仅 `anim/pydec_tx_rx_structure.svg`、`anim/spec_dummy_70b.svg` 含 clip-path（装饰/渐变用），未见文字被裁迹象（像素墨迹密度正常）。
- **竖排/旋转文本**：rotate(-90) 文本 10 处（longcode/pydec/spec_bit_order/spec_frame_flow），CTM 映射已正确覆盖（F013 即为其一）。
- **乱码/缺字体**：全站统一字体栈 `'Helvetica Neue'→…→'Microsoft YaHei'/SimHei` + 代码标签 Consolas/Menlo/monospace；Windows 渲染回退正常，掩膜墨迹密度无异常（无 tofu 迹象）。
- **空文本**：0 个。
- **动画态抽查**：动画版与静态版孪生判定一致（同几何同结论）；flowdot/flowtail 流光副本与基线几何重合已归并计数（如 anim/longcode F007 dup=3）。

## 工具可靠性自检（合成样本 7 阳性 + 3 阴性对照）

`%TEMP%\overlap_selftest\selftest.svg`：TT 深叠→BLOCKER（像素 1816px 交集）、TT em 擦边→LOW、线穿字→HIGH（32px）、标签底遮线→LOW、压边框→HIGH（91px）、越出底盒→HIGH（14px）、viewBox 越界→HIGH；阴性（盒内正常标签、端点擦线）0 误报。

## 归档说明（2026-11-05 16:05 补记）

- 本报告为**修复前基线**（BLOCKER=4 / HIGH=39 / LOW=65），证据目录 `overlap_evidence_20261105/`
  （26 张全页 PNG 为修复前渲染 + 43 张 B/H 放大裁剪）。
- 修复后复检见 `overlap_report_20261105_after_fix.md`（BLOCKER=0 / HIGH=0 / LOW=58，
  证据 `overlap_evidence_20261105_after_fix/`）。
- 基线一度被 t2 自验时同名覆盖，已从 git HEAD（=修复前 SVG）重跑本工具完整复原
  （数值逐项一致：B4/H39/L65）。

<!-- ymzhu 2026-11-05 16:05 -->
