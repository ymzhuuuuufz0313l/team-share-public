#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_scramble_rolling.py
把 spec_scramble_rolling.svg 转成纯 CSS 动画 SVG（确定性分组变换，无手工编辑）。

特效：
- 标题（head）/ 编码前行（.row 0.10s）/ 编码后行（.row 0.20s）/
  图例条组（.row 0.30s，含绿色"加扰区间"bar breathe 呼吸）/
  右侧小图例（head 0.30s）/ LFSR 回环+标签（.row 0.40s）/ n+1 行（.row 0.50s）
- 绿色虚线反馈回环（LFSR 连续，d="M 660 292 C 700 320 660 360 620 372 L 220 372 L 220 388"）
  复制为 flowdot（#059669），L 由 Python 采样三次贝塞尔+线段精确计算 —— 关键"滚动"动效
- 纯 CSS <style>，无 script，无外部资源；
  零改动数据文本/几何/颜色/width/height/viewBox

自检：1 XML well-formed  2 <text> 多重集==源  3 无 <script>
     4 ≥1 @keyframes  5 <svg> 开头标签一致  6 size>1024  7 打印分组计数
"""
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_scramble_rolling.svg"
OUT = BASE / "anim" / "spec_scramble_rolling.svg"


def path_length(d, n=200):
    """绝对 M/L/C 段路径总长；C 段按 n 点采样。"""
    segs = re.findall(r"([MCL])\s*([-\d.]+(?:\s+[-\d.]+)*)", d)
    pts = []
    cur = None
    for cmd, args in segs:
        nums = [float(x) for x in args.split()]
        if cmd == "M":
            cur = (nums[0], nums[1])
            pts.append(cur)
        elif cmd == "L":
            cur = (nums[0], nums[1])
            pts.append(cur)
        elif cmd == "C":
            p0, p1, p2, p3 = cur, (nums[0], nums[1]), (nums[2], nums[3]), (nums[4], nums[5])
            for k in range(1, n + 1):
                t = k / n
                u = 1 - t
                x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
                y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
                pts.append((x, y))
            cur = p3
    return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(pts, pts[1:]))


def _f(x):
    """CSS 数值：整数去小数点，否则 3 位小数。"""
    xf = float(x)
    return str(int(xf)) if xf.is_integer() else f"{xf:.3f}".rstrip("0").rstrip(".")


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    # ---- 按内容定位结构单元 ----
    title_i = next(i for i in range(2, end) if "滚动机制" in lines[i])
    subtitle_i = title_i + 1
    assert "scramble" in lines[subtitle_i].lower(), "标题下一行应为副标题"

    pre_i = next(i for i in range(subtitle_i + 1, end) if ">编码前<" in lines[i])
    arrow_i = next(i for i in range(pre_i + 1, end) if 'x1="470" y1="158"' in lines[i])
    assert lines[arrow_i].strip().startswith("<line"), "编码箭头应为 <line>"
    pre_start, pre_end = pre_i, arrow_i - 1
    assert pre_end >= pre_start, "编码前行应为非空段"

    bar_start = next(i for i in range(arrow_i + 1, end)
                     if lines[i].strip().startswith("<rect")
                     and 'y="282"' in lines[i] and 'width="540"' in lines[i])
    assert 'fill="#16a34a"' in lines[bar_start], "图例首条应为绿色加扰区间 bar"
    post_start, post_end = arrow_i, bar_start - 1
    assert post_end >= post_start, "编码后行应为非空段"

    swatch_start = next(i for i in range(bar_start + 1, end)
                        if lines[i].strip().startswith('<rect x="1010"'))
    bar_end = swatch_start - 1

    loop_i = next(i for i in range(swatch_start, end)
                  if lines[i].strip().startswith("<path") and "M 660 292" in lines[i])
    loop_label_i = loop_i + 1
    assert "LFSR" in lines[loop_label_i], "回环次行应为 LFSR 标签"

    next_i = next(i for i in range(loop_label_i + 1, end) if ">n+1 行<" in lines[i])
    next_start, next_end = next_i, end - 1
    assert next_end >= next_start, "n+1 行应为非空段"

    m = re.search(r'd="([^"]+)"', lines[loop_i])
    d_loop = m.group(1)
    L = path_length(d_loop)
    P = L + 88   # keyframes 位移区间 / dash 周期
    G = L + 80   # dash gap

    style = (
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

    # ---- 组装 ----
    out = []
    out.append(lines[0])            # <svg ...>（width/height/viewBox 原样）
    out.append(style)               # 动画 <style>（紧随 line 1）
    out.append(lines[1])            # 字体 <style>（KEEP）
    out.extend(lines[2:title_i])    # defs + 白色背景 rect

    out.append('<g class="head">')                                # 标题 + 副标题
    out.extend(lines[title_i:subtitle_i + 1])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.10s">')   # 编码前行
    out.extend(lines[pre_start:pre_end + 1])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.20s">')   # 编码后行（含下行箭头/标签）
    out.extend(lines[post_start:post_end + 1])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.30s">')   # 图例条组（3 bar + 左标签 + 灰注）
    i = bar_start
    while i <= bar_end:
        if i == bar_start:
            out.append('<g class="breathe">')   # 绿色"加扰区间"bar 呼吸
            out.append(lines[i])
            out.append("</g>")
        else:
            out.append(lines[i])
        i += 1
    out.append("</g>")

    out.append('<g class="head" style="animation-delay:0.30s">')  # 右侧小图例
    out.extend(lines[swatch_start:loop_i])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.40s">')   # LFSR 回环 + 标签 + flowdot
    out.append(lines[loop_i])
    out.append(f'<path class="flowdot" d="{d_loop}" fill="none" '
               'stroke="#059669" stroke-width="2.5" stroke-linecap="round"/>')
    out.append(lines[loop_label_i])
    out.append("</g>")

    out.append('<g class="row" style="animation-delay:0.50s">')   # n+1 行
    out.extend(lines[next_start:next_end + 1])
    out.append("</g>")

    out.append(lines[end])
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return L


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
    L = build()
    res = check()
    print(f"[make_anim_spec_scramble_rolling] L_loop={L:.2f}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for k, v in res.items() if k != "groups")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 18:41
