# -*- coding: utf-8 -*-
"""Render real PT timing report paths as dark terminal-style annotated images.
Highlights: startpoint / endpoint / clock / data-path / slack lines.
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, '..', 'image')
os.makedirs(OUT, exist_ok=True)

FONT_MONO = 'C:/Windows/Fonts/consola.ttf'
FONT_BOLD = 'C:/Windows/Fonts/consolab.ttf'
FONT_CJK  = 'C:/Windows/Fonts/msyh.ttc'

# palette
BG      = (13, 15, 30)
PANEL   = (22, 26, 48)
FG      = (216, 222, 255)
MUTED   = (148, 156, 190)
ACCENT  = (124, 107, 255)
CYAN    = (34, 211, 238)
PINK    = (244, 114, 182)
GREEN   = (110, 231, 183)
YELLOW  = (252, 211, 77)
RED     = (248, 113, 113)
DIMLINE = (38, 44, 78)

def font(sz, bold=False):
    try:
        return ImageFont.truetype(FONT_BOLD if bold else FONT_MONO, sz)
    except Exception:
        return ImageFont.truetype(FONT_MONO, sz)

def cjkfont(sz):
    try:
        return ImageFont.truetype(FONT_CJK, sz)
    except Exception:
        return font(sz)

def render(title, subtitle, lines, outfile, width=1500, highlight=None):
    """lines: list of (text, color, bold). highlight: dict phase_label -> color for drawing."""
    hfont = font(30, True)
    sfont = cjkfont(16)
    cell_h = 28
    pad_x = 40
    pad_top = 110

    # measure
    mfont = font(18)
    maxw = 0
    for t, _, _ in lines:
        maxw = max(maxw, mfont.getlength(t))
    maxw = int(maxw)
    W = max(width, maxw + pad_x * 2)
    H = pad_top + cell_h * len(lines) + 40

    img = Image.new('RGB', (W, H), BG)
    d = ImageDraw.Draw(img)

    # header panel
    d.rectangle([0, 0, W, pad_top], fill=PANEL)
    d.line([0, pad_top, W, pad_top], fill=ACCENT, width=3)
    d.text((pad_x, 22), title, font=hfont, fill=ACCENT)
    d.text((pad_x, 66), subtitle, font=sfont, fill=MUTED)

    y = pad_top + 6
    for text, color, bold in lines:
        f = font(18, bold)
        d.text((pad_x, y + 2), text, font=f, fill=color)
        y += cell_h

    img.save(outfile)
    return W, H


def build_1p_report():
    lines = []
    def add(t, color=FG, bold=False): lines.append((t, color, bold))

    add('Report : timing  (delay_type max · slack_lesser_than 0.5 · pba path)', MUTED)
    add('Design : HV2M23_digital_top   Corner: wc_typical_125   Mode: 1P (single lane)', MUTED)
    add('', MUTED)
    add('Startpoint: LC_CSPIF_L0/KEY_RST_18UI_reg', CYAN, True)
    add('             (rising edge flip-flop clocked by RX0_OD_CLK_DIV2)', MUTED)
    add('Endpoint:   CLKGEN_U0/U_DCLK0_OD_DIV1P5/SAMP_CNT_reg_2_', GREEN, True)
    add('             (rising edge flip-flop clocked by RX0_OD_CLK)', MUTED)
    add('Path Group: RX0_OD_CLK', YELLOW)
    add('', MUTED)
    add('  clock RX0_OD_CLK_DIV2 (rise edge)              2.520000   2.520000', MUTED)
    add('  clk_lane_od_L0 (in)                            0.000000 & 2.520000 f', MUTED)
    add('  C_12__IOBUF/I (CLKBUFX8AS9)                    0.000252 & 2.520252 f', MUTED)
    add('  C_12__IOBUF/O (CLKBUFX8AS9)                    0.162749 & 2.683001 f', MUTED)
    add('  ... (时钟树 4.0ns) ...', MUTED)
    add('  LC_CSPIF_L0/KEY_RST_18UI_reg/Q (DFFRBQX1AS9)   0.380941 & 4.704466 f', ACCENT, True)
    add('  LC_CSPIF_L0/PLACE_FE_OFC33_.../O (BUFX8AS9)    0.252250 & 4.956776 f', ACCENT)
    add('  CLKGEN_U0/U_DCLK0_OD_DIV1P5/PLACE_FE_.../O(INV) 0.199178 & 5.256471 r', ACCENT)
    add('  CLKGEN_U0/U_DCLK0_OD_DIV1P5/PLACE_FE_PSBC15/O (BUFX2) 0.250709 & 5.509114 r', ACCENT)
    add('  CLKGEN_U0/U_DCLK0_OD_DIV1P5/SAMP_CNT_reg_2_/D (AND2DFFRBQX2) 0.028939 & 5.538052 r', ACCENT, True)
    add('  data arrival time                               5.538052', ACCENT)
    add('', MUTED)
    add('  clock RX0_OD_CLK (rise edge)                   5.040000   5.040000', MUTED)
    add('  ... (时钟树) ...', MUTED)
    add('  CLKGEN_U0/U_DCLK0_OD_DIV1P5/SAMP_CNT_reg_2_/CK  0.004551 & 6.364950 r', GREEN)
    add('  clock reconvergence pessimism                  0.000210   6.365160', MUTED)
    add('  clock uncertainty                             -0.400000   5.965160', MUTED)
    add('  library setup time                             1.000000  -0.211856', MUTED)
    add('  data required time                                       5.753305', MUTED)
    add('  ---------------------------------------------------------------------', MUTED)
    add('  data required time                                        5.753305', MUTED)
    add('  data arrival time                                         5.538052', MUTED)
    add('  ---------------------------------------------------------------------', MUTED)
    add('  slack (MET)                                           0.215253', GREEN, True)

    render(
        '① 1P 模式 · 被误报的 SAMP_CNT 路径（wc_typical_125）',
        'startpoint=KEY_RST_18UI_reg(RX0_OD_CLK_DIV2) → endpoint=SAMP_CNT_reg_2_(RX0_OD_CLK)',
        lines, os.path.join(OUT, 'rpt_1p_sampcnt.png')
    )


def build_2p_report():
    lines = []
    def add(t, color=FG, bold=False): lines.append((t, color, bold))

    add('Report : timing  (delay_type max · slack_lesser_than 0.5 · pba path)', MUTED)
    add('Design : HV2M23_digital_top   Corner: wc_typical_125   Mode: 2P (dual lane)', MUTED)
    add('', MUTED)
    add('Startpoint: CENTER1/TOTAL_DTCTL/DTCTL_L1/SL_DLY3_reg', CYAN, True)
    add('             (rising edge flip-flop clocked by CLK_L1_DTCTL_OD_DIV1P5)', MUTED)
    add('Endpoint:   CENTER1/TOTAL_DTCTL/DTCTL_L0/DB_L_AB_SWAP_ACTIVE_reg', GREEN, True)
    add('             (rising edge flip-flop clocked by CLK_L0_DTCTL_OD_DIV1P5)', MUTED)
    add('Last common pin: C_12__IOBUF/O', MUTED)
    add('Path Group: CLK_L0_DTCTL_OD_DIV1P5', YELLOW)
    add('', MUTED)
    add('  clock CLK_L1_DTCTL_OD_DIV1P5 (rise edge)       5.355000   5.355000', MUTED)
    add('  clk_lane_od_L0 (in)                            0.000000 & 5.355278 r', MUTED)
    add('  CLKGEN_U1/BUF_DCLK0_OD/O (CLKBUFX4AS9)         0.323524 & 5.842522 r', MUTED)
    add('  ... (时钟树 5.9ns，跨 lane 到 lane1) ...', MUTED)
    add('  CLKGEN_U1/U_DCLK1_OD_DIV1P5/SAMP_CNT_reg_2_/CK 0.001182 & 6.908620 r', ACCENT, True)
    add('  CLKGEN_U1/U_DCLK1_OD_DIV1P5/SAMP_CNT_reg_2_/Q  0.461162 & 7.369782 f', ACCENT, True)
    add('  CLKGEN_U1/U_DCLK1_OD_DIV1P5/U5/O (CLKOR2X1)    0.279905 & 7.662199 f', ACCENT)
    add('  ... (数据路径 7.7→10.2ns，经 MUX/分频器) ...', MUTED)
    add('  CENTER1/TOTAL_DTCTL/DTCTL_L1/SL_DLY3_reg/CK     0.006711 & 10.217807 r', ACCENT)
    add('  CENTER1/TOTAL_DTCTL/DTCTL_L1/SL_DLY3_reg/Q      0.486537 & 10.704344 r', ACCENT, True)
    add('  ... (组合逻辑 10.7→11.9ns) ...', MUTED)
    add('  DTCTL_COMB/U16/O (OAI222X1)                    0.302055 & 11.484543 r', ACCENT)
    add('  DTCTL_L0/PLACE_FE_RC_30_0/B1 (AOI12X1)         0.223774 & 11.923440 r', ACCENT)
    add('  ...', MUTED)
    add('  data arrival time / required time ...', MUTED)
    add('  slack (MET)   (2P 下真实检查，时序收敛)', GREEN, True)

    render(
        '② 2P 模式 · 同一族 lane1 路径的真实检查（wc_typical_125）',
        '2P 下 lane1 工作 → SAMP_CNT / SL_DLY3 等路径必须真查（不能 false）',
        lines, os.path.join(OUT, 'rpt_2p_sampcnt.png')
    )


def build_constraint_fig():
    lines = []
    def add(t, color=FG, bold=False): lines.append((t, color, bold))

    add('  # ============ 方案 B：对 1P 假路径设置 set_max_delay ============', YELLOW, True)
    add('  # 合并约束后：不设 false path（否则 2P 漏检），改用 max_delay 覆盖', MUTED)
    add('  # 值 = 2P 模式真实周期（10.71ns），不多不少', MUTED)
    add('', MUTED)
    add('  set_max_delay 10.71 \\', ACCENT, True)
    add('    -through [get_pins {u_LOGIC_CENTER/LINK_LOGIC/LC_CSPIF_L0/KEY_RST_18UI_reg/Q}] \\', CYAN, True)
    add('    -to     [get_pins {u_LOGIC_CENTER/CLKGEN_U1/U_DCLK1_OD_DIV1P5/SAMP_CNT_reg_*/D}]', GREEN, True)
    add('', MUTED)
    add('  # ---------- 方案 B 检查清单 ----------', YELLOW, True)
    add('  # ① 2P 下这条路径 slack 必须先 MET（有真实余量）', MUTED)
    add('  # ② 设完对比 2P 报告 slack 无异常（证明没过度放松）', MUTED)
    add('  # ③ -through 起点 + -to 终点精确限定，别误伤真实路径', MUTED)
    add('  # ④ 全局搜索同路径无残留 set_false_path（优先级冲突，false 吞 max_delay）', MUTED)
    add('  # ⑤ hold 检查照常跑（max_delay 只影响 setup）', MUTED)

    render(
        '③ 在报告路径上精确设置约束（set_max_delay 写法）',
        '起点 -through → 终点 -to，值取 2P 周期；与 false_path 不混用',
        lines, os.path.join(OUT, 'rpt_constraint.png')
    )


if __name__ == '__main__':
    build_1p_report()
    build_2p_report()
    build_constraint_fig()
    print('done:', os.listdir(OUT))
