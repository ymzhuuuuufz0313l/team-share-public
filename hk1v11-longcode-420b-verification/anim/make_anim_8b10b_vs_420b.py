#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_8b10b_vs_420b.py
把 8b10b_vs_420b_architecture.svg 转成纯 CSS 动画 SVG（确定性结构变换，无手工编辑）。

源结构（line1 即 <svg>，无 XML 声明）：
- line2: 字体 <style>（保留）
- <defs> markers、白色背景 rect
- 标题 + 副标题（2 个 <text>）
- 左列「8B/10B 模式」(rect x=40 y=88 w=640)：6 个堆叠 box
- 右列「420B 长编码模式」(rect x=720 y=88 w=640)：堆叠 box
- 每列 5 条蓝色箭头（左 x=360 / 右 x=1040，位于 box 间隙：174-190, 316-332,
  392-408, 464-480, 558-574）
- 底部对照表「关键差异对照」(rect x=40 y=690 w=1320 h=484)：
  表头行 (y=726) + 13 数据行 (y=762..1146，每行 = 3 rect + 3 text)

变换（只加 <g> 包裹、<style> 块、2 条装饰 <path>、class 属性，零数据改动）：
- 动画 <style> 插在 <svg> 开标签正后（字体 style 之前），字体 style 保留。
- 标题+副标题 → <g class="head">（delay 0）
- 左列（box + 本列 5 箭头 + flow path）→ <g class="row" delay 0.08s>
- 右列（同构）→ <g class="row" delay 0.16s>
- 表头行（含表容器 rect + 「关键差异对照」标题）→ <g class="row" delay 0.24s>
- 13 数据行 → 各一个 <g class="row">，0.03s 步进（0.27s … 0.63s）
- 流动光点：每列 1 条沿本列 5 段箭头走位的多子路径（总长 80），
  stroke-dasharray "8 72"（周期 = 总长 ⇒ 路径上恒有 1 个 8 单位光点，无长停顿），
  @keyframes stroke-dashoffset 80→0，周期 80/150≈0.5333s，linear infinite，
  左右两列错开半周期（0.2667s）。
  说明：若用整条直线 M 360 174 V 558 会穿过中间 box 内部及其居中文字，
  故按任务允许采用「实际箭头线段」方案。
- 每列底部「线上数据验证」box（左 rect x=70 y=574 / 右 rect x=750 y=574，
  各 rect+2 text）→ <g class="breathe">（嵌在列 .row 内：外层 reveal、内层 effect）。
- 自检：XML well-formed、<text> 多重集与源一致、无 <script>、≥1 @keyframes、
  <svg> 开标签与源一致、size>1024B，并打印 .row/.head/.flowdot/.breathe 计数。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "8b10b_vs_420b_architecture.svg"
OUT = BASE / "anim" / "8b10b_vs_420b_architecture.svg"

# 每列 5 段箭头（y: 174→190, 316→332, 392→408, 464→480, 558→574），总长 5*16 = 80
LEFT_D = "M 360 174 V 190 M 360 316 V 332 M 360 392 V 408 M 360 464 V 480 M 360 558 V 574"
RIGHT_D = "M 1040 174 V 190 M 1040 316 V 332 M 1040 392 V 408 M 1040 464 V 480 M 1040 558 V 574"
FLOW_LEN = 80.0
FLOW_SPEED = 150.0  # 单位/秒（按 (L+88)/150 公式的隐含速度）
FLOW_PERIOD = FLOW_LEN / FLOW_SPEED  # 0.5333s
FLOW_HALF = FLOW_PERIOD / 2.0

STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".breathe { animation: br 3.2s ease-in-out infinite; }\n"
    "@keyframes br { 0%,100% { opacity:1; } 50% { opacity:0.55; } }\n"
    ".flowdot { fill:none; stroke:#2563eb; stroke-width:1.5; stroke-dasharray:8 72; }\n"
    f".flowdot-l {{ animation: flowL {FLOW_PERIOD:.4f}s linear infinite; }}\n"
    f".flowdot-r {{ animation: flowR {FLOW_PERIOD:.4f}s linear infinite {FLOW_HALF:.4f}s; }}\n"
    f"@keyframes flowL {{ from {{ stroke-dashoffset:{FLOW_LEN:.0f}; }} to {{ stroke-dashoffset:0; }} }}\n"
    f"@keyframes flowR {{ from {{ stroke-dashoffset:{FLOW_LEN:.0f}; }} to {{ stroke-dashoffset:0; }} }}\n"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head{opacity:1!important}}\n"
    "</style>"
)


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # 结构断言（确定性前提）
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert "font-family" in lines[1], "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    n = len(lines)
    svg_end = n - 1

    def find(pred, what, start=2, end=svg_end):
        hits = [i for i in range(start, end) if pred(lines[i].strip())]
        assert hits, f"未找到: {what}"
        return hits

    # 标题 / 副标题
    title_i = find(lambda s: s.startswith("<text") and ">8B/10B vs 420B 长编码" in s, "标题")[0]
    sub_i = find(lambda s: s.startswith("<text") and "0717v1 修正" in s, "副标题")[0]
    assert sub_i == title_i + 1, "副标题应紧跟标题"

    # 左 / 右列容器 rect
    left_box_i = find(lambda s: s.startswith('<rect x="40" y="88" width="640"'), "左列容器")[0]
    right_box_i = find(lambda s: s.startswith('<rect x="720" y="88" width="640"'), "右列容器")[0]
    assert left_box_i < right_box_i

    # 每列 5 条箭头（x1=360 / x1=1040），且连续
    left_arrows = find(lambda s: s.startswith('<line x1="360"'), "左列箭头")
    right_arrows = find(lambda s: s.startswith('<line x1="1040"'), "右列箭头")
    for hits, name in ((left_arrows, "左列"), (right_arrows, "右列")):
        assert len(hits) == 5, f"{name}箭头应为 5 条，实得 {len(hits)}"
        assert hits == list(range(hits[0], hits[0] + 5)), f"{name}箭头应为连续行"
    assert left_box_i < min(left_arrows) and right_box_i < min(right_arrows)

    left_col_end = right_box_i                                # 左列 = [left_box_i, right_box_i)
    right_col_end = min(left_arrows[0], right_arrows[0])      # 右列 = [right_box_i, 首条箭头)
    assert right_box_i < right_col_end < svg_end

    # 每列底部「线上数据验证」box（breathe 块 = rect + 2 text）
    left_br_i = find(lambda s: s.startswith('<rect x="70" y="574"'), "左列底部验证 box")[0]
    right_br_i = find(lambda s: s.startswith('<rect x="750" y="574"'), "右列底部验证 box")[0]
    assert left_box_i <= left_br_i < left_col_end, "左 breathe 块应在左列内"
    assert right_box_i <= right_br_i < right_col_end, "右 breathe 块应在右列内"
    for bi, end in ((left_br_i, left_col_end), (right_br_i, right_col_end)):
        assert lines[bi + 1].strip().startswith("<text") and lines[bi + 2].strip().startswith("<text"), \
            "breathe 块应为 rect + 2 text"
        assert bi + 3 <= end, "breathe 块应完整落在列内"

    # 表：容器 rect + 「关键差异对照」标题 + 表头行 (3 rect y=726 + 3 text)
    table_box_i = find(lambda s: s.startswith('<rect x="40" y="690" width="1320"'), "表容器")[0]
    table_title_i = find(lambda s: s.startswith("<text") and ">关键差异对照<" in s, "表标题")[0]
    assert table_title_i == table_box_i + 1, "表标题应紧跟表容器"
    header_rects = find(
        lambda s: s.startswith('<rect x="60" y="726"') or s.startswith('<rect x="270" y="726"')
        or s.startswith('<rect x="740" y="726"'), "表头行 3 rect")
    assert len(header_rects) == 3 and header_rects == list(range(header_rects[0], header_rects[0] + 3))
    header_start = header_rects[0]
    assert all(lines[header_start + k].strip().startswith("<text") for k in (3, 4, 5)), "表头行应为 3 rect + 3 text"
    header_end = header_start + 6

    # 13 数据行：每行首 rect x=60 height=32，行 = 3 rect + 3 text
    row_re = re.compile(r'^<rect x="60" y="\d+" width="210" height="32"')
    data_starts = []
    i = header_end
    while i < svg_end:
        if not row_re.match(lines[i].strip()):
            break
        data_starts.append(i)
        i += 6
    assert len(data_starts) == 13, f"应为 13 个数据行，实得 {len(data_starts)}"
    for s0 in data_starts:
        assert lines[s0 + 1].strip().startswith("<rect") and lines[s0 + 2].strip().startswith("<rect") \
            and all(lines[s0 + k].strip().startswith("<text") for k in (3, 4, 5)), "数据行应为 3 rect + 3 text"
    assert data_starts[-1] + 6 == svg_end, "末行数据行应到 </svg> 前"

    # ---- 组装输出 ----
    out = []
    out.append(lines[0])      # <svg ...>（width/height/viewBox 原样保留）
    out.append(STYLE)         # 动画 <style>（插在字体 style 前）
    out.append(lines[1])      # 字体 <style>（保留）
    out.extend(lines[2:title_i])  # <defs> + 白色背景 rect

    # head：标题 + 副标题
    out.append('<g class="head">')
    out.append(lines[title_i])
    out.append(lines[sub_i])
    out.append("</g>")

    def emit_column(start, end, arrows, flow_d, flow_cls, br_i):
        g = []
        i = start
        while i < end:
            if i == br_i:
                g.append('<g class="breathe">')
                g.append(lines[i]); g.append(lines[i + 1]); g.append(lines[i + 2])
                g.append("</g>")
                i += 3
                continue
            g.append(lines[i])
            i += 1
        g.extend(arrows)
        g.append(f'<path class="flowdot {flow_cls}" d="{flow_d}"/>')
        return g

    # 左列（box + 箭头 + 流动光点）
    out.append('<g class="row" style="animation-delay:0.08s">')
    out.extend(emit_column(left_box_i, left_col_end, [lines[k] for k in left_arrows],
                           LEFT_D, "flowdot-l", left_br_i))
    out.append("</g>")
    # 右列
    out.append('<g class="row" style="animation-delay:0.16s">')
    out.extend(emit_column(right_box_i, right_col_end, [lines[k] for k in right_arrows],
                           RIGHT_D, "flowdot-r", right_br_i))
    out.append("</g>")

    # 表头行（含表容器 + 表标题）
    out.append('<g class="row" style="animation-delay:0.24s">')
    out.extend(lines[table_box_i:header_end])
    out.append("</g>")
    # 13 数据行，0.03s 步进
    for r, s0 in enumerate(data_starts):
        delay = (24 + 3 * (r + 1)) / 100.0  # 0.27 … 0.63
        out.append(f'<g class="row" style="animation-delay:{delay:.2f}s">')
        out.extend(lines[s0:s0 + 6])
        out.append("</g>")

    out.append(lines[svg_end])  # </svg>
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return {
        "head": 1,
        "row": 2 + 1 + len(data_starts),
        "flowdot": 2,
        "breathe": 2,
        "data_rows": len(data_starts),
    }


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
        res["text_multiset"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text_multiset"] = f"NG: {e}"

    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    data = OUT.read_text(encoding="utf-8")
    res["no_script"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = "OK" if "@keyframes" in data else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    return res, data


def main():
    counts = build()
    res, data = check()
    n_row = data.count('class="row"')
    n_head = data.count('class="head"')
    n_flow = data.count('class="flowdot ')
    n_breathe = data.count('class="breathe"')
    print(f"[make_anim_8b10b_vs_420b] built: head={counts['head']} row={counts['row']} "
          f"flowdot={counts['flowdot']} breathe={counts['breathe']} data_rows={counts['data_rows']}")
    print(f"  groups in output: .row={n_row} .head={n_head} .flowdot={n_flow} .breathe={n_breathe}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 19:22
