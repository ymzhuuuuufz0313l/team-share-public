#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_table_1111v1.py — 20261111 表变更图（1111v1，静态事实源 + 动画版，blueprint-ui-style v4）
# 2026-11-09 重写：估宽折行 + 行高自适应 + badge 独立末列 + 生成器内置重叠自检（修复 11-06 版文字溢出画布/压胶囊）
# 数据源：HK1V11_Register_20261111.xlsm（T1 提取 excel_20261111_extract.json → images/data/reg_table_1111v1.json）
# 出：images/reg_table_1111v1.svg（静态） + images/anim/reg_table_1111v1.svg（动画）
import io, os, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf, archive_snapshot, table_anim  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = out_path("images/reg_table_1111v1.svg")
OUT_ANIM   = out_path("images/anim/reg_table_1111v1.svg")

BG, INK, MUTED = "#ffffff", "#1e293b", "#64748b"
LINE, HEAD_BG  = "#e2e8f0", "#f1f5f9"
ROW_A, ROW_B   = "#ffffff", "#f8fafc"
STATE_COLOR = {
    "新增": ("#0d9488", "#ccfbf1"), "描述": ("#b45309", "#f7e8d4"), "更名": ("#7c3aed", "#ede9fe"),
}

W = 1100
CX0, C1, C2, C3, C4, C5, C6 = 40, 70, 210, 495, 780, 1002, W - 40  # badge 独立末列 1002-1060

BREAK_CHARS = " /·，、；;,_-）)】》"

def _load_rows(fig):
    """读取 images/data/<fig>.json 的行数据（A0：表格数据单一事实源）。"""
    import json as _json
    p = Path(__file__).resolve().parents[1] / "data" / (fig + ".json")
    with io.open(p, encoding="utf-8") as f:
        d = _json.load(f)
    return [tuple(r) for r in d["rows"]]

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

ROWS = _load_rows("reg_table_1111v1")   # 数据源 = images/data/reg_table_1111v1.json（唯一事实源，勿在此改数）

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
         '<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">20261111 表 · VSYNC_SEL 新增 + 描述更新（1111v1）</text>' % INK,
         '<text x="550.0" y="70" text-anchor="middle" font-size="12.5" fill="%s">%s</text>' % (MUTED, esc('较 20261106 表：D1 新增 VSYNC_SEL@0x06[0]（双版字节映射图已重生成）+ D3 CRC 开关语义 + D4 khead 限定 + D5 SMART_CS 拆名 · 11/6 批量变更 1106v2 代已覆盖')),
         '<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C6 - CX0, HEAD_BG)]
    headers = [("#", (CX0 + C1) / 2), ("字段 / 项", (C1 + C2) / 2), ("旧（1111 表前）", (C2 + C3) / 2),
               ("新（20261111 表）", (C3 + C4) / 2), ("落位 / 状态", (C4 + C5) / 2), ("类", (C5 + C6) / 2)]
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
    for k, ln in enumerate(wrap('PORSD 复位域以 RTL 1118v1（RSTN，不受 NLOCK reset 控制）为准，excel 11/6 豁免表漏列属表缺陷、站点按 RTL 终态呈现 · 11/11 D1 图已重生成 chip_sel0/1 双版字节映射（VSYNC_SEL@0x06[0]）', 12, 1020)):
        a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12" fill="%s">%s</text>' % (FY + k * 17, MUTED, esc(ln)))
    a.append('</svg>')
    return "\n".join(a)

static = build_static()
archive_snapshot("images/reg_table_1111v1.svg", "auto" + __import__("datetime").date.today().strftime("%Y%m%d"))
write_text_lf(OUT_STATIC, static)

def build_anim(svg):
    """动画版：Kit v4 全套 CSS + sweepband 扫光 + cellwave 行波（不触碰任何 <text>）。"""
    return table_anim(svg)

anim = build_anim(static)
archive_snapshot("images/anim/reg_table_1111v1.svg", "auto" + __import__("datetime").date.today().strftime("%Y%m%d"))
write_text_lf(OUT_ANIM, anim)

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
# ymzhu 2026-11-17 19:33
# ymzhu 2026-11-18 16:15
