#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_bit_order.py — v4（Motion Kit v4 · §6.8 spec_bit_order）

整体重写 v2。v4 变化：kit CSS 换 §2 v4 逐字（flowdot 加粗 3.5 + flowtail 拖尾 +
pulse 缩放辉光取代 glow-*）；入场箭头 delay 规则 v2 的 +0.35 → v4 的 +0.55s。

规格（MOTION_KIT.md §6.8，1200×560）：
- 行序（入场）：标题(0) → 三列网格(0.3) → 发送顺序箭头组(0.6) → byte 标签(0.7)
  → 串行化(0.9) → Case1 条带(1.05) → 时间轴(1.5)。
- draw（delay = max(两端 row/head delay)+0.55）：
  竖直↑ 1.15（组 0.6）、串行化↓ 1.6（指向 Case1 1.05）、时间轴→ 2.05（head 1.5）。
- 稳态·列车（族 1）：竖直↑ 2 包 + flowtail（d 同箭头，0.7s，delay 0/-0.35/尾 0，
  向上走 = Bit0→Bit7）；时间轴→ 2 包（0.7s，delay -0.2/-0.55，与竖直列错相）。
- 稳态·行波（族 2）：Case1 条带 24 格左→右 0.08s/格（2.9s）= 逐 bit 发送；
  三列网格按列波（R/G/B phase 0/1/2s，列内自下而上 0.08s/格，3.6s）。
- 稳态·脉冲（族 3）：R0[0] 格 pulse-b（delay -1.4s，"Bit0 最先发出"英雄）。
- flowdot 不穿文字核查：竖直边 x=74±1.75，与 x≥78 的 Bit7/Bit0 标签、
  x∈[83,93] 的旋转注释均不相交；时间轴 y=540±1.75，条带底部 y=514、
  轴标签顶 y≈524，均不相交。

铁律：源 SVG 只读；text 多重集 / <svg> 开标签 / 几何颜色零改动；纯 CSS 无
script/SMIL；保留源 defs 与背景 rect（assert 保护）；kit <style> 逐字嵌入
（第 2 行字体 <style> 之后独立一行）；reduced-motion 用 kit 媒体块；确定性幂等。
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

# —— Motion Kit v4 CSS（MOTION_KIT.md §2 逐字，不增删类）——
KIT_RULES = [
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
]
KIT_STYLE = "<style>\n" + "\n".join(KIT_RULES) + "\n</style>"


def cont(*subs):
    def pred(line):
        return all(s in line for s in subs)
    return pred


def find_idx(lines, pred, tag, lo=0):
    hits = [i for i in range(lo, len(lines)) if pred(lines[i])]
    assert hits, f"未找到锚点: {tag}"
    return hits[0]


def sec(x):
    v = round(x, 3)
    return f"{int(v)}s" if v == int(v) else f"{v:g}s"


def tag_draw(line, delay):
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return (line.rstrip()[:-2].rstrip()
            + f' class="draw" pathLength="100" style="animation-delay:{sec(delay)}"/>')


def flowdot(d, color, dur, delay, w=None):
    st = f"animation-duration:{sec(dur)};animation-delay:{sec(delay)}"
    if w is not None:
        st += f";stroke-width:{w:g}"
    return f'<path d="{d}" stroke="{color}" class="flowdot" pathLength="100" style="{st}"/>'


def flowtail(d, color, dur, delay, w=None):
    st = f"animation-duration:{sec(dur)};animation-delay:{sec(delay)}"
    if w is not None:
        st += f";stroke-width:{w:g}"
    return f'<path d="{d}" stroke="{color}" class="flowtail" pathLength="100" style="{st}"/>'


def cw(delay, dur):
    return (f'<g class="cellwave" style="animation-delay:{sec(delay)};'
            f'animation-duration:{sec(dur)}">')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    last = len(lines) - 1

    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[last].strip() == "</svg>", "末行应为 </svg>"
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    assert lines[8].strip() == "</defs>", "defs 应在 idx8 关闭"
    assert lines[9].lstrip().startswith('<rect width="1200"'), "defs 后应为白底 rect"

    # ---- 锚点定位（0 基）----
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
    assert "串行化" in lines[serial_idx + 1]
    assert "传输时间轴方向" in lines[timeline_idx + 1]
    assert timeline_idx + 2 == last, "时间轴标签后应直接 </svg>"

    out = [lines[0], lines[1], KIT_STYLE.replace("\n", eol)]
    out.extend(lines[2:title_idx])  # defs + 白底（铁律 §0.4）

    counts = {"row": 0, "head": 0, "draw": 0, "flowdot": 0,
              "flowtail": 0, "cellwave": 0, "pulse-b": 0}

    # head#1 标题（delay 0）
    counts["head"] += 1
    out.append('<g class="head">')
    out.extend(lines[title_idx:subtitle_idx + 1])
    out.append("</g>")

    # row#1 三列网格（0.3）：列波 cellwave（R/G/B phase 0/1/2s，列内自下而上
    # 0.08s/格 = Bit0 先亮，3.6s 周期）；R0[0] 格 pulse-b 英雄
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
        delay = col_phase[x] + (7 - ci) * 0.08
        counts["cellwave"] += 1
        out.append(cw(delay, 3.6))
        if x == "110" and ci == 7:  # R0[0]：Bit0 最先发出 → 脉冲英雄
            counts["pulse-b"] += 1
            out.append('<g class="pulse-b" style="animation-delay:-1.4s">')
            out.extend(lines[i:i + 2])
            out.append("</g>")
        else:
            out.extend(lines[i:i + 2])
        out.append("</g>")
        i += 2
    assert sum(rows_seen.values()) == 24, "网格应 24 格"
    out.append("</g>")

    # row#2 发送顺序箭头组（0.6）：竖箭头 draw(1.15=0.6+0.55) + 列车 2 包+尾
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.6s">')
    for j in range(grid_end + 1, byte_start):
        if j == arrow_idx:
            counts["draw"] += 1
            out.append(tag_draw(lines[j], 1.15))
            counts["flowdot"] += 2
            counts["flowtail"] += 1
            out.append(flowdot("M 74 356 L 74 122", "#2563eb", 0.7, 0.0))
            out.append(flowdot("M 74 356 L 74 122", "#2563eb", 0.7, -0.35))
            out.append(flowtail("M 74 356 L 74 122", "#2563eb", 0.7, 0.0))
        else:
            out.append(lines[j])
    out.append("</g>")

    # row#3 byte 标签（0.7）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.7s">')
    out.extend(lines[byte_start:byte_end + 1])
    out.append("</g>")

    # row#4 串行化箭头（0.9）：draw(1.6 = Case1 1.05 + 0.55，避免悬浮箭头)
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.9s">')
    counts["draw"] += 1
    out.append(tag_draw(lines[serial_idx], 1.6))
    out.append(lines[serial_idx + 1])
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
        out.append(cw(n * 0.08, 2.9))
        out.extend(lines[i:i + 2])
        out.append("</g>")
        i += 2
        n += 1
    assert n == 24, f"条带应 24 格，实际 {n}"
    assert ">…<" in lines[strip_end + 1]
    out.append(lines[strip_end + 1])  # "…" 标注
    out.append("</g>")

    # head#2 时间轴（1.5）：draw(2.05=1.5+0.55) + 列车 2 包（与竖列错相）
    counts["head"] += 1
    out.append('<g class="head" style="animation-delay:1.5s">')
    counts["draw"] += 1
    out.append(tag_draw(lines[timeline_idx], 2.05))
    counts["flowdot"] += 2
    out.append(flowdot("M 60 540 L 1140 540", "#2563eb", 0.7, -0.2))
    out.append(flowdot("M 60 540 L 1140 540", "#2563eb", 0.7, -0.55))
    out.append(lines[timeline_idx + 1])  # "传输时间轴方向"
    out.append("</g>")

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
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = f"OK({os.path.getsize(OUT)})" if os.path.getsize(OUT) > 1024 else "NG"
    res["rmfix"] = "OK" if (
        re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
        and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
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
# ymzhu 2026-10-28 16:51
