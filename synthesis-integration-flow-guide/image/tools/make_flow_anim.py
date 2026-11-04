#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
make_flow_anim.py — 确定性生成脚本：静态 graphviz SVG -> 动画 SVG（纯 CSS，网站用）

★「流向版」特效（2026-10-26 重写）: 视觉焦点全部放在"数据怎么走"上。
   规则 1/2/3/6（fireworks-tech-graph skill · Animated SVG）: 纯 CSS、零数据变更、
   infinite 只动 opacity/transform/filter/stroke-dashoffset、六项校验。

  1. 无入场动画: 删掉 rowIn / scale-in / scanSweep / nodeShimmer / edgePulse / frameDrift。
     图直接静态呈现，任何元素不得有 opacity:0 初始态（终态 == 静态图）。
  2. 虚线边 dash march（12 条, 按 path 是否有 stroke-dasharray 自动判定）:
     stroke-dashoffset 0 -> -7（7 = dash5+gap2, 无缝）, 周期 1.1s（比上一版 1.4s 更快）,
     方向沿路径（源 -> 目标, 指向箭头）。
  3. 实线边流光点（22 条）: 每条实线边新增一条装饰 path（class="flowdot", d 与原边完全相同,
     fill=none, stroke=#0e7490, stroke-width=2.5, stroke-linecap=round）。
     stroke-dasharray "8 GAP" + stroke-dashoffset 动画, GAP 与周期按每条边数值计算的路径长度 L
     定制（Python 解析 path 的 M/C 坐标, 对 cubic bezier 采样 50 点求长度）:
       GAP = L + 80;  @keyframes 从 stroke-dashoffset:(L+88) 到 0
       （dashoffset 递减 = 光点从路径起点流向终点, 指向箭头; 脚本内置方向校验）
       周期 = (L+88)/150 s（统一 150pt/s 速度）, linear infinite, delay i*0.13s。
     采用每边独立 keyframes（pkt1..pkt22, 具体数值）——比 "var() in keyframes" 更稳, 零兼容性风险。
  4. 门禁节点呼吸（仅 2 个）: 按 <title> 内容定位 signoff(node16) 与 to_signoff(node29),
     infinite opacity 1<->0.55, 3.2s。其余 30 个节点无任何动画。
  5. 其余一律无动画。

  零数据变更: 只新增 <style>、22 条装饰 flowdot path、以及既有元素的 class 属性；
  全部 <text> 内容、既有几何、颜色、opacity 默认值、viewBox 与静态版一致（校验保证）。
  新增的 flowdot 属"装饰性 path", 类比 skill 扫光实例允许新增的 <rect>, 不改动任何原有元素数据。

幂等: 每次都从未改动的静态源重新解析、重建输出；重复运行产出字节一致（md5 相同）。
用法:  python make_flow_anim.py
源(只读):  E:/project/team-share-public/synthesis-integration-flow-guide/image/script-flow-overview.svg  （静态主名位；原站点根裸图 2026-11-04 归档至 image/archive/20260826/）
输出(覆盖): E:/project/team-share-public/synthesis-integration-flow-guide/image/anim/script-flow-overview.svg
"""
import html
import math
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

SRC = r"E:\project\team-share-public\synthesis-integration-flow-guide\image\script-flow-overview.svg"
OUT = r"E:\project\team-share-public\synthesis-integration-flow-guide\image\anim\script-flow-overview.svg"

# ---- 时序 / 视觉参数 ----
DASH_PERIOD = 1.10      # 虚线 dash march 周期(s): 比上一版 1.4s 更快（约 1.0-1.4s 区间）
DASH_STEP = 7           # dash5 + gap2 = 一个无缝周期（只动 stroke-dashoffset）
DOT_LEN = 8.0           # 流光点 dash 长度（pt）
DOT_GAP_EXTRA = 80.0    # GAP = L + 80
DOT_TAIL = 8.0          # keyframes 从 (L+80+8) = L+88 到 0；末尾 88pt 为出画静息
DOT_SPEED = 150.0       # 流光点统一速度（pt/s）
DOT_STAGGER = 0.13      # 各实线边 animation-delay 错落步长(s)
BREATH_NODES = {"signoff", "to_signoff"}   # 仅这 2 个门禁节点呼吸（按 <title> 定位）
BREATH_PERIOD = 3.2     # 门禁呼吸周期(s), opacity 1<->0.55
SAMPLE_N = 50           # 每条 cubic bezier 采样点数（求路径长度 L）

BLOCK_RE = re.compile(r'^\s*<g id="(clust\d+|node\d+|edge\d+)" class="(cluster|node|edge)">\s*$')
TOKEN_RE = re.compile(r'[MLC]|-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?')


# ---- 路径几何: 解析 M/C, 采样 cubic bezier 求长度 ----
def parse_path(d):
    """返回 (start_pt, segs): segs = [(p0,p1,p2,p3), ...], 直线退化为 p1=p0, p2=p3 的 cubic。"""
    toks = TOKEN_RE.findall(d)
    segs, cur, i, n = [], None, 0, len(toks)
    while i < n:
        t = toks[i]
        if t in "MLC":
            cmd = t
            i += 1
            if cmd == "M":
                x, y = float(toks[i]), float(toks[i + 1]); i += 2
                cur = (x, y)
            elif cmd == "L":
                while i + 1 < n and toks[i] not in "MLC":
                    x, y = float(toks[i]), float(toks[i + 1]); i += 2
                    segs.append((cur, cur, (x, y), (x, y)))
                    cur = (x, y)
            elif cmd == "C":
                while i + 5 < n and toks[i] not in "MLC":
                    x1, y1 = float(toks[i]), float(toks[i + 1])
                    x2, y2 = float(toks[i + 2]), float(toks[i + 3])
                    x, y = float(toks[i + 4]), float(toks[i + 5])
                    i += 6
                    segs.append((cur, (x1, y1), (x2, y2), (x, y)))
                    cur = (x, y)
        else:
            raise SystemExit(f"[error] 未识别的 path token: {t!r}")
    if cur is None or not segs:
        raise SystemExit("[error] path 无有效线段")
    return cur, segs


def sample_cubic(p0, p1, p2, p3, n=SAMPLE_N):
    pts = []
    for k in range(n + 1):
        t = k / n
        mt = 1.0 - t
        a, b, c, d = mt ** 3, 3 * mt ** 2 * t, 3 * mt * t * t, t ** 3
        pts.append((a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                    a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1]))
    return pts


def path_length(segs):
    total = 0.0
    for (p0, p1, p2, p3) in segs:
        pts = sample_cubic(p0, p1, p2, p3)
        for k in range(len(pts) - 1):
            total += math.hypot(pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
    return total


def parse_source(text):
    """解析源 SVG: graph0 头部、大标题、背景多边形、10 簇 / 32 节点 / 34 边（扁平块）。
    边额外记录: d、路径长度 L、箭头多边形点、has_dash。"""
    lines = text.replace("\r\n", "\n").split("\n")
    g0_idx = next(i for i, l in enumerate(lines) if '<g id="graph0"' in l)
    header = lines[: g0_idx + 1]
    title_idx = next(i for i in range(g0_idx + 1, len(lines)) if lines[i].strip().startswith("<title"))
    poly_idx = next(i for i in range(g0_idx + 1, len(lines)) if lines[i].strip().startswith("<polygon"))
    head_idx = next(i for i in range(poly_idx + 1, len(lines)) if lines[i].strip().startswith("<text"))

    blocks, order = {}, []
    i, n = head_idx + 1, len(lines)
    while i < n and lines[i].strip() != "</g>":  # 最后的 </g> 关闭 graph0
        m = BLOCK_RE.match(lines[i])
        if m is None:
            i += 1
            continue
        bid, kind = m.group(1), m.group(2)
        j = i + 1
        while j < n and lines[j].strip() != "</g>":
            if lines[j].strip().startswith("<g"):
                raise SystemExit(f"[error] {bid}: 出现嵌套 <g>，扁平结构假设不成立")
            j += 1
        if j >= n:
            raise SystemExit(f"[error] {bid}: 未找到 </g>")
        blk = lines[i : j + 1]
        raw = "\n".join(blk)
        t = re.search(r"<title>(.*?)</title>", raw)
        d = re.search(r"\bd=\"([^\"]+)\"", raw)
        start = segs = L = None
        arrow_pts = None
        has_dash = any("stroke-dasharray" in l for l in blk if l.strip().startswith("<path"))
        if kind == "edge":
            start, segs = parse_path(d.group(1))
            L = path_length(segs)
            ap = re.search(r"\bpoints=\"([^\"]+)\"", raw)
            if ap:
                arrow_pts = [(float(x), float(y)) for x, y in re.findall(r"(-?[\d.]+),(-?[\d.]+)", ap.group(1))]
        blocks[bid] = {
            "kind": kind,
            "name": html.unescape(t.group(1)) if t else None,
            "d": d.group(1) if d else None,
            "length": L,
            "arrow_pts": arrow_pts,
            "lines": blk,
            "has_dash": has_dash,
        }
        order.append(bid)
        i = j + 1
    return lines, header, title_idx, poly_idx, head_idx, blocks, order


def check_structure(blocks, order):
    clusters = [b for b in order if blocks[b]["kind"] == "cluster"]
    nodes = [b for b in order if blocks[b]["kind"] == "node"]
    edges = [b for b in order if blocks[b]["kind"] == "edge"]
    if not (len(clusters) == 10 and len(nodes) == 32 and len(edges) == 34):
        raise SystemExit(f"[error] 结构数量不符: cluster={len(clusters)} node={len(nodes)} edge={len(edges)}")
    n_dash = sum(1 for b in edges if blocks[b]["has_dash"])
    if n_dash != 12:
        raise SystemExit(f"[error] 虚线边数量不符: {n_dash} != 12")
    gates = [b for b in nodes if blocks[b]["name"] in BREATH_NODES]
    if len(gates) != 2:
        raise SystemExit(f"[error] 门禁节点数量不符: {len(gates)} != 2 -> {[blocks[b]['name'] for b in gates]}")
    return edges, gates


def build_css(dot_params):
    """dot_params: [(i1based, L, GAP, PK, dur, delay), ...] 文档序。生成 pkt1..pktN keyframes。"""
    c = []
    c.append(" <style>")
    c.append("  /* 流向版: 无入场动画, 图静态呈现; infinite 只动 opacity / stroke-dashoffset (规则 1/2/3) */")
    c.append("  /* 1) 虚线边(12, 按 stroke-dasharray 自动判定): dash march, 周期 "
              f"{DASH_PERIOD:.2f}s (比上一版 1.4s 更快), 方向 源->目标(指向箭头) */")
    c.append(f"  .march{{animation:march {DASH_PERIOD:.2f}s linear infinite}}")
    c.append(f"  @keyframes march{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-{DASH_STEP}}}}}")
    c.append("  /* 2) 实线边(22): 流光点 flowdot (装饰 path, d 与原边相同); 每边独立 keyframes pktN")
    c.append("     (比 var() in keyframes 更稳); dasharray 8/GAP(L+80); 周期 (L+88)/150s (统一 150pt/s); delay i*0.13s */")
    c.append("  .flowdot{fill:none;stroke:#0e7490;stroke-width:2.5;stroke-linecap:round}")
    for (idx, L, GAP, PK, dur, delay) in dot_params:
        c.append(f"  @keyframes pkt{idx}{{from{{stroke-dashoffset:{PK:.2f}}}to{{stroke-dashoffset:0}}}}")
    c.append(f"  /* 3) 门禁节点呼吸(仅 2: signoff / to_signoff): opacity 1↔0.55, {BREATH_PERIOD}s */")
    c.append(f"  .breath{{animation:breath {BREATH_PERIOD:.2f}s ease-in-out infinite}}")
    c.append("  @keyframes breath{0%,100%{opacity:1}50%{opacity:0.55}}")
    c.append(" </style>")
    return c


def verify_direction(blocks, order, edges):
    """方向校验: 每条实线边的路径终点(最后 C 段终点)应紧邻箭头多边形(箭头在 path 末端)。
    keyframes 从 (L+88) 递减到 0 = dashoffset 递减 = 光点沿路径 起点(源) -> 终点(目标/箭头)。"""
    bad = []
    for bid in edges:
        if blocks[bid]["has_dash"]:
            continue
        _, segs = parse_path(blocks[bid]["d"])
        end_pt = segs[-1][3]
        ap = blocks[bid]["arrow_pts"]
        if not ap:
            bad.append((bid, "no arrow"))
            continue
        cx = sum(p[0] for p in ap) / len(ap)
        cy = sum(p[1] for p in ap) / len(ap)
        dist = math.hypot(end_pt[0] - cx, end_pt[1] - cy)
        if dist > 6.0:
            bad.append((bid, f"end->arrow dist={dist:.2f}"))
    return bad


def build(lines, header, title_idx, poly_idx, head_idx, blocks, order, edges, dot_params, css_lines):
    out = list(header)
    out += css_lines
    out.append(lines[title_idx])   # <title>script_flow</title>（静态）
    out.append(lines[poly_idx])    # 白色背景多边形（静态）
    out.append(lines[head_idx])    # 整图大标题（静态, 无入场包裹）

    dot_iter = iter(dot_params)
    for bid in order:
        b = blocks[bid]
        if b["kind"] == "edge" and b["has_dash"]:
            # 虚线边: 原 path 加 class="march"（dash march）
            out += [l.replace("<path ", '<path class="march" ', 1)
                    if l.strip().startswith("<path") else l for l in b["lines"]]
        elif b["kind"] == "edge":
            # 实线边: 在原 path 之后插入一条 flowdot 装饰 path（d 与原边相同）
            idx, L, GAP, PK, dur, delay = next(dot_iter)
            flowdot = (f'<path class="flowdot" d="{b["d"]}" '
                       f'style="stroke-dasharray:{DOT_LEN:.0f} {GAP:.2f};'
                       f'animation:pkt{idx} {dur:.3f}s linear {delay:.2f}s infinite"/>')
            newlines = []
            for l in b["lines"]:
                newlines.append(l)
                if l.strip().startswith("<path"):
                    newlines.append(flowdot)
            out += newlines
        elif b["kind"] == "node" and b["name"] in BREATH_NODES:
            # 门禁节点: <g class="node breath">（呼吸）
            out += [l.replace(' class="node"', ' class="node breath"', 1)
                    if l.strip().startswith(f'<g id="{bid}"') else l for l in b["lines"]]
        else:
            out += b["lines"]

    out.append(' </g>')    # 关闭 graph0
    out.append(' </svg>')
    return "\n".join(out) + "\n"


def validate(src_path, out_path):
    res = []

    def add(name, ok, detail):
        res.append((name, bool(ok), detail))

    # 1) XML 良构
    try:
        t1 = ET.parse(src_path)
        t2 = ET.parse(out_path)
        add("1. XML 良构（静态 & 动画）", True, "两份均解析通过")
    except ET.ParseError as e:
        add("1. XML 良构", False, f"ParseError: {e}")
        return res

    NS = "{http://www.w3.org/2000/svg}"

    # 2) <text> 多重集一致
    def texts(root):
        return Counter((e.text or "") for e in root.iter(NS + "text"))
    c1, c2 = texts(t1.getroot()), texts(t2.getroot())
    diff = {k: (c1.get(k, 0), c2.get(k, 0)) for k in set(c1) | set(c2) if c1.get(k, 0) != c2.get(k, 0)}
    add("2. <text> 多重集一致（静态 vs 动画）", c1 == c2,
        f"静态 {sum(c1.values())} 条 / 动画 {sum(c2.values())} 条" + (f" 差异={diff}" if diff else " 完全相同"))

    raw = open(out_path, encoding="utf-8").read()

    # 3) 无 <script>
    has_script = re.search(r"(?is)<script\b", raw)
    add("3. 无 <script>", has_script is None, "未找到 <script>" if not has_script else "发现 <script>!")

    # 4) @keyframes 存在
    kf = re.findall(r"@keyframes\s+([A-Za-z0-9_-]+)", raw)
    add("4. @keyframes 存在", len(kf) >= 1, f"{len(kf)} 组: {', '.join(kf[:4])} ... {', '.join(kf[-2:])}（共 {len(kf)}）")

    # 5) viewBox 相同
    v1, v2 = t1.getroot().get("viewBox"), t2.getroot().get("viewBox")
    add("5. viewBox 相同", v1 == v2, f"静态={v1} / 动画={v2}")

    # 6) 结构计数: flowdot=22, march(虚线 dashmarch)=12, breath=2
    root2 = t2.getroot()
    def cnt(cls):
        return sum(1 for e in root2.iter() if cls in (e.get("class") or "").split())
    expected = {"flowdot": 22, "march": 12, "breath": 2}
    actual = {k: cnt(k) for k in expected}
    bad = {k: (actual[k], expected[k]) for k in expected if actual[k] != expected[k]}
    # 无 opacity:0 初始态（规则 1: 无入场动画）
    has_opacity0 = re.search(r"(?i)opacity\s*:\s*0(?![.\d])", raw) or re.search(r"(?i)\bopacity=\"0\"|opacity=\"0\.\d\"", raw)
    n_g1 = sum(1 for e in t1.getroot().iter(NS + "g"))
    n_g2 = sum(1 for e in root2.iter(NS + "g"))
    detail = "actual=" + str(actual) + (" == expected" if not bad else f" expected={expected} 不符={bad}")
    detail += f" | <g> 总数: 静态 {n_g1} -> 动画 {n_g2}（新增 {n_g2 - n_g1}）"
    detail += f" | 无 opacity:0 初始态: {'是' if not has_opacity0 else '否(发现!)'}"
    add("6. 结构计数（flowdot=22 / march=12 / breath=2）+ 无入场", (not bad) and (not has_opacity0), detail)
    return res


def main():
    src_text = open(SRC, encoding="utf-8").read()
    lines, header, title_idx, poly_idx, head_idx, blocks, order = parse_source(src_text)
    edges, gates = check_structure(blocks, order)

    # 实线边（文档序）-> 流光点参数（数值计算 L）
    solid = [b for b in edges if not blocks[b]["has_dash"]]
    if len(solid) != 22:
        raise SystemExit(f"[error] 实线边数量不符: {len(solid)} != 22")
    dot_params = []
    for i, bid in enumerate(solid):
        L = blocks[bid]["length"]
        GAP = L + DOT_GAP_EXTRA        # L + 80
        PK = L + DOT_TAIL              # L + 88（keyframes 起点）
        dur = PK / DOT_SPEED           # (L+88)/150 s
        delay = i * DOT_STAGGER        # i*0.13s
        dot_params.append((i + 1, L, GAP, PK, dur, delay))

    # 方向校验（实线边终点应指向箭头）
    dir_bad = verify_direction(blocks, order, edges)
    css_lines = build_css(dot_params)
    out_text = build(lines, header, title_idx, poly_idx, head_idx, blocks, order, edges, dot_params, css_lines)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(out_text)

    print(f"输出: {OUT}")
    print(f"规模: {len(src_text)} -> {len(out_text)} 字节（{out_text.count(chr(10))} 行）")
    print(f"无入场动画: 图直接静态呈现（无 rowIn/scale-in/scanSweep/shimmer/pulse/frameDrift, 无 opacity:0 初始态）")
    print(f"虚线边 dash march: {sum(1 for b in edges if blocks[b]['has_dash'])} 条, 周期 {DASH_PERIOD:.2f}s, 方向 源->目标(指向箭头)")
    print(f"实线边流光点: {len(solid)} 条 (统一 {DOT_SPEED:.0f}pt/s, GAP=L+{DOT_GAP_EXTRA:.0f}, 周期=(L+{DOT_TAIL+DOT_GAP_EXTRA:.0f})/150s, delay i*{DOT_STAGGER}s)")
    for (idx, L, GAP, PK, dur, delay) in dot_params:
        print(f"  pkt{idx:<2} L={L:8.2f}  GAP={GAP:8.2f}  PK={PK:8.2f}  周期={dur:7.3f}s  delay={delay:5.2f}s")
    print(f"门禁呼吸(仅 2): {', '.join(sorted(blocks[b]['name'] for b in gates))}, opacity 1<->0.55, {BREATH_PERIOD}s")
    print(f"\n光点方向校验: keyframes (L+88)->0 = dashoffset 递减 = 光点 起点(源)->终点(目标/箭头)")
    print(f"  实线边终点->箭头多边形距离 <= 6pt: {'ALL PASS' if not dir_bad else 'FAIL ' + str(dir_bad)}")

    print("\n=== 六项校验 ===")
    allok = True
    for name, ok, detail in validate(SRC, OUT):
        allok &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] {name} — {detail}")
    if dir_bad:
        allok = False
    print("\n结果: " + ("ALL PASS" if allok else "SOME FAILED"))
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()

# ymzhu 2026-11-04 15:54
