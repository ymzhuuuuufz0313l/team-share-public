#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_dummy_70b.py
把 spec_dummy_70b.svg 转成纯 CSS 动画 SVG（确定性 <g> 分组 + <style> 注入 + 流向粒子，无手工编辑）。

结构：
- 标题 + 副标题            -> <g class="head">（delay 0）
- 4 个流水线步骤框（rect+text+后续箭头）-> 各 <g class="row">，0.06s 级联（①→④ 从左到右）
    每条流水线箭头上叠 <path class="flowdot">（stroke-dashoffset 动画，数据 ①→②→③→④ 流动）
- 3 条数据行（LSP / Active Line / Config Line：左标签框 + Before 框 + After 框 + 连接箭头）
    -> 各 <g class="row">，0.30/0.35/0.40s
    - Active 行 "D · 70b×N" 与 "K5~K8" 单元格 -> <g class="breathe">（呼吸）
- 底部注释                 -> <g class="head">（delay 0.45s）

不改动任何数据文本/几何/颜色；width/height/viewBox 与源一致。
输出后自检：XML well-formed、<text> 多重集与源一致、无 <script>、≥1 @keyframes、
<svg> 开标签与源一致、文件 >1KB、打印分组计数。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_dummy_70b.svg"
OUT = BASE / "anim" / "spec_dummy_70b.svg"

ANIM_STYLE = (
    "<style>\n"
    ".row { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }\n"
    ".head { opacity:0; animation: rowIn 0.4s ease forwards; }\n"
    ".breathe { animation: br 3.2s ease-in-out infinite; }\n"
    "@keyframes br { 0%,100% { opacity:1; } 50% { opacity:0.55; } }\n"
    ".flowdot { stroke-dasharray: 8 110; animation: pkt 0.947s linear infinite; }\n"
    "@keyframes pkt { from { stroke-dashoffset:110; } to { stroke-dashoffset:0; } }\n"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important} .row,.head{opacity:1!important}}\n"
    "</style>"
)


def flowdot(x1, x2, y, delay):
    """在流水线箭头（长度 30）上叠一个 stroke-dashoffset 流动粒子。"""
    return (
        f'<path class="flowdot" d="M {x1} {y} L {x2} {y}" fill="none" '
        f'stroke="#2563eb" stroke-width="2.5" stroke-linecap="round" '
        f'style="animation-delay:{delay}s"/>'
    )


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # 结构断言（确定性前提）
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"

    def find_text_idx(prefix, start=0, end=None):
        end = len(lines) if end is None else end
        for i in range(start, end):
            s = lines[i].strip()
            if not s.startswith("<text"):
                continue
            m = re.search(r'>([^<]*)</text>$', s)
            if m and m.group(1).startswith(prefix):
                return i
        raise AssertionError(f"text not found: {prefix}")

    title_idx = find_text_idx("非 413b 整数倍数据处理")
    subtitle_idx = find_text_idx("编码后去掉")
    s1 = find_text_idx("① 补 Dmy")
    s2 = find_text_idx("② 加扰")
    s3 = find_text_idx("③ 413b/420b 编码")
    s4 = find_text_idx("④ 去 dummy")
    lsp = find_text_idx("LSP")
    active = find_text_idx("Active Line")
    config = find_text_idx("Config Line")
    note_idx = find_text_idx("多通道对齐示例")

    # 顺序断言（内容定位正确性）
    assert title_idx < subtitle_idx < s1 < s2 < s3 < s4 < lsp < active < config < note_idx, \
        f"顺序异常: {title_idx} {subtitle_idx} {s1} {s2} {s3} {s4} {lsp} {active} {config} {note_idx}"

    # 行范围（每行 = 左标签框起，至下一行左标签框前）
    lsp_start, lsp_end = lsp - 1, active - 1
    active_start, active_end = active - 1, config - 1
    config_start, config_end = config - 1, note_idx

    # Active 行的呼吸单元（"D · 70b×N" 与 "K5~K8"：rect + text）
    active_slice = lines[active_start:active_end]
    breathe_ranges = []
    for j, s in enumerate(active_slice):
        t = s.strip()
        if t.startswith("<text") and (">D · 70b×N<" in t or ">K5~K8<" in t):
            assert active_slice[j - 1].strip().startswith("<rect"), "呼吸单元前一行应为 rect"
            breathe_ranges.append((j - 1, j + 1))
    assert len(breathe_ranges) == 2, f"Active 行呼吸单元应为 2，实际 {len(breathe_ranges)}"

    def emit_with_breathe(slice_, ranges):
        out, i = [], 0
        for (a, b) in sorted(ranges):
            out.extend(slice_[i:a])
            out.append('<g class="breathe">')
            out.extend(slice_[a:b])
            out.append("</g>")
            i = b
        out.extend(slice_[i:])
        return out

    # 组装输出
    out = []
    out.append(lines[0])            # <svg ...>（原样保留 width/height/viewBox）
    out.append(ANIM_STYLE)          # 动画 <style>，紧跟 <svg>
    out.append(lines[1])            # 原字体 <style>（保留）
    # <defs>（marker 定义）
    defs_end = next(i for i in range(2, 20) if lines[i].strip() == "</defs>")
    out.extend(lines[2:defs_end + 1])
    # 白色背景 rect（不透明，不参与动画）
    bg_idx = next(i for i in range(defs_end, note_idx)
                  if "width=\"1200\"" in lines[i] and "fill=\"#ffffff\"" in lines[i])
    out.append(lines[bg_idx])

    # head：标题 + 副标题
    out.append('<g class="head" style="animation-delay:0s">')
    out.extend(lines[title_idx:subtitle_idx + 1])
    out.append("</g>")

    # 4 个步骤框（rect + text + 箭头 + 流向粒子）
    step_specs = [
        (s1, "0.06", 314, 344, "0"),
        (s2, "0.12", 604, 634, "0.13"),
        (s3, "0.18", 894, 924, "0.26"),
        (s4, "0.24", None, None, None),
    ]
    for (idx, delay, ax1, ax2, fdelay) in step_specs:
        out.append(f'<g class="row" style="animation-delay:{delay}s">')
        out.append(lines[idx - 1])      # 步骤框 rect
        out.append(lines[idx])          # 步骤标签 text
        if ax1 is not None:
            out.append(lines[idx + 1])  # 连接箭头 line
            out.append(flowdot(ax1, ax2, 106, fdelay))
        out.append("</g>")

    # LSP 行
    out.append('<g class="row" style="animation-delay:0.30s">')
    out.extend(lines[lsp_start:lsp_end])
    out.append("</g>")

    # Active Line 行（含呼吸单元）
    out.append('<g class="row" style="animation-delay:0.35s">')
    out.extend(emit_with_breathe(active_slice, breathe_ranges))
    out.append("</g>")

    # Config Line 行
    out.append('<g class="row" style="animation-delay:0.40s">')
    out.extend(lines[config_start:config_end])
    out.append("</g>")

    # 底部注释
    out.append('<g class="head" style="animation-delay:0.45s">')
    out.extend(lines[note_idx:note_idx + 1])
    out.append("</g>")

    out.append(lines[-1])            # </svg>

    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
    res = {}
    # 1. XML well-formed
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"
    # 2. <text> 多重集与源一致
    def texts(p):
        root = ET.parse(str(p)).getroot()
        return Counter(el.text or "" for el in root.iter(f"{NS}text"))
    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text"] = f"NG: {e}"
    data = OUT.read_text(encoding="utf-8")
    # 3. 无 <script
    res["no_script"] = "OK" if "<script" not in data else "NG"
    # 4. ≥1 @keyframes
    nkey = data.count("@keyframes")
    res["keyframes"] = f"OK ({nkey})" if nkey >= 1 else "NG"
    # 5. <svg> 开标签与源一致
    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""
    res["svg_tag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    # 6. size > 1024
    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    counts = {
        "row": data.count('class="row"'),
        "head": data.count('class="head"'),
        "breathe": data.count('class="breathe"'),
        "flowdot": data.count('class="flowdot"'),
        "keyframes": data.count("@keyframes"),
    }
    print("[make_anim_spec_dummy_70b] groups:", counts)
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 18:49
