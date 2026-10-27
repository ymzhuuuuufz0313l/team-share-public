#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_checksum.py
把 checksum_address_map.svg 转成纯 CSS 动画 SVG（确定性行分组变换，无手工编辑）。

规则：
- 以行标签（font-weight=600 的 <text>0xNN (n)</text>）为界分组：
  每个地址行（行标签起，至下一行标签前，含 chip_sel=0/1 小标注）包进
  <g class="row" style="animation-delay: Xs">，X = 行序号 × 0.03s。
- 标题 + 位号列头 与 图例（含底部注释）分别包 <g class="head">。
- 0x1D 行中 khead_20b_sel[4:0] 单元格（1027v1 变更；rect + 2 个 text）包 <g class="chg">（脉冲高亮）。
- <svg> 内加 <style>（纯 CSS，无 script，无外部资源）。
- 不改动任何数据文本/几何/颜色；width/height/viewBox 与源一致。
- 输出后用 xml.etree 自检：well-formed、<text> 多重集与源一致、文件 >1KB、无 <script>。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images")
SRC = BASE / "checksum_address_map.svg"
OUT = BASE / "anim" / "checksum_address_map.svg"

STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".chg { animation: chgPulse 2s ease-in-out 4s infinite; }\n"
    "@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }\n"
    "</style>"
)

ROW_LABEL = re.compile(
    r'^<text x="170" y="[\d.]+" text-anchor="end" font-size="14" '
    r'font-weight="600" fill="#1e293b">0x[0-9A-Fa-f]+ \(\d+\)</text>$'
)


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # 结构断言（确定性前提）
    assert lines[0].startswith("<?xml"), "line1 应为 XML 声明"
    assert lines[1].lstrip().startswith("<svg"), "line2 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    svg_end_idx = len(lines) - 1

    # 行标签 / 图例 / chg 单元格定位
    row_starts = [i for i in range(2, svg_end_idx) if ROW_LABEL.match(lines[i].strip())]
    assert row_starts, "未找到行标签"
    legend_idx = next(
        i for i in range(2, svg_end_idx)
        if lines[i].strip().startswith("<text") and ">图例<" in lines[i]
    )
    assert legend_idx > row_starts[-1], "图例应在所有行之后"
    chg_label = next(
        i for i in range(2, svg_end_idx)
        if lines[i].strip().startswith("<text") and ">khead_20b_sel[4:0]<" in lines[i]
    )
    assert lines[chg_label - 1].strip().startswith("<rect"), "khead_20b_sel 前一行应为 rect"
    assert lines[chg_label + 1].strip().startswith("<text"), "khead_20b_sel 后一行应为 value text"
    chg_rect, chg_value = chg_label - 1, chg_label + 1

    out = []
    out.append(lines[0])  # XML 声明
    out.append(lines[1])  # <svg ...>（width/height/viewBox 原样保留）
    out.append(STYLE)
    out.append(lines[2])  # 白色背景 rect（保持不透明，不参与动画）

    # head #1：标题 + 位号列头（自 line3 起至第一个行标签前）
    out.append('<g class="head">')
    out.extend(lines[3:row_starts[0]])
    out.append("</g>")

    # 行：每个地址行一个 <g class="row">，0.03s 级联
    for r, start in enumerate(row_starts):
        end = row_starts[r + 1] if r + 1 < len(row_starts) else legend_idx
        delay = f"{r * 0.03:.2f}s"
        out.append(f'<g class="row" style="animation-delay:{delay}">')
        i = start
        while i < end:
            if i == chg_rect:
                # khead_20b_sel[4:0] 单元格（rect + label + value）脉冲高亮
                out.append('<g class="chg">')
                out.append(lines[i])
                out.append(lines[i + 1])
                out.append(lines[i + 2])
                out.append("</g>")
                i += 3
                continue
            out.append(lines[i])
            i += 1
        out.append("</g>")

    # head #2：图例 + 底部注释（至 </svg> 前）
    out.append('<g class="head">')
    out.extend(lines[legend_idx:svg_end_idx])
    out.append("</g>")

    out.append(lines[svg_end_idx])  # </svg>
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return len(row_starts)


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"

    def texts(p):
        root = ET.parse(str(p)).getroot()
        return Counter(el.text or "" for el in root.iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text"] = f"NG: {e}"

    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    data = OUT.read_text(encoding="utf-8")
    res["no_script"] = "OK" if "<script" not in data else "NG"
    # viewBox/width/height 与源一致
    import re as _re
    def svgtag(p):
        m = _re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    return res


def main():
    n = build()
    res = check()
    print(f"[make_anim_checksum] rows={n}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:42
