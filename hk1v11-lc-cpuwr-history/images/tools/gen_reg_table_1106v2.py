#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_table_1106v2.py — 20261106 表字段迁址图（1106v2，静态事实源 + 动画版，blueprint-ui-style v4）
# 2026-11-09 重写：估宽折行 + 行高自适应 + badge 独立末列 + 生成器内置重叠自检（修复 11-06 版文字溢出画布/压胶囊）
# 数据源：LC_CPUWR_history/CHANGES.md 1106v2 + script/_regen_1106/{t9_impl,t12}.md
# 出：images/reg_table_1106v2.svg（静态） + images/anim/reg_table_1106v2.svg（动画）
import io, os, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "reg_table_1106v2.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "reg_table_1106v2.svg")

BG, INK, MUTED = "#ffffff", "#1e293b", "#64748b"
LINE, HEAD_BG  = "#e2e8f0", "#f1f5f9"
ROW_A, ROW_B   = "#ffffff", "#f8fafc"
STATE_COLOR = {
    "迁址": ("#1d4ed8", "#dbeafe"), "门控": ("#b45309", "#f7e8d4"),
    "复位": ("#0d9488", "#ccfbf1"), "env":  ("#7c3aed", "#ede9fe"),
}

W = 1100
CX0, C1, C2, C3, C4, C5, C6 = 40, 70, 210, 495, 780, 1002, W - 40  # badge 独立末列 1002-1060

BREAK_CHARS = " /·，、；;,_-）)】》"
def _cw(ch, fs):
    if unicodedata.east_asian_width(ch) in 'WF': return fs
    if ch in '✅❌⚠→✓✗': return fs
    return fs * 0.58
def text_w(s, fs): return sum(_cw(c, fs) for c in s)
def wrap(s, fs, maxw):
    lines, cur = [], ''
    for ch in s:
        if text_w(cur + ch, fs) > maxw and cur:
            cut = -1
            for j in range(len(cur) - 1, max(0, int(len(cur) * 0.4)) - 1, -1):
                if cur[j] in BREAK_CHARS: cut = j; break
            if cut < 0: cut = len(cur) - 1
            lines.append(cur[:cut + 1].rstrip())
            rest = cur[cut + 1:].lstrip()
            cur = (rest + ch).lstrip()
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines or ['']

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

ROWS = [
    ("1", "VPS_EN_0", "R_REG40_F[6]（0x28[6]，LSI 门控）", "R_REG29_F[0]（0x1D[0]，去 LSI 门控）", "LC_CPUWR；0x28[6] 回 Reserved", "迁址"),
    ("2", "SP_S[2:0]", "R_REG29_F[2:0]（0x1D[2:0]）", "R_REG29_F[3:1]（0x1D[3:1]）", "LC_REG_MAPPING", "迁址"),
    ("3", "reg_eq_rbc0/1", "R_REG08_F[1:0]（0x08[1:0]，ungated）", "R_REG35_F[1:0]（0x23[1:0]，带出 LSI 门控）", "输出口迁 LC_CPUWR（>31 规则）", "门控"),
    ("4", "reg_eol", "R_REG56_F[6]（0x38[6]）", "R_REG57_F[6]（0x39[6]，LSI 保留）", "LC_CPUWR", "迁址"),
    ("5", "unlock reset 6 组", "N_RST_NLOCK 域", "RSTN 域（13 组全 RSTN）", "AVE_RGBW/AVE_LAST/DPLC_GROUP/DPOLINV/AVE_MODE/CTRLF_CHECKSUM", "复位"),
    ("6", "env 同步", "auto_script 1106 包版 / 运行时 1022 代", "auto_script 补 0x23/0x39 + 运行时追平 + checker 键位同步", "DV_TCON_C/isprx_env（两副本 md5 同）", "env"),
]

HEAD_Y = 100
LH, PAD = 17.5, 16
# 预折行（fs, maxw）：字段 12.5/112、旧 12/257、新 12/257、落位 11.5/168
WL = [(r[0], wrap(r[1], 12.5, 112), wrap(r[2], 12, 257), wrap(r[3], 12, 257), wrap(r[4], 11.5, 168), r[5]) for r in ROWS]
GEOM = []
y = HEAD_Y + 34
for r in WL:
    n = max(len(r[1]), len(r[2]), len(r[3]), len(r[4]))
    h = max(70, n * LH + 2 * PAD)
    GEOM.append((y, int(h))); y += int(h)
FY, H = y + 26, y + 26 + 40

def col_lines(a, x0, lines, fs, color, weight=None, mono=False):
    extra = ' font-weight="%s"' % weight if weight else ''
    fam = ' font-family="Consolas, Monaco, monospace"' if mono else ''
    for k, ln in enumerate(lines):
        a.append('<text x="%d" y="%.1f" font-size="%s" fill="%s"%s%s>%s</text>' % (x0, 0, fs, color, extra, fam, esc(ln)))

def build_static():
    a = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG),
         '<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">20261106 表 · 字段迁址 + 复位维度（1106v2）</text>' % INK,
         '<text x="550.0" y="70" text-anchor="middle" font-size="12.5" fill="%s">%s</text>' % (MUTED, esc('较 20261103 新表四字段迁址 + unlock reset 6 组迁 RSTN + env 三件追平 · 双盲审→交叉验证→裁决修复→RTL 三关')),
         '<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C6 - CX0, HEAD_BG)]
    headers = [("#", (CX0 + C1) / 2), ("字段 / 项", (C1 + C2) / 2), ("旧（1106v1/1104 代）", (C2 + C3) / 2),
               ("新（20261106 表）", (C3 + C4) / 2), ("落位 / 状态", (C4 + C5) / 2), ("类", (C5 + C6) / 2)]
    for txt, x in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="13.5" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, INK, esc(txt)))
    for i, (no, dim, old, new, place, badge) in enumerate(WL):
        y0, rh = GEOM[i]; cy = y0 + rh / 2
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C6 - CX0, rh, ROW_A if i % 2 == 0 else ROW_B, LINE))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="14" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, cy + 5, MUTED, esc(no)))
        for cols in ((C1 + 12, dim, '12.5', INK, '600', False), (C2 + 12, old, '12', INK, None, False),
                     (C3 + 12, new, '12', INK, None, False), (C4 + 12, place, '11.5', MUTED, None, False)):
            x0, lines, fs, color, wt, mono = cols
            ty0 = cy - (len(lines) - 1) * LH / 2 + 4
            for k, ln in enumerate(lines):
                extra = ' font-weight="%s"' % wt if wt else ''
                a.append('<text x="%d" y="%.1f" font-size="%s" fill="%s"%s>%s</text>' % (x0, ty0 + k * LH, fs, color, extra, esc(ln)))
        fg, bgc = STATE_COLOR[badge]
        bx = (C5 + C6) / 2
        bw = max(46, text_w(badge, 11.5) + 22)
        a.append('<rect x="%.1f" y="%.1f" width="%.0f" height="23" rx="11.5" fill="%s" stroke="%s" stroke-width="1"/>' % (bx - bw / 2, cy - 11.5, bw, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11.5" font-weight="700" fill="%s">%s</text>' % (bx, cy + 4, fg, esc(badge)))
    for k, ln in enumerate(wrap('复位规格三条（unlock reset 13 组全 RSTN / I2C_EN=1 全免 / PORSD 不受 password&checksum 保护 / password error reset 例外地址段）详见「复位规格 · 20261106」页', 12, 1020)):
        a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12" fill="%s">%s</text>' % (FY + k * 17, MUTED, esc(ln)))
    a.append('</svg>')
    return "\n".join(a)

static = build_static()
os.makedirs(os.path.dirname(OUT_ANIM), exist_ok=True)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(static)

CSS = """<style>
.title, .head { opacity:0; animation: fadeIn .4s ease forwards; }
.row { opacity:0; animation: rowIn .35s cubic-bezier(.22,.7,.3,1) forwards; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes rowIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:none; } }
@media (prefers-reduced-motion:reduce) { *{animation:none!important} .title,.head,.row{opacity:1!important} }
</style>"""

def build_anim(svg):
    svg = svg.replace('font-size="22" font-weight="bold" fill="#1e293b"', 'class="title" font-size="22" font-weight="bold" fill="#1e293b"', 1)
    svg = svg.replace('<rect x="40" y="100" width="%d" height="34" fill="#f1f5f9"/>' % (C6 - CX0), '<rect class="head" x="40" y="100" width="%d" height="34" fill="#f1f5f9"/>' % (C6 - CX0), 1)
    for i, (ry, rh) in enumerate(GEOM):
        pattern = '<rect x="40" y="%d" width="%d" height="%d" fill=' % (ry, C6 - CX0, rh)
        idx = svg.find(pattern)
        if idx == -1: continue
        svg = svg[:idx + 5] + ' class="row" style="animation-delay:%.2fs"' % (0.15 + i * 0.14) + svg[idx + 5:]
    return svg.replace("</svg>", CSS + "\n</svg>")

anim = build_anim(static)
io.open(OUT_ANIM, "w", encoding="utf-8", newline="\n").write(anim)

ss, sa = ET.fromstring(static), ET.fromstring(anim)
st = Counter(t.text for t in ss.iter() if t.tag.endswith('text') and t.text is not None)
at = Counter(t.text for t in sa.iter() if t.tag.endswith('text') and t.text is not None)
drift = "drift-0" if st == at else "DRIFT"
s_static = "static-clean" if ("@keyframes" not in static and "animation:" not in static) else "static-HAS-anim!"
a_anim = "anim-ok" if ("@keyframes" in anim and "animation:" in anim) else "anim-MISSING!"

def overlap_audit(root):
    boxes = []
    for t in root.iter():
        if not t.tag.endswith('text') or t.text is None: continue
        fs = float(t.get('font-size', 13)); x = float(t.get('x', 0)); yy = float(t.get('y', 0))
        anc = t.get('text-anchor', 'start'); w = text_w(t.text, fs)
        x0 = x - w / 2 if anc == 'middle' else x
        boxes.append((x0, yy - fs * 0.78, x0 + w, yy + fs * 0.22))
    bad = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if min(boxes[i][2], boxes[j][2]) - max(boxes[i][0], boxes[j][0]) > 2 and \
               min(boxes[i][3], boxes[j][3]) - max(boxes[i][1], boxes[j][1]) > 2: bad += 1
        if boxes[i][2] > W - 2 or boxes[i][0] < 2: bad += 1
    return bad

n_ov = overlap_audit(ss)
print("written %s %dB / %s %dB" % (OUT_STATIC, len(static), OUT_ANIM, len(anim)))
print("xml+ %s %s %s overlap=%d" % (s_static, a_anim, drift, n_ov))
assert s_static == "static-clean" and a_anim == "anim-ok" and drift == "drift-0" and n_ov == 0, "validation failed"
print("ALL PASS")
# ymzhu 2026-11-09 10:20
