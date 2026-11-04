#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_postpt_tables_anim.py

Deterministic generator: rebuild the postPT setup/hold summary tables as
ANIMATED SVG, reading data directly from the report CSV (zero manual entry).

Style matches the reference PNG (2519x1169):
  - full-width deep teal-green title band, white text (title left / subtitle right)
  - green column-header row
  - zebra data rows (white / #f4f6f4) with thin light-gray grid
  - values right-aligned monospace (Consolas family); zero = green, non-zero = dark
Animation (pure CSS, no <script>, no external resources):
  - row reveal: each data row <g class="row"> stagger 0.025s, 0.4s fade + 4px slide-up;
    title/header band <g class="head"> delay 0
  - breathing (persistent, infinite): non-zero cells opacity 1<->0.55, 2.8s,
    per-cell staggered delay; zero cells stay static
  - final settled state == static table
Six built-in validations run and printed on every invocation.

Usage (run 4 times for the 4 outputs):
  python gen_postpt_tables_anim.py --metric setup --mode 2P
  python gen_postpt_tables_anim.py --metric hold   --mode 2P
  python gen_postpt_tables_anim.py --metric setup --mode 1P
  python gen_postpt_tables_anim.py --metric hold   --mode 1P
"""
import argparse
import csv
import hashlib
import os
import sys
import xml.etree.ElementTree as ET

BASE = r"E:\project\team-share-public\synthesis-integration-flow-guide"
DATA_DIR = os.path.join(BASE, "server-reports", "postpt_summary")
OUT_DIR = os.path.join(BASE, "image", "anim")

# ---------------------------------------------------------------------------
# Layout constants (match reference PNG 2519x1169)
# ---------------------------------------------------------------------------
W, H = 2519, 1169
M = 25                 # left/right margin
HEADER_H = 58          # title band height
COLHEAD_H = 54         # column-header row height
DATA_TOP = HEADER_H + COLHEAD_H      # 112
N_COLS = 10            # corner columns
FIRST_COL_RIGHT = 548  # boundary: metric col | first data col
DATA_LEFT = FIRST_COL_RIGHT
DATA_RIGHT = W - M     # 2494
COL_W = (DATA_RIGHT - DATA_LEFT) / N_COLS   # 194.6

# Colors
C_BAND    = "#157a6a"
C_COLHEAD = "#2e8b6a"
C_ZEBRA_A = "#ffffff"
C_ZEBRA_B = "#f4f6f4"
C_GRID    = "#d7dbd7"
C_ZERO    = "#1a7a3c"
C_NONZERO = "#2d2d2d"
C_LABEL   = "#2d2d2d"
C_WHITE   = "#ffffff"

FONT = "Consolas, 'SFMono-Regular', Menlo, 'Courier New', monospace"

# Font sizes
F_TITLE = 30
F_SUB   = 26
F_COL   = 19
F_DATA  = 19

# Animation params
ROW_STAGGER    = 0.025   # per data row, seconds
BREATH_PERIOD  = 2.8     # seconds
BREATH_STAGGER = 0.05    # (row+col) * this, seconds


def F(x):
    """Deterministic coordinate/number formatting (strip trailing zeros)."""
    s = f"{x:.3f}"
    return s.rstrip("0").rstrip(".")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_csv(path):
    """Return (corners, data):
    corners: list of 10 corner names (from header row, even indices 2..20)
    data   : list of (label, [10 biggest-violation verbatim strings])
    """
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.reader(f) if r and any(c.strip() for c in r)]
    header = rows[0]
    corners = [header[i] for i in range(2, len(header), 2)]
    data = []
    for r in rows[2:]:
        label = r[0]
        # biggest-violation value per corner sits at even indices 2,4,...,20
        vals = [r[i] for i in range(2, len(r), 2)]
        data.append((label, vals))
    return corners, data


def build_svg(corners, data, metric, mode):
    n_rows = len(data)
    row_h = (H - DATA_TOP) / n_rows
    # vertical gridline x positions (metric|data boundary + between data cols + right edge)
    vbounds = [FIRST_COL_RIGHT] + [DATA_LEFT + k * COL_W for k in range(1, N_COLS)] + [DATA_RIGHT]

    left_title = f"report_{metric}.csv ({mode})"
    kind = "max" if metric == "setup" else "min"
    right_title = f"{metric}/{kind} 路径违例总表"

    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">'
    )
    p.append("<style><![CDATA[")
    p.append(".head{opacity:0;animation:rowIn 0.4s ease forwards;}")
    p.append(".row{opacity:0;animation:rowIn 0.4s ease forwards;}")
    p.append(f".chg{{animation:breath {F(BREATH_PERIOD)}s ease-in-out infinite;}}")
    p.append("@keyframes rowIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}")
    p.append("@keyframes breath{0%{opacity:1;}50%{opacity:0.55;}100%{opacity:1;}}")
    p.append("]]></style>")

    # white canvas
    p.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')

    # ---- title band (head, delay 0) ----
    p.append('<g class="head">')
    p.append(f'<rect x="0" y="0" width="{W}" height="{F(HEADER_H)}" fill="{C_BAND}"/>')
    ty = F(HEADER_H * 0.64)
    p.append(f'<text x="{M}" y="{ty}" font-size="{F_TITLE}" font-weight="bold" fill="{C_WHITE}">{esc(left_title)}</text>')
    p.append(f'<text x="{F(DATA_RIGHT)}" y="{ty}" font-size="{F_SUB}" fill="{C_WHITE}" text-anchor="end">{esc(right_title)}</text>')
    p.append("</g>")

    # ---- column-header row (head, delay 0) ----
    p.append('<g class="head">')
    p.append(f'<rect x="0" y="{F(HEADER_H)}" width="{W}" height="{F(COLHEAD_H)}" fill="{C_COLHEAD}"/>')
    cy = F(HEADER_H + COLHEAD_H * 0.62)
    p.append(f'<text x="{M + 10}" y="{cy}" font-size="{F_COL}" fill="{C_WHITE}">metric</text>')
    for i, name in enumerate(corners):
        cx = F(DATA_LEFT + (i + 0.5) * COL_W)
        p.append(f'<text x="{cx}" y="{cy}" font-size="{F_COL}" fill="{C_WHITE}" text-anchor="middle" class="chn">{esc(name)}</text>')
    p.append("</g>")

    # ---- data rows ----
    for r, (label, vals) in enumerate(data):
        top = DATA_TOP + r * row_h
        zebra = C_ZEBRA_A if r % 2 == 0 else C_ZEBRA_B
        rdelay = r * ROW_STAGGER
        p.append(f'<g class="row" style="animation-delay:{F(rdelay)}s">')
        # zebra background (full width)
        p.append(f'<rect x="0" y="{F(top)}" width="{W}" height="{F(row_h)}" fill="{zebra}"/>')
        # row label
        ly = F(top + row_h * 0.64)
        p.append(f'<text x="{M + 10}" y="{ly}" font-size="{F_DATA}" fill="{C_LABEL}" class="lbl">{esc(label)} (biggest violation)</text>')
        # value cells
        for c, v in enumerate(vals):
            is_zero = (float(v) == 0.0)
            color = C_ZERO if is_zero else C_NONZERO
            cls = "val" if is_zero else "val chg"
            style = "" if is_zero else f' style="animation-delay:{F((r + c) * BREATH_STAGGER)}s"'
            rx = F(DATA_LEFT + (c + 1) * COL_W - 14)
            p.append(f'<text x="{rx}" y="{ly}" font-size="{F_DATA}" fill="{color}" text-anchor="end" class="{cls}"{style}>{esc(v)}</text>')
        # grid: bottom horizontal line + vertical segments for this row
        gy = F(top + row_h)
        p.append(f'<line x1="{M}" y1="{gy}" x2="{F(DATA_RIGHT)}" y2="{gy}" stroke="{C_GRID}" stroke-width="1"/>')
        for x in vbounds:
            p.append(f'<line x1="{F(x)}" y1="{F(top)}" x2="{F(x)}" y2="{F(top + row_h)}" stroke="{C_GRID}" stroke-width="1"/>')
        p.append("</g>")

    p.append("</svg>")
    return "\n".join(p)


def validate(svg, data):
    """Run validations 1-5; return list of (name, ok, detail)."""
    res = []
    # 1. XML well-formed
    try:
        root = ET.fromstring(svg)
        res.append(("1. XML well-formed", True, ""))
    except ET.ParseError as e:
        res.append(("1. XML well-formed", False, str(e)))
        return res

    # 2. no <script>
    has_script = "<script" in svg.lower()
    res.append(("2. no <script>", (not has_script), ""))

    # 3. @keyframes present
    has_kf = "@keyframes" in svg
    res.append(("3. @keyframes present", has_kf, ""))

    # 4. transcription: every numeric cell in SVG == source CSV value (count & values equal)
    transcribed = []
    for el in root.iter():
        cls = (el.get("class") or "").split()
        if "val" in cls:
            transcribed.append((el.text or "").strip())
    source_vals = []
    for _label, vals in data:
        source_vals.extend(vals)
    ok4 = (transcribed == source_vals)
    res.append(("4. transcription (count & values == CSV)", ok4,
                f"svg_cells={len(transcribed)} src_vals={len(source_vals)}"))

    # 5. row count == source data rows
    # (match by class only: SVG namespace would make tag == "{ns}g")
    row_count = sum(1 for el in root.iter() if (el.get("class") or "") == "row")
    ok5 = (row_count == len(data))
    res.append(("5. row count == source rows", ok5,
                f"svg_rows={row_count} src_rows={len(data)}"))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--metric", required=True, choices=["setup", "hold"])
    ap.add_argument("--mode", required=True, choices=["2P", "1P"])
    args = ap.parse_args()
    metric, mode = args.metric, args.mode

    csv_path = os.path.join(DATA_DIR, "POST_PT_" + mode, f"report_{metric}.csv")
    prefix = "30" if mode == "2P" else "31"
    out_name = f"{prefix}_postpt_{metric}_{mode.lower()}.svg"
    out_path = os.path.join(OUT_DIR, out_name)

    corners, data = read_csv(csv_path)
    assert len(corners) == N_COLS, f"expected {N_COLS} corners, got {len(corners)}"
    for label, vals in data:
        assert len(vals) == N_COLS, f"row '{label}': expected {N_COLS} values, got {len(vals)}"
        for v in vals:
            float(v)  # ensure every value is numeric

    # deterministic double build -> idempotency (validation 6)
    svg = build_svg(corners, data, metric, mode)
    svg2 = build_svg(corners, data, metric, mode)
    md5_a = hashlib.md5(svg.encode("utf-8")).hexdigest()
    md5_b = hashlib.md5(svg2.encode("utf-8")).hexdigest()

    res = validate(svg, data)
    res.append(("6. idempotent (2 builds, md5 equal)", md5_a == md5_b, f"{md5_a} == {md5_b}"))

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(svg)
    with open(out_path, "rb") as f:
        md5_file = hashlib.md5(f.read()).hexdigest()

    print("=" * 64)
    print(f"[{out_name}]  source: {os.path.relpath(csv_path, BASE)}")
    print(f"  output : {out_path}")
    for name, ok, detail in res:
        tag = "PASS" if ok else "FAIL"
        extra = f"  ({detail})" if detail else ""
        print(f"  [{tag}] {name}{extra}")
    print(f"  file md5: {md5_file}")
    print("=" * 64)
    if not all(ok for _n, ok, _d in res):
        sys.exit(1)


if __name__ == "__main__":
    main()
