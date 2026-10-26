#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_beat.py
把 config_data_beat_regroup_0721.svg 转成纯 CSS 动画 SVG（确定性行分组变换，无手工编辑）。

规则：
- 顶部标题/副标题/图例色块/两栏列头/中缝线 包进 <g class="head">。
- 区域标签（区域 A~D）与左右两栏的每个“拍行”（源文件中每一行即一个按 y 坐标聚类的
  元素组）各自包进 <g class="row" style="animation-delay: Xs">，X = 行序号 × 0.03s。
- 底部绿色汇总框（text 含 "XOR 总量不变" 的框的全部元素）包 <g class="chg">（脉冲高亮），
  其外层同样包 <g class="row">。
- 底部橙色汇总框（"过渡依赖"）包 <g class="row">。
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
SRC = BASE / "config_data_beat_regroup_0721.svg"
OUT = BASE / "anim" / "config_data_beat_regroup_0721.svg"

STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".chg { animation: chgPulse 2s ease-in-out 4s infinite; }\n"
    "@keyframes chgPulse { 0%,100% { opacity:1; } 50% { opacity:0.45; } }\n"
    "</style>"
)

REGION = re.compile(r'^<text x="60" y="\d+" font-size="13" font-weight="700" fill="#0f172a">区域 ')
BEAT = re.compile(r'^<rect x="\d+" y="\d+" width="\d+" height="50" rx="9"')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # 结构断言（确定性前提）
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    svg_end_idx = len(lines) - 1

    # 定位：第一个区域标签 / 绿色汇总框 / 橙色汇总框
    region_idxs = [i for i in range(1, svg_end_idx) if REGION.match(lines[i].strip())]
    assert len(region_idxs) == 4, f"应找到 4 个区域标签，实际 {len(region_idxs)}"
    head_end = region_idxs[0]  # head = lines[1:head_end)（背景 rect 除外）

    green_txt = next(i for i in range(1, svg_end_idx) if "XOR 总量不变" in lines[i])
    assert lines[green_txt - 1].strip().startswith("<rect"), "绿框前一行应为 rect"
    green_rect = green_txt - 1

    orange_txt = next(i for i in range(1, svg_end_idx) if ">过渡依赖<" in lines[i])
    assert lines[orange_txt - 1].strip().startswith("<rect"), "橙框前一行应为 rect"
    orange_rect = orange_txt - 1
    assert green_rect < orange_rect < svg_end_idx

    # 行区域：每个源行 = 区域标签 或 拍行
    row_region = list(range(head_end, green_rect))
    for i in row_region:
        assert REGION.match(lines[i].strip()) or BEAT.match(lines[i].strip()), \
            f"行区域出现未识别元素: {lines[i][:60]}"
    # 汇总框内部均为 rect/text 行
    for i in list(range(green_rect, orange_rect)) + list(range(orange_rect, svg_end_idx)):
        assert lines[i].strip().startswith("<rect") or lines[i].strip().startswith("<text"), \
            f"汇总框区域出现未识别元素: {lines[i][:60]}"

    out = []
    out.append(lines[0])  # <svg ...>（width/height/viewBox 原样保留）
    out.append(STYLE)
    out.append(lines[1])  # 白色背景 rect（保持不透明，不参与动画）

    # head：标题/副标题/图例色块/两栏列头/中缝线
    out.append('<g class="head">')
    out.extend(lines[2:head_end])
    out.append("</g>")

    # 行：0.03s 级联（区域标签 + 拍行）
    r = 0
    for i in row_region:
        delay = f"{r * 0.03:.2f}s"
        out.append(f'<g class="row" style="animation-delay:{delay}">')
        out.append(lines[i])
        out.append("</g>")
        r += 1

    # 绿色汇总框：row 入场 + chg 脉冲
    delay = f"{r * 0.03:.2f}s"
    out.append(f'<g class="row" style="animation-delay:{delay}">')
    out.append('<g class="chg">')
    out.extend(lines[green_rect:orange_rect])
    out.append("</g>")
    out.append("</g>")
    r += 1

    # 橙色汇总框
    delay = f"{r * 0.03:.2f}s"
    out.append(f'<g class="row" style="animation-delay:{delay}">')
    out.extend(lines[orange_rect:svg_end_idx])
    out.append("</g>")

    out.append(lines[svg_end_idx])  # </svg>
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return r + 1  # 总行数（含两个汇总框）


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
    import re as _re
    def svgtag(p):
        m = _re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    return res


def main():
    n = build()
    res = check()
    print(f"[make_anim_beat] rows={n}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 15:05
