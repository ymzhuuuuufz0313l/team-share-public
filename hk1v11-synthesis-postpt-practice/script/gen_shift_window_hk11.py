# -*- coding: utf-8 -*-
# gen_shift_window_hk11.py — ch09 §6.3 时钟偏移容限图（1104V0）
# v3 2026-11-04：修红线标签硬编码残值（上代 −1.09388/+0.40129，与本代线位不符）→
#   全部数值改 phy csv 直算（参照 docs/to_signoff_1104v2/gen_signoff_1104v2.py 做法），去除硬编码：
#   数据通道（零手工）：port→FF setup = phy csv rx0_00_max 行，port→FF hold = rx0_00_min 行
#   （1104 代际 input port 即头名，ch09 §6.3 口径）；左移容限 = max+0.3+0.4(=+0.7)；右移容限 = min+0.3+0.15(=+0.45)。
# v2 2026-10-30：修 6 处重叠（数据窗压轴 / ns 标注溢出 / 箭头三层文字过密 /
#   红线标签穿 Panel B 条形 / 右移公式穿红线 / 红线无箭头 marker），补 <defs>
# 站点色板（practice :root）：纸 #f4f1ea / 墨 #1c2534 / 琥珀 #b45309 / 深青 #0e7490
#   绿 #047857 / 红 #b91c1c / 蓝 #1d4ed8 / 面 #fffdf7 / 线 #c9bfa8 / 网格 #ddd6c8
# 数据源（零手工）：1104V0 本地 SYNTHESIS 包 report_phy_busskew.csv（rx0_00_max/min 两行）
import csv, io, os

SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_STATIC = os.path.join(SITE, "images", "56_signoff_shift_window_hk11.svg")
PHY_CSV = r"E:\project\HK1V11\SYNTHESIS\top\sta\post\pt\summary\latest\report_phy_busskew.csv"

C_BG, C_PANEL, C_BORDER = "#f4f1ea", "#fffdf7", "#c9bfa8"
C_TEXT, C_MUTED, C_GRID = "#1c2534", "#5b6675", "#ddd6c8"
C_AMBER, C_TEAL, C_GREEN, C_RED, C_BLUE = "#b45309", "#0e7490", "#047857", "#b91c1c", "#1d4ed8"

def read_phy_shift(path):
    """phy csv -> 每 corner (name, lft=rx0_00_max+0.7, rgt=rx0_00_min+0.45, mx, mn) + 全角最小者；csv 列序输出。"""
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    hdr = rows[0][1:11]
    get = lambda rn: [float(r[1:11][i]) for i in range(10) for r in [next(x for x in rows[1:] if x[0] == rn)]]
    mx = get("report_timing_rx0_00_max.rpt")
    mn = get("report_timing_rx0_00_min.rpt")
    corners = []
    for i, c in enumerate(hdr):
        corners.append((c.replace("_125", "").replace("_m40", "").replace("_25", ""),
                        mx[i] + 0.7, mn[i] + 0.45, mx[i], mn[i]))
    li = min(range(10), key=lambda i: corners[i][1])
    ri = min(range(10), key=lambda i: corners[i][2])
    return corners, corners[li], corners[ri], hdr

# ---------- 数据直算（零手工）----------
corners, lmin, rmin, _hdr = read_phy_shift(PHY_CSV)
LFT, RGT = -lmin[1], rmin[2]   # 全角最小左移（负线位）/ 右移（正线位）

L = []
a = L.append
W, H = 1440, 900
a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
a('<style>text{font-family:"Microsoft YaHei","Noto Sans SC",monospace;fill:%s}.mono{font-family:Consolas,"Microsoft YaHei",monospace}</style>' % C_TEXT)
a('<defs>'
  '<marker id="mB" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
  '<path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker>'
  '</defs>' % C_BLUE)
a('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C_BG))
a('<text x="14" y="34" font-size="11" fill="%s" class="mono">HK1V11 · SIGNOFF · CLOCK SHIFT WINDOW · 1104V0 · 10 CORNER</text>' % C_AMBER)
a('<text x="14" y="66" font-size="22" font-weight="bold"><tspan fill="%s">时钟偏移容限</tspan> — 采样时钟相对数据可左移 / 右移多少</text>' % C_AMBER)

# ---------- Panel A: 时间轴窗 ----------
# 布局（自上而下）：标题 118 / 红线顶 150 / 箭头粗标 174 / 箭头线 190 /
#   箭头公式 214 / 角点注 234 / 数据窗 248-292 / 轴 310 / 刻度字 336 /
#   红线底标+ns 单位 358 / 公式框 372-492（面板底 520）
a('<rect x="40" y="90" width="1360" height="430" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
a('<text x="60" y="118" font-size="16.5" font-weight="bold">① 容限窗全景 — 采样时钟相位可在 [数据窗 − 左限, 数据窗 + 右限] 内偏移</text>')

X0, X1 = 120, 1320
VMIN, VMAX = -1.6, 1.6
def tx(v): return X0 + (v - VMIN) / (VMAX - VMIN) * (X1 - X0)
AXIS_Y = 310

# 碰界红线（先画，贯穿箭头层到轴下沿；标签放轴下方独立行，不与任何层抢位）
# 红线标签 = 实际线位（csv 直算），非上代硬编码残值
for val, lab in ((LFT, "%.5f（setup 碰界）" % LFT), (RGT, "+%.5f（hold 碰界）" % RGT)):
    a('<line x1="%.1f" y1="150" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (tx(val), tx(val), AXIS_Y + 12, C_RED))
    a('<text x="%.1f" y="358" font-size="11" fill="%s" class="mono" text-anchor="middle">%s</text>' % (tx(val), C_RED, lab))

# 轴
a('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (X0, AXIS_Y, X1, AXIS_Y, C_TEXT))
v = -1.5
while v <= 1.51:
    a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (tx(v), AXIS_Y, tx(v), AXIS_Y + 8, C_MUTED))
    a('<text x="%.1f" y="336" font-size="12" text-anchor="middle" class="mono" fill="%s">%+.1f</text>' % (tx(v), C_MUTED, v))
    v += 0.5
a('<text x="%d" y="358" font-size="12" class="mono" fill="%s" text-anchor="end">ns（0 = 名义采样沿）</text>' % (X1, C_MUTED))

# 数据窗（悬在轴上方 18px，不压轴线、不遮刻度）
a('<rect x="%.1f" y="248" width="%.1f" height="44" fill="%s" opacity="0.85"/>' % (tx(-0.25), tx(0.25) - tx(-0.25), C_TEAL))
a('<text x="%.1f" y="275" font-size="12.5" fill="#fffdf7" text-anchor="middle">数据有效窗</text>' % tx(0))

# 左移容限箭头（0 → LFT）：三层文字各隔 20px，右端避开红线
a('<line x1="%.1f" y1="190" x2="%.1f" y2="190" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), tx(LFT), C_BLUE))
a('<text x="%.1f" y="174" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">← 左移容限 %.5f ns</text>' % (tx(-0.55), C_BLUE, -LFT))
a('<text x="%.1f" y="214" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF setup %+.5f +0.3+0.4</text>' % (tx(-0.55), C_BLUE, lmin[3]))
a('<text x="%.1f" y="234" font-size="11" fill="%s" text-anchor="middle">%s（setup 先碰界）</text>' % (tx(-0.55), C_MUTED, lmin[0]))

# 右移容限箭头（0 → RGT）：标签中心右移到 1030，整体避让 x≈870 的红线
a('<line x1="%.1f" y1="190" x2="%.1f" y2="190" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), tx(RGT), C_BLUE))
a('<text x="%.1f" y="174" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">右移容限 %.5f ns →</text>' % (1030, C_BLUE, RGT))
a('<text x="%.1f" y="214" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF hold %+.5f +0.3+0.15</text>' % (1030, C_BLUE, rmin[4]))
a('<text x="%.1f" y="234" font-size="11" fill="%s" text-anchor="middle">%s（hold 先碰界）</text>' % (1030, C_MUTED, rmin[0]))

# 底部公式说明
a('<rect x="60" y="372" width="1320" height="120" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>' % (C_BG, C_BORDER))
a('<text x="80" y="398" font-size="13.5" font-weight="bold" fill="%s">换算公式（把 set_input_delay 与 uncertainty 的预算还原成 2M23 裸口径）</text>' % C_AMBER)
a('<text x="80" y="424" font-size="13" class="mono">左移容限 = port→FF setup slack + 0.3（max input delay） + 0.4（setup uncertainty）</text>')
a('<text x="80" y="448" font-size="13" class="mono">右移容限 = port→FF hold slack + 0.3（min input delay −0.3 还原） + 0.15（hold uncertainty）</text>')
a('<text x="80" y="472" font-size="11.5" fill="%s">注：1104V0 代际 port→FF setup = phy csv rx0_00_max 行、port→FF hold = rx0_00_min 行（input port 即头名）；数值全部由 csv 直算，无手录。</text>' % C_MUTED)

# ---------- Panel B: 逐角容限条形 ----------
a('<rect x="40" y="540" width="1360" height="330" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
a('<text x="60" y="568" font-size="16.5" font-weight="bold">② 逐角容限（10 corner）</text>')
# 图例放标题行右侧（红线数值进图例，不再画进条形区）
a('<rect x="500" y="558" width="16" height="12" fill="%s" opacity="0.9"/>' % C_BLUE)
a('<text x="521" y="568" font-size="12">左移 / setup 侧</text>')
a('<rect x="660" y="558" width="16" height="12" fill="%s" opacity="0.9"/>' % C_TEAL)
a('<text x="681" y="568" font-size="12">右移 / hold 侧</text>')
a('<line x1="820" y1="564" x2="848" y2="564" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % C_RED)
a('<text x="856" y="568" font-size="12" fill="%s">全角最小：左 %.5f / 右 %.5f</text>' % (C_RED, -LFT, RGT))

BX, BW, BGAP = 80, 60, 70
BY0, BY1 = 610, 842
BMAX = 1.8
def by(v): return BY1 - v / BMAX * (BY1 - BY0)

# 全角最小红虚线先画（在条形后面，穿过条形处被条形覆盖，数值已进图例）
a('<line x1="70" y1="%.1f" x2="1345" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4" opacity="0.55"/>' % (by(-LFT), by(-LFT), C_RED))
a('<line x1="70" y1="%.1f" x2="1345" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4" opacity="0.55"/>' % (by(RGT), by(RGT), C_RED))

for i, (name, lft, rgt, _mx, _mn) in enumerate(corners):
    x = BX + i * (BW + BGAP)
    a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x, by(lft), BW // 2, BY1 - by(lft), C_BLUE))
    a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x + BW // 2, by(rgt), BW // 2, BY1 - by(rgt), C_TEAL))
    a('<text x="%d" y="%.1f" font-size="9" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW // 4, by(lft) - 5, C_BLUE, lft))
    a('<text x="%d" y="%.1f" font-size="9" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW * 3 // 4, by(rgt) - 5, C_TEAL, rgt))
    a('<text x="%d" y="858" font-size="10" text-anchor="middle" class="mono" fill="%s">%s</text>' % (x + BW // 2, C_MUTED, name))

a('</svg>')
svg = "\n".join(L)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(svg)
print("written", OUT_STATIC, len(svg), "LFT=%.5f RGT=%.5f lmin=%s rmin=%s" % (LFT, RGT, lmin[0], rmin[0]))
# ymzhu 2026-11-04 12:30
