#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_longcode_verification_architecture.py  (Motion Kit v2)

把 longcode_verification_architecture.svg 升级为 v2 纯 CSS in-SVG 动画：
- 入场编排（.row/.head，行序：标题0 → Test/Config .15 → TX .4 → RX .6 →
  Transaction .8 → 离线 band 1.15 → 版本条 1.5 → 图例 1.7）
- 箭头自绘（.draw + pathLength=100，delay = 源面板 delay + 0.35）
- 数据列车（.flowdot：蓝链 TX→RX 8 边 ×2 包；绿链离线 4 边 ×2 包，0.7s 周期，
  按边序 0.15s 递增相位）
- 虚线行进（.fademarch：紫色期望值/比对连接器、绿色 tap 虚线长边、橙色配置虚线）
- 英雄辉光（.glow-b TAP 徽章 / .glow-g ✅ verdict 盒）

铁律：源 SVG 只读；数据/几何/颜色零改动；纯 CSS 无 <script>；kit CSS 逐字嵌入；
reduced-motion 媒体块原样保留。确定性、幂等、无第三方依赖。
"""
import re
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "longcode_verification_architecture.svg"
OUT = BASE / "anim" / "longcode_verification_architecture.svg"

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
    """在自闭合标签 '/>' 前追加属性。"""
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
    """单个数据包：外层 .fade 负责 delay 前隐藏。"""
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
    i_tc = idx("<rect x=\"40\" y=\"88\"")                # 12
    i_tx = idx("<rect x=\"40\" y=\"192\"")               # 26
    i_tr = idx("<rect x=\"40\" y=\"504\"")               # 65
    i_rx = idx("<rect x=\"776\" y=\"192\"")              # 75
    i_off = idx("<rect x=\"40\" y=\"650\"")              # 100
    i_ver = idx("<rect x=\"40\" y=\"862\"")              # 124
    i_ar1 = idx("<line x1=\"375\" y1=\"174\"")           # 127
    i_leg = idx("<line x1=\"60\" y1=\"952\"")            # 149
    assert (i_title, i_tc, i_tx, i_tr, i_rx, i_off, i_ver, i_ar1, i_leg) == \
           (10, 12, 26, 65, 75, 100, 124, 127, 149), "源图结构与预期不符"

    # TAP 徽章（RX 组内）与 ✅ verdict 盒（离线组内）
    i_tap_rect = idx("<rect x=\"1072\" y=\"232\"")
    i_tap_text = next(i for i, l in enumerate(lines) if ">TAP<" in l)
    assert i_tap_rect + 1 == i_tap_text and i_rx < i_tap_rect < i_off
    i_vd_rect = idx("<rect x=\"566\" y=\"768\"")
    i_vd_text = next(i for i in range(i_off, len(lines)) if "long_pydec_report_lane0.md" in lines[i])
    assert i_vd_rect + 1 == i_vd_text and i_off < i_vd_rect < i_ver

    # 箭头区逐条规格：(行号, 内容前缀, 类型, delay)
    ARROWS = [
        (127, '<line x1="375" y1="174"', "draw", 0.50),   # Test/Config → TX
        (128, '<line x1="660" y1="174"', "draw", 0.50),   # Test/Config → TX 侧
        (129, '<line x1="955" y1="174"', "march", 0.50),  # 橙色配置虚线
        (130, '<line x1="540" y1="320"', "draw", 0.75),   # TX 内部 → long_encoding
        (131, '<line x1="375" y1="484"', "draw", 0.75),   # TX → Transaction
        (132, '<line x1="364" y1="562"', "draw", 1.15),   # transaction → driver
        (133, '<path d="M 712 562', "draw", 1.15),        # 蓝色串行链路 driver→RX
        (134, '<text transform="rotate(-90 748', "fade", 1.15),  # 串行链路标签
        (135, '<line x1="968" y1="288"', "draw", 0.95),   # RX 内部 ↓ ×4
        (136, '<line x1="968" y1="358"', "draw", 0.95),
        (137, '<line x1="968" y1="428"', "draw", 0.95),
        (138, '<line x1="968" y1="498"', "draw", 0.95),
        (139, '<path d="M 1136 257', "march", 0.95),      # 绿色 tap 虚线长边
        (140, '<text x="700" y="624"', "fade", 0.95),     # tap 标签
        (141, '<path d="M 204 610', "march", 1.50),       # 紫色期望值虚线
        (142, '<path d="M 204 626 A', "fade", 1.50),      # 紫色小弧
        (143, '<line x1="294" y1="718"', "draw", 1.50),   # 离线链 4 箭头
        (144, '<line x1="526" y1="718"', "draw", 1.50),
        (145, '<line x1="808" y1="718"', "draw", 1.50),
        (146, '<line x1="944" y1="748"', "draw", 1.50),
        (147, '<line x1="344" y1="792"', "march", 1.50),  # 紫色逐区域 diff
        (148, '<text x="455" y="784"', "fade", 1.50),     # diff 标签
    ]
    for i, pref, _t, _d in ARROWS:
        assert lines[i].lstrip().startswith(pref), f"arrow anchor mismatch @line {i+1}: {lines[i]}"

    # ---- 数据列车边几何 ----
    # 蓝链：build→pad / pad→encode / encode→long_encoding / 串行链路 / RX 内部 4 边
    blue_edges = [
        "M 450 268 L 450 278",                       # build_bit_stream → pad_bit_stream
        "M 450 320 L 450 330",                       # pad_bit_stream → encode_with_70b_alignment
        line_to_d(lines[130]),                       # encode → long_encoding（沿源边）
        get_d(lines[133]),                           # 串行链路 → CHPI_KCODE_ALIGN
        line_to_d(lines[135]),                       # KCODE_ALIGN → long_decoding_top
        line_to_d(lines[136]),                       # long_decoding_top → decoder_7b
        line_to_d(lines[137]),                       # decoder_7b → descramble_7b
        line_to_d(lines[138]),                       # descramble_7b → dout
    ]
    # 绿链离线：tap_debug → dap → decode_dap.py → pydec → report
    green_edges = [line_to_d(lines[i]) for i in (143, 144, 145, 146)]

    # ---- 组装 ----
    out = [lines[0], lines[1], KIT_CSS]
    # 保留源 <defs>（5 个箭头 marker）+ 全页白底 rect（v2.1：Qwen 交叉验证发现缺失 → 箭头端丢失）
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    d_end = next(i for i, l in enumerate(lines) if l.strip() == "</defs>")
    bg_end = next(i for i in range(d_end, d_end + 3) if 'fill="#ffffff"' in lines[i])
    out.extend(lines[2:bg_end + 1])

    def group(rng, cls, delay, glow=()):
        """rng: [start,end) 0 基；glow: list of (start,end,cls,gdelay) 嵌套辉光组。"""
        out.append(f'<g class="{cls}" style="animation-delay:{fmt(delay)}s">')
        glow_stack = []
        i = rng[0]
        while i < rng[1]:
            for gs, ge, gc, gd in glow:
                if i == gs:
                    out.append(f'<g class="{gc}" style="animation-delay:{fmt(gd)}s">')
                    glow_stack.append(ge)
            out.append(lines[i])
            i += 1
            while glow_stack and i >= glow_stack[-1]:
                glow_stack.pop()
                out.append("</g>")
        assert not glow_stack
        out.append("</g>")

    group((i_title, i_title + 2), "head", 0)                       # 标题+副标题
    group((i_tc, i_tx), "row", 0.15)                               # Test/Config
    group((i_tx, i_tr), "row", 0.40)                               # TX
    group((i_tr, i_rx), "row", 0.80)                               # Transaction/Driver
    group((i_rx, i_off), "row", 0.60,
          glow=[(i_tap_rect, i_tap_text + 1, "glow-b", 1.2)])      # RX（含 TAP 辉光）
    group((i_off, i_ver), "row", 1.15,
          glow=[(i_vd_rect, i_vd_rect + 3, "glow-g", 1.9)])        # 离线 band（含 verdict 辉光）
    group((i_ver, i_ver + 3), "row", 1.50)                         # 版本条

    # 箭头区（保持原文档顺序；draw 元素外套 .fade 负责 delay 前隐藏）
    for i, _pref, kind, delay in ARROWS:
        ln = lines[i]
        if kind == "draw":
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(tag_draw(ln, delay))
            out.append("</g>")
        elif kind == "march":
            out.append(tag_cls(ln, "fademarch", delay))
        else:  # fade 文本标签
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(ln)
            out.append("</g>")

    # 数据列车（蓝 8 边 ×2 包，相位 0.15s 递增；绿 4 边 ×2 包）
    for k, d in enumerate(blue_edges):
        base = 1.00 + 0.15 * k
        out.extend(flowdot(d, "#2563eb", base))
        out.extend(flowdot(d, "#2563eb", base + 0.35))
    for k, d in enumerate(green_edges):
        base = 1.60 + 0.15 * k
        out.extend(flowdot(d, "#059669", base))
        out.extend(flowdot(d, "#059669", base + 0.35))

    group((i_leg, len(lines) - 1), "head", 1.70)                   # 底部图例
    out.append("</svg>")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-27 10:37
