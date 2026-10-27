#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_lsp_kcode.py  (v2 — Motion Kit v2)

按 MOTION_KIT.md §4.9 把 spec_lsp_kcode.svg 升级为 v2 动画：
- 入场编排（row/head）：标题(0) → 编码前(0.2) → 括号(0.5) → 编码后(0.65)
  → dmy 注释(0.8) → K 表 4 行(1.0/1.15/1.3/1.45) → 先发/后发(1.7)
- draw：括号下划线（path，实线，delay=0.5+0.35）；先发/后发 2 个箭头
  （delay=1.7+0.35）
- cellwave：编码前/编码后两行 0xEA~0xED 橙格左右行进波（0.1s/格，3s 周期，
  两行同相）；K 表 4 行 bit 串按行 phase（0.5s 递增，3.6s 周期）
- glow-b（2）：编码前 K3 格（delay 1.4s）；K 表 K3 行（delay 2.8s，phase 差 1.4s）
- flow：先发/后发箭头各 2 包（按箭头标注方向：向上，stroke-width 2 —— 边
  仅 14px 高，按 kit 护栏用细笔避免压线）
- 括号下划线为实线（无 dasharray）→ 不用 march

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
SRC = BASE / "spec_lsp_kcode.svg"
OUT = BASE / "anim" / "spec_lsp_kcode.svg"
NAME = "make_anim_spec_lsp_kcode"

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
    hits = [i for i in range(lo, len(lines)) if all(s in lines[i] for s in subs)]
    assert len(hits) == 1, f"锚点非唯一命中 {subs}: {hits}"
    return hits[0]


def tag_draw(line, delay):
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return (line.rstrip()[:-2].rstrip()
            + f' class="draw" pathLength="100" style="animation-delay:{delay}s"/>')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"

    # ---- 结构锚点（源行号，0 基） ----
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
    def orange_pairs(y, hi):
        ps = [(i, i + 1) for i in range(hi[0], hi[1])
              if lines[i].strip().startswith("<rect") and 'fill="#ffedd5"' in lines[i]
              and f'y="{y}"' in lines[i]]
        for r, t in ps:
            assert lines[t].strip().startswith("<text"), "橙格 rect 后应紧跟 text"
        return ps

    pre_pairs = orange_pairs(114, (pre_label, bracket))
    post_pairs = orange_pairs(210, (post_label, dmy_note))
    assert len(pre_pairs) == 12 and len(post_pairs) == 12, \
        f"橙格应各 12 组，实际 pre={len(pre_pairs)} post={len(post_pairs)}"

    # 编码前 K3 格（glow-b 英雄）：rect x=760 y=114 + text K3
    pre_k3_pair = next(((i, i + 1) for i in range(pre_label, bracket)
                        if lines[i].strip().startswith("<rect") and 'x="760"' in lines[i]
                        and 'y="114"' in lines[i]))
    assert ">K3<" in lines[pre_k3_pair[1]], "编码前 K3 格定位失败"

    def emit_row_with_wave(out, lo, hi, pairs, delay0, step, dur):
        """行组入场 + 橙格 cellwave（对 pair 以外元素按原样夹层输出）。"""
        out.append('<g class="row" style="animation-delay:%gs">' % delay0)
        cur = lo
        for k, (r, t) in enumerate(pairs):
            out.extend(lines[cur:r])
            out.append('<g class="cellwave" style="animation-duration:%gs;animation-delay:%gs">'
                       % (dur, round(step * k, 2)))
            out.extend(lines[r:t + 1])
            out.append("</g>")
            cur = t + 1
        out.extend(lines[cur:hi])
        out.append("</g>")

    out = [lines[0], lines[1], KIT_STYLE.replace("\n", eol)]
    out.extend(lines[2:title])          # defs + 背景白 rect

    # 标题(0)
    out.append('<g class="head">')
    out.extend(lines[title:subtitle + 1])
    out.append("</g>")

    # 编码前(0.2)：K3 格外套 glow-b（delay 1.4，入场后进入辉光）
    out.append('<g class="row" style="animation-delay:0.2s">')
    cur = pre_label
    for k, (r, t) in enumerate(pre_pairs):
        out.extend(lines[cur:r])
        out.append('<g class="cellwave" style="animation-duration:3s;animation-delay:%gs">'
                   % round(0.1 * k, 2))
        if (r, t) == pre_k3_pair:
            out.append('<g class="glow-b" style="animation-delay:1.4s">')
            out.extend(lines[r:t + 1])
            out.append("</g>")
        else:
            out.extend(lines[r:t + 1])
        out.append("</g>")
        cur = t + 1
    out.extend(lines[cur:pre_k3_pair[0]])
    out.append('<g class="glow-b" style="animation-delay:1.4s">')
    out.extend(lines[pre_k3_pair[0]:pre_k3_pair[1] + 1])
    out.append("</g>")
    out.extend(lines[pre_k3_pair[1] + 1:bracket])
    out.append("</g>")

    # 括号(0.5)：实线下划线 draw（0.5+0.35=0.85）+ "32 Byte" 标注
    out.append('<g class="fade" style="animation-delay:0.85s">')
    out.append(tag_draw(lines[bracket], 0.85))
    out.append(lines[bracket_label])
    out.append("</g>")

    # 编码后(0.65)：橙格行波与编码前同相（0.1s/格，3s 周期）
    emit_row_with_wave(out, post_label, dmy_note, post_pairs, 0.65, 0.1, 3)

    # dmy 注释(0.8)
    out.append('<g class="head" style="animation-delay:0.8s">')
    out.append(lines[dmy_note])
    out.append("</g>")

    # K 码表：节标题随 K1 行(1.0)；bit 串按行 cellwave（0.5s 递增，3.6s）
    # K3 行整体 glow-b（delay 2.8 = 1.4 + phase 差 1.4）
    for n, (row, bit, delay, wd) in enumerate([
            (k1, k1_bit, 1.0, 0.0), (k2, k2_bit, 1.15, 0.5),
            (k3, k3_bit, 1.3, 1.0), (k4, k4_bit, 1.45, 1.5)]):
        out.append('<g class="row" style="animation-delay:%gs">' % delay)
        if n == 0:
            out.append(lines[khead])
        if n == 2:  # K3 行：外层辉光、内层 bit 串行波
            out.append('<g class="glow-b" style="animation-delay:2.8s">')
            out.extend(lines[row:row + 2])          # K chip rect+text
            out.append('<g class="cellwave" style="animation-duration:3.6s;animation-delay:1s">')
            out.extend(lines[row + 2:bit + 1])      # bit 白盒 rect + bit text
            out.append("</g>")
            out.append("</g>")
        else:
            out.extend(lines[row:row + 2])
            out.append('<g class="cellwave" style="animation-duration:3.6s;animation-delay:%gs">' % wd)
            out.extend(lines[row + 2:bit + 1])
            out.append("</g>")
        out.append("</g>")

    # 先发/后发(1.7)：2 箭头 draw（1.7+0.35=2.05）+ 各 2 包 flowdot（0.7s，
    # 错 0.35s 成列车；边仅 14px 高 → stroke-width 2）
    out.append('<g class="row" style="animation-delay:1.7s">')
    out.append(tag_draw(lines[arrow_first], 2.05))
    out.append(lines[arrow_first_label])
    out.append('<path class="flowdot" d="M 950 542 L 950 528" stroke="#2563eb" '
               'stroke-width="2" pathLength="100" '
               'style="animation-duration:0.7s;animation-delay:2.2s"/>')
    out.append('<path class="flowdot" d="M 950 542 L 950 528" stroke="#2563eb" '
               'stroke-width="2" pathLength="100" '
               'style="animation-duration:0.7s;animation-delay:2.55s"/>')
    out.append(tag_draw(lines[arrow_last], 2.05))
    out.append(lines[arrow_last_label])
    out.append('<path class="flowdot" d="M 178 542 L 178 528" stroke="#2563eb" '
               'stroke-width="2" pathLength="100" '
               'style="animation-duration:0.7s;animation-delay:2.3s"/>')
    out.append('<path class="flowdot" d="M 178 542 L 178 528" stroke="#2563eb" '
               'stroke-width="2" pathLength="100" '
               'style="animation-duration:0.7s;animation-delay:2.65s"/>')
    out.append(lines[dir_note])
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
