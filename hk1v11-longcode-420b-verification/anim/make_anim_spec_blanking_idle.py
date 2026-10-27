#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_blanking_idle.py — v2（Motion Kit v2 · §4.10 spec_blanking_idle）

整体重写 v1。规格（kit §4.10）：
- 行序（入场）：标题(0) → IDLE 面板(0.2) → lane 面板(0.5，Lane1~4 子级联 0.5~0.95)
  → V blanking 行(0.85) → Config 行(1.05) → VBP 行(1.25) → 注释(1.45)。
- cellwave（本图主角·lane 轮换点亮）：每 lane 的 4 个 K 格按轮换序点亮，
  delay = 该格在轮换序中的位置 × 0.6s，duration 2.4s，4 条 lane 共用同一时间线
  （Lane1 K5→K6→K7→K8 / Lane2 K6→K7→K8→K5 / Lane3 K7→K8→K5→K6 / Lane4 K8→K5→K6→K7）。
  源 SVG 每个 lane 行按轮换序排列单元格 → 序内位置 = 行内单元格序号（确定性）。
- cellwave2：IDLE 面板 bit 串格（K5~K8 4 行，0.4s 递增，3.2s 周期）。
- flow：源图 lane 间"箭头"是 text 字形"→"而非 path/line，无可复制的箭头几何；
  按 kit §3/§6 护栏（flowdot 只能复制既有箭头元素、宁缺勿穿）放弃，详见报告 caveats。
- glow（1）：VBP 首行 行盒（glow-b）。
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
SRC = BASE / "spec_blanking_idle.svg"
OUT = BASE / "anim" / "spec_blanking_idle.svg"
NAME = "make_anim_spec_blanking_idle"

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


# 单元：start/end 谓词 + 入场 delay + 特效（idlebit / lane / glow）
UNITS = [
    dict(start=cont("H/V blanking 与 IDLE"), end=cont("为优化 EMI"), head=True),
    dict(start=cont("IDLE pattern · 10-bit"), end=cont("0000111100"), row=0.20, idlebit=True),
    dict(start=cont("lane 间轮换（EMI 优化）"), end=cont("lane 间轮换（EMI 优化）"), row=0.50),
    dict(start=cont(">Lane1<"), end=cont(">Lane2<"), end_before=True, row=0.50, lane=True),
    dict(start=cont(">Lane2<"), end=cont(">Lane3<"), end_before=True, row=0.65, lane=True),
    dict(start=cont(">Lane3<"), end=cont(">Lane4<"), end_before=True, row=0.80, lane=True),
    dict(start=cont(">Lane4<"), end=cont("V blanking 行结构"), end_before=True, row=0.95, lane=True),
    dict(start=cont("V blanking 行结构"), end=cont("H-IDLE"), row=0.85),
    dict(start=cont("Config Line 单独成行"), end=cont('x="918.0"'), row=1.05),
    dict(start=cont(">VBP 首行<"), end=cont('x="688.0"'), row=1.25, glow="glow-b"),
    dict(start=cont("注：Active Line"), end=cont("注：Active Line"), row=1.45),
]


def find_idx(lines, pred, lo, unique=True):
    hits = [i for i in range(lo, len(lines)) if pred(lines[i])]
    if unique:
        assert len(hits) == 1, f"期望唯一命中 (lo={lo})，实际 {len(hits)}: {hits}"
    assert hits, f"无命中 (lo={lo})"
    return hits[0]


def cw_tag(delay, dur):
    return (f'<g class="cellwave" style="animation-delay:{delay:.2f}s;'
            f'animation-duration:{dur}s">')


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
        if u.get("end_before"):
            e = find_idx(lines, u["end"], s + 1, unique=False) - 1
        else:
            e = find_idx(lines, u["end"], s, unique=False)
        assert e >= s and s == cursor, f"单元范围/空隙异常: cursor={cursor} start={s} end={e}"
        if u.get("head"):
            counts["head"] += 1
            out.append('<g class="head">')
        else:
            counts["row"] += 1
            out.append(f'<g class="row" style="animation-delay:{u["row"]:.2f}s">')
        seg = lines[s:e + 1]

        if u.get("idlebit"):
            # IDLE 面板：bit 串格（rect x="124" + 其 text）逐格 cellwave，0.4s 递增，3.2s 周期
            i, n = 0, 0
            while i < len(seg):
                if seg[i].strip().startswith('<rect x="124"'):
                    counts["cellwave"] += 1
                    out.append(cw_tag(n * 0.4, 3.2))
                    out.extend(seg[i:i + 2])
                    out.append("</g>")
                    i += 2
                    n += 1
                else:
                    out.append(seg[i])
                    i += 1
            assert n == 4, f"IDLE bit 串格应 4 格，实际 {n}"
        elif u.get("lane"):
            # lane 行：4 个 K 格按行内序（=轮换序）点亮，delay=位置×0.6s，2.4s 周期
            i, n = 0, 0
            while i < len(seg):
                if seg[i].strip().startswith("<rect") and i + 1 < len(seg) \
                        and seg[i + 1].strip().startswith("<text"):
                    counts["cellwave"] += 1
                    out.append(cw_tag(n * 0.6, 2.4))
                    out.extend(seg[i:i + 2])
                    out.append("</g>")
                    i += 2
                    n += 1
                else:
                    out.append(seg[i])
                    i += 1
            assert n == 4, f"lane 应 4 格，实际 {n}"
        elif u.get("glow"):
            counts["glow"] += 1
            out.append(f'<g class="{u["glow"]}">')
            out.extend(seg)
            out.append("</g>")
        else:
            out.extend(seg)
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
# ymzhu 2026-10-27 10:40
