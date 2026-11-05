#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_frame_flow.py  (Motion Kit v4 · 1105 0924 帧结构重绘版)

新版静态图（generate_longcode_report_svgs.py · gen_spec_frameflow，1200x700）：
Clock → LSP → 帧 0 配置行 → VBP×2 → Active×3 → VFP 第 0 行（= 下一帧配置行，
高亮）→ VFP 其余行 → 底部 K3|K2 注记。旧版「Config Line 单独成行 + K2 or K3」
语义已废弃（旧图归档 archive/20260720/）。

动效规格（沿 MOTION_KIT.md §6.4 骨架，按新版行结构重排）：
- 入场：标题(0) → Clock(.15) → LSP(.35) → 帧0(.55) → VBP1(.70)/VBP2(.85)/
  VBP 括号(1.00) → Act1(1.10)/Act2(1.22)/…(1.32)/last(1.42)/括号(1.52) →
  VFP0 高亮(1.62) → VFP rest(1.75) → 尾括号(1.85) → 注记(1.95)。
  一次性总长 1.95+0.55=2.50s ≤2.5s。本图无箭头 → 无 draw（校验软项）。
- 稳态族（2 族）：
  * 行波 cellwave（主角）：帧0/VBP×2/Active×3/VFP0/VFP rest 共 8 行组整行
    cellwave，自上而下 0.18s 递增，周期 4.5s（内联 duration）= 帧滚动波。
  * 脉冲 pulse×5：Clock 条 pulse-b(-2.1s)；LSP 条 pulse-b(-1.4s)；
    「VFP 第 0 行 = 帧 c+1 配置行」高亮组 pulse-t(-0.7s，0924 修复点)；
    VFP 其余行组 pulse-t(-1.4s)；底部 K3 注记 pulse-t(-2.1s)。
- 不加列车/breathe/sweep（行波+脉冲已 2 族、画面已密）。
- kit <style> 按铁律 §0.5 放在源图第 2 行字体 <style> 的下一行。

铁律：源 SVG 只读；text/几何/颜色零改动；纯 CSS in-SVG；kit CSS §2 逐字；
保留源 defs + 背景 rect + 字体 style；reduced-motion 块原样；
确定性幂等；零第三方依赖。
"""
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "images" / "spec_frame_flow.svg"
OUT = BASE / "images" / "anim" / "spec_frame_flow.svg"

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

# 单元：((起,止) 0 基, 入场 delay, cellwave delay（None=不包波）, pulse(类,delay)|None, head?)
UNITS = [
    ((10, 12), 0.00, None, None, True),                 # 标题 + 副标题
    ((12, 14), 0.15, None, ("pulse-b", -2.1), False),   # Clock training 条
    ((14, 16), 0.35, None, ("pulse-b", -1.4), False),   # LSP 条
    ((16, 27), 0.55, 0.00, None, False),                # 帧 0 配置行（K4|CTRL_F|Dmy|K3|K2|IDLE + 标签）
    ((27, 37), 0.70, 0.18, None, False),                # VBP 行 1
    ((37, 48), 0.85, 0.36, None, False),                # VBP 行 2 + 标签
    ((48, 50), 1.00, None, None, False),                # VBP 括号 + 竖排标签
    ((50, 60), 1.10, 0.54, None, False),                # Active line1
    ((60, 70), 1.22, 0.72, None, False),                # Active line2
    ((70, 71), 1.32, None, None, False),                # ……
    ((71, 81), 1.42, 0.90, None, False),                # Active last line
    ((81, 85), 1.52, None, None, False),                # Active 括号 + 竖排标签 + 右侧 2 标签
    ((85, 98), 1.62, 1.08, ("pulse-t", -0.7), False),   # VFP 第 0 行 = 帧 c+1 配置行（0924 高亮）
    ((98, 109), 1.75, 1.26, ("pulse-t", -1.4), False),  # VFP 其余行（同 VBP）
    ((109, 112), 1.85, None, None, False),              # …… + VFP 括号 + 竖排标签
    ((112, 114), 1.95, None, ("pulse-t", -2.1), False), # 底部 2 条注记（K3|K2 teal + 帧 c+1）
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
    assert len(lines) == 115, f"应为 115 行, 实得 {len(lines)}"
    for i, needle in [(10, "420b 帧数据流"), (11, "LSP 训练 → 每帧"), (13, "Clock training pattern"),
                      (15, "LSP（K2"), (26, "帧 0 配置行"), (47, "VBP 行 × vbp"),
                      (70, "……"), (83, "Active 行 × vact"),
                      (85, '<rect x="202" y="496"'), (96, "VFP 第 0 行 = 帧 c+1 配置行"),
                      (97, "0924：并入首 VFP 行"), (108, "VFP 其余行（同 VBP）"),
                      (112, "Config 行尾：SCREN=1 → K3"), (113, "帧 c+1：VBP → Active")]:
        assert needle in lines[i], f"line{i+1} 应含 {needle!r}: {lines[i][:80]}"
    assert (UNITS[0][0][0], UNITS[-1][0][1]) == (10, 114), "单元应覆盖全部内容行"
    for (a, b), _d, _c, _p, _h in UNITS:
        assert 10 <= a < b <= 114, f"单元范围越界: {(a, b)}"
    # 每个数据行组应为 5 段 rect+text（10 行）
    for s in (16, 27, 37, 50, 60, 71, 86, 98):
        assert lines[s].strip().startswith("<rect") and lines[s + 1].strip().startswith("<text"), \
            f"行组起点 {s} 应为 rect+text 对"
        assert sum(1 for j in range(s, s + 10) if lines[j].strip().startswith("<rect")) == 5, \
            f"行组 {s} 应含 5 个 rect"

    # ---- 组装 ----
    out = [lines[0], lines[1]] + KIT_CSS.split("\n")   # 铁律 §0.5：kit style 在字体 style 下一行
    out.extend(lines[2:10])                            # 源 <defs> + 白底 rect

    counts = {"row": 0, "head": 0, "cellwave": 0, "pulse": 0}
    for (a, b), delay, cw, pulse, head in UNITS:
        if head:
            counts["head"] += 1
            out.append('<g class="head">')
        else:
            counts["row"] += 1
            out.append('<g class="row" style="animation-delay:%gs">' % delay)
        if cw is not None:
            counts["cellwave"] += 1
            out.append('<g class="cellwave" style="animation-delay:%gs;'
                       'animation-duration:%gs">' % (cw, CW_DUR))
        if pulse:
            counts["pulse"] += 1
            out.append('<g class="%s" style="animation-delay:%gs">' % (pulse[0], pulse[1]))
        out.extend(lines[a:b])
        if pulse:
            out.append("</g>")
        if cw is not None:
            out.append("</g>")
        out.append("</g>")
    out.append(lines[114])                              # </svg>

    text = eol.join(out) + (eol if tail_nl else "")
    OUT.write_text(text, encoding="utf-8", newline="")
    print("written: %s (%d bytes)  effects=%s" % (OUT, OUT.stat().st_size, counts))


if __name__ == "__main__":
    build()

# ymzhu 2026-11-05 11:20
