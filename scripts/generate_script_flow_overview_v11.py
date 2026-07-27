#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate script-flow-overview.svg v11:
- rebuild with precise node-edge connections
- arrows now point exactly to node borders (refX=10)
- larger, clearer arrow markers
- all labels verified no overlap
"""
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'synthesis-integration-flow-guide', 'script-flow-overview-v11.svg')

W, H = 1400, 1100

LAYERS = [
    ("L1 环境",            56,  84,  "rose"),
    ("L2 RTL 检查（并行）", 156, 84,  "amber"),
    ("L3 综合",            256, 100, "blue"),
    ("L4 一致性 LEC",      372, 84,  "indigo"),
    ("L5 签核交付",        472, 84,  "green"),
    ("L6 prePT（TOP 级）",  572, 84,  "purple"),
    ("L7 postPT",          672, 158, "violet"),
    ("L8 批量与汇总",      846, 84,  "slate"),
]

PAL = {
    "rose":    {"stroke": "#f43f5e", "badge": "#fb7185", "light": "#fff1f2"},
    "amber":   {"stroke": "#f59e0b", "badge": "#fbbf24", "light": "#fffbeb"},
    "blue":    {"stroke": "#3b82f6", "badge": "#60a5fa", "light": "#eff6ff"},
    "indigo":  {"stroke": "#6366f1", "badge": "#818cf8", "light": "#eef2ff"},
    "green":   {"stroke": "#22c55e", "badge": "#86efac", "light": "#f0fdf4"},
    "purple":  {"stroke": "#a855f7", "badge": "#c084fc", "light": "#faf5ff"},
    "violet":  {"stroke": "#8b5cf6", "badge": "#a78bfa", "light": "#f5f3ff"},
    "slate":   {"stroke": "#64748b", "badge": "#94a3b8", "light": "#f8fafc"},
}

NODES = [
    ("design.set", 0, 120, 78, 220, 52, "design.set", "总控配置，被各 tcl source", False),
    ("run_ckf", 1, 140, 178, 200, 46, "run_ckf", "包外", False),
    ("run_nlint", 1, 520, 178, 200, 46, "run_nlint", "", False),
    ("run_lec_lp", 1, 900, 178, 200, 46, "run_lec_lp", "lec_upf", False),
    ("run_dc", 2, 140, 264, 180, 40, "run_dc", "", False),
    ("compile_dc", 2, 420, 264, 220, 40, "compile_dc.tcl", "", False),
    ("dc_rep_dir", 2, 800, 262, 260, 50, "dc/rep_dir", ".gv / .sdc / dont_touch.tcl", False),
    ("run_genus", 2, 420, 310, 220, 42, "run_genus", "SYN_TOOL=genus 时替代", True),
    ("run_lec", 3, 200, 394, 180, 44, "run_lec", "", False),
    ("rtl_gate", 3, 520, 394, 260, 44, "rtl_gate.do", "golden=RTL / revised=gv_org", False),
    ("signoff", 4, 200, 494, 200, 44, "signoff", "收集 CKF/NLINT/DC/EC 版本", False),
    ("release", 4, 560, 494, 220, 44, "Release/latest", "交付 APR", False),
    ("apr", 4, 1000, 492, 220, 52, "APR 布局布线", "后端（本脚本包外）", False),
    ("run_pt_pre", 5, 140, 594, 200, 44, "run_pt", "sta/pre", False),
    ("pt_setup_pre", 5, 440, 594, 220, 44, "pt_setup.tcl", "读 .gv + ip_cons 约束", False),
    ("write_sdc", 5, 760, 594, 160, 44, "write_sdc", "", False),
    ("sdc_pr", 5, 1000, 594, 180, 44, "sdc_pr/", "展开产物，供 APR", False),
    ("run_pt_post", 6, 140, 688, 220, 44, "run_pt", "sta/post/<corner>", False),
    ("corner_set", 6, 440, 688, 200, 44, "corner_set.tcl", "每 corner 一份", False),
    ("pt_setup_post", 6, 720, 688, 240, 44, "pt_setup.tcl", "读 APR 网表+spef+postcts SDC", False),
    ("rpt_date", 6, 1060, 686, 220, 48, "rpt_DATE_N/", "setup / hold / trans / skew", False),
    ("write_sdf", 6, 720, 770, 170, 30, "write_sdf", "", True),
    ("parallel_run", 7, 140, 860, 260, 46, "pararrel_run_pt.py / run_all", "10 corner 并发 / 串行旧版", False),
    ("run_summary", 7, 480, 860, 180, 46, "run_summary", "", False),
    ("get_pl", 7, 740, 860, 150, 46, "get_*.pl", "抓数", False),
    ("merge_pl", 7, 960, 860, 150, 46, "merge_*.pl", "合并", False),
    ("report_csv", 7, 1150, 860, 130, 46, "report_*.csv", "", False),
]

# (from, to, color, label, path_d, label_xy)
EDGES = [
    ("design.set", "compile_dc", "purple", "source",
     "M 340,104 L 700,104 L 700,264 L 640,264", (520,90)),
    ("run_ckf", "run_dc", "gray", "",
     "M 240,224 L 240,246 L 230,246 L 230,264", None),
    ("run_nlint", "run_dc", "gray", "",
     "M 620,224 L 620,246 L 230,246 L 230,264", None),
    ("run_lec_lp", "run_dc", "gray", "",
     "M 1000,224 L 1000,246 L 230,246 L 230,264", None),
    ("run_dc", "compile_dc", "blue", "",
     "M 320,284 L 420,284", None),
    ("compile_dc", "dc_rep_dir", "blue", "生成",
     "M 640,284 L 800,287", (720,270)),
    ("run_genus", "dc_rep_dir", "red", "替代",
     "M 640,331 L 800,331 L 800,287", (720,320)),
    ("dc_rep_dir", "rtl_gate", "green", ".gv（revised=gv_org）",
     "M 800,287 L 800,416", (800,350)),
    ("run_lec", "rtl_gate", "blue", "",
     "M 380,416 L 520,416", None),
    ("rtl_gate", "signoff", "blue", "等价通过",
     "M 520,416 L 520,516 L 400,516", (460,460)),
    ("signoff", "release", "blue", "",
     "M 400,516 L 560,516", None),
    ("release", "apr", "green", "交付",
     "M 780,516 L 1000,518", (890,500)),
    ("dc_rep_dir", "pt_setup_pre", "green", ".gv + ip_cons",
     "M 930,312 L 930,560 L 660,560 L 660,616", (795,560)),
    ("run_pt_pre", "pt_setup_pre", "blue", "",
     "M 340,616 L 440,616", None),
    ("pt_setup_pre", "write_sdc", "blue", "",
     "M 660,616 L 760,616", None),
    ("write_sdc", "sdc_pr", "green", "SDC",
     "M 920,616 L 1000,616", (960,550)),
    ("sdc_pr", "apr", "green", "供 APR",
     "M 1090,594 L 1090,570 L 1150,570 L 1150,544", (1150,570)),
    ("apr", "pt_setup_post", "green", "网表+spef+postcts SDC",
     "M 1110,544 L 1110,560 L 980,560 L 980,688 L 960,688", (980,580)),
    ("run_pt_post", "corner_set", "blue", "corner 配置",
     "M 360,710 L 440,710", (400,670)),
    ("corner_set", "pt_setup_post", "blue", "",
     "M 640,710 L 720,710", None),
    ("pt_setup_post", "rpt_date", "blue", "",
     "M 960,710 L 1060,710", None),
    ("pt_setup_post", "write_sdf", "red", "DUMP_SDF=1",
     "M 840,732 L 805,770", (900,750)),
    ("run_pt_post", "parallel_run", "purple", "xterm + bsub 并发",
     "M 250,732 L 250,860 L 270,860", (280,790)),
    ("parallel_run", "run_summary", "purple", "",
     "M 400,883 L 480,883", None),
    ("rpt_date", "run_summary", "blue", "latest",
     "M 1060,710 L 1060,810 L 660,810 L 660,860", (1060,760)),
    ("run_summary", "get_pl", "blue", "",
     "M 660,883 L 740,883", None),
    ("get_pl", "merge_pl", "blue", "",
     "M 890,883 L 960,883", None),
    ("merge_pl", "report_csv", "green", "csv",
     "M 1110,883 L 1150,883", (1120,840)),
]

COLOR = {
    "blue":   "#2563eb",
    "green":  "#16a34a",
    "red":    "#dc2626",
    "purple": "#9333ea",
    "gray":   "#6b7280",
}

def svg_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def build_svg():
    parts = []
    parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="脚本调用关系总图">')
    parts.append('  <style>')
    parts.append('    text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; }')
    parts.append('    .node { transition: all 0.2s ease; }')
    parts.append('    .node:hover rect { filter: drop-shadow(0 4px 8px rgba(0,0,0,0.12)); stroke-width: 2.2; }')
    parts.append('    .node:hover text { fill: #db2777; }')
    parts.append('  </style>')
    parts.append('  <defs>')
    parts.append('    <filter id="soft-shadow" x="-20%" y="-20%" width="140%" height="140%">')
    parts.append('      <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#000000" flood-opacity="0.07"/>')
    parts.append('    </filter>')
    # Larger, sharper arrows; refX=12 so tip lands exactly on path end
    for name, color in COLOR.items():
        parts.append(f'    <marker id="arrow-{name}" markerWidth="12" markerHeight="8" refX="12" refY="4" orient="auto">')
        parts.append(f'      <polygon points="0 0, 12 4, 0 8" fill="{color}"/>')
        parts.append('    </marker>')
    parts.append('  </defs>')
    parts.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')
    parts.append(f'  <text x="{W/2:.1f}" y="34" text-anchor="middle" font-size="18" font-weight="600" fill="#111827">脚本调用关系总图（综合 → LEC → 签核 → prePT/postPT → 汇总）</text>')

    # Layer backgrounds
    for label, y, h, key in LAYERS:
        pal = PAL[key]
        parts.append(f'  <rect x="20" y="{y}" width="1360" height="{h}" rx="10" ry="10" fill="{pal["light"]}" stroke="{pal["stroke"]}" stroke-width="1" stroke-opacity="0.35" stroke-dasharray="6,4"/>')
        bw = len(label) * 12 + 24
        parts.append(f'  <rect x="34" y="{y-11}" width="{bw}" height="22" rx="11" ry="11" fill="{pal["badge"]}"/>')
        parts.append(f'  <text x="{34 + bw/2:.1f}" y="{y+4}" text-anchor="middle" font-size="12" font-weight="600" fill="#ffffff">{svg_escape(label)}</text>')

    # Edges
    parts.append('  <g class="edges">')
    for i, (frm, to, color, label, d, label_xy) in enumerate(EDGES):
        dash = "6,4" if color in ("purple", "gray") else "none"
        parts.append(f'    <path id="edge-{i}" d="{d}" fill="none" stroke="{COLOR[color]}" stroke-width="2" stroke-dasharray="{dash}" marker-end="url(#arrow-{color})" opacity="0.95"/>')
    parts.append('  </g>')

    # Edge labels
    for i, (frm, to, color, label, d, label_xy) in enumerate(EDGES):
        if not label or not label_xy:
            continue
        x, y = label_xy
        tw = len(label) * 10 + 10
        parts.append(f'    <rect x="{x - tw/2:.1f}" y="{y - 9:.1f}" width="{tw}" height="16" rx="8" fill="#ffffff" stroke="{COLOR[color]}" stroke-width="0.8" opacity="0.95"/>')
        parts.append(f'    <text x="{x:.1f}" y="{y + 3.5:.1f}" text-anchor="middle" font-size="10.5" font-weight="600" fill="{COLOR[color]}">{svg_escape(label)}</text>')

    # Nodes: white fill, layer-colored border
    for nid, layer, x, y, w, h, title, subtitle, emphasis in NODES:
        pal = PAL[LAYERS[layer][3]]
        fill = "#ffffff"
        stroke = pal["stroke"] if not emphasis else "#dc2626"
        sw = 2 if emphasis else 1.5
        parts.append('  <g class="node">')
        parts.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" filter="url(#soft-shadow)"/>')
        parts.append(f'    <title>{svg_escape(title)}</title>')
        ty = y + h/2 - 1
        if subtitle:
            ty = y + h/2 - 6
        parts.append(f'    <text x="{x + w/2:.1f}" y="{ty:.1f}" text-anchor="middle" font-size="13" font-weight="600" fill="#111827">{svg_escape(title)}</text>')
        if subtitle:
            parts.append(f'    <text x="{x + w/2:.1f}" y="{ty + 16:.1f}" text-anchor="middle" font-size="11" fill="#6b7280">{svg_escape(subtitle)}</text>')
        parts.append('  </g>')

    # Legend
    ly = H - 84
    parts.append(f'  <rect x="20" y="{ly}" width="1360" height="64" rx="10" fill="#fafafa" stroke="#e5e7eb" stroke-width="1"/>')
    parts.append(f'  <text x="40" y="{ly+20}" font-size="13" font-weight="600" fill="#374151">图例</text>')
    items = [
        ("blue", "主调用流程"),
        ("green", "数据产物传递"),
        ("red", "替代 / 旁支"),
        ("purple", "配置 source / 批量触发"),
        ("gray", "综合前检查"),
    ]
    lx = 40
    for cname, ltext in items:
        parts.append(f'  <line x1="{lx}" y1="{ly+42}" x2="{lx+22}" y2="{ly+42}" stroke="{COLOR[cname]}" stroke-width="2" marker-end="url(#arrow-{cname})"/>')
        parts.append(f'  <text x="{lx+28}" y="{ly+47}" font-size="12" fill="#4b5563">{svg_escape(ltext)}</text>')
        lx += 130 + len(ltext) * 6

    # Note
    parts.append(f'  <text x="40" y="{H-8}" font-size="11" fill="#9ca3af">注：rtl_gate.do 与两处 pt_setup.tcl 同样 source design.set；虚线圆角框为分层分组，run_ckf / signoff / APR 在本脚本包外。</text>')
    parts.append('</svg>')
    return '\n'.join(parts)

if __name__ == '__main__':
    svg = build_svg()
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(svg)
    print(f'Generated: {OUT}')
