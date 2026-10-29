#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gen_signoff_tables_hk1v11.py — HK1V11 signoff 表图生成器（1029V0 run, rev2 2026-10-30）

抄袭来源（结构/配色/动画逐项照抄）：
  A 族（setup/hold）← gen_postpt_tables_anim.py（#157a6a/#2e8b6a/#1a7a3c/#2d2d2d, FS 30/26/19/19）
  B 族（trans/physkew/sdskew）← gen_postpt_skew_tables_anim.py（#0e7c6b/#f4f8f7/#1e8449/#212529,
     TITLE_H 60 / HEADER_H 52 / ROW_H 44 / COL_W 192, corner 列序照抄 2M23 字母序）
相对 rev1 的改动（ymzhu 2026-10-30 指示）：
  ① phy 表负值不再红显（回归 2M23 原样：非零一律深色+呼吸）
  ② setup/hold 违例格在数值旁标注违例条数 "(N)"
  ③ 红色加深 #b91c1c -> #7f1d1d
  ④ 全表数值统一 5 位小数显示
红显规则（改后）：setup/hold violN>0、trans<0、sdskew 出窗 -> 深红 #7f1d1d

输出：../images/5{1..5}_signoff_*.svg（静态）+ ../images/anim/ 同名（动画）
校验：XML / 无 script / keyframes / 转录逐值 / 行数 / 幂等
"""
import csv, hashlib, os, re, sys
import xml.etree.ElementTree as ET

SITE = r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice"
DATA = r"E:\project\HK1V11\SYNTHESIS\top\sta\post\pt\summary\latest"
OUT_STATIC = os.path.join(SITE, "images")
OUT_ANIM = os.path.join(SITE, "images", "anim")

RED = "#7f1d1d"   # 深红（rev2 加深）

CORNER_HDR = ["lt_cbest_m40", "lt_cworst_m40", "lt_typical_m40", "ml_cbest_125",
              "tt_cbest_25", "tt_cworst_25", "tt_typical_25", "wc_cbest_125",
              "wc_cworst_125", "wc_typical_125"]

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))

def f5(v):
    return "%.5f" % float(v)

def read_pairs(path):
    """setup/hold/trans：返回 [(label, [10 个显示串], [10 个原始float]])，显示串=5位小数+违例条数(N)"""
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
        out.append((r[0], disp, big))
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
        m = re.match(r"(.+?)\s*:\s*\[([-+\d.]+)\s*:\s*([-+\d.]+)\]", r[0])
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
A_FONT = "Consolas, 'SFMono-Regular', Menlo, 'Courier New', monospace"
A_FS_T, A_FS_S, A_FS_C, A_FS_D = 30, 26, 19, 19

def fmt(x):
    s = "%.2f" % x
    return s.rstrip("0").rstrip(".")

def build_A(metric, data, subtitle):
    n = len(data)
    H = max(A_HMIN, A_HEADER_H + A_COLHEAD_H + n * 54)
    data_left, data_right = A_FIRST_COL_RIGHT, A_W - A_M
    col_w = (data_right - data_left) / 10.0
    row_h = (H - A_HEADER_H - A_COLHEAD_H) / n
    css = ("<style><![CDATA["
           ".head{opacity:0;animation:rowIn 0.4s ease forwards;}"
           ".row{opacity:0;animation:rowIn 0.4s ease forwards;}"
           ".chg{animation:breath 2.8s ease-in-out infinite;}"
           "@keyframes rowIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}"
           "@keyframes breath{0%{opacity:1;}50%{opacity:0.55;}100%{opacity:1;}}"
           "]]></style>")
    p = ['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" font-family="%s">'
         % (A_W, H, A_W, H, esc(A_FONT))]
    p.append(css)
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="#ffffff"/>' % (A_W, H))
    ty = A_HEADER_H * 0.64
    p.append('<g class="head">')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (A_W, A_HEADER_H, A_C_BAND))
    p.append('<text x="%d" y="%s" font-size="%d" font-weight="bold" fill="%s">report_%s.csv (HK1V11 1029V0)</text>'
             % (A_M, fmt(ty), A_FS_T, A_C_WHITE, metric))
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
    for i, (label, disp, raw) in enumerate(data):
        ry = top + i * row_h
        p.append('<g class="row" style="animation-delay:%.3fs">' % ((i + 1) * 0.025))
        p.append('<rect x="0" y="%s" width="%d" height="%s" fill="%s"/>'
                 % (fmt(ry), A_W, fmt(row_h), "#ffffff" if i % 2 == 0 else A_C_ZEBRA))
        p.append('<text x="%d" y="%s" font-size="%d" fill="%s">%s</text>'
                 % (A_M + 10, fmt(ry + row_h * 0.62), A_FS_D, A_C_NONZERO, esc(label)))
        for k in range(10):
            v, fv = disp[k], raw[k]
            x = data_left + (k + 1) * col_w - 14
            if fv < 0:   # 违例（biggest<0 ⟺ violN>0，disp 已带 (N) 条数）
                color, cls = RED, ' class="val chg" style="animation-delay:%.2fs"' % ((i + k) * 0.05)
            elif fv == 0:
                color, cls = A_C_ZERO, ' class="val"'
            else:
                color, cls = A_C_NONZERO, ' class="val chg" style="animation-delay:%.2fs"' % ((i + k) * 0.05)
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
.head { opacity:0; animation: rowIn 0.4s ease forwards; }
.row  { opacity:0; animation: rowIn 0.4s ease forwards; }
@keyframes rowIn { from { opacity:0; transform: translateY(4px); }
                   to   { opacity:1; transform: none; } }
.breath { animation: breathe 2.8s ease-in-out infinite; }
@keyframes breathe { 0%,100% { opacity:1; } 50% { opacity:0.55; } }
.frameBreath { animation: frameB 2.8s ease-in-out infinite; }
@keyframes frameB { 0%,100% { stroke-opacity:1; } 50% { stroke-opacity:0.45; } }
</style>"""

def build_B(title, subtitle, label_w, rows, mode, red_fn, zero_frame=False):
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
        p.append('<g class="row" style="animation-delay:%.3fs">' % ((i + 1) * 0.025))
        p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>'
                 % (ry, W, B_ROW_H, "#ffffff" if i % 2 == 0 else B_ZEBRA))
        p.append('<text class="lab" x="%d" y="%d" font-size="%d" fill="%s">%s</text>'
                 % (B_PAD_L, ry + 28, B_FS_D, B_DARK, esc(label)))
        for k in range(10):
            fv = raw[k]
            if red_fn(fv, label):
                color, cls = RED, 'class="val breath" style="animation-delay:%.2fs"' % ((i + k) * 0.15)
            elif fv == 0:
                color, cls = B_GREEN, 'class="val"'
            else:
                color, cls = B_DARK, 'class="val breath" style="animation-delay:%.2fs"' % ((i + k) * 0.15)
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

# ============================================================ 生成
def gen_all():
    os.makedirs(OUT_ANIM, exist_ok=True)
    outs = []
    for mid, sub in [("setup", "setup/max 路径违例总表（红=违例，括号内为条数）"),
                     ("hold", "hold/min 路径违例总表（红=违例，括号内为条数）")]:
        data = read_pairs(os.path.join(DATA, "report_%s.csv" % mid))
        outs.append(("%s_signoff_%s_hk11" % ({"setup": "51", "hold": "52"}[mid], mid),
                     build_A(mid, data, sub), data))
    data = read_pairs(os.path.join(DATA, "report_trans.csv"))
    rows = [("%s (biggest violation)" % lb, disp, raw) for lb, disp, raw in data]
    svg = build_B("report_trans.csv (HK1V11 1029V0)", "max_trans/cap 约束违例总表",
                  430, rows, "metric", lambda fv, lb: fv < 0,
                  zero_frame=all(fv >= 0 for _, _, raws in data for fv in raws))
    outs.append(("53_signoff_trans_hk11", svg, data))
    data = read_plain(os.path.join(DATA, "report_phy_busskew.csv"))
    rows = [(lb.replace(".rpt", ""), disp, raw) for lb, disp, raw in data]
    # rev2: phy 负值不红显（回归 2M23 原样）
    svg = build_B("report_phy_busskew.csv (HK1V11 1029V0)", "PHY bus skew 各组 slack (ns)",
                  417, rows, "report_files", lambda fv, lb: False)
    outs.append(("54_signoff_physkew_hk11", svg, data))
    sd = read_sdskew(os.path.join(DATA, "report_sd_busskew.csv"))
    win = {lb: (lo, hi) for lb, disp, raw, lo, hi in sd}
    rows = [(lb, disp, raw) for lb, disp, raw, lo, hi in sd]
    def red_by_label(fv, lb):
        lo, hi = win.get(lb, (-1e9, 1e9))
        return not (lo <= fv <= hi)
    svg = build_B("report_sd_busskew.csv (HK1V11 1029V0)",
                  "SD skew margin, 规格 1p [−3.5,+3.5] / dplc [−0.9,+4.1] ns（出窗红显）",
                  340, rows, "report_files", red_by_label)
    outs.append(("55_signoff_sdskew_margin_hk11", svg, sd))
    return outs

def strip_css(svg):
    return re.sub(r"<style>.*?</style>", "", svg, flags=re.S)

def validate(svg, data, path):
    ok = []
    try:
        ET.parse(path); ok.append("xml+")
    except ET.ParseError as e:
        ok.append("xml- %s" % e)
    ok.append("noscript+" if "<script" not in svg.lower() else "noscript-")
    root = ET.parse(path).getroot()
    got = [t.text for t in root.iter() if t.tag.endswith("text") and "val" in (t.get("class") or "")]
    exp = []
    for item in data:
        exp.extend(item[1])
    ok.append("transcript+" if got == exp else "transcript- %d/%d" % (len(got), len(exp)))
    return " ".join(ok)

if __name__ == "__main__":
    for name, svg, data in gen_all():
        sp = os.path.join(OUT_STATIC, name + ".svg")
        ap = os.path.join(OUT_ANIM, name + ".svg")
        open(sp, "w", encoding="utf-8", newline="\n").write(strip_css(svg))
        m1 = hashlib.md5(svg.encode()).hexdigest()
        open(ap, "w", encoding="utf-8", newline="\n").write(svg)
        m2 = hashlib.md5(open(ap, encoding="utf-8").read().encode()).hexdigest()
        print("%s  anim=%dB  %s  idem=%s" % (name, len(svg), validate(svg, data, ap), "+" if m1 == m2 else "-"))
# ymzhu 2026-10-30 19:05
