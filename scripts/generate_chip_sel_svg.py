#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate SVG byte-lane register maps for chip_sel=0 and chip_sel=1
from LC_CPUWR_history markdown tables.
"""

import re
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Style configuration
# ---------------------------------------------------------------------------
COLORS = {
    "reserved":   "#e2e8f0",
    "control":    "#ccfbf1",   # teal
    "power":      "#fef3c7",   # amber
    "cdr":        "#e0e7ff",   # indigo
    "status":     "#e0f2fe",   # sky
    "chip1only":  "#fce7f3",   # pink
    "text":       "#1e293b",
    "muted":      "#64748b",
    "border":     "#94a3b8",
    "diff":       "#ef4444",
    "bg":         "#ffffff",
}

CATEGORY_MAP = {
    "SCREN": "control",
    "AVE_RGBW": "control",
    "PORSD": "control",
    "AVE_LAST": "control",
    "SD_CHOP": "control",
    "CH_SEL": "control",
    "SDC": "control",
    "DPLC_MODE": "control",
    "AVE_MODE": "control",
    "DPOLINV": "control",
    "DPLC_GROUP": "control",
    "CTRLF_CHECKSUM": "control",
    "reg_eq_rbc0": "cdr",
    "reg_eq_rbc1": "cdr",
    "STP_EN": "control",
    "TP_CONTROL": "control",
    "SD_CHOP_F": "control",
    "SR_PR": "power",
    "SR_PF": "power",
    "SR_NR": "power",
    "SR_NF": "power",
    "SMART_CS": "chip1only",
    "PWRC_TA": "power",
    "PWRC_TB": "power",
    "PWRC_P": "power",
    "PWRC_N": "power",
    "SP_S": "control",
    "VBK": "control",
    "PWRC_CTRL": "power",
    "VBK_EN": "control",
    "PWRC_N1": "power",
    "PWRC_P1": "power",
    "PWRC_N2": "power",
    "PWRC_P2": "power",
    "PWRC_N3": "power",
    "PWRC_P3": "power",
    "R_TESTO_SEL": "test",
    "TESTO_EN_OPT": "test",
    "PWRC_TSEL": "power",
    "R_MON_DC_VOL": "cdr",
    "R_UTC": "cdr",
    "R_FRM_CHK_MODE": "control",
    "HIZ_SEL": "control",
    "SRE": "control",
    "SRER_P": "control",
    "SREF_P": "control",
    "SRER_N": "control",
    "SREF_N": "control",
    "STR": "control",
    "CVBP_SEPARATE": "control",
    "R_CH12_HIZ": "control",
    "R_CH34_HIZ": "control",
    "reg_ana_test_sel": "test",
    "reg_cr_done_cnt": "cdr",
    "reg_cdr_rlpf": "cdr",
    "reg_cdr_icp": "cdr",
    "reg_icp_bias_tune": "cdr",
    "reg_kvco_ctrl": "cdr",
    "Skip_frame_count": "control",
    "Level_Skip_frame": "control",
    "ACS_EN": "control",
    "AABB": "control",
    "R_BAC": "control",
    "DBCO_DRV": "control",
    "DBC_VBK_ON": "control",
    "DBC": "control",
    "R_DBC_WIDTH_OPT": "control",
    "R_MASK_6PIX": "control",
    "CP_VBP1R": "control",
    "CP_VBP2R": "control",
    "OVC_POS": "control",
    "OVC_NEG": "control",
    "CP_VBN1L": "control",
    "CP_VBN2L": "control",
    "DCBIAS_CHOP": "control",
    "DCBIAS_TOT": "control",
    "DC_MON_SEL": "test",
    "BGR_SEL": "control",
    "BGR_TRIM": "control",
    "LENB_SHIFT": "control",
    "CN_VBP1R": "control",
    "CN_VBP2R": "control",
    "R_PTAT_EN": "control",
    "PWRC_LS": "power",
    "TP_F_AHEAD": "test",
    "CN_VBN1L": "control",
    "CN_VBN2L": "control",
    "HIZ_MIN_SEL": "control",
    "R_HIZ_MIN_VAL": "control",
    "LD_D_OPT": "control",
    "TEST_PRTCT": "test",
    "reg_lane_ctrl": "control",
    "reg_fbdiv_clk_sel": "cdr",
    "reg_pin_eq": "control",
    "CG_OFF": "control",
    "reg_lane_ck_inv_en": "control",
    "regr_lane_pll_done": "status",
    "regr_lane_pll_fine_lock": "status",
    "regr_lane_pll_fast_lock": "status",
    "regr_lane_pll_lock_flag": "status",
    "regr_lane_vctrl_underflow": "status",
    "regr_lane_vctrl_overflow": "status",
    "reg_eq_bias_tune": "cdr",
    "reg_vos_ctrl": "control",
    "reg_vos_ad_en": "control",
    "UTC_long01_frame": "cdr",
    "UTC_header_cnt": "cdr",
    "UTC_header_frame": "cdr",
    "FSYNC": "control",
    "POL": "control",
    "POLC": "control",
    "H4INV": "control",
    "LD_R": "control",
    "LD_F": "control",
    "CS": "control",
    "BKDU": "control",
    "LOAD": "control",
    "POL2": "control",
    "reg_fast_lock_icp": "cdr",
    "reg_fast_lock_rlpf": "cdr",
    "reg_fine_lock_icp": "cdr",
    "reg_fine_lock_rlpf": "cdr",
    "reg_lock_wd_sel": "cdr",
    "reg_pbs_flt": "cdr",
}


def get_category(name: str) -> str:
    # strip bus index like [3:0]
    base = re.sub(r"\[.*\]", "", name).strip()
    # strip numeric suffix from array names if not exact match
    if base in CATEGORY_MAP:
        return CATEGORY_MAP[base]
    # try without trailing digits
    base2 = re.sub(r"\d+$", "", base)
    if base2 in CATEGORY_MAP:
        return CATEGORY_MAP[base2]
    return "reserved" if "Reserved" in name else "control"


def parse_table(path: Path):
    rows = []
    in_table = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("|") and "地址(DEC)" in line:
                in_table = True
                continue
            if in_table and line.startswith("|"):
                parts = [p.strip() for p in line.strip("|").split("|")]
                if len(parts) < 6:
                    continue
                # skip header separator
                if parts[0] == "地址(DEC)":
                    continue
                try:
                    dec = int(parts[0])
                    hex_addr = parts[1]
                    bits = parts[2]
                    name = parts[3]
                    default = parts[4]
                    access = parts[5]
                    rows.append({
                        "dec": dec,
                        "hex": hex_addr,
                        "bits": bits,
                        "name": name,
                        "default": default,
                        "access": access,
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
    """Group rows by address and merge contiguous fields."""
    addr_rows = defaultdict(list)
    for r in rows:
        addr_rows[r["dec"]].append(r)

    addresses = sorted(addr_rows.keys())
    result = {}
    for dec in addresses:
        # sort by msb descending so [7:5] comes before [4:0]
        entries = []
        for r in addr_rows[dec]:
            rng = bit_range(r["bits"])
            if rng is None:
                continue
            msb, lsb = rng
            entries.append({
                "dec": dec,
                "hex": r["hex"],
                "msb": msb,
                "lsb": lsb,
                "name": r["name"],
                "default": r["default"],
                "access": r["access"],
                "category": get_category(r["name"]),
            })
        entries.sort(key=lambda x: -x["msb"])
        result[dec] = entries
    return result


def normalize_default(d):
    """Return a comparable string for default value."""
    return d.strip().replace("b'", "'").replace("b0", "0").replace("b1", "1")


def compute_differences(map0, map1):
    """Return set of (dec, msb, lsb) cells that differ between chip_sel0 and chip_sel1."""
    diffs = set()
    for dec in set(map0.keys()) | set(map1.keys()):
        cells0 = {(e["msb"], e["lsb"]): e for e in map0.get(dec, [])}
        cells1 = {(e["msb"], e["lsb"]): e for e in map1.get(dec, [])}
        for key in set(cells0.keys()) | set(cells1.keys()):
            e0 = cells0.get(key)
            e1 = cells1.get(key)
            if e0 is None or e1 is None:
                diffs.add((dec, key[0], key[1]))
            elif normalize_default(e0["default"]) != normalize_default(e1["default"]):
                diffs.add((dec, key[0], key[1]))
            elif e0["name"] != e1["name"]:
                diffs.add((dec, key[0], key[1]))
    return diffs


def escape_xml(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def generate_svg(title: str, reg_map, diffs=None, highlight_label=""):
    diffs = diffs or set()

    # Layout
    left_margin = 90
    top_margin = 90
    cell_w = 82
    cell_h = 46
    row_gap = 6
    addr_col_w = 80
    bit_label_h = 24

    addresses = sorted(reg_map.keys())

    def is_fully_reserved(dec):
        entries = reg_map.get(dec, [])
        if not entries:
            return True
        # check if single entry [7:0] is Reserved
        if len(entries) == 1 and entries[0]["name"] == "Reserved" and entries[0]["msb"] == 7 and entries[0]["lsb"] == 0:
            return True
        return False

    def make_rows():
        rows = []
        run_start = None
        for dec in addresses:
            if is_fully_reserved(dec):
                if run_start is None:
                    run_start = dec
                continue
            if run_start is not None:
                rows.append(("range", run_start, dec - 1))
                run_start = None
            rows.append(("addr", dec))
        if run_start is not None:
            rows.append(("range", run_start, addresses[-1]))
        return rows

    rows = make_rows()
    row_h = cell_h + row_gap
    content_h = len(rows) * row_h + bit_label_h + 40
    svg_w = left_margin + addr_col_w + 8 * cell_w + 40
    svg_h = content_h + top_margin + 140  # extra for title/legend/footer

    # Legend
    legend_items = [
        ("Reserved", COLORS["reserved"]),
        ("控制/配置", COLORS["control"]),
        ("电源/PWRC", COLORS["power"]),
        ("CDR/PLL/模拟", COLORS["cdr"]),
        ("状态/只读", COLORS["status"]),
        ("chip_sel=1 专用", COLORS["chip1only"]),
    ]

    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" style="background:{COLORS["bg"]}">')
    lines.append(f'<rect width="{svg_w}" height="{svg_h}" fill="{COLORS["bg"]}"/>')

    # Title
    lines.append(f'<text x="{svg_w/2}" y="40" text-anchor="middle" font-size="22" font-weight="bold" fill="{COLORS["text"]}">{escape_xml(title)}</text>')

    # Bit labels
    bit_y = top_margin + 20
    for i in range(8):
        bit = 7 - i
        x = left_margin + addr_col_w + i * cell_w
        lines.append(f'<text x="{x + cell_w/2}" y="{bit_y}" text-anchor="middle" font-size="12" fill="{COLORS["muted"]}">[{bit}]</text>')

    # Rows
    for idx, row in enumerate(rows):
        y = top_margin + bit_label_h + 10 + idx * row_h

        if row[0] == "range":
            start_dec, end_dec = row[1], row[2]
            start_hex = f"0x{start_dec:02X}"
            end_hex = f"0x{end_dec:02X}"
            label = f"{start_hex} ~ {end_hex} ({start_dec} ~ {end_dec})"
            # collapsed reserved row
            lines.append(f'<text x="{left_margin + addr_col_w - 12}" y="{y + cell_h/2 + 5}" text-anchor="end" font-size="13" font-weight="600" fill="{COLORS["muted"]}">{escape_xml(label)}</text>')
            x = left_margin + addr_col_w
            w = 8 * cell_w - 1
            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cell_h}" fill="{COLORS["reserved"]}" stroke="{COLORS["border"]}" stroke-width="1" stroke-dasharray="4,3" rx="4"/>')
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 + 4}" text-anchor="middle" font-size="12" fill="{COLORS["muted"]}">⋯ 全 Reserved ⋯</text>')
            continue

        dec = row[1]
        hex_str = reg_map[dec][0]["hex"] if reg_map[dec] else f"0x{dec:02X}"
        # address label
        lines.append(f'<text x="{left_margin + addr_col_w - 12}" y="{y + cell_h/2 + 5}" text-anchor="end" font-size="14" font-weight="600" fill="{COLORS["text"]}">{hex_str} ({dec})</text>')

        # note for chip_sel1 special addresses
        note_text = ""
        if highlight_label and dec in (0x09, 0x0A, 0x1F):
            note_text = highlight_label

        for entry in reg_map[dec]:
            msb, lsb = entry["msb"], entry["lsb"]
            width_bits = msb - lsb + 1
            start_col = 7 - msb
            x = left_margin + addr_col_w + start_col * cell_w
            w = width_bits * cell_w - 1
            cat = entry["category"]
            fill = COLORS.get(cat, COLORS["control"])
            is_diff = (dec, msb, lsb) in diffs
            stroke = COLORS["diff"] if is_diff else COLORS["border"]
            stroke_w = 2.5 if is_diff else 1

            lines.append(f'<rect x="{x}" y="{y}" width="{w}" height="{cell_h}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" rx="4"/>')

            # text: field name and default
            name = entry["name"]
            default = entry["default"]
            # abbreviate very long names
            display_name = name[:16] + "…" if len(name) > 16 else name

            # choose font size based on width
            font_size = 10 if width_bits >= 2 else 8
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 - 2}" text-anchor="middle" font-size="{font_size}" font-weight="500" fill="{COLORS["text"]}">{escape_xml(display_name)}</text>')
            lines.append(f'<text x="{x + w/2}" y="{y + cell_h/2 + 12}" text-anchor="middle" font-size="{font_size - 1}" fill="{COLORS["muted"]}">{escape_xml(default)}</text>')

            if is_diff:
                # diff star
                star_r = 5
                star_x = x + w - star_r - 3
                star_y = y + star_r + 3
                lines.append(f'<circle cx="{star_x}" cy="{star_y}" r="{star_r}" fill="{COLORS["diff"]}"/>')
                lines.append(f'<text x="{star_x}" y="{star_y + 3}" text-anchor="middle" font-size="8" fill="white" font-weight="bold">★</text>')

        if note_text:
            nx = left_margin + addr_col_w + 8 * cell_w + 8
            lines.append(f'<text x="{nx}" y="{y + cell_h/2 + 4}" font-size="11" fill="{COLORS["diff"]}" font-weight="600">{escape_xml(note_text)}</text>')

    # Legend
    legend_y = svg_h - 80
    lines.append(f'<text x="{left_margin}" y="{legend_y - 10}" font-size="13" font-weight="600" fill="{COLORS["text"]}">图例</text>')
    lx = left_margin
    for label, color in legend_items:
        lines.append(f'<rect x="{lx}" y="{legend_y}" width="14" height="14" fill="{color}" stroke="{COLORS["border"]}" rx="2"/>')
        lines.append(f'<text x="{lx + 20}" y="{legend_y + 11}" font-size="11" fill="{COLORS["text"]}">{escape_xml(label)}</text>')
        lx += 110

    # Diff marker legend
    lines.append(f'<rect x="{lx}" y="{legend_y}" width="14" height="14" fill="{COLORS["control"]}" stroke="{COLORS["diff"]}" stroke-width="2" rx="2"/>')
    lines.append(f'<text x="{lx + 20}" y="{legend_y + 11}" font-size="11" fill="{COLORS["text"]}">{escape_xml("与 chip_sel=0 不同")}</text>')

    # Footer
    footer_y = svg_h - 30
    lines.append(f'<text x="{svg_w/2}" y="{footer_y}" text-anchor="middle" font-size="11" fill="{COLORS["muted"]}">0714v1+：chip_sel=1 的 0x09/0x0A/0x1F 默认值由 LC_REG_MAPPING 写标志 + 回拼字节实现</text>')

    lines.append('</svg>')
    return "\n".join(lines)


def main():
    base = Path(__file__).parent
    src0 = Path("E:/project/HK1V11/LC_CPUWR_history/chip_sel0_register_address_map.md")
    src1 = Path("E:/project/HK1V11/LC_CPUWR_history/chip_sel1_register_address_map.md")

    rows0 = parse_table(src0)
    rows1 = parse_table(src1)

    map0 = build_address_map(rows0)
    map1 = build_address_map(rows1)

    diffs = compute_differences(map0, map1)

    svg0 = generate_svg("chip_sel = 0 寄存器默认字节映射", map0)
    svg1 = generate_svg("chip_sel = 1 寄存器默认字节映射", map1, diffs, "LC_REG_MAPPING 回拼")

    out0 = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images/chip_sel0_register_map.svg")
    out1 = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images/chip_sel1_register_map.svg")

    out0.write_text(svg0, encoding="utf-8")
    out1.write_text(svg1, encoding="utf-8")

    print(f"Generated: {out0}")
    print(f"Generated: {out1}")
    print(f"Diff cells: {len(diffs)}")


if __name__ == "__main__":
    main()
