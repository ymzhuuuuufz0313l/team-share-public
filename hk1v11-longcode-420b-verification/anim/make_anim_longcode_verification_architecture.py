#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_longcode_verification_architecture.py  (Motion Kit v4 整体重写)

MOTION_KIT.md §6.1 规格（1200x980 六面板架构图）：
- 入场编排 §5：容器→内容→箭头；箭头 delay = max(两端面板 row delay)+0.55s
  （修 v2 +0.35s 悬浮箭头缺陷）。行序：标题0 → Test/Config .15 → TX .40 →
  RX .60 → Transaction .80 → 离线 band 1.15 → 版本条 1.50 → 图例 1.70。
- 稳态族（3 族）：
  * 列车 train：蓝链 8 边（build_bit_stream→pad→encode→long_encoding→
    CHPI_KCODE_ALIGN + RX 内部链 4 边）每边 2 包 + flowtail 拖尾，0.7s/边，
    按边序错 phase；绿链离线 4 边每边 3 包 + 拖尾（2026-10-28 晚动效加密：
    2→3 包，更明显的"列车"），duration 1.4s（×2 慢速支路对比）。
  * 脉冲 pulse：TAP 徽章 pulse-b(-1.4s)；✅ verdict 盒 pulse-t(-0.7s)。
  * 生长 dashgrow：紫色"期望值/比对"虚线连接器 2 条（相位错开）。
- march 辅助（不计数）：橙色配置虚线、绿色 tap 长虚线。
- cellwave：§6.1 可选项——TX 面板 K2/K3/K4 在源图中无独立 chip（均为整盒文字），
  剥离会破坏 row 组边界 → 按"不好剥离就跳过"跳过。
铁律：源 SVG 只读；text/几何/颜色零改动；纯 CSS in-SVG；kit CSS §2 逐字；
保留源 defs + 背景 rect + 第 2 行字体 style；reduced-motion 块原样；
确定性幂等；零第三方依赖。
"""
import re
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "longcode_verification_architecture.svg"
OUT = BASE / "anim" / "longcode_verification_architecture.svg"

# ---- Motion Kit v4 CSS（MOTION_KIT.md §2 逐字，勿改）----
KIT_CSS = """<style>
.row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}
.pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}
@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}
.pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}
@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}
.sweepband{opacity:.85;animation:sweepMove 8s linear infinite}
@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}
.dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}
@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}
.march{animation:march 1.5s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.cellwave{animation:wave 2.6s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}
</style>"""


def fmt(v):
    return f"{v:g}"


def add_attrs(line, attrs):
    """在自闭合标签 '/>' 前追加属性（原属性零改动）。"""
    s = line.rstrip()
    assert s.endswith("/>"), f"not self-closing: {s}"
    return s[:-2].rstrip() + " " + attrs + "/>"


def tag_draw(line, delay):
    return add_attrs(line, f'class="draw" pathLength="100" style="animation-delay:{fmt(delay)}s"')


def line_to_d(line):
    x1 = re.search(r'x1="([-\d.]+)"', line).group(1)
    y1 = re.search(r'y1="([-\d.]+)"', line).group(1)
    x2 = re.search(r'x2="([-\d.]+)"', line).group(1)
    y2 = re.search(r'y2="([-\d.]+)"', line).group(1)
    return f"M {x1} {y1} L {x2} {y2}"


def get_d(line):
    return re.search(r'd="([^"]+)"', line).group(1)


def train_edge(d, color, dur, phase, enter, packets=2):
    """一条边的数据列车：packets 包（整周期均布 = 错相位）+ 各自 flowtail 拖尾，
    外包 .fade 负责入场前隐藏。绿链离线 3 包（2026-10-28 加密）。"""
    out = [f'<g class="fade" style="animation-delay:{fmt(enter)}s">']
    for p in range(packets):
        dl = phase - p * dur / float(packets)
        out.append(f'<path class="flowtail" d="{d}" stroke="{color}" pathLength="100" '
                   f'style="animation-duration:{fmt(dur)}s;animation-delay:{fmt(dl)}s"/>')
        out.append(f'<path class="flowdot" d="{d}" stroke="{color}" pathLength="100" '
                   f'style="animation-duration:{fmt(dur)}s;animation-delay:{fmt(dl)}s"/>')
    out.append("</g>")
    return out


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

    # ---- 箭头/连接器逐条规格（0 基行号, 前缀, 类型, 入场 delay）----
    # delay = max(两端面板 row delay) + 0.55（§5 铁律）
    ARROWS = [
        (127, '<line x1="375" y1="174"', "draw", 0.95),   # Test/Config → TX（max .15/.40 +.55）
        (128, '<line x1="660" y1="174"', "draw", 0.95),   # Test/Config → TX 侧
        (129, '<line x1="955" y1="174"', "march", 1.15),  # 橙色配置虚线 → RX（max .15/.60）
        (130, '<line x1="540" y1="320"', "draw", 0.95),   # TX 内部 encode → long_encoding
        (131, '<line x1="375" y1="484"', "draw", 1.35),   # TX → Transaction（max .40/.80）
        (132, '<line x1="364" y1="562"', "draw", 1.35),   # transaction → driver
        (133, '<path d="M 712 562', "draw", 1.35),        # 蓝串行链路 driver → RX（max .80/.60）
        (134, '<text transform="rotate(-90 748', "fade", 1.35),  # 串行链路标签
        (135, '<line x1="968" y1="288"', "draw", 1.15),   # RX 内部 ↓ ×4（.60+.55）
        (136, '<line x1="968" y1="358"', "draw", 1.15),
        (137, '<line x1="968" y1="428"', "draw", 1.15),
        (138, '<line x1="968" y1="498"', "draw", 1.15),
        (139, '<path d="M 1136 257', "march", 1.70),      # 绿色 tap 虚线长边（max .60/1.15）
        (140, '<text x="700" y="624"', "fade", 1.70),     # tap 标签
        (141, '<path d="M 204 610', "grow", 1.70),        # 紫色期望值虚线 → dashgrow
        (142, '<path d="M 204 626 A', "fade", 1.50),      # 紫色小弧（12px，dashgrow 会糊 → fade）
        (143, '<line x1="294" y1="718"', "draw", 1.70),   # 离线链 4 箭头（1.15+.55）
        (144, '<line x1="526" y1="718"', "draw", 1.70),
        (145, '<line x1="808" y1="718"', "draw", 1.70),
        (146, '<line x1="944" y1="748"', "draw", 1.70),
        (147, '<line x1="344" y1="792"', "grow", 1.70),   # 紫色逐区域 diff → dashgrow
        (148, '<text x="455" y="784"', "fade", 1.70),     # diff 标签
    ]
    for i, pref, _t, _d in ARROWS:
        assert lines[i].lstrip().startswith(pref), f"arrow anchor mismatch @line {i+1}: {lines[i]}"

    # ---- 列车边几何 ----
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
    blue_enter = [0.95, 0.95, 0.95, 1.35, 1.15, 1.15, 1.15, 1.15]
    green_edges = [line_to_d(lines[i]) for i in (143, 144, 145, 146)]
    green_enter = [1.70] * 4

    # ---- 组装 ----
    out = [lines[0], lines[1]] + KIT_CSS.split("\n")
    # 保留源 <defs>（5 个箭头 marker）+ 全页白底 rect（铁律 §0.4）
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    d_end = next(i for i, l in enumerate(lines) if l.strip() == "</defs>")
    bg_end = next(i for i in range(d_end, d_end + 3) if 'fill="#ffffff"' in lines[i])
    out.extend(lines[2:bg_end + 1])

    def group(rng, cls, delay, pulse=()):
        """rng: [start,end) 0 基；pulse: list of (start,end,cls,gdelay) 嵌套脉冲组。"""
        out.append(f'<g class="{cls}" style="animation-delay:{fmt(delay)}s">')
        stack = []
        i = rng[0]
        while i < rng[1]:
            for gs, ge, gc, gd in pulse:
                if i == gs:
                    out.append(f'<g class="{gc}" style="animation-delay:{fmt(gd)}s">')
                    stack.append(ge)
            out.append(lines[i])
            i += 1
            while stack and i >= stack[-1]:
                stack.pop()
                out.append("</g>")
        assert not stack
        out.append("</g>")

    group((i_title, i_title + 2), "head", 0)                        # 标题+副标题
    group((i_tc, i_tx), "row", 0.15)                                # Test/Config
    group((i_tx, i_tr), "row", 0.40)                                # TX
    group((i_tr, i_rx), "row", 0.80)                                # Transaction/Driver
    group((i_rx, i_off), "row", 0.60,
          pulse=[(i_tap_rect, i_tap_text + 1, "pulse-b", -1.4)])    # RX（TAP 徽章脉冲）
    group((i_off, i_ver), "row", 1.15,
          pulse=[(i_vd_rect, i_vd_rect + 3, "pulse-t", -0.7)])      # 离线 band（verdict 脉冲）
    group((i_ver, i_ver + 3), "row", 1.50)                          # 版本条

    # 箭头/连接器区（保持原文档顺序；一次性外层 .fade 负责入场前隐藏）
    for i, _pref, kind, delay in ARROWS:
        ln = lines[i]
        if kind == "draw":
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(tag_draw(ln, delay))
            out.append("</g>")
        elif kind == "march":
            phase = -0.75 if i == 139 else 0.0
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(add_attrs(ln, f'class="march" style="animation-delay:{fmt(phase)}s"'))
            out.append("</g>")
        elif kind == "grow":
            phase = -1.3 if i == 141 else 0.0  # 两条紫色生长虚线相位错开
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(add_attrs(ln, f'class="dashgrow" style="animation-delay:{fmt(phase)}s"'))
            out.append("</g>")
        else:  # fade 文本标签
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(ln)
            out.append("</g>")

    # 数据列车：蓝链 8 边（0.7s，-0.1s/边错 phase）；绿链 4 边（1.4s 慢速，-0.2s/边，
    # 每边 3 包 = 更明显的慢速列车）
    for k, (d, enter) in enumerate(zip(blue_edges, blue_enter)):
        out.extend(train_edge(d, "#2563eb", 0.7, -0.1 * k, enter))
    for k, (d, enter) in enumerate(zip(green_edges, green_enter)):
        out.extend(train_edge(d, "#059669", 1.4, -0.2 * k, enter, packets=3))

    group((i_leg, len(lines) - 1), "head", 1.70)                    # 底部图例
    out.append("</svg>")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-28 19:06
