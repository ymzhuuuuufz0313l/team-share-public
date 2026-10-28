#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_checksum_logic.py — checksum_logic_flow.svg 动画版生成器
（Motion Kit v4；本图此前无动画生成器，本文件为 v4 新建）。

源（只读）:  ../checksum_logic_flow.svg   （静态版由 make_checksum_logic.py 生成，不在此碰）
输出:        checksum_logic_flow.svg

v4 规格（1240×900，四段式实现逻辑图）：
- 入场（先容器→再内容→最后箭头，一次性总长 ≤2.5s）：
  · head 标题+副标题(0)
  · ① 段标(0.15) + 8 个拍盒 0.25 起 0.07s 递进（至 0.74）
  · ② 段标(0.55) + 累加盒(0.70) + 锁存盒(0.78)
  · ③ 段标(0.90) + 判据盒(1.00) + 防护盒(1.08) + match_eff 盒(1.18)
  · ④ 段标(1.25) + 四个计数/提交/解锁盒(1.28/1.34/1.40/1.44)
  · 1027v1-B 修复面板(1.60) + 图例(1.72)
  · 箭头（§5 规则 delay ≥ max(两端面板)+0.55）：
    实线数据流 .draw：A1 1.30 / A2 1.35 / A3 1.55 / A5 1.75 / A10 1.90 / A11 2.00
    （A10/A11 内联 duration 0.5/0.45s，最晚 2.00+0.45=2.45s 收尾）
    虚线控制流 .fade（保留源 dasharray，不用 .draw 以免覆盖虚线几何）：
    A4 1.65 / A6 1.75 / A7 1.75 / A8 1.90 / A9 1.95（内联 0.45s）
    箭头旁标签随箭头同拍 fade。
- 稳态（3 族，肉眼可辨）：
  · 列车 flowdot/flowtail（主数据流 teal #0e7490）：
    A1 1 包(1.2s) / A2 2 包+拖尾(1.5s) / A3 1 包(1.2s) / A5 2 包+拖尾(1.6s)
    + A11 琥珀 1 包(1.2s)（unmatch→unlock 支路）；全部藏在箭头 fade 组内，
    入场后随箭头一起现身；同族错相位。
  · 脉冲 pulse×3（错相位 -0.7 / -1.4 / -2.1）：
    5'h04 修复盒+◆（琥珀 pulse）/ update_en_a 提交门（蓝 pulse-b）
    / match_eff_a 判决盒（深青 pulse-t）。
  · 行波 cellwave×6：① 段 6 个实线拍盒（5'h01/02/03/0A/0B/0E）按拍序
    左→右错相位（0.55s/盒，4.2s 周期）= 参与字节逐拍扫描；
    5'h04 用 pulse、gap 虚线盒不参与波。
- 铁律：源 SVG 只读；<text> 多重集 / svg 开标签 / 几何颜色零改动；
  纯 CSS 无 script 无 SMIL；kit CSS §2 逐字嵌入；源 defs（3 个 marker）
  与背景 rect 原样保留；reduced-motion 用 kit 原文；确定性幂等。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images")
SRC = BASE / "checksum_logic_flow.svg"
OUT = BASE / "anim" / "checksum_logic_flow.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类）
KIT_CSS = "\n".join([
    ".row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}",
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}",
    "@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}",
    ".pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}",
    "@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}",
    ".pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}",
    "@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}",
    ".sweepband{opacity:.85;animation:sweepMove 8s linear infinite}",
    "@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}",
    ".dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}",
    "@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}",
    ".march{animation:march 1.5s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".cellwave{animation:wave 2.6s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".step{animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}",
])

TEAL = "#0e7490"
AMBER = "#b45309"


def flowdot(d, color, delay, dur):
    return ('<path class="flowdot" d="%s" stroke="%s" pathLength="100" '
            'style="animation-duration:%s;animation-delay:%s"/>' % (d, color, dur, delay))


def flowtail(d, color, delay, dur):
    return ('<path class="flowtail" d="%s" stroke="%s" pathLength="100" '
            'style="animation-duration:%s;animation-delay:%s"/>' % (d, color, dur, delay))


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tail_nl = raw.endswith(eol)
    lines = raw.split(eol)
    if tail_nl:
        lines = lines[:-1]
    assert lines[0].startswith("<?xml"), "line1 应为 XML 声明"
    assert lines[1].lstrip().startswith("<svg"), "line2 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def txt(i):
        s = lines[i].strip()
        assert s.startswith("<text") and s.endswith("</text>"), f"line{i+1} 应为 text"
        return s

    def rect(i):
        assert lines[i].strip().startswith("<rect"), f"line{i+1} 应为 rect"
        return lines[i]

    # ---- 结构锚点（0 基行号，全部 assert 保护；锚定文本取每元素独有前缀） ----
    a = {}
    keys = [
        ("title", "LC_CPUWR Seg1 Checksum 实现逻辑"),
        ("sub", "0721v1 3B/beat 按字节有效性折叠"),
        ("s1", "① 帧数据流"),
        ("s2", "② 累加与锁存"),
        ("s3", "③ 帧尾比较"),
        ("s4", "④ 提交门控与计数"),
        ("fix_t", "1027v1-B 修复（2026-10-27"),
        ("lg1", "数据流（流光点=流向）"),
        ("lg2", "修复点（呼吸高亮）"),
    ]
    for k, prefix in keys:
        a[k] = next(i for i in range(2, end) if lines[i].strip().startswith("<text")
                    and prefix in lines[i])
    # 拍盒 = ① 段标后到 A1 前的 rect（每盒 rect+4 text）
    beat_rects = [i for i in range(a["s1"], end)
                  if lines[i].strip().startswith("<rect") and i < a["s2"]]
    # A1 = s1..s2 间的箭头 path（竖直 xdata_a ↓，d 以 M 620,202 起；◆ 是填充菱形）
    a1 = next(i for i in range(a["s1"], a["s2"])
              if lines[i].strip().startswith("<path") and 'd="M 620,202' in lines[i])
    a1_lb = a1 + 1
    assert "xdata_a" in lines[a1_lb], "A1 标签应为 xdata_a"
    # ② 段两盒 rect
    acc_rects = [i for i in range(a["s2"], a["s3"]) if lines[i].strip().startswith("<rect")]
    assert len(acc_rects) == 2, "② 段应有 2 个盒"
    a2 = next(i for i in range(a["s2"], a["s3"]) if lines[i].strip().startswith("<path"))
    a2_lb = a2 + 1
    assert "帧尾锁存" in lines[a2_lb], "A2 标签应为 帧尾锁存"
    # ③ 段：judge1/judge2 rect + A3/A4 path + prev 标签 + match_eff rect + A5/A6
    judge_rects = [i for i in range(a["s3"], a["s4"]) if lines[i].strip().startswith("<rect")]
    assert len(judge_rects) == 3, "③ 段应有 3 个盒（判据/防护/match_eff）"
    j1, j2, meff = judge_rects
    paths3 = [i for i in range(a["s3"], a["s4"]) if lines[i].strip().startswith("<path")]
    assert len(paths3) == 4, "③ 段应有 4 条 path（A3/A4/A5/A6）"
    a3, a4, a5, a6 = paths3
    prev_lb = next(i for i in range(a4 + 1, a5) if lines[i].strip().startswith("<text"))
    assert "prev_xsum_a" in lines[prev_lb], "prev 标签异常"
    # ④ 段：4 盒 rect + 5 path（A7/A8/A9 控制链 + A10 / A11）+ 计数注释
    paths4 = [i for i in range(a["s4"], a["fix_t"])
              if lines[i].strip().startswith("<path") and 'stroke="' in lines[i]]
    assert len(paths4) == 5, "④ 段应有 5 条 path"
    c_rects = [i for i in range(a["s4"], paths4[0]) if lines[i].strip().startswith("<rect")]
    assert len(c_rects) == 4, "④ 段应有 4 个盒"
    c1, c2, c3, c4 = c_rects
    assert "update_en_a" in lines[c2 + 1], "c2 应为 update_en_a"
    a7, a8, a9, a10, a11 = paths4
    note_eff0 = next(i for i in range(a11 + 1, a["fix_t"])
                     if lines[i].strip().startswith("<text"))
    assert "match_eff_a=0" in lines[note_eff0], "match_eff_a=0 注释异常"
    # 修复面板：rect（fix_t-2）+ ◆ path（fix_t-1）+ 标题 text（fix_t）+ 说明文字
    fix_rect = a["fix_t"] - 2
    assert lines[fix_rect].strip().startswith("<rect"), "修复面板 rect 异常"
    fix_dia = fix_rect + 1
    assert lines[fix_dia].strip().startswith("<path"), "修复 ◆ path 异常"
    fix_end = a["lg1"] - 1  # 修复面板文字止于图例前（lg1 前一行是 legend path）
    while not lines[fix_end].strip().startswith("<text"):
        fix_end -= 1
    assert "验证脚本" in lines[fix_end], "修复面板末行异常"

    # 拍盒分组：rect 起 4 行 text（第 5 盒 5'h04 含 ◆ path 在盒后）
    boxes = []
    for br in beat_rects:
        if "5'h04" in lines[br + 1]:
            boxes.append((br, br + 5))      # rect+4text+◆path
        else:
            boxes.append((br, br + 4))
    assert len(boxes) == 8, f"应 8 个拍盒，实际 {len(boxes)}"
    wave_boxes = [b for b, (s, e) in enumerate(boxes)
                  if "5'h04" not in lines[boxes[b][0] + 1]
                  and "gap" not in lines[boxes[b][0] + 1]]
    assert len(wave_boxes) == 6, "行波盒应 6 个"

    # ---- 组装 ----
    o = []
    o.append(lines[0])                      # <?xml?>
    o.append(lines[1])                      # <svg ...>
    o.append("<style>\n" + KIT_CSS + "\n</style>")  # kit CSS（§2 逐字）
    o.append(lines[2])                      # 白底 rect
    o.extend(lines[3:a["title"]])           # 源 defs（3 个 marker）原样保留

    def g_row(span, delay, inner=None):
        o.append(f'<g class="row" style="animation-delay:{delay}s">')
        if inner:
            o.append(inner)
        o.extend(lines[span[0]:span[1] + 1])
        if inner:
            o.append("</g>")
        o.append("</g>")

    # head：标题+副标题(0)
    g_row((a["title"], a["sub"]), 0)

    # ① 段标(0.15) + 8 拍盒（0.25 起 0.07s 递进；5'h04=pulse，6 实盒=cellwave）
    o.append(f'<g class="row" style="animation-delay:0.15s">')
    o.append(lines[a["s1"]])
    o.append("</g>")
    for k, (s, e) in enumerate(boxes):
        delay = round(0.25 + 0.07 * k, 2)
        o.append(f'<g class="row" style="animation-delay:{delay}s">')
        head_line = lines[s + 1]
        if "5'h04" in head_line:
            o.append('<g class="pulse" style="animation-delay:-0.7s">')
            o.extend(lines[s:e + 1])
            o.append("</g>")
        elif "gap" not in head_line:
            wv = (f'<g class="cellwave" style="animation-duration:4.2s;'
                  f'animation-delay:-{0.55 * wave_boxes.index(k):.2f}s">')
            o.append(wv)
            o.extend(lines[s:e + 1])
            o.append("</g>")
        else:
            o.extend(lines[s:e + 1])
        o.append("</g>")

    # A1：draw 1.30 + 标签 fade 同拍 + 列车 1 包（短边单点）
    o.append(f'<g class="fade" style="animation-delay:1.3s">')
    o.append(lines[a1].replace(
        "<path ", '<path class="draw" pathLength="100" style="animation-delay:1.3s" ', 1))
    o.append(lines[a1_lb])
    o.append(flowdot("M 620,202 L 620,236", TEAL, "-0.1s", "1.2s"))
    o.append("</g>")

    # ② 段标(0.55) + 两盒(0.70/0.78)
    o.append(f'<g class="row" style="animation-delay:0.55s">')
    o.append(lines[a["s2"]])
    o.append("</g>")
    g_row((acc_rects[0], acc_rects[1] - 1), 0.70)
    g_row((acc_rects[1], a2 - 1), 0.78)

    # A2：draw 1.35 + 标签 + 列车 2 包 + 拖尾（1.5s）
    o.append(f'<g class="fade" style="animation-delay:1.35s">')
    o.append(lines[a2].replace(
        "<path ", '<path class="draw" pathLength="100" style="animation-delay:1.35s" ', 1))
    o.append(lines[a2_lb])
    o.append(flowdot("M 500,318 L 770,318", TEAL, "-0.2s", "1.5s"))
    o.append(flowdot("M 500,318 L 770,318", TEAL, "-0.95s", "1.5s"))
    o.append(flowtail("M 500,318 L 770,318", TEAL, "-0.2s", "1.5s"))
    o.append("</g>")

    # ③ 段标(0.90) + judge1(1.00) + judge2(1.08) + match_eff(1.18, pulse-t)
    o.append(f'<g class="row" style="animation-delay:0.9s">')
    o.append(lines[a["s3"]])
    o.append("</g>")
    g_row((j1, j2 - 1), 1.00)
    g_row((j2, a3 - 1), 1.08)
    o.append(f'<g class="row" style="animation-delay:1.18s">')
    o.append('<g class="pulse-t" style="animation-delay:-2.1s">')
    o.extend(lines[meff:a5])
    o.append("</g>")
    o.append("</g>")

    # A3（draw 1.55 + 列车 1 包）；A4（虚线 fade 1.65 + prev 标签）
    o.append(f'<g class="fade" style="animation-delay:1.55s">')
    o.append(lines[a3].replace(
        "<path ", '<path class="draw" pathLength="100" style="animation-delay:1.55s" ', 1))
    o.append(flowdot("M 320,360 L 320,410", TEAL, "-0.7s", "1.2s"))
    o.append("</g>")
    o.append(f'<g class="fade" style="animation-delay:1.65s">')
    o.append(lines[a4])
    o.append(lines[prev_lb])
    o.append("</g>")

    # A5（draw 1.75 + 列车 2 包+拖尾 1.6s）；A6（虚线 fade 1.75）
    o.append(f'<g class="fade" style="animation-delay:1.75s">')
    o.append(lines[a5].replace(
        "<path ", '<path class="draw" pathLength="100" style="animation-delay:1.75s" ', 1))
    o.append(flowdot("M 320,506 L 610,540", TEAL, "-0.5s", "1.6s"))
    o.append(flowdot("M 320,506 L 610,540", TEAL, "-1.3s", "1.6s"))
    o.append(flowtail("M 320,506 L 610,540", TEAL, "-0.5s", "1.6s"))
    o.append("</g>")
    o.append(f'<g class="fade" style="animation-delay:1.75s">')
    o.append(lines[a6])
    o.append("</g>")

    # ④ 段标(1.25) + 四盒 1.28/1.34/1.40/1.44（c2 update_en=pulse-b）
    o.append(f'<g class="row" style="animation-delay:1.25s">')
    o.append(lines[a["s4"]])
    o.append("</g>")
    g_row((c1, c2 - 1), 1.28)
    o.append(f'<g class="row" style="animation-delay:1.34s">')
    o.append('<g class="pulse-b" style="animation-delay:-1.4s">')
    o.extend(lines[c2:c3])
    o.append("</g>")
    o.append("</g>")
    g_row((c3, c4 - 1), 1.40)
    g_row((c4, a7 - 1), 1.44)

    # A7/A8/A9 虚线控制链 fade 1.75/1.90/1.95（内联 0.45s，收尾 2.40s）
    o.append(f'<g class="fade" style="animation-delay:1.75s">')
    o.append(lines[a7])
    o.append("</g>")
    o.append(f'<g class="fade" style="animation-delay:1.9s;animation-duration:0.45s">')
    o.append(lines[a8])
    o.append("</g>")
    o.append(f'<g class="fade" style="animation-delay:1.95s;animation-duration:0.45s">')
    o.append(lines[a9])
    o.append("</g>")

    # A10（draw 1.90 内联 0.5s + 列车 1 包）；A11（琥珀 draw 2.00 内联 0.45s + 1 包）
    # + match_eff_a=0 注释 fade 2.0
    o.append(f'<g class="fade" style="animation-delay:1.9s">')
    o.append(lines[a10].replace(
        "<path ", '<path class="draw" pathLength="100" '
                  'style="animation-delay:1.9s;animation-duration:0.5s" ', 1))
    o.append(flowdot("M 290,676 L 340,676", TEAL, "-0.55s", "1.2s"))
    o.append("</g>")
    o.append(f'<g class="fade" style="animation-delay:2s;animation-duration:0.45s">')
    o.append(lines[a11].replace(
        "<path ", '<path class="draw" pathLength="100" '
                  'style="animation-delay:2s;animation-duration:0.45s" ', 1))
    o.append(lines[note_eff0])
    o.append(flowdot("M 870,676 L 930,676", AMBER, "-0.35s", "1.2s"))
    o.append("</g>")

    # 修复面板(1.60) + 图例(1.72)
    o.append(f'<g class="row" style="animation-delay:1.6s">')
    o.extend(lines[fix_rect:fix_end + 1])
    o.append("</g>")
    o.append(f'<g class="row" style="animation-delay:1.72s">')
    o.extend(lines[a["lg1"] - 1:end])
    o.append("</g>")

    o.append(lines[end])  # </svg>
    text = eol.join(o)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return {"draw": text.count('class="draw"'), "fade": text.count('class="fade"'),
            "flowdot": text.count('class="flowdot"'), "flowtail": text.count('class="flowtail"'),
            "pulse": len(re.findall(r'class="pulse(-[tb])?"', text)),
            "cellwave": text.count('class="cellwave"'),
            "row": text.count('class="row"')}


NS = "{http://www.w3.org/2000/svg}"


def check():
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG {e}"

    def texts(p):
        return Counter(el.text or "" for el in ET.parse(str(p)).getroot().iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except Exception as e:
        res["text"] = f"NG {e}"

    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    res["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    rm = re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
    res["rmfix"] = "OK" if (rm and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    fam = {"train": len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
           "pulse": len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
           "sweep": len(re.findall(r'class="[^"]*sweepband', data)),
           "grow": len(re.findall(r'class="[^"]*dashgrow', data)),
           "wave": len(re.findall(r'class="[^"]*cellwave', data)),
           "step": len(re.findall(r'class="[^"]*step"', data))}
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    return res


def main():
    stats = build()
    res = check()
    print("[make_anim_checksum_logic v4]", stats)
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK" or v.startswith("OK("))
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 17:20
