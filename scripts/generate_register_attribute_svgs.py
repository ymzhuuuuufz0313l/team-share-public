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

    # checksum - muted palette: normal addresses gray, only diffs/special colored
    "chk_full":   "#f1f5f9",   # participates in XOR accumulation (now muted gray)
    "chk_ctrl":   "#fed7aa",   # checksum control (0x07)
    "chk_end":    "#fef08a",   # frame end boundary (0x27)
    "chk_none":   "#e2e8f0",   # reserved/empty (slightly darker gray)
    "chk_sel0":   "#bfdbfe",   # chip_sel=0 field (soft blue)
    "chk_sel1":   "#bbf7d0",   # chip_sel=1 field (soft green)
    "chk_both":   "#f1f5f9",   # same in both chip_sel modes (gray)

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
    # 0810v1: reg147 (0x93 BCC_M) protected; reg160/161 (0xA0/0xA1 SDID/AEQ) NOT protected
    if dec == 0x93:
        return "lsi_prot"
    if dec == 0xA0 or dec == 0xA1:
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
    if 0x00 <= dec <= 0x44 or 0x90 <= dec <= 0x92 or dec in (0x93, 0xA0, 0xA1):
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


def entries_equal(entries0, entries1):
    """Return True if two address entry lists are identical in name/default/bits."""
    if len(entries0) != len(entries1):
        return False
    def key(e):
        return (e["msb"], e["lsb"], e["name"], e["default"])
    return sorted((key(e) for e in entries0), reverse=True) == sorted((key(e) for e in entries1), reverse=True)


def generate_checksum_dual_svg(title, map0, map1):
    """
    Generate checksum diagram. Addresses with identical chip_sel0/1 content
    are shown as a single row; differing addresses show two rows.
    """
    left_margin = 90
    top_margin = 100
    addr_col_w = 90
    label_col_w = 80
    cell_w = 80
    cell_h = 40
    row_gap = 8
    group_gap_single = 16
    group_gap_dual = 24
    bit_label_h = 24
    label_header_h = 22  # vertical space for address label

    # participating addresses (including control/frame-end for context)
    addresses = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06,
                 0x07, 0x08, 0x09, 0x0A,
                 0x1D, 0x1E, 0x1F,
                 0x27]

    svg_w = left_margin + addr_col_w + label_col_w + 8 * cell_w + 40

    # precompute which addresses differ
    diff_flags = {dec: not entries_equal(map0.get(dec, []), map1.get(dec, [])) for dec in addresses}

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="" viewBox="0 0 {svg_w}" style="background:{COLORS["bg"]}">')
    lines.append(f'<rect width="{svg_w}" height="" fill="{COLORS["bg"]}"/>')
    lines.append(f'<text x="{svg_w/2}" y="40" text-anchor="middle" font-size="22" font-weight="bold" fill="{COLORS["text"]}">{escape_xml(title)}</text>')

    # Bit labels
    bit_y = top_margin + 16
    for i in range(8):
        bit = 7 - i
        x = left_margin + addr_col_w + label_col_w + i * cell_w
        lines.append(f'<text x="{x + cell_w/2}" y="{bit_y}" text-anchor="middle" font-size="12" fill="{COLORS["muted"]}">[{bit}]</text>')

    def render_row(y, dec, mode_label, reg_map, base_color_key):
        # mode label (only for dual-row groups)
        if mode_label:
            lines.append(f'<text x="{left_margin + addr_col_w - 8}" y="{y + cell_h/2 + 4}" text-anchor="end" font-size="12" fill="{COLORS["muted"]}">{escape_xml(mode_label)}</text>')

        entries = reg_map.get(dec, [])
        # build per-bit map
        bit_fields = {b: None for b in range(8)}
        for e in entries:
            for b in range(e["lsb"], e["msb"] + 1):
                bit_fields[b] = e

        # merge contiguous same-field cells
        cells = []
        current = None
        start = None
        prev_bit = None
        current_entry = None
        for bit in range(7, -1, -1):
            e = bit_fields[bit]
            key = (e["name"] if e else None, e["default"] if e else None)
            if key != current:
                if current is not None:
                    cells.append((start, prev_bit, current_entry))
                current = key
                current_entry = e
                start = bit
            prev_bit = bit
        if current is not None:
            cells.append((start, prev_bit, current_entry))

        for msb, lsb, e in cells:
            width_bits = msb - lsb + 1
            start_col = 7 - msb
            x = left_margin + addr_col_w + label_col_w + start_col * cell_w
            w = width_bits * cell_w - 1
            has_field = e is not None

            # determine fill color: reserved/empty always gray; real fields colored
            if not has_field or e["name"] == "Reserved":
                fill = COLORS["chk_none"]
            elif dec == 0x07:
                fill = COLORS["chk_ctrl"]
            elif dec == 0x27:
                fill = COLORS["chk_end"]
            else:
                fill = COLORS[base_color_key]

            stroke = COLORS["border"]
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cell_h}" fill="{fill}" stroke="{stroke}" stroke-width="1" rx="4"/>')

            if has_field:
                name = e["name"]
                display_name = name[:14] + "…" if len(name) > 14 else name
                font_size = 9 if width_bits >= 2 else 8
                lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 - 3}" text-anchor="middle" font-size="{font_size}" font-weight="500" fill="{COLORS["text"]}">{escape_xml(display_name)}</text>')
                lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 + 11}" text-anchor="middle" font-size="{font_size - 1}" fill="{COLORS["muted"]}">{escape_xml(e["default"])}</text>')

    gy = top_margin + bit_label_h + 16
    for dec in addresses:
        is_diff = diff_flags[dec]
        hex_str = f"0x{dec:02X}"

        # address label always sits in a small header above the row(s)
        lines.append(f'<text x="{left_margin + addr_col_w - 10}" y="{gy + 16}" text-anchor="end" font-size="14" font-weight="600" fill="{COLORS["text"]}">{hex_str} ({dec})</text>')

        if is_diff:
            group_h = label_header_h + 2 * cell_h + row_gap + 8
            row0_y = gy + label_header_h + 4
            row1_y = row0_y + cell_h + row_gap
            render_row(row0_y, dec, "chip_sel=0", map0, "chk_sel0")
            render_row(row1_y, dec, "chip_sel=1", map1, "chk_sel1")
        else:
            group_h = label_header_h + cell_h + 8
            # single row: no mode label, color (chk_both) indicates same for both chip_sel modes
            render_row(gy + label_header_h + 4, dec, "", map0, "chk_both")

        gy += group_h + (group_gap_dual if is_diff else group_gap_single)

    svg_h = gy + 110
    # patch height attributes
    lines[1] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" style="background:{COLORS["bg"]}">'
    lines[2] = f'<rect width="{svg_w}" height="{svg_h}" fill="{COLORS["bg"]}"/>'

    # Legend
    legend_y = svg_h - 75
    lines.append(f'<text x="{left_margin}" y="{legend_y - 10}" font-size="13" font-weight="600" fill="{COLORS["text"]}">图例</text>')
    legend_items = [
        ("普通地址", "chk_both"),
        ("chip_sel=0", "chk_sel0"),
        ("chip_sel=1", "chk_sel1"),
        ("0x07 控制", "chk_ctrl"),
        ("0x27 frame end", "chk_end"),
    ]
    lx = left_margin
    for label, color_key in legend_items:
        color = COLORS[color_key]
        lines.append(f'<rect x="{lx}" y="{legend_y}" width="14" height="14" fill="{color}" stroke="{COLORS["border"]}" rx="2"/>')
        lines.append(f'<text x="{lx + 18}" y="{legend_y + 11}" font-size="10" fill="{COLORS["text"]}">{escape_xml(label)}</text>')
        lx += 145

    # Footer
    footer_text = "普通地址与 Reserved 位为灰色；蓝色=chip_sel=0 字段，绿色=chip_sel=1 字段；橙色=0x07 控制寄存器，黄色=0x27 frame end 边界。"
    lines.append(f'<text x="{svg_w/2}" y="{svg_h - 30}" text-anchor="middle" font-size="11" fill="{COLORS["muted"]}">{escape_xml(footer_text)}</text>')

    lines.append('</svg>')
    return "\n".join(lines)


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
    src0 = Path("E:/project/HK1V11/LC_CPUWR_history/chip_sel0_register_address_map.md")
    src1 = Path("E:/project/HK1V11/LC_CPUWR_history/chip_sel1_register_address_map.md")
    rows0 = parse_table(src0)
    rows1 = parse_table(src1)
    map0 = build_address_map(rows0)
    map1 = build_address_map(rows1)

    out_dir = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Checksum participation (dual chip_sel view)
    svg_chk = generate_checksum_dual_svg(
        "LC_CPUWR 0810v1 参与 checksum 的地址（chip_sel=0 / chip_sel=1 对照）",
        map0,
        map1,
    )
    (out_dir / "checksum_address_map.svg").write_text(svg_chk, encoding="utf-8")

    # 2. LSI protection
    svg_lsi = generate_attr_svg(
        "LC_CPUWR 0810v1 不受 LSI_PRTECT 保护的地址",
        map1,
        lambda dec, name: lsi_status(dec),
        [
            ("受 LSI_PRTECT 保护", "lsi_prot"),
            ("不受保护", "lsi_open"),
            ("密码寄存器 (0x30)", "lsi_pwd"),
        ],
        "0x00~0x1F、0x27、0x40~0x44、0xA0~0xA1 读回/输出不经过 LSI_PRTECT 掩码"
    )
    (out_dir / "lsi_unprotected_address_map.svg").write_text(svg_lsi, encoding="utf-8")

    # 3. Reset domain
    svg_rst = generate_attr_svg(
        "LC_CPUWR 0810v1 复位域分类",
        map1,
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
