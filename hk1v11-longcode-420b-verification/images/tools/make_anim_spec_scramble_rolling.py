#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_scramble_rolling.py — v4（1105 · 0924 加扰策略重绘版）

新版静态图（generate_longcode_report_svgs.py · gen_spec_scramble，1200×560）：
① Active/VBK 行（SCREN 门控加扰域 + 三横条）→ 行间顺承（LFSR 连续）→ n+1 行
→ ② Config 行（第一条 VFP 行 · CTRL_F 恒不加扰 · 灰条 key 不推进 + 蓝短条仅编码）
→ ③ K3 边界盒（SCREN=1 行尾 · TX/RX 复位 0XFFFF · RX 延 4 拍）。
旧版「全 payload 加扰（含 CTRL_F）/HBP 行」画法已废弃（归档 archive/20260720/）。

动效规格（沿 MOTION_KIT.md §6.6 骨架，按新版三段结构重排）：
- 行序：标题(0) → ①段(0.2) → 三横条(0.85) → 图例 head(1.05) → 顺承(1.15)
  → n+1 行(1.25) → ②段(1.4/1.5) → ②横条(1.65) → ③K3 盒(1.8)。
  一次性总长 1.8+0.55=2.35s ≤2.5s。
- draw：三横条（绿/橙/蓝）与②灰条/蓝短条 rect .draw+pathLength 依次绘出。
- 稳态·生长（主角）：顺承绿色虚线环 .dashgrow（2.6s）—— Active/VBK 行间
  key 逐轮演化的语义；n 行截止 → n+1 行起始（不复位）。
- 稳态·列车：绿条（SCR_KEY update，540px）2 包白点 4.2s；蓝条 2 包 + 链色
  flowtail（#1d4ed8）；②蓝短条（仅编码仍流动）2 包白点；**②灰条（key 不推进）
  刻意不挂列车** —— 绿条滚动 vs 灰条静止 = 0924 策略的视觉对照。
- 稳态·行波：①/②两行 K5~K8 黄格（各 5 格）cellwave（0.3s 递增，2.4s）。
- 稳态·脉冲：顺承注释 .pulse-t(-0.7s)；③K3 边界盒 .pulse(-1.4s 琥珀)。
- 稳态族：列车/生长/行波/脉冲 = 4 族（≤4 上限内）。

铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动（loop 的
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
SRC = BASE / "images" / "spec_scramble_rolling.svg"
OUT = BASE / "images" / "anim" / "spec_scramble_rolling.svg"
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
    title = idx(lines, "滚动与门控（0924 后）")
    subtitle = title + 1
    assert "加扰域" in lines[subtitle]
    s1_label = idx(lines, "① Active / VBK 行 payload")
    act_label = idx(lines, ">Active 行<")
    bar_label = idx(lines, "加扰区间（CTR_L ~ Dmy）")
    assert bar_label > act_label
    bar_g = idx(lines, '<rect x="120" y="158"', 'fill="#16a34a"')
    bar_o = idx(lines, '<rect x="120" y="180"', 'fill="#ea580c"')
    bar_b = idx(lines, '<rect x="214" y="202"', 'fill="#2563eb"')
    note = idx(lines, "K 码 / IDLE 期间")
    leg1 = idx(lines, '<rect x="1010" y="158"')
    leg4 = idx(lines, "key 不推进</text>", lo=leg1)
    loop = idx(lines, "<path", "M 700 150")
    loop_label = loop + 1
    assert "LFSR 连续" in lines[loop_label]
    nplus_label = idx(lines, ">n+1 行<")
    bar_low = idx(lines, '<rect x="120" y="318"')
    low_label = bar_low + 1
    assert "继续滚动" in lines[low_label]
    s2_label = idx(lines, "② Config 行（第一条 VFP 行）")
    cfg_label = idx(lines, ">Config 行<")
    bar_gr = idx(lines, '<rect x="120" y="414"', 'fill="#9ca3af"')
    bar_gr_label = idx(lines, "SCR_KEY 不推进")
    bar_bs = idx(lines, '<rect x="120" y="436"', 'fill="#2563eb"')
    bar_bs_label = idx(lines, "413/420 ENC（编码但恒不加扰）")
    k3box = idx(lines, '<rect x="60" y="470"')
    k3_end = idx(lines, "K3_FIND_rp_d[3]")
    end = len(lines) - 1

    # ①/② 两行黄格（K5~K8 + 末尾 K5）：rect(#fef9c3) 与其 text 成对
    def yellow_pairs(y):
        ps = [(i, i + 1) for i in range(act_label, k3box)
              if lines[i].strip().startswith("<rect") and 'fill="#fef9c3"' in lines[i]
              and f'y="{y}"' in lines[i]]
        for r, t in ps:
            assert lines[t].strip().startswith("<text"), "黄格 rect 后应紧跟 text"
        return ps

    yellow_a = yellow_pairs(106)
    assert len(yellow_a) == 5, f"①行黄格应 5 组，实际 {len(yellow_a)}"
    yellow_b = yellow_pairs(362)
    assert len(yellow_b) == 5, f"②行黄格应 5 组，实际 {len(yellow_b)}"

    # ---- 组装 ----
    o = [lines[0], lines[1], "<style>\n" + KIT_CSS + "\n</style>"]
    o.extend(lines[2:title])          # defs + 背景白 rect（铁律 4）

    # 标题 head(0)
    o.append('<g class="head">')
    o.extend(lines[title:subtitle + 1])
    o.append("</g>")

    # ①段 row(0.2)：节标题 + 行标签 + 格子；黄格 cellwave（0.3s 递增，2.4s 周期）
    o.append('<g class="row" style="animation-delay:0.2s">')
    o.extend(lines[s1_label:yellow_a[0][0]])
    for k, (r, t) in enumerate(yellow_a):
        o.append('<g class="cellwave" style="animation-duration:2.4s;animation-delay:%gs">' % (0.3 * k))
        o.extend(lines[r:t + 1])
        o.append("</g>")
        if k < len(yellow_a) - 1:
            nxt = yellow_a[k + 1][0]
            o.extend(lines[t + 1:nxt])
    o.extend(lines[yellow_a[-1][1] + 1:bar_label])
    o.append("</g>")

    # 三横条 row(0.85)：rect .draw+pathLength 依次绘出（0.1s 错开）；
    # 绿条（SCR_KEY update）2 包白点（4.2s，-0.75/-2.85 均布）；
    # 蓝条 2 包白点 + 链色 flowtail（#1d4ed8，-1.05/-2.85 与绿错相 0.3，共享 -2.85）
    o.append('<g class="row" style="animation-delay:0.85s">')
    o.append(lines[bar_label])
    o.append(tag_draw(lines[bar_g], 0.85))
    o.append('<path class="flowdot" d="M 120 163 L 660 163" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-0.75s"/>')
    o.append('<path class="flowdot" d="M 120 163 L 660 163" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-2.85s"/>')
    o.append(tag_draw(lines[bar_o], 0.95))
    o.append(lines[note])
    o.append(tag_draw(lines[bar_b], 1.05))
    o.append('<path class="flowdot" d="M 214 207 L 570 207" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-2.85s"/>')
    o.append('<path class="flowdot" d="M 214 207 L 570 207" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-1.05s"/>')
    o.append('<path class="flowtail" d="M 214 207 L 570 207" stroke="#1d4ed8" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-2.85s"/>')
    o.append('<path class="flowtail" d="M 214 207 L 570 207" stroke="#1d4ed8" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-1.05s"/>')
    o.append("</g>")

    # 图例 head(1.05)
    o.append('<g class="head" style="animation-delay:1.05s">')
    o.extend(lines[leg1:leg4 + 1])
    o.append("</g>")

    # 顺承 row(1.15)：绿色虚线环 .dashgrow 持续生长（稳态主角）；注释 .pulse-t
    o.append('<g class="row" style="animation-delay:1.15s">')
    o.append(tag_class(lines[loop], "dashgrow"))
    o.append('<g class="pulse-t" style="animation-delay:-0.7s">')
    o.append(lines[loop_label])
    o.append("</g>")
    o.append("</g>")

    # n+1 行 row(1.25)：标签 + 格子 + 底部绿条（draw）+ 注释
    o.append('<g class="row" style="animation-delay:1.25s">')
    o.extend(lines[nplus_label:bar_low])
    o.append(tag_draw(lines[bar_low], 1.25))
    o.append(lines[low_label])
    o.append("</g>")

    # ②段 row(1.4/1.5)：节标题(1.4) + Config 行格子(1.5，黄格 cellwave 同规格)
    o.append('<g class="row" style="animation-delay:1.4s">')
    o.extend(lines[s2_label:cfg_label + 1])
    o.append("</g>")
    o.append('<g class="row" style="animation-delay:1.5s">')
    o.extend(lines[cfg_label + 1:yellow_b[0][0]])
    for k, (r, t) in enumerate(yellow_b):
        o.append('<g class="cellwave" style="animation-duration:2.4s;animation-delay:%gs">' % (0.3 * k))
        o.extend(lines[r:t + 1])
        o.append("</g>")
        if k < len(yellow_b) - 1:
            nxt = yellow_b[k + 1][0]
            o.extend(lines[t + 1:nxt])
    o.extend(lines[yellow_b[-1][1] + 1:bar_gr])
    o.append("</g>")

    # ②横条 row(1.65)：灰条（key 不推进 —— 刻意无列车：与绿条滚动对照）
    # draw 绘出 + 标签；蓝短条（仅编码仍流动）draw + 2 包白点（4.2s）
    o.append('<g class="row" style="animation-delay:1.65s">')
    o.append(tag_draw(lines[bar_gr], 1.65))
    o.append(lines[bar_gr_label])
    o.append(tag_draw(lines[bar_bs], 1.75))
    o.append(lines[bar_bs_label])
    o.append('<path class="flowdot" d="M 120 441 L 454 441" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-0.35s"/>')
    o.append('<path class="flowdot" d="M 120 441 L 454 441" stroke="#ffffff" '
             'pathLength="100" style="animation-duration:4.2s;animation-delay:-2.45s"/>')
    o.append("</g>")

    # ③ K3 边界盒 row(1.8) + pulse（琥珀英雄）
    o.append('<g class="row" style="animation-delay:1.8s">')
    o.append('<g class="pulse" style="animation-delay:-1.4s">')
    o.extend(lines[k3box:k3_end + 1])
    o.append("</g>")
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
    res["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    res["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    rm = re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
    res["rmfix"] = "OK" if (rm and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    fast = [m.group(1) for m in re.finditer(r'flow(?:dot|tail)[^"]*"[^>]*animation-duration:([0-9.]+)s', data)]
    res["train>=2.4s"] = "OK" if all(float(x) >= 2.4 for x in fast) else f"NG({','.join(fast)})"
    fam = {
        "train":   len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
        "pulse":   len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
        "sweep":   len(re.findall(r'class="[^"]*sweepband', data)),
        "grow":    len(re.findall(r'class="[^"]*dashgrow', data)),
        "wave":    len(re.findall(r'class="[^"]*cellwave', data)),
        "step":    len(re.findall(r'class="[^"]*step"', data)),
    }
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    for k, v in res.items():
        print(f"  {k}: {v}")
    hard = ("xml", "text", "noscript", "nosmil", "keyframes", "svgtag", "size",
            "kit_train", "kit_pulse", "kit_sweep", "rmfix", "no_glow", "train>=2.4s")
    ok = all(str(res.get(k, "NG")) == "OK" or str(res.get(k, "NG")).startswith("OK(") for k in hard) \
        and str(res["steady>=2fam"]).startswith("OK")
    return ok


def main():
    build()
    data = OUT.read_text(encoding="utf-8")
    print(f"[{NAME} v4]",
          f"draw={data.count('class=\"draw\"')}",
          f"dashgrow={data.count('class=\"dashgrow\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"flowtail={data.count('class=\"flowtail\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"pulse={data.count('class=\"pulse\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}")
    ok = check()
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-11-05 11:25
