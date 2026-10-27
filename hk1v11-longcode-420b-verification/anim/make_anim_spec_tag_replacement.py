#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_tag_replacement.py — v2（Motion Kit v2，整体重写，不基于 v1 逻辑）

按 MOTION_KIT.md §4.4 规格：
- 行序：标题(0) → 输入行(0.2) → 输出行(0.55) → A→B 箭头(0.85) → 图例(0.9)
        → ①(1.1) ②(1.25) ③(1.4) ④(1.55)
- draw：输入→输出蓝色↓箭头（delay 0.9）；A→B 箭头（delay 1.2）
- step：4 个步骤框 .step，delay 0 / -1.5 / -3 / -4.5s（6s 循环）
- flow：A→B 箭头 2 包（1.6s 周期，delay 0.2 / 1.0 形成"列车"）
- cellwave：输出行全部单元格（含"输出 420b"标签格）从左到右 0.1s/格，周期 3.4s
- glow：输入行两个红色全 0 / 全 1 格 glow-o，phase 差 1.4s（delay 0 / -1.4）
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  字体 <style> 保留在行 2，motion kit <style> 为行 3；reduced-motion 用 kit 原文。
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

MOTION_STYLE = (
    "<style>\n"
    ".row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}\n"
    ".head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}\n"
    "@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}\n"
    ".draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}\n"
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}\n"
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}\n"
    "@keyframes fadeIn{to{opacity:1}}\n"
    ".fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}\n"
    ".breathe{animation:br 3.2s ease-in-out infinite}\n"
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}\n"
    ".cellwave{animation:wave 3s ease-in-out infinite}\n"
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}\n"
    ".march{animation:march 1.8s linear infinite}\n"
    "@keyframes march{to{stroke-dashoffset:-16}}\n"
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}\n"
    "@keyframes flow{to{stroke-dashoffset:-100}}\n"
    ".glow-b{animation:glowB 2.8s ease-in-out infinite}\n"
    "@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}\n"
    ".glow-g{animation:glowG 2.8s ease-in-out infinite}\n"
    "@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}\n"
    ".glow-o{animation:glowO 2.8s ease-in-out infinite}\n"
    "@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}\n"
    ".step{animation:stepLit 6s ease-in-out infinite}\n"
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}\n"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}\n"
    "</style>"
)


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def find(pred, start=2, stop=None):
        stop = end if stop is None else stop
        for i in range(start, stop):
            if pred(lines[i]):
                return i
        raise AssertionError("anchor not found")

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
    cells_end = a2b_i  # 输出行单元格区止于 A→B 箭头
    assert cells_end > out_start

    legend_start = find(lambda s: s.strip().startswith('<rect x="890"'), b_i)
    # 图例末 = 第一个 y="300" 步骤框前
    step_rects = [i for i in range(legend_start, end)
                  if lines[i].strip().startswith("<rect") and 'y="300"' in lines[i]]
    assert len(step_rects) == 4, f"应有 4 个步骤框, 实得 {len(step_rects)}"

    # ---- 输入行红格（全 0 / 全 1）：rect+text 对，glow-o ----
    red_cells = [i for i in range(input_start, input_end + 1)
                 if lines[i].strip().startswith("<rect") and 'fill="#fee2e2"' in lines[i]]
    assert len(red_cells) == 2, f"应有 2 个红色格, 实得 {len(red_cells)}"
    for i in red_cells:
        assert lines[i + 1].strip().startswith("<text"), "红格后应紧跟 text"

    # ---- 输出行单元格（rect y=208 + 紧随 text），cellwave ----
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
    o.append(lines[0])          # <svg>（开标签原样）
    o.append(lines[1])          # 行2：字体 <style>（保留）
    o.append(MOTION_STYLE)      # 行3：motion kit <style>
    o.extend(lines[2:title_i])  # defs + 白底

    # 标题 0
    o.append('<g class="head">')
    o.extend(lines[title_i:sub_i + 1])
    o.append("</g>")

    # 输入行 0.2（红格 glow-o）
    o.append('<g class="row" style="animation-delay:0.2s">')
    i = input_start
    red_glow = {red_cells[0]: "0s", red_cells[1]: "-1.4s"}
    while i <= input_end:
        if i in red_glow:
            o.append(f'<g class="glow-o" style="animation-delay:{red_glow[i]}">')
            o.append(lines[i])
            o.append(lines[i + 1])
            o.append("</g>")
            i += 2
            continue
        o.append(lines[i])
        i += 1
    o.append("</g>")

    # ↓ 替换箭头 draw（源面板=输出行 0.55 + 0.35 = 0.9）
    o.append(lines[down_arrow_i].replace(
        "<line ", '<line class="draw" pathLength="100" style="animation-delay:0.9s" ', 1))

    # 输出行 0.55（单元格 cellwave 0.1s/格，3.4s 周期）
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

    # A→B 箭头组 0.85：draw（0.85+0.35=1.2）+ flow 2 包（1.6s 周期）
    o.append('<g class="row" style="animation-delay:0.85s">')
    o.append(lines[a2b_i].replace(
        "<line ", '<line class="draw" pathLength="100" style="animation-delay:1.2s" ', 1))
    for d in (0.2, 1.0):
        o.append(f'<path class="flowdot" d="M 655 196 L 830 196" stroke="#2563eb" '
                 f'stroke-width="2.5" pathLength="100" '
                 f'style="animation-duration:1.6s;animation-delay:{d}s"/>')
    o.extend(lines[a2b_label_i:b_i + 1])
    o.append("</g>")

    # 图例 0.9
    o.append('<g class="head" style="animation-delay:0.9s">')
    o.extend(lines[legend_start:step_rects[0]])
    o.append("</g>")

    # ①②③④：row 入场 1.1/1.25/1.4/1.55 + .step 循环 0/-1.5/-3/-4.5
    step_delays = [0, -1.5, -3, -4.5]
    row_delays = [1.1, 1.25, 1.4, 1.55]
    for r in range(4):
        s = step_rects[r]
        e = step_rects[r + 1] if r + 1 < 4 else end
        o.append(f'<g class="row" style="animation-delay:{row_delays[r]}s">')
        o.append(f'<g class="step" style="animation-delay:{step_delays[r]}s">')
        o.extend(lines[s:e])
        o.append("</g>")
        o.append("</g>")

    o.append(lines[end])
    text = eol.join(o)
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
    res["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["rmfix"] = "OK" if (
        re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
        and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)
    ) else "NG"
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_spec_tag_replacement]",
          f"draw={data.count('class=\"draw\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"glow-o={data.count('class=\"glow-o\"')}",
          f"step={data.count('class=\"step\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}")
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:20
