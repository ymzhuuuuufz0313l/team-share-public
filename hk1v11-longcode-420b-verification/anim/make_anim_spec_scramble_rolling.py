#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_scramble_rolling.py — v4（Motion Kit v4，整体重写；v2 类名/delay 逻辑不沿用）

MOTION_KIT.md §6.6 规格（1200×520）：
- 行序：标题(0) → 编码前(0.2) → 编码后(0.5) → 三横条(0.85/0.95/1.05)
        → LFSR 回环(1.15) → n+1 行(1.25) → 图例(1.4)。
        一次性总长 = 1.4+0.55 = 1.95s ≤ 2.5s。
- draw：↓箭头 delay 1.05（=编码后 0.5+0.55，§5 规则）；
  三横条 rect .draw + pathLength="100" 依次绘出（随各自 row，0.1s 错开）。
- 生长（主角）：LFSR 绿色虚线反馈环 .dashgrow（2.6s）—— key 逐轮演化的语义，
  虚段沿“n 行截止 → n+1 行起始”方向持续生长回卷（取代 v2 的 march）。
- 列车：绿条 1 包、蓝条 1 包 + flowtail（白色高亮在实心条上扫过，左→右错 phase；
  duration 2.2s，delay -0.4 / -1.5）。
- 行波：编码后行 K5~K8 黄格 + 末尾 K5 共 5 格 cellwave（0.3s 递增，2.4s）。
- 脉冲：“n 行截止状态 → n+1 行起始状态（LFSR 连续）”注释 .pulse-t（delay -0.7）。
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动（loop 的
  stroke-dasharray="6,3" 属性原样保留，渲染由 .dashgrow CSS 覆盖）；纯 CSS 无
  script；kit CSS §2 逐字嵌入为行 3（行 2 字体 <style> 原样保留）；源 defs +
  背景 rect 保留；reduced-motion 用 kit 原文；确定性幂等（只依赖源 SVG）。
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


def tag_class(line, cls):
    """给自闭合元素加 class（不删任何既有属性）。"""
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return line.rstrip()[:-2].rstrip() + f' class="{cls}"/>'


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"

    # ---- 结构锚点（源行号，0 基；全部 assert 保护） ----
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

    # ---- 组装 ----
    o = [lines[0], lines[1], "<style>\n" + KIT_CSS + "\n</style>"]
    o.extend(lines[2:title])          # defs + 背景白 rect（铁律 4）

    # 标题 head(0)
    o.append('<g class="head">')
    o.extend(lines[title:subtitle + 1])
    o.append("</g>")

    # 编码前 row(0.2)：标签 + 全部格子
    o.append('<g class="row" style="animation-delay:0.2s">')
    o.extend(lines[pre_label:arrow])
    o.append("</g>")

    # 编码前→编码后 ↓箭头：draw 1.05（=编码后 0.5+0.55，§5 规则），标签同拍淡入
    o.append('<g class="fade" style="animation-delay:1.05s">')
    o.append(tag_draw(lines[arrow], 1.05))
    o.append(lines[arrow_label])
    o.append("</g>")

    # 编码后 row(0.5)：标签 + 格子；黄格 cellwave（0.3s 递增，2.4s 周期）
    o.append('<g class="row" style="animation-delay:0.5s">')
    o.extend(lines[post_label:yellow[0][0]])
    for k, (r, t) in enumerate(yellow):
        o.append('<g class="cellwave" style="animation-duration:2.4s;animation-delay:%gs">' % (0.3 * k))
        o.extend(lines[r:t + 1])
        o.append("</g>")
        if k < len(yellow) - 1:
            nxt = yellow[k + 1][0]
            o.extend(lines[t + 1:nxt])
    o.extend(lines[yellow[-1][1] + 1:bar_g])
    o.append("</g>")

    # 三横条 row(0.85/0.95/1.05)：rect .draw+pathLength 依次绘出（0.1s 错开）；
    # 绿条 1 包、蓝条 1 包+flowtail 白色高亮列车（2.2s，错 phase）
    o.append('<g class="row" style="animation-delay:0.85s">')
    o.append(lines[bar_label])
    o.append(tag_draw(lines[bar_g], 0.85))
    o.append('<path class="flowdot" d="M 120 287 L 660 287" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:2.2s;animation-delay:-0.4s"/>')
    o.append("</g>")
    o.append('<g class="row" style="animation-delay:0.95s">')
    o.append(lines[bar_note])
    o.append(tag_draw(lines[bar_o], 0.95))
    o.append("</g>")
    o.append('<g class="row" style="animation-delay:1.05s">')
    o.append(tag_draw(lines[bar_b], 1.05))
    o.append('<path class="flowdot" d="M 214 331 L 570 331" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:2.2s;animation-delay:-1.5s"/>')
    o.append('<path class="flowtail" d="M 214 331 L 570 331" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:2.2s;animation-delay:-1.5s"/>')
    o.append("</g>")

    # LFSR 回环 row(1.15)：绿色虚线环 .dashgrow 持续生长（稳态主角）；
    # 注释 .pulse-t
    o.append('<g class="row" style="animation-delay:1.15s">')
    o.append(tag_class(lines[loop], "dashgrow"))
    o.append('<g class="pulse-t" style="animation-delay:-0.7s">')
    o.append(lines[loop_label])
    o.append("</g>")
    o.append("</g>")

    # n+1 行 row(1.25)：标签 + 格子 + 底部“scramble 继续滚动”绿条 + 注释
    o.append('<g class="row" style="animation-delay:1.25s">')
    o.extend(lines[next_label:bar_low])
    o.append(lines[bar_low])
    o.append(lines[low_label])
    o.append("</g>")

    # 图例 head(1.4)
    o.append('<g class="head" style="animation-delay:1.4s">')
    o.extend(lines[sw1:loop])
    o.append("</g>")

    o.append(lines[end])
    text = eol.join(o).replace("\n", eol) + (eol if tail else "")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
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
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"
    tag = lambda p: re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8")).group(0)
    res["svgtag"] = "OK" if tag(SRC) == tag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["kit_train"] = "OK" if ".flowdot{" in data and "stroke-width:3.5" in data else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    res["rmfix"] = "OK" if ".flowdot,.flowtail,.sweepband{display:none!important}" in data else "NG"
    for k, v in res.items():
        print(f"  {k}: {v}")
    return all(v == "OK" for v in res.values())


def main():
    build()
    data = OUT.read_text(encoding="utf-8")
    print(f"[{NAME} v4]",
          f"draw={data.count('class=\"draw\"')}",
          f"dashgrow={data.count('class=\"dashgrow\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"flowtail={data.count('class=\"flowtail\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"pulse-t={data.count('class=\"pulse-t\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}",
          f"fade={data.count('class=\"fade\"')}")
    ok = check()
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 16:58
