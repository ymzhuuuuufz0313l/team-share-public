#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_scramble_rolling.py  (v2 — Motion Kit v2)

按 MOTION_KIT.md §4.5 把 spec_scramble_rolling.svg 升级为 v2 动画：
- 入场编排（row/head）：标题(0) → 编码前(0.2) → 编码后(0.5) → 三条横条
  (0.85/0.95/1.05) → LFSR 回环(1.15) → n+1 行(1.25) → 图例(1.4)
- draw：编码前→编码后 ↓箭头；三条横条（rect）加 pathLength="100" 依次绘出
  （0.55s，错 0.1s）
- march：绿色虚线 LFSR 反馈环持续行进
- flow：绿条 1 包、蓝条 1 包（左→右，错 phase）
- cellwave：编码后行 K5~K8 黄格 + 末尾 K5（0.3s 递增，2.4s 周期）
- glow-g（1）："n 行截止状态 → n+1 行起始状态（LFSR 连续）" 注释

铁律：源 SVG 只读；text 多重集 / <svg> 开标签 / 几何颜色零改动；纯 CSS 无
script；kit <style> 逐字嵌入为第 3 行（第 2 行字体 <style> 原样保留）；
确定性幂等（只依赖源文件内容）。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_scramble_rolling.svg"
OUT = BASE / "anim" / "spec_scramble_rolling.svg"
NAME = "make_anim_spec_scramble_rolling"

# MOTION_KIT.md §2 — 逐字（不得增删类）
KIT_STYLE = (
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


def idx(lines, *subs, lo=0):
    """唯一命中含全部子串的行号（assert 保护）。"""
    hits = [i for i in range(lo, len(lines)) if all(s in lines[i] for s in subs)]
    assert len(hits) == 1, f"锚点非唯一命中 {subs}: {hits}"
    return hits[0]


def tag_draw(line, delay):
    """给自闭合元素加 class="draw" pathLength="100" + delay。"""
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return (line.rstrip()[:-2].rstrip()
            + f' class="draw" pathLength="100" style="animation-delay:{delay}s"/>')


def tag_class(line, cls, extra=""):
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    ins = f' class="{cls}"' + (f' {extra}' if extra else "")
    return line.rstrip()[:-2].rstrip() + ins + "/>"


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"

    # ---- 结构锚点（源行号，0 基） ----
    title = idx(lines, "滚动机制")
    subtitle = title + 1
    assert "scramble" in lines[subtitle].lower()
    pre_label = idx(lines, ">编码前<")
    arrow = idx(lines, '<line x1="470" y1="158"')
    arrow_label = arrow + 1
    assert "编码后" in lines[arrow_label]
    post_label = idx(lines, ">编码后<", lo=arrow_label + 1)
    bar_g = idx(lines, '<rect x="120" y="282"', 'fill="#16a34a"')
    bar_o = idx(lines, '<rect x="120" y="304"', 'fill="#ea580c"')
    bar_b = idx(lines, '<rect x="214" y="326"', 'fill="#2563eb"')
    bar_label = idx(lines, "加扰区间")
    bar_note = idx(lines, "K 码期间 scramble 停止滚动", lo=bar_label + 1)
    sw1 = idx(lines, '<rect x="1010" y="282"')
    loop = idx(lines, "<path", "M 660 292")
    loop_label = loop + 1
    assert "LFSR" in lines[loop_label]
    next_label = idx(lines, ">n+1 行<")
    bar_low = idx(lines, '<rect x="120" y="444"')
    low_label = bar_low + 1
    assert "继续滚动" in lines[low_label]
    end = len(lines) - 1

    # 编码后行黄格（K5~K8 + 末尾 K5）：rect(x, y=210, #fef9c3) 与其 text 成对
    yellow = [(i, i + 1) for i in range(post_label, bar_g)
              if lines[i].strip().startswith("<rect") and 'fill="#fef9c3"' in lines[i]
              and 'y="210"' in lines[i]]
    for r, t in yellow:
        assert lines[t].strip().startswith("<text"), "黄格 rect 后应紧跟 text"
    assert len(yellow) == 5, f"黄格应为 5 组，实际 {len(yellow)}"

    out = [lines[0], lines[1], KIT_STYLE.replace("\n", eol)]
    out.extend(lines[2:title])          # defs + 背景白 rect

    # 标题(0)
    out.append('<g class="head">')
    out.extend(lines[title:subtitle + 1])
    out.append("</g>")

    # 编码前(0.2)：标签 + 全部格子
    out.append('<g class="row" style="animation-delay:0.2s">')
    out.extend(lines[pre_label:arrow])
    out.append("</g>")

    # 编码前→编码后 ↓箭头：draw（源面板 delay 0.5 + 0.35 = 0.85），标签 fade
    out.append('<g class="fade" style="animation-delay:0.85s">')
    out.append(tag_draw(lines[arrow], 0.85))
    out.append(lines[arrow_label])
    out.append("</g>")

    # 编码后(0.5)：标签 + 格子；黄格 cellwave（0.3s 递增，2.4s 周期）
    out.append('<g class="row" style="animation-delay:0.5s">')
    out.extend(lines[post_label:yellow[0][0]])
    for k, (r, t) in enumerate(yellow):
        out.append('<g class="cellwave" style="animation-duration:2.4s;animation-delay:%gs">' % (0.3 * k))
        out.extend(lines[r:t + 1])
        out.append("</g>")
        if k < len(yellow) - 1:
            nxt = yellow[k + 1][0]
            out.extend(lines[t + 1:nxt])
    out.extend(lines[yellow[-1][1] + 1:bar_g])
    out.append("</g>")

    # 三条横条：row 入场 + rect .draw 依次绘出（0.85/0.95/1.05）；
    # 绿/蓝条各 1 包 flowdot（左→右，错 phase）
    out.append('<g class="row" style="animation-delay:0.85s">')
    out.append(lines[bar_label])
    out.append(tag_draw(lines[bar_g], 0.85))
    out.append('<path class="flowdot" d="M 120 287 L 660 287" stroke="#16a34a" '
               'stroke-width="2.5" pathLength="100" '
               'style="animation-duration:1.6s;animation-delay:1.9s"/>')
    out.append("</g>")
    out.append('<g class="row" style="animation-delay:0.95s">')
    out.append(lines[bar_note])
    out.append(tag_draw(lines[bar_o], 0.95))
    out.append("</g>")
    out.append('<g class="row" style="animation-delay:1.05s">')
    out.append(tag_draw(lines[bar_b], 1.05))
    out.append('<path class="flowdot" d="M 214 331 L 570 331" stroke="#2563eb" '
               'stroke-width="2.5" pathLength="100" '
               'style="animation-duration:1.6s;animation-delay:2.6s"/>')
    out.append("</g>")

    # 图例(1.4)
    out.append('<g class="head" style="animation-delay:1.4s">')
    out.extend(lines[sw1:loop])
    out.append("</g>")

    # LFSR 回环(1.15)：绿色虚线环 .march 持续行进；标签 glow-g
    out.append('<g class="row" style="animation-delay:1.15s">')
    out.append(tag_class(lines[loop], "march"))
    out.append('<g class="glow-g" style="animation-delay:1.4s">')
    out.append(lines[loop_label])
    out.append("</g>")
    out.append("</g>")

    # n+1 行(1.25)：标签 + 格子 + 底部"scramble 继续滚动"绿条 + 注释
    out.append('<g class="row" style="animation-delay:1.25s">')
    out.extend(lines[next_label:bar_low])
    out.append(lines[bar_low])
    out.append(lines[low_label])
    out.append("</g>")

    out.append(lines[end])
    text = eol.join(out) + (eol if tail else "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


def check():
    import os
    NS = "{http://www.w3.org/2000/svg}"
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG {e}"
    texts = lambda p: Counter(el.text or "" for el in
                              ET.parse(str(p)).getroot().iter(f"{NS}text"))
    res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"
    tag = lambda p: re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8")).group(0)
    res["svgtag"] = "OK" if tag(SRC) == tag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["rmfix"] = "OK" if (
        re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
        and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)
    ) else "NG"
    for k, v in res.items():
        print(f"  {k}: {v}")
    return all(v == "OK" for v in res.values())


def main():
    build()
    print(f"[{NAME}]")
    ok = check()
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:20
