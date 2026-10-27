#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_bit_order.py — v2（Motion Kit v2 · §4.6 spec_bit_order）

整体重写 v1：v1 的逐边 keyframes 逻辑被 kit 统一 `flow` keyframe 取代。
规格（kit §4.6）：
- 行序（入场）：标题(0) → 网格(0.3) → 发送顺序箭头(0.6) → byte 标签(0.7)
  → 串行化箭头(0.9) → Case1 条带(1.05) → 时间轴(1.5)。一次性总时长 ≤2.5s。
- draw：竖直发送顺序箭头、串行化 ↓箭头、时间轴箭头（delay = 源面板 delay+0.35）。
- flowdot：竖直发送顺序箭头 2 包（0.7s，向上 = Bit0→Bit7）；时间轴 2 包（向右）。
- cellwave：Case1 条带 24 格从左到右（0.08s/格，2.9s 周期）；
  三列网格按列波（R 0 / G 1s / B 2s phase，列内自下而上 0.08s/格，3.6s 周期）。
- glow（1）：网格 R0[0] 格（glow-b，"Bit0 最先发出"英雄，delay 1.4s）。
铁律：源 SVG 只读；数据/几何/颜色零改动；纯 CSS 无 script；kit CSS 逐字嵌入；
reduced-motion 用 kit 给定媒体块；确定性幂等。
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_bit_order.svg"
OUT = BASE / "anim" / "spec_bit_order.svg"
NAME = "make_anim_spec_bit_order"

# —— Motion Kit v2 CSS（MOTION_KIT.md §2 逐字）——
KIT_RULES = [
    ".row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".cellwave{animation:wave 3s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}",
    ".march{animation:march 1.8s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".glow-b{animation:glowB 2.8s ease-in-out infinite}",
    "@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}",
    ".glow-g{animation:glowG 2.8s ease-in-out infinite}",
    "@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}",
    ".glow-o{animation:glowO 2.8s ease-in-out infinite}",
    "@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}",
    ".step{animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}",
]
STYLE = "<style>\n" + "\n".join(KIT_RULES) + "\n</style>"


def cont(*subs):
    def pred(line):
        return all(s in line for s in subs)
    return pred


def find_idx(lines, pred, tag, lo=0, unique=False):
    hits = [i for i in range(lo, len(lines)) if pred(lines[i])]
    if unique:
        assert len(hits) == 1, f"期望唯一命中 {tag}，实际 {len(hits)}: {hits}"
    assert hits, f"未找到锚点: {tag}"
    return hits[0]


def add_draw(line, delay):
    """在首个标签后插入 draw 标签属性（原属性一律不动）。"""
    return re.sub(r"^(<[a-z]+) ", rf'\1 class="draw" pathLength="100" style="animation-delay:{delay:.2f}s" ',
                  line, count=1)


def flowdot(d, color, dur, delay, w=2.5):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
            f'class="flowdot" pathLength="100" '
            f'style="animation-duration:{dur}s;animation-delay:{delay:.2f}s"/>')


def g_cellwave(delay, dur):
    return f'<g class="cellwave" style="animation-delay:{delay:.2f}s;animation-duration:{dur}s">'


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    last = len(lines) - 1

    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[last].strip() == "</svg>", "末行应为 </svg>"

    # ---- 锚点定位 ----
    title_idx = find_idx(lines, cont("数据传输方向"), "标题")
    subtitle_idx = title_idx + 1
    assert "Packet Data 按 byte 依次发送" in lines[subtitle_idx]

    grid_start = find_idx(lines, cont('<rect x="110" y="104"'), "网格首 rect")
    grid_end = find_idx(lines, cont('x="278.0"', ">B0[0]<"), "网格末格 B0[0]")
    arrow_idx = find_idx(lines, cont('d="M 74 356 L 74 122"'), "发送顺序竖箭头")
    byte_start = find_idx(lines, cont(">byte0<"), "byte0 标签")
    byte_end = find_idx(lines, cont(">byte2<"), "byte2 标签")
    serial_idx = find_idx(lines, cont('<line x1="230" y1="420"'), "串行化箭头")
    case1_title = find_idx(lines, cont("Case1 · 413b data"), "Case1 标题")
    strip_start = case1_title + 1
    assert lines[strip_start].strip().startswith('<rect x="60" y="482"'), "Case1 strip 首 rect"
    strip_end = find_idx(lines, cont('x="1069.0"', ">G0[7]<"), "Case1 strip 末格")
    timeline_idx = find_idx(lines, cont('<line x1="60" y1="540"'), "时间轴")
    assert (title_idx < grid_start < grid_end < arrow_idx < byte_start <= byte_end
            < serial_idx < case1_title < strip_start < strip_end < timeline_idx < last)

    out = [lines[0], STYLE.replace("\n", eol), lines[1]]
    out.extend(lines[2:title_idx])  # defs + 白底

    counts = {"row": 0, "head": 0, "draw": 0, "flowdot": 0, "cellwave": 0, "glow-b": 0}

    # head#1 标题（delay 0）
    counts["head"] += 1
    out.append('<g class="head">')
    out.extend(lines[title_idx:subtitle_idx + 1])
    out.append("</g>")

    # row#1 三列网格（0.3）：列波 cellwave（R 0 / G 1 / B 2 phase，列内自下而上 0.08s/格，3.6s 周期）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.3s">')
    col_phase = {"110": 0.0, "178": 1.0, "246": 2.0}
    rows_seen = {"110": 0, "178": 0, "246": 0}
    i = grid_start
    while i <= grid_end:
        m = re.search(r'<rect x="(\d+)"', lines[i])
        assert m and lines[i + 1].strip().startswith("<text"), "网格应为 rect+text 成对"
        x = m.group(1)
        assert x in col_phase, f"网格列 x={x} 异常"
        ci = rows_seen[x]
        rows_seen[x] += 1
        delay = col_phase[x] + (7 - ci) * 0.08  # 自下而上（Bit0 先亮 → Bit7）
        counts["cellwave"] += 1
        out.append(g_cellwave(delay, 3.6))
        if x == "110" and ci == 7:  # R0[0]：Bit0 最先发出 → 英雄辉光
            counts["glow-b"] += 1
            out.append('<g class="glow-b" style="animation-delay:1.4s">')
            out.extend(lines[i:i + 2])
            out.append("</g>")
        else:
            out.extend(lines[i:i + 2])
        out.append("</g>")
        i += 2
    assert sum(rows_seen.values()) == 24, "网格应 24 格"
    out.append("</g>")

    # row#2 发送顺序箭头组（0.6）：竖箭头 draw(0.95) + 2 包 flowdot（向上）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.6s">')
    for j in range(grid_end + 1, byte_start):
        if j == arrow_idx:
            counts["draw"] += 1
            out.append(add_draw(lines[j], 0.95))
            counts["flowdot"] += 2
            out.append(flowdot("M 74 356 L 74 122", "#2563eb", 0.7, 0.2))
            out.append(flowdot("M 74 356 L 74 122", "#2563eb", 0.7, 0.55))
        else:
            out.append(lines[j])
    out.append("</g>")

    # row#3 byte 标签（0.7）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.7s">')
    out.extend(lines[byte_start:byte_end + 1])
    out.append("</g>")

    # row#4 串行化箭头（0.9）：draw(1.25)
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.9s">')
    counts["draw"] += 1
    out.append(add_draw(lines[serial_idx], 1.25))
    out.append(lines[serial_idx + 1])
    assert "串行化" in lines[serial_idx + 1]
    out.append("</g>")

    # row#5 Case1 条带（1.05）：24 格 cellwave 左→右 0.08s/格，2.9s 周期
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:1.05s">')
    out.append(lines[case1_title])
    i = strip_start
    n = 0
    while i <= strip_end:
        assert lines[i].strip().startswith("<rect") and lines[i + 1].strip().startswith("<text"), \
            "条带应为 rect+text 成对"
        counts["cellwave"] += 1
        out.append(g_cellwave(n * 0.08, 2.9))
        out.extend(lines[i:i + 2])
        out.append("</g>")
        i += 2
        n += 1
    assert n == 24, f"条带应 24 格，实际 {n}"
    out.append(lines[strip_end + 1])  # "…" 标注
    assert ">…<" in lines[strip_end + 1]
    out.append("</g>")

    # head#2 时间轴（1.5）：draw(1.85) + 2 包 flowdot（向右）
    counts["head"] += 1
    out.append('<g class="head" style="animation-delay:1.5s">')
    counts["draw"] += 1
    out.append(add_draw(lines[timeline_idx], 1.85))
    counts["flowdot"] += 2
    out.append(flowdot("M 60 540 L 1140 540", "#2563eb", 0.7, 0.2, w=2))
    out.append(flowdot("M 60 540 L 1140 540", "#2563eb", 0.7, 0.55, w=2))
    out.append(lines[timeline_idx + 1])  # "传输时间轴方向"
    assert "传输时间轴方向" in lines[timeline_idx + 1]
    out.append("</g>")

    assert timeline_idx + 2 == last, "时间轴标签后应直接 </svg>"
    out.append(lines[last])

    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return counts


NS = "{http://www.w3.org/2000/svg}"


def check():
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"

    def texts(p):
        return Counter(el.text or "" for el in ET.parse(str(p)).getroot().iter(f"{NS}text"))
    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except Exception as e:
        res["text"] = f"NG: {e}"

    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = f"OK({os.path.getsize(OUT)})" if os.path.getsize(OUT) > 1024 else "NG"
    res["rmfix"] = "OK" if (
        re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
        and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    return res


def main():
    counts = build()
    res = check()
    print(f"[{NAME}] effects:", counts)
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:35
