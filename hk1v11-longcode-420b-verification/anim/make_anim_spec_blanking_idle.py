#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_blanking_idle.py — v4（Motion Kit v4 · §6.10 spec_blanking_idle）

整体重写 v2。v4 变化：kit CSS 换 §2 v4 逐字（cellwave 带缩放 + pulse 缩放辉光
取代 glow-*）；v2 的 cellwave2 统一并入 v4 cellwave 类。

规格（MOTION_KIT.md §6.10，1200×660）：
- 行序（入场）：标题(0) → IDLE 面板(0.2) → lane 面板(0.5，Lane1~4 子级联
  0.5/0.65/0.8/0.95) → V blanking(0.85) → Config(1.05) → VBP(1.25) → 注释(1.45)。
- 稳态·行波（族 1，本图主角·lane 轮换演出）：每 lane 的 4 个 K 格按轮换序点亮
  （Lane1 K5→K6→K7→K8；Lane2 K6→…；Lane3 K7→…；Lane4 K8→…）：每格
  class="cellwave" + 内联 animation-duration:2.4s，delay = 轮换序位置 × 0.6s，
  4 lane 共用时间线 = 轮换偏移可视化（源 SVG 每 lane 行已按轮换序排列单元格，
  序内位置 = 行内单元格序号，确定性）。IDLE 面板 bit 串格 0.4s 递增（3.2s）。
- 稳态·脉冲（族 2）：VBP 首行行盒 pulse-b（delay -1.4s）。
- 列车：v4 §6.10 要求"每 lane 格间小箭头（8 条）各 1 包"，但源图 lane 间箭头
  是 text 字形"→"而非 path/line，全图无任何可复制的箭头几何（铁律 §0.3 只允许
  复制箭头得到装饰路径）→ 按 §5"宁缺勿穿"护栏放弃，见报告 caveats。
  行波+脉冲已满足稳态 ≥2 族硬指标。
- 无 path/line 元素 → 本图无 draw；source 图内箭头语义由行波轮换承担。

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
SRC = BASE / "spec_blanking_idle.svg"
OUT = BASE / "anim" / "spec_blanking_idle.svg"
NAME = "make_anim_spec_blanking_idle"

# —— Motion Kit v4 CSS（MOTION_KIT.md §2 逐字，不增删类）——
KIT_RULES = [
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
]
KIT_STYLE = "<style>\n" + "\n".join(KIT_RULES) + "\n</style>"


def cont(*subs):
    def pred(line):
        return all(s in line for s in subs)
    return pred


# 单元：start/end 谓词 + 入场 delay + 特效（idlebit / lane / pulse）
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
    dict(start=cont(">VBP 首行<"), end=cont('x="688.0"'), row=1.25, pulse="pulse-b"),
    dict(start=cont("注：Active Line"), end=cont("注：Active Line"), row=1.45),
]


def find_idx(lines, pred, lo, unique=True):
    hits = [i for i in range(lo, len(lines)) if pred(lines[i])]
    if unique:
        assert len(hits) == 1, f"期望唯一命中 (lo={lo})，实际 {len(hits)}: {hits}"
    assert hits, f"无命中 (lo={lo})"
    return hits[0]


def sec(x):
    v = round(x, 3)
    return f"{int(v)}s" if v == int(v) else f"{v:g}s"


def cw(delay, dur):
    return (f'<g class="cellwave" style="animation-delay:{sec(delay)};'
            f'animation-duration:{sec(dur)}">')


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

    out = [lines[0], lines[1], KIT_STYLE.replace("\n", eol)]
    out.extend(lines[2:bg + 1])  # defs + 白底（铁律 §0.4）

    counts = {"row": 0, "head": 0, "cellwave": 0, "pulse-b": 0}
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
                    out.append(cw(n * 0.4, 3.2))
                    out.extend(seg[i:i + 2])
                    out.append("</g>")
                    i += 2
                    n += 1
                else:
                    out.append(seg[i])
                    i += 1
            assert n == 4, f"IDLE bit 串格应 4 格，实际 {n}"
        elif u.get("lane"):
            # lane 行：4 个 K 格按行内序（=轮换序）点亮，delay=位置×0.6s，2.4s 周期；
            # 4 lane 共用时间线 → Lane1 K5 与 Lane2 K6 同步亮 = 轮换偏移可视化
            i, n = 0, 0
            while i < len(seg):
                if seg[i].strip().startswith("<rect") and i + 1 < len(seg) \
                        and seg[i + 1].strip().startswith("<text"):
                    counts["cellwave"] += 1
                    out.append(cw(n * 0.6, 2.4))
                    out.extend(seg[i:i + 2])
                    out.append("</g>")
                    i += 2
                    n += 1
                else:
                    out.append(seg[i])
                    i += 1
            assert n == 4, f"lane 应 4 格，实际 {n}"
        elif u.get("pulse"):
            counts["pulse-b"] += 1
            out.append(f'<g class="{u["pulse"]}" style="animation-delay:-1.4s">')
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
