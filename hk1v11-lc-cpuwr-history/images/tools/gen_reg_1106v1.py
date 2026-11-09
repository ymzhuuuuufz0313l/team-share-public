#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_1106v1.py — 1106v1 服务器回传包 · 寄存器变更图（静态事实源 + 动画版，blueprint-ui-style v4）
# 2026-11-09 重写：估宽折行 + 行高自适应 + badge 宽度自适应 + 生成器内置重叠自检（修复 11-06 版文字压胶囊/列互叠）
# 数据源（零手工，源自 LC_CPUWR_history/CHANGES.md 1106v1 条目 (a)~(j) + 双轨 CHANGES + _1106_smartcs_excel_audit.md）
# 出：images/1106v1_reg_changes.svg（静态） + images/anim/1106v1_reg_changes.svg（动画）
import io, os, re, unicodedata
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "1106v1_reg_changes.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "1106v1_reg_changes.svg")

BG, INK, MUTED = "#ffffff", "#1e293b", "#64748b"
LINE, HEAD_BG  = "#e2e8f0", "#f1f5f9"
ROW_A, ROW_B   = "#ffffff", "#f8fafc"
TYPE_COLOR = {
    "恒直出": ("#0d9488", "#ccfbf1"), "新增": ("#1d4ed8", "#dbeafe"),
    "归属":   ("#6366f1", "#e0e7ff"), "收窄": ("#b45309", "#f7e8d4"),
    "env":    ("#7c3aed", "#ede9fe"), "删除": ("#dc2626", "#fee2e2"),
}
OK_GREEN = "#22c55e"

W = 1100
CX0, C1, C2, C3, C4, C5 = 40, 72, 556, 662, 868, W - 40   # 列 x 边界（类型=胶囊独立列）

# ---- layout core：估宽 + 贪心折行（2026-11-09，防重叠核心）----
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
            for j in range(len(cur) - 1, max(0, int(len(cur)*0.4)) - 1, -1):
                if cur[j] in BREAK_CHARS:
                    cut = j; break
            if cut < 0: cut = len(cur) - 1
            lines.append(cur[:cut+1].rstrip())
            cur = cur[cut+1:].lstrip() + ch if cur[cut] not in ' ' else ch if ch != ' ' else ''
            cur = cur or ''
        else:
            cur += ch
    if cur: lines.append(cur)
    return lines or ['']

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

ROWS = [
    ("1", ["SMART_CS 恒直出（去 CHIP_SEL 门控）", "0x02 无条件直通 {R_REG02_F[7:6],[3:2]}，cs=0 也直出"], "恒直出", "LC_REG_MAPPING", "✅ 符合 20261103 表", OK_GREEN),
    ("2", ["VPS_EN_0 新增输出端口", "0x28[6] low-power 上抛（R_REG40_F[6]），164 行"], "新增", "LINK_CONFIG_CTRL", "✅ 新端口", OK_GREEN),
    ("3", ["四根寄存器输出连接移位", "VPS_EN_1/khead/TP_SEL/BACSCR → LC_REG_MAPPING 实例尾部（挂法同 1104v1）"], "归属", "LINK_CONFIG_CTRL", "✅ 功能零变化", OK_GREEN),
    ("4", ["khead 消费链收窄 [4:0]→[2:0]", "CHPI_DECODE / SHORT&LONG_ENCODING(_ALIGN) / long_encoding 全链"], "收窄", "全链 6 文件", "✅ 清 1104 挂账", OK_GREEN),
    ("5", ["K4_FIND_1 新信号链", "SHORT_ENCODING_ALIGN 输出 → SHORT_ENCODING_OUTPUT", "config_mode_k4_1（新配置模式寄存器）"], "新增", "SHORT_ENCODING", "✅ 新链", OK_GREEN),
    ("6", ["env_cfg 寄存器表 19 hunk", "TP_SEL@0x08[5:4] 默认 11 / 0x1D 重排 / 删 TP_F_AHEAD / 新增 SCS_PKT_HALF"], "env", "DV_TCON_C", "✅ 19 hunk", OK_GREEN),
    ("7", ["LENB_CTRL 删 BIT_ALIGN_PT_DLY", "打拍寄存器删除（少一拍延迟，任务书外 V1 服务器项）"], "删除", "LENB_CTRL", "✅ 自查补充", OK_GREEN),
]

HEAD_Y = 100
LH, PAD = 19, 17   # 内容行高 / 上下留白
# 预折行（fs, maxw）：变更点 12.5px/458、模块 11.5px/186、状态 12.5px/174
WL = [(r[0], [ln for part in r[1] for ln in wrap(part, 12.5, 458)], r[2],
       wrap(r[3], 11.5, 186), wrap(r[4], 12.5, 174), r[5]) for r in ROWS]
GEOM = []          # (y, h) 每行，供动画注入
y = HEAD_Y + 34
for r in WL:
    h = max(64, len(r[1]) * LH + 2 * PAD, len(r[3]) * LH + 2 * PAD, len(r[4]) * LH + 2 * PAD)
    GEOM.append((y, int(h))); y += int(h)
top, FY, H = HEAD_Y + 34, y + 26, y + 26 + 40

def build_static():
    a = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG),
         '<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG),
         '<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">1106v1 服务器回传包 · 寄存器变更</text>' % INK,
         '<text x="550.0" y="70" text-anchor="middle" font-size="12.5" fill="%s">%s</text>' % (MUTED, esc(wrap('2026-11-06 · 基线 1104v1（本机）+ 服务器 1106 代修改 · 三件套 md5 与 V1 tar 原字节一致 · 寄存器表推进 20261103→20261106', 12.5, 1000)[0])),
         '<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG)]
    headers = [("#", (CX0 + C1) / 2), ("变更点（旧 → 新）", (C1 + C2) / 2), ("类型", (C2 + C3) / 2),
               ("影响模块", (C3 + C4) / 2), ("状态", (C4 + C5) / 2)]
    for txt, x in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="middle" font-size="14" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, INK, esc(txt)))
    for i, (no, chg, typ, mod, status, scolor) in enumerate(WL):
        (y0, rh) = GEOM[i]
        cy = y0 + rh / 2
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, rh, ROW_A if i % 2 == 0 else ROW_B, LINE))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="15" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, cy + 5, MUTED, esc(no)))
        ty0 = cy - (len(chg) - 1) * LH / 2 + 4.5
        for k, ln in enumerate(chg):
            a.append('<text x="%d" y="%.1f" font-size="12.5" fill="%s">%s</text>' % (C1 + 14, ty0 + k * LH, INK, esc(ln)))
        fg, bgc = TYPE_COLOR[typ]
        bw = max(52, text_w(typ, 12) + 26)
        a.append('<rect x="%.1f" y="%.1f" width="%.0f" height="24" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % ((C2 + C3) / 2 - bw / 2, cy - 12, bw, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="%s">%s</text>' % ((C2 + C3) / 2, cy + 4, fg, esc(typ)))
        ty0 = cy - (len(mod) - 1) * LH / 2 + 4
        for k, ln in enumerate(mod):
            a.append('<text x="%d" y="%.1f" font-size="11.5" fill="%s" font-family="Consolas, Monaco, monospace">%s</text>' % (C3 + 12, ty0 + k * LH, INK, esc(ln)))
        ty0 = cy - (len(status) - 1) * LH / 2 + 4.5
        for k, ln in enumerate(status):
            a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" font-weight="700" fill="%s">%s</text>' % ((C4 + C5) / 2, ty0 + k * LH, scolor, esc(ln)))
    for k, ln in enumerate(wrap('SMART_CS 恒直出符合 20261103 表（chip_sel 不控制 0x02）· khead 消费链 [2:0] 收窄清 1104 挂账宽度半边 · env↔RTL 0x1D 打包不一致待反馈 · changelist NO56', 12, 1020)):
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
        svg = svg[:idx + 5] + ' class="row" style="animation-delay:%.2fs"' % (0.15 + i * 0.12) + svg[idx + 5:]
    return svg.replace("</svg>", CSS + "\n</svg>")

anim = build_anim(static)
io.open(OUT_ANIM, "w", encoding="utf-8", newline="\n").write(anim)

# ---- 校验：XML / 双版 / 零漂移 + 重叠自检（硬门禁）----
ss, sa = ET.fromstring(static), ET.fromstring(anim)
st = Counter(t.text for t in ss.iter() if t.tag.endswith('text') and t.text is not None)
at = Counter(t.text for t in sa.iter() if t.tag.endswith('text') and t.text is not None)
drift = "drift-0" if st == at else "DRIFT"
s_static = "static-clean" if ("@keyframes" not in static and "animation:" not in static) else "static-HAS-anim!"
a_anim = "anim-ok" if ("@keyframes" in anim and "animation:" in anim) else "anim-MISSING!"

def overlap_audit(xml):
    boxes = []
    for t in ss.iter():
        if not t.tag.endswith('text') or t.text is None: continue
        fs = float(t.get('font-size', 13)); x = float(t.get('x', 0)); yy = float(t.get('y', 0))
        anc = t.get('text-anchor', 'start'); w = text_w(t.text, fs)
        x0 = x - w / 2 if anc == 'middle' else x
        boxes.append((x0, yy - fs * 0.78, x0 + w, yy + fs * 0.22))
    bad = 0
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            ox = min(boxes[i][2], boxes[j][2]) - max(boxes[i][0], boxes[j][0])
            oy = min(boxes[i][3], boxes[j][3]) - max(boxes[i][1], boxes[j][1])
            if ox > 2 and oy > 2: bad += 1
        if boxes[i][2] > W - 2 or boxes[i][0] < 2: bad += 1
    return bad

n_ov = overlap_audit(static)
print("written %s %dB / %s %dB" % (OUT_STATIC, len(static), OUT_ANIM, len(anim)))
print("xml+ %s %s %s overlap=%d" % (s_static, a_anim, drift, n_ov))
assert s_static == "static-clean" and a_anim == "anim-ok" and drift == "drift-0" and n_ov == 0, "validation failed"
print("ALL PASS")
# ymzhu 2026-11-09 10:20
