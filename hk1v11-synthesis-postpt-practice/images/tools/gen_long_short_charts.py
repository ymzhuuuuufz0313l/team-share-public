# -*- coding: utf-8 -*-
"""gen_long_short_charts.py — §4.7 长短编码模式对比图（ch08-powerpro）。

生成（数据驱动，数值零手写，全部来自 longcode_{4g,3g}_data.json）：
  images/power_module_compare_long_short.svg        模块级对比条形图（静态 = 事实源）
  images/anim/power_module_compare_long_short.svg   动画版（同几何，注入 kit CSS）
  images/power_composition_donut_long_short.svg     长编码@4G 功耗组成环形图（静态）
  images/anim/power_composition_donut_long_short.svg 动画版

口径（与 §4.5/§4.6 同族，_draft_s47_longcode_compare.md 骨架）：
  * 模块图：LC_CHPI_DECODE 下 LONG/SHORT_ENCODING 的叶子子块（组级口径），
    三系列 = 长编码@4G（1118 包）/ 长编码@3G（1118 包）/ 短编码参照（1117 包 @4G，同频），
    行序按 Δ(长@4G − 短@4G) 降序（同频 4G 对比）。
  * 环形图：长编码@4G top total 组成（LONG 组 / SHORT 组 / 其他），
    断言 Σ片 == 中心值（QA 门 6）。

用法：
  python gen_long_short_charts.py            # 生成/幂等更新 4 个 SVG
  python gen_long_short_charts.py --check    # 只读：与目标逐字节比对，漂移 exit 1

PNG 快照（images/*.png）由 Edge headless 截图产出（blueprint-ui-style skill 流程），不入本脚本。
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent              # .../images/tools
SITE_ROOT = HERE.parents[1]                         # 站点根
DATA_DIR = Path(r"E:\project\HK1V11\script\_power1117")
J4G = DATA_DIR / "longcode_4g_data.json"
J3G = DATA_DIR / "longcode_3g_data.json"

# ---- 站点色板（blueprint-ui-style：纸底/墨/琥珀/深青/蓝；呈现层常量）----
PAPER, SURFACE = "#f4f1ea", "#fffdf7"
INK, MUTED, GRID, BORDER = "#1c2534", "#5b6675", "#ddd6c8", "#c9bfa8"
C_LONG4G, C_LONG3G, C_SHORT = "#0e7490", "#b45309", "#1d4ed8"
C_REST = "#a89f8c"

FONT = 'text{font-family:ui-monospace,Consolas,"Microsoft YaHei",sans-serif;}'

import datetime
TAIL_SIG = "<!-- ymzhu %s -->" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

# kit CSS（Motion Kit v4 §2 逐字嵌入，与 make_anim_power_compare_hk11.py 同源；
# 校验硬门要求 flowdot/pulse/sweep/rmfix 签名齐全，缺一即 FAIL）
ANIM_CSS = "\n".join([
    ".row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}",
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}",
    "@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}",
    ".pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}",
    "@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}",
    ".pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}",
    "@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}",
    ".sweepband{opacity:.85;animation:sweepMove 8s linear infinite}",
    "@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}",
    ".dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}",
    "@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}",
    ".march{animation:march 1.5s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".cellwave{animation:wave 2.6s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".step{animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}",
])


def load():
    d4 = json.loads(J4G.read_text(encoding="utf-8"))["cases"]
    d3 = json.loads(J3G.read_text(encoding="utf-8"))["cases"]
    return d4["long_4g"], d3["long_3g"], d4["short_ref_4g"]   # F3：短码@4G 参照（同频）


def _leaf(blocks, group):
    """组内叶子子块：{块名末段: µW}（剔除组级合计键）。"""
    out = {}
    for k, v in blocks.items():
        parts = k.split(".")
        if len(parts) >= 2 and parts[-2] == group:      # 叶子（组级键的倒数第二段是 LC_CHPI_DECODE）
            out[parts[-1].replace(group + "_", "", 1)] = v["total"] if isinstance(v, dict) else v
    return out


def vfmt(v):
    """数值标签：整数（含 0）不带小数尾，非整数两位小数。"""
    return "%d" % round(v) if abs(v - round(v)) < 1e-9 else "%.2f" % v


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ================================================================ 模块对比条形图
def build_bar_svg(l4, l3, sr, anim):
    ROWS = []   # (label, group, v4, v3, vs)
    for group, disp in (("LONG_ENCODING", "LONG"), ("SHORT_ENCODING", "SHORT")):
        for blk in sorted(set(_leaf(l4["blocks"], group))
                          | set(_leaf(sr["blocks"], group))):
            ROWS.append((disp, blk,
                         _leaf(l4["blocks"], group).get(blk, 0.0),
                         _leaf(l3["blocks"], group).get(blk, 0.0),
                         _leaf(sr["blocks"], group).get(blk, 0.0)))
    ROWS.sort(key=lambda r: r[2] - r[4], reverse=True)   # Δ(长4G − 短@4G) 降序

    W, H = 1260, 744
    X0, AXLEN, TICK = 268, 932, 1000
    AXIS_MAX = 6200
    SCALE = AXLEN / AXIS_MAX
    TOP_Y, PITCH, BAR_H, GAP = 122, 60, 14, 5
    t4 = l4["top_total_uW"] / 1000.0
    t3 = l3["top_total_uW"] / 1000.0
    ts = sr["top_total_uW"] / 1000.0

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}">']
    o.append("<style>" + FONT + "</style>")
    if anim:
        o.append("<style>\n" + ANIM_CSS + "\n</style>")
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
    # 标题条
    o.append(f'<g class="head"><rect x="0" y="0" width="{W}" height="42" fill="{INK}"/>'
             f'<text x="14" y="21" dominant-baseline="central" fill="#f4f1ea" font-size="15" '
             f'font-weight="bold">HK1V11 长短编码模块功耗对比 — LONG / SHORT_ENCODING 叶子子块（µW）</text>'
             f'<text x="{W - 14}" y="21" text-anchor="end" dominant-baseline="central" '
             f'fill="#e8c59e" font-size="12">top total：长@4G {vfmt(t4)} mW · 长@3G {vfmt(t3)} mW · 短参照@4G {vfmt(ts)} mW</text></g>')
    # 轴 + 网格
    g = [f'<g class="fade">']
    for tk in range(0, AXIS_MAX, TICK):
        x = X0 + tk * SCALE
        g.append(f'<line x1="{x:.1f}" y1="{TOP_Y - 18}" x2="{x:.1f}" y2="{TOP_Y + PITCH * len(ROWS) - 6}" '
                 f'stroke="{GRID}" stroke-width="1"/>'
                 f'<text x="{x:.1f}" y="{TOP_Y - 26}" text-anchor="middle" fill="{MUTED}" font-size="11">{tk}</text>')
    g.append(f'<line x1="{X0}" y1="{TOP_Y - 18}" x2="{X0}" y2="{TOP_Y + PITCH * len(ROWS) - 6}" '
             f'stroke="{BORDER}" stroke-width="1.5"/>')
    g.append("</g>")
    o.extend(g)
    # 行
    for i, (grp, blk, v4, v3, vs) in enumerate(ROWS):
        y0 = TOP_Y + PITCH * i
        cls = f' class="row" style="animation-delay:{0.15 + 0.08 * i:.2f}s"' if anim else ""
        o.append(f"<g{cls}>")
        o.append(f'<text x="{X0 - 14}" y="{y0 + 22}" text-anchor="end" dominant-baseline="central" '
                 f'fill="{INK}" font-size="13" font-weight="bold">{esc(grp)} · {esc(blk)}</text>')
        wcls = ' class="cellwave" style="animation-delay:%.1fs"' % (-0.12 * i) if anim else ""
        o.append(f"<g{wcls}>")
        for j, (v, col, tag) in enumerate(((v4, C_LONG4G, "长@4G"),
                                           (v3, C_LONG3G, "长@3G"),
                                           (vs, C_SHORT, "短参照"))):
            y = y0 + j * (BAR_H + GAP)
            w = v * SCALE
            o.append(f'<rect x="{X0}" y="{y}" width="{w:.1f}" height="{BAR_H}" rx="2" '
                     f'fill="{col}" fill-opacity="0.9"/>')
            if w > 1:
                o.append(f'<text x="{X0 + w + 8:.1f}" y="{y + BAR_H / 2}" dominant-baseline="central" '
                         f'fill="{col}" font-size="11">{vfmt(v)}</text>')
            else:
                o.append(f'<text x="{X0 + 8}" y="{y + BAR_H / 2}" dominant-baseline="central" '
                         f'fill="{MUTED}" font-size="11">{vfmt(v)}</text>')
        o.append("</g>")
        d = v4 - vs
        pcls = (' class="pulse" style="animation-delay:%gs"' % (-0.6 * i)) if (anim and i < 3) else ""
        if pcls:
            o.append(f"<g{pcls}>")
        o.append(f'<text x="{W - 6}" y="{y0 + 22}" text-anchor="end" dominant-baseline="central" '
                 f'fill="{MUTED}" font-size="11">Δ {d:+,.0f}</text>')
        if pcls:
            o.append("</g>")
        o.append("</g>")
    # 图例
    ly = H - 26
    lg = [f'<g class="fade">']
    lx = 268
    for col, tag in ((C_LONG4G, "长编码 @4G（1118）"), (C_LONG3G, "长编码 @3G（1118）"),
                     (C_SHORT, "短编码参照 @4G（1117）")):
        lg.append(f'<rect x="{lx}" y="{ly - 9}" width="14" height="10" fill="{col}"/>'
                  f'<text x="{lx + 20}" y="{ly - 4}" fill="{INK}" font-size="12">{tag}</text>')
        lx += 20 + 12 * len(tag) + 28
    lg.append(f'<text x="268" y="{ly + 14}" fill="{MUTED}" font-size="11">'
              f'数据源 longcode_{{4g,3g}}_data.json · Initial Design</text>')
    lg.append("</g>")
    o.extend(lg)
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" '
             f'stroke="{BORDER}" stroke-width="1"/>')
    o.append(TAIL_SIG)
    o.append("</svg>")
    return "\n".join(o) + "\n"


# ================================================================ 组成环形图
def build_donut_svg(l4, l3, anim):
    top = l4["top_total_uW"]
    v_long = l4["blocks"]["u_LOGIC_CENTER.LINK_LOGIC.LC_CHPI_DECODE.LONG_ENCODING"]["total"]
    v_short = l4["blocks"]["u_LOGIC_CENTER.LINK_LOGIC.LC_CHPI_DECODE.SHORT_ENCODING"]["total"]
    v_rest = round(top - v_long - v_short, 2)
    assert abs(v_long + v_short + v_rest - top) < 0.01, "Σ片 != 中心值"
    slices = (("LONG_ENCODING", v_long, C_LONG4G), ("SHORT_ENCODING", v_short, C_SHORT),
              ("其他（top − 两编码组）", v_rest, C_REST))

    W, H = 760, 470
    CX, CY, R, SW = 235, 240, 118, 44
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}">']
    o.append("<style>" + FONT + "</style>")
    if anim:
        o.append("<style>\n" + ANIM_CSS + "\n</style>")
    o.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}"/>')
    o.append(f'<g class="head"><rect x="0" y="0" width="{W}" height="42" fill="{INK}"/>'
             f'<text x="14" y="21" dominant-baseline="central" fill="#f4f1ea" font-size="15" '
             f'font-weight="bold">HK1V11 长编码 @4G 功耗组成（Initial Design）</text>'
             f'<text x="{W - 14}" y="21" text-anchor="end" dominant-baseline="central" '
             f'fill="#e8c59e" font-size="12">PACK_TAR_1118V0 rep_dir_1lane_4g_420b_1118</text></g>')
    # 环：pathLength=100 + dasharray（12 点起顺时针）
    cum = 0.0
    for name, v, col in slices:
        p = v / top * 100.0
        o.append(f'<g class="row"><circle cx="{CX}" cy="{CY}" r="{R}" fill="none" stroke="{col}" '
                 f'stroke-width="{SW}" pathLength="100" stroke-dasharray="{p:.4f} {100 - p:.4f}" '
                 f'stroke-dashoffset="{25 - cum:.4f}"/>')
        mid = (cum + p / 2) % 100 / 100 * 360
        import math
        a = math.radians(mid - 90)
        lx, ly = CX + (R) * math.cos(a), CY + (R) * math.sin(a)
        o.append(f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="2.2" fill="{SURFACE}"/></g>')
        cum += p
    # 图例
    ly = 130
    o.append('<g class="fade">')
    for k, (name, v, col) in enumerate(slices):
        wcls = (' class="cellwave" style="animation-delay:%gs"' % (0.7 * k)
                if (anim and k < 2) else "")
        if wcls:
            o.append(f"<g{wcls}>")
        o.append(f'<rect x="470" y="{ly - 10}" width="14" height="10" fill="{col}"/>'
                 f'<text x="490" y="{ly - 5}" fill="{INK}" font-size="13">{esc(name)}</text>'
                 f'<text x="740" y="{ly - 5}" text-anchor="end" fill="{INK}" font-size="13" '
                 f'font-weight="bold">{v:,.2f} µW</text>'
                 f'<text x="740" y="{ly + 13}" text-anchor="end" fill="{MUTED}" font-size="11">'
                 f'{v / top * 100:.1f}%</text>')
        if wcls:
            o.append("</g>")
        ly += 46
    _l3g = l3["blocks"]["u_LOGIC_CENTER.LINK_LOGIC.LC_CHPI_DECODE.LONG_ENCODING"]["total"]
    _s3g = l3["blocks"]["u_LOGIC_CENTER.LINK_LOGIC.LC_CHPI_DECODE.SHORT_ENCODING"]["total"]
    o.append(f'<text x="{W // 2}" y="{H - 16}" text-anchor="middle" fill="{MUTED}" font-size="11">'
             f'长@3G 档：LONG {_l3g:,.2f} / SHORT {_s3g:,.2f} / top {l3["top_total_uW"]:,.2f} µW</text>')
    o.append("</g>")
    pcls = ' class="pulse" style="animation-delay:-1.2s"' if anim else ""
    o.append(f"<g{pcls}>"
             f'<text x="{CX}" y="{CY - 12}" text-anchor="middle" fill="{INK}" font-size="26" '
             f'font-weight="bold">{vfmt(top / 1000.0)} mW</text>'
             f'<text x="{CX}" y="{CY + 14}" text-anchor="middle" fill="{MUTED}" font-size="12">'
             f'{top:,.2f} µW</text></g>')
    o.append(f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" fill="none" '
             f'stroke="{BORDER}" stroke-width="1"/>')
    o.append(TAIL_SIG)
    o.append("</svg>")
    return "\n".join(o) + "\n"


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    new = path.read_text(encoding="utf-8") if path.is_file() else None
    if new == text:
        print(f"SKIPPED {path}")
        return
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"WROTE {path} bytes={len(text.encode('utf-8'))} "
          f"md5={hashlib.md5(text.encode('utf-8')).hexdigest()}")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只读比对，漂移 exit 1")
    a = ap.parse_args(argv)
    l4, l3, sr = load()
    outs = {
        SITE_ROOT / "images/power_module_compare_long_short.svg": build_bar_svg(l4, l3, sr, False),
        SITE_ROOT / "images/anim/power_module_compare_long_short.svg": build_bar_svg(l4, l3, sr, True),
        SITE_ROOT / "images/power_composition_donut_long_short.svg": build_donut_svg(l4, l3, False),
        SITE_ROOT / "images/anim/power_composition_donut_long_short.svg": build_donut_svg(l4, l3, True),
    }
    def _nosig(t):
        return "\n".join(ln for ln in t.splitlines() if not ln.startswith("<!-- ymzhu "))

    if a.check:
        bad = [p for p, t in outs.items()
               if not p.is_file() or _nosig(p.read_text(encoding="utf-8")) != _nosig(t)]
        if bad:
            print("DRIFT: %s" % bad)
            return 1
        print("CHECK OK (4 files)")
        return 0
    for p, t in outs.items():
        write(p, t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
# ymzhu 2026-11-18 11:30
