#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate SVG diagrams for LC_CPUWR register attributes:
1. Checksum participation
2. LSI protection
3. Reset domain classification

Data is derived from LC_CPUWR_20260714_v1_decimal.v RTL analysis,
using chip_sel1_register_address_map.md for field names.
"""

import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Style configuration
# ---------------------------------------------------------------------------
COLORS = {
    "text":       "#1e293b",
    "muted":      "#64748b",
    "border":     "#94a3b8",
    "bg":         "#ffffff",

    # checksum
    "chk_full":   "#22c55e",   # participates in XOR accumulation
    "chk_ctrl":   "#f97316",   # checksum control (0x07)
    "chk_end":    "#facc15",   # frame end boundary (0x27)
    "chk_none":   "#e2e8f0",   # no checksum

    # LSI protection
    "lsi_prot":   "#f87171",   # protected by LSI_PRTECT
    "lsi_open":   "#4ade80",   # not protected
    "lsi_pwd":    "#c084fc",   # password register (0x30 TEST_PRTCT)

    # reset domains
    "rst_nlock":  "#dbeafe",   # N_RST_NLOCK (muted, most common)
    "rst_n":      "#f97316",   # N_RST (emphasized)
    "rst_scr":    "#22c55e",   # RSTN_SCR_EN (emphasized)
    "rst_other":  "#fbbf24",   # other / mixed
}


def parse_table(path: Path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if len(parts) < 6 or parts[0] == "地址(DEC)":
                continue
            try:
                dec = int(parts[0])
                rows.append({
                    "dec": dec,
                    "hex": parts[1],
                    "bits": parts[2],
                    "name": parts[3],
                    "default": parts[4],
                    "access": parts[5],
                })
            except ValueError:
                continue
    return rows


def bit_range(bits: str):
    m = re.match(r"\[(\d+)(?::(\d+))?\]", bits)
    if not m:
        return None
    msb = int(m.group(1))
    lsb = int(m.group(2)) if m.group(2) else msb
    return msb, lsb


def build_address_map(rows):
    from collections import defaultdict
    addr_rows = defaultdict(list)
    for r in rows:
        addr_rows[r["dec"]].append(r)

    result = {}
    for dec in sorted(addr_rows.keys()):
        entries = []
        for r in addr_rows[dec]:
            rng = bit_range(r["bits"])
            if rng is None:
                continue
            entries.append({
                "dec": dec,
                "hex": r["hex"],
                "msb": rng[0],
                "lsb": rng[1],
                "name": r["name"],
                "default": r["default"],
                "access": r["access"],
            })
        entries.sort(key=lambda x: -x["msb"])
        result[dec] = entries
    return result


def is_fully_reserved(entries):
    return (len(entries) == 1 and
            entries[0]["name"] == "Reserved" and
            entries[0]["msb"] == 7 and entries[0]["lsb"] == 0)


# ---------------------------------------------------------------------------
# Attribute data derived from RTL
# ---------------------------------------------------------------------------

def checksum_status(dec, msb=None, lsb=None):
    """
    Return color key for checksum status.
    """
    if dec == 0x07:
        return "chk_ctrl"
    if dec == 0x27:
        return "chk_end"
    if dec in (0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
               0x08, 0x09, 0x0A,
               0x1D, 0x1E, 0x1F):
        return "chk_full"
    return "chk_none"


def lsi_status(dec, msb=None, lsb=None):
    """
    Return color key for LSI protection status.
    """
    if dec == 0x30:
        return "lsi_pwd"
    if 0x00 <= dec <= 0x1F:
        return "lsi_open"
    if dec == 0x27:
        return "lsi_open"
    if 0x20 <= dec <= 0x39:
        return "lsi_prot"
    if 0x40 <= dec <= 0x44:
        return "lsi_open"
    if 0x90 <= dec <= 0x92:
        return "lsi_prot"
    return "lsi_open"


def reset_domain(dec, name):
    """
    Return color key for reset domain of a specific field.
    """
    # Special per-bit cases
    if dec == 0x00 and name == "SCREN":
        return "rst_scr"
    if dec == 0x01 and name == "PORSD":
        return "rst_n"
    if dec == 0x05 and name.startswith("CH_SEL"):
        return "rst_n"
    if dec == 0x06 and name in ("SDC", "DPLC_MODE"):
        return "rst_n"
    if dec == 0x20 and name.startswith("R_TESTO_SEL"):
        return "rst_n"
    if dec == 0x21 and name.startswith("R_UTC"):
        return "rst_n"
    if dec == 0x30:
        return "rst_n"
    # Default for most addresses
    if 0x00 <= dec <= 0x44 or 0x90 <= dec <= 0x92:
        return "rst_nlock"
    return "rst_other"


# ---------------------------------------------------------------------------
# SVG generation
# ---------------------------------------------------------------------------

def escape_xml(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_attr_svg(title, reg_map, attr_func, legend_items, footer_text=""):
    left_margin = 90
    top_margin = 90
    cell_w = 82
    cell_h = 46
    row_gap = 6
    addr_col_w = 80
    bit_label_h = 24

    addresses = sorted(reg_map.keys())

    # collapse consecutive fully-reserved addresses
    rows = []
    run_start = None
    for dec in addresses:
        if is_fully_reserved(reg_map[dec]):
            if run_start is None:
                run_start = dec
            continue
        if run_start is not None:
            rows.append(("range", run_start, dec - 1))
            run_start = None
        rows.append(("addr", dec))
    if run_start is not None:
        rows.append(("range", run_start, addresses[-1]))

    row_h = cell_h + row_gap
    content_h = len(rows) * row_h + bit_label_h + 40
    svg_w = left_margin + addr_col_w + 8 * cell_w + 40
    svg_h = content_h + top_margin + 150

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" style="background:{COLORS["bg"]}">')
    lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="{COLORS["bg"]}"/>')
    lines.append(f'<text x="{svg_w/2}" y="40" text-anchor="middle" font-size="22" font-weight="bold" fill="{COLORS["text"]}">{escape_xml(title)}</text>')

    bit_y = top_margin + 20
    for i in range(8):
        bit = 7 - i
        x = left_margin + addr_col_w + i * cell_w
        lines.append(f'<text x="{x + cell_w/2}" y="{bit_y}" text-anchor="middle" font-size="12" fill="{COLORS["muted"]}">[{bit}]</text>')

    for idx, row in enumerate(rows):
        y = top_margin + bit_label_h + 10 + idx * row_h
        if row[0] == "range":
            s, e = row[1], row[2]
            label = f"0x{s:02X} ~ 0x{e:02X} ({s} ~ {e})"
            lines.append(f'<text x="{left_margin + addr_col_w - 12}" y="{y + cell_h/2 + 5}" text-anchor="end" font-size="13" font-weight="600" fill="{COLORS["muted"]}">{escape_xml(label)}</text>')
            x = left_margin + addr_col_w
            w = 8 * cell_w - 1
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cell_h}" fill="{COLORS["chk_none"]}" stroke="{COLORS["border"]}" stroke-width="1" stroke-dasharray="4,3" rx="4"/>')
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 + 4}" text-anchor="middle" font-size="12" fill="{COLORS["muted"]}">⋯ 全 Reserved ⋯</text>')
            continue

        dec = row[1]
        hex_str = reg_map[dec][0]["hex"] if reg_map[dec] else f"0x{dec:02X}"
        lines.append(f'<text x="{left_margin + addr_col_w - 12}" y="{y + cell_h/2 + 5}" text-anchor="end" font-size="14" font-weight="600" fill="{COLORS["text"]}">{hex_str} ({dec})</text>')

        for entry in reg_map[dec]:
            msb, lsb = entry["msb"], entry["lsb"]
            width_bits = msb - lsb + 1
            start_col = 7 - msb
            x = left_margin + addr_col_w + start_col * cell_w
            w = width_bits * cell_w - 1
            attr = attr_func(dec, entry["name"])
            fill = COLORS.get(attr, COLORS["chk_none"])
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cell_h}" fill="{fill}" stroke="{COLORS["border"]}" stroke-width="1" rx="4"/>')

            name = entry["name"]
            display_name = name[:16] + "…" if len(name) > 16 else name
            font_size = 10 if width_bits >= 2 else 8
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 - 2}" text-anchor="middle" font-size="{font_size}" font-weight="500" fill="{COLORS["text"]}">{escape_xml(display_name)}</text>')
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 + 12}" text-anchor="middle" font-size="{font_size - 1}" fill="{COLORS["muted"]}">{escape_xml(entry["default"])}</text>')

    # Legend
    legend_y = svg_h - 90
    lines.append(f'<text x="{left_margin}" y="{legend_y - 10}" font-size="13" font-weight="600" fill="{COLORS["text"]}">图例</text>')
    lx = left_margin
    for label, color_key in legend_items:
        color = COLORS[color_key]
        lines.append(f'<rect x="{lx}" y="{legend_y}" width="14" height="14" fill="{color}" stroke="{COLORS["border"]}" rx="2"/>')
        lines.append(f'<text x="{lx + 20}" y="{legend_y + 11}" font-size="11" fill="{COLORS["text"]}">{escape_xml(label)}</text>')
        lx += 130

    # Footer
    if footer_text:
        lines.append(f'<text x="{svg_w/2}" y="{svg_h - 30}" text-anchor="middle" font-size="11" fill="{COLORS["muted"]}">{escape_xml(footer_text)}</text>')

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    src = Path("E:/project/HK1V11/LC_CPUWR_history/chip_sel1_register_address_map.md")
    rows = parse_table(src)
    reg_map = build_address_map(rows)

    out_dir = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Checksum participation
    svg_chk = generate_attr_svg(
        "LC_CPUWR 0714v1 参与 checksum 的地址",
        reg_map,
        lambda dec, name: checksum_status(dec),
        [
            ("参与 XOR 累加", "chk_full"),
            ("Checksum 控制", "chk_ctrl"),
            ("Frame end 边界", "chk_end"),
            ("不参与", "chk_none"),
        ],
        "0616_v2 起 0x09/0x0A/0x1D/0x1E 纳入 Seg1 checksum；Seg2 (0x20~0x38) 无 checksum"
    )
    (out_dir / "checksum_address_map.svg").write_text(svg_chk, encoding="utf-8")

    # 2. LSI protection
    svg_lsi = generate_attr_svg(
        "LC_CPUWR 0714v1 不受 LSI_PRTECT 保护的地址",
        reg_map,
        lambda dec, name: lsi_status(dec),
        [
            ("受 LSI_PRTECT 保护", "lsi_prot"),
            ("不受保护", "lsi_open"),
            ("密码寄存器 (0x30)", "lsi_pwd"),
        ],
        "0x00~0x1F、0x27、0x40~0x44 读回/输出不经过 LSI_PRTECT 掩码"
    )
    (out_dir / "lsi_unprotected_address_map.svg").write_text(svg_lsi, encoding="utf-8")

    # 3. Reset domain
    svg_rst = generate_attr_svg(
        "LC_CPUWR 0714v1 复位域分类",
        reg_map,
        lambda dec, name: reset_domain(dec, name),
        [
            ("N_RST_NLOCK", "rst_nlock"),
            ("N_RST", "rst_n"),
            ("RSTN_SCR_EN", "rst_scr"),
        ],
        "大部分字段由 N_RST_NLOCK 复位；0x30 TEST_PRTCT 由 N_RST 复位"
    )
    (out_dir / "reset_domain_address_map.svg").write_text(svg_rst, encoding="utf-8")

    print(f"Generated:\n  {out_dir / 'checksum_address_map.svg'}\n  {out_dir / 'lsi_unprotected_address_map.svg'}\n  {out_dir / 'reset_domain_address_map.svg'}")


if __name__ == "__main__":
    main()
