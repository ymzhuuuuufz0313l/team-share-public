#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_pydec_tx_rx_structure.py  (Motion Kit v4 整体重写)

MOTION_KIT.md §6.2 规格（1200x680 TX/RX + 离线比对 band）：
- 入场编排 §5：标题0 → TX .20 → RX .45 → 离线 band .85 → 图例 1.5；
  箭头 delay = max(两端面板)+0.55s（修 v2 悬浮箭头）。
- 稳态族（4 族 + breathe 辅助；2026-10-28 晚动效加密 round 新增生长族）：
  * 列车 train：绿脚本链 3 边（tap_debug→decode_dap→pydec→…）每边 2 包+flowtail
    拖尾，0.7s；蓝 K 码对齐（CHPI 串行）2 边每边 2 包。
  * 脉冲 pulse：TAP 徽章 pulse-b(-1.4s)；✅ verdict 盒 pulse-t(-0.7s)。
  * 扫光 sweepband：离线比对 band 区域 1 处（§4 配方：defs 渐变+clipPath，
    P=区域宽+240，X0=区域左-0.54P 保证 t=0 光带完全在区域左侧、8s 无缝左→右扫）。
  * 生长 dashgrow（新）：紫色"期望值"链 2 条虚线连接器（dump↓ 3.2s/-1.6s、
    rawbyte→report 期望值 2.8s/-0.5s）+ RTL 虚线盒边（3.0s/-1.0s）持续生长
    回卷，相位错开；"实际值"连线为实线（draw）→ dashgrow 会把实线伪造成虚线，
    按"dashgrow 只能用在既有虚线上"放弃（caveat）。
  * breathe 辅助（不计数）："dout_24b + 2-bit valid" 文本。
- march 辅助（不计数，缩减）：灰色"传统路径"、绿 lane0↓（实际值侧保持行进，
  与期望值侧"生长"形成对照）。
铁律：源 SVG 只读；text/几何/颜色零改动；纯 CSS in-SVG；kit CSS §2 逐字；
保留源 defs + 背景 rect + 第 2 行字体 style；reduced-motion 块原样；
确定性幂等；零第三方依赖。
"""
import re
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "pydec_tx_rx_structure.svg"
OUT = BASE / "anim" / "pydec_tx_rx_structure.svg"

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

# ---- 扫光带几何（§4 配方）：离线比对 band rect x=40 y=480 w=1120 h=130 ----
SW_L, SW_Y, SW_W, SW_H = 40, 480, 1120, 130
SW_P = SW_W + 240                                   # P = 区域宽 + 240 = 1360
SW_X0 = SW_L - 0.54 * SW_P                          # -694.4：t=0 光带右缘恰在区域左缘
SW_DEFS = f"""    <linearGradient id="sweepG-1" gradientUnits="userSpaceOnUse" x1="{SW_X0:g}" y1="0" x2="{SW_X0 + SW_P:g}" y2="0">
      <stop offset="0" stop-color="rgba(180,83,9,0)"/>
      <stop offset="0.46" stop-color="rgba(180,83,9,0)"/>
      <stop offset="0.5" stop-color="rgba(180,83,9,.3)"/>
      <stop offset="0.54" stop-color="rgba(180,83,9,0)"/>
      <stop offset="1" stop-color="rgba(180,83,9,0)"/>
    </linearGradient>
    <clipPath id="sweepC-1"><rect x="{SW_L}" y="{SW_Y}" width="{SW_W}" height="{SW_H}"/></clipPath>"""
SW_BAND = (f'<g clip-path="url(#sweepC-1)"><rect class="sweepband" x="{SW_X0:g}" y="{SW_Y}" '
           f'width="{SW_P:g}" height="{SW_H}" fill="url(#sweepG-1)" style="--sweepP:{SW_P:g}px"/></g>')


def fmt(v):
    return f"{v:g}"


def add_attrs(line, attrs):
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


def train_edge(d, color, dur, phase, enter, tail=True):
    """数据列车：2 包（错半周期），tail=True 时每包带 flowtail 拖尾；外包 .fade 隐藏到入场。"""
    out = [f'<g class="fade" style="animation-delay:{fmt(enter)}s">']
    for p in (0, 1):
        dl = phase - p * dur / 2.0
        if tail:
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
    i_dout = next(i for i in range(i_rx, len(lines)) if "descramble_7b → dout_24b" in lines[i])
    assert i_rtl < i_dout < i_rtl + 7                    # breathe 目标文本在 RTL 盒内
    assert lines[i_rtl].find("stroke-dasharray") >= 0, "RTL 盒应为虚线"

    # ---- 箭头/连接器逐条规格（0 基行号, 前缀, 类型, 入场 delay）----
    # dashgrow 规格（2026-10-28 加密）：紫期望值链 2 条，duration 2.8/3.2s 相位错开
    GROW_SPEC = {77: (3.2, -1.6), 79: (2.8, -0.5)}
    EDGES = [
        # TX 内部 2 ↓（TX=.20 → delay .75）
        (70, '<line x1="230" y1="188"', "draw", 0.75),
        (71, '<line x1="230" y1="264"', "draw", 0.75),
        # 灰色"传统路径"虚线（RX=.45 → 1.0）
        (72, '<line x1="674" y1="192"', "march", 1.00),
        (73, '<text x="700" y="206"', "fade", 1.00),
        # RX→脚本 3 箭头（RX=.45 → 1.0）
        (74, '<line x1="824" y1="160"', "draw", 1.00),
        (75, '<line x1="1003" y1="192"', "draw", 1.00),
        (76, '<line x1="1003" y1="276"', "draw", 1.00),
        # 离线 band 连接（band=.85 → 1.4）
        (77, '<path d="M 214 424', "grow", 1.40),       # 紫 dump → 离线 rawbyte（虚线生长）
        (78, '<path d="M 1003 364', "march", 1.40),     # 绿 lane0 ↓ 虚线
        (79, '<line x1="364" y1="552"', "grow", 1.40),  # 紫 rawbyte→report 期望值（虚线生长）
        (80, '<text x="417" y="544"', "fade", 1.40),    # 期望值 标签
        (81, '<line x1="846" y1="552"', "draw", 1.40),  # lane0→report 实际值（实线）
        (82, '<text x="838" y="544"', "fade", 1.40),    # 实际值 标签
    ]
    for i, pref, _t, _d in EDGES:
        assert lines[i].lstrip().startswith(pref), f"edge anchor mismatch @line {i+1}: {lines[i]}"

    # ---- 列车边几何 ----
    green_edges = [line_to_d(lines[i]) for i in (74, 75, 76)]   # tap→脚本链 3 边
    blue_edges = [get_d(lines[i_ser1]), get_d(lines[i_ser2])]   # CHPI K 码对齐 2 边

    # ---- 组装 ----
    out = [lines[0], lines[1]] + KIT_CSS.split("\n")
    # 保留源 <defs>（5 个箭头 marker；末尾追加扫光渐变+clipPath）+ 全页白底 rect
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    d_end = next(i for i, l in enumerate(lines) if l.strip() == "</defs>")
    bg_end = next(i for i in range(d_end, d_end + 3) if 'fill="#ffffff"' in lines[i])
    out.extend(lines[2:d_end])
    out.extend(SW_DEFS.split("\n"))
    out.extend(lines[d_end:bg_end + 1])

    def group(rng, cls, delay, nested=(), insert_after=None, replace=None):
        """rng [start,end)；nested: (start,end,cls,gdelay)；insert_after: (idx, lines)；
        replace: {idx: lines}（如 RTL 虚线盒 march 改造）。"""
        out.append(f'<g class="{cls}" style="animation-delay:{fmt(delay)}s">')
        stack = []
        i = rng[0]
        while i < rng[1]:
            for gs, ge, gc, gd in nested:
                if i == gs:
                    out.append(f'<g class="{gc}" style="animation-delay:{fmt(gd)}s">')
                    stack.append(ge)
            if replace and i in replace:
                out.extend(replace[i])
            else:
                out.append(lines[i])
            if insert_after and i == insert_after[0]:
                out.extend(insert_after[1])
            i += 1
            while stack and i >= stack[-1]:
                stack.pop()
                out.append("</g>")
        assert not stack
        out.append("</g>")

    group((i_title, i_title + 2), "head", 0)                        # 标题+副标题
    group((i_tx, i_ser1), "row", 0.20)                              # TX 面板
    # 蓝色 CHPI 串行 2 边 + 旋转标签（TX .20 / RX .45 → delay 1.0）
    out.append('<g class="fade" style="animation-delay:1s">')
    out.append(tag_draw(lines[i_ser1], 1.0))
    out.append(tag_draw(lines[i_ser2], 1.0))
    out.append(lines[i_ser2 + 1])                                   # rotate(-90) 标签
    out.append("</g>")
    group((i_rx, i_off), "row", 0.45,                               # RX 面板
          nested=[(i_tap_rect, i_tap_text + 1, "pulse-b", -1.4),
                  (i_dout, i_dout + 1, "breathe", 0)],
          replace={i_rtl: [
              '<g class="fade" style="animation-delay:1s">',
              add_attrs(lines[i_rtl], 'class="dashgrow" style="animation-duration:3s;'
                                       'animation-delay:-1s"'),
              "</g>"]})
    group((i_off, EDGES[0][0]), "row", 0.85,                        # 离线 band（面板底色之上、
          nested=[(i_vd_rect, i_vd_rect + 4, "pulse-t", -0.7)],     # 内容之下插扫光带）
          insert_after=(i_off, SW_BAND.split("\n")))

    # 箭头/连接器区（保持原文档顺序）
    for i, _pref, kind, delay in EDGES:
        ln = lines[i]
        if kind == "draw":
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(tag_draw(ln, delay))
            out.append("</g>")
        elif kind == "march":
            phase = -0.5  # 绿 lane0 ↓（实际值侧行进，与期望值侧生长对照）
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(add_attrs(ln, f'class="march" style="animation-delay:{fmt(phase)}s"'))
            out.append("</g>")
        elif kind == "grow":
            gdur, gdl = GROW_SPEC[i]
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(add_attrs(ln, f'class="dashgrow" style="animation-duration:{fmt(gdur)}s;'
                                     f'animation-delay:{fmt(gdl)}s"'))
            out.append("</g>")
        else:
            out.append(f'<g class="fade" style="animation-delay:{fmt(delay)}s">')
            out.append(ln)
            out.append("</g>")

    # 数据列车：绿脚本链 3 边（2 包+拖尾 0.7s，-0.1s/边）；蓝 K 码 2 边（2 包）
    for k, d in enumerate(green_edges):
        out.extend(train_edge(d, "#059669", 0.7, -0.1 * k, 1.0))
    for k, d in enumerate(blue_edges):
        out.extend(train_edge(d, "#2563eb", 0.7, -0.1 * k, 1.0, tail=False))

    group((i_leg, len(lines) - 1), "head", 1.50)                    # 底部图例
    out.append("</svg>")

    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-28 19:06
