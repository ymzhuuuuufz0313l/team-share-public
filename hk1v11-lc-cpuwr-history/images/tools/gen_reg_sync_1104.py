#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_sync_1104.py — 1104 服务器同步 · 寄存器变更图（静态事实源 + 动画版，blueprint-ui-style v4）
# 数据源（零手工，源自 t3/t11 双轨 CHANGES + changelist NO=12 草稿）：
#   服务器 PACK_TAR_1104V1 态覆盖本地，较 1029v1-clean 5 处差异（用户 11-04 确认全部有意、全采不回退）。
# 出：images/1104_reg_sync_changes.svg（静态） + images/anim/1104_reg_sync_changes.svg（动画）
# 配色对齐现有寄存器图（白底 #ffffff / 墨 #1e293b / 灰 #64748b / 线 #94a3b8 #e2e8f0）
import io, os, re
import xml.etree.ElementTree as ET
from collections import Counter

# 本脚本位于 images/tools/（2026-11-04 归位），输出 = 上级 images/ 主名位（当前采纳版）
BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = os.path.join(BASE, "..", "1104_reg_sync_changes.svg")
OUT_ANIM   = os.path.join(BASE, "..", "anim", "1104_reg_sync_changes.svg")

# ---- 站点/现有图配色（对齐 chip_sel*_register_map.svg）----
BG      = "#ffffff"
INK     = "#1e293b"
MUTED   = "#64748b"
LINE    = "#e2e8f0"
LINE2   = "#94a3b8"
HEAD_BG = "#f1f5f9"
ROW_A   = "#ffffff"
ROW_B   = "#f8fafc"
# 类型 badge 配色
TYPE_COLOR = {
    "集成":  ("#f59e0b", "#fef3c7"),
    "功能":  ("#6366f1", "#e0e7ff"),
    "构建":  ("#0d9488", "#ccfbf1"),
    "版本":  ("#94a3b8", "#f1f5f9"),
}
OK_GREEN = "#22c55e"
WARN_AMB = "#f59e0b"

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

def build_static():
    a = []
    a.append('<?xml version="1.0" encoding="UTF-8"?>')
    a.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" style="background:%s">' % (W, H, W, H, BG))
    a.append('<rect width="%d" height="%d" fill="%s"/>' % (W, H, BG))
    # 标题
    a.append('<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">1104 服务器同步 · 寄存器变更</text>' % INK)
    a.append('<text x="550.0" y="70" text-anchor="middle" font-size="13" fill="%s">2026-11-04 · PACK_TAR_1104V1 · 未单独升版本号（本地基线 1029v1）</text>' % MUTED)
    # 表头
    HEAD_Y = 100
    a.append('<rect x="%d" y="%d" width="%d" height="34" fill="%s"/>' % (CX0, HEAD_Y, C5 - CX0, HEAD_BG))
    headers = [("#", C1, "middle"), ("变更点", (CX0 + C1 + C2) / 2, "middle"), ("类型", (C2 + C3) / 2, "middle"),
               ("影响模块", (C3 + C4) / 2, "middle"), ("状态", (C4 + C5) / 2, "middle")]
    for txt, x, anc in headers:
        a.append('<text x="%.1f" y="%d" text-anchor="%s" font-size="14" font-weight="700" fill="%s">%s</text>' % (x, HEAD_Y + 22, anc, INK, esc(txt)))
    # 数据行
    rows = [
        ("1", "集成前移：4 挂账输出连线（R_KHEAD_20B_SEL / R_TP_SEL /\nR_BACSCR_EOL / R_SCS_PKT_HALF）", "集成", "LINK_CONFIG_CTRL", "✅ 已连", OK_GREEN),
        ("2", "CS_SET_1H：~R_BKDU → ~BKDU_SYNC（同步版）", "功能", "LC_CPUWR", "✅ 同步版", OK_GREEN),
        ("3", "R_TP_F_AHEAD (0x2E[3]) 停用：回 Reserved、\nLC_CPUWR 端口注释、LINK 驱常量 0", "功能", "LC_CPUWR + LINK", "✅ 停用", OK_GREEN),
        ("4", "R_DPLC_MODE：`ifdef LONG_VU440_FPGA 强 1\u2032b0（长编码构建）", "构建", "LC_CPUWR", "✅ 长编码强0", OK_GREEN),
        ("5", "LC_REG_MAPPING 头仍 1027v1（功能已等同 1029v1，未升头）", "版本", "LC_REG_MAPPING", "⏸ 未升头", WARN_AMB),
    ]
    ROW_H = 88
    top = HEAD_Y + 34
    for i, (no, change, typ, mod, status, scolor) in enumerate(rows):
        y0 = top + i * ROW_H
        rbg = ROW_A if i % 2 == 0 else ROW_B
        a.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s" stroke="%s" stroke-width="1"/>' % (CX0, y0, C5 - CX0, ROW_H, rbg, LINE))
        # # 列
        a.append('<text x="%.1f" y="%.1f" text-anchor="middle" font-size="15" font-weight="700" fill="%s">%s</text>' % ((CX0 + C1) / 2, y0 + ROW_H / 2 + 5, MUTED, esc(no)))
        # 变更点（最多 2 行，从 C1 列右缘起）
        TX = C1 + 14
        lines = change.split("\n")
        if len(lines) == 1:
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + ROW_H / 2 + 5, INK, esc(lines[0])))
        else:
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + 34, INK, esc(lines[0])))
            a.append('<text x="%d" y="%.1f" font-size="13.5" fill="%s">%s</text>' % (TX, y0 + 56, INK, esc(lines[1])))
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
    FY = top + len(rows) * ROW_H + 26
    a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12.5" fill="%s">用户 11-04 确认 5 处差异全部有意 · 全采不回退 · changelist Register Change NO=12 登记草稿（待用户登记）</text>' % (FY, MUTED))
    a.append('</svg>')
    return "\n".join(a)

H = 720  # 高度（标题+副题+表头+5行×88+底注）
static = build_static()
os.makedirs(os.path.dirname(OUT_ANIM), exist_ok=True)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(static)

# ---- 动画版：静态 + <style>（@keyframes 行级渐入 + 类型/状态脉冲）----
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
    row_ys = [134, 222, 310, 398, 486]
    for i, ry in enumerate(row_ys):
        pattern = '<rect x="40" y="%d" width="1020" height="88" fill=' % ry
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
# ymzhu 2026-11-04 16:10
