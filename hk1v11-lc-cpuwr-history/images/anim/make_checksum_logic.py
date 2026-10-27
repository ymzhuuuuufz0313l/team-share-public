#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_checksum_logic.py — LC_CPUWR Seg1 checksum 实现逻辑图（静态 + 动画版一并生成）。

输出（幂等）：
  ../checksum_logic_flow.svg          静态版（站点 images/）
  checksum_logic_flow.svg             动画版（站点 images/anim/）

动画（流向版，2026-10-26 用户定稿口径）：无入场动画（无 opacity:0 初始态）；
主干 4 条连接线流光点（infinite，150pt/s）；5'h04 修复卡呼吸（2s）；update_en 提交门呼吸
（stroke-opacity 3.2s）。纯 CSS 无 <script>，终态=静态图。

自检（六项）：XML well-formed / <text> 多重集一致 / 无 <script> / keyframes 存在 /
viewBox 一致 / 特效组计数。
"""
import xml.etree.ElementTree as ET
from collections import Counter
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.normpath(os.path.join(HERE, os.pardir, "checksum_logic_flow.svg"))
ANIM = os.path.join(HERE, "checksum_logic_flow.svg")

W, H = 1240, 900
INK, MUT, BRD = "#1e293b", "#64748b", "#94a3b8"
TEAL, TEAL_L = "#0e7490", "#ccfbf1"
GRAY_L = "#f1f5f9"
AMBER_B, AMBER_L = "#fb923c", "#fff7ed"
GREEN_L = "#ecfdf5"

L = []          # static elements (flat, one per line)
FLOW = []       # (path_d, length) spine connectors to animate


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=12, weight=None, fill=INK, anchor="middle", mono=False):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    w = f' font-weight="{weight}"' if weight else ""
    f = ' font-family="Consolas, Monaco, monospace"' if mono else ' font-family="Microsoft YaHei, PingFang SC, sans-serif"'
    L.append(f'<text x="{x}" y="{y}" font-size="{size}"{f} fill="{fill}"{a}{w}>{esc(s)}</text>')


def diamond(cx, cy, r, fill):
    L.append(f'<path d="M {cx},{cy - r} L {cx + r},{cy} L {cx},{cy + r} L {cx - r},{cy} Z" fill="{fill}"/>')


def rect(x, y, w, h, fill, stroke=BRD, sw=1.25, rx=6, dash=None, cls=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' class="{cls}"' if cls else ""
    L.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"{d}{c}/>')


def arrow(x1, y1, x2, y2, color=TEAL, sw=2.5, dash=None, flow=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    L.append(f'<path d="M {x1},{y1} L {x2},{y2}" stroke="{color}" stroke-width="{sw}" fill="none"{d} marker-end="url(#arr_{color[1:]})" stroke-linecap="round"/>')
    if flow:
        FLOW.append((f"M {x1},{y1} L {x2},{y2}", abs(x2 - x1) + abs(y2 - y1), color))


# ---------------- defs & title ----------------
L.append(f'<rect width="{W}" height="{H}" fill="#ffffff"/>')
L.append('<defs>')
for c in (TEAL, "#6b7280", "#b45309"):
    L.append(f'<marker id="arr_{c[1:]}" viewBox="0 0 10 7" refX="9" refY="3.5" markerWidth="9" markerHeight="6.5" orient="auto"><path d="M0,0 L10,3.5 L0,7 Z" fill="{c}"/></marker>')
L.append('</defs>')
text(W // 2, 36, "LC_CPUWR Seg1 Checksum 实现逻辑（WCK1_A 单域 · 三帧一致提交）", 22, 800)
text(W // 2, 58, "0721v1 3B/beat 按字节有效性折叠  ·  1023v1-E2 比较合法性防护  ·  1027v1-B 修复 0x0A 覆盖", 12.5, fill=MUT)

# ---------------- Lane 1: beat stream ----------------
text(40, 92, "① 帧数据流 —— 每拍 3 字节（C/D/F 槽），xdata_a 按拍选择参与字节", 13, 700, anchor="start")
beats = [
    ("5'h01", "C^D^F", "0x00 · 01 · 02", "全参与", False),
    ("5'h02", "C^D^F", "0x03 · 04 · 05", "全参与", False),
    ("5'h03", "C^F", "0x06 · 0x08", "0x07 ✗ 控制", False),
    ("5'h04", "C^D", "0x09 · 0x0A", "0x0B gap", True),
    ("gap 05-09", "—", "0x0C ~ 0x1A", "无参与字节", False),
    ("5'h0A", "F", "0x1D", "0x1B/1C gap", False),
    ("5'h0B", "C^D", "0x1E · 0x1F", "0x20 ✗ 出窗", False),
    ("5'h0E", "C", "0x27 帧尾", "0x28/29 ✗", False),
]
cw, ch, gap, x0, y1 = 138, 92, 8, 40, 104
for i, (tag, fold, addrs, note, fix) in enumerate(beats):
    x = x0 + i * (cw + gap)
    grp_open = len(L)
    if fix:
        L.insert(grp_open, "")  # placeholder, replaced at anim build
        FIX_OPEN = len(L) - 1
    fill = TEAL_L if fix else (GRAY_L if tag.startswith("gap") else "#ffffff")
    stroke = "#b45309" if fix else BRD
    rect(x, y1, cw, ch, fill, stroke, 1.6 if fix else 1.25,
         dash="5,3" if tag.startswith("gap") else None)
    text(x + cw / 2, y1 + 22, tag, 13, 700, TEAL if not fix else "#b45309", mono=True)
    text(x + cw / 2, y1 + 44, fold, 12, 700, mono=True)
    text(x + cw / 2, y1 + 64, addrs, 10.5, fill=INK, mono=True)
    text(x + cw / 2, y1 + 82, note, 9.5, fill=MUT)
    if fix:
        diamond(x + cw - 14, y1 + 12, 7, "#b45309")
        FIX_CLOSE = len(L)
        FIX_RANGE = (FIX_OPEN, FIX_CLOSE, x)

# spine: cards -> xsum
cx = 320
arrow(W // 2, y1 + ch + 6, W // 2, 236, flow=True)
text(W // 2 + 10, 226, "xdata_a（逐拍送入 XOR）", 11, fill=TEAL, anchor="start")

# ---------------- Lane 2: accumulate & latch ----------------
text(40, 262, "② 累加与锁存", 13, 700, anchor="start")
rect(cx - 180, 276, 360, 84, "#ffffff")
text(cx, 296, "运行 XOR 累加器  xsum_a", 13, 700)
text(cx, 316, "frame_start 直存首拍 · xor_en 逐拍 ^xdata_a · 帧尾拍不累加", 10.5, fill=MUT)
text(cx, 334, "复位/退出 chksum_mode 清 0", 10, fill=MUT)
px = 940
rect(px - 170, 276, 340, 84, "#ffffff")
text(px, 296, "上一帧全帧 XOR  prev_xsum_a", 13, 700)
text(px, 316, "frame_end 拍锁存 xsum_a ^ xdata_a", 10.5, fill=MUT)
text(px, 334, "prev_valid_a=1 才允许参与比较（1023v1）", 10, fill=MUT)
arrow(cx + 180, 318, px - 170, 318, flow=True)
text((cx + 180 + px - 170) / 2, 308, "帧尾锁存（^ 0x27 校验字节）", 10.5, fill=TEAL)

# ---------------- Lane 3: compare + guard ----------------
text(40, 396, "③ 帧尾比较 + 合法性防护", 13, 700, anchor="start")
rect(cx - 220, 410, 440, 96, "#ffffff")
text(cx, 432, "match_a 判据（帧尾拍）", 13, 700)
text(cx, 452, "(xsum_a ^ xdata_a) == prev_xsum_a  &&  frame_end_a", 11.5, mono=True)
text(cx, 472, "xdata_a@帧尾 = 0x27 校验字节（DATA_C 槽）", 10, fill=MUT)
text(cx, 490, "两帧一致 ⇔ 本帧数据+校验 与历史累计吻合", 10, fill=MUT)
gx = 940
rect(gx - 170, 410, 340, 96, "#ffffff")
text(gx, 432, "防护 cmp_valid_a（1023v1-E2）", 13, 700)
text(gx, 452, "prev_valid_a & frm_seen_start_a", 11.5, mono=True)
text(gx, 472, "幻影首帧 / 截断残帧 / 模式中途进入 → 不比较", 10, fill=MUT)
text(gx, 490, "防护帧完整性，不防字节覆盖洞（见 1027v1-B）", 10, fill="#b45309")
arrow(cx, 360, cx, 410, flow=True)
arrow(gx, 360, gx, 410, color="#6b7280", sw=2, dash="5,3")
text((cx + gx) / 2, 400, "prev_xsum_a", 10.5, fill=MUT)
mx = W / 2 + 30
rect(mx - 190, 540, 380, 52, TEAL_L)
text(mx, 562, "match_eff_a = match_a & cmp_valid_a", 12.5, 700, mono=True)
text(mx, 582, "合法比较结果，四消费点唯一入口", 9.5, fill=MUT)
arrow(cx, 506, mx - 40, 540, flow=True)
arrow(gx, 506, mx + 40, 540, color="#6b7280", sw=2, dash="5,3")

# ---------------- Lane 4: commit & counters ----------------
text(40, 626, "④ 提交门控与计数", 13, 700, anchor="start")
by = 640
rect(80, by, 210, 72, "#ffffff")
text(185, by + 28, "match_cnt_a（1bit）", 12.5, 700, mono=True)
text(185, by + 48, "上一帧合法匹配标志", 10, fill=MUT)
rect(340, by, 250, 72, GREEN_L, stroke="#16a34a", sw=1.6, cls=None)  # update_en gate
text(465, by + 26, "update_en_a", 13.5, 800, "#166534", mono=True)
text(465, by + 46, "match_cnt_a & match_eff_a", 10.5, mono=True, fill="#166534")
text(465, by + 62, "→ shadow 整帧提交 active", 10, fill="#166534")
rect(660, by, 210, 72, "#ffffff")
text(765, by + 28, "unmatch_cnt_a（3bit）", 12, 700, mono=True)
text(765, by + 48, "合法 mismatch 连续计数", 10, fill=MUT)
rect(930, by, 250, 72, AMBER_L, stroke=AMBER_B)
text(1055, by + 28, "连续 5 次 → unlock_one_shot", 12, 700, "#c2410c")
text(1055, by + 48, "直写通路解锁（one-shot）", 10, fill="#c2410c")
arrow(mx, 592, mx, 610, color="#6b7280", sw=2, dash="5,3")
arrow(mx, 610, 465, 636, color="#6b7280", sw=2, dash="5,3")
arrow(mx, 610, 765, 636, color="#6b7280", sw=2, dash="5,3")
arrow(290, by + 36, 340, by + 36, flow=True)
arrow(870, by + 36, 930, by + 36, color="#b45309", sw=2)
text(990, 628, "match_eff_a=0 时计数", 9.5, fill=MUT)

# ---------------- fix callout ----------------
rect(80, 744, 1080, 92, AMBER_L, AMBER_B, 1.6)
diamond(100, 763, 8, "#c2410c")
text(118, 768, "1027v1-B 修复（2026-10-27，DV boundary_chip1 F30 暴露）", 13, 800, "#c2410c", anchor="start")
text(100, 790, "xdata_a 三元链曾漏写 5'h04 分支（落默认 DATA_C）→ 0x0A 三个月未进入运行 XOR：仅改 0x0A+陈旧校验的帧假匹配误提交（F30 实测），", 11, fill=INK, anchor="start")
text(100, 808, "改 0x0A+正确校验的帧假 mismatch（提交被阻+unmatch 污染）。补 (5'h04)?(DATA_C^DATA_D) 一行后，参与集恢复 0716v1_work 等价集（上图 ◆ 卡即修复点）。", 11, fill=INK, anchor="start")
text(100, 826, "同类错误六轴排查无其他问题；验证脚本 script/xcheck_1027v1_xdata_a.py / xcheck_1027v1_similar.py", 10, fill=MUT, anchor="start")

# ---------------- legend ----------------
L.append(f'<path d="M 80,858 L 130,858" stroke="{TEAL}" stroke-width="2.5" marker-end="url(#arr_{TEAL[1:]})"/>')
text(140, 862, "数据流（流光点=流向）", 10.5, fill=MUT, anchor="start")
L.append('<path d="M 330,858 L 380,858" stroke="#6b7280" stroke-width="2" stroke-dasharray="5,3" marker-end="url(#arr_6b7280)"/>')
text(390, 862, "控制/判据", 10.5, fill=MUT, anchor="start")
L.append(f'<rect x="500" y="850" width="18" height="12" fill="{TEAL_L}" stroke="#b45309" stroke-width="1.4" rx="3"/>')
text(526, 862, "修复点（呼吸高亮）", 10.5, fill=MUT, anchor="start")
L.append(f'<rect x="680" y="850" width="18" height="12" fill="{GREEN_L}" stroke="#16a34a" stroke-width="1.4" rx="3"/>')
text(706, 862, "提交门（呼吸）", 10.5, fill=MUT, anchor="start")
L.append(f'<rect x="840" y="850" width="18" height="12" fill="{AMBER_L}" stroke="{AMBER_B}" stroke-width="1.4" rx="3"/>')
text(866, 862, "mismatch / unlock 侧", 10.5, fill=MUT, anchor="start")
L.append(f'<rect x="1010" y="850" width="18" height="12" fill="{GRAY_L}" stroke="{BRD}" stroke-width="1.2" rx="3" stroke-dasharray="4,3"/>')
text(1036, 862, "gap（无参与字节）", 10.5, fill=MUT, anchor="start")

# ================= build static =================
def build_static():
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            + "\n".join(l for l in L if l) + "\n</svg>\n")


# ================= build anim =================
def build_anim():
    fx0, fx1, _ = FIX_RANGE
    lines = [l for l in L if l]
    # wrap fix card (from its rect through its note text) in breathing group
    lines[fx0:fx1] = ['<g class="chg">'] + lines[fx0:fx1] + ["</g>"]
    # update_en gate breathing: wrap by locating the gate rect + its 3 texts (they follow the match_cnt block)
    gi = next(i for i, l in enumerate(lines) if 'fill="' + GREEN_L + '"' in l and 'stroke="#16a34a"' in l)
    lines[gi:gi + 4] = ['<g class="gate">'] + lines[gi:gi + 4] + ["</g>"]
    style = ["<style>",
             ".chg { animation: chgPulse 2s ease-in-out infinite; }",
             "@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }",
             ".gate rect { animation: gatePulse 3.2s ease-in-out infinite; }",
             "@keyframes gatePulse { 0%,100% { stroke-opacity:1; } 50% { stroke-opacity:0.4; } }"]
    for n, (d, ln, col) in enumerate(FLOW):
        style.append(f'.flow{n} {{ stroke-dasharray: 7 {ln + 64}; animation: pkt{n} {(ln + 72) / 150:.2f}s linear infinite; }}')
        style.append(f'@keyframes pkt{n} {{ from {{ stroke-dashoffset: {ln + 72}; }} to {{ stroke-dashoffset: 0; }} }}')
    style.append("</style>")
    # duplicated flow paths appended near end (before </svg>)
    flow_paths = [f'<path class="flow{n}" d="{d}" fill="none" stroke="{TEAL}" stroke-width="2.5" stroke-linecap="round" opacity="0.9"/>'
                  for n, (d, _, _) in enumerate(FLOW)]
    # insert style after defs; flow paths before legend (painter: under texts is fine—they are paths in empty corridors)
    di = next(i for i, l in enumerate(lines) if l.strip() == "</defs>")
    lines[di + 1:di + 1] = style
    li = len(lines)
    lines[li:li] = flow_paths
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            + "\n".join(lines) + "\n</svg>\n")


st, an = build_static(), build_anim()
open(STATIC, "w", encoding="utf-8", newline="\n").write(st)
open(ANIM, "w", encoding="utf-8", newline="\n").write(an)

# ================= self-checks =================
NS = "{http://www.w3.org/2000/svg}"
ok = True


def tms(p):
    return Counter((e.text or "") for e in ET.parse(p).getroot().iter(NS + "text"))


try:
    ET.parse(STATIC); ET.parse(ANIM); print("[1] XML well-formed: OK")
except Exception as e:
    ok = False; print("[1] FAIL:", e)
if tms(STATIC) == tms(ANIM):
    print("[2] text multiset equal: OK")
else:
    ok = False; print("[2] FAIL")
if b"<script" not in open(ANIM, "rb").read():
    print("[3] no <script>: OK")
else:
    ok = False; print("[3] FAIL")
kf = an.count("@keyframes")
print(f"[4] keyframes present: {'OK' if kf >= 3 else 'FAIL'} ({kf})"); ok &= kf >= 3
print(f"[5] viewBox identical: {'OK' if f'viewBox=\"0 0 {W} {H}\"' in an and f'viewBox=\"0 0 {W} {H}\"' in st else 'FAIL'}")
cnt = (an.count('class="chg"'), an.count('class="gate"'), an.count('class="flow'))
print(f"[6] effect groups chg/gate/flow = {cnt} (expect 1/1/{len(FLOW)})")
ok &= cnt == (1, 1, len(FLOW))
print("RESULT:", "ALL OK" if ok else "FAIL")

# ymzhu 2026-10-27 19:32
