#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_pydec_txrx.py
把 pydec_tx_rx_structure.svg 转成纯 CSS 动画 SVG（确定性结构分组变换，可复跑）。

变换规则（零数据/文本/几何/颜色改动，无 <script>，无外部资源）：
- 在 <svg> 行（第 1 行）之后、既有字体 <style> 之前插入动画 <style>（字体 <style> 原样保留）。
- 显隐（一次性, forwards）：
  * 标题+副标题 -> <g class="head">（delay 0）
  * 结构层（左 TX 面板、串行链路、右 RX 面板、底部离线比对面板、箭头区）
    -> <g class="row" style="animation-delay: N*0.04s">
  * 底部图例 -> <g class="head">（delay 0）
- 无限效果（嵌套分组，不与 reveal 冲突）：
  * breathe: 绿色 TAP 胶囊、绿色 verdict 框（long_pydec_report ✅）-> <g class="breathe">
  * flow packets: 两条蓝色串行 path（TX→RX）与绿色离线 path 各复制一个装饰
    <path class="flowdot">（d 与原边完全一致、同描边色），per-edge @keyframes 驱动
    stroke-dashoffset 递减（源→目标方向）；L = 解析 M/L/C 坐标实算的 path 长度
    （cubic bezier 按 50 点采样）。
- 输出后自检：XML well-formed、<text> 多重集与源一致、无 <script>、@keyframes 存在、
  <svg> 开标签与源逐字一致、>1KB、.row/.head/.breathe/.flowdot 计数符合预期。
"""
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "pydec_tx_rx_structure.svg"
OUT = BASE / "anim" / "pydec_tx_rx_structure.svg"
NS = "{http://www.w3.org/2000/svg}"


def path_length(d):
    """计算 SVG path 长度（大写 M/L/C；cubic bezier 按 50 点采样）。"""
    raw = re.findall(r"([MLC])|([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)", d)
    groups = []
    for c, n in raw:
        if c:
            groups.append([c, []])
        else:
            groups[-1][1].append(float(n))
    assert groups and all(g[0] in "MLC" for g in groups), \
        f"only absolute M/L/C supported: {[g[0] for g in groups]}"

    def cubic(p0, p1, p2, p3, n=50):
        seg = 0.0
        px, py = p0
        for k in range(1, n + 1):
            t = k / n
            u = 1 - t
            x = u**3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0]
            y = u**3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1]
            seg += math.hypot(x - px, y - py)
            px, py = x, y
        return seg

    total = 0.0
    cx = cy = 0.0
    started = False
    for c, nums in groups:
        if c == "M":
            assert len(nums) % 2 == 0
            if not started:
                cx, cy = nums[0], nums[1]
                j = 2
                started = True
            else:  # 后续 M：move 计长
                total += math.hypot(nums[0] - cx, nums[1] - cy)
                cx, cy = nums[0], nums[1]
                j = 2
            while j + 1 < len(nums):  # 隐式 L
                x, y = nums[j], nums[j + 1]
                j += 2
                total += math.hypot(x - cx, y - cy)
                cx, cy = x, y
        elif c == "L":
            assert len(nums) % 2 == 0
            j = 0
            while j + 1 < len(nums):
                x, y = nums[j], nums[j + 1]
                j += 2
                total += math.hypot(x - cx, y - cy)
                cx, cy = x, y
        else:  # C
            assert len(nums) % 6 == 0
            j = 0
            while j + 6 <= len(nums):
                x1, y1, x2, y2, x, y = nums[j:j + 6]
                j += 6
                total += cubic((cx, cy), (x1, y1), (x2, y2), (x, y))
                cx, cy = x, y
    assert started, "path must start with M"
    return total


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def find_line(lines, needle, start=0):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i
    raise AssertionError(f"line not found: {needle!r}")


def make_style(edges):
    """edges: list of (label, L, delay_s)"""
    p = [
        "<style>",
        ".row { opacity:0; animation: rowIn 0.4s ease forwards; }",
        "@keyframes rowIn { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform: none; } }",
        ".head { opacity:0; animation: rowIn 0.4s ease forwards; }",
        ".breathe { animation: br 3.2s ease-in-out infinite; }",
        "@keyframes br { 0%,100% { opacity:1; } 50% { opacity:0.55; } }",
        ".flowdot { fill:none; }",
    ]
    for i, (label, L, delay) in enumerate(edges, 1):
        p.append(f"/* flow packet {i}: {label} | L={fmt(L)} | period={fmt((L + 88) / 150)}s */")
        d = f"; animation-delay: {fmt(delay)}s" if delay else ""
        p.append(
            f".f{i} {{ stroke-dasharray: 8 {fmt(L + 80)}; "
            f"animation: pkt{i} {fmt((L + 88) / 150)}s linear infinite{d}; }}"
        )
        p.append(
            f"@keyframes pkt{i} {{ from {{ stroke-dashoffset: {fmt(L + 88)}; }} "
            f"to {{ stroke-dashoffset: 0; }} }}"
        )
    p.append("@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head{opacity:1!important}}")
    p.append("</style>")
    return "\n".join(p)


def flowdot_line(cls, d, color, delay):
    st = f' style="animation-delay:{fmt(delay)}s"' if delay else ""
    return (f'<path class="flowdot {cls}" d="{d}" fill="none" stroke="{color}" '
            f'stroke-width="2.5" stroke-linecap="round"{st}/>')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)

    # ---- 结构断言（确定性前提）----
    assert lines[0].startswith("<svg"), "line1 应为 <svg>"
    assert "<style>text" in lines[1], "line2 应为既有字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    svg_end = len(lines) - 1

    title_i = find_line(lines, "420b 收发结构框图")
    assert lines[title_i].strip().startswith("<text")
    assert "DATA_ALIGN_PRE" in lines[title_i + 1], "标题下一行应为副标题"

    left_rect = find_line(lines, "发送端 TX（UVM）") - 1
    rx_rect = find_line(lines, "接收端 RX（DUT + 脚本）") - 1
    bottom_rect = find_line(lines, "离线比对（脚本完成") - 1
    for r in (left_rect, rx_rect, bottom_rect):
        assert lines[r].strip().startswith("<rect"), f"面板 rect 缺失: {lines[r]}"

    serial_start = find_line(lines, 'd="M 396 292')
    assert left_rect < serial_start < rx_rect, "串行链路应在左右面板之间"
    arrows_start = next(i for i in range(bottom_rect + 2, svg_end)
                        if lines[i].strip().startswith("<line"))
    assert arrows_start > bottom_rect
    legend_i = find_line(lines, ">主数据流（线上）<") - 1
    assert lines[legend_i].strip().startswith("<line"), "图例首行应为 <line>"
    assert legend_i > arrows_start

    # TAP 胶囊（RX 面板内）：rect + 1 text
    tap_i = find_line(lines, ">TAP<", rx_rect)
    assert lines[tap_i - 1].strip().startswith("<rect"), "TAP 文本前一行应为 rect"
    assert rx_rect < tap_i < bottom_rect
    # verdict 绿框（底部面板内）：rect + 3 text
    verdict_i = find_line(lines, "long_pydec_report_lane0.md", bottom_rect)
    assert lines[verdict_i - 1].strip().startswith("<rect"), "verdict 前一行应为 rect"
    assert lines[verdict_i + 1].strip().startswith("<text")
    assert lines[verdict_i + 2].strip().startswith("<text")
    assert bottom_rect < verdict_i < arrows_start

    # flow packet 边
    b1_i = find_line(lines, 'd="M 396 292')
    b2_i = find_line(lines, 'd="M 396 304')
    g1_i = find_line(lines, 'd="M 1003 364')
    get_d = lambda i: re.search(r'd="([^"]+)"', lines[i]).group(1)
    d_b1, d_b2, d_g1 = get_d(b1_i), get_d(b2_i), get_d(g1_i)
    edges = [
        ("blue serial #1", path_length(d_b1), 0.0),
        ("blue serial #2", path_length(d_b2), 0.8),
        ("green offline", path_length(d_g1), 1.6),
    ]

    # ---- 组装 ----
    out = []
    out.append(lines[0])  # <svg ...>（width/height/viewBox 原样保留）
    out.append(make_style(edges))  # 动画 <style>，插在 line1 之后
    out.extend(lines[1:title_i])  # 既有字体 <style> + <defs> + 白色背景 rect（原样保留）

    out.append('<g class="head">')
    out.extend(lines[title_i:title_i + 2])  # 标题 + 副标题
    out.append("</g>")

    rows = [
        (left_rect, serial_start, ()),          # 左 TX 面板
        (serial_start, rx_rect, ()),            # 串行链路（2 path + 旋转标注）
        (rx_rect, bottom_rect, ((tap_i - 1, tap_i + 1),)),  # 右 RX 面板
        (bottom_rect, arrows_start, ((verdict_i - 1, verdict_i + 3),)),  # 底部面板
        (arrows_start, legend_i, ()),           # 箭头区
    ]
    for r, (a, b, breathes) in enumerate(rows):
        delay = f"{r * 0.04:.2f}s"
        out.append(f'<g class="row" style="animation-delay:{delay}">')
        i = a
        for bs, be in breathes:
            assert bs >= i and be <= b
            while i < bs:
                out.append(lines[i])
                i += 1
            out.append('<g class="breathe">')
            out.extend(lines[i:be])
            out.append("</g>")
            i = be
        while i < b:
            out.append(lines[i])
            i += 1
        out.append("</g>")

    out.append('<g class="head">')
    out.extend(lines[legend_i:svg_end])  # 底部图例
    out.append("</g>")

    # flow packets（装饰性，置于 reveal 分组之外、文件末尾）
    out.append(flowdot_line("f1", d_b1, "#2563eb", edges[0][2]))
    out.append(flowdot_line("f2", d_b2, "#2563eb", edges[1][2]))
    out.append(flowdot_line("f3", d_g1, "#059669", edges[2][2]))

    out.append(lines[svg_end])  # </svg>
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return edges


def check(edges):
    res = {}
    # 1. XML well-formed
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"
        return res

    # 2. <text> 多重集一致
    def texts(p):
        root = ET.parse(str(p)).getroot()
        return Counter(el.text or "" for el in root.iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text"] = f"NG: {e}"

    data = OUT.read_text(encoding="utf-8")
    # 3. 无 <script>
    res["no_script"] = "OK" if "<script" not in data else "NG"
    # 4. keyframes 存在
    res["keyframes"] = "OK" if "@keyframes" in data else "NG"
    # 5. <svg> 开标签与源一致
    m1 = re.search(r"<svg[^>]*>", SRC.read_text(encoding="utf-8"))
    m2 = re.search(r"<svg[^>]*>", data)
    res["svg_tag"] = "OK" if m1 and m2 and m1.group(0) == m2.group(0) else "NG"
    # 6. 文件大小
    size = os.path.getsize(OUT)
    res["size"] = f"OK ({size} bytes)" if size > 1024 else "NG"
    # 7b. 既有字体 <style> 行逐字保留
    src_lines = SRC.read_text(encoding="utf-8", newline="").split(
        "\r\n" if "\r\n" in SRC.read_text(encoding="utf-8", newline="") else "\n")
    font_line = next(l for l in src_lines if "font-family" in l)
    res["font_style"] = "OK" if font_line in data else "NG"
    # 7. 分组计数
    expected = {
        r'class="row"': 5,
        r'class="head"': 2,
        r'class="breathe"': 2,
        r'class="flowdot': 3,
    }
    for pat, want in expected.items():
        got = len(re.findall(pat, data))
        res[f"count.{pat}"] = f"OK ({got})" if got == want else f"NG (got {got}, want {want})"
    return res


def main():
    edges = build()
    res = check(edges)
    print("[make_anim_pydec_txrx] flow edges:")
    for label, L, delay in edges:
        print(f"  {label}: L={fmt(L)} period={fmt((L + 88) / 150)}s delay={delay}s")
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-26 19:22
