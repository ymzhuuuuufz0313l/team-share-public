# 生成「脚本调用关系总图」SVG（style-1 flat icon，贴近站点粉色 accent）
# 用法（在站点根目录下）: script/.venv/Scripts/python.exe image/tools/_gen_flow_svg.py
# 2026-11-04 自 script/ 迁入 image/tools/：'..' 相对 __file__ 现解析到 image/script-flow-overview.svg（静态主名位，事实源）
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'script-flow-overview.svg')

W, H = 1280, 972
C = {
    'text': '#111827', 'sub': '#6b7280', 'box_stroke': '#d1d5db',
    'blue': '#2563eb', 'green': '#16a34a', 'red': '#dc2626',
    'purple': '#9333ea', 'gray': '#6b7280', 'pink': '#db2777',
    'pink_soft': '#fce7f3', 'blue_tint': '#eff6ff', 'green_tint': '#f0fdf4',
    'purple_tint': '#faf5ff', 'orange_tint': '#fff7ed',
}
FONT = "'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei', 'Microsoft JhengHei', 'SimHei', sans-serif"

lines = []
A = lines.append

A(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">')
A('  <style>')
A(f'    text {{ font-family: {FONT}; }}')
A('  </style>')
A('  <defs>')
for name, color in [('arrow-blue', C['blue']), ('arrow-green', C['green']),
                    ('arrow-red', C['red']), ('arrow-purple', C['purple']),
                    ('arrow-gray', C['gray'])]:
    A(f'    <marker id="{name}" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">')
    A(f'      <polygon points="0 0, 10 3.5, 0 7" fill="{color}"/>')
    A('    </marker>')
A('  </defs>')
A(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')

# 标题
A(f'  <text x="{W//2}" y="34" text-anchor="middle" font-size="18" font-weight="600" fill="{C["text"]}">脚本调用关系总图（综合 → LEC → 签核 → prePT/postPT → 汇总）</text>')

# ---------- 层容器 ----------
layers = [
    ('L1 环境', 56, 84),
    ('L2 RTL 检查（并行）', 156, 84),
    ('L3 综合', 256, 100),
    ('L4 一致性 LEC', 372, 84),
    ('L5 签核交付', 472, 84),
    ('L6 prePT（TOP 级）', 572, 84),
    ('L7 postPT', 672, 100),
    ('L8 批量与汇总', 788, 84),
]
for label, y, h in layers:
    A(f'  <rect x="20" y="{y}" width="1240" height="{h}" rx="10" ry="10" fill="none" stroke="{C["box_stroke"]}" stroke-width="1.2" stroke-dasharray="6,4"/>')
    lw = 14 + len(label) * 13
    A(f'  <rect x="34" y="{y - 11}" width="{lw}" height="22" rx="11" ry="11" fill="{C["pink"]}"/>')
    A(f'  <text x="{34 + lw//2}" y="{y + 4}" text-anchor="middle" font-size="12" font-weight="600" fill="#ffffff">{label}</text>')

# ---------- 节点 ----------
def node(x, y, w, h, title, sub=None, fill='#ffffff', stroke=None, title_size=13):
    stroke = stroke or C['box_stroke']
    A(f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
    cx = x + w // 2
    if sub:
        A(f'  <text x="{cx}" y="{y + h//2 - 2}" text-anchor="middle" font-size="{title_size}" font-weight="600" fill="{C["text"]}">{title}</text>')
        A(f'  <text x="{cx}" y="{y + h//2 + 15}" text-anchor="middle" font-size="11" fill="{C["sub"]}">{sub}</text>')
    else:
        A(f'  <text x="{cx}" y="{y + h//2 + 5}" text-anchor="middle" font-size="{title_size}" font-weight="600" fill="{C["text"]}">{title}</text>')

# L1
node(120, 78, 220, 52, 'design.set', '总控配置，被各 tcl source', fill=C['pink_soft'], stroke=C['pink'])
# L2
node(140, 178, 200, 46, 'run_ckf', '包外', fill=C['orange_tint'])
node(480, 178, 200, 46, 'run_nlint', fill=C['orange_tint'])
node(820, 178, 200, 46, 'run_lec_lp', 'lec_upf', fill=C['orange_tint'])
# L3
node(140, 264, 180, 40, 'run_dc', fill=C['blue_tint'])
node(420, 264, 220, 40, 'compile_dc.tcl', fill=C['blue_tint'])
node(780, 262, 260, 50, 'dc/rep_dir', '.gv / .sdc / dont_touch.tcl', fill=C['blue_tint'])
node(420, 310, 220, 42, 'run_genus', 'SYN_TOOL=genus 时替代', fill='#ffffff', stroke=C['red'])
# L4
node(200, 394, 180, 44, 'run_lec', fill=C['blue_tint'])
node(520, 394, 260, 44, 'rtl_gate.do', 'golden=RTL / revised=gv_org', fill=C['blue_tint'])
# L5
node(200, 494, 200, 44, 'signoff', '收集 CKF/NLINT/DC/EC 版本', fill=C['blue_tint'])
node(560, 494, 220, 44, 'Release/latest', '交付 APR', fill=C['green_tint'])
# APR（后端，外部）
node(980, 492, 220, 52, 'APR 布局布线', '后端（本脚本包外）', fill=C['orange_tint'])
# L6
node(140, 594, 200, 44, 'run_pt', 'sta/pre', fill=C['purple_tint'])
node(440, 594, 220, 44, 'pt_setup.tcl', '读 .gv + ip_cons 约束', fill=C['purple_tint'])
node(760, 594, 160, 44, 'write_sdc', fill=C['purple_tint'])
node(980, 594, 180, 44, 'sdc_pr/', '展开产物，供 APR', fill=C['green_tint'])
# L7
node(140, 688, 220, 44, 'run_pt', 'sta/post/&lt;corner&gt;', fill=C['purple_tint'])
node(440, 688, 200, 44, 'corner_set.tcl', fill=C['purple_tint'])
node(720, 688, 240, 44, 'pt_setup.tcl', '读 APR 网表+spef+postcts SDC', fill=C['purple_tint'])
node(1040, 686, 200, 48, 'rpt_DATE_N/', 'setup / hold / trans / skew', fill=C['green_tint'])
node(720, 738, 170, 30, 'write_sdf', None, fill='#ffffff', stroke=C['red'])
# L8
node(140, 810, 260, 46, 'pararrel_run_pt.py / run_all', '10 corner 并发 / 串行旧版', fill=C['purple_tint'])
node(480, 810, 180, 46, 'run_summary', fill=C['blue_tint'])
node(740, 810, 150, 46, 'get_*.pl', '抓数', fill=C['blue_tint'])
node(940, 810, 150, 46, 'merge_*.pl', '合并', fill=C['blue_tint'])
node(1130, 810, 130, 46, 'report_*.csv', None, fill=C['green_tint'])

# ---------- 箭头 ----------
def path(d, color, marker, dash=None, width=1.5):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    A(f'  <path d="{d}" fill="none" stroke="{color}" stroke-width="{width}"{dash_attr} marker-end="url(#{marker})"/>')

def label(x, y, text, color=None, anchor='middle', size=11):
    color = color or C['sub']
    A(f'  <text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" fill="{color}">{text}</text>')

# L2 三项检查 → run_dc（灰色虚线，汇入总线后单箭头）
for cx in (240, 580, 920):
    A(f'  <path d="M {cx},224 L {cx},246 L 230,246" fill="none" stroke="{C["gray"]}" stroke-width="1.5" stroke-dasharray="5,3"/>')
path('M 230,246 L 230,260', C['gray'], 'arrow-gray', dash='5,3')
label(600, 242, '综合前检查通过', C['gray'])

# design.set → compile_dc.tcl（紫色虚线，x=460 走廊下穿，跨越灰色检查总线处用跳线弧）
path('M 340,104 L 460,104 L 460,238 A 6,6 0 0 1 460,250 L 460,260', C['purple'], 'arrow-purple', dash='6,4')
label(452, 190, 'source', C['purple'], anchor='end')

# L3 主流
path('M 320,284 L 416,284', C['blue'], 'arrow-blue')
path('M 640,284 L 776,284', C['blue'], 'arrow-blue')
label(708, 276, '生成', C['blue'])
# run_genus 旁支 → dc/rep_dir
path('M 640,331 L 900,331 L 900,316', C['red'], 'arrow-red')

# dc/rep_dir → rtl_gate.do（.gv）
path('M 910,312 L 910,366 L 650,366 L 650,390', C['green'], 'arrow-green')
label(790, 360, '.gv（revised=gv_org）', C['green'])

# L4
path('M 380,416 L 516,416', C['blue'], 'arrow-blue')

# rtl_gate.do → signoff
path('M 650,438 L 650,464 L 300,464 L 300,490', C['blue'], 'arrow-blue')
label(480, 458, '等价通过', C['blue'])

# L5
path('M 400,516 L 556,516', C['blue'], 'arrow-blue')
path('M 780,516 L 976,524', C['green'], 'arrow-green')
label(880, 510, '交付', C['green'])

# dc/rep_dir → pt_setup.tcl(pre)（.gv + ip_cons，右侧数据轨，从 L6 节点上方走廊进入顶部；跨越 sdc_pr→APR 箭头处用跳线弧）
path('M 1040,287 L 1244,287 L 1244,580 L 1098,580 A 6,6 0 0 0 1082,580 L 550,580 L 550,590', C['green'], 'arrow-green')
label(1236, 450, '.gv + ip_cons', C['green'], anchor='end')

# L6 主流
path('M 340,616 L 436,616', C['blue'], 'arrow-blue')
path('M 660,616 L 756,616', C['blue'], 'arrow-blue')
path('M 920,616 L 976,616', C['green'], 'arrow-green')
label(948, 608, 'SDC', C['green'])

# sdc_pr/ → APR
path('M 1090,594 L 1090,548', C['green'], 'arrow-green')
label(1118, 570, '供 APR', C['green'], anchor='start')

# APR → pt_setup.tcl(post)（网表+spef+postcts SDC，下方绕行进入顶部）
path('M 1150,544 L 1150,664 L 840,664 L 840,684', C['green'], 'arrow-green')
label(995, 658, '网表 + spef + postcts SDC', C['green'])

# L7 主流
path('M 360,710 L 436,710', C['blue'], 'arrow-blue')
path('M 640,710 L 716,710', C['blue'], 'arrow-blue')
label(678, 702, 'corner 配置', C['blue'])
path('M 960,710 L 1036,710', C['blue'], 'arrow-blue')

# DUMP_SDF 分支 → write_sdf
path('M 540,732 L 540,753 L 716,753', C['red'], 'arrow-red', dash='6,4')
label(620, 746, 'DUMP_SDF=1', C['red'])

# 批量 → run_pt(post)
path('M 270,810 L 270,736', C['purple'], 'arrow-purple', dash='6,4')
label(284, 776, 'xterm + bsub 并发', C['purple'], anchor='start')

# rpt_DATE_N → run_summary（latest）
path('M 1140,734 L 1140,780 L 570,780 L 570,806', C['blue'], 'arrow-blue')
label(1000, 774, 'latest', C['blue'])

# L8 汇总链
path('M 660,833 L 736,833', C['blue'], 'arrow-blue')
path('M 890,833 L 936,833', C['blue'], 'arrow-blue')
path('M 1090,833 L 1126,833', C['green'], 'arrow-green')
label(1108, 825, 'csv', C['green'], anchor='middle')

# ---------- 图例 ----------
ly = 896
A(f'  <rect x="20" y="{ly - 14}" width="1240" height="62" rx="10" ry="10" fill="#fafafa" stroke="{C["box_stroke"]}" stroke-width="1"/>')
legend = [
    (C['blue'], None, '主调用流程'),
    (C['green'], None, '数据产物传递'),
    (C['red'], None, '替代 / 旁支'),
    (C['purple'], '6,4', '配置 source / 批量触发'),
    (C['gray'], '5,3', '综合前检查'),
]
lx = 60
for color, dash, text in legend:
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
    marker = {'#2563eb': 'arrow-blue', '#16a34a': 'arrow-green', '#dc2626': 'arrow-red',
              '#9333ea': 'arrow-purple', '#6b7280': 'arrow-gray'}[color]
    A(f'  <line x1="{lx}" y1="{ly + 10}" x2="{lx + 34}" y2="{ly + 10}" stroke="{color}" stroke-width="1.5"{dash_attr} marker-end="url(#{marker})"/>')
    A(f'  <text x="{lx + 42}" y="{ly + 14}" font-size="12" fill="{C["sub"]}">{text}</text>')
    lx += 42 + len(text) * 13 + 40
A(f'  <text x="60" y="{ly + 38}" font-size="11" fill="{C["sub"]}">注：rtl_gate.do 与两处 pt_setup.tcl 同样 source design.set；虚线圆角框为分层分组，run_ckf / signoff / APR 在本脚本包外。</text>')

A('</svg>')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('SVG written:', os.path.normpath(OUT))

# ymzhu 2026-11-04 15:54
