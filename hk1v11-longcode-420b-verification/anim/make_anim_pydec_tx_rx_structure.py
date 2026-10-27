#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_pydec_tx_rx_structure.py  (Motion Kit v2)

把 pydec_tx_rx_structure.svg 升级为 v2 纯 CSS in-SVG 动画：
- 入场编排（.row/.head，行序：标题0 → TX .2 → RX .45 → 离线 band .85 → 图例 1.1）
- 箭头自绘（.draw + pathLength=100：TX 内部 2↓、CHPI 蓝色串行 2 边、
  RX→脚本 3 箭头、离线 lane0→report 箭头；delay = 源面板 delay + 0.35）
- 数据列车（.flowdot：绿脚本链 3 边 ×2 包 0.7s，0.15s 相位递增；
  蓝 K 码对齐 2 边 ×2 包）
- 虚线行进（.fademarch：RTL 解码链虚线盒、紫色期望值连接器、
  绿色 lane0↓ 虚线、灰色"传统路径"）
- 英雄辉光（.glow-b TAP 徽章 / .glow-g ✅ verdict 盒）
- 呼吸（.breathe："dout_24b + 2-bit valid" 文本）

铁律：源 SVG 只读；数据/几何/颜色零改动；纯 CSS 无 <script>；kit CSS 逐字嵌入；
reduced-motion 媒体块原样保留。确定性、幂等、无第三方依赖。
"""
import re
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "pydec_tx_rx_structure.svg"
OUT = BASE / "anim" / "pydec_tx_rx_structure.svg"

# ---- Motion Kit v2 CSS（MOTION_KIT.md §2 逐字，勿改）----
KIT_CSS = """<style>
.row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.cellwave{animation:wave 3s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}
.march{animation:march 1.8s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.glow-b{animation:glowB 2.8s ease-in-out infinite}
@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}
.glow-g{animation:glowG 2.8s ease-in-out infinite}
@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}
.glow-o{animation:glowO 2.8s ease-in-out infinite}
@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}
</style>"""


def fmt(v):
    return f"{v:g}"


def add_attrs(line, attrs):
    s = line.rstrip()
    assert s.endswith("/>"), f"not self-closing: {s}"
    return s[:-2].rstrip() + " " + attrs + "/>"


def tag_draw(line, delay):
    return add_attrs(line, f'class="draw" pathLength="100" style="animation-delay:{fmt(delay)}s"')


def tag_cls(line, cls, delay):
    return add_attrs(line, f'class="{cls}" style="animation-delay:{fmt(delay)}s"')


def line_to_d(line):
    x1 = re.search(r'x1="([-\d.]+)"', line).group(1)
    y1 = re.search(r'y1="([-\d.]+)"', line).group(1)
    x2 = re.search(r'x2="([-\d.]+)"', line).group(1)
    y2 = re.search(r'y2="([-\d.]+)"', line).group(1)
    return f"M {x1} {y1} L {x2} {y2}"


def get_d(line):
    return re.search(r'd="([^"]+)"', line).group(1)


def flowdot(d, color, delay, dur=0.7, width="2.5"):
    g_open = f'<g class="fade" style="animation-delay:{fmt(delay)}s">'
    p = (f'<path class="flowdot" d="{d}" stroke="{color}" stroke-width="{width}" '
         f'pathLength="100" style="animation-duration:{fmt(dur)}s;animation-delay:{fmt(delay)}s"/>')
    return [g_open, p, "</g>"]


def build():
    raw = SRC.read_text(encoding="utf-8")
    assert "\r" not in raw, "源图应为 LF 行尾"
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    assert lines[0].startswith('<svg xmlns'), "line1 应为 <svg> 开标签"
    assert lines[1].lstrip().startswith("<style>text"), "line2 应为既有字体 <style>"
    assert lines[-1] == "</svg>", "末行应为 </svg>"

    def idx(prefix, start=0):
        for i in range(start, len(lines)):
            if lines[i].lstrip().startswith(prefix):
                return i
        raise AssertionError(f"anchor not found: {prefix!r}")

    # ---- 结构锚点（0 基）----
    i_title = idx("<text x=\"600\" y=\"40\"")            # 10
    i_tx = idx("<rect x=\"40\" y=\"100\"")               # 12
    i_ser1 = idx("<path d=\"M 396 292")                  # 29 蓝色串行 1
    i_ser2 = idx("<path d=\"M 396 304")                  # 30 蓝色串行 2
    i_rx = idx("<rect x=\"500\" y=\"100\"")              # 32
    i_rtl = idx("<rect x=\"524\" y=\"214\"")             # 40 RTL 虚线盒
    i_off = idx("<rect x=\"40\" y=\"480\"")              # 58
    i_leg = idx("<line x1=\"60\" y1=\"648\"")            # 83
    assert (i_title, i_tx, i_ser1, i_ser2, i_rx, i_rtl, i_off, i_leg) == \
           (10, 12, 29, 30, 32, 40, 58, 83), "源图结构与预期不符"

    i_tap_rect = idx("<rect x=\"784\" y=\"134\"")
    i_tap_text = next(i for i, l in enumerate(lines) if ">TAP<" in l)
    assert i_tap_rect + 1 == i_tap_text and i_rx < i_tap_rect < i_rtl
    i_vd_rect = idx("<rect x=\"470\" y=\"520\"")
    i_vd_text = next(i for i in range(i_off, len(lines)) if "long_pydec_report_lane0.md" in lines[i])
    assert i_vd_rect + 1 == i_vd_text and i_off < i_vd_rect < i_leg
    i_dout = next(i for i in range(i_rx, len(lines)) if "descramble_7b → dout_24b" in lines[i])  # breathe 目标文本
    assert i_rx < i_dout < i_rtl + 7 and i_dout > i_rtl   # 在 RTL 盒内

    # 箭头/连接器逐条规格：(行号, 内容前缀, 类型, delay)
    EDGES = [
        # TX 内部 2 ↓（含在箭头区，源面板 TX=0.2 → delay 0.55）
        (70, '<line x1="230" y1="188"', "draw", 0.55),
        (71, '<line x1="230" y1="264"', "draw", 0.55),
        # 灰色"传统路径"虚线
        (72, '<line x1="674" y1="192"', "march", 0.80),
        (73, '<text x="700" y="206"', "fade", 0.80),
        # RX→脚本 3 箭头（RX=0.45 → delay 0.8）
        (74, '<line x1="824" y1="160"', "draw", 0.80),
        (75, '<line x1="1003" y1="192"', "draw", 0.80),
        (76, '<line x1="1003" y1="276"', "draw", 0.80),
        # 离线 band 连接（0.85 → delay 1.2）
        (77, '<path d="M 214 424', "march", 1.20),      # 紫 dump→离线 rawbyte
        (78, '<path d="M 1003 364', "march", 1.20),     # 绿 lane0↓ 虚线
        (79, '<line x1="364" y1="552"', "march", 1.20), # 紫 rawbyte→report 期望值
        (80, '<text x="417" y="544"', "fade", 1.20),    # 期望值 标签
        (81, '<line x1="846" y1="552"', "draw", 1.20),  # lane0→report 实际值（实线）
        (82, '<text x="838" y="544"', "fade", 1.20),    # 实际值 标签
    ]
    for i, pref, _t, _d in EDGES:
        assert lines[i].lstrip().startswith(pref), f"edge anchor mismatch @line {i+1}: {lines[i]}"
    assert lines[i_rtl].find("stroke-dasharray") >= 0, "RTL 盒应为虚线"

    # ---- 数据列车边几何 ----
    green_edges = [line_to_d(lines[i]) for i in (74, 75, 76)]   # tap→脚本链 3 边
    blue_edges = [get_d(lines[i_ser1]), get_d(lines[i_ser2])]   # CHPI K 码对齐 2 边

    # ---- 组装 ----
    out = [lines[0], lines[1], KIT_CSS]
    # 保留源 <defs>（5 个箭头 marker）+ 全页白底 rect（v2.1：Qwen 交叉验证发现缺失 → 箭头端丢失）
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    d_end = next(i for i, l in enumerate(lines) if l.strip() == "</defs>")
    bg_end = next(i for i in range(d_end, d_end + 3) if 'fill="#ffffff"' in lines[i])
    out.extend(lines[2:bg_end + 1])

    def group(rng, cls, delay, extra=()):
        """extra: list of (start,end,mode,cls,gdelay) 嵌套子组（glow/breathe）。"""
        out.append(f'<g class="{cls}" style="animation-delay:{fmt(delay)}s">')
        stack = []
        i = rng[0]
        while i < rng[1]:
            # 组内单行 class 修改（如 RTL 虚线盒 fademarch）
            ln = lines[i]
            if i == i_rtl:
                ln = tag_cls(ln, "fademarch", 0.80)
            for gs, ge, gc, gd in extra:
                if i == gs:
                    out.append(f'<g class="{gc}" style="animation-delay:{fmt(gd)}s">')
                    stack.append(ge)
            out.append(ln)
            i += 1
            while stack and i >= stack[-1]:
                stack.pop()
                out.append("</g>")
        assert not stack
        out.append("</g>")

    group((i_title, i_title + 2), "head", 0)                       # 标题+副标题
    group((i_tx, i_ser1), "row", 0.20)                             # TX 面板
    # 蓝色 CHPI 串行 2 边 + 旋转标签（TX 0.2 → delay 0.55）
    out.append('<g class="fade" style="animation-delay:0.55s">')
    out.append(tag_draw(lines[i_ser1], 0.55))
    out.append(tag_draw(lines[i_ser2], 0.55))
    out.append(lines[i_ser2 + 1])                                  # rotate(-90) 标签
    out.append("</g>")
    group((i_rx, i_off), "row", 0.45,
          extra=[(i_tap_rect, i_tap_text + 1, "glow-b", 1.2),
                 (i_dout, i_dout + 1, "breathe", 0)])              # RX（TAP 辉光 + dout 呼吸）
    group((i_off, EDGES[0][0]), "row", 0.85,
          extra=[(i_vd_rect, i_vd_rect + 4, "glow-g", 1.9)])       # 离线 band（verdict 辉光）

    # 箭头区（保持原文档顺序）
    for i, _pref, kind, delay in EDGES:
        ln = lines[i]
        if kind == "draw":
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(tag_draw(ln, delay))
            out.append("</g>")
        elif kind == "march":
            out.append(tag_cls(ln, "fademarch", delay))
        else:
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(ln)
            out.append("</g>")

    # 数据列车：绿脚本链 3 边 ×2 包（0.8 起 0.15s 递增）；蓝 K 码 2 边 ×2 包（0.55/0.70 起）
    for k, d in enumerate(green_edges):
        base = 0.80 + 0.15 * k
        out.extend(flowdot(d, "#059669", base))
        out.extend(flowdot(d, "#059669", base + 0.35))
    for k, d in enumerate(blue_edges):
        base = 0.55 + 0.15 * k
        out.extend(flowdot(d, "#2563eb", base))
        out.extend(flowdot(d, "#2563eb", base + 0.35))

    group((i_leg, len(lines) - 1), "head", 1.10)                   # 底部图例
    out.append("</svg>")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-27 10:37
