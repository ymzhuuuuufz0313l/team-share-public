# -*- coding: utf-8 -*-
# Generate lsi_unprotected_address_map.svg from scratch (0827v1).
#
# 旧版脚本通过解析旧 SVG 重排版，会继承旧图中的语义错误（字段名复制错位、缺行、
# chip_sel0/1 默认值混杂、reg37/38 默认值过期等）。本版本改为：
#   1) 字段名/默认值直接解析 chip_sel0_register_address_map.md（单一事实源）
#   2) LSI_PRTECT 保护状态硬编码自 LC_CPUWR.v（0827v1）RTL 真值：
#      - 输出门控：R_REG32~38/40~47/51/53~57/144~147 字段 assign 带 LSI_PRTECT ? 掩码
#      - 读回掩码：REGRD_NOML case 中 8'd32~38/40~47/49~57/144~147 带 & {8{LSI_PRTECT}}
#      - 0x27(39) 0707v1 起解除保护；0x30(48) 为密码寄存器（==8'h72 解锁，不掩码）；
#        0xA0/0xA1 (160/161) 0810v1 起无掩码
#
# 用法：python regen_lsi_map.py   （覆盖写 images/lsi_unprotected_address_map.svg）

import xml.etree.ElementTree as ET

MD0 = r"E:\project\HK1V11\LC_CPUWR_history\chip_sel0_register_address_map.md"
DST = r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\lsi_unprotected_address_map.svg"

VERSION = "0827v1"

# --- RTL 真值：LSI_PRTECT 保护状态（按地址，十进制） ---
PROTECTED = set(range(32, 39)) | set(range(40, 48)) | set(range(49, 58)) | {144, 145, 146, 147}
PASSWORD  = {48}          # TEST_PRTCT，==8'h72 解锁，自身不掩码
# 其余地址（0~31、39、64~68、160、161）不受 LSI_PRTECT 保护

# --- 解析 chip_sel0 地址映射表 ---
def parse_md(path):
    """返回 [(addr_dec, addr_hex, [(hi, lo, name, default), ...]), ...]，按地址/位段排序"""
    rows = {}
    order = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 6 or not cols[0].isdigit():
            continue
        dec = int(cols[0])
        hexa = cols[1]
        bits = cols[2].strip("[]")
        if ":" in bits:
            hi, lo = int(bits.split(":")[0]), int(bits.split(":")[1])
        else:
            hi = lo = int(bits)
        if dec not in rows:
            rows[dec] = (hexa, [])
            order.append(dec)
        rows[dec][1].append((hi, lo, cols[3], cols[4]))
    out = []
    for dec in order:
        hexa, fields = rows[dec]
        fields.sort(key=lambda f: -f[0])   # 高位在前
        out.append((dec, hexa, fields))
    return out

def clean_default(v):
    """修正常见笔误，统一写法"""
    v = v.strip()
    v = v.replace("2b'", "2'b").replace("1b'", "1'b").replace("4b0000", "4'b0000")
    return v

TABLE = parse_md(MD0)

# 0827v1 视觉优化：连续（地址连续、纯 Reserved [7:0]、未受保护）行合并为区间带，与其他图风格一致
def is_pure_reserved(row):
    _, _, fields = row
    return len(fields) == 1 and fields[0][2] == "Reserved" and fields[0][0] == 7 and fields[0][1] == 0

UNITS = []  # ('row', row) 或 ('band', first_row, last_row)
i = 0
while i < len(TABLE):
    row = TABLE[i]
    if is_pure_reserved(row) and row[0] not in PROTECTED:
        j = i + 1
        while (j < len(TABLE) and TABLE[j][0] == TABLE[j - 1][0] + 1
               and is_pure_reserved(TABLE[j]) and TABLE[j][0] not in PROTECTED):
            j += 1
        if j - i >= 3:
            UNITS.append(('band', TABLE[i], TABLE[j - 1]))
        else:
            UNITS.extend(('row', r) for r in TABLE[i:j])
        i = j
    else:
        UNITS.append(('row', row))
        i += 1

# --- 颜色（柔和低饱和） ---
C_PROT = "#fecaca"   # 受 LSI_PRTECT 保护（红）
C_FREE = "#bbf7d0"   # 不受保护（绿）
C_PWD  = "#e9d5ff"   # 密码寄存器（紫）
C_RSRV = "#e2e8f0"   # 整行 Reserved（灰，虚线）

def fill_of(addr):
    if addr in PASSWORD:
        return C_PWD
    return C_PROT if addr in PROTECTED else C_FREE

# --- 布局参数 ---
COL_W   = 124
ROW_H   = 52
CELL_H  = 46
X0      = 170
LABEL_X = 158
TOP     = 124
CHAR_F  = 0.56

def fit_font(name, span):
    avail = span * COL_W - 16
    for f in (10, 9, 8, 7.5, 7, 6.5):
        if len(name) * f * CHAR_F <= avail:
            return f
    return 6.5

width  = X0 + 8 * COL_W + 36
n_rows = len(UNITS)
height = TOP + n_rows * ROW_H + 170
cx = width / 2

out = []
out.append('<?xml version="1.0" encoding="UTF-8"?>')
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background:#ffffff">')
out.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
out.append(f'<text x="{cx}" y="38" text-anchor="middle" font-size="22" font-weight="bold" fill="#1e293b">LC_CPUWR {VERSION} 寄存器 LSI_PRTECT 保护状态（chip_sel = 0 视图）</text>')
out.append(f'<text x="{cx}" y="62" text-anchor="middle" font-size="12" fill="#64748b">红色=受 LSI_PRTECT 保护（输出门控 + I2C 读回掩码）；绿色=不受保护；紫色=密码寄存器 0x30（=8&apos;h72 解锁）；字段/默认值取自 chip_sel0_register_address_map.md（{VERSION}）</text>')
out.append(f'<text x="{cx}" y="82" text-anchor="middle" font-size="11" fill="#64748b">0827v1：0x38[6] 新增 reg_eol（1&apos;b0，受保护）；0x33[6:2] 改 Reserved（复位 5&apos;b00000）；0x02/0x03/0x04 新增单 bit lane_ctrl3/4/1/2/0（默认 0，不受保护）；保护范围自 0810v1 起不变</text>')

for i in range(8):
    bx = X0 + i * COL_W + COL_W / 2
    out.append(f'<text x="{bx}" y="{TOP - 14}" text-anchor="middle" font-size="12" fill="#64748b">[{7 - i}]</text>')

for idx, unit in enumerate(UNITS):
    y = TOP + idx * ROW_H
    if unit[0] == 'band':
        r0, r1 = unit[1], unit[2]
        out.append(f'<text x="{LABEL_X}" y="{y + 28}" text-anchor="end" font-size="13" font-weight="600" fill="#64748b">{r0[1]} ~ {r1[1]} ({r0[0]} ~ {r1[0]})</text>')
        out.append(f'<rect x="{X0}" y="{y}" width="{8 * COL_W}" height="{CELL_H}" fill="{C_RSRV}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3" rx="4"/>')
        out.append(f'<text x="{X0 + 4 * COL_W}" y="{y + 29}" text-anchor="middle" font-size="12" fill="#64748b">⋯ 全 Reserved ⋯（不受保护）</text>')
        continue
    dec, hexa, fields = unit[1]
    out.append(f'<text x="{LABEL_X}" y="{y + 28}" text-anchor="end" font-size="14" font-weight="600" fill="#1e293b">{hexa} ({dec})</text>')
    # 整行 Reserved → 灰色虚线行
    if len(fields) == 1 and fields[0][2] == "Reserved" and fields[0][0] == 7 and fields[0][1] == 0:
        note = "Reserved"
        if dec in PROTECTED:
            note += "（读回掩码）"
        out.append(f'<rect x="{X0}" y="{y}" width="{8 * COL_W}" height="{CELL_H}" fill="{C_RSRV}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3" rx="4"/>')
        out.append(f'<text x="{X0 + 4 * COL_W}" y="{y + 29}" text-anchor="middle" font-size="12" fill="#64748b">{note}</text>')
        continue
    fill = fill_of(dec)
    for hi, lo, name, default in fields:
        span = hi - lo + 1
        bit = 7 - hi               # 列号：bit7 在最左
        x = X0 + bit * COL_W
        w = span * COL_W
        nf = fit_font(name, span)
        df = 9 if nf >= 10 else (8 if nf >= 8 else 7)
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{CELL_H}" fill="{fill}" stroke="#94a3b8" stroke-width="1" rx="4"/>')
        out.append(f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" font-size="{nf}" font-weight="500" fill="#1e293b">{name}</text>')
        dv = clean_default(default)
        if dv:
            out.append(f'<text x="{x + w / 2}" y="{y + 36}" text-anchor="middle" font-size="{df}" fill="#64748b">{dv}</text>')

# --- 图例 + 脚注 ---
ly = TOP + n_rows * ROW_H + 24
out.append(f'<text x="90" y="{ly}" font-size="13" font-weight="600" fill="#1e293b">图例</text>')
out.append(f'<rect x="90" y="{ly + 10}" width="14" height="14" fill="{C_PROT}" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="110" y="{ly + 21}" font-size="11" fill="#1e293b">受 LSI_PRTECT 保护</text>')
out.append(f'<rect x="240" y="{ly + 10}" width="14" height="14" fill="{C_FREE}" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="260" y="{ly + 21}" font-size="11" fill="#1e293b">不受保护</text>')
out.append(f'<rect x="350" y="{ly + 10}" width="14" height="14" fill="{C_PWD}" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="370" y="{ly + 21}" font-size="11" fill="#1e293b">密码寄存器 (0x30)</text>')
out.append(f'<rect x="500" y="{ly + 10}" width="14" height="14" fill="{C_RSRV}" stroke="#94a3b8" stroke-width="1" stroke-dasharray="3,2" rx="2"/>')
out.append(f'<text x="520" y="{ly + 21}" font-size="11" fill="#1e293b">整行 Reserved</text>')
out.append(f'<text x="{cx}" y="{ly + 52}" text-anchor="middle" font-size="11" fill="#64748b">不受保护：0x00~0x1F、0x27、0x40~0x44、0xA0/0xA1；受保护：0x20~0x26、0x28~0x2F、0x31~0x39、0x90~0x93；0x30 写入 8&apos;h72 后解锁</text>')
out.append(f'<text x="{cx}" y="{ly + 72}" text-anchor="middle" font-size="11" fill="#64748b">chip_sel=1 差异（0x02 SMART_CS、0x09/0x0A/0x1F 回拼默认值）见 chip_sel1 寄存器图；保护状态两种 chip_sel 一致</text>')
out.append('</svg>')

open(DST, "w", encoding="utf-8").write("\n".join(out))
print("written:", DST, f"({width}x{height}, {n_rows} rows)")

ET.parse(DST)
print("XML valid")
