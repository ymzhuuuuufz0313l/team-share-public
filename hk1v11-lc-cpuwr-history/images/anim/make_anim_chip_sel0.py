#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chip_sel0_register_map.svg -> 动画版（纯 CSS、自包含、无 <script>）。

确定性行级变换（不重排、不改动任何数据文本/几何/颜色）：
1. 行标签 = <text x="158" ... font-weight="600">（每行一个），把行标签起（含行尾 pill）
   到下一行标签前的全部元素包进 <g class="row" style="animation-delay: 行序号*0.03s">；
   标题/位号列/POR 表头包进第一个 <g class="head">，图例+脚注包进第二个 <g class="head">。
2. 变更单元格脉冲：0x1D 行 khead_20b_sel[4:0] 单元格（1027v1 变更；
   = rect + label text + value text 三连行）包进 <g class="chg">。
3. 内嵌 <style>（@keyframes rowIn / chgPulse）；fill forwards，动画终态与源图一致。
4. 自检：a) xml.etree 解析 OK；b) 源/输出 <text> 文本多重集一致；c) 输出 > 1KB。
"""
import os
from collections import Counter
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, os.pardir, "chip_sel0_register_map.svg"))
OUT = os.path.join(HERE, "chip_sel0_register_map.svg")

STYLE = """<style>
.row { opacity:0; animation: rowIn 0.4s ease forwards; }
.head { opacity:0; animation: rowIn 0.4s ease forwards; }
.chg { animation: chgPulse 2s ease-in-out 4s infinite; }
@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }
@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }
</style>"""

DELAY_STEP = 0.03  # 秒 / 行


def is_row_label(line: str) -> bool:
    return line.startswith("<text") and 'x="158"' in line and 'font-weight="600"' in line


def wrap_chg(lines, target: str):
    """把含 target 的单元格（上一行 rect + 本行 label text + 下一行 value text）包进 <g class="chg">。"""
    for i, ln in enumerate(lines):
        if (">" + target + "</text>") in ln:
            if lines[i - 1].lstrip().startswith("<rect") and lines[i + 1].lstrip().startswith("<text"):
                return (lines[: i - 1] + ['<g class="chg">', lines[i - 1], lines[i],
                                           lines[i + 1], "</g>"] + lines[i + 2:])
    raise ValueError("chg target not found: " + target)


def convert() -> None:
    with open(SRC, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()

    assert lines[0].startswith("<?xml"), "missing XML declaration"
    assert lines[1].lstrip().startswith("<svg"), "missing <svg> open on line 2"
    assert lines[-1].strip() == "</svg>", "missing </svg> on last line"
    body = lines[2:-1]

    label_pos = [i for i, ln in enumerate(body) if is_row_label(ln)]
    assert len(label_pos) >= 2, "no row labels found"
    legend_pos = next(i for i, ln in enumerate(body) if ">图例</text>" in ln)
    assert legend_pos > label_pos[-1], "legend must come after last row"
    assert body[0].lstrip().startswith("<rect"), "expected background rect as first body element"
    assert label_pos[0] > 0, "header zone must be non-empty"

    out = [lines[0], lines[1]]
    out.extend(STYLE.splitlines())
    out.append(body[0])  # 背景白底 rect，保持原位不包组

    out.append('<g class="head">')  # 标题 + 位号列 + POR 默认值表头
    out.extend(body[1:label_pos[0]])
    out.append("</g>")

    for k, start in enumerate(label_pos):
        end = label_pos[k + 1] if k + 1 < len(label_pos) else legend_pos
        seg = list(body[start:end])
        label = seg[0]
        if "0x1D (29)" in label:
            seg = wrap_chg(seg, "khead_20b_sel[4:0]")
        out.append('<g class="row" style="animation-delay: %.2fs">' % (k * DELAY_STEP))
        out.extend(seg)
        out.append("</g>")

    out.append('<g class="head">')  # 图例 + 脚注
    out.extend(body[legend_pos:])
    out.append("</g>")
    out.append("</svg>")

    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")


NS = "{http://www.w3.org/2000/svg}"


def text_multiset(path: str) -> Counter:
    return Counter(el.text or "" for el in ET.parse(path).getroot().iter(NS + "text"))


def selfcheck() -> bool:
    ok = True
    # a. well-formed
    try:
        ET.parse(OUT)
        print("[a] xml.etree parse: OK")
    except ET.ParseError as e:
        ok = False
        print("[a] xml.etree parse: NG ->", e)
    # b. text multiset equivalence
    src, outm = text_multiset(SRC), text_multiset(OUT)
    if src == outm:
        print("[b] text multiset: OK (%d <text> elements)" % sum(outm.values()))
    else:
        ok = False
        print("[b] text multiset: NG -> only_in_src=%r only_in_out=%r"
              % (src - outm, outm - src))
    # c. file exists and > 1KB
    size = os.path.getsize(OUT) if os.path.exists(OUT) else 0
    if size > 1024:
        print("[c] output file: OK (%d bytes)" % size)
    else:
        ok = False
        print("[c] output file: NG (size=%d)" % size)
    # d. 附加：svg 头一致、无 script
    with open(SRC, encoding="utf-8") as f:
        src_svg = f.readline().strip()
    with open(OUT, encoding="utf-8") as f:
        out_svg = f.readline().strip()
    with open(OUT, encoding="utf-8") as f:
        no_script = "<script" not in f.read()
    if src_svg == out_svg and no_script:
        print("[d] svg attrs identical + no <script>: OK")
    else:
        ok = False
        print("[d] svg attrs identical + no <script>: NG (src_svg=%r out_svg=%r no_script=%s)"
              % (src_svg, out_svg, no_script))
    return ok


if __name__ == "__main__":
    convert()
    ok = selfcheck()
    raise SystemExit(0 if ok else 1)

# ymzhu 2026-10-27 10:42
