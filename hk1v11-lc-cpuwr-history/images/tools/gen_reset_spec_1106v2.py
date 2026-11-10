#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reset_spec_1106v2.py — 复位规格图（20261106 / 1106v2 落地，静态事实源 + 动画版，blueprint-ui-style v4）
# 2026-11-09 重写：估宽折行 + 行高自适应 + badge 独立列 + 生成器内置重叠自检（修复 11-06 版底注溢出画布/列互叠）
# 2026-11-10 1106v4：PORSD 维度改动列「零改动」→「1106v4 写门控修复」+ 关键内容补一句 + 标题/副标题更新
# 数据源：LC_CPUWR_history/CHANGES.md 1106v2 (5) + 1106v4（PORSD 写门控修复，NO59）+ script/_ds_audit_1106/summary.md（三路 DS 盲审）
# 出：images/reset_spec_1106v2.svg（静态） + images/anim/reset_spec_1106v2.svg（动画）
import io, os, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "reset_spec_1106v2.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "reset_spec_1106v2.svg")

BG, INK, MUTED = "#ffffff", "#1e293b", "#64748b"
LINE, HEAD_BG  = "#e2e8f0", "#f1f5f9"
ROW_A, ROW_B   = "#ffffff", "#f8fafc"
STATE_COLOR = {
    "迁移": ("#b45309", "#f7e8d4"), "已符合": ("#0d9488", "#ccfbf1"),
    "零改动": ("#16a34a", "#dcfce7"), "一致": ("#1d4ed8", "#dbeafe"),
    "链路": ("#7c3aed", "#ede9fe"),
}

W = 1100
CX0, C1, C2, C3, C4, C5 = 40, 70, 300, 792, 872, W - 40  # badge 独立列 792-872；改动 872-1060

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

# 数据行（# | 维度 | 关键内容[行列表] | RTL 状态 badge | 改动）
ROWS = [
    ("1", "unlock reset 例外清单", ["13 组 CTRL_F 信号全 RSTN 域", "AVE_RGBW / AVE_LAST / DPLC_GROUP / DPOLINV / AVE_MODE / CTRLF_CHECKSUM + 其余 7 组"], "迁移", "6 组 t9 迁 RSTN"),
    ("2", "I2C_EN=1 全免 unlock reset", ["I2C_EN_CTL → TEST_EN → I_TEST_REG_EN → RSTNGEN:50", "I2C_EN=1 时寄存器不进入 unlock reset 语义"], "链路", "零改动（链路已存在）"),
    ("3", "PORSD 不受 password & checksum 保护", ["PORSD = RSTN 域 + 不在 LSI（password）集", "1106v4：直写绕 chksum 门控 + update_en_a 回填移除", "checksum 排除属 BCC 主端软件口径（非 RTL）"], "已符合", "1106v4 写门控修复"),
    ("4", "password error reset 例外地址段", ["受门控段 32-38 / 40-47 / 51 / 53-57 / 144-147（dec）", "0x40~0x44 整块（dec 64~68）不做 password error reset"], "一致", "零改动（=表 AC 列）"),
]

HEAD_Y = 100
LH, PAD = 17.5, 16
# 预折行（fs, maxw）：维度 12.5/206、关键内容 12/456、改动 12/172
WL = [(r[0], wrap(r[1], 12.5, 206), [ln for part in r[2] for ln in wrap(part, 12, 456)], r[3], wrap(r[4], 12, 172)) for r in ROWS]
GEOM = []
y = HEAD_Y + 34
for r in WL:
    n = max(len(r[1]), len(r[2]), len(r[4]))
    h = max(74, n * LH + 2 * PAD)
    GEOM.append((y, int(h))); y += int(h)
FY, H = y + 26, y + 26 + 58

def build_static():
    a = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG),
         '<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">复位规格 · 20261106（1106v2→v4 终版）</text>' % INK,
         '<text x="550.0" y="70" text-anchor="middle" font-size="12.5" fill="%s">%s</text>' % (MUTED, esc('复位规格四条已落地（含 1106v4 PORSD 写门控修复） · 三路 DS 盲审四维度全过 · 两项裁定关闭 · 2026-11-10')),
         '<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG)]
    headers = [("#", (CX0 + C1) / 2), ("复位规格维度", (C1 + C2) / 2), ("关键内容（位段 / 地址 / 链路）", (C2 + C3) / 2),
               ("RTL 状态", (C3 + C4) / 2), ("改动", (C4 + C5) / 2)]
    for txt, x in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="13.5" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, INK, esc(txt)))
    for i, (no, dim, content, badge, change) in enumerate(WL):
        y0, rh = GEOM[i]; cy = y0 + rh / 2
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, rh, ROW_A if i % 2 == 0 else ROW_B, LINE))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="14" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, cy + 5, MUTED, esc(no)))
        ty0 = cy - (len(dim) - 1) * LH / 2 + 4.5
        for k, ln in enumerate(dim):
            a.append('<text x="%d" y="%.1f" font-size="12.5" font-weight="600" fill="%s">%s</text>' % (C1 + 12, ty0 + k * LH, INK, esc(ln)))
        ty0 = cy - (len(content) - 1) * LH / 2 + 4
        for k, ln in enumerate(content):
            a.append('<text x="%d" y="%.1f" font-size="12" fill="%s">%s</text>' % (C2 + 12, ty0 + k * LH, INK, esc(ln)))
        fg, bgc = STATE_COLOR[badge]
        bx = (C3 + C4) / 2
        bw = max(50, text_w(badge, 11.5) + 22)
        a.append('<rect x="%.1f" y="%.1f" width="%.0f" height="23" rx="11.5" fill="%s" stroke="%s" stroke-width="1"/>' % (bx - bw / 2, cy - 11.5, bw, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="11.5" font-weight="700" fill="%s">%s</text>' % (bx, cy + 4, fg, esc(badge)))
        ty0 = cy - (len(change) - 1) * LH / 2 + 4.5
        for k, ln in enumerate(change):
            a.append('<text x="%d" y="%.1f" font-size="12" font-weight="600" fill="%s">%s</text>' % (C4 + 14, ty0 + k * LH, INK, esc(ln)))
    for k, ln in enumerate(wrap('unlock reset 13 组明细（位段）：0x00[7:5] / 0x01[7] / 0x05[7:5] / 0x06[7,5,3,2,1] / 0x07[3:0] / 0x20[5:0] / 0x21[5:4] / 0x30[7:0] / I2C 0xF0·0xF1 · 0xA0~0xA1 只读不参与 password error reset', 12, 1020)):
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
    svg = svg.replace('<rect x="40" y="100" width="%d" height="34" fill="#f1f5f9"/>' % (C5 - CX0), '<rect class="head" x="40" y="100" width="%d" height="34" fill="#f1f5f9"/>' % (C5 - CX0), 1)
    for i, (ry, rh) in enumerate(GEOM):
        pattern = '<rect x="40" y="%d" width="%d" height="%d" fill=' % (ry, C5 - CX0, rh)
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
# ymzhu 2026-11-10 11:28
