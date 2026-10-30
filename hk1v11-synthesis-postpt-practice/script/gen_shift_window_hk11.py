# -*- coding: utf-8 -*-
# gen_shift_window_hk11.py — ch09 §6.3 时钟偏移容限图（1029V0，左 1.094 / 右 0.401）
# 站点色板（practice :root）：纸 #f4f1ea / 墨 #1c2534 / 琥珀 #b45309 / 深青 #0e7490
#   绿 #047857 / 红 #b91c1c / 蓝 #1d4ed8 / 面 #fffdf7 / 线 #c9bfa8 / 网格 #ddd6c8
# 数据源（零手工）：wc/lt 角实测（ch09 §6.3 换算表）
#   port→FF setup: lt_cworst +0.393883, wc_cworst +2.186397
#   port→FF hold:  lt_typical −0.048711, wc_cworst +0.173885
#   还原预算：setup +0.3+0.4；hold +0.3+0.15
import io, os

SITE = r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice"
OUT = os.path.join(SITE, "images", "anim", "56_signoff_shift_window_hk11.svg")
OUT_STATIC = os.path.join(SITE, "images", "56_signoff_shift_window_hk11.svg")

C_BG, C_PANEL, C_BORDER = "#f4f1ea", "#fffdf7", "#c9bfa8"
C_TEXT, C_MUTED, C_GRID = "#1c2534", "#5b6675", "#ddd6c8"
C_AMBER, C_TEAL, C_GREEN, C_RED, C_BLUE = "#b45309", "#0e7490", "#047857", "#b91c1c", "#1d4ed8"
SOFT, SOFT_RED, SOFT_BLUE = "#f7e8d4", "#f8dede", "#d3e3f6"

L = []
a = L.append
W, H = 1440, 900
a('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">' % (W, H, W, H))
a('<style>text{font-family:"Microsoft YaHei","Noto Sans SC",monospace;fill:%s}.mono{font-family:Consolas,"Microsoft YaHei",monospace}</style>' % C_TEXT)
a('<rect width="%d" height="%d" fill="%s"/>' % (W, H, C_BG))
a('<text x="14" y="34" font-size="11" fill="%s" class="mono">HK1V11 · SIGNOFF · CLOCK SHIFT WINDOW · 1029V0 · 10 CORNER</text>' % C_AMBER)
a('<text x="14" y="66" font-size="22" font-weight="bold"><tspan fill="%s">时钟偏移容限</tspan> — 采样时钟相对数据可左移 / 右移多少</text>' % C_AMBER)

# ---------- Panel A: 时间轴窗 ----------
a('<rect x="40" y="90" width="1360" height="430" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
a('<text x="60" y="118" font-size="16.5" font-weight="bold">① 容限窗全景 — 采样时钟相位可在 [数据窗 − 左限, 数据窗 + 右限] 内偏移</text>')

# 坐标轴：0 = 名义采样沿位置；左负右正
X0, X1 = 120, 1320          # 轴范围
VMIN, VMAX = -1.6, 1.6      # 显示值域 ns
def tx(v): return X0 + (v - VMIN) / (VMAX - VMIN) * (X1 - X0)
AXIS_Y = 360

# 轴
a('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="2"/>' % (X0, AXIS_Y, X1, AXIS_Y, C_TEXT))
v = -1.5
while v <= 1.51:
    a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="1"/>' % (tx(v), AXIS_Y, tx(v), AXIS_Y + 8, C_MUTED))
    a('<text x="%.1f" y="%d" font-size="12" text-anchor="middle" class="mono" fill="%s">%+.1f</text>' % (tx(v), AXIS_Y + 26, C_MUTED, v))
    v += 0.5
a('<text x="%d" y="%d" font-size="12" class="mono" fill="%s">ns（0 = 名义采样沿）</text>' % (X1 + 6, AXIS_Y + 4, C_MUTED))

# 数据窗（中心矩形示意，宽 0.5）
a('<rect x="%.1f" y="%d" width="%.1f" height="46" fill="%s" opacity="0.85"/>' % (tx(-0.25), AXIS_Y - 23, tx(0.25) - tx(-0.25), C_TEAL))
a('<text x="%.1f" y="%d" font-size="12.5" fill="#fffdf7" text-anchor="middle">数据有效窗</text>' % (tx(0), AXIS_Y + 3))

# 左移容限箭头（0 → −1.09388）
a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), AXIS_Y - 60, tx(-1.09388), AXIS_Y - 60, C_BLUE))
a('<text x="%.1f" y="%d" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">← 左移容限 1.09388 ns</text>' % (tx(-0.55), AXIS_Y - 72, C_BLUE))
a('<text x="%.1f" y="%d" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF setup +0.393883 +0.3+0.4</text>' % (tx(-0.55), AXIS_Y - 40, C_BLUE))
a('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">lt_cworst_m40（setup 先碰界）</text>' % (tx(-0.55), AXIS_Y - 26, C_MUTED))

# 右移容限箭头（0 → +0.40129）
a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="3" marker-end="url(#mB)"/>' % (tx(0), AXIS_Y - 60, tx(0.40129), AXIS_Y - 60, C_BLUE))
a('<text x="%.1f" y="%d" font-size="13.5" fill="%s" text-anchor="middle" font-weight="bold">右移容限 0.40129 ns →</text>' % (tx(0.72), AXIS_Y - 72, C_BLUE))
a('<text x="%.1f" y="%d" font-size="11.5" class="mono" fill="%s" text-anchor="middle">= port→FF hold −0.048711 +0.3+0.15</text>' % (tx(0.72), AXIS_Y - 40, C_BLUE))
a('<text x="%.1f" y="%d" font-size="11" fill="%s" text-anchor="middle">lt_typical_m40（hold 先碰界）</text>' % (tx(0.72), AXIS_Y - 26, C_MUTED))

# 碰界标记（红）
a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (tx(-1.09388), AXIS_Y - 90, tx(-1.09388), AXIS_Y + 12, C_RED))
a('<text x="%.1f" y="%d" font-size="11" fill="%s" class="mono" text-anchor="middle">−1.09388（setup 碰界）</text>' % (tx(-1.09388), AXIS_Y - 96, C_RED))
a('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="%s" stroke-width="2.5" stroke-dasharray="5,3"/>' % (tx(0.40129), AXIS_Y - 90, tx(0.40129), AXIS_Y + 12, C_RED))
a('<text x="%.1f" y="%d" font-size="11" fill="%s" class="mono" text-anchor="middle">+0.40129（hold 碰界）</text>' % (tx(0.40129), AXIS_Y - 96, C_RED))

# 底部公式说明
a('<rect x="60" y="%d" width="1320" height="130" rx="2" fill="%s" stroke="%s" stroke-width="1.2"/>' % (AXIS_Y + 44, C_BG, C_BORDER))
a('<text x="80" y="%d" font-size="13.5" font-weight="bold" fill="%s">换算公式（把 set_input_delay 与 uncertainty 的预算还原成 2M23 裸口径）</text>' % (AXIS_Y + 72, C_AMBER))
a('<text x="80" y="%d" font-size="13" class="mono">左移容限 = port→FF setup slack + 0.3（max input delay） + 0.4（setup uncertainty）</text>' % (AXIS_Y + 98))
a('<text x="80" y="%d" font-size="13" class="mono">右移容限 = port→FF hold slack + 0.3（min input delay −0.3 还原） + 0.15（hold uncertainty）</text>' % (AXIS_Y + 122))
a('<text x="80" y="%d" font-size="11.5" fill="%s">注：port→FF setup 取自 rx0_00_max.rpt 内 dout_lane 块（FF→FF 只是抢了头名）；port→FF hold 即 phy 表 rx0_00_min 行</text>' % (AXIS_Y + 146, C_MUTED))

# ---------- Panel B: 逐角容限条形 ----------
a('<rect x="40" y="540" width="1360" height="330" rx="2" fill="%s" stroke="%s" stroke-width="1.5"/>' % (C_PANEL, C_BORDER))
a('<text x="60" y="568" font-size="16.5" font-weight="bold">② 逐角容限（10 corner，蓝=左移/setup 侧、青=右移/hold 侧，红虚线=全角最小）</text>')

corners = [
    ("wc_cworst",  2.88640, 0.62389),
    ("wc_cbest",   2.96676, 0.57163),
    ("wc_typical", 2.90272, 0.62364),
    ("lt_cworst",  1.09388, 0.40660),
    ("lt_cbest",   1.19273, 0.40698),
    ("lt_typical", 1.12826, 0.40129),
    ("ml_cbest",   1.57391, 0.42736),
    ("tt_cworst",  1.60629, 0.46943),
    ("tt_cbest",   1.70101, 0.47037),
    ("tt_typical", 1.63806, 0.46960),
]
BX, BW, BGAP = 80, 60, 70
BY0, BY1 = 600, 840
BMAX = 3.2
def by(v): return BY1 - v / BMAX * (BY1 - BY0)
for i, (name, lft, rgt) in enumerate(corners):
    x = BX + i * (BW + BGAP)
    a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x, by(lft), BW // 2, BY1 - by(lft), C_BLUE))
    a('<rect x="%d" y="%.1f" width="%d" height="%.1f" fill="%s" opacity="0.9"/>' % (x + BW // 2, by(rgt), BW // 2, BY1 - by(rgt), C_TEAL))
    a('<text x="%d" y="%.1f" font-size="10" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW // 4, by(lft) - 6, C_BLUE, lft))
    a('<text x="%d" y="%.1f" font-size="10" text-anchor="middle" class="mono" fill="%s">%.2f</text>' % (x + BW * 3 // 4, by(rgt) - 6, C_TEAL, rgt))
    a('<text x="%d" y="%d" font-size="10" text-anchor="middle" class="mono" fill="%s">%s</text>' % (x + BW // 2, BY1 + 16, C_MUTED, name))

# 全角最小虚线
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (BX - 10, by(1.09388), BX + 10 * (BW + BGAP), by(1.09388), C_RED))
a('<text x="%d" y="%.1f" font-size="11" fill="%s" class="mono">左移全角最小 1.094</text>' % (BX + 10 * (BW + BGAP) - 160, by(1.09388) - 8, C_RED))
a('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="%s" stroke-width="2" stroke-dasharray="6,4"/>' % (BX - 10, by(0.40129), BX + 10 * (BW + BGAP), by(0.40129), C_RED))
a('<text x="%d" y="%.1f" font-size="11" fill="%s" class="mono">右移全角最小 0.401</text>' % (BX + 10 * (BW + BGAP) - 160, by(0.40129) - 8, C_RED))

a('</svg>')
svg = "\n".join(L)
io.open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
io.open(OUT_STATIC, "w", encoding="utf-8", newline="\n").write(svg)
print("written", OUT, len(svg))
