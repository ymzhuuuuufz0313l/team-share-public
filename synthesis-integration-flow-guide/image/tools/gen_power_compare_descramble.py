# -*- coding: utf-8 -*-
# gen_power_compare_descramble.py — descramble/noscramble 2lane 1.6G 单独对比图（1106）
# 生成物：image/power_compare_descramble_1106.png（本目录脚本按图版标准规则 4 归位）
# 模板：与 gen_power_compare_vertical.py 前四块同款（teal 块 6 列 + HV2M23 高亮）。
# 合规三处（2026-11-06 按 pil-table-render teal 节修正，此前版本被用户驳回）：
#   1. 4x 总超采样（G.S=2 × 本图 EXTRA=2；skill「防缩放糊」）
#   2. 同一元素单字体整串渲染（禁逐字符中英混排）
#   3. ascent 基线居中（font.getmetrics()[0]，禁 (cell_h-size)//2 近似）
# 数据源：1106 PTPX Time-Based 实测（t_8b2lane_descramble24b/8b/noscramble 后仿 VCD，2lane 1.6G）。
# 24b 首跑波形速率不对曾误测 8.57 mW，已作废，以复跑 14.7 mW 为准。
import os
import sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
import _gen_be_review_images as G
from PIL import Image, ImageDraw

EXTRA = 2                       # 本图额外超采样系数（G.S=2 × EXTRA=2 = 总 4x）
S = G.S * EXTRA

f_t = G.F_CJK_B(11 * EXTRA)     # 块标题（CJK 粗体单一字体，整串渲染）
f_h = G.F_MONO_B(9 * EXTRA)     # 表头（纯 ASCII，mono 单字体）
f_m = G.F_MONO(9 * EXTRA)       # 数据（纯 ASCII，mono 单字体）

TEAL     = G.TEAL
TEAL_HI  = G.TEAL_HI
ZEBRA    = G.ZEBRA
INK      = G.INK
BORDER   = G.BORDER
GRID     = G.GRID
TXT_HL   = (14, 60, 52)

HDR = ["CHIP", "Clk Freq", "Process", "Area", "Lane", "Normal"]

# 1106 实测：noscramble=13.3 / descramble 8b=15.2 / 24b=14.7 mW（Total；细分列待补报告）
ROWS = [
    ["HV2M23(noscramble)", "1.6G", "145", "167727", "2L", "13.3"],
    ["HV2M23(descr8b)", "1.6G", "145", "167727", "2L", "15.2"],
    ["HV2M23(descr24b)", "1.6G", "145", "167727", "2L", "14.7"],
]

TITLE = "PTPX 功耗对比（SVT，1106，descramble 2lane 1.6G）"

TITLE_H = 22 * S
HDR_H   = 20 * S
ROW_H   = 13 * S
MARGIN  = 8 * S
PAD     = 8 * S

def text_w(t, f):
    # 纯长度测量：整串一次量（等宽 ASCII + CJK 全角近似）
    w = 0
    for ch in t:
        w += f_m.getlength(ch) if ord(ch) < 0x2E80 else f_c.getlength(ch)
    return w

def ascent(f):
    return f.getmetrics()[0]

col_w = [0] * len(HDR)
for j, h in enumerate(HDR):
    col_w[j] = int(text_w(h, f_h)) + PAD * 2
for r in ROWS:
    for j, v in enumerate(r):
        col_w[j] = max(col_w[j], int(text_w(v, f_m)) + PAD * 2)
W = sum(col_w) + MARGIN * 2
H = MARGIN * 2 + TITLE_H + HDR_H + ROW_H * len(ROWS)

img = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)

y = MARGIN
# 块标题条（CJK 粗体整串 + ascent 居中）
d.rectangle([MARGIN, y, W - MARGIN, y + TITLE_H], fill=TEAL)
d.text((MARGIN + PAD, y + (TITLE_H - ascent(f_t)) // 2), TITLE, font=f_t, fill=(255, 255, 255))
y += TITLE_H
# 表头（单字体整串 + ascent 居中）
d.rectangle([MARGIN, y, W - MARGIN, y + HDR_H], fill=TEAL)
x = MARGIN
for j, htext in enumerate(HDR):
    tw = text_w(htext, f_h)
    d.text((x + (col_w[j] - tw) / 2, y + (HDR_H - ascent(f_h)) // 2),
           htext, font=f_h, fill=(255, 255, 255))
    x += col_w[j]
y += HDR_H
# 数据行（ASCII 单元格 = mono 单字体整串；首列 ascent 居中）
for i, r in enumerate(ROWS):
    hl = r[0].startswith("HV2M23")
    bg = TEAL_HI if hl else (ZEBRA if i % 2 else (255, 255, 255))
    d.rectangle([MARGIN, y, W - MARGIN, y + ROW_H], fill=bg)
    x = MARGIN
    for j, v in enumerate(r):
        fill = TXT_HL if hl else INK
        if j == 0:
            d.text((x + PAD, y + (ROW_H - ascent(f_m)) // 2), v, font=f_m, fill=fill)
        else:
            tw = text_w(v, f_m)
            d.text((x + (col_w[j] - tw) / 2, y + (ROW_H - ascent(f_m)) // 2),
                   v, font=f_m, fill=fill)
        x += col_w[j]
    d.line([MARGIN, y + ROW_H, W - MARGIN, y + ROW_H], fill=GRID, width=S)
    y += ROW_H
d.rectangle([MARGIN, MARGIN, W - MARGIN, y], outline=BORDER, width=S)

out = os.path.join(TOOLS, "..", "power_compare_descramble_1106.png")
img.save(out)
print("done", img.size, "->", os.path.normpath(out))

# ymzhu 2026-11-06 16:05
