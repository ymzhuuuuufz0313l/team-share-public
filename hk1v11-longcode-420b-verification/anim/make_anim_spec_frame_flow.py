#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_frame_flow.py  (Motion Kit v4 整体重写)

MOTION_KIT.md §6.4 规格（1200x700 420b 帧数据流）：
- 入场编排 §5：标题(0) → Clock(0.15) → LSP(0.35) → Frame c(0.55)
  → Active 4 行(0.70/0.85/1.00/1.15) → c+1(1.30) → VBK(1.45/1.60) → 括号(1.75)。
  一次性总长 1.75+0.6=2.35s ≤2.5s。本图无箭头 → 无 draw（校验软项）。
- 稳态族（2 族，§6.4 明示不加列车/breathe/sweep；2026-10-28 晚动效加密 +2 脉冲）：
  * 行波 cellwave（主角）：所有"行"（Frame c、Active line1/line2/last、c+1、
    VBK×2 共 7 行组）整行组包 cellwave，自上而下 0.18s 递增，
    周期 4.5s（内联 duration）= 帧滚动波。
  * 脉冲 pulse（2→4）：Clock training 条 pulse-b(-2.1s，与 LSP 的 -1.4s 错 0.7s)；
    LSP 条 pulse-b(-1.4s)；"Config Line · Frame c+1" 行盒 pulse-t(-0.7s，0717 修复点)；
    V blanking 两行组 pulse-t(-1.4s，两行同 delay = 同步呼吸的一个两行组，
    与既有 pulse-t 错 0.7s)。
- kit <style> 按铁律 §0.5 放在源图第 2 行字体 <style> 的下一行（修 v2 顺序）。
- 源图为 CRLF 行尾、末行 </svg> 无换行：原样保留。
铁律：源 SVG 只读；text/几何/颜色零改动；纯 CSS in-SVG；kit CSS §2 逐字；
保留源 defs + 背景 rect + 字体 style；reduced-motion 块原样；
确定性幂等；零第三方依赖。
"""
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_frame_flow.svg"
OUT = BASE / "anim" / "spec_frame_flow.svg"

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

CW_DUR = 4.5  # 帧滚动波周期（§6.4 指定，内联 duration）

# 顺序单元：(起, 止) 0 基、入场 delay、cellwave delay（None=不包波）、pulse(类, delay)
UNITS = [
    ((10, 12), 0.00, None, None),            # 标题 + 副标题（head）
    ((12, 14), 0.15, None, ("pulse-b", -2.1)),   # Clock training 条（脉冲，加密新增）
    ((14, 16), 0.35, None, ("pulse-b", -1.4)),   # LSP 条（脉冲）
    ((16, 27), 0.55, 0.00, None),            # Config Line（Frame c）
    ((27, 37), 0.70, 0.18, None),            # Video Active line1
    ((37, 48), 0.85, 0.36, None),            # Video Active line2 + ……
    ((48, 58), 1.00, 0.54, None),            # Video Active last line
    ((58, 60), 1.15, None, None),            # Video Active 括号 + 竖排标签
    ((60, 73), 1.30, 0.72, ("pulse-t", -0.7)),   # Config Line c+1（0717 修复点）
    ((73, 83), 1.45, 0.90, ("pulse-t", -1.4)),   # V blanking line1（两行组同步脉冲）
    ((83, 93), 1.60, 1.08, ("pulse-t", -1.4)),   # V blanking line2（同上，同 delay 同步）
    ((93, 96), 1.75, None, None),            # …… + V blanking 括号 + 竖排标签
]


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tail_nl = raw.endswith(eol)
    lines = raw.split(eol)
    if tail_nl:
        lines.pop()

    # ---- 结构断言（0 基）----
    assert lines[0].startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style>text"), "line2 应为字体 <style>"
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    assert lines[8].strip() == "</defs>", "line9 应为 </defs>"
    assert lines[9].lstrip().startswith('<rect width="1200"'), "line10 应为白底 rect"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    assert len(lines) == 97, f"应为 97 行, 实得 {len(lines)}"
    for i, needle in [(10, "420b 帧数据流"), (13, "Clock training pattern"), (15, "LSP（K2"),
                      (26, "Config Line（Frame c 配置）"), (47, "……"), (59, ">Video Active<"),
                      (72, "0717v1：单独成行"), (93, "……"), (95, ">V blanking<")]:
        assert needle in lines[i], f"line{i+1} 应含 {needle!r}: {lines[i]}"
    assert (UNITS[0][0][0], UNITS[-1][0][1]) == (10, 96), "单元应覆盖全部内容行"
    for (a, b), _d, _c, _p in UNITS:
        assert 10 <= a < b <= 96, f"单元范围越界: {(a, b)}"

    # ---- 组装 ----
    out = [lines[0], lines[1]] + KIT_CSS.split("\n")   # 铁律 §0.5：kit style 在字体 style 下一行
    out.extend(lines[2:10])                            # 源 <defs> + 白底 rect

    counts = {"row": 0, "head": 0, "cellwave": 0, "pulse": 0}
    for k, ((a, b), delay, cw, pulse) in enumerate(UNITS):
        if k == 0:
            cls = "head"
            counts["head"] += 1
            out.append(f'<g class="{cls}">')
        else:
            cls = "row"
            counts["row"] += 1
            out.append(f'<g class="{cls}" style="animation-delay:{delay:g}s">')
        if cw is not None:
            counts["cellwave"] += 1
            out.append(f'<g class="cellwave" style="animation-delay:{cw:g}s;'
                       f'animation-duration:{CW_DUR:g}s">')
        if pulse:
            counts["pulse"] += 1
            out.append(f'<g class="{pulse[0]}" style="animation-delay:{pulse[1]:g}s">')
        out.extend(lines[a:b])
        if pulse:
            out.append("</g>")
        if cw is not None:
            out.append("</g>")
        out.append("</g>")
    out.append(lines[96])                              # </svg>

    text = eol.join(out) + (eol if tail_nl else "")
    OUT.write_text(text, encoding="utf-8", newline="")
    print(f"written: {OUT} ({OUT.stat().st_size} bytes)  effects={counts}")


if __name__ == "__main__":
    build()

# ymzhu 2026-10-28 19:06
