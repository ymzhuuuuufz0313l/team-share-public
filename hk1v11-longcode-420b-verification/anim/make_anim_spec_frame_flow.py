#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_frame_flow.py — v2（Motion Kit v2 · §4.8 spec_frame_flow）

整体重写 v1。规格（kit §4.8）：
- 行序（入场）：标题(0) → Clock 条(0.15) → LSP 条(0.35) → Frame c 行(0.55)
  → Active 4 行(0.7/0.85/1.0/1.15) → c+1 行(1.3) → VBK 2 行(1.45/1.6)
  → 括号+省略(1.75)。一次性总时长 ≤2.5s。
- cellwave（本图主角·帧滚动波）：所有"行"（Frame c、4 个 Active、c+1、2 个 VBK）
  整行组包 <g class="cellwave">，自上而下 delay 0.18s 递增，周期 4.5s（内联 duration）。
- glow（2）：LSP 条（glow-b）；"Config Line · Frame c+1 配置"行盒（glow-g，0717 修复点，delay 1.4s）。
- 不加 flow/breathe（行波已是主角）；本图无实线箭头 → 无 draw。
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
SRC = BASE / "spec_frame_flow.svg"
OUT = BASE / "anim" / "spec_frame_flow.svg"
NAME = "make_anim_spec_frame_flow"

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

CW_DUR = 4.5  # 帧滚动波周期（kit §4.8）


def cont(*subs):
    def pred(line):
        return all(s in line for s in subs)
    return pred


# 顺序单元：start/end 谓词 + 入场 delay + cellwave delay（None=不包波） + glow（可选）
UNITS = [
    dict(start=cont("420b 帧数据流"), end=cont("LSP 训练 →"), row=None, head=True),
    dict(start=cont('<rect x="210" y="100"'), end=cont("Clock training pattern"), row=0.15),
    dict(start=cont('<rect x="210" y="146"'), end=cont("LSP（K2"), row=0.35,
         glow=("glow-b", None)),
    dict(start=cont('<rect x="210" y="192"'), end=cont("Config Line（Frame c 配置）"),
         row=0.55, cw=0.00),
    dict(start=cont('<rect x="210" y="238"'), end=cont("H blanking"), row=0.70, cw=0.18),
    dict(start=cont('<rect x="210" y="284"'), end=cont('y="356"'), row=0.85, cw=0.36),
    dict(start=cont('<rect x="210" y="364"'), end=cont("H blanking"), row=1.00, cw=0.54),
    dict(start=cont("M 194 242"), end=cont(">Video Active<"), row=1.15),
    dict(start=cont('<rect x="202" y="412"'), end=cont("0717v1：单独成行"), row=1.30,
         cw=0.72, glow=("glow-g", 1.4)),
    dict(start=cont('<rect x="210" y="476"'), end=cont("H blanking"), row=1.45, cw=0.90),
    dict(start=cont('<rect x="210" y="522"'), end=cont("H blanking"), row=1.60, cw=1.08),
    dict(start=cont('y="592"'), end=cont(">V blanking<"), row=1.75),
]


def find_idx(lines, pred, lo, unique=True):
    hits = [i for i in range(lo, len(lines)) if pred(lines[i])]
    if unique:
        assert len(hits) == 1, f"期望唯一命中 (lo={lo})，实际 {len(hits)}: {hits}"
    assert hits, f"无命中 (lo={lo})"
    return hits[0]


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    assert lines[0].startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    svg_end = len(lines) - 1
    defs_end = next(i for i in range(2, svg_end) if lines[i].strip() == "</defs>")
    bg = defs_end + 1
    assert lines[bg].lstrip().startswith('<rect width="1200"'), "defs 后应为白底 rect"
    content_start = bg + 1

    out = [lines[0], STYLE.replace("\n", eol), lines[1]]
    out.extend(lines[2:bg + 1])

    counts = {"row": 0, "head": 0, "cellwave": 0, "glow": 0}
    cursor = content_start
    for u in UNITS:
        s = find_idx(lines, u["start"], cursor, unique=False)
        e = find_idx(lines, u["end"], s, unique=False)
        assert e >= s and s == cursor, f"单元范围/空隙异常: cursor={cursor} start={s} end={e}"
        if u.get("head"):
            counts["head"] += 1
            out.append('<g class="head">')
        else:
            counts["row"] += 1
            out.append(f'<g class="row" style="animation-delay:{u["row"]:.2f}s">')
        glow = u.get("glow")
        if u.get("cw") is not None:
            counts["cellwave"] += 1
            out.append(f'<g class="cellwave" style="animation-delay:{u["cw"]:.2f}s;'
                       f'animation-duration:{CW_DUR}s">')
        if glow:
            counts["glow"] += 1
            tag = f'<g class="{glow[0]}"'
            tag += (f' style="animation-delay:{glow[1]:.1f}s">' if glow[1] is not None else '>')
            out.append(tag)
        out.extend(lines[s:e + 1])
        if glow:
            out.append("</g>")
        if u.get("cw") is not None:
            out.append("</g>")
        out.append("</g>")
        cursor = e + 1

    assert cursor == svg_end, f"内容行未完全覆盖: cursor={cursor}, svg_end={svg_end}"
    out.append(lines[svg_end])

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
# ymzhu 2026-10-27 10:38
