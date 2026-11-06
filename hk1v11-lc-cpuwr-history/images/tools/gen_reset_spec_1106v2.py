#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reset_spec_1106v2.py — 复位规格图（20261106 / 1106v2 落地，静态事实源 + 动画版，blueprint-ui-style v4）
# 数据源：LC_CPUWR_history/CHANGES.md 1106v2 (5) + script/_regen_1106/{t9_impl,fix_round1}.md（用户亲自 review 材料）
# 出：images/reset_spec_1106v2.svg（静态） + images/anim/reset_spec_1106v2.svg（动画）
# 配色对齐现有寄存器图（白底 #ffffff / 墨 #1e293b / 灰 #64748b / 线 #94a3b8 #e2e8f0）
import io, os
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "reset_spec_1106v2.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "reset_spec_1106v2.svg")

BG      = "#ffffff"
INK     = "#1e293b"
MUTED   = "#64748b"
LINE    = "#e2e8f0"
HEAD_BG = "#f1f5f9"
ROW_A   = "#ffffff"
ROW_B   = "#f8fafc"
# 状态 badge 配色（fg, bg）
STATE_COLOR = {
    "迁移":   ("#b45309", "#f7e8d4"),   # 琥珀（t9 迁 RSTN）
    "已符合": ("#0d9488", "#ccfbf1"),   # 青
    "零改动": ("#16a34a", "#dcfce7"),   # 绿
    "一致":   ("#1d4ed8", "#dbeafe"),   # 蓝
    "链路":   ("#7c3aed", "#ede9fe"),   # 紫
}

W = 1100
CX0 = 40
C1  = 92            # # 列右
C2  = 320           # 复位规格维度 列右
C3  = 800           # 关键内容 列右
C4  = 930           # RTL 状态 列右
C5  = W - 40        # 改动 列右 (1060)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# 数据行（# | 维度 | 关键内容[1-2 行] | RTL 状态 badge | 改动）
ROWS = [
    ("1", "unlock reset 例外清单", ["13 组 CTRL_F 信号全 RSTN 域", "AVE_RGBW / AVE_LAST / DPLC_GROUP / DPOLINV / AVE_MODE / CTRLF_CHECKSUM + 其余 7 组"], "迁移", "6 组 t9 迁 RSTN"),
    ("2", "I2C_EN=1 全免 unlock reset", ["I2C_EN_CTL → TEST_EN → I_TEST_REG_EN → RSTNGEN:50", "I2C_EN=1 时寄存器不进入 unlock reset 语义"], "链路", "零改动（链路已存在）"),
    ("3", "PORSD 不受 password & checksum 保护", ["PORSD = RSTN 域 + 不在 LSI（password）集", "checksum 排除属 BCC 主端软件口径（非 RTL）"], "已符合", "零改动"),
    ("4", "password error reset 例外地址段", ["受门控段 32-38 / 40-47 / 51 / 53-57 / 144-147（dec）", "0x40~0x44 整块（dec 64~68）不做 password error reset"], "一致", "零改动（=表 AC 列）"),
]

HEAD_Y = 100
ROW_H = 96
top = HEAD_Y + 34
FY = top + len(ROWS) * ROW_H + 30
H = FY + 40

def build_static():
    a = []
    a.append('<?xml version="1.0" encoding="UTF-8"?>')
    a.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG))
    a.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    a.append('<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">复位规格 · 20261106（1106v2 落地）</text>' % INK)
    a.append('<text x="550.0" y="70" text-anchor="middle" font-size="13" fill="%s">用户补充复位规格三条已全部落地/核实 · 本轮 t12 复位零新增修复项 · 经 RTL 三关复核维持正确</text>' % MUTED)
    # 表头
    a.append('<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG))
    headers = [("#", C1, "middle"), ("复位规格维度", (CX0 + C1 + C2) / 2, "middle"), ("关键内容（位段 / 地址 / 链路）", (C2 + C3) / 2, "middle"),
               ("RTL 状态", (C3 + C4) / 2, "middle"), ("改动", (C4 + C5) / 2, "middle")]
    for txt, x, anc in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="%s" font-size="14" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, anc, INK, esc(txt)))
    # 数据行
    for i, (no, dim, content, badge, change) in enumerate(ROWS):
        y0 = top + i * ROW_H
        rbg = ROW_A if i % 2 == 0 else ROW_B
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, ROW_H, rbg, LINE))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="15" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, y0 + ROW_H / 2 + 5, MUTED, esc(no)))
        # 维度
        TX = C1 + 14
        a.append('<text x="%d" y="%.1f" font-size="13.5" font-weight="600" fill="%s">%s</text>' % (TX, y0 + ROW_H / 2 + 5, INK, esc(dim)))
        # 关键内容（2 行）
        TX2 = C2 + 14
        a.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s">%s</text>' % (TX2, y0 + 38, INK, esc(content[0])))
        a.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s">%s</text>' % (TX2, y0 + 60, INK, esc(content[1])))
        # badge
        fg, bgc = STATE_COLOR[badge]
        bx = (C3 + C4) / 2
        a.append('<rect x="%.1f" y="%.1f" width="62" height="24" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % (bx - 31, y0 + ROW_H / 2 - 12, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="%s">%s</text>' % (bx, y0 + ROW_H / 2 + 4, fg, esc(badge)))
        # 改动
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" font-weight="600" fill="%s">%s</text>' % ((C4 + C5) / 2, y0 + ROW_H / 2 + 5, INK, esc(change)))
    # 底注
    a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12.5" fill="%s">unlock reset 13 组明细（位段）：0x00[7:5] / 0x01[7] / 0x05[7:5] / 0x06[7,5,3,2,1] / 0x07[3:0] / 0x20[5:0] / 0x21[5:4] / 0x30[7:0] / I2C 0xF0·0xF1 · 0xA0~0xA1 只读不参与 password error reset</text>' % (FY, MUTED))
    a.append('</svg>')
    return "\n".join(a)

static = build_static()
os.makedirs(os.path.dirname(OUT_ANIM), exist_ok=True)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(static)

# ---- 动画版：静态 + <style>（行级渐入，站点固定模块）----
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
    row_ys = [top + i * ROW_H for i in range(len(ROWS))]
    for i, ry in enumerate(row_ys):
        pattern = '<rect x="40" y="%d" width="1020" height="%d" fill=' % (ry, ROW_H)
        idx = svg.find(pattern)
        if idx == -1:
            continue
        delay = ' class="row" style="animation-delay:%.2fs"' % (0.15 + i * 0.14)
        svg = svg[:idx + 5] + delay + svg[idx + 5:]
    svg = svg.replace("</svg>", CSS + "\n</svg>")
    return svg

anim = build_anim(static)
io.open(OUT_ANIM, "w", encoding="utf-8", newline="\n").write(anim)

# ---- 校验 ----
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
# ymzhu 2026-11-06 21:00
