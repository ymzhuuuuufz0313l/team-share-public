#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_tag_replacement.py — v4（Motion Kit v4，整体重写；v2 类名/delay 逻辑不沿用）

MOTION_KIT.md §6.5 规格（1200×460）：
- 行序：标题(0) → 输入行(0.2) → 输出行(0.55) → A→B 组(0.85) → 图例(0.9)
        → ①~④(1.1/1.25/1.4/1.55)。一次性总长 = 1.55+0.55 = 2.10s ≤ 2.5s。
- draw（§5：delay ≥ 两端面板 delay+0.55）：
  · 输入→输出 ↓替换箭头 delay 1.1（两端 max = 输出行 0.55）
  · A→B 发送顺序箭头 delay 1.1（两端 = 输出行 0.55）
- step：4 框循环 delay 0 / -1.5 / -3 / -4.5s（6s 周期）
- 列车：A→B 箭头 2 包 + flowtail（duration 1.6s，phase -0.2 / -1.0，tail 随包 1）
- 行波：输出行全部 10 个单元格（含标签格）左→右 cellwave（0.1s/格，duration 3.4s）
- 脉冲：全0/全1 两个红格 .pulse（琥珀，delay 0 / -1.4，phase 差 1.4s）
- march：源图 header 位无虚线（§6.5“若有”条件不成立，跳过）
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs + 背景 rect 保留（assert 保护）；字体 <style> 留行 2；
  reduced-motion 用 kit 原文；确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_tag_replacement.svg"
OUT = BASE / "anim" / "spec_tag_replacement.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类）
KIT_CSS = "\n".join([
    ".row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 1.5s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 1.5s linear infinite}",
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}",
    "@keyframes pulse{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(180,83,9,.8))}}",
    ".pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}",
    "@keyframes pulseT{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(14,116,144,.8))}}",
    ".pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}",
    "@keyframes pulseB{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(29,78,216,.8))}}",
    ".sweepband{opacity:.85;animation:sweepMove 8s linear infinite}",
    "@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}",
    ".dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}",
    "@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}",
    ".march{animation:march 1.5s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".cellwave{transform-box:fill-box;transform-origin:center;animation:wave 2.6s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.72;transform:scale(1.01)}}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".step{transform-box:fill-box;transform-origin:center;animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85));transform:scale(1.02)}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0));transform:none}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85));transform:scale(1.02)}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}",
])


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def find(pred, start=2, stop=None):
        stop = end if stop is None else stop
        for i in range(start, stop):
            if pred(lines[i]):
                return i
        raise AssertionError("anchor not found")

    # ---- 结构锚点（源行号，0 基；全部 assert 保护） ----
    title_i = find(lambda s: "分组标签替换" in s)
    sub_i = title_i + 1
    assert "59 组" in lines[sub_i]

    input_label_t = find(lambda s: ">输入 413b<" in s, title_i)
    input_start = input_label_t - 1
    assert lines[input_start].strip().startswith("<rect"), "输入标签前应为 rect"

    cap1_i = find(lambda s: ">全 0<" in s, input_label_t)
    cap2_i = find(lambda s: ">全 1<" in s, cap1_i)
    input_end = cap2_i  # 输入行含两条红格说明

    down_arrow_i = find(lambda s: 'x1="442" y1="172"' in s, input_end)
    assert lines[down_arrow_i].strip().startswith("<line")

    out_label_t = find(lambda s: ">输出 420b<" in s, down_arrow_i)
    out_start = out_label_t - 1
    assert lines[out_start].strip().startswith("<rect")

    a2b_i = find(lambda s: 'x1="655" y1="196"' in s, out_start)
    a2b_label_i = find(lambda s: "发送顺序 A → B" in s, a2b_i)
    b_i = find(lambda s: 'x="795"' in s and ">B<" in s, a2b_label_i)
    cells_end = a2b_i
    assert cells_end > out_start

    legend_start = find(lambda s: s.strip().startswith('<rect x="890"'), b_i)
    step_rects = [i for i in range(legend_start, end)
                  if lines[i].strip().startswith("<rect") and 'y="300"' in lines[i]]
    assert len(step_rects) == 4, f"应有 4 个步骤框, 实得 {len(step_rects)}"

    # 输入行红格（全 0 / 全 1）：rect+text 对 → .pulse
    red_cells = [i for i in range(input_start, input_end + 1)
                 if lines[i].strip().startswith("<rect") and 'fill="#fee2e2"' in lines[i]]
    assert len(red_cells) == 2, f"应有 2 个红色格, 实得 {len(red_cells)}"
    for i in red_cells:
        assert lines[i + 1].strip().startswith("<text"), "红格后应紧跟 text"

    # 输出行单元格（rect y=208 + 紧随 text，含标签格）→ .cellwave
    cell_pairs = []
    i = out_start
    while i < cells_end:
        s = lines[i].strip()
        if s.startswith("<rect") and 'y="208"' in s:
            assert lines[i + 1].strip().startswith("<text"), "单元格 rect 后应为 text"
            cell_pairs.append((i, i + 1))
            i += 2
            continue
        i += 1
    assert len(cell_pairs) == 10, f"输出行应有 10 个单元格(含标签格), 实得 {len(cell_pairs)}"

    # ---- 组装 ----
    o = []
    o.append(lines[0])                                        # <svg> 开标签原样
    o.append(lines[1])                                        # 行2：字体 <style>（保留）
    o.append("<style>\n" + KIT_CSS + "\n</style>")            # 行3：kit CSS §2 逐字
    o.extend(lines[2:title_i])                                # defs + 白底（铁律 4）

    # 标题 head(0)
    o.append('<g class="head">')
    o.extend(lines[title_i:sub_i + 1])
    o.append("</g>")

    # 输入行 row(0.2)；红格 .pulse（琥珀，phase 差 1.4s）
    o.append('<g class="row" style="animation-delay:0.2s">')
    red_pulse = {red_cells[0]: "0s", red_cells[1]: "-1.4s"}
    i = input_start
    while i <= input_end:
        if i in red_pulse:
            o.append(f'<g class="pulse" style="animation-delay:{red_pulse[i]}">')
            o.append(lines[i])
            o.append(lines[i + 1])
            o.append("</g>")
            i += 2
            continue
        o.append(lines[i])
        i += 1
    o.append("</g>")

    # ↓ 替换箭头：draw 1.1 = max(输入 0.2, 输出 0.55) + 0.55（§5 规则）
    o.append('<g class="fade" style="animation-delay:1.1s">')
    o.append(lines[down_arrow_i].replace(
        "<line ", '<line class="draw" pathLength="100" style="animation-delay:1.1s" ', 1))
    o.append("</g>")

    # 输出行 row(0.55)；全部 10 格 cellwave 左→右 0.1s/格，duration 3.4s
    o.append('<g class="row" style="animation-delay:0.55s">')
    i = out_start
    k = 0
    while i < cells_end:
        if (i, i + 1) in cell_pairs:
            o.append(f'<g class="cellwave" style="animation-duration:3.4s;animation-delay:{k * 0.1:.1f}s">')
            o.append(lines[i])
            o.append(lines[i + 1])
            o.append("</g>")
            k += 1
            i += 2
            continue
        o.append(lines[i])  # "……" 等散文本
        i += 1
    o.append("</g>")

    # A→B 组 row(0.85)：draw 1.1（=输出行 0.55+0.55）+ 列车 2 包 + flowtail（1.6s）
    o.append('<g class="row" style="animation-delay:0.85s">')
    o.append('<g class="fade" style="animation-delay:1.1s">')
    o.append(lines[a2b_i].replace(
        "<line ", '<line class="draw" pathLength="100" style="animation-delay:1.1s" ', 1))
    for d in ("-0.2s", "-1.0s"):
        o.append('<path class="flowdot" d="M 655 196 L 830 196" stroke="#2563eb" '
                 f'pathLength="100" style="animation-duration:1.6s;animation-delay:{d}"/>')
    o.append('<path class="flowtail" d="M 655 196 L 830 196" stroke="#2563eb" '
             'pathLength="100" style="animation-duration:1.6s;animation-delay:-0.2s"/>')
    o.append("</g>")
    o.extend(lines[a2b_label_i:b_i + 1])  # “发送顺序 A → B” + A/B
    o.append("</g>")

    # 图例 head(0.9)
    o.append('<g class="head" style="animation-delay:0.9s">')
    o.extend(lines[legend_start:step_rects[0]])
    o.append("</g>")

    # ①②③④：row 入场 1.1/1.25/1.4/1.55 + .step 循环 0/-1.5/-3/-4.5
    step_delays = ["0s", "-1.5s", "-3s", "-4.5s"]
    row_delays = [1.1, 1.25, 1.4, 1.55]
    for r in range(4):
        s = step_rects[r]
        e = step_rects[r + 1] if r + 1 < 4 else end
        o.append(f'<g class="row" style="animation-delay:{row_delays[r]}s">')
        o.append(f'<g class="step" style="animation-delay:{step_delays[r]}">')
        o.extend(lines[s:e])
        o.append("</g>")
        o.append("</g>")

    o.append(lines[end])
    text = eol.join(o).replace("\n", eol)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


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
    res["kit_train"] = "OK" if ".flowdot{" in data and "stroke-width:3.5" in data else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    res["rmfix"] = "OK" if ".flowdot,.flowtail,.sweepband{display:none!important}" in data else "NG"
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_spec_tag_replacement v4]",
          f"draw={data.count('class=\"draw\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"flowtail={data.count('class=\"flowtail\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"pulse={data.count('class=\"pulse\"')}",
          f"step={data.count('class=\"step\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}",
          f"fade={data.count('class=\"fade\"')}")
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 16:58
