# -*- coding: utf-8 -*-
# Generate config_data_beat_regroup_0721.svg
# LC_CPUWR 0721v1 beat regroup comparison: 0716_v1_work (2B/beat) vs 0721_v1 (3B/beat)

CELL_W, CELL_H, CELL_GAP = 34, 34, 6
BEAT_PAD = 8

C_INC   = ("#ecfdf5", "#16a34a", "#166534")   # included in checksum: fill, border, text
C_GAP   = ("#f1f5f9", "#cbd5e1", "#94a3b8")   # gap / not participating
C_EXCL  = ("#fff7ed", "#fb923c", "#c2410c")   # 0x07 excluded control reg
C_FEND  = ("#fefce8", "#eab308", "#a16207")   # frame_end 0x27
C_OLD   = "#475569"
C_NEW   = "#2563eb"

def cell(x, y, label, kind):
    f, b, t = kind
    s = f'<rect x="{x}" y="{y}" width="{CELL_W}" height="{CELL_H}" rx="5" fill="{f}" stroke="{b}" stroke-width="1.5"/>'
    s += f'<text x="{x+CELL_W/2}" y="{y+22}" text-anchor="middle" font-size="12" font-weight="600" fill="{t}">{label}</text>'
    return s

def beat(x, y, beat_label, cells, fold, frame_color):
    n = len(cells)
    w = BEAT_PAD*2 + n*CELL_W + (n-1)*CELL_GAP
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{CELL_H+2*BEAT_PAD}" rx="9" fill="none" stroke="{frame_color}" stroke-width="2" stroke-dasharray="none"/>'
    s += f'<text x="{x+w/2}" y="{y-8}" text-anchor="middle" font-size="11" font-weight="700" fill="{frame_color}">{beat_label}</text>'
    for i, (lab, kind) in enumerate(cells):
        s += cell(x+BEAT_PAD+i*(CELL_W+CELL_GAP), y+BEAT_PAD, lab, kind)
    s += f'<text x="{x+w/2}" y="{y+CELL_H+2*BEAT_PAD+18}" text-anchor="middle" font-size="11" fill="#334155">{fold}</text>'
    return s

parts = []
parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="1240" height="780" viewBox="0 0 1240 780" font-family="Calibri,Segoe UI,Arial,sans-serif">')
parts.append('<rect width="1240" height="780" fill="#ffffff"/>')
parts.append('<text x="620" y="36" text-anchor="middle" font-size="22" font-weight="800" fill="#1e293b">LC_CPUWR 0721v1 配置拍重组对照（流内字节顺序不变，仅分组 2B/拍 → 3B/拍）</text>')
parts.append('<text x="620" y="60" text-anchor="middle" font-size="13" fill="#64748b">FCONFIG 60B：30 拍 → 20 拍（END 5\'d30 → 5\'d20） ｜ LCONFIG 6B：3 拍 → 2 拍（END 3\'d4 → 3\'d3） ｜ 寄存器地址映射与 XOR 总量均不变</text>')

# legend
lx = 70
for txt, kind in [("参与 checksum 字节", C_INC), ("gap / 不参与", C_GAP), ("0x07 控制寄存器（排除）", C_EXCL), ("0x27 frame end", C_FEND)]:
    f, b, t = kind
    parts.append(f'<rect x="{lx}" y="76" width="16" height="16" rx="4" fill="{f}" stroke="{b}" stroke-width="1.5"/>')
    parts.append(f'<text x="{lx+22}" y="89" font-size="12" fill="#334155">{txt}</text>')
    lx += 22 + len(txt)*12 + 34

# column headers
parts.append(f'<text x="320" y="128" text-anchor="middle" font-size="15" font-weight="800" fill="{C_OLD}">0716_v1_work：2 字节/拍（C, D）</text>')
parts.append(f'<text x="920" y="128" text-anchor="middle" font-size="15" font-weight="800" fill="{C_NEW}">0721_v1：3 字节/拍（C, D, F）</text>')
parts.append('<line x1="620" y1="110" x2="620" y2="700" stroke="#e2e8f0" stroke-width="2"/>')

G, I, X, E = C_GAP, C_INC, C_EXCL, C_FEND

def zone(y0, title):
    parts.append(f'<text x="60" y="{y0}" font-size="13" font-weight="700" fill="#0f172a">{title}</text>')

# ---------------- Zone A: 0x00~0x0B ----------------
zone(158, '区域 A：0x00 ~ 0x0B（checksum 区开头）')
y = 170
# old beats 5'h01..5'h06
old_beats = [
    ("5'h01", [("00",I),("01",I)], "C^D"),
    ("5'h02", [("02",I),("03",I)], "C^D"),
    ("5'h03", [("04",I),("05",I)], "C^D"),
    ("5'h04", [("06",I),("07",X)], "C"),
    ("5'h05", [("08",I),("09",I)], "C^D"),
    ("5'h06", [("0A",I),("0B",G)], "C"),
]
x = 36
for lab, cells, fold in old_beats:
    parts.append(beat(x, y, lab, cells, fold, "#94a3b8"))
    x += BEAT_PAD*2 + 2*CELL_W + CELL_GAP + 6
# new beats 5'h01..5'h04
new_beats = [
    ("5'h01", [("00",I),("01",I),("02",I)], "C^D^F"),
    ("5'h02", [("03",I),("04",I),("05",I)], "C^D^F"),
    ("5'h03", [("06",I),("07",X),("08",I)], "C^F"),
    ("5'h04", [("09",I),("0A",I),("0B",G)], "C^D"),
]
x = 656
for lab, cells, fold in new_beats:
    parts.append(beat(x, y, lab, cells, fold, C_NEW))
    x += BEAT_PAD*2 + 3*CELL_W + 2*CELL_GAP + 16

# ---------------- Zone B: 0x1B~0x20 ----------------
zone(288, '区域 B：0x1B ~ 0x20（跨 Segment1 边界，0721 后 0x1F/0x20 同拍）')
y = 300
old_b = [
    ("5'h0E", [("1B",G),("1C",G)], "—"),
    ("5'h0F", [("1D",I),("1E",G)], "D"),          # note: old 0x1D at 5'h0F pos D
    ("5'h10", [("1E",I),("1F",I)], "C^D"),
    ("5'h11", [("20",G),("21",G)], "—"),
]
# correct old mapping: 0x1B,0x1C at 5'h0E? old pairs: 5'h0E=(0x1B? no)...
# old pairs from decode: 5'h0D=(0x19? gap).. let's just show the relevant ones:
old_b = [
    ("5'h0F", [("1C",G),("1D",I)], "D"),
    ("5'h10", [("1E",I),("1F",I)], "C^D"),
    ("5'h11", [("20",G),("21",G)], "—"),
]
x = 48
for lab, cells, fold in old_b:
    parts.append(beat(x, y, lab, cells, fold, "#94a3b8"))
    x += BEAT_PAD*2 + 2*CELL_W + CELL_GAP + 16
new_b = [
    ("5'h0A", [("1B",G),("1C",G),("1D",I)], "F"),
    ("5'h0B", [("1E",I),("1F",I),("20",G)], "C^D"),
]
x = 656
for lab, cells, fold in new_b:
    parts.append(beat(x, y, lab, cells, fold, C_NEW))
    x += BEAT_PAD*2 + 3*CELL_W + 2*CELL_GAP + 16

# ---------------- Zone C: 0x27 frame end ----------------
zone(418, '区域 C：0x27（checksum frame end；每帧最后一笔参与字节）')
y = 430
old_c = [
    ("5'h13", [("26",G),("27",E)], "frame_end: D"),
    ("5'h14", [("27",E),("28",G)], "frame_end: D"),
]
old_c = [
    ("5'h14", [("26",G),("27",E)], "frame_end: D"),
]
x = 48
for lab, cells, fold in old_c:
    parts.append(beat(x, y, lab, cells, fold, "#94a3b8"))
    x += BEAT_PAD*2 + 2*CELL_W + CELL_GAP + 16
new_c = [
    ("5'h0E", [("27",E),("28",G),("29",G)], "frame_end: C"),
]
x = 656
for lab, cells, fold in new_c:
    parts.append(beat(x, y, lab, cells, fold, C_NEW))
    x += BEAT_PAD*2 + 3*CELL_W + 2*CELL_GAP + 16

# ---------------- Zone D: LCONFIG ----------------
zone(548, '区域 D：LCONFIG 0x40 ~ 0x44（6B：3 拍 → 2 拍，无 pad）')
y = 560
old_l = [
    ("3'h1", [("40",I),("41",I)], "A,B"),
    ("3'h2", [("42",I),("43",I)], "A,B"),
    ("3'h3", [("44",I),("--",G)], "A"),
]
x = 48
for lab, cells, fold in old_l:
    parts.append(beat(x, y, lab, cells, fold, "#94a3b8"))
    x += BEAT_PAD*2 + 2*CELL_W + CELL_GAP + 16
new_l = [
    ("3'h1", [("40",I),("41",I),("42",I)], "A,B,E"),
    ("3'h2", [("43",I),("44",I),("--",G)], "A,B"),
]
x = 656
for lab, cells, fold in new_l:
    parts.append(beat(x, y, lab, cells, fold, C_NEW))
    x += BEAT_PAD*2 + 3*CELL_W + 2*CELL_GAP + 16

# ---------------- Summary ----------------
parts.append('<rect x="48" y="688" width="560" height="72" rx="10" fill="#ecfdf5" stroke="#16a34a" stroke-width="1.5"/>')
parts.append('<text x="64" y="714" font-size="13" font-weight="700" fill="#166534">XOR 总量不变（结合律）</text>')
parts.append('<text x="64" y="734" font-size="12" fill="#166534">0x00^01^02^03^04^05^06^08^09^0A^1D^1E^1F，frame_end=0x27</text>')
parts.append('<text x="64" y="752" font-size="12" fill="#166534">分组变化不改值 → checker / DV 期望与回归行为不变</text>')
parts.append('<rect x="640" y="688" width="560" height="72" rx="10" fill="#fff7ed" stroke="#fb923c" stroke-width="1.5"/>')
parts.append('<text x="656" y="714" font-size="13" font-weight="700" fill="#c2410c">过渡依赖</text>')
parts.append('<text x="656" y="734" font-size="12" fill="#c2410c">CHPI_CONFIG_L0 未升 24bit 前，LINK_LOGIC 将 [23:16] tie-off 防 X 传播</text>')
parts.append('<text x="656" y="752" font-size="12" fill="#c2410c">全芯片 FCONFIG 流仿真待上游升版后联调（END：5\'d20 / 3\'d3）</text>')

parts.append('</svg>')

out = r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\config_data_beat_regroup_0721.svg"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(parts))
print("written:", out)
