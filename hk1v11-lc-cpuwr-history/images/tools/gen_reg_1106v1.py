#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_1106v1.py — 1106v1 服务器回传包 · 寄存器变更图（静态事实源 + 动画版，blueprint-ui-style v4）
# 数据源（零手工，源自 LC_CPUWR_history/CHANGES.md 1106v1 条目 (a)~(j) + 双轨 CHANGES + _1106_smartcs_excel_audit.md）：
#   服务器回传包 1106 代批准覆盖（PACK_TAR_1106V1/V0/V2，他人修改、diff-first 全采），基线 = 本机 1104v1。
#   SMART_CS 恒直出 / VPS_EN_0 新端口 / 四根连接移 LC_REG_MAPPING 尾部 / khead 消费链 [2:0] 收窄 /
#   K4_FIND_1 新链 / env_cfg 19 hunk / LENB_CTRL 删打拍。寄存器表推进 20261103→20261106。
# 出：images/1106v1_reg_changes.svg（静态） + images/anim/1106v1_reg_changes.svg（动画）
# 配色对齐现有寄存器图（白底 #ffffff / 墨 #1e293b / 灰 #64748b / 线 #94a3b8 #e2e8f0）
import io, os
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "1106v1_reg_changes.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "1106v1_reg_changes.svg")

# ---- 站点/现有图配色（对齐 chip_sel*_register_map.svg / 1104v1_reg_changes.svg）----
BG      = "#ffffff"
INK     = "#1e293b"
MUTED   = "#64748b"
LINE    = "#e2e8f0"
HEAD_BG = "#f1f5f9"
ROW_A   = "#ffffff"
ROW_B   = "#f8fafc"
# 类型 badge 配色（fg, bg）
TYPE_COLOR = {
    "恒直出": ("#0d9488", "#ccfbf1"),
    "新增":   ("#1d4ed8", "#dbeafe"),
    "归属":   ("#6366f1", "#e0e7ff"),
    "收窄":   ("#b45309", "#f7e8d4"),
    "env":   ("#7c3aed", "#ede9fe"),
    "删除":   ("#dc2626", "#fee2e2"),
}
OK_GREEN = "#22c55e"

W = 1100
# 列 x 边界
CX0 = 40            # 左边
C1  = 92            # # 列右
C2  = 560           # 变更点 列右
C3  = 672           # 类型 列右
C4  = 884           # 影响模块 列右
C5  = W - 40        # 状态 列右 (1060)

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# 数据行（# | 变更点[1-2 行 list] | 类型 | 影响模块 | 状态 | 状态色）
ROWS = [
    ("1", ["SMART_CS 恒直出（去 CHIP_SEL 门控）", "0x02 无条件直通 {R_REG02_F[7:6],[3:2]}，cs=0 也直出"], "恒直出", "LC_REG_MAPPING", "✅ 符合 20261103 表", OK_GREEN),
    ("2", ["VPS_EN_0 新增输出端口", "0x28[6] low-power 上抛（R_REG40_F[6]），164 行"], "新增", "LINK_CONFIG_CTRL", "✅ 新端口", OK_GREEN),
    ("3", ["四根寄存器输出连接移位", "VPS_EN_1/khead/TP_SEL/BACSCR → LC_REG_MAPPING 实例尾部（挂法同 1104v1）"], "归属", "LINK_CONFIG_CTRL", "✅ 功能零变化", OK_GREEN),
    ("4", ["khead 消费链收窄 [4:0]→[2:0]", "CHPI_DECODE / SHORT&LONG_ENCODING(_ALIGN) / long_encoding 全链"], "收窄", "全链 6 文件", "✅ 清 1104 挂账", OK_GREEN),
    ("5", ["K4_FIND_1 新信号链", "SHORT_ENCODING_ALIGN 输出 → SHORT_ENCODING_OUTPUT config_mode_k4_1"], "新增", "SHORT_ENCODING", "✅ 新链", OK_GREEN),
    ("6", ["env_cfg 寄存器表 19 hunk", "TP_SEL@0x08[5:4] 默认 11 / 0x1D 重排 / 删 TP_F_AHEAD / 新增 SCS_PKT_HALF"], "env", "DV_TCON_C", "✅ 19 hunk", OK_GREEN),
    ("7", ["LENB_CTRL 删 BIT_ALIGN_PT_DLY", "打拍寄存器删除（少一拍延迟，任务书外 V1 服务器项）"], "删除", "LENB_CTRL", "✅ 自查补充", OK_GREEN),
]

HEAD_Y = 100
ROW_H = 88
top = HEAD_Y + 34
FY = top + len(ROWS) * ROW_H + 30
H = FY + 40  # 高度（动态）

def build_static():
    a = []
    a.append('<?xml version="1.0" encoding="UTF-8"?>')
    a.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG))
    a.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    # 标题
    a.append('<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">1106v1 服务器回传包 · 寄存器变更</text>' % INK)
    a.append('<text x="550.0" y="70" text-anchor="middle" font-size="13" fill="%s">2026-11-06 · 基线 1104v1（本机）+ 服务器 1106 代修改 · 三件套 md5 与 V1 tar 原字节一致 · 寄存器表推进 20261103→20261106</text>' % MUTED)
    # 表头
    a.append('<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG))
    headers = [("#", C1, "middle"), ("变更点（旧 → 新）", (CX0 + C1 + C2) / 2, "middle"), ("类型", (C2 + C3) / 2, "middle"),
               ("影响模块", (C3 + C4) / 2, "middle"), ("状态", (C4 + C5) / 2, "middle")]
    for txt, x, anc in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="%s" font-size="14" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, anc, INK, esc(txt)))
    # 数据行
    for i, (no, change, typ, mod, status, scolor) in enumerate(ROWS):
        y0 = top + i * ROW_H
        rbg = ROW_A if i % 2 == 0 else ROW_B
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, ROW_H, rbg, LINE))
        # # 列
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="15" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, y0 + ROW_H / 2 + 5, MUTED, esc(no)))
        # 变更点（最多 2 行，从 C1 列右缘起）
        TX = C1 + 14
        if len(change) == 1:
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + ROW_H / 2 + 5, INK, esc(change[0])))
        else:
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + 34, INK, esc(change[0])))
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + 56, INK, esc(change[1])))
        # 类型 badge
        fg, bgc = TYPE_COLOR[typ]
        bx = (C2 + C3) / 2
        a.append('<rect x="%.1f" y="%.1f" width="56" height="24" rx="12" fill="%s" stroke="%s" stroke-width="1"/>' % (bx - 28, y0 + ROW_H / 2 - 12, bgc, fg))
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12" font-weight="700" fill="%s">%s</text>' % (bx, y0 + ROW_H / 2 + 4, fg, esc(typ)))
        # 影响模块
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="12.5" fill="%s" font-family="Consolas, Monaco, monospace">%s</text>' % ((C3 + C4) / 2, y0 + ROW_H / 2 + 5, INK, esc(mod)))
        # 状态
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="13" font-weight="700" fill="%s">%s</text>' % ((C4 + C5) / 2, y0 + ROW_H / 2 + 5, scolor, esc(status)))
    # 底注
    a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12.5" fill="%s">SMART_CS 恒直出符合 20261103 表（chip_sel 不控制 0x02）· khead 消费链 [2:0] 收窄清 1104 挂账宽度半边 · env↔RTL 0x1D 打包不一致待反馈 · changelist NO56</text>' % (FY, MUTED))
    a.append('</svg>')
    return "\n".join(a)

static = build_static()
os.makedirs(os.path.dirname(OUT_ANIM), exist_ok=True)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(static)

# ---- 动画版：静态 + <style>（@keyframes 行级渐入，站点固定模块）----
CSS = """<style>
.title, .head { opacity:0; animation: fadeIn .4s ease forwards; }
.row { opacity:0; animation: rowIn .35s cubic-bezier(.22,.7,.3,1) forwards; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }
@keyframes rowIn { from { opacity:0; transform:translateY(6px); } to { opacity:1; transform:none; } }
@media (prefers-reduced-motion:reduce) { *{animation:none!important} .title,.head,.row{opacity:1!important} }
</style>"""

def build_anim(svg):
    # 给标题加 class title
    svg = svg.replace('font-size="22" font-weight="bold" fill="#1e293b"', 'class="title" font-size="22" font-weight="bold" fill="#1e293b"', 1)
    # 表头背景 rect 加 head
    svg = svg.replace('<rect x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>', '<rect class="head" x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>', 1)
    # 数据行：在每行背景 rect 的 <rect 后插入 class row + 延迟
    row_ys = [top + i * ROW_H for i in range(len(ROWS))]
    for i, ry in enumerate(row_ys):
        pattern = '<rect x="40" y="%d" width="1020" height="%d" fill=' % (ry, ROW_H)
        idx = svg.find(pattern)
        if idx == -1:
            continue
        delay = ' class="row" style="animation-delay:%.2fs"' % (0.15 + i * 0.12)
        svg = svg[:idx + 5] + delay + svg[idx + 5:]
    # 注入 CSS 在 </svg> 前
    svg = svg.replace("</svg>", CSS + "\n</svg>")
    return svg

anim = build_anim(static)
io.open(OUT_ANIM, "w", encoding="utf-8", newline="\n").write(anim)

# ---- 校验：XML 有效 / 静态无动画 / 动画有 / <text> 零漂移 ----
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
# ymzhu 2026-11-06 19:10
