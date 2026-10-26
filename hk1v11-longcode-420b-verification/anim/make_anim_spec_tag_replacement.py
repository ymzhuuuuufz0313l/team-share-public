#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_tag_replacement.py
把 spec_tag_replacement.svg 转成纯 CSS 动画 SVG（确定性分组变换，无手工编辑）。

特效：
- 标题（head 0s）/ 输入行（.row 0.10s）/ 输出行（.row 0.20s）/ 图例（head 0.30s）
- 4 个 step 盒 ①~④ 各 .row，0.05s 级联左→右（0.35s/0.40s/0.45s/0.50s）
- 输出行 3 个黄色 tag 单元格（101010，#fef08a）各包 <g class="breathe">，tag 高亮呼吸
- "发送顺序 A → B" 蓝箭头（直线 (655,196)→(830,196)，L=175）复制为 flowdot，#2563eb
- 纯 CSS <style>，无 script，无外部资源；
  零改动数据文本/几何/颜色/width/height/viewBox

自检：1 XML well-formed  2 <text> 多重集==源  3 无 <script>
     4 ≥1 @keyframes  5 <svg> 开头标签一致  6 size>1024  7 打印分组计数
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_tag_replacement.svg"
OUT = BASE / "anim" / "spec_tag_replacement.svg"

# "发送顺序 A → B" 蓝箭头：直线 (655,196)→(830,196)，L = 175（精确）
L_A2B = 175.0


def _f(x):
    """CSS 数值：整数去小数点，否则 3 位小数。"""
    xf = float(x)
    return str(int(xf)) if xf.is_integer() else f"{xf:.3f}".rstrip("0").rstrip(".")


def style_block():
    P = L_A2B + 88   # keyframes 位移区间 / dash 周期
    G = L_A2B + 80   # dash gap
    return (
        "<style>\n"
        ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
        "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
        ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
        ".breathe { animation: br 3.2s ease-in-out infinite; }\n"
        "@keyframes br { 0%,100% { opacity:1; } 50% { opacity:0.55; } }\n"
        f".flowdot {{ stroke-dasharray: 8 {_f(G)}; animation: pkt1 {_f(P / 150.0)}s linear infinite; }}\n"
        f"@keyframes pkt1 {{ from {{ stroke-dashoffset: {_f(P)}; }} to {{ stroke-dashoffset: 0; }} }}\n"
        "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .row, .head { opacity: 1 !important; } }\n"
        "</style>"
    )


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    # ---- 按内容定位结构单元 ----
    title_i = next(i for i in range(2, end) if "分组标签替换" in lines[i])
    subtitle_i = title_i + 1
    assert "59 组" in lines[subtitle_i], "标题下一行应为副标题"

    input_label_i = next(i for i in range(subtitle_i + 1, end) if ">输入 413b<" in lines[i])
    input_start = input_label_i - 1
    assert lines[input_start].strip().startswith("<rect"), "输入行起点前一行应为 label rect"

    arrow_down_i = next(i for i in range(input_label_i + 1, end) if 'x1="442" y1="172"' in lines[i])
    input_end = arrow_down_i - 1
    assert input_end >= input_start, "输入行应为非空段"

    output_label_i = next(i for i in range(arrow_down_i + 1, end) if ">输出 420b<" in lines[i])
    legend_start = next(i for i in range(output_label_i + 1, end)
                        if lines[i].strip().startswith('<rect x="890"'))
    output_end = legend_start - 1
    assert output_end >= output_label_i, "输出行应为非空段"

    step_rects = [i for i in range(legend_start, end)
                  if lines[i].strip().startswith("<rect") and 'y="300"' in lines[i]]
    assert len(step_rects) == 4, f"应有 4 个 step 盒, 实得 {len(step_rects)}"

    # 输出行内黄色 tag 单元格（rect y=208 fill #fef08a + 次行 101010 text）
    yellow_cells = [(i, i + 1) for i in range(arrow_down_i, output_end + 1)
                    if lines[i].strip().startswith("<rect")
                    and 'y="208"' in lines[i] and 'fill="#fef08a"' in lines[i]]
    assert len(yellow_cells) == 3, f"应有 3 个黄色 tag 单元格, 实得 {len(yellow_cells)}"
    for a, b in yellow_cells:
        assert ">101010<" in lines[b], "黄色 cell 次行应为 101010 text"

    a2b_i = next(i for i in range(arrow_down_i, output_end + 1) if 'x1="655" y1="196"' in lines[i])
    assert lines[a2b_i].strip().startswith("<line"), "A→B 箭头应为 <line>"

    # ---- 组装 ----
    out = []
    out.append(lines[0])            # <svg ...>（width/height/viewBox 原样）
    out.append(style_block())       # 动画 <style>（紧随 line 1）
    out.append(lines[1])            # 字体 <style>（KEEP）
    out.extend(lines[2:title_i])    # defs + 白色背景 rect

    out.append('<g class="head">')                                # 标题 + 副标题
    out.extend(lines[title_i:subtitle_i + 1])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.10s">')   # 输入行
    out.extend(lines[input_start:input_end + 1])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.20s">')   # 输出行（含下行箭头/A→B 箭头）
    i = arrow_down_i
    while i <= output_end:
        if (i, i + 1) in yellow_cells:
            out.append('<g class="breathe">')
            out.append(lines[i])
            out.append(lines[i + 1])
            out.append("</g>")
            i += 2
            continue
        out.append(lines[i])
        if i == a2b_i:
            out.append('<path class="flowdot" d="M 655 196 L 830 196" fill="none" '
                       'stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>')
        i += 1
    out.append("</g>")

    out.append('<g class="head" style="animation-delay:0.30s">')  # 图例
    out.extend(lines[legend_start:step_rects[0]])
    out.append("</g>")

    for r, s in enumerate(step_rects):                             # 4 steps，0.05s 级联
        e2 = step_rects[r + 1] if r + 1 < len(step_rects) else end
        delay = f"{0.35 + r * 0.05:.2f}s"
        out.append(f'<g class="row" style="animation-delay:{delay}">')
        out.extend(lines[s:e2])
        out.append("</g>")

    out.append(lines[end])
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return len(step_rects)


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"
        return res

    def texts(p):
        root = ET.parse(str(p)).getroot()
        return Counter(el.text or "" for el in root.iter(f"{NS}text"))

    try:
        res["text_multiset"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text_multiset"] = f"NG: {e}"

    data = OUT.read_text(encoding="utf-8")
    res["no_script"] = "OK" if "<script" not in data else "NG"
    nk = data.count("@keyframes")
    res["keyframes"] = f"OK ({nk})" if nk >= 1 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    res["groups"] = (
        f"row={data.count('class=\"row\"')} head={data.count('class=\"head\"')} "
        f"breathe={data.count('class=\"breathe\"')} flowdot={data.count('class=\"flowdot\"')}"
    )
    return res


def main():
    n = build()
    res = check()
    print(f"[make_anim_spec_tag_replacement] steps={n} L_A2B={L_A2B:g}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for k, v in res.items() if k != "groups")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 18:41
