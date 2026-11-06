#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_table_1106v2.py — 20261106 表字段迁址图（1106v2，静态事实源 + 动画版，blueprint-ui-style v4）
# 数据源：LC_CPUWR_history/CHANGES.md 1106v2 + script/_regen_1106/{t9_impl,t12}.md
# 出：images/reg_table_1106v2.svg（静态） + images/anim/reg_table_1106v2.svg（动画）
import io, os
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "reg_table_1106v2.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "reg_table_1106v2.svg")

BG      = "#ffffff"
INK     = "#1e293b"
MUTED   = "#64748b"
LINE    = "#e2e8f0"
HEAD_BG = "#f1f5f9"
ROW_A   = "#ffffff"
ROW_B   = "#f8fafc"
STATE_COLOR = {
    "迁址":   ("#1d4ed8", "#dbeafe"),   # 蓝（字段迁址）
    "门控":   ("#b45309", "#f7e8d4"),   # 琥珀（门控变化）
    "复位":   ("#0d9488", "#ccfbf1"),   # 青（复位维度）
    "env":    ("#7c3aed", "#ede9fe"),   # 紫（env 同步）
}

W = 1100
CX0 = 40
C1  = 92            # # 列右
C2  = 250           # 字段/项 列右
C3  = 560           # 旧 列右
C4  = 880           # 新 列右
C5  = W - 40        # 落位/状态 列右 (1060)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

ROWS = [
    ("1", "VPS_EN_0", "R_REG40_F[6]（0x28[6]，LSI 门控）", "R_REG29_F[0]（0x1D[0]，去 LSI 门控）", "LC_CPUWR；0x28[6] 回 Reserved", "迁址"),
    ("2", "SP_S[2:0]", "R_REG29_F[2:0]（0x1D[2:0]）", "R_REG29_F[3:1]（0x1D[3:1]）", "LC_REG_MAPPING", "迁址"),
    ("3", "reg_eq_rbc0/1", "R_REG08_F[1:0]（0x08[1:0]，ungated）", "R_REG35_F[1:0]（0x23[1:0]，带出 LSI 门控）", "输出口迁 LC_CPUWR（>31 规则）", "门控"),
    ("4", "reg_eol", "R_REG56_F[6]（0x38[6]）", "R_REG57_F[6]（0x39[6]，LSI 保留）", "LC_CPUWR", "迁址"),
    ("5", "unlock reset 6 组", "N_RST_NLOCK 域", "RSTN 域（13 组全 RSTN）", "AVE_RGBW/AVE_LAST/DPLC_GROUP/DPOLINV/AVE_MODE/CTRLF_CHECKSUM", "复位"),
    ("6", "env 同步", "auto_script 1106 包版 / 运行时 1022 代", "auto_script 补 0x23/0x39 + 运行时追平 + checker 键位同步", "DV_TCON_C/isprx_env（两副本 md5 同）", "env"),
]

HEAD_Y = 100
ROW_H = 92
top = HEAD_Y + 34
FY = top + len(ROWS) * ROW_H + 30
H = FY + 40

def build_static():
    a = []
    a.append('<?xml version="1.0" encoding="UTF-8"?>')
    a.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG))
    a.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    a.append('<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">20261106 表 · 字段迁址 + 复位维度（1106v2）</text>' % INK)
    a.append('<text x="550.0" y="70" text-anchor="middle" font-size="13" fill="%s">较 20261103 新表四字段迁址 + unlock reset 6 组迁 RSTN + env 三件追平 · 双盲审→交叉验证→裁决修复→RTL 三关</text>' % MUTED)
    a.append('<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG))
    headers = [("#", C1, "middle"), ("字段 / 项", (CX0 + C1 + C2) / 2, "middle"), ("旧（1106v1 / 1104 代）", (C2 + C3) / 2, "middle"),
               ("新（20261106 表，1106v2）", (C3 + C4) / 2, "middle"), ("落位 / 状态", (C4 + C5) / 2, "middle")]
    for txt, x, anc in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="%s" font-size="14" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, anc, INK, esc(txt)))
    for i, (no, dim, old, new, place, badge) in enumerate(ROWS):
        y0 = top + i * ROW_H
        rbg = ROW_A if i % 2 == 0 else ROW_B
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, ROW_H, rbg, LINE))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="15" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, y0 + ROW_H / 2 + 5, MUTED, esc(no)))
        a.append('<text x="%d" y="%.1f" font-size="13.5" font-weight="600" fill="%s">%s</text>' % (C1 + 14, y0 + ROW_H / 2 + 5, INK, esc(dim)))
        a.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s">%s</text>' % (C2 + 14, y0 + ROW_H / 2 + 5, INK, esc(old)))
        a.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s">%s</text>' % (C3 + 14, y0 + ROW_H / 2 + 5, INK, esc(new)))
        fg, bgc = STATE_COLOR[badge]
        bx = (C4 + C5) / 2
        a.append('<rect x="%.1f" y="%.1f" width="52" height="24" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % (bx - 26, y0 + ROW_H / 2 - 12, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="%s">%s</text>' % (bx, y0 + ROW_H / 2 + 4, fg, esc(badge)))
        a.append('<text x="%d" y="%.1f" font-size="11.5" fill="%s">%s</text>' % (C4 + 14, y0 + ROW_H / 2 + 5, MUTED, esc(place)))
    a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12.5" fill="%s">复位规格三条（unlock reset 13 组全 RSTN / I2C_EN=1 全免 / PORSD 不受 password&amp;checksum 保护 / password error reset 例外地址段）详见「复位规格 · 20261106」页</text>' % (FY, MUTED))
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
    svg = svg.replace('<rect x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>', '<rect class="head" x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>', 1)
    for i, ry in enumerate([top + i * ROW_H for i in range(len(ROWS))]):
        pattern = '<rect x="40" y="%d" width="1020" height="%d" fill=' % (ry, ROW_H)
        idx = svg.find(pattern)
        if idx == -1: continue
        delay = ' class="row" style="animation-delay:%.2fs"' % (0.15 + i * 0.14)
        svg = svg[:idx + 5] + delay + svg[idx + 5:]
    svg = svg.replace("</svg>", CSS + "\n</svg>")
    return svg

anim = build_anim(static)
io.open(OUT_ANIM, "w", encoding="utf-8", newline="\n").write(anim)

ss = ET.fromstring(static); sa = ET.fromstring(anim)
st = Counter(t.text for t in ss.iter() if t.tag.endswith('text') and t.text is not None)
at = Counter(t.text for t in sa.iter() if t.tag.endswith('text') and t.text is not None)
drift = "drift-0" if st == at else "DRIFT %d/%d" % (len(st), len(at))
s_static = "static-clean" if ("@keyframes" not in static and "animation:" not in static) else "static-HAS-anim!"
a_anim = "anim-ok" if ("@keyframes" in anim and "animation:" in anim) else "anim-MISSING!"
print("written %s  %dB" % (OUT_STATIC, len(static)))
print("written %s  %dB" % (OUT_ANIM, len(anim)))
print("xml+ %s %s %s" % (s_static, a_anim, drift))
assert s_static == "static-clean" and a_anim == "anim-ok" and drift == "drift-0", "validation failed"
print("ALL PASS")
# ymzhu 2026-11-06 21:15
