#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_8b10b_vs_420b.py — v2（Motion Kit v2 整体重写）

把 8b10b_vs_420b_architecture.svg（1400x1210 双列架构对比图）升级为 v2 动效：
入场编排 + 箭头自绘 + 数据列车（双列赛跑）+ 单元格行波 + 英雄辉光。

源结构锚点（1-based 行号，read 出的 lines[i-1]）：
  1  <svg> ｜ 2 字体 <style> ｜ 3-9 <defs> ｜ 10 白底 rect ｜ 11-12 标题/副标题
  左列 13-43：容器(13)+列标题(14)+Test Layer(15-17)+isptx_sequence(18-29,
    含 5 个 chip 单元格 20-29)+transaction(30-33)+driver(34-36)+DUT(37-40)
    +线上数据验证(41-43)
  右列 44-78：容器(44)+列标题(45)+Test Layer(46-48)+isptx_sequence 420b(49-60,
    含 5 个 chip 单元格 51-60)+ref model(61-64)+transaction(65-68)+driver(69-71)
    +DUT(72-75)+线上数据验证 0717(76-78)
  spine 箭头：左 79-83（x=360）、右 84-88（x=1040），各 5 段
  底部对照表：容器(89)+标题(90)+表头(91-96)+13 数据行(97-174, 每行 3rect+3text)
  175 </svg>

v2 编排（kit §4.3）：
  行序：标题(0) → 左列盒自上而下(0.15 起步进 0.12) → 右列盒(0.30 起步进 0.12)
        → 底部对比区(1.4 表头组; 13 数据行 1.45 起步进 0.04, 总时长 ≤2.5s)
  draw：两列 10 段 spine 箭头（左 0.5+0.1e / 右 0.65+0.1e），pathLength=100
  flow：双列"赛跑"——每段 spine 复制 2 个 flowdot（周期 0.7s），列车按边序
        错 phase（0.11s/边 = 16/100*0.7s 恰好接续）；右列整体再偏移 0.35s
  cellwave：两列各 5 个 chip 单元格（rect+text 逐格包 g），自上而下 0.1s/格，
        周期 3.2s；右列整体偏移半周期 1.6s（双列不同相）
  glow：左"线上数据验证"盒 glow-b / 右"线上数据验证（0717 新增）"盒 glow-g
  march：源图无虚线边框盒 → 不用。breathe：kit 明示不加。

不变量：源 SVG 只读；text 多重集 / <svg> 开标签零改动；纯 CSS 无 <script>；
kit §2 样式逐字嵌入；reduced-motion 块原样；确定性幂等。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "8b10b_vs_420b_architecture.svg"
OUT = BASE / "anim" / "8b10b_vs_420b_architecture.svg"

# ---- Motion Kit v2 CSS（§2 逐字，多行作为一个 <style> 块整体插入） ----
KIT_CSS = """<style>
.row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.cellwave{animation:wave 3s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}
.march{animation:march 1.8s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.glow-b{animation:glowB 2.8s ease-in-out infinite}
@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}
.glow-g{animation:glowG 2.8s ease-in-out infinite}
@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}
.glow-o{animation:glowO 2.8s ease-in-out infinite}
@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}
</style>"""

# spine 箭头几何（y 区段，两列相同）：段长 16
SPINE_Y = [(174, 190), (316, 332), (392, 408), (464, 480), (558, 574)]
FLOW_PERIOD = 0.7       # 每段列车周期（kit §4.3）
FLOW_EDGE_STEP = 0.11   # 相邻段 phase 差 ≈ 16/100*0.7s（段间恰接续）
FLOW_PACKETS = 2        # 每段 2 包，错半周期
RIGHT_PHASE = 0.35      # 右列整体相位偏移（赛跑）
CW_STEP = 0.1           # cellwave 0.1s/格
CW_PERIOD = 3.2         # cellwave 周期（kit §4.3 指定 3.2s）
CW_RIGHT_PHASE = 1.6    # 右列行波偏移半周期


def tag_draw(line: str, delay: float) -> str:
    """给实线箭头 <line> 加 .draw + pathLength + delay（属性追加在 /> 前，原属性零改动）。"""
    assert line.rstrip().endswith("/>") and "<line" in line, f"非 line 元素: {line}"
    return line.rstrip()[:-2] + f' class="draw" pathLength="100" style="animation-delay:{delay:.2f}s"/>'


def flow_path(x: int, y0: int, y1: int, delay: float) -> str:
    return (f'<path class="flowdot" d="M {x} {y0} L {x} {y1}" pathLength="100" '
            f'stroke="#2563eb" stroke-width="2.5" '
            f'style="animation-duration:{FLOW_PERIOD}s;animation-delay:{delay:.2f}s"/>')


def build() -> dict:
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    L = [s for s in lines]  # 0-based; 文件第 n 行 = L[n-1]

    # ---- 结构断言（确定性前提） ----
    assert L[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert "font-family" in L[1], "line2 应为字体 <style>"
    assert L[174].strip() == "</svg>", "末行应为 </svg>"
    assert ">8B/10B vs 420B 长编码" in L[10], "line11 应为标题"
    assert "0717v1 修正" in L[11], "line12 应为副标题"
    assert L[12].startswith('<rect x="40" y="88" width="640"'), "line13 左列容器"
    assert L[43].startswith('<rect x="720" y="88" width="640"'), "line44 右列容器"
    for k, (y0, y1) in zip(range(78, 83), SPINE_Y):
        assert L[k] == f'<line x1="360" y1="{y0}" x2="360" y2="{y1}" stroke="#2563eb" stroke-width="1.5" marker-end="url(#ar-blue)"/>', f"左箭头 line{k+1}"
    for k, (y0, y1) in zip(range(83, 88), SPINE_Y):
        assert L[k] == f'<line x1="1040" y1="{y0}" x2="1040" y2="{y1}" stroke="#2563eb" stroke-width="1.5" marker-end="url(#ar-blue)"/>', f"右箭头 line{k+1}"
    assert L[88].startswith('<rect x="40" y="690" width="1320"'), "line89 表容器"
    assert ">关键差异对照<" in L[89], "line90 表标题"
    row_re = re.compile(r'^<rect x="60" y="(\d+)" width="210" height="32"')
    dstart = []
    i = 96
    while i < 174 and row_re.match(L[i]):
        dstart.append(i)
        assert all(t.strip().startswith("<rect") for t in L[i + 1:i + 3]), "数据行 rect"
        assert all(t.strip().startswith("<text") for t in L[i + 3:i + 6]), "数据行 text"
        i += 6
    assert len(dstart) == 13, f"应为 13 数据行, 实得 {len(dstart)}"
    assert dstart[-1] + 6 == 174, "末数据行应紧邻 </svg>"

    out = []
    out.append(L[0])                       # <svg ...> 原样
    out.append(L[1])                       # 字体 <style> 保留（行 2）
    out.extend(KIT_CSS.split("\n"))        # motion <style>（行 3 起，kit 逐字）
    out.extend(L[2:10])                    # <defs> + 白底 rect

    # 标题/副标题 → .head
    out.append('<g class="head">')
    out.append(L[10]); out.append(L[11])
    out.append("</g>")

    def cellwave_pair(rect_i, text_i, delay):
        return ([f'<g class="cellwave" style="animation-duration:{CW_PERIOD}s;animation-delay:{delay:.2f}s">',
                 L[rect_i], L[text_i], "</g>"])

    counts = {"draw": 0, "flowdot": 0, "cellwave": 0, "glow": 0, "row": 0, "head": 1}

    # ---- 左列（盒自上而下 delay 0.15 步进 0.12） ----
    out.append('<g class="row" style="animation-delay:0.15s">')
    out.extend(L[12:17])      # 容器 + 列标题 + Test Layer
    out.append("</g>")
    out.append('<g class="row" style="animation-delay:0.27s">')
    out.append(L[17]); out.append(L[18])
    for c, (r, t) in enumerate([(19, 20), (21, 22), (23, 24), (25, 26), (27, 28)]):
        out.extend(cellwave_pair(r, t, c * CW_STEP))
        counts["cellwave"] += 1
    out.append("</g>")
    for d, (a, b) in [(0.39, (29, 33)), (0.51, (33, 36)), (0.63, (36, 40))]:
        out.append(f'<g class="row" style="animation-delay:{d}s">')
        out.extend(L[a:b])
        out.append("</g>")
    out.append('<g class="row" style="animation-delay:0.75s">')
    out.append('<g class="glow-b" style="animation-delay:1.4s">')
    out.extend(L[40:43])      # 左"线上数据验证"（结果盒）
    out.append("</g></g>")
    counts["glow"] += 1
    counts["row"] += 6

    # ---- 右列（delay 0.30 步进 0.12） ----
    out.append('<g class="row" style="animation-delay:0.3s">')
    out.extend(L[43:48])      # 容器 + 列标题 + Test Layer
    out.append("</g>")
    out.append('<g class="row" style="animation-delay:0.42s">')
    out.append(L[48]); out.append(L[49])
    for c, (r, t) in enumerate([(50, 51), (52, 53), (54, 55), (56, 57), (58, 59)]):
        out.extend(cellwave_pair(r, t, CW_RIGHT_PHASE + c * CW_STEP))
        counts["cellwave"] += 1
    out.append("</g>")
    for d, (a, b) in [(0.54, (60, 64)), (0.66, (64, 68)), (0.78, (68, 71)), (0.90, (71, 75))]:
        out.append(f'<g class="row" style="animation-delay:{d}s">')
        out.extend(L[a:b])
        out.append("</g>")
    out.append('<g class="row" style="animation-delay:1.02s">')
    out.append('<g class="glow-g" style="animation-delay:1.55s">')
    out.extend(L[75:78])      # 右"线上数据验证（0717 新增）"（结果盒）
    out.append("</g></g>")
    counts["glow"] += 1
    counts["row"] += 7

    # ---- spine 箭头：draw 自绘（左 0.5+0.1e / 右 0.65+0.1e） ----
    for e, k in enumerate(range(78, 83)):
        out.append(tag_draw(L[k], 0.5 + 0.1 * e))
        counts["draw"] += 1
    for e, k in enumerate(range(83, 88)):
        out.append(tag_draw(L[k], 0.65 + 0.1 * e))
        counts["draw"] += 1

    # ---- 数据列车：双列赛跑（每段 2 包，周期 0.7s；右列整体 +0.35s） ----
    for x, base in ((360, 1.15), (1040, 1.15 + RIGHT_PHASE)):
        for e, (y0, y1) in enumerate(SPINE_Y):
            for p in range(FLOW_PACKETS):
                delay = base + e * FLOW_EDGE_STEP + p * (FLOW_PERIOD / 2.0)
                out.append(flow_path(x, y0, y1, delay))
                counts["flowdot"] += 1

    # ---- 底部对比区：表头组 1.4；13 数据行 1.45 起步进 0.04 ----
    out.append('<g class="row" style="animation-delay:1.4s">')
    out.extend(L[88:96])      # 表容器 + 表标题 + 表头
    out.append("</g>")
    counts["row"] += 1
    for r, s0 in enumerate(dstart):
        out.append(f'<g class="row" style="animation-delay:{1.45 + 0.04 * r:.2f}s">')
        out.extend(L[s0:s0 + 6])
        out.append("</g>")
    counts["row"] += 13

    out.append(L[174])        # </svg>
    text = eol.join(out)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return counts


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
    res = {}
    try:
        ET.parse(str(OUT)); res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG: {e}"

    def texts(p):
        return Counter(el.text or "" for el in ET.parse(str(p)).getroot().iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except ET.ParseError as e:
        res["text"] = f"NG: {e}"
    data = OUT.read_text(encoding="utf-8")
    size = os.path.getsize(OUT)
    res["size"] = "OK" if size > 1024 else "NG"
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["rmfix"] = "OK" if (re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
                            and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    return res, data


def main():
    counts = build()
    res, data = check()
    print("[make_anim_8b10b_vs_420b v2] effects:",
          " ".join(f"{k}={v}" for k, v in counts.items()))
    for k, v in res.items():
        print(f"  {k}: {v}")
    ok = all(str(v).startswith("OK") for v in res.values())
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:15
