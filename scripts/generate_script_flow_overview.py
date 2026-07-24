#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate script-flow-overview.svg with polished visual hierarchy.
Run: python generate_script_flow_overview.py
"""
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'synthesis-integration-flow-guide', 'script-flow-overview.svg')

# Canvas
W, H = 1320, 1020

# Layer groups: (label, y, height, color_key)
LAYERS = [
    ("L1 环境",            56,  84,  "rose"),
    ("L2 RTL 检查（并行）", 156, 84,  "amber"),
    ("L3 综合",            256, 100, "blue"),
    ("L4 一致性 LEC",      372, 84,  "indigo"),
    ("L5 签核交付",        472, 84,  "green"),
    ("L6 prePT（TOP 级）",  572, 84,  "purple"),
    ("L7 postPT",          672, 100, "violet"),
    ("L8 批量与汇总",      788, 84,  "slate"),
]

COLOR_PALETTE = {
    "rose":    {"bg": "#fff1f2", "stroke": "#f43f5e", "text": "#881337", "badge": "#fb7185"},
    "amber":   {"bg": "#fffbeb", "stroke": "#f59e0b", "text": "#78350f", "badge": "#fbbf24"},
    "blue":    {"bg": "#eff6ff", "stroke": "#3b82f6", "text": "#1e3a8a", "badge": "#60a5fa"},
    "indigo":  {"bg": "#eef2ff", "stroke": "#6366f1", "text": "#312e81", "badge": "#818cf8"},
    "green":   {"bg": "#f0fdf4", "stroke": "#22c55e", "text": "#14532d", "badge": "#86efac"},
    "purple":  {"bg": "#faf5ff", "stroke": "#a855f7", "text": "#581c87", "badge": "#c084fc"},
    "violet":  {"bg": "#f5f3ff", "stroke": "#8b5cf6", "text": "#4c1d95", "badge": "#a78bfa"},
    "slate":   {"bg": "#f8fafc", "stroke": "#64748b", "text": "#0f172a", "badge": "#94a3b8"},
}

# Nodes: id, layer index, x, y, width, height, title, subtitle, emphasis bool
NODES = [
    # L1
    ("design.set", 0, 160, 78, 220, 52, "design.set", "总控配置，被各 tcl source", False),
    # L2
    ("run_ckf", 1, 160, 178, 180, 46, "run_ckf", "包外", False),
    ("run_nlint", 1, 500, 178, 200, 46, "run_nlint", "", False),
    ("run_lec_lp", 1, 860, 178, 200, 46, "run_lec_lp", "lec_upf", False),
    # L3
    ("run_dc", 2, 160, 264, 180, 40, "run_dc", "", False),
    ("compile_dc", 2, 440, 264, 220, 40, "compile_dc.tcl", "", False),
    ("dc_rep_dir", 2, 800, 262, 280, 50, "dc/rep_dir", ".gv / .sdc / dont_touch.tcl", False),
    ("run_genus", 2, 440, 314, 220, 42, "run_genus", "SYN_TOOL=genus 时替代", True),
    # L4
    ("run_lec", 3, 220, 394, 180, 44, "run_lec", "", False),
    ("rtl_gate", 3, 540, 394, 260, 44, "rtl_gate.do", "golden=RTL / revised=gv_org", False),
    # L5
    ("signoff", 4, 220, 494, 200, 44, "signoff", "收集 CKF/NLINT/DC/EC 版本", False),
    ("release", 4, 560, 494, 220, 44, "Release/latest", "交付 APR", False),
    ("apr", 4, 980, 492, 240, 52, "APR 布局布线", "后端（本脚本包外）", False),
    # L6
    ("run_pt_pre", 5, 160, 594, 200, 44, "run_pt", "sta/pre", False),
    ("pt_setup_pre", 5, 460, 594, 220, 44, "pt_setup.tcl", "读 .gv + ip_cons 约束", False),
    ("write_sdc", 5, 780, 594, 160, 44, "write_sdc", "", False),
    ("sdc_pr", 5, 1000, 594, 180, 44, "sdc_pr/", "展开产物，供 APR", False),
    # L7
    ("run_pt_post", 6, 160, 688, 220, 44, "run_pt", "sta/post/<corner>", False),
    ("corner_set", 6, 440, 688, 200, 44, "corner_set.tcl", "每 corner 一份", False),
    ("pt_setup_post", 6, 720, 688, 240, 44, "pt_setup.tcl", "读 APR 网表+spef+postcts SDC", False),
    ("rpt_date", 6, 1040, 686, 220, 48, "rpt_DATE_N/", "setup / hold / trans / skew", False),
    ("write_sdf", 6, 720, 742, 170, 34, "write_sdf", "", True),
    # L8
    ("parallel_run", 7, 160, 810, 280, 46, "pararrel_run_pt.py / run_all", "10 corner 并发 / 串行旧版", False),
    ("run_summary", 7, 500, 810, 180, 46, "run_summary", "", False),
    ("get_pl", 7, 760, 810, 150, 46, "get_*.pl", "抓数", False),
    ("merge_pl", 7, 960, 810, 150, 46, "merge_*.pl", "合并", False),
    ("report_csv", 7, 1150, 810, 130, 46, "report_*.csv", "", False),
]



# Edges: (from_id, to_id, color, label, style)
# color: blue=main, green=data, red=alt, purple=source, gray=check
EDGES = [
    # L1 -> L3 (source design.set)
    ("design.set", "run_dc", "purple", "source", "dashed"),
    ("design.set", "compile_dc", "purple", "", "dashed"),
    ("design.set", "run_genus", "purple", "", "dashed"),
    ("design.set", "run_pt_pre", "purple", "source", "dashed"),
    ("design.set", "pt_setup_pre", "purple", "", "dashed"),
    ("design.set", "pt_setup_post", "purple", "", "dashed"),
    ("design.set", "rtl_gate", "purple", "", "dashed"),
    ("design.set", "run_lec", "purple", "", "dashed"),
    # L2 checks -> L3
    ("run_ckf", "run_dc", "gray", "", "dashed"),
    ("run_nlint", "run_dc", "gray", "", "dashed"),
    ("run_lec_lp", "run_dc", "gray", "", "dashed"),
    # L3
    ("run_dc", "compile_dc", "blue", "", "solid"),
    ("compile_dc", "dc_rep_dir", "blue", "生成", "solid"),
    ("run_genus", "dc_rep_dir", "red", "替代", "solid"),
    ("dc_rep_dir", "rtl_gate", "green", ".gv（revised=gv_org）", "solid"),
    # L4
    ("run_lec", "rtl_gate", "blue", "", "solid"),
    ("rtl_gate", "signoff", "blue", "等价通过", "solid"),
    # L5
    ("signoff", "release", "blue", "", "solid"),
    ("release", "apr", "green", "交付", "solid"),
    ("dc_rep_dir", "pt_setup_pre", "green", ".gv + ip_cons", "solid"),
    # L6
    ("run_pt_pre", "pt_setup_pre", "blue", "", "solid"),
    ("pt_setup_pre", "write_sdc", "blue", "", "solid"),
    ("write_sdc", "sdc_pr", "green", "SDC", "solid"),
    ("sdc_pr", "apr", "green", "供 APR", "solid"),
    # L7
    ("apr", "pt_setup_post", "green", "网表+spef+postcts SDC", "solid"),
    ("run_pt_post", "corner_set", "blue", "corner 配置", "solid"),
    ("corner_set", "pt_setup_post", "blue", "", "solid"),
    ("pt_setup_post", "rpt_date", "blue", "", "solid"),
    ("pt_setup_post", "write_sdf", "red", "DUMP_SDF=1", "dashed"),
    # L8
    ("run_pt_post", "parallel_run", "purple", "xterm + bsub 并发", "dashed"),
    ("rpt_date", "run_summary", "blue", "latest", "solid"),
    ("run_summary", "get_pl", "blue", "", "solid"),
    ("get_pl", "merge_pl", "blue", "", "solid"),
    ("merge_pl", "report_csv", "green", "csv", "solid"),
]

COLOR = {
    "blue":   "#2563eb",
    "green":  "#16a34a",
    "red":    "#dc2626",
    "purple": "#9333ea",
    "gray":   "#6b7280",
}

LIGHT = {
    "blue":   "#dbeafe",
    "green":  "#dcfce7",
    "red":    "#fee2e2",
    "purple": "#f3e8ff",
    "gray":   "#f3f4f6",
}

def node_center(nid):
    for n in NODES:
        if n[0] == nid:
            _, _, x, y, w, h, _, _, _ = n
            return (x + w/2, y + h/2)
    raise ValueError(nid)

def node_rect(nid):
    for n in NODES:
        if n[0] == nid:
            _, _, x, y, w, h, _, _, _ = n
            return (x, y, w, h)
    raise ValueError(nid)

def make_edge_path(x1, y1, x2, y2, style, start_node, end_node):
    """Create smooth paths avoiding right-angle corners."""
    # Determine entry/exit points
    sx, sy, sw, sh = node_rect(start_node)
    ex, ey, ew, eh = node_rect(end_node)
    
    # Choose start side: prefer right, else left, else bottom/top
    if x2 > x1 + sw/2 + ew/2:
        x1_out = sx + sw
        y1_out = y1
    elif x2 < x1 - sw/2 - ew/2:
        x1_out = sx
        y1_out = y1
    else:
        x1_out = x1
        if y2 > y1:
            y1_out = sy + sh
        else:
            y1_out = sy
    
    # Choose end side
    if x2 > x1:
        x2_in = ex
        y2_in = y2
    elif x2 < x1:
        x2_in = ex + ew
        y2_in = y2
    else:
        x2_in = x2
        if y2 > y1:
            y2_in = ey
        else:
            y2_in = ey + eh
    
    # Build path with bezier curves
    if abs(x2_in - x1_out) < 30:
        # mostly vertical
        d = f"M {x1_out:.1f} {y1_out:.1f} L {x2_in:.1f} {y2_in:.1f}"
    elif abs(y2_in - y1_out) < 30:
        # mostly horizontal
        d = f"M {x1_out:.1f} {y1_out:.1f} L {x2_in:.1f} {y2_in:.1f}"
    else:
        # curved: horizontal then vertical
        mid_x = (x1_out + x2_in) / 2
        d = f"M {x1_out:.1f} {y1_out:.1f} C {mid_x:.1f} {y1_out:.1f}, {mid_x:.1f} {y2_in:.1f}, {x2_in:.1f} {y2_in:.1f}"
    return d

def svg_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def build_svg():
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="脚本调用关系总图">')
    parts.append('  <style>')
    parts.append('    text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }')
    parts.append('    .node { transition: all 0.2s ease; cursor: pointer; }')
    parts.append('    .node:hover rect { filter: drop-shadow(0 6px 12px rgba(0,0,0,0.12)); stroke-width: 2.5; }')
    parts.append('    .node:hover text { fill: #db2777; }')
    parts.append('    .edge { transition: stroke-width 0.2s; }')
    parts.append('    .edge:hover { stroke-width: 3; }')
    parts.append('  </style>')
    parts.append('  <defs>')
    # shadow filter
    parts.append('    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">')
    parts.append('      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.08"/>')
    parts.append('    </filter>')
    # arrow markers
    for name, color in COLOR.items():
        parts.append(f'    <marker id="arrow-{name}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
        parts.append(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
        parts.append('    </marker>')
    parts.append('  </defs>')
    
    # Background
    parts.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')
    
    # Title
    parts.append(f'  <text x="{W/2:.1f}" y="36" text-anchor="middle" font-size="20" font-weight="700" fill="#111827">脚本调用关系总图</text>')
    parts.append(f'  <text x="{W/2:.1f}" y="58" text-anchor="middle" font-size="13" fill="#6b7280">综合 → LEC → 签核 → prePT → postPT → 汇总</text>')
    
    # Layer backgrounds
    for label, y, h, key in LAYERS:
        pal = COLOR_PALETTE[key]
        # dashed rounded rectangle
        parts.append(f'  <rect x="24" y="{y}" width="{W-48}" height="{h}" rx="12" ry="12" fill="{pal["bg"]}" stroke="{pal["stroke"]}" stroke-width="1" stroke-opacity="0.35" stroke-dasharray="6,4"/>')
        # badge
        bw = len(label) * 12 + 24
        parts.append(f'  <rect x="40" y="{y-11}" width="{bw}" height="24" rx="12" ry="12" fill="{pal["badge"]}"/>')
        parts.append(f'  <text x="{40 + bw/2:.1f}" y="{y+6}" text-anchor="middle" font-size="12" font-weight="700" fill="#ffffff">{svg_escape(label)}</text>')
    
    # Edges first (behind nodes)
    parts.append('  <g class="edges">')
    for i, (frm, to, color, label, style) in enumerate(EDGES):
        x1, y1 = node_center(frm)
        x2, y2 = node_center(to)
        d = make_edge_path(x1, y1, x2, y2, style, frm, to)
        stroke_dash = "6,4" if style == "dashed" else "5,3" if color == "gray" else "none"
        parts.append(f'    <path id="edge-{i}" class="edge" d="{d}" fill="none" stroke="{COLOR[color]}" stroke-width="2" stroke-dasharray="{stroke_dash}" marker-end="url(#arrow-{color})" opacity="0.9"/>')
    parts.append('  </g>')
    
    # Edge labels
    for i, (frm, to, color, label, style) in enumerate(EDGES):
        if not label:
            continue
        x1, y1 = node_center(frm)
        x2, y2 = node_center(to)
        # place label at midpoint, slightly offset
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # simple offset based on direction
        if abs(x2 - x1) > abs(y2 - y1):
            my -= 12
        else:
            mx += 10
        # white background pill for readability
        tw = len(label) * 10 + 12
        parts.append(f'    <rect x="{mx - tw/2:.1f}" y="{my - 10:.1f}" width="{tw}" height="18" rx="9" fill="{LIGHT[color]}" stroke="{COLOR[color]}" stroke-width="0.5" opacity="0.95"/>')
        parts.append(f'    <text x="{mx:.1f}" y="{my + 4:.1f}" text-anchor="middle" font-size="11" font-weight="600" fill="{COLOR[color]}">{svg_escape(label)}</text>')
    
    # Nodes
    for nid, layer, x, y, w, h, title, subtitle, emphasis in NODES:
        pal = COLOR_PALETTE[LAYERS[layer][3]]
        fill = "#ffffff" if emphasis else pal["bg"]
        stroke = pal["stroke"] if not emphasis else COLOR["red"]
        stroke_width = 2 if emphasis else 1.5
        
        parts.append('  <g class="node">')
        parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" ry="10" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" filter="url(#shadow)"/>')
        parts.append(f'    <title>{svg_escape(title)}</title>')
        # title
        ty = y + h/2 - 2
        if subtitle:
            ty = y + h/2 - 6
        parts.append(f'    <text x="{x + w/2:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="13" font-weight="700" fill="{pal["text"]}">{svg_escape(title)}</text>')
        if subtitle:
            parts.append(f'    <text x="{x + w/2:.1f}" y="{ty + 17:.1f}" text-anchor="middle" font-size="11" fill="#6b7280">{svg_escape(subtitle)}</text>')
        parts.append('  </g>')
    
    # Legend
    ly = H - 92
    parts.append(f'  <rect x="40" y="{ly}" width="{W-80}" height="72" rx="12" fill="#fafafa" stroke="#e5e7eb" stroke-width="1"/>')
    parts.append(f'  <text x="60" y="{ly+22}" font-size="13" font-weight="700" fill="#374151">图例</text>')
    legend_items = [
        ("blue", "主调用流程"),
        ("green", "数据产物传递"),
        ("red", "替代 / 旁支"),
        ("purple", "配置 source / 批量触发"),
        ("gray", "综合前检查"),
    ]
    lx = 60
    for cname, ltext in legend_items:
        parts.append(f'  <line x1="{lx}" y1="{ly+45}" x2="{lx+24}" y2="{ly+45}" stroke="{COLOR[cname]}" stroke-width="2" marker-end="url(#arrow-{cname})"/>')
        parts.append(f'  <text x="{lx+30}" y="{ly+50}" font-size="12" fill="#4b5563">{svg_escape(ltext)}</text>')
        lx += 130 + len(ltext) * 6
    
    # Note
    parts.append(f'  <text x="40" y="{H-16}" font-size="11" fill="#9ca3af">注：rtl_gate.do 与两处 pt_setup.tcl 同样 source design.set；虚线圆角框为分层分组，run_ckf / signoff / APR 在本脚本包外。</text>')
    
    parts.append('</svg>')
    return '\n'.join(parts)

if __name__ == '__main__':
    svg = build_svg()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'Generated: {OUT}')
