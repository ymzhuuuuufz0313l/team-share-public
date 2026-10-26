#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_anim_reset.py — 把静态 SVG 转成纯 CSS 动画 SVG（确定性行级变换，不手工编辑大文件）。

源（只读）:  ..\\reset_domain_address_map.svg
输出:        anim\\reset_domain_address_map.svg

规则（不改动任何数据文本 / 几何 / 颜色，仅包 <g> + 注入 <style>）:
  1. 以每个行标签（含波段标签 "0xNN ~ 0xNN (n ~ n)"，判定: x=158 + text-anchor=end
     + font-weight=600）为界，把该行起到下一行标签前的全部元素包进
     <g class="row" style="animation-delay: Xs">，X = 行序号(0 起) × 0.03s。
     标题/列头(顶部) 与 图例/尾部说明(底部) 包进 <g class="head">；
     背景 <rect> 保持顶层（始终可见，白底白底无视觉差异）。
  2. <svg> 后注入 <style>：
     .row/.head 入场（opacity 0→1 + translateY 6px，0.4s，forwards，最终态与源一致）；
     .chg 对 0x2F 行 SCS_PKT_HALF 单元格（rect + 两个 text）轻微脉冲
     （2s ease-in-out，4s 起，infinite，只动 opacity 不动配色）。
  3. 纯 CSS（SVG 内 <style> + @keyframes），无 <script>、无外部资源，<img> 可播放。
  4. width/height/viewBox 与源一致。

用法:  python make_anim_reset.py   （幂等：总是从源重新生成）
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

SRC = r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\reset_domain_address_map.svg"
DST = r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\anim\reset_domain_address_map.svg"

ROW_LABEL_X = "158"          # 行标签列 x 坐标
CHG_FIELD = "SCS_PKT_HALF"   # 变更单元格字段名
CHG_ROW_PREFIX = "0x2F"      # 变更所在行
CHG_ROW_NEXT = "0x30"        # 变更行的下一行标签
LEGEND_TEXT = "图例"
ROW_DELAY_S = 0.03

STYLE_BLOCK = [
    "<style>",
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }",
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }",
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }",
    ".chg { animation: chgPulse 2s ease-in-out 4s infinite; }",
    "@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }",
    "</style>",
]


def get_open_tag(line):
    """返回单行元素的 (标签名, 属性dict)；非元素行返回 (None, None)。"""
    m = re.match(r'^\s*<([A-Za-z][\w-]*)((?:\s+[\w-]+="[^"]*")*)\s*/?>', line)
    if not m:
        return None, None
    return m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))


def get_text_content(line):
    """返回单行 <text> 的文本内容；非 text 行返回 None。"""
    m = re.match(r'^\s*<text\b[^>]*>(.*?)</text>\s*$', line)
    return m.group(1) if m else None


def is_row_label(line):
    """行标签: <text x="158" ... text-anchor="end" ... font-weight="600">0xNN (n)</text>
    或波段标签 "0xNN ~ 0xNN (n ~ n)"（同样的属性形态）。"""
    tag, attrs = get_open_tag(line)
    return (tag == "text"
            and attrs.get("x") == ROW_LABEL_X
            and attrs.get("text-anchor") == "end"
            and attrs.get("font-weight") == "600")


def transform(src, dst):
    with open(src, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    EOL = "\r\n" if "\r\n" in raw else "\n"
    ends_with_eol = raw.endswith(EOL)
    lines = raw.split(EOL)
    if ends_with_eol:
        lines = lines[:-1]

    svg_open_idx = next(i for i, l in enumerate(lines) if l.lstrip().startswith("<svg"))
    svg_close_idx = next(i for i, l in enumerate(lines) if l.strip() == "</svg>")

    row_idxs = [i for i, l in enumerate(lines) if is_row_label(l)]
    if not row_idxs or row_idxs[0] <= svg_open_idx:
        raise ValueError("row labels not found / misordered")
    if not all(svg_open_idx < i < svg_close_idx for i in row_idxs):
        raise ValueError("row label outside <svg> body")

    legend_start = next(
        (i for i in range(row_idxs[-1] + 1, svg_close_idx)
         if get_text_content(lines[i]) == LEGEND_TEXT),
        None,
    )
    if legend_start is None:
        raise ValueError("legend (图例) not found after last row")

    # ---- 定位 0x2F 行的 SCS_PKT_HALF 单元格（rect + 两个 text，连续三行）----
    i2f = next(i for i in row_idxs if (get_text_content(lines[i]) or "").startswith(CHG_ROW_PREFIX))
    i30 = next(i for i in row_idxs if (get_text_content(lines[i]) or "").startswith(CHG_ROW_NEXT))
    if not i2f < i30:
        raise ValueError("0x2F / 0x30 rows not in order")
    t = next((i for i in range(i2f + 1, i30)
              if CHG_FIELD in (get_text_content(lines[i]) or "")), None)
    if t is None:
        raise ValueError(f"{CHG_FIELD} cell not found in {CHG_ROW_PREFIX} row")
    if get_open_tag(lines[t - 1])[0] != "rect":
        raise ValueError("cell <rect> not found before SCS_PKT_HALF text")
    if get_open_tag(lines[t + 1])[0] != "text":
        raise ValueError("cell default <text> not found after SCS_PKT_HALF text")
    chg = (t - 1, t, t + 1)

    # ---- 分区: 顶部 head / N 个 row / 底部 head；背景 rect 保持顶层 ----
    bg_idx = svg_open_idx + 1
    if get_open_tag(lines[bg_idx])[0] != "rect":
        raise ValueError("expected background <rect> right after <svg>")
    top_head = (bg_idx + 1, row_idxs[0] - 1)
    rows = []
    for k, ri in enumerate(row_idxs):
        end = row_idxs[k + 1] - 1 if k + 1 < len(row_idxs) else legend_start - 1
        rows.append((k, ri, end))
    bottom_head = (legend_start, svg_close_idx - 1)

    # 连续性校验：覆盖 [bg_idx+1, svg_close_idx-1]，无缺口无重叠
    prev = top_head[0] - 1
    for s, e in [top_head] + [(r[1], r[2]) for r in rows] + [bottom_head]:
        if s != prev + 1 or s > e:
            raise ValueError(f"section gap/overlap at [{s},{e}]")
        prev = e
    if prev != svg_close_idx - 1:
        raise ValueError("sections do not reach </svg>")
    if not (rows[0][1] <= chg[0] and chg[2] <= rows[0][2] or
            any(s <= chg[0] and chg[2] <= e for k, s, e in rows
                if s <= i2f <= e)):
        raise ValueError("chg cell outside the 0x2F row section")

    out = []
    out.extend(lines[:svg_open_idx + 1])   # <?xml?> + <svg ...>
    out.extend(STYLE_BLOCK)
    out.append(lines[bg_idx])              # 背景 rect（顶层）

    def emit_head(s, e):
        out.append('<g class="head">')
        out.extend(lines[s:e + 1])
        out.append("</g>")

    def emit_row(rownum, s, e):
        out.append(f'<g class="row" style="animation-delay: {rownum * ROW_DELAY_S:.2f}s">')
        i = s
        while i <= e:
            if i == chg[0]:
                out.append('<g class="chg">')
            out.append(lines[i])
            if i == chg[2]:
                out.append("</g>")
            i += 1
        out.append("</g>")

    emit_head(*top_head)
    for rownum, s, e in rows:
        emit_row(rownum, s, e)
    emit_head(*bottom_head)
    out.extend(lines[svg_close_idx:])      # </svg>

    result = EOL.join(out) + (EOL if ends_with_eol else "")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="") as f:
        f.write(result)
    return result, len(row_idxs)


def _all_text_contents(path):
    root = ET.parse(path).getroot()
    c = Counter()
    for el in root.iter():
        tag = el.tag
        if tag == "text" or (isinstance(tag, str) and tag.endswith("}text")):
            c[el.text if el.text is not None else ""] += 1
    return c


def self_check(src, dst):
    report = {}
    try:
        ET.parse(dst)
        report["xml"] = ("OK", "well-formed")
    except ET.ParseError as ex:
        report["xml"] = ("NG", str(ex))
    try:
        a, b = _all_text_contents(src), _all_text_contents(dst)
        if a == b:
            report["text"] = ("OK", f"multiset equal ({sum(a.values())} <text> elements)")
        else:
            report["text"] = ("NG", f"only_src={dict(a - b)} only_dst={dict(b - a)}")
    except ET.ParseError as ex:
        report["text"] = ("NG", f"parse error: {ex}")
    if os.path.exists(dst) and os.path.getsize(dst) > 1024:
        report["size"] = ("OK", f"{os.path.getsize(dst)} bytes (> 1 KB)")
    else:
        report["size"] = ("NG", "missing or <= 1 KB")
    return report


def main():
    result, n_rows = transform(SRC, DST)
    # 额外不变量自检（不进入报告口径，但失败即报错）
    assert "<script" not in result, "must not contain <script>"
    assert "http://" not in result.replace("http://www.w3.org/2000/svg", ""), "external resource?"
    assert result.count('<g class="chg">') == 1, "exactly one chg group expected"
    assert result.count("<svg") == 1
    report = self_check(SRC, DST)
    print(f"src : {SRC}")
    print(f"dst : {DST}")
    print(f"rows: {n_rows}  (delays 0.00s .. { (n_rows - 1) * ROW_DELAY_S:.2f}s)")
    for key in ("xml", "text", "size"):
        status, msg = report[key]
        print(f"{key:4}: {status}  {msg}")
    ok = all(s == "OK" for s, _ in report.values())
    print("RESULT:", "ALL OK" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
