#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_lsp_kcode.py
把 spec_lsp_kcode.svg（LSP 序列与 K 码 K1~K4）转成纯 CSS 动画 SVG（确定性行分组变换，无手工编辑）。

变换规则（纯 CSS，in-SVG <style>，无 script，无外部资源；数据文本/几何/颜色/width/height/viewBox 全部不变）：
- 标题 + 副标题 包 <g class="head">（一次性 reveal）。
- 各单元自上而下以 <g class="row"> reveal（0.06s 级联）：
  编码前行（K2 + 0xEA..×8 + K3 + 括号 + "32 Byte" 标注）/ 编码后行（+ dmy + "280b" 注）/
  "K 码（K1 ~ K4）· 40-bit · 不加扰" 节标题 / K1 / K2 / K3 / K4（自上而下逐行构建）/
  底部 先发/后发 蓝色箭头 + 串行方向注。
- K3 行（"K3 放在序列最后" 高亮）内层包 <g class="breathe"> 呼吸脉冲（必选 infinite 动画；
  外层 reveal 与内层 breathe 分属不同 <g>，同一元素不叠两个动画）。
- 先发/后发箭头仅 14px 高，flow dot 效果不可靠 → 按护栏跳过，仅用 breathe 满足必选 infinite。
- prefers-reduced-motion：关闭动画并强制显示。
- 输出后自检：XML well-formed、<text> 多重集与源一致、无 <script>、≥1 @keyframes、
  <svg> 开标签与源一致、size>1KB、打印分组计数。
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_lsp_kcode.svg"
OUT = BASE / "anim" / "spec_lsp_kcode.svg"
NAME = "make_anim_spec_lsp_kcode"

STEP = 0.06  # 行 reveal 级联步长（秒）

STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".breathe { animation: br 3.2s ease-in-out infinite; }\n"
    "@keyframes br { 0%,100% { opacity:1; } 50% { opacity:0.55; } }\n"
    "@media (prefers-reduced-motion: reduce) {\n"
    "  * { animation: none !important; }\n"
    "  .row, .head { opacity:1 !important; }\n"
    "}\n"
    "</style>"
)


def cont(*subs):
    def pred(line):
        return all(s in line for s in subs)
    return pred


UNITS = [
    dict(cls="head", start=cont("LSP 序列与 K 码"), end=cont("K3 放在序列最后"), end_kind="first"),
    dict(cls="row", start=cont(">编码前<"), end=cont("32 Byte"), end_kind="first"),
    dict(cls="row", start=cont(">编码后<"), end=cont("280b"), end_kind="first"),
    dict(cls="row", start=cont("K 码（K1 ~ K4）· 40-bit"), end=cont("K 码（K1 ~ K4）· 40-bit"), end_kind="first"),
    dict(cls="row", start=cont('<rect x="60" y="350"'), end=cont("11 0000000000 11110000"), end_kind="first"),
    dict(cls="row", start=cont('<rect x="60" y="396"'), end=cont("00 1111111111 00001100"), end_kind="first"),
    dict(cls="row", start=cont('<rect x="60" y="442"'), end=cont("11 0000000000 11000011"), end_kind="first",
         breathe=dict(kind="whole", delay=None)),
    dict(cls="row", start=cont('<rect x="60" y="488"'), end=cont("00 1111111111 00110011"), end_kind="first"),
    dict(cls="row", start=cont('x1="950"'), end=cont("LSB-first"), end_kind="first"),
]


def find_idx(lines, pred, lo, hi=None, unique=True):
    hi = len(lines) if hi is None else hi
    hits = [i for i in range(lo, hi) if pred(lines[i])]
    if unique:
        assert len(hits) == 1, f"期望唯一命中 (lo={lo})，实际 {len(hits)} 处: {hits}"
    else:
        assert hits, f"无命中 (lo={lo})"
    return hits[0]


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # 结构断言（确定性前提）
    assert lines[0].startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    svg_end = len(lines) - 1
    assert lines[2].strip() == "<defs>", "line3 应为 <defs>"
    defs_end = next(i for i in range(3, svg_end) if lines[i].strip() == "</defs>")
    bg = defs_end + 1
    assert lines[bg].lstrip().startswith('<rect width="1200"'), "defs 后应为白色背景 rect"
    content_start = bg + 1

    out = [lines[0], STYLE.replace("\n", eol), lines[1]]
    out.extend(lines[2:bg + 1])  # defs + 白色背景（不参与动画）

    counts = {"head": 0, "row": 0, "breathe": 0}
    cursor = content_start
    row_no = 0
    for u in UNITS:
        s = find_idx(lines, u["start"], cursor)
        if u["end_kind"] == "before":
            e = find_idx(lines, u["end"], s + 1, unique=False) - 1
        else:
            e = find_idx(lines, u["end"], s, unique=False)
        assert e >= s, f"单元范围倒置: {s}..{e}"
        assert s == cursor, f"单元间存在空隙: cursor={cursor}, start={s}（行被丢弃）"
        counts[u["cls"]] += 1
        if u["cls"] == "row":
            row_no += 1
            out.append(f'<g class="row" style="animation-delay:{row_no * STEP:.2f}s">')
        else:
            out.append('<g class="head">')
        br = u.get("breathe")
        if br is None:
            out.extend(lines[s:e + 1])
        else:
            counts["breathe"] += 1
            if br["kind"] == "whole":
                bs, be = s, e
            else:
                bs = find_idx(lines, br["from"], s + 1, unique=False)
                be = e
                assert bs <= be, f"breathe 范围倒置: {bs}..{be}"
            out.extend(lines[s:bs])
            btag = '<g class="breathe">'
            if br.get("delay"):
                btag = f'<g class="breathe" style="animation-delay:{br["delay"]:.1f}s">'
            out.append(btag)
            out.extend(lines[bs:be + 1])
            out.append("</g>")
        out.append("</g>")
        cursor = e + 1

    assert cursor == svg_end, f"内容行未完全覆盖: cursor={cursor}, svg_end={svg_end}"
    out.append(lines[svg_end])

    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return counts


NS = "{http://www.w3.org/2000/svg}"


def check():
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

    data = OUT.read_text(encoding="utf-8")
    res["no_script"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = (f"OK ({data.count('@keyframes')} @keyframes)"
                        if data.count("@keyframes") >= 1 else "NG")

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"

    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    return res


def main():
    counts = build()
    res = check()
    print(f"[{NAME}] groups: head={counts['head']} row={counts['row']} breathe={counts['breathe']}")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 18:42
