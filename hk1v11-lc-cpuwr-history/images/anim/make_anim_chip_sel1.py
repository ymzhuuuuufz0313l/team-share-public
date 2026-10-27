#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_anim_chip_sel1.py — 确定性转换：静态 SVG -> 动画 SVG（纯 CSS、自包含、无 <script>）

源（只读）:  <repo>/images/chip_sel1_register_map.svg
输出（同名）: <repo>/images/anim/chip_sel1_register_map.svg

转换规则：
  1. 按行分组：以每个行标签（x="158" 的 0xNN (n) <text>）为界，把该行起（含行尾 pill）
     到下一行标签前的全部元素包进 <g class="row" style="animation-delay: Xs">，
     X = 行序号(0 基) * 0.03s。标题 / 位号列 [7]..[0] / POR 默认值 与 图例 包进
     <g class="head">（无 delay）。白色背景 rect 保持顶层静态（根 svg 本身已有白底）。
  2. 在 <svg> 内加 <style>：.row/.head 用 rowIn 淡入上移；.chg 用 chgPulse 脉冲。
     变更单元格：0x1D 行 label 为 khead_20b_sel[4:0] 的单元格（1027v1 变更；
     rect + 两个 text）包进 <g class="chg">。
  3. 逐行包裹：所有源行字节内容原样保留，只插入 <g> 包裹行与 <style> 块，
     不改动任何数据文本 / 几何 / 颜色；width/height/viewBox 与源一致。
  4. 自检：a) 输出 XML well-formed；b) 源/输出全部 <text> 文本多重集完全一致；
     c) 输出存在且 > 1KB；另校验根属性一致、无 <script>。
"""

import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "chip_sel1_register_map.svg"
OUT = HERE / "chip_sel1_register_map.svg"

SVG_NS = "http://www.w3.org/2000/svg"

ROW_LABEL_RE = re.compile(r'^<text\b[^>]*\bx="158"[^>]*>\s*0x')
LEGEND_RE = re.compile(r'>图例</text>')
ELEM_RE = re.compile(r'^<(rect|text|circle)\b')
CHG_MARKER_RE = re.compile(r'>\s*khead_20b_sel\[4:0\]\s*<')

CSS = (
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".chg { animation: chgPulse 2s ease-in-out 4s infinite; }\n"
    "@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }\n"
)


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def render_row(row: list[str]) -> list[str]:
    """把一行内的变更单元格（rect + label text + value text 三连）包进 <g class="chg">。"""
    chg_rects = set()
    for j, line in enumerate(row):
        if (
            line.startswith("<text ")
            and CHG_MARKER_RE.search(line)
            and j >= 1
            and j + 1 < len(row)
            and row[j - 1].startswith("<rect ")
            and row[j + 1].startswith("<text ")
        ):
            chg_rects.add(j - 1)
    out = []
    i = 0
    while i < len(row):
        if i in chg_rects:
            out.append('<g class="chg">')
            out.extend(row[i : i + 3])
            out.append("</g>")
            i += 3
        else:
            out.append(row[i])
            i += 1
    return out


def main() -> None:
    raw = SRC.read_text(encoding="utf-8")
    lines = raw.split("\n")

    # ---- 结构断言（源文件为"每元素一行"的扁平 SVG）----
    if not lines[0].startswith("<?xml"):
        fail("line1 不是 XML 声明")
    if not lines[1].lstrip().startswith("<svg"):
        fail("line2 不是 <svg>")
    close_idx = None
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "</svg>":
            close_idx = i
            break
    if close_idx is None:
        fail("找不到 </svg>")
    body = lines[2:close_idx]
    if body[0].strip() != '<rect width="1100" height="2946" fill="#ffffff"/>':
        fail("line3 不是白色背景 rect")
    for i, l in enumerate(body):
        if not ELEM_RE.match(l):
            fail(f"body 第 {i} 行不是 rect/text/circle: {l[:60]}")

    row_starts = [i for i, l in enumerate(body) if ROW_LABEL_RE.match(l)]
    legend_idx = next((i for i, l in enumerate(body) if LEGEND_RE.search(l)), None)
    if not row_starts:
        fail("未找到行标签")
    if legend_idx is None or legend_idx <= row_starts[-1]:
        fail("未找到图例或其位置异常")
    if any(not l.startswith("<text ") for s in row_starts for l in [body[s]]):
        fail("存在非 text 行标签")
    if len(set(row_starts)) != len(row_starts):
        fail("行标签重复")

    # 变更单元格定位（全文件恰好一处）
    n_khead = sum(1 for l in body if "khead_20b_sel[4:0]" in l)
    if n_khead != 1:
        fail(f"khead_20b_sel[4:0] 出现次数异常: {n_khead}")

    # ---- 组装输出 ----
    out: list[str] = []
    out.append(lines[0])  # XML 声明
    out.append(lines[1])  # <svg ...>（width/height/viewBox/style 与源一致）
    out.append("<style>")
    out.append(CSS.rstrip("\n"))
    out.append("</style>")
    out.append(body[0])  # 白色背景 rect（静态，不进动画组）

    head1 = body[1 : row_starts[0]]  # 标题 + 位号列 + POR 默认值
    out.append('<g class="head">')
    out.extend(head1)
    out.append("</g>")

    n_chg = 0
    for k, s in enumerate(row_starts):
        e = row_starts[k + 1] if k + 1 < len(row_starts) else legend_idx
        delay = f"{k * 0.03:.2f}s"
        out.append(f'<g class="row" style="animation-delay: {delay}">')
        row = body[s:e]
        before = len(row)
        rendered = render_row(row)
        # chg 包裹会插入 2 行 <g class="chg"> + </g>，每个单元格 +2
        n_chg += (len(rendered) - before) // 2
        out.extend(rendered)
        out.append("</g>")

    head2 = body[legend_idx:]  # 图例 + 尾注
    out.append('<g class="head">')
    out.extend(head2)
    out.append("</g>")
    out.append("</svg>")
    out.append("")  # 末尾换行

    if n_chg != 1:
        fail(f"chg 单元格包裹数异常: {n_chg}（期望 1，1027v1 khead_20b_sel）")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out), encoding="utf-8")

    # ---- 自检 ----
    # a) 输出 XML well-formed
    try:
        out_tree = ET.parse(OUT)
        xml_ok = True
    except ET.ParseError as exc:
        fail(f"输出 XML 解析失败: {exc}")
        xml_ok = False
    src_root = ET.parse(SRC).getroot()
    out_root = out_tree.getroot()
    attr_ok = src_root.attrib == out_root.attrib

    # b) 全部 <text> 文本多重集比较
    def text_multiset(path: Path) -> Counter:
        t = ET.parse(path)
        return Counter((el.text or "") for el in t.getroot().iter(f"{{{SVG_NS}}}text"))

    src_texts = text_multiset(SRC)
    out_texts = text_multiset(OUT)
    text_ok = src_texts == out_texts

    # c) 输出存在且 > 1KB；附加：无 <script>
    size = OUT.stat().st_size if OUT.exists() else 0
    size_ok = size > 1024
    no_script = b"<script" not in OUT.read_bytes()

    print(f"rows = {len(row_starts)} (delay 0s .. {((len(row_starts) - 1) * 0.03):.2f}s)")
    print(f"chg cells wrapped = {n_chg}")
    print(f"output = {OUT}")
    print(f"[a] XML well-formed : {'OK' if xml_ok else 'NG'}")
    print(f"    root attrs equal: {'OK' if attr_ok else 'NG'}")
    print(f"[b] text multiset   : {'OK' if text_ok else 'NG'} "
          f"(src {sum(src_texts.values())} / out {sum(out_texts.values())} 个 <text>)")
    print(f"[c] exists & >1KB   : {'OK' if size_ok else 'NG'} ({size} bytes)")
    print(f"    no <script>     : {'OK' if no_script else 'NG'}")
    if not (xml_ok and attr_ok and text_ok and size_ok and no_script):
        fail("自检未全部通过")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    main()

# ymzhu 2026-10-27 10:42
