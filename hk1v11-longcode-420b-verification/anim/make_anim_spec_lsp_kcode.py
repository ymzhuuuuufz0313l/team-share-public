#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_lsp_kcode.py — v4（Motion Kit v4 · §6.9 spec_lsp_kcode）

整体重写 v2。v4 变化：kit CSS 换 §2 v4 逐字（flowdot 加粗 3.5 + flowtail 拖尾 +
pulse 缩放辉光取代 glow-*）；入场箭头 delay 规则 v2 的 +0.35 → v4 的 +0.55s。

规格（MOTION_KIT.md §6.9，1200×620）：
- 行序（入场）：标题(0) → 编码前(0.2) → 括号(0.5) → 编码后(0.65) → dmy 注释(0.8)
  → K 表 4 行(1.0/1.15/1.3/1.45) → 先发/后发(1.7)。
- draw：括号实线下划线（1.05 = 0.5+0.55）；先发/后发 2 箭头
  （2.05 = max(两端 K 表行 1.45)+0.55）。
- 稳态·行波（族 1）：编码前/后两行 0xEA~0xED 橙格左右行进（0.1s/格，3s，
  两行同相）；K 表 4 行 bit 串按行 phase（0/0.5/1.0/1.5s，3.6s）。
- 稳态·列车（族 2）：先发/后发箭头各 2 包 + flowtail（d 同箭头向上 = 按标注
  方向走，0.7s；先发 delay 0/-0.35，后发 -0.15/-0.5 错相）。边仅 14px 高且上端
  贴 K4 bit 盒 → 按 §5 护栏内联 stroke-width：dot 2.5 / tail 4。
- 稳态·脉冲（族 3）：编码前行 K3 格 pulse-b（delay -1.4s）；K 表 K3 行 pulse-b
  （delay 0s，phase 差 1.4s）。
- 括号下划线源为实线（无 dasharray）→ 用 draw，不用 march。

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
SRC = BASE / "spec_lsp_kcode.svg"
OUT = BASE / "anim" / "spec_lsp_kcode.svg"
NAME = "make_anim_spec_lsp_kcode"

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


def idx(lines, *subs, lo=0):
    hits = [i for i in range(lo, len(lines)) if all(s in lines[i] for s in subs)]
    assert len(hits) == 1, f"锚点非唯一命中 {subs}: {hits}"
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
    tail = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    assert lines[8].strip() == "</defs>", "defs 应在 idx8 关闭"
    assert lines[9].lstrip().startswith('<rect width="1200"'), "defs 后应为白底 rect"

    # ---- 结构锚点（0 基）----
    title = idx(lines, "LSP 序列与 K 码")
    subtitle = title + 1
    assert "K3 放在序列最后" in lines[subtitle]
    pre_label = idx(lines, ">编码前<")
    post_label = idx(lines, ">编码后<")
    bracket = idx(lines, "<path", "M 120 158")
    bracket_label = bracket + 1
    assert "32 Byte" in lines[bracket_label]
    dmy_note = idx(lines, "280b")
    khead = idx(lines, "K 码（K1 ~ K4）· 40-bit")
    k1 = idx(lines, '<rect x="60" y="350"')
    k1_bit = k1 + 3
    k2 = idx(lines, '<rect x="60" y="396"')
    k2_bit = k2 + 3
    k3 = idx(lines, '<rect x="60" y="442"')
    k3_bit = k3 + 3
    k4 = idx(lines, '<rect x="60" y="488"')
    k4_bit = k4 + 3
    arrow_first = idx(lines, 'x1="950"', "<line")
    arrow_first_label = arrow_first + 1
    assert "先发" in lines[arrow_first_label]
    arrow_last = idx(lines, 'x1="178"', "<line")
    arrow_last_label = arrow_last + 1
    assert "后发" in lines[arrow_last_label]
    dir_note = idx(lines, "串行发送方向")
    end = len(lines) - 1

    # 橙格：rect(x, y=114/210, #ffedd5) + 紧随 text 成对（每行 12 格）
    def orange_pairs(y, lo, hi):
        ps = [(i, i + 1) for i in range(lo, hi)
              if lines[i].strip().startswith("<rect") and 'fill="#ffedd5"' in lines[i]
              and f'y="{y}"' in lines[i]]
        for r, t in ps:
            assert lines[t].strip().startswith("<text"), "橙格 rect 后应紧跟 text"
        return ps

    pre_pairs = orange_pairs(114, pre_label, bracket)
    post_pairs = orange_pairs(210, post_label, dmy_note)
    assert len(pre_pairs) == 12 and len(post_pairs) == 12, \
        f"橙格应各 12 组，实际 pre={len(pre_pairs)} post={len(post_pairs)}"

    # 编码前 K3 格（pulse-b 英雄）：rect x=760 y=114 + text K3
    pre_k3 = next(i for i in range(pre_label, bracket)
                  if lines[i].strip().startswith("<rect") and 'x="760"' in lines[i]
                  and 'y="114"' in lines[i])
    assert ">K3<" in lines[pre_k3 + 1], "编码前 K3 格定位失败"

    out = [lines[0], lines[1], KIT_STYLE.replace("\n", eol)]
    out.extend(lines[2:title])          # defs + 背景白 rect（铁律 §0.4）

    counts = {"row": 0, "head": 0, "draw": 0, "fade": 0, "flowdot": 0,
              "flowtail": 0, "cellwave": 0, "pulse-b": 0}

    # 标题(0)
    counts["head"] += 1
    out.append('<g class="head">')
    out.extend(lines[title:subtitle + 1])
    out.append("</g>")

    # 编码前(0.2)：12 橙格 cellwave（0.1s/格，3s）+ K3 格 pulse-b（-1.4s 相位）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.2s">')
    cur = pre_label
    for k, (r, t) in enumerate(pre_pairs):
        out.extend(lines[cur:r])
        counts["cellwave"] += 1
        out.append(cw(0.1 * k, 3))
        out.extend(lines[r:t + 1])
        out.append("</g>")
        cur = t + 1
    out.extend(lines[cur:pre_k3])
    counts["pulse-b"] += 1
    out.append('<g class="pulse-b" style="animation-delay:-1.4s">')
    out.extend(lines[pre_k3:pre_k3 + 2])
    out.append("</g>")
    out.extend(lines[pre_k3 + 2:bracket])
    out.append("</g>")

    # 括号(0.5)：实线下划线 draw(1.05=0.5+0.55) + "32 Byte" 标注（fade 同步）
    counts["fade"] += 1
    out.append('<g class="fade" style="animation-delay:1.05s">')
    counts["draw"] += 1
    out.append(tag_draw(lines[bracket], 1.05))
    out.append(lines[bracket_label])
    out.append("</g>")

    # 编码后(0.65)：橙格行波与编码前同相（0.1s/格，3s）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:0.65s">')
    cur = post_label
    for k, (r, t) in enumerate(post_pairs):
        out.extend(lines[cur:r])
        counts["cellwave"] += 1
        out.append(cw(0.1 * k, 3))
        out.extend(lines[r:t + 1])
        out.append("</g>")
        cur = t + 1
    out.extend(lines[cur:dmy_note])
    out.append("</g>")

    # dmy 注释(0.8)
    counts["head"] += 1
    out.append('<g class="head" style="animation-delay:0.8s">')
    out.append(lines[dmy_note])
    out.append("</g>")

    # K 码表 4 行(1.0/1.15/1.3/1.45)：节标题随 K1 行；bit 串按行 cellwave
    # （0/0.5/1.0/1.5s，3.6s）；K3 行整体 pulse-b（delay 0s，与编码前 K3 差 1.4s）
    for n, (row, bit, delay, wd) in enumerate([
            (k1, k1_bit, 1.0, 0.0), (k2, k2_bit, 1.15, 0.5),
            (k3, k3_bit, 1.3, 1.0), (k4, k4_bit, 1.45, 1.5)]):
        counts["row"] += 1
        out.append(f'<g class="row" style="animation-delay:{sec(delay)}">')
        if n == 0:
            out.append(lines[khead])
        if n == 2:  # K3 行：外层脉冲、内层 bit 串行波
            counts["pulse-b"] += 1
            out.append('<g class="pulse-b" style="animation-delay:0s">')
            out.extend(lines[row:row + 2])          # K chip rect+text
            counts["cellwave"] += 1
            out.append(cw(wd, 3.6))
            out.extend(lines[row + 2:bit + 1])      # bit 白盒 rect + bit text
            out.append("</g>")
            out.append("</g>")
        else:
            out.extend(lines[row:row + 2])
            counts["cellwave"] += 1
            out.append(cw(wd, 3.6))
            out.extend(lines[row + 2:bit + 1])
            out.append("</g>")
        out.append("</g>")

    # 先发/后发(1.7)：2 箭头 draw(2.05 = K4 行 1.45 + 0.55) + 各 2 包 + flowtail
    # （0.7s；边仅 14px 高且上端贴盒 → §5 护栏内联 stroke-width dot 2.5 / tail 4）
    counts["row"] += 1
    out.append('<g class="row" style="animation-delay:1.7s">')
    counts["draw"] += 1
    out.append(tag_draw(lines[arrow_first], 2.05))
    out.append(lines[arrow_first_label])
    counts["flowdot"] += 2
    counts["flowtail"] += 1
    out.append(flowdot("M 950 542 L 950 528", "#2563eb", 0.7, 0.0, w=2.5))
    out.append(flowdot("M 950 542 L 950 528", "#2563eb", 0.7, -0.35, w=2.5))
    out.append(flowtail("M 950 542 L 950 528", "#2563eb", 0.7, 0.0, w=4))
    counts["draw"] += 1
    out.append(tag_draw(lines[arrow_last], 2.05))
    out.append(lines[arrow_last_label])
    counts["flowdot"] += 2
    counts["flowtail"] += 1
    out.append(flowdot("M 178 542 L 178 528", "#2563eb", 0.7, -0.15, w=2.5))
    out.append(flowdot("M 178 542 L 178 528", "#2563eb", 0.7, -0.5, w=2.5))
    out.append(flowtail("M 178 542 L 178 528", "#2563eb", 0.7, -0.15, w=4))
    out.append(lines[dir_note])
    out.append("</g>")

    out.append(lines[end])
    text = eol.join(out) + (eol if tail else "")
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
