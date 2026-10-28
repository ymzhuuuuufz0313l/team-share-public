#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_8b10b_vs_420b.py  (Motion Kit v4 整体重写)

MOTION_KIT.md §6.3 规格（1400x1210 双列 8B/10B vs 420B 对比图）：
- 入场编排 §5：标题(0) → 左列盒自上而下 0.15 起步进 0.12（Test .15 / seq .27 /
  transaction .39 / driver .51 / DUT .63 / 线上验证 .75）→ 右列 0.30 起步进 0.12
  （.30/.42/.54/.66/.78/.90/1.02）→ 底部对比表 表头 1.4 + 13 数据行 1.45 起步进 0.04。
- draw：两列 spine 箭头逐段（左 0.82+0.12e、右 0.97+0.12e；
  delay = max(两端盒 row delay)+0.55）。源图无横向对比箭头 → §6.3 的
  "横向对比箭头"不适用（caveat）。
- 稳态族（3 族；2026-10-28 晚动效加密：行波提速 + 列车加包）：
  * 列车 train（双列赛跑）：左列 spine 5 边每边 3 包+flowtail（整周期均布），
    stroke 蓝 #1d4ed8；右列同参数整体 phase +0.35s，stroke 琥珀 #b45309。
  * 行波 cellwave：两列全部 5+5 个 chip 单元格（源图无更多 bit 格，"扩到全部
    bit 格"已满足）自上而下 0.07s/格（加密 0.1→0.07，落在 0.06~0.08 档），
    右列整体 +1.3s（半周期）。
  * 脉冲 pulse：左"线上数据验证"盒 pulse(-1.4s) / 右"线上数据验证（0717 新增）"盒
    pulse-t(-0.7s)（源图无独立"编码效率/编码率"盒 → 选 2 个 verdict 盒，caveat）。
- 不加 breathe；源图无虚线 → 无 march。
铁律：源 SVG 只读；text/几何/颜色零改动；纯 CSS in-SVG；kit CSS §2 逐字；
保留源 defs + 背景 rect + 第 2 行字体 style；reduced-motion 块原样；
确定性幂等；零第三方依赖。
"""
import re
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "8b10b_vs_420b_architecture.svg"
OUT = BASE / "anim" / "8b10b_vs_420b_architecture.svg"

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

# spine 箭头几何（y 区段，两列相同）：段长 16
SPINE_Y = [(174, 190), (316, 332), (392, 408), (464, 480), (558, 574)]
FLOW_PERIOD = 0.7       # 每段列车周期
FLOW_EDGE_STEP = 0.11   # 相邻段 phase 差（段间接续）
FLOW_PACKETS = 3        # 每段 3 包（2026-10-28 加密 2→3），整周期均布
RIGHT_PHASE = 0.35      # 右列整体相位偏移（双列赛跑）
CW_STEP = 0.07          # cellwave 0.07s/格（2026-10-28 加密 0.1→0.07，0.06~0.08 档）
CW_RIGHT_PHASE = 1.3    # 右列行波偏移半周期（cellwave 默认周期 2.6s）
# draw delay = max(两端盒 row delay) + 0.55（§5 铁律）
LEFT_DRAW = [0.82, 0.94, 1.06, 1.18, 1.30]    # 盒 .15/.27/.39/.51/.63/.75
RIGHT_DRAW = [0.97, 1.09, 1.21, 1.33, 1.45]   # 盒 .30/.42/.54/.66/.78/.90


def fmt(v):
    return f"{v:g}"


def tag_draw(line: str, delay: float) -> str:
    """给实线箭头 <line> 加 .draw + pathLength + delay（原属性零改动）。"""
    assert line.rstrip().endswith("/>") and "<line" in line, f"非 line 元素: {line}"
    return line.rstrip()[:-2] + f' class="draw" pathLength="100" style="animation-delay:{fmt(delay)}s"/>'


def train_edge(x, y0, y1, color, phase, enter):
    """一段 spine 的数据列车：3 包（整周期均布）+ flowtail 拖尾，外包 .fade 到入场才显现。"""
    d = f"M {x} {y0} L {x} {y1}"
    out = [f'<g class="fade" style="animation-delay:{fmt(enter)}s">']
    for p in range(FLOW_PACKETS):
        dl = phase - p * (FLOW_PERIOD / float(FLOW_PACKETS))
        out.append(f'<path class="flowtail" d="{d}" stroke="{color}" pathLength="100" '
                   f'style="animation-duration:{fmt(FLOW_PERIOD)}s;animation-delay:{fmt(dl)}s"/>')
        out.append(f'<path class="flowdot" d="{d}" stroke="{color}" pathLength="100" '
                   f'style="animation-duration:{fmt(FLOW_PERIOD)}s;animation-delay:{fmt(dl)}s"/>')
    out.append("</g>")
    return out


def build():
    raw = SRC.read_text(encoding="utf-8")
    assert "\r" not in raw, "源图应为 LF 行尾"
    lines = raw.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    L = lines  # 0 基；文件第 n 行 = L[n-1]

    # ---- 结构断言（确定性前提）----
    assert L[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert "font-family" in L[1], "line2 应为字体 <style>"
    assert L[174].strip() == "</svg>", "末行应为 </svg>"
    assert ">8B/10B vs 420B 长编码" in L[10], "line11 应为标题"
    assert "0717v1 修正" in L[11], "line12 应为副标题"
    assert L[2].strip() == "<defs>", "line3 应为 <defs>"
    assert L[8].strip() == "</defs>", "line9 应为 </defs>"
    assert L[9].lstrip().startswith('<rect width="1400"'), "line10 应为白底 rect"
    assert L[12].startswith('<rect x="40" y="88" width="640"'), "line13 左列容器"
    assert L[43].startswith('<rect x="720" y="88" width="640"'), "line44 右列容器"
    for k, (y0, y1) in zip(range(78, 83), SPINE_Y):
        assert L[k] == f'<line x1="360" y1="{y0}" x2="360" y2="{y1}" stroke="#2563eb" stroke-width="1.5" marker-end="url(#ar-blue)"/>', f"左箭头 line{k+1}"
    for k, (y0, y1) in zip(range(83, 88), SPINE_Y):
        assert L[k] == f'<line x1="1040" y1="{y0}" x2="1040" y2="{y1}" stroke="#2563eb" stroke-width="1.5" marker-end="url(#ar-blue)"/>', f"右箭头 line{k+1}"
    assert L[88].startswith('<rect x="40" y="690" width="1320"'), "line89 表容器"
    assert ">关键差异对照<" in L[89], "line90 表标题"
    row_re = re.compile(r'^<rect x="60" y="(\d+)" width="210" height="32"')
    dstart = []
    i = 96
    while i < 174 and row_re.match(L[i]):
        dstart.append(i)
        assert all(t.strip().startswith("<rect") for t in L[i + 1:i + 3]), "数据行 rect"
        assert all(t.strip().startswith("<text") for t in L[i + 3:i + 6]), "数据行 text"
        i += 6
    assert len(dstart) == 13, f"应为 13 数据行, 实得 {len(dstart)}"
    assert dstart[-1] + 6 == 174, "末数据行应紧邻 </svg>"

    # ---- 组装 ----
    out = [L[0], L[1]] + KIT_CSS.split("\n")   # <svg> + 字体 style + kit style（下一行）
    out.extend(L[2:10])                        # 源 <defs>（5 marker）+ 白底 rect

    # 标题/副标题 → .head
    out.append('<g class="head">')
    out.append(L[10]); out.append(L[11])
    out.append("</g>")

    def cellwave_pair(rect_i, text_i, delay):
        return ([f'<g class="cellwave" style="animation-delay:{fmt(delay)}s">',
                 L[rect_i], L[text_i], "</g>"])

    def row_group(delay, a, b, inner=None):
        out.append(f'<g class="row" style="animation-delay:{fmt(delay)}s">')
        if inner:
            inner()
        else:
            out.extend(L[a:b])
        out.append("</g>")

    # ---- 左列（盒自上而下 0.15 步进 0.12）----
    row_group(0.15, 12, 17)                                   # 容器 + 列标题 + Test Layer

    def left_seq():
        out.append(L[17]); out.append(L[18])
        for c, (r, t) in enumerate([(19, 20), (21, 22), (23, 24), (25, 26), (27, 28)]):
            out.extend(cellwave_pair(r, t, c * CW_STEP))
    row_group(0.27, 17, 30, left_seq)                         # isptx_sequence + 5 chip 行波

    for d, (a, b) in [(0.39, (29, 33)), (0.51, (33, 36)), (0.63, (36, 40))]:
        row_group(d, a, b)                                    # transaction / driver / DUT

    def left_verify():
        out.append('<g class="pulse" style="animation-delay:-1.4s">')
        out.extend(L[40:43])                                  # 左"线上数据验证"（verdict 盒）
        out.append("</g>")
    row_group(0.75, 40, 43, left_verify)

    # ---- 右列（0.30 步进 0.12）----
    row_group(0.30, 43, 48)                                   # 容器 + 列标题 + Test Layer

    def right_seq():
        out.append(L[48]); out.append(L[49])
        for c, (r, t) in enumerate([(50, 51), (52, 53), (54, 55), (56, 57), (58, 59)]):
            out.extend(cellwave_pair(r, t, CW_RIGHT_PHASE + c * CW_STEP))
    row_group(0.42, 48, 60, right_seq)                        # isptx_sequence 420b + 5 chip 行波

    for d, (a, b) in [(0.54, (60, 64)), (0.66, (64, 68)), (0.78, (68, 71)), (0.90, (71, 75))]:
        row_group(d, a, b)                                    # ref model / transaction / driver / DUT

    def right_verify():
        out.append('<g class="pulse-t" style="animation-delay:-0.7s">')
        out.extend(L[75:78])                                  # 右"线上数据验证（0717 新增）"
        out.append("</g>")
    row_group(1.02, 75, 78, right_verify)

    # ---- spine 箭头：draw 自绘（delay = max(两端盒)+0.55）----
    for e, k in enumerate(range(78, 83)):
        out.append(tag_draw(L[k], LEFT_DRAW[e]))
    for e, k in enumerate(range(83, 88)):
        out.append(tag_draw(L[k], RIGHT_DRAW[e]))

    # ---- 数据列车：双列赛跑（左蓝 #1d4ed8 / 右琥珀 #b45309，右列整体 +0.35s）----
    for e, (y0, y1) in enumerate(SPINE_Y):
        out.extend(train_edge(360, y0, y1, "#1d4ed8", -FLOW_EDGE_STEP * e, LEFT_DRAW[e]))
    for e, (y0, y1) in enumerate(SPINE_Y):
        out.extend(train_edge(1040, y0, y1, "#b45309", RIGHT_PHASE - FLOW_EDGE_STEP * e, RIGHT_DRAW[e]))

    # ---- 底部对比区：表头组 1.4；13 数据行 1.45 起步进 0.04 ----
    row_group(1.40, 88, 96)
    for r, s0 in enumerate(dstart):
        row_group(1.45 + 0.04 * r, s0, s0 + 6)

    out.append(L[174])        # </svg>
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-28 19:06
