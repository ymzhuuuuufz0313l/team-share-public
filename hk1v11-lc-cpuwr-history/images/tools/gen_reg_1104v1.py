#!/usr/bin/env python
# -*- coding: utf-8 -*-
# gen_reg_1104v1.py — 1104v1 迭代变更 · 寄存器三件套升版图（静态事实源 + 动画版，blueprint-ui-style v4）
# 数据源（零手工，源自 t14 1104v1 changelist + 双轨 CHANGES + _reg_20261103_consistency.md）：
#   三件套升版（LC_CPUWR/LC_REG_MAPPING/LINK_CONFIG_CTRL → 1104v1，LINK_CONFIG_CTRL 首次加版本头），
#   基线 = 1104 服务器态（commit 88d369c1）。四项移址 + 0x08 默认 0x00→0x30 + 旧位回 Reserved。
# r1（2026-11-04，b49e5741）：新增第 7 行输出口归属修正——TP_SEL@0x08 / khead_20b_sel@0x1D[7:5] /
#   BACSCR_EOL@0x1D[4] 三输出口 LC_CPUWR→LC_REG_MAPPING（地址≤31 规则），三关复评 0/0/0/0；
#   被替换 r0 版快照于 images/archive/20261104/（图版生命周期与归档标准，2026-11-04）。
# 出：images/1104v1_reg_changes.svg（静态） + images/anim/1104v1_reg_changes.svg（动画）
# 配色对齐现有寄存器图（白底 #ffffff / 墨 #1e293b / 灰 #64748b / 线 #94a3b8 #e2e8f0）
import io, os
import xml.etree.ElementTree as ET
from collections import Counter
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf, archive_snapshot, table_anim  # noqa: E402

# 本脚本位于 images/tools/（2026-11-04 归位），输出 = 上级 images/ 主名位（当前采纳版）
BASE = os.path.dirname(os.path.abspath(__file__))
OUT_STATIC = out_path("images/1104v1_reg_changes.svg")
OUT_ANIM   = out_path("images/anim/1104v1_reg_changes.svg")

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
    "移址":  ("#6366f1", "#e0e7ff"),
    "默认":  ("#0d9488", "#ccfbf1"),
    "版本":  ("#94a3b8", "#f1f5f9"),
    "归属":  ("#1d4ed8", "#dbeafe"),
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


def _load_rows(fig):
    """读取 images/data/<fig>.json 的行数据（A0：表格数据单一事实源）。"""
    import json as _json
    p = Path(__file__).resolve().parents[1] / "data" / (fig + ".json")
    with io.open(p, encoding="utf-8") as f:
        d = _json.load(f)
    return [tuple(r) for r in d["rows"]]

def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

# 数据行（# | 变更点[可 2 行] | 类型 | 影响模块 | 状态 | 状态色）
ROWS = _load_rows("1104v1_reg_changes")   # 数据源 = images/data/1104v1_reg_changes.json（唯一事实源，勿在此改数）

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
    a.append('<text x="550.0" y="42" text-anchor="middle" font-size="22" font-weight="bold" fill="%s">1104v1 迭代变更 · 寄存器三件套升版</text>' % INK)
    a.append('<text x="550.0" y="70" text-anchor="middle" font-size="13" fill="%s">2026-11-04 · 基线 1104 服务器态 · LC_CPUWR / LC_REG_MAPPING / LINK_CONFIG_CTRL → 1104v1（含归属修正）</text>' % MUTED)
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
        lines = change.split("\\n")
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
    a.append('<text x="550.0" y="%d" text-anchor="middle" font-size="12.5" fill="%s">三关全过（初评 critical=0 high=1 → 归属修正 b49e5741 后复评 0/0/0/0）· 极性反转 3\'b101=40bit 其余 20bit · khead 上层消费链改宽挂账（GLM 审查 H1）</text>' % (FY, MUTED))
    a.append('</svg>')
    return "\n".join(a)

static = build_static()
archive_snapshot("images/1104v1_reg_changes.svg", "auto" + __import__("datetime").date.today().strftime("%Y%m%d"))
write_text_lf(OUT_STATIC, static)

# ---- 动画版：静态 + <style>（@keyframes 行级渐入）----
def build_anim(svg):
    """动画版：Kit v4 全套 CSS + sweepband 扫光 + cellwave 行波（不触碰任何 <text>）。"""
    return table_anim(svg)

anim = build_anim(static)
archive_snapshot("images/anim/1104v1_reg_changes.svg", "auto" + __import__("datetime").date.today().strftime("%Y%m%d"))
write_text_lf(OUT_ANIM, anim)

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
# ymzhu 2026-11-17 19:33