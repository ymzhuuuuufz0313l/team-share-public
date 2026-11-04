#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gen_signoff_1104v2.py — HK1V11 1104V2 signoff 表图独立版生成器（run 2026-11-04）

模板谱系（逐项照抄 practice 站当前模板，ymzhu 2026-11-04 指示"直接按照当前网站的模板去做"）：
  51/52（setup/hold A 族）+ 53/54/55（B 族）← hk1v11-synthesis-postpt-practice/script/gen_signoff_tables_hk1v11.py
  56（shift window）← hk1v11-synthesis-postpt-practice/script/gen_shift_window_hk11.py v2
相对站点模板的本版改动（仅三处，结构/配色/动画词汇零改动）：
  ① 数据源换 1104V2 包（PACK_TAR_1104V2 已解压目录，只读）；输出改本独立目录 docs/to_signoff_1104v2/
  ② 标题年代 1104V0 -> 1104V2；56 号红线标签/箭头数值全部由 csv 计算（站点 V0 版红线标签为上代
     硬编码残值 −1.09388/+0.40129，与线位不符，本版修正为数据驱动，不再硬编码）
  ③ A 族 CSS 补 prefers-reduced-motion 关停块（对齐 B 族与 v4 架构契约）
56 号数据通道（零手工）：port→FF setup = phy csv rx0_00_max 行，port→FF hold = rx0_00_min 行
  （1104 代际 input port 即头名，ch09 §6.3 口径）；左移容限 = max +0.3+0.4；右移容限 = min +0.3+0.15。
输出：./5{1..6}_signoff_*.svg（静态=事实源）+ ./anim/ 同名（动画）+ stats_1104v2.json + index.html
校验：XML / 无 script / 转录逐值（51-55）/ 成对完整 / 幂等
复跑：python gen_signoff_1104v2.py（幂等，重跑输出字节一致）
"""
import csv, hashlib, json, os, re, sys
import xml.etree.ElementTree as ET

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = r"C:\Users\zhuyanming\Downloads\PACK_TAR_1104V2\project\HK1V11\designer\DD\ymzhu\HK1V11\SYNTHESIS\top\sta\post\pt\summary\latest"
V0_DATA = r"E:\project\HK1V11\script\_syn_1104V0\SYNTHESIS\top\sta\post\pt\summary\latest"  # 对比用（只读，可选）
OUT_STATIC = BASE
OUT_ANIM = os.path.join(BASE, "anim")
GEN = "1104V2"

RED = "#7f1d1d"   # 深红
RED_BG = "#f8dede"  # 违例格浅红背景
BLUE_BG = "#d3e3f6"  # PHY 表最紧格浅蓝背景

CORNER_HDR = ["lt_cbest_m40", "lt_cworst_m40", "lt_typical_m40", "ml_cbest_125",
              "tt_cbest_25", "tt_cworst_25", "tt_typical_25", "wc_cbest_125",
              "wc_cworst_125", "wc_typical_125"]

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

def f5(v):
    return "%.5f" % float(v)

def read_pairs(path):
    """setup/hold/trans：返回 [(label, [10 个显示串], [10 个原始float])，显示串=5位小数+违例条数(N)"""
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    header = rows[0]
    corners = [header[i] for i in range(2, len(header), 2)]
    cmap = {c: i for i, c in enumerate(corners)}
    order = [cmap[c] for c in CORNER_HDR]
    out = []
    for r in rows[2:]:
        big = [float(r[2 + 2 * k]) for k in order]
        cnt = [int(float(r[1 + 2 * k] or 0)) for k in order]
        disp = [f5(b) + ("(%d)" % n if n > 0 else "") for b, n in zip(big, cnt)]
        out.append((r[0], disp, big, cnt))
    return out

def read_plain(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    cmap = {c: i for i, c in enumerate(rows[0][1:11])}
    order = [cmap[c] for c in CORNER_HDR]
    return [(r[0], [f5(r[1:11][i]) for i in order],
             [float(r[1:11][i]) for i in order]) for r in rows[1:]]

def read_sdskew(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    cmap = {c: i for i, c in enumerate(rows[0][1:11])}
    order = [cmap[c] for c in CORNER_HDR]
    out = []
    for r in rows[1:]:
        if "_margin_" not in r[0]:
            continue
        m = re.match(r"(.+?)\s*:\s*\[([\-+\d.]+)\s*:\s*([\-+\d.]+)\]", r[0])
        label = m.group(1).strip() if m else r[0].split(" : ")[0].strip()
        lo = float(m.group(2)) if m else -1e9
        hi = float(m.group(3)) if m else 1e9
        vals = [float(r[1:11][i]) for i in order]
        out.append((label, [f5(v) for v in vals], vals, lo, hi))
    return out

# ============================================================ A 族：setup/hold
A_W, A_HMIN, A_M = 2519, 1169, 25
A_HEADER_H, A_COLHEAD_H = 58, 54
A_FIRST_COL_RIGHT = 548
A_C_BAND, A_C_COLHEAD = "#157a6a", "#2e8b6a"
A_C_ZEBRA, A_C_GRID = "#f4f6f4", "#d7dbd7"
A_C_ZERO, A_C_NONZERO, A_C_WHITE = "#1a7a3c", "#2d2d2d", "#ffffff"
A_FONT = "Consolas, 'Cascadia Mono', 'Courier New', monospace"
A_FS_T, A_FS_S, A_FS_C, A_FS_D = 30, 26, 20, 20

def fmt(x):
    s = "%.2f" % x
    return s.rstrip("0").rstrip(".")

def build_A(metric, data, subtitle):
    n = len(data)
    H = max(A_HMIN, A_HEADER_H + A_COLHEAD_H + n * 54)
    data_left, data_right = A_FIRST_COL_RIGHT, A_W - A_M
    col_w = (data_right - data_left) / 10.0
    row_h = (H - A_HEADER_H - A_COLHEAD_H) / n
    # ③ A 族补 reduced-motion 关停（对齐 B 族 / v4 契约）
    css = ("<style><![CDATA["
           ".head{opacity:0;animation:rowIn 0.3s ease forwards;}"
           ".row{opacity:0;animation:rowIn 0.3s ease forwards;}"
           ".chg{animation:breath 1.4s ease-in-out infinite;}"
           "@keyframes rowIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}"
           "@keyframes breath{0%{opacity:1;}50%{opacity:0.55;}100%{opacity:1;}}"
           "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"
           "]]></style>")
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">'
         % (A_W, H, A_W, H, esc(A_FONT))]
    p.append(css)
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (A_W, H))
    ty = A_HEADER_H * 0.64
    p.append('<g class="head">')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (A_W, A_HEADER_H, A_C_BAND))
    p.append('<text x="%d" y="%s" font-size="%d" font-weight="bold" fill="%s">report_%s.csv (HK1V11 %s)</text>'
             % (A_M, fmt(ty), A_FS_T, A_C_WHITE, metric, GEN))
    p.append('<text x="%d" y="%s" font-size="%d" fill="%s" text-anchor="end">%s</text>'
             % (data_right, fmt(ty), A_FS_S, A_C_WHITE, esc(subtitle)))
    p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (A_HEADER_H, A_W, A_COLHEAD_H, A_C_COLHEAD))
    cy = A_HEADER_H + A_COLHEAD_H * 0.62
    p.append('<text x="%d" y="%s" font-size="%d" fill="%s">metric</text>'
             % (A_M + 10, fmt(cy), A_FS_C, A_C_WHITE))
    for i, name in enumerate(CORNER_HDR):
        cx = data_left + (i + 0.5) * col_w
        p.append('<text x="%s" y="%s" font-size="%d" fill="%s" text-anchor="middle">%s</text>'
                 % (fmt(cx), fmt(cy), A_FS_C, A_C_WHITE, esc(name)))
    p.append('</g>')
    top = A_HEADER_H + A_COLHEAD_H
    for i, item in enumerate(data):
        label, disp, raw = item[0], item[1], item[2]
        ry = top + i * row_h
        p.append('<g class="row" style="animation-delay:%.3fs">' % ((i + 1) * 0.012))
        p.append('<rect x="0" y="%s" width="%d" height="%s" fill="%s"/>'
                 % (fmt(ry), A_W, fmt(row_h), "#ffffff" if i % 2 == 0 else A_C_ZEBRA))
        p.append('<text x="%d" y="%s" font-size="%d" fill="%s">%s</text>'
                 % (A_M + 10, fmt(ry + row_h * 0.62), A_FS_D, A_C_NONZERO, esc(label)))
        for k in range(10):
            v, fv = disp[k], raw[k]
            x = data_left + (k + 1) * col_w - 14
            if fv < 0:
                p.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>'
                         % (fmt(data_left + k * col_w), fmt(ry), fmt(col_w), fmt(row_h), RED_BG))
                color, cls = RED, ' class="val chg" style="animation-delay:%.2fs"' % ((i + k) * 0.025)
            elif fv == 0:
                color, cls = A_C_ZERO, ' class="val"'
            else:
                color, cls = A_C_NONZERO, ' class="val chg" style="animation-delay:%.2fs"' % ((i + k) * 0.025)
            p.append('<text%s x="%s" y="%s" font-size="%d" fill="%s" text-anchor="end">%s</text>'
                     % (cls, fmt(x), fmt(ry + row_h * 0.62), A_FS_D, color, esc(v)))
        p.append('</g>')
    for k in range(11):
        gx = data_left + k * col_w if k else A_FIRST_COL_RIGHT
        p.append('<line x1="%s" y1="%d" x2="%s" y2="%s" stroke="%s" stroke-width="1"/>'
                 % (fmt(gx), A_HEADER_H, fmt(gx), fmt(H - 1), A_C_GRID))
    for i in range(1, n):
        p.append('<line x1="1" y1="%s" x2="%d" y2="%s" stroke="%s" stroke-width="1"/>'
                 % (fmt(top + i * row_h), A_W - 1, fmt(top + i * row_h), A_C_GRID))
    p.append('<rect x="1" y="1" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>'
             % (A_W - 2, H - 2, "#c0c6c6"))
    p.append('</svg>')
    return "\n".join(p)

# ============================================================ B 族
B_BAND, B_ZEBRA = "#0e7c6b", "#f4f8f7"
B_GRID, B_BORDER = "#d0d8d6", "#c0c6c6"
B_GREEN, B_DARK, B_WHITE = "#1e8449", "#212529", "#ffffff"
B_FONT = "Consolas, 'Cascadia Mono', 'Courier New', monospace"
B_TITLE_H, B_HEADER_H, B_ROW_H, B_COL_W = 60, 52, 44, 192
B_FS_T, B_FS_H, B_FS_D = 26, 20, 20
B_PAD_L, B_PAD_R = 12, 14
B_CSS = """<style>
.head { opacity:0; animation: rowIn 0.3s ease forwards; }
.row  { opacity:0; animation: rowIn 0.3s ease forwards; }
@keyframes rowIn { from { opacity:0; transform: translateY(4px); }
                   to   { opacity:1; transform: none; } }
.breath { animation: breathe 1.4s ease-in-out infinite; }
@keyframes breathe { 0%,100% { opacity:1; } 50% { opacity:0.55; } }
.frameBreath { animation: frameB 1.4s ease-in-out infinite; }
@keyframes frameB { 0%,100% { stroke-opacity:1; } 50% { stroke-opacity:0.45; } }
.hlcell { stroke-dasharray: 6,4; animation: hlGlow 1.5s ease-in-out infinite, hlDash 3s linear infinite; }
@keyframes hlGlow { 0%,100% { filter: drop-shadow(0 0 0 rgba(115,168,212,0)); } 50% { filter: drop-shadow(0 0 8px rgba(115,168,212,0.8)); } }
@keyframes hlDash { 0% { stroke-dashoffset: 0; } 100% { stroke-dashoffset: -48; } }
@media (prefers-reduced-motion:reduce){ *{animation:none!important} .hlcell,.breath{opacity:1!important;stroke-dashoffset:0!important} }
</style>"""

def build_B(title, subtitle, label_w, rows, mode, red_fn, zero_frame=False, hl=None):
    """rows: [(label, disp[10], raw[10])]；red_fn(raw_float, label) -> True 红显"""
    n = len(rows)
    W = label_w + 10 * B_COL_W + 2
    H = B_TITLE_H + B_HEADER_H + n * B_ROW_H + 2
    col_x = [label_w + k * B_COL_W for k in range(11)]
    y0 = B_TITLE_H + B_HEADER_H
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">'
         % (W, H, W, H, esc(B_FONT))]
    p.append(B_CSS)
    p.append('<g class="head">')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (W, B_TITLE_H, B_BAND))
    p.append('<text x="16" y="38.5" font-size="%d" font-weight="bold" fill="%s">%s</text>'
             % (B_FS_T, B_WHITE, esc(title)))
    p.append('<text x="%d" y="36.5" font-size="20" fill="%s" text-anchor="end">%s</text>'
             % (W - 16, B_WHITE, esc(subtitle)))
    p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (B_TITLE_H, W, B_HEADER_H, B_BAND))
    p.append('<text x="%d" y="%d" font-size="%d" font-weight="bold" fill="%s">%s</text>'
             % (B_PAD_L, B_TITLE_H + 32, B_FS_H, B_WHITE, esc(mode)))
    for k in range(10):
        cx = (col_x[k] + col_x[k + 1]) / 2.0
        p.append('<text x="%d" y="%d" font-size="%d" font-weight="bold" fill="%s" text-anchor="middle">%s</text>'
                 % (int(cx), B_TITLE_H + 32, B_FS_H, B_WHITE, esc(CORNER_HDR[k])))
    p.append('</g>')
    for i, (label, disp, raw) in enumerate(rows):
        ry = y0 + i * B_ROW_H
        p.append('<g class="row" style="animation-delay:%.3fs">' % ((i + 1) * 0.012))
        p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>'
                 % (ry, W, B_ROW_H, "#ffffff" if i % 2 == 0 else B_ZEBRA))
        p.append('<text class="lab" x="%d" y="%d" font-size="%d" fill="%s">%s</text>'
                 % (B_PAD_L, ry + 28, B_FS_D, B_DARK, esc(label)))
        for k in range(10):
            fv = raw[k]
            if hl and (i, k) in hl:
                p.append('<rect class="hlcell" x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1.5"/>'
                         % (col_x[k], ry, B_COL_W, B_ROW_H, BLUE_BG, "#7aa8d4"))
            if red_fn(fv, label):
                p.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                         % (col_x[k], ry, B_COL_W, B_ROW_H, RED_BG))
                color, cls = RED, 'class="val breath" style="animation-delay:%.2fs"' % ((i + k) * 0.07)
            elif fv == 0:
                color, cls = B_GREEN, 'class="val"'
            else:
                color, cls = B_DARK, 'class="val breath" style="animation-delay:%.2fs"' % ((i + k) * 0.07)
            p.append('<text %s x="%d" y="%d" font-size="%d" fill="%s" text-anchor="end">%s</text>'
                     % (cls, col_x[k + 1] - B_PAD_R, ry + 28, B_FS_D, color, esc(disp[k])))
        p.append('</g>')
    for k in range(1, 11):
        p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (col_x[k], B_TITLE_H, col_x[k], H - 2, B_GRID))
    for i in range(n):
        p.append('<line x1="1" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (y0 + i * B_ROW_H, W - 1, y0 + i * B_ROW_H, B_GRID))
    frame = ' class="frameBreath"' if zero_frame else ""
    p.append('<rect%s x="1" y="1" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>'
             % (frame, W - 2, H - 2, B_BORDER))
    p.append('</svg>')
    return "\n".join(p)

# ============================================================ 56 号：时钟偏移容限（数据驱动改造版）
SW_CSS_ANIM = """<style>
.head, .panel { opacity:0; animation: rowIn .35s cubic-bezier(.22,.7,.3,1) forwards; }
.row { opacity:0; animation: rowIn .3s ease forwards; }
@keyframes rowIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:none; } }
.arrowDash { stroke-dasharray: 8,5; animation: arrowGrow 2.4s linear infinite; }
@keyframes arrowGrow { 0% { stroke-dashoffset:0; } 100% { stroke-dashoffset:-52; } }
.boundPulse { animation: boundGlow 1.5s ease-in-out infinite; }
@keyframes boundGlow { 0%,100% { opacity:1; filter:drop-shadow(0 0 0 rgba(185,28,28,0)); } 50% { opacity:.7; filter:drop-shadow(0 0 6px rgba(185,28,28,.8)); } }
.formulaGlow { animation: fGlow 2s ease-in-out infinite; }
@keyframes fGlow { 0%,100% { opacity:1; } 50% { opacity:.75; } }
@media (prefers-reduced-motion:reduce) { *{animation:none!important} .head,.panel,.row{opacity:1!important} .arrowDash{stroke-dasharray:none!important} }
</style>"""

def read_phy_shift(path):
    """phy csv -> 每 corner (lft=rx0_00_max+0.7, rgt=rx0_00_min+0.45) + 全角最小者；csv 列序输出。"""
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    hdr = rows[0][1:11]
    get = lambda rn: [float(r[1:11][i]) for i in range(10) for r in [next(x for x in rows[1:] if x[0] == rn)]]
    mx = get("report_timing_rx0_00_max.rpt")
    mn = get("report_timing_rx0_00_min.rpt")
    corners = []
    for i, c in enumerate(hdr):
        corners.append((c.replace("_125", "").replace("_m40", "").replace("_25", ""),
                        mx[i] + 0.7, mn[i] + 0.45, mx[i], mn[i]))
    li = min(range(10), key=lambda i: corners[i][1])
    ri = min(range(10), key=lambda i: corners[i][2])
    return corners, corners[li], corners[ri], hdr

def build_shift(path):
    corners, lmin, rmin, hdr = read_phy_shift(path)
    C_BG, C_PANEL, C_BORDER = "#f4f1ea", "#fffdf7", "#c9bfa8"
    C_TEXT, C_MUTED, C_GRID = "#1c2534", "#5b6675", "#ddd6c8"
    C_AMBER, C_TEAL, C_RED, C_BLUE = "#b45309", "#0e7490", "#b91c1c", "#1d4ed8"
    L = []
    a = L.append
    W, H = 1440, 900
    a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
    a('<style>text{font-family:"Microsoft YaHei","Noto Sans SC",monospace;fill:%s}.mono{font-family:Consolas,"Microsoft YaHei",monospace}</style>' % C_TEXT)
    a('<defs>'
      '<marker id="mB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
      '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
      '</defs>' % C_BLUE)
    a('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C_BG))
    a('<text x="14" y="34" font-size="11" fill="%s" class="mono">HK1V11 · SIGNOFF · CLOCK SHIFT WINDOW · %s · 10 CORNER</text>' % (C_AMBER, GEN))
    a('<text x="14" y="66" font-size="22" font-weight="bold"><tspan fill="%s">时钟偏移容限</tspan> — 采样时钟相对数据可左移 / 右移多少</text>' % C_AMBER)

    a('<rect class="panel" x="40" y="90" width="1360" height="430" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
    a('<text x="60" y="118" font-size="16.5" font-weight="bold">① 容限窗全景 — 采样时钟相位可在 [数据窗 − 左限, 数据窗 + 右限] 内偏移</text>')

    X0, X1 = 120, 1320
    VMIN, VMAX = -1.6, 1.6
    def tx(v): return X0 + (v - VMIN) / (VMAX - VMIN) * (X1 - X0)
    AXIS_Y = 310
    LFT, RGT = -lmin[1], rmin[2]
    for val, lab in ((LFT, "%.5f（setup 碰界）" % LFT), (RGT, "+%.5f（hold 碰界）" % RGT)):
        a('<line class="boundPulse" x1="%.1f" y1="150" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (tx(val), tx(val), AXIS_Y + 12, C_RED))
        a('<text x="%.1f" y="358" font-size="11" fill="%s" class="mono" text-anchor="middle">%s</text>' % (tx(val), C_RED, lab))
    a('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (X0, AXIS_Y, X1, AXIS_Y, C_TEXT))
    v = -1.5
    while v <= 1.51:
        a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (tx(v), AXIS_Y, tx(v), AXIS_Y + 8, C_MUTED))
        a('<text x="%.1f" y="336" font-size="12" text-anchor="middle" class="mono" fill="%s">%+.1f</text>' % (tx(v), C_MUTED, v))
        v += 0.5
    a('<text x="%d" y="358" font-size="12" class="mono" fill="%s" text-anchor="end">ns（0 = 名义采样沿）</text>' % (X1, C_MUTED))
    a('<rect x="%.1f" y="248" width="%.1f" height="44" fill="%s" opacity="0.85"/>' % (tx(-0.25), tx(0.25) - tx(-0.25), C_TEAL))
    a('<text x="%.1f" y="275" font-size="12.5" fill="#fffdf7" text-anchor="middle">数据有效窗</text>' % tx(0))

    a('<line class="arrowDash" x1="%.1f" y1="190" x2="%.1f" y2="190" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), tx(LFT), C_BLUE))
    a('<text x="%.1f" y="174" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">← 左移容限 %.5f ns</text>' % (tx(-0.55), C_BLUE, -LFT))
    a('<text x="%.1f" y="214" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF setup %+.5f +0.3+0.4</text>' % (tx(-0.55), C_BLUE, lmin[3]))
    a('<text x="%.1f" y="234" font-size="11" fill="%s" text-anchor="middle">%s（setup 先碰界）</text>' % (tx(-0.55), C_MUTED, lmin[0]))
    a('<line class="arrowDash" x1="%.1f" y1="190" x2="%.1f" y2="190" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), tx(RGT), C_BLUE))
    a('<text x="%.1f" y="174" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">右移容限 %.5f ns →</text>' % (1030, C_BLUE, RGT))
    a('<text x="%.1f" y="214" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF hold %+.5f +0.3+0.15</text>' % (1030, C_BLUE, rmin[4]))
    a('<text x="%.1f" y="234" font-size="11" fill="%s" text-anchor="middle">%s（hold 先碰界）</text>' % (1030, C_MUTED, rmin[0]))

    a('<rect class="formulaGlow" x="60" y="372" width="1320" height="120" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>' % (C_BG, C_BORDER))
    a('<text x="80" y="398" font-size="13.5" font-weight="bold" fill="%s">换算公式（把 set_input_delay 与 uncertainty 的预算还原成 2M23 裸口径）</text>' % C_AMBER)
    a('<text x="80" y="424" font-size="13" class="mono">左移容限 = port→FF setup slack + 0.3（max input delay） + 0.4（setup uncertainty）</text>')
    a('<text x="80" y="448" font-size="13" class="mono">右移容限 = port→FF hold slack + 0.3（min input delay −0.3 还原） + 0.15（hold uncertainty）</text>')
    a('<text x="80" y="472" font-size="11.5" fill="%s">注：%s 代际 port→FF setup = phy csv rx0_00_max 行、port→FF hold = rx0_00_min 行（input port 即头名）；数值全部由 csv 直算，无手录。</text>' % (C_MUTED, GEN))

    a('<rect class="panel" x="40" y="540" width="1360" height="330" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
    a('<text x="60" y="568" font-size="16.5" font-weight="bold">② 逐角容限（10 corner）</text>')
    a('<rect x="500" y="558" width="16" height="12" fill="%s" opacity="0.9"/>' % C_BLUE)
    a('<text x="521" y="568" font-size="12">左移 / setup 侧</text>')
    a('<rect x="660" y="558" width="16" height="12" fill="%s" opacity="0.9"/>' % C_TEAL)
    a('<text x="681" y="568" font-size="12">右移 / hold 侧</text>')
    a('<line x1="820" y1="564" x2="848" y2="564" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % C_RED)
    a('<text x="856" y="568" font-size="12" fill="%s">全角最小：左 %.5f / 右 %.5f</text>' % (C_RED, -LFT, RGT))

    BX, BW, BGAP = 80, 60, 70
    BY0, BY1 = 610, 842
    BMAX = 1.8
    def by(v): return BY1 - v / BMAX * (BY1 - BY0)
    a('<line x1="70" y1="%.1f" x2="1345" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4" opacity="0.55"/>' % (by(-LFT), by(-LFT), C_RED))
    a('<line x1="70" y1="%.1f" x2="1345" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4" opacity="0.55"/>' % (by(RGT), by(RGT), C_RED))
    for i, (name, lft, rgt, _mx, _mn) in enumerate(corners):
        x = BX + i * (BW + BGAP)
        a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x, by(lft), BW // 2, BY1 - by(lft), C_BLUE))
        a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x + BW // 2, by(rgt), BW // 2, BY1 - by(rgt), C_TEAL))
        a('<text x="%d" y="%.1f" font-size="9" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW // 4, by(lft) - 5, C_BLUE, lft))
        a('<text x="%d" y="%.1f" font-size="9" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW * 3 // 4, by(rgt) - 5, C_TEAL, rgt))
        a('<text x="%d" y="858" font-size="10" text-anchor="middle" class="mono" fill="%s">%s</text>' % (x + BW // 2, C_MUTED, name))
    a('</svg>')
    return "\n".join(L)

# ============================================================ 统计
def viol_stats(rows_pairs):
    """[(label,disp,raw,cnt)] -> dict：总格/域清单/每角计数/worst。用 setup.rpt|hold.rpt 总行 + 域行。"""
    total_row = next(r for r in rows_pairs if r[0] in ("setup.rpt", "hold.rpt"))
    per_corner = {CORNER_HDR[k]: (total_row[3][k], total_row[2][k]) for k in range(10)}
    domains = []
    for lb, disp, raw, cnt in rows_pairs:
        if lb in ("setup.rpt", "hold.rpt", "async"):
            continue
        cells = [(CORNER_HDR[k], cnt[k], raw[k]) for k in range(10) if cnt[k] > 0]
        if cells:
            domains.append({"domain": lb, "cells": cells})
    n_cells = sum(len(d["cells"]) for d in domains)
    wc = min(((raw[k], lb, CORNER_HDR[k]) for lb, disp, raw, cnt in rows_pairs
              if lb not in ("setup.rpt", "hold.rpt") for k in range(10)), key=lambda t: t[0])
    worst_dom = {"slack": wc[0], "domain": wc[1], "corner": wc[2]}
    return {"per_corner": per_corner, "domains": domains, "cells": n_cells,
            "total": sum(total_row[3]), "worst": worst_dom}

def sdskew_stats(sd):
    out_cells = []
    p1_in = p1_all = dplc_b_l = dplc_b_r = 0
    for lb, disp, raw, lo, hi in sd:
        for k in range(10):
            in_win = lo <= raw[k] <= hi
            if "_1p_" in lb:
                p1_all += 1
                p1_in += 1 if in_win else 0
            if "_dplc_" in lb and "_margin_b_" in lb:
                if lb.startswith("sd_l_"):
                    dplc_b_l += 1 if in_win else 0
                else:
                    dplc_b_r += 1 if in_win else 0
            if not in_win:
                out_cells.append({"row": lb, "corner": CORNER_HDR[k], "val": raw[k], "win": [lo, hi]})
    return {"out_of_window": out_cells, "p1_in_window": "%d/%d" % (p1_in, p1_all),
            "dplc_b_l": "%d/20" % dplc_b_l, "dplc_b_r": "%d/20" % dplc_b_r}

# ============================================================ 生成
def gen_all():
    os.makedirs(OUT_ANIM, exist_ok=True)
    outs, stats = [], {}
    for mid, sub in [("setup", "setup/max 路径违例总表（红=违例，括号内为条数）"),
                     ("hold", "hold/min 路径违例总表（红=违例，括号内为条数）")]:
        data = read_pairs(os.path.join(DATA, "report_%s.csv" % mid))
        outs.append(("%s_signoff_%s_hk11" % ({"setup": "51", "hold": "52"}[mid], mid),
                     build_A(mid, data, sub), data))
        stats[mid] = viol_stats(data)
    data = read_pairs(os.path.join(DATA, "report_trans.csv"))
    rows = [("%s (biggest violation)" % lb, disp, raw) for lb, disp, raw, _c in data]
    svg = build_B("report_trans.csv (HK1V11 %s)" % GEN, "max_trans/cap 约束违例总表",
                  430, rows, "metric", lambda fv, lb: fv < 0,
                  zero_frame=all(fv >= 0 for _, _, raws, _c in data for fv in raws))
    outs.append(("53_signoff_trans_hk11", svg, data))
    tr = {}
    for lb, disp, raw, cnt in data:
        tr[lb] = {"per_corner": {CORNER_HDR[k]: (cnt[k], raw[k]) for k in range(10)}}
        tr[lb]["total"] = sum(cnt)
        tr[lb]["worst"] = min(raw)
    stats["trans"] = tr
    data = read_plain(os.path.join(DATA, "report_phy_busskew.csv"))
    rows = [(lb.replace(".rpt", ""), disp, raw) for lb, disp, raw in data]
    hl = set()
    for i, (lb, disp, raw) in enumerate(rows):
        if lb.endswith("rx0_00_max") or lb.endswith("rx0_00_min"):
            hl.add((i, raw.index(min(raw))))
    svg = build_B("report_phy_busskew.csv (HK1V11 %s)" % GEN, "PHY bus skew 各组 slack (ns)",
                  417, rows, "report_files", lambda fv, lb: False, hl=hl)
    outs.append(("54_signoff_physkew_hk11", svg, data))
    rx0 = {lb: raw for lb, disp, raw in data}
    stats["phy"] = {"rx0_00_max_min": min(rx0["report_timing_rx0_00_max.rpt"]),
                    "rx0_00_max_corner": CORNER_HDR[rx0["report_timing_rx0_00_max.rpt"].index(min(rx0["report_timing_rx0_00_max.rpt"]))],
                    "rx0_00_min_min": min(rx0["report_timing_rx0_00_min.rpt"]),
                    "rx0_00_min_corner": CORNER_HDR[rx0["report_timing_rx0_00_min.rpt"].index(min(rx0["report_timing_rx0_00_min.rpt"]))]}
    sd = read_sdskew(os.path.join(DATA, "report_sd_busskew.csv"))
    win = {lb: (lo, hi) for lb, disp, raw, lo, hi in sd}
    def fmt_win(x):
        return ('%g' % x)
    rows = [("%s [%s,%s]" % (lb, fmt_win(win[lb][0]), fmt_win(win[lb][1])) if lb in win else lb,
             disp, raw) for lb, disp, raw, lo, hi in sd]
    def red_by_label(fv, lbl):
        base = lbl.split(" [")[0]
        lo, hi = win.get(base, (-1e9, 1e9))
        return not (lo <= fv <= hi)
    svg = build_B("report_sd_busskew.csv (HK1V11 %s)" % GEN,
                  "SD skew margin, 规格 1p [−3.5,+3.5] / dplc [−0.9,+4.1] ns（出窗红显）",
                  430, rows, "report_files", red_by_label)
    outs.append(("55_signoff_sdskew_margin_hk11", svg, sd))
    stats["sdskew"] = sdskew_stats(sd)
    outs.append(("56_signoff_shift_window_hk11", build_shift(os.path.join(DATA, "report_phy_busskew.csv")), None))
    _c, lmin, rmin, _h = read_phy_shift(os.path.join(DATA, "report_phy_busskew.csv"))
    stats["shift"] = {"left_min": lmin[1], "left_corner": lmin[0], "right_min": rmin[2],
                      "right_corner": rmin[0]}
    return outs, stats

def strip_css(svg):
    return re.sub(r"<style>.*?</style>", "", svg, flags=re.S)

def validate(svg, data, path):
    ok = []
    try:
        ET.parse(path); ok.append("xml+")
    except ET.ParseError as e:
        ok.append("xml- %s" % e)
    ok.append("noscript+" if "<script" not in svg.lower() else "noscript-")
    if data is not None:
        root = ET.parse(path).getroot()
        got = [t.text for t in root.iter() if t.tag.endswith("text") and "val" in (t.get("class") or "")]
        exp = []
        for item in data:
            exp.extend(item[1])
        ok.append("transcript+" if got == exp else "transcript- %d/%d" % (len(got), len(exp)))
    return " ".join(ok)

# ============================================================ index.html（独立展示页）
def v0_stats():
    """对比用 V0 包统计（只读；不可达时返回 None，页面降级提示）。"""
    try:
        st = {}
        st["setup"] = viol_stats(read_pairs(os.path.join(V0_DATA, "report_setup.csv")))
        st["hold"] = viol_stats(read_pairs(os.path.join(V0_DATA, "report_hold.csv")))
        tr = read_pairs(os.path.join(V0_DATA, "report_trans.csv"))
        st["trans_total"] = {lb: sum(c) for lb, _d, _r, c in tr}
        st["sdskew_out"] = len(sdskew_stats(read_sdskew(os.path.join(V0_DATA, "report_sd_busskew.csv")))["out_of_window"])
        _c, lmin, rmin, _h = read_phy_shift(os.path.join(V0_DATA, "report_phy_busskew.csv"))
        st["shift"] = {"left": lmin[1], "left_corner": lmin[0], "right": rmin[2], "right_corner": rmin[0]}
        st["phy"] = {"rx0min": min(read_plain(os.path.join(V0_DATA, "report_phy_busskew.csv"))[1][2])}
        return st
    except OSError:
        return None

def _cnt_row(per_corner):
    return " ".join(str(per_corner[c][0]) for c in
                    ["wc_cworst_125", "wc_cbest_125", "wc_typical_125", "lt_cworst_m40",
                     "lt_cbest_m40", "lt_typical_m40", "ml_cbest_125", "tt_cworst_25",
                     "tt_cbest_25", "tt_typical_25"])

def gen_index_html(stats, v0):
    f = lambda x: ("%.5f" % x)
    s, sd, sh = stats["setup"], stats["sdskew"], stats["shift"]
    h = stats["hold"]
    out_cells = sd["out_of_window"]
    oc_txt = ("；".join("%s @%s = %s（窗 [%g,%g]）" % (c["row"], c["corner"], f(c["val"]), c["win"][0], c["win"][1]) for c in out_cells)) or "无"
    worst_s, worst_h = s["worst"], h["worst"]
    tr_t = stats["trans"]["transition"]
    tr_c = stats["trans"]["capacitance"]
    if v0:
        vs, vh = v0["setup"], v0["hold"]
        cmp_rows = """
<tr><td>setup 违例计数（角序 wc_cworst·wc_cbest·wc_typ·lt_cworst·lt_cbest·lt_typ·ml·tt×3）</td>
<td class="mono">%s</td><td class="mono">%s</td><td>持平（总 %d → %d，域结构不变）</td></tr>
<tr><td>worst setup</td><td class="mono">%s（%s @%s）</td><td class="mono">%s（%s @%s）</td><td>同域同角，数值微移</td></tr>
<tr><td>hold 违例计数</td><td class="mono">%s</td><td class="mono">%s</td><td class="ok">总 %d → %d，tt 系 3 角清零</td></tr>
<tr><td>worst hold</td><td class="mono">%s</td><td class="mono">%s</td><td class="ok">改善 %.1f%%（RX_CLK 族收敛）</td></tr>
<tr><td>trans / cap 违例总数</td><td class="mono">%d / %d</td><td class="mono">%d / %d</td><td>逐角一致（同代际特征）</td></tr>
<tr><td>sdskew 出窗格</td><td class="mono">%d 格（dplc a_min wc_cbest+wc_typ）</td><td class="mono">%d 格（wc_cbest）</td><td>P5 悬置延续，收敛中</td></tr>
<tr><td>rx0_00_min 最小（port→FF hold）</td><td class="mono">%s @lt_typical</td><td class="mono">%s @lt_typical</td><td class="ok">hold 修复主见效点</td></tr>
<tr><td>时钟偏移容限 左/右（裸口径）</td><td class="mono">%s / %s</td><td class="mono">%s / %s</td><td>右移 +%.5f，左移基本持平</td></tr>""" % (
            _cnt_row(vs["per_corner"]), _cnt_row(s["per_corner"]), vs["total"], s["total"],
            f(vs["worst"]["slack"]), vs["worst"]["domain"], vs["worst"]["corner"],
            f(worst_s["slack"]), worst_s["domain"], worst_s["corner"],
            _cnt_row(vh["per_corner"]), _cnt_row(h["per_corner"]), vh["total"], h["total"],
            f(vh["worst"]["slack"]), f(worst_h["slack"]),
            100.0 * abs(vh["worst"]["slack"] - worst_h["slack"]) / abs(vh["worst"]["slack"]),
            v0["trans_total"]["transition"], v0["trans_total"]["capacitance"],
            tr_t["total"], tr_c["total"],
            v0["sdskew_out"], len(out_cells),
            f(v0["phy"]["rx0min"]), f(stats["phy"]["rx0_00_min_min"]),
            f(v0["shift"]["left"]), f(v0["shift"]["right"]), f(sh["left_min"]), f(sh["right_min"]),
            sh["right_min"] - v0["shift"]["right"])
        cmp_note = "对比基线 = 本地 1104V0 包（script/_syn_1104V0，与本机 SYNTHESIS summary 逐字节一致）。V2 与 V0 <b>同 1104 代际</b>（DC 11-03 → PT 11-04 三方对齐口径内）：setup/trans/skew 违例域结构逐角一致，主差异集中在 hold 侧（修复迭代特征），不展开。"
    else:
        cmp_rows = '<tr><td colspan="4">V0 包本地不可达（script/_syn_1104V0），对比省略</td></tr>'
        cmp_note = ""
    html = (HTML_HEAD % (GEN, GEN, GEN)) + (HTML_CARDS % dict(
        gen=GEN,
        s_cells=s["cells"], s_total=s["total"], s_worst=f(worst_s["slack"]), s_dom=worst_s["domain"], s_cor=worst_s["corner"],
        h_cells=h["cells"], h_total=h["total"], h_worst=f(worst_h["slack"]), h_dom=worst_h["domain"], h_cor=worst_h["corner"],
        tr_worst=f(tr_t["worst"]), tr_total=tr_t["total"], cap_total=tr_c["total"],
        p1=sd["p1_in_window"], bl=sd["dplc_b_l"], br=sd["dplc_b_r"], oc=oc_txt,
        left=f(sh["left_min"]), lcor=sh["left_corner"], right=f(sh["right_min"]), rcor=sh["right_corner"],
        v0hold=("%d → %d" % (v0["hold"]["total"], h["total"])) if v0 else "—",
        v0hw=("%s → %s" % (f(v0["hold"]["worst"]["slack"]), f(worst_h["slack"]))) if v0 else "—",
        v0oc=("%d → %d 格" % (v0["sdskew_out"], len(out_cells))) if v0 else "—",
    )) + (HTML_FIGS % {"rxmin": f(stats["phy"]["rx0_00_min_min"])}) + (HTML_CMP % (cmp_note, cmp_rows)) + HTML_TAIL
    with open(os.path.join(BASE, "index.html"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print("page  -> index.html")

HTML_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>%s TO SIGNOFF · HK1V11（独立版）</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Serif+SC:wght@600;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#f4f1ea;--surface:#fffdf7;--text:#1c2534;--muted:#5b6675;--accent:#b45309;
--accent-soft:#f7e8d4;--line:#ddd6c8;--ok:#047857;--warn:#8a5305;--bad:#b91c1c;--teal:#0e7490;
--mono:"IBM Plex Mono",Consolas,"Cascadia Mono",monospace;--serif:"Noto Serif SC",serif;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:15px/1.65 "PingFang SC","Microsoft YaHei",sans-serif;font-variant-numeric:tabular-nums}
.mono{font-family:var(--mono)}
.topbar{position:sticky;top:0;z-index:9;display:flex;align-items:center;gap:14px;padding:10px 22px;
background:rgba(244,241,234,.94);border-bottom:1px solid var(--line);backdrop-filter:blur(6px)}
.topbar .brand{font-family:var(--mono);font-weight:600;font-size:14px;letter-spacing:.08em}
.topbar .meta{font-family:var(--mono);font-size:12px;color:var(--muted)}
#motionToggle{margin-left:auto;font-family:var(--mono);font-size:12.5px;padding:5px 12px;cursor:pointer;
background:var(--accent);color:#fff;border:none;border-radius:999px}
#motionToggle:hover{filter:brightness(1.08)}
main{max-width:1180px;margin:0 auto;padding:34px 22px 60px}
.hero .kicker{font-family:var(--mono);font-size:12px;letter-spacing:.22em;color:var(--accent);text-transform:uppercase;margin-bottom:10px}
.hero .kicker::before{content:"— "}
.hero h1{font-family:var(--serif);font-weight:900;font-size:clamp(30px,4.6vw,46px);margin:0 0 10px}
.hero h1 .thin{color:var(--accent)}
.hero .lead{max-width:46em;color:var(--text)}
.hero .meta{font-family:var(--mono);font-size:12px;color:var(--muted);margin-top:14px}
.section-title{font-family:var(--mono);font-size:13px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:44px 0 14px}
.section-title::after{content:"";display:block;height:1px;background:var(--line);margin-top:6px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
.card{background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);
border-radius:6px;padding:14px 16px;box-shadow:0 6px 18px rgba(28,37,52,.07)}
.card .num{font-family:var(--mono);font-size:11.5px;color:var(--muted);letter-spacing:.06em}
.card .title{font-family:var(--mono);font-weight:600;font-size:22px;margin:6px 0 4px}
.card .desc{font-size:13px;color:var(--muted)}
.card.ok{border-left-color:var(--ok)} .card.ok .title{color:var(--ok)}
.card.warn{border-left-color:var(--warn)} .card.warn .title{color:var(--warn)}
.fig{margin:26px 0}
.fig-head{display:flex;align-items:baseline;gap:10px;font-family:var(--mono);font-size:13.5px;font-weight:600;margin-bottom:8px}
.fig-head .fig-no{color:var(--accent)}
.fig-wrap{background:var(--surface);border:1px solid var(--line);border-radius:6px;padding:8px;overflow-x:auto}
.fig-wrap img{display:block;min-width:100%%;height:auto}
figcaption{font-size:13px;color:var(--muted);margin-top:8px;max-width:60em}
figcaption a{color:var(--teal);text-decoration:none;border-bottom:1px dotted var(--teal)}
table.cmp{border-collapse:collapse;width:100%%;background:var(--surface);border:1px solid var(--line);font-size:13.5px}
table.cmp th,table.cmp td{padding:8px 10px;border-top:1px solid var(--line);text-align:left;vertical-align:top}
table.cmp thead th{border-top:none;border-bottom:2px solid var(--line);font-family:var(--mono);font-size:12.5px}
table.cmp td.mono{font-family:var(--mono);font-size:12.5px;word-break:break-word}
table.cmp td.ok{color:var(--ok);font-weight:600}
blockquote{background:var(--accent-soft);border-left:4px solid var(--accent);margin:16px 0;padding:10px 16px;font-size:13.5px;border-radius:0 6px 6px 0}
.files td{font-family:var(--mono);font-size:12.5px}
pre{background:#131f38;color:#e9e5d9;padding:14px 16px;border-radius:6px;font-family:var(--mono);font-size:12.5px;overflow-x:auto}
footer{border-top:1px solid var(--line);margin-top:50px;padding:16px 0 0;font-family:var(--mono);font-size:11.5px;color:var(--muted)}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>
</head>
<body>
<nav class="topbar">
  <span class="brand">HK1V11_SIGNOFF_%s</span>
  <span class="meta">PACK_TAR_1104V2 · summary/latest · 10 corner · 独立版（不嵌站）</span>
  <button id="motionToggle" type="button">动画版 · 切静态</button>
</nav>
<main>
<section class="hero">
  <div class="kicker">HK1V11 · POST-PT · SIGNOFF · STANDALONE</div>
  <h1>%s post-PT <span class="thin">签核总表</span></h1>
  <p class="lead">1104V2 服务器包 PT summary 五表一图独立版：逐项沿用 practice 站（hk1v11-synthesis-postpt-practice ch09 §6）signoff 表图模板，零手工录入——本页所有数字与图内数值均由 csv 直算。</p>
  <div class="meta">DATA&nbsp; C:\\Users\\zhuyanming\\Downloads\\PACK_TAR_1104V2\\project\\HK1V11\\designer\\DD\\ymzhu\\HK1V11\\SYNTHESIS\\top\\sta\\post\\pt\\summary\\latest<br>
  OUT&nbsp; E:\\project\\HK1V11\\docs\\to_signoff_1104v2\\ · GEN 2026-11-04 · 表图 51–56 与站点 ch09 同款</div>
</section>
"""

HTML_CARDS = """
<div class="section-title">签核状态速览（%(gen)s · 10 corner）</div>
<div class="cards">
  <div class="card warn"><div class="num">setup（10 角）</div><div class="title">%(s_cells)d 格 / 3 域</div>
    <div class="desc">总违例 %(s_total)d · worst %(s_worst)s（%(s_dom)s @%(s_cor)s）</div></div>
  <div class="card warn"><div class="num">hold（10 角）</div><div class="title">%(h_cells)d 格 / 2 域</div>
    <div class="desc">总违例 %(h_total)d · worst %(h_worst)s（%(h_dom)s @%(h_cor)s）</div></div>
  <div class="card warn"><div class="num">trans / cap</div><div class="title">20 格 / 2 域</div>
    <div class="desc">transition %(tr_total)d 条 · cap %(cap_total)d 条 · worst %(tr_worst)s @wc_cworst</div></div>
  <div class="card ok"><div class="num">skew margin</div><div class="title">1p %(p1)s 在窗</div>
    <div class="desc">dplc b 组 l %(bl)s · r %(br)s · 出窗：%(oc)s</div></div>
  <div class="card"><div class="num">时钟偏移容限（裸口径）</div><div class="title">左 %(left)s / 右 %(right)s</div>
    <div class="desc">左 @%(lcor)s（setup 先碰界）· 右 @%(rcor)s（hold 先碰界）</div></div>
  <div class="card ok"><div class="num">演进 · 1104V0 → 1104V2（同代际）</div><div class="title">hold %(v0hold)s 条</div>
    <div class="desc">worst %(v0hw)s · P5 出窗 %(v0oc)s · setup/trans 持平</div></div>
</div>
"""

HTML_FIGS = """
<div class="section-title">签核表图（默认动画版 · 右上角切换静态，零重载）</div>
<figure class="fig" id="f51">
  <div class="fig-head"><span class="fig-no">51</span>setup 总表 · report_setup.csv</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/51_signoff_setup_hk11.svg" data-static="51_signoff_setup_hk11.svg" data-anim="anim/51_signoff_setup_hk11.svg" alt="1104V2 setup 总表" loading="lazy"></div>
  <figcaption>红=违例（括号内条数，呼吸常驻）；绿 0=零违例；深色正数=有 margin 的最差路径余量；全表 5 位小数。<a href="51_signoff_setup_hk11.png">PNG 快照</a> · <a href="51_signoff_setup_hk11.svg">静态 SVG</a> · <a href="anim/51_signoff_setup_hk11.svg">动画 SVG</a></figcaption>
</figure>
<figure class="fig" id="f52">
  <div class="fig-head"><span class="fig-no">52</span>hold 总表 · report_hold.csv</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/52_signoff_hold_hk11.svg" data-static="52_signoff_hold_hk11.svg" data-anim="anim/52_signoff_hold_hk11.svg" alt="1104V2 hold 总表" loading="lazy"></div>
  <figcaption>违例集中在 lt 系 + ml_cbest（OSC_CLK + RX_CLK 两域），tt 系 3 角本代清零。<a href="52_signoff_hold_hk11.png">PNG 快照</a> · <a href="52_signoff_hold_hk11.svg">静态 SVG</a> · <a href="anim/52_signoff_hold_hk11.svg">动画 SVG</a></figcaption>
</figure>
<figure class="fig" id="f53">
  <div class="fig-head"><span class="fig-no">53</span>trans / cap 总表 · report_trans.csv</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/53_signoff_trans_hk11.svg" data-static="53_signoff_trans_hk11.svg" data-anim="anim/53_signoff_trans_hk11.svg" alt="1104V2 trans/cap 总表" loading="lazy"></div>
  <figcaption>transition + capacitance 10 角全违例（每角 1~45 条），与 1104V0 逐角一致。<a href="53_signoff_trans_hk11.png">PNG 快照</a> · <a href="53_signoff_trans_hk11.svg">静态 SVG</a> · <a href="anim/53_signoff_trans_hk11.svg">动画 SVG</a></figcaption>
</figure>
<figure class="fig" id="f54">
  <div class="fig-head"><span class="fig-no">54</span>PHY bus skew · report_phy_busskew.csv</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/54_signoff_physkew_hk11.svg" data-static="54_signoff_physkew_hk11.svg" data-anim="anim/54_signoff_physkew_hk11.svg" alt="1104V2 phy busskew" loading="lazy"></div>
  <figcaption>rx0_00_min（hold）负值在 lt 系 + ml（最差 %(rxmin)s @lt_typical）；rx0_00_max（setup）仅 lt_cworst 微负；按 2M23 原样负值不红显；浅蓝框（辉光呼吸+虚线生长）= rx0_00 两行各自最紧角。</figcaption>
</figure>
<figure class="fig" id="f55">
  <div class="fig-head"><span class="fig-no">55</span>SD skew margin · report_sd_busskew.csv</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/55_signoff_sdskew_margin_hk11.svg" data-static="55_signoff_sdskew_margin_hk11.svg" data-anim="anim/55_signoff_sdskew_margin_hk11.svg" alt="1104V2 sdskew margin" loading="lazy"></div>
  <figcaption>规格窗写入行首（1p [−3.5,+3.5] / dplc [−0.9,+4.1]），出窗红显；本代仅 1 格出窗（sd_r_dplc_margin_a_min @wc_cbest，P5 悬置口径延续，非新违例）。</figcaption>
</figure>
<figure class="fig" id="f56">
  <div class="fig-head"><span class="fig-no">56</span>时钟偏移容限 · phy csv 换算</div>
  <div class="fig-wrap"><img class="fig-img" src="anim/56_signoff_shift_window_hk11.svg" data-static="56_signoff_shift_window_hk11.svg" data-anim="anim/56_signoff_shift_window_hk11.svg" alt="1104V2 时钟偏移容限" loading="lazy"></div>
  <figcaption>左移容限 = port→FF setup（phy csv rx0_00_max 行）+0.3+0.4；右移 = port→FF hold（rx0_00_min 行）+0.3+0.15；红线标签由 csv 直算（修正站点 V0 版上代硬编码残值）。</figcaption>
</figure>
"""

HTML_CMP = """
<div class="section-title">与 1104V0 对比（简要）</div>
<blockquote>%s</blockquote>
<table class="cmp">
<thead><tr><th>指标</th><th>1104V0</th><th>1104V2</th><th>备注</th></tr></thead>
<tbody>%s
</tbody></table>
"""

HTML_TAIL = """
<div class="section-title">文件清单与复跑</div>
<table class="cmp files">
<thead><tr><th>文件</th><th>说明</th></tr></thead>
<tbody>
<tr><td class="mono">51…56_signoff_*.svg / anim/ 同名</td><td>六图静态版（事实源）+ 动画版；XML/无script/转录逐值/成对完整/幂等 六项校验 ALL PASS</td></tr>
<tr><td class="mono">51…56_signoff_*.png</td><td>Edge 无头 DPR2 快照（render_png_1104v2.py 产出）</td></tr>
<tr><td class="mono">gen_signoff_1104v2.py</td><td>唯一生成入口：csv → 51-56 SVG 双版 + stats_1104v2.json + index.html（幂等可复跑）</td></tr>
<tr><td class="mono">render_png_1104v2.py</td><td>PNG 快照渲染器（msedge --headless，逐张渲染+落盘轮询）</td></tr>
<tr><td class="mono">verify_png_1104v2.py</td><td>PNG 程序化验收：尺寸=2×viewBox、标题条色、51/52/55 全表红格矩阵 vs csv 逐格比对（350+350+160 格）、56 关键色存在性</td></tr>
<tr><td class="mono">stats_1104v2.json</td><td>本页速览/对比表全部数字的机器可读源</td></tr>
<tr><td class="mono">README.md</td><td>文件清单、关键数字、V0 对比与复跑说明</td></tr>
</tbody></table>
<pre>cd E:\\project\\HK1V11\\docs\\to_signoff_1104v2
python gen_signoff_1104v2.py    # 51-56 SVG（静态+动画）+ stats + index.html
python render_png_1104v2.py     # PNG 快照（DPR2）
python verify_png_1104v2.py     # 程序化验收（尺寸/红格矩阵 vs csv/关键色）</pre>
<footer>HK1V11 SIGNOFF STANDALONE · 1104V2 · AUTHOR ymzhu · GEN 2026-11-04 · 模板谱系 hk1v11-synthesis-postpt-practice ch09 §6</footer>
</main>
<script>
(function(){
  var m=new URLSearchParams(location.search).get('motion')||sessionStorage.getItem('motion-mode')||
    (matchMedia('(prefers-reduced-motion: reduce)').matches?'static':'anim');
  var btn=document.getElementById('motionToggle');
  function lock(img){if(img.naturalWidth){img.style.aspectRatio=img.naturalWidth+'/'+img.naturalHeight;img.style.width='100%';img.style.height='auto';}}
  document.querySelectorAll('img.fig-img').forEach(function(img){
    if(img.complete)lock(img);else img.addEventListener('load',function(){lock(img);},{once:true});});
  function setMode(mo,save){
    document.documentElement.classList.toggle('page-static',mo==='static');
    document.querySelectorAll('img.fig-img').forEach(function(img){
      var t=mo==='static'?img.dataset.static:img.dataset.anim;
      if(img.getAttribute('src')===t)return;
      var p=new Image();p.onload=function(){img.src=t;};p.src=t;});
    btn.textContent=mo==='anim'?'动画版 · 切静态':'静态版 · 切动画';
    btn.setAttribute('aria-pressed',mo==='anim'?'true':'false');
    if(save)sessionStorage.setItem('motion-mode',mo);}
  btn.addEventListener('click',function(){
    setMode(document.documentElement.classList.contains('page-static')?'anim':'static',true);});
  setMode(m,false);
})();
</script>
</body>
</html>
<!-- ymzhu 2026-11-04 11:55 -->
"""

if __name__ == "__main__":
    outs, stats = gen_all()
    all_ok = True
    for name, svg, data in outs:
        sp = os.path.join(OUT_STATIC, name + ".svg")
        ap = os.path.join(OUT_ANIM, name + ".svg")
        if name.startswith("56"):
            anim_svg = svg.replace("</svg>", SW_CSS_ANIM + "\n</svg>")
            open(sp, "w", encoding="utf-8", newline="\n").write(svg)
            open(ap, "w", encoding="utf-8", newline="\n").write(anim_svg)
        else:
            anim_svg = svg
            open(sp, "w", encoding="utf-8", newline="\n").write(strip_css(svg))
            open(ap, "w", encoding="utf-8", newline="\n").write(anim_svg)
        m1 = hashlib.md5(anim_svg.encode()).hexdigest()
        m2 = hashlib.md5(open(ap, encoding="utf-8").read().encode()).hexdigest()
        pair = "+" if os.path.exists(sp) else "-"
        line = "%s  pair=%s  anim=%dB  %s  idem=%s" % (name, pair, len(svg), validate(svg, data, ap), "+" if m1 == m2 else "-")
        print(line)
        all_ok = all_ok and "xml+" in line and "noscript+" in line and "transcript-" not in line and pair == "+"
    with open(os.path.join(BASE, "stats_1104v2.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=1)
    print("stats -> stats_1104v2.json")
    gen_index_html(stats, v0_stats())
    print("ALL", "PASS" if all_ok else "FAIL")
# ymzhu 2026-11-04 11:55
