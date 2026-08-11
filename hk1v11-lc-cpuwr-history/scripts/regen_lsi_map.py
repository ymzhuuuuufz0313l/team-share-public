# -*- coding: utf-8 -*-
# Regenerate lsi_unprotected_address_map.svg with text-driven layout (no truncation / no overlap).
# Strategy: parse original SVG cells (color/name/default/bit-span), re-layout on a wider uniform
# bit grid (COL_W=124), adaptive font sizing so every field name fits fully.

import re, math

SRC = r"E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\lsi_unprotected_address_map.svg"
DST = SRC  # overwrite

MD0 = r"E:\project\HK1V11\LC_CPUWR_history\chip_sel0_register_address_map.md"
MD1 = r"E:\project\HK1V11\LC_CPUWR_history\chip_sel1_register_address_map.md"

# --- parse address-map MDs -> (addr_dec, high, low) -> field name ---
def parse_md(path):
    tbl = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 6 or not cols[0].isdigit():
            continue
        dec = int(cols[0])
        bits = cols[2].strip("[]")
        if ":" in bits:
            hi, lo = int(bits.split(":")[0]), int(bits.split(":")[1])
        else:
            hi = lo = int(bits)
        tbl[(dec, hi, lo)] = cols[3]
    return tbl

MAP1 = parse_md(MD1)   # chip_sel=1 first (has SMART_CS / SR_* / PWRC_* / FSEL)
MAP0 = parse_md(MD0)

def full_name(addr, hi, lo, orig):
    return MAP1.get((addr, hi, lo)) or MAP0.get((addr, hi, lo)) or orig

raw = open(SRC, encoding="utf-8").read()

# --- parse cells ---
rect_re = re.compile(
    r'<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="46" fill="(#[0-9a-f]{6})"[^>]*/>'
    r'\s*<text x="[\d.]+" y="[\d.]+" text-anchor="middle" font-size="[\d.]+" font-weight="500" fill="#1e293b">([^<]+)</text>'
    r'\s*<text x="[\d.]+" y="[\d.]+" text-anchor="middle" font-size="[\d.]+" fill="#64748b">([^<]*)</text>')

label_re = re.compile(r'<text x="158" y="([\d.]+)" text-anchor="end" font-size="1[34]" font-weight="600" fill="[^"]+">([^<]+)</text>')
dash_re = re.compile(
    r'<rect x="170" y="([\d.]+)" width="655" height="46" fill="#e2e8f0"[^>]*/>'
    r'\s*<text x="497.5" y="[\d.]+" text-anchor="middle" font-size="12" fill="#64748b">([^<]+)</text>')

cells = []   # (y, bit_idx, span, fill, name, default)
for m in rect_re.finditer(raw):
    x, y, w, fill, name, default = m.groups()
    if fill == "#e2e8f0":
        continue
    bit_idx = round((float(x) - 170) / 82)
    span = max(1, round(float(w) / 82))
    cells.append(dict(y=float(y), bit=bit_idx, span=span, fill=fill,
                      name=name, default=default))

labels = {round(float(y)) - 28: txt for y, txt in label_re.findall(raw)}
dashrows = {round(float(y)): txt for y, txt in dash_re.findall(raw)}

addr_of = {}
for y, txt in labels.items():
    m = re.match(r"0x[0-9A-Fa-f]+ \((\d+)\)", txt)
    if m:
        addr_of[y] = int(m.group(1))

# resolve full field names via MD lookup
unresolved = []
for c in cells:
    addr = addr_of.get(round(c["y"]))
    if addr is None:
        unresolved.append(c["name"])
        continue
    hi = 7 - c["bit"]
    lo = 8 - c["bit"] - c["span"]
    new = full_name(addr, hi, lo, c["name"])
    if new.endswith("\u2026"):
        unresolved.append(f"0x{addr:02X}[{hi}:{lo}] {c['name']} -> {new}")
    c["name"] = new

# group rows by y
rows = {}
for c in cells:
    rows.setdefault(c["y"], []).append(c)
row_ys = sorted(rows.keys() | set(dashrows))

# --- layout params ---
COL_W   = 124     # uniform bit column width
ROW_H   = 52
CELL_H  = 46
X0      = 170
LABEL_X = 158
TOP     = 124     # first row y
CHAR_F  = 0.56    # approx char width factor (Calibri 500)

def fit_font(name, span):
    avail = span * COL_W - 16
    for f in (10, 9, 8, 7.5, 7, 6.5):
        if len(name) * f * CHAR_F <= avail:
            return f
    return 6.5

out = []
out.append('<?xml version="1.0" encoding="UTF-8"?>')

# compute canvas
width  = X0 + 8 * COL_W + 36
n_rows = len(row_ys)
height = TOP + n_rows * ROW_H + 130
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" style="background:#ffffff">')
out.append(f'<rect width="{width}" height="{height}" fill="#ffffff"/>')
cx = width / 2
out.append(f'<text x="{cx}" y="38" text-anchor="middle" font-size="22" font-weight="bold" fill="#1e293b">LC_CPUWR 0810v1 寄存器 LSI_PRTECT 保护状态</text>')
out.append(f'<text x="{cx}" y="62" text-anchor="middle" font-size="12" fill="#64748b">红色=受 LSI_PRTECT 保护（输出/读回经掩码）；绿色=不受保护；紫色=密码寄存器 0x30；0810v1 同步寄存器表（reg48/reg160/reg161 无掩码、reg147 保留保护）</text>')

# bit headers
for i in range(8):
    bx = X0 + i * COL_W + COL_W / 2
    out.append(f'<text x="{bx}" y="{TOP - 14}" text-anchor="middle" font-size="12" fill="#64748b">[{7 - i}]</text>')

for idx, ry in enumerate(row_ys):
    y = TOP + idx * ROW_H
    # address label
    lab = labels.get(round(ry))
    if lab:
        fs = 13 if "~" in lab else 14
        out.append(f'<text x="{LABEL_X}" y="{y + 28}" text-anchor="end" font-size="{fs}" font-weight="600" fill="#1e293b">{lab}</text>')
    # dashed reserved row
    if round(ry) in dashrows:
        out.append(f'<rect x="{X0}" y="{y}" width="{8 * COL_W}" height="{CELL_H}" fill="#e2e8f0" stroke="#94a3b8" stroke-width="1" stroke-dasharray="4,3" rx="4"/>')
        out.append(f'<text x="{X0 + 4 * COL_W}" y="{y + 29}" text-anchor="middle" font-size="12" fill="#64748b">{dashrows[round(ry)]}</text>')
        continue
    # field cells
    for c in sorted(rows.get(ry, []), key=lambda d: d["bit"]):
        x = X0 + c["bit"] * COL_W
        w = c["span"] * COL_W
        nf = fit_font(c["name"], c["span"])
        df = 9 if nf >= 10 else (8 if nf >= 8 else 7)
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{CELL_H}" fill="{c["fill"]}" stroke="#94a3b8" stroke-width="1" rx="4"/>')
        out.append(f'<text x="{x + w / 2}" y="{y + 21}" text-anchor="middle" font-size="{nf}" font-weight="500" fill="#1e293b">{c["name"]}</text>')
        if c["default"]:
            out.append(f'<text x="{x + w / 2}" y="{y + 36}" text-anchor="middle" font-size="{df}" fill="#64748b">{c["default"]}</text>')

# legend + caption
ly = TOP + n_rows * ROW_H + 24
out.append(f'<text x="90" y="{ly}" font-size="13" font-weight="600" fill="#1e293b">图例</text>')
out.append(f'<rect x="90" y="{ly + 10}" width="14" height="14" fill="#f87171" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="110" y="{ly + 21}" font-size="11" fill="#1e293b">受 LSI_PRTECT 保护</text>')
out.append(f'<rect x="240" y="{ly + 10}" width="14" height="14" fill="#4ade80" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="260" y="{ly + 21}" font-size="11" fill="#1e293b">不受保护</text>')
out.append(f'<rect x="350" y="{ly + 10}" width="14" height="14" fill="#c084fc" stroke="#94a3b8" rx="2"/>')
out.append(f'<text x="370" y="{ly + 21}" font-size="11" fill="#1e293b">密码寄存器 (0x30)</text>')
out.append(f'<text x="{cx}" y="{ly + 60}" text-anchor="middle" font-size="11" fill="#64748b">0x00~0x1F、0x27、0x40~0x44 读回/输出不经过 LSI_PRTECT 掩码；0x20~0x39（除 0x27）、0x90~0x92 受保护</text>')
out.append('</svg>')

open(DST, "w", encoding="utf-8").write("\n".join(out))
print("written:", DST, f"({width}x{height}, {n_rows} rows, {len(cells)} cells)")
if unresolved:
    print("UNRESOLVED (still truncated):", len(unresolved))
    for u in unresolved:
        print("  -", u.encode("unicode_escape").decode())

# quick XML validation
import xml.etree.ElementTree as ET
ET.parse(DST)
print("XML valid")
