#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_bit_order.py
把 spec_bit_order.svg 转成纯 CSS 动画 SVG（确定性分组变换，无手工编辑）。

效果（保持简单）：
- 一次性 reveal（forwards，外层组只做 reveal）：
  * 标题 + 副标题          → <g class="head">（delay 0）
  * 三列 bit 网格（整列）  → <g class="row">（R0 0.08s / G0 0.16s / B0 0.24s，字节自左向右构建）
  * Case1 串行流 strip     → <g class="row">（0.32s）
  * 底部传输时间轴          → <g class="head">（0.40s）
- 无限循环（内层组只做效果，不与外层 reveal 抢同一属性）：
  * 首发送 bit R0[0]（网格 R0 列末行 rect+text）→ <g class="breathe"> 呼吸
  * 左侧「发送顺序」竖箭上一枚 flow 包：复制 <path d="M 74 356 L 74 122">，
    stroke-dash 位移自下而上 = Bit0 先发顺序（仅此一个 flow 包）
- 不改动任何数据/文本/几何/颜色；width/height/viewBox 与源一致。
- prefers-reduced-motion:reduce 时停全部动画，且 .row/.head 强制可见。
- 输出后自检：XML well-formed、<text> 多重集与源一致、无 <script>、≥1 @keyframes、
  <svg> 开标签与源一致、文件 >1KB，并打印分组计数。确定性 + 幂等（重复运行输出相同）。
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_bit_order.svg"
OUT = BASE / "anim" / "spec_bit_order.svg"

STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:none} }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".breathe { animation: br 3.2s ease-in-out infinite; }\n"
    "@keyframes br { 0%,100%{opacity:1} 50%{opacity:0.55} }\n"
    ".flowdot { stroke-dasharray:8 322; animation: pkt 2.147s linear infinite; }\n"
    "@keyframes pkt { from{stroke-dashoffset:322} to{stroke-dashoffset:0} }\n"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important} .row,.head{opacity:1!important}}\n"
    "</style>"
)

# 竖箭（d 与源中 path 相同）的 flow 包复制件：dasharray 8 322（8 + (234+80)），
# dashoffset 322→0 线性循环（(234+88)/150 = 2.147s），点自下而上 = Bit0 先发。
FLOWDOT = ('<path d="M 74 356 L 74 122" fill="none" stroke="#2563eb" '
           'stroke-width="2.5" stroke-linecap="round" class="flowdot"/>')


def find_idx(lines, pred, tag, start=0):
    for i in range(start, len(lines)):
        if pred(lines[i]):
            return i
    raise AssertionError(f"未找到: {tag}")


def cell(lines, x, label, start=0):
    return find_idx(
        lines,
        lambda l, x=x, lab=label: (l.strip().startswith("<text")
                                   and f'x="{x}"' in l and f">{lab}<" in l),
        f"{label}@x={x}", start)


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    last = len(lines) - 1

    # 结构断言（确定性前提）
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>（无 XML 声明）"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[last].strip() == "</svg>", "末行应为 </svg>"

    # 定位（按内容，不按猜测行号）
    title_idx = find_idx(lines,
                         lambda l: l.strip().startswith("<text") and "数据传输方向" in l,
                         "标题")
    subtitle_idx = title_idx + 1
    assert "Packet Data 按 byte 依次发送" in lines[subtitle_idx], "副标题应在标题后一行"

    r0_7, r0_0 = cell(lines, "142.0", "R0[7]"), cell(lines, "142.0", "R0[0]")
    g0_7, g0_0 = cell(lines, "210.0", "G0[7]"), cell(lines, "210.0", "G0[0]")
    b0_7, b0_0 = cell(lines, "278.0", "B0[7]"), cell(lines, "278.0", "B0[0]")
    assert title_idx < r0_7 < r0_0 < g0_7 < g0_0 < b0_7 < b0_0, "三列顺序应为 R0→G0→B0"

    strip_start = find_idx(lines,
                           lambda l: l.strip().startswith('<rect x="60" y="482"'),
                           "Case1 strip 首 rect")
    strip_end = cell(lines, "1069.0", "G0[7]", start=strip_start)
    assert lines[strip_start - 1].strip().startswith("<text") \
        and "Case1 · 413b data" in lines[strip_start - 1], "Case1 标题应在 strip 前一行为 text"

    arrow_idx = find_idx(lines, lambda l: 'd="M 74 356 L 74 122"' in l, "发送顺序竖箭头")
    timeline_idx = find_idx(lines,
                            lambda l: l.strip().startswith('<line x1="60" y1="540" x2="1140" y2="540"'),
                            "底部传输时间轴")
    assert b0_0 < arrow_idx < strip_start < strip_end < timeline_idx < last, "块顺序异常"

    # 每列 = 首 cell 前一行 rect 起，至末 cell text 止（整列 16 行 = 8×(rect+text)）
    def col(a, b):
        assert lines[a - 1].strip().startswith("<rect"), "列首 text 前一行应为 rect"
        return a - 1, b

    r0_rect, r0_end = col(r0_7, r0_0)
    g0_rect, g0_end = col(g0_7, g0_0)
    b0_rect, b0_end = col(b0_7, b0_0)

    out = []
    out.append(lines[0])             # <svg ...>（width/height/viewBox 原样）
    out.append(STYLE)                # 动画 <style>，紧跟 line1
    out.append(lines[1])             # 原字体 <style>（保留）
    out.extend(lines[2:title_idx])   # defs + 白色背景 rect（不参与动画）

    # head #1：标题 + 副标题
    out.append('<g class="head">')
    out.extend(lines[title_idx:subtitle_idx + 1])
    out.append("</g>")

    # R0 列 reveal；末行 R0[0]（首发送 bit）单元格（rect+text）内层呼吸
    out.append('<g class="row" style="animation-delay:0.08s">')
    out.extend(lines[r0_rect:r0_end - 1])
    out.append('<g class="breathe">')
    out.extend(lines[r0_end - 1:r0_end + 1])
    out.append("</g>")
    out.append("</g>")

    # G0 / B0 列 reveal
    out.append('<g class="row" style="animation-delay:0.16s">')
    out.extend(lines[g0_rect:g0_end + 1])
    out.append("</g>")
    out.append('<g class="row" style="animation-delay:0.24s">')
    out.extend(lines[b0_rect:b0_end + 1])
    out.append("</g>")

    # 中间段：… / Bit7 / Bit0 / Packet Data / 竖箭头(+flow 包) / 发送顺序 /
    #        byte0>>byte1>>byte2 / 串行化箭头+文字 / Case1 标题（保持原样，不参与 reveal）
    for i in range(b0_end + 1, strip_start):
        out.append(lines[i])
        if i == arrow_idx:
            out.append(FLOWDOT)

    # Case1 串行流 strip reveal
    out.append('<g class="row" style="animation-delay:0.32s">')
    out.extend(lines[strip_start:strip_end + 1])
    out.append("</g>")

    # strip 之后至时间轴之前（… 标注）
    out.extend(lines[strip_end + 1:timeline_idx])

    # head #2：底部传输时间轴
    out.append('<g class="head" style="animation-delay:0.40s">')
    out.append(lines[timeline_idx])
    out.append("</g>")

    out.extend(lines[timeline_idx + 1:last])  # 时间轴标签等
    out.append(lines[last])                   # </svg>

    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    res = {}
    root = None
    try:
        root = ET.parse(str(OUT)).getroot()
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"

    if root is not None:
        def texts(p):
            r = ET.parse(str(p)).getroot()
            return Counter(el.text or "" for el in r.iter(f"{NS}text"))

        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"

        counts = {}
        for g in root.iter(f"{NS}g"):
            c = (g.get("class") or "").strip()
            if c:
                counts[c] = counts.get(c, 0) + 1
        for el in root.iter(f"{NS}path"):
            if (el.get("class") or "") == "flowdot":
                counts["flowdot"] = counts.get("flowdot", 0) + 1
        res["groups"] = (f"OK row={counts.get('row', 0)} head={counts.get('head', 0)} "
                         f"breathe={counts.get('breathe', 0)} flowdot={counts.get('flowdot', 0)}")
    else:
        res["text"] = "NG (xml parse failed)"
        res["groups"] = "NG (xml parse failed)"
        counts = {}

    data = OUT.read_text(encoding="utf-8")
    res["no_script"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = (f"OK ({data.count('@keyframes')})"
                        if data.count("@keyframes") >= 1 else "NG")

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"

    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    return res, counts


def main():
    build()
    res, counts = check()
    print("[make_anim_spec_bit_order] groups:",
          {k: counts.get(k, 0) for k in ("row", "head", "breathe", "flowdot")})
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = (all(str(v).startswith("OK") for v in res.values())
          and counts.get("row") == 4 and counts.get("head") == 2
          and counts.get("breathe") == 1 and counts.get("flowdot") == 1)
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 18:49
