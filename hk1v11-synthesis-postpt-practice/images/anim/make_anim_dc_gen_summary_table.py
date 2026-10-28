#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_dc_gen_summary_table.py — v4（Motion Kit v4，整体重写；旧版单元格错峰呼吸不沿用）

dc_gen_summary_table（3928×489，三代总览表，静态版=images/ 同名 svg）规格：
- 入场（总长 ≤2.5s）：表头 .head(0) → 网格 .fade(0.05) → r1 .row(0.25) → r2 .row(0.55)
  → r3 .row(0.85)；末项 0.85+0.55=1.4s
- 稳态（3 族）：
  · 行波 cellwave ×3：三代行整行组包（r1/r2/r3，duration 3.6s，phase 0/-1.2/-2.4）
    ——自上而下的代际演进波
  · 扫光 sweepband ×1（§4 配方，琥珀）：r3 当代行（y396..489，P=4168）——
    "关键路径优化后收敛"结果行语义扫光；置于行底色之上、行文字之下（行内 br 标记后插入）
  · 脉冲 ×2（错相位）：r2 "452 条 / -1.45 ns / hold 30" .pulse(-1.4s)——最差一代；
    r3 "11 条 / -0.01 ns / hold 21" .pulse-t(-0.7s)——收敛结果（深青辉光配绿色文本）
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs（diagF2/clipD2）/背景 rect 保留（assert 保护）；
  源字体 <style> 原样保留（残留 animation 声明惰性、无 kit 同名冲突）；
  reduced-motion 双保险；确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice")
SRC = BASE / "images" / "dc_gen_summary_table.svg"
OUT = BASE / "images" / "anim" / "dc_gen_summary_table.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类；与 canonical 站一致）
KIT_CSS = "\n".join([
    ".row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 1.5s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 1.5s linear infinite}",
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}",
    "@keyframes pulse{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(180,83,9,.8))}}",
    ".pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}",
    "@keyframes pulseT{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(14,116,144,.8))}}",
    ".pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}",
    "@keyframes pulseB{0%,100%{transform:scale(1);filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{transform:scale(1.03);filter:drop-shadow(0 0 12px rgba(29,78,216,.8))}}",
    ".sweepband{opacity:.85;animation:sweepMove 8s linear infinite}",
    "@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}",
    ".dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}",
    "@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}",
    ".march{animation:march 1.5s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".cellwave{transform-box:fill-box;transform-origin:center;animation:wave 2.6s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.72;transform:scale(1.01)}}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".step{transform-box:fill-box;transform-origin:center;animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85));transform:scale(1.02)}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0));transform:none}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85));transform:scale(1.02)}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}",
])

SWEEP = dict(x0=0, y=396, w=3928, h=93, n=1)


def sweep_defs(s):
    p = s["w"] + 240
    return (
        f'<linearGradient id="sweepG-{s["n"]}" gradientUnits="userSpaceOnUse" x1="{s["x0"]}" y1="0" x2="{s["x0"] + p}" y2="0">'
        '<stop offset="0" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="0.46" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#b45309" stop-opacity="0.3"/>'
        '<stop offset="0.54" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#b45309" stop-opacity="0"/>'
        '</linearGradient>\n'
        f'<clipPath id="sweepC-{s["n"]}"><rect x="{s["x0"]}" y="{s["y"]}" width="{s["w"]}" height="{s["h"]}"/></clipPath>'
    )


def sweep_group(s):
    p = s["w"] + 240
    return (f'<g clip-path="url(#sweepC-{s["n"]})">'
            f'<rect class="sweepband" x="{s["x0"]}" y="{s["y"]}" width="{p}" height="{s["h"]}" '
            f'fill="url(#sweepG-{s["n"]})" style="--sweepP:{p}px"/></g>')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>" or lines[-1].strip().startswith("<!--"), "末行异常"
    end = next(i for i, s in enumerate(lines) if s.strip() == "</svg>")

    def find(pred, start=0, stop=None):
        stop = end if stop is None else stop
        for i in range(start, stop):
            if pred(lines[i]):
                return i
        raise AssertionError("anchor not found")

    def group_close(open_i):
        depth = 0
        for i in range(open_i + 1, end):
            t = lines[i]
            opens = len(re.findall(r"<g(\s|>)", t))
            closes = t.count("</g>")
            if closes > opens + depth:
                return i
            depth += opens - closes
        raise AssertionError("group close not found")

    # ---- 结构锚点 ----
    style_close = find(lambda s: s.strip() == "</style>")
    defs_close = find(lambda s: s.strip() == "</defs>")
    assert any('id="diagF2"' in lines[i] for i in range(style_close, defs_close)), "源 defs(diagF2) 应保留"
    bg_i = find(lambda s: s.strip() == '<rect x="0" y="0" width="3928" height="489" fill="#fffdf7"/>')
    hdr_g = find(lambda s: s.strip() == '<g class="hdr">')
    hdr_g_close = group_close(hdr_g)
    r_g = {}
    for n in (1, 2, 3):
        o = find(lambda s, n=n: s.strip() == f'<g class="r{n}">',
                 r_g[n - 1][1] + 1 if n > 1 else hdr_g)
        r_g[n] = (o, group_close(o))
    grid_g = find(lambda s: s.strip().startswith('<g stroke="#ddd6c8"'))
    grid_g_close = find(lambda s: s.strip() == "</g>", grid_g + 1)
    pl2_g = find(lambda s: '<g class="pl2">' in s)
    pl3_g = find(lambda s: '<g class="pl3">' in s)
    assert r_g[2][0] < pl2_g < r_g[2][1], "pl2 应在 r2 内"
    assert r_g[3][0] < pl3_g < r_g[3][1], "pl3 应在 r3 内"

    # ---- 组装 ----
    o = []
    o.extend(lines[0:style_close + 1])
    o.append("<style>\n" + KIT_CSS + "\n</style>")
    o.extend(lines[style_close + 1:defs_close])
    o.append(sweep_defs(SWEEP))
    o.append(lines[defs_close])
    o.extend(lines[defs_close + 1:bg_i + 1])                 # 背景 rect

    # 表头 .head(0)
    o.append('<g class="hdr head" style="animation-delay:0s">')
    o.extend(lines[hdr_g + 1:hdr_g_close])
    o.append("</g>")
    o.extend(lines[hdr_g_close + 1:r_g[1][0]])

    # 三代行：.row + 内层 cellwave（phase 0/-1.2/-2.4，duration 3.6s）
    # r3 行内 br 标记后插扫光带；pl2 文本组加 pulse、pl3 加 pulse-t
    row_d = {1: 0.25, 2: 0.55, 3: 0.85}
    wave_ph = {1: "0s", 2: "-1.2s", 3: "-2.4s"}
    for n in (1, 2, 3):
        ro, rc = r_g[n]
        o.append(f'<g class="r{n} row" style="animation-delay:{row_d[n]}s">')
        o.append(f'<g class="cellwave" style="animation-duration:3.6s;animation-delay:{wave_ph[n]}">')
        for i in range(ro + 1, rc):
            if n == 2 and i == pl2_g:
                o.append(lines[i].replace('<g class="pl2">',
                                          '<g class="pl2 pulse" style="animation-delay:-1.4s">', 1))
            elif n == 3 and i == pl3_g:
                o.append(lines[i].replace('<g class="pl3">',
                                          '<g class="pl3 pulse-t" style="animation-delay:-0.7s">', 1))
            elif n == 3 and 'class="br"' in lines[i]:
                o.append(lines[i])
                o.append(sweep_group(SWEEP))                 # 当代行扫光带
            else:
                o.append(lines[i])
        o.append("</g>")                                     # cellwave
        o.append("</g>")                                     # row

    # 网格 .fade(0.05) + tl 遗留条（opacity=0 原样） + 边框
    o.append('<g class="fade" style="animation-delay:0.05s">')
    o.extend(lines[grid_g:grid_g_close + 1])
    o.append("</g>")
    o.extend(lines[grid_g_close + 1:])

    text = eol.join(o)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG {e}"

    def texts(p):
        return Counter(el.text or "" for el in ET.parse(str(p)).getroot().iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except Exception as e:
        res["text"] = f"NG {e}"

    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    res["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    res["rmfix"] = "OK" if ".flowdot,.flowtail,.sweepband{display:none!important}" in data else "NG"
    fam = {
        "train": len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
        "pulse": len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
        "sweep": len(re.findall(r'class="[^"]*sweepband', data)),
        "grow": len(re.findall(r'class="[^"]*dashgrow', data)),
        "wave": len(re.findall(r'class="[^"]*cellwave', data)),
        "step": len(re.findall(r'class="[^"]*step"', data)),
    }
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    res["families"] = fam
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_dc_gen_summary_table v4]",
          "row=", len(re.findall(r'class="r\d row"', data)),
          "cellwave=", data.count('class="cellwave"'),
          "sweepband=", data.count('class="sweepband"'),
          "pulse=", len(re.findall(r'class="pl\d pulse', data)))
    ok = True
    for k, v in res.items():
        if k != "families":
            print(f"  {k}: {v}")
            ok &= str(v) == "OK" or str(v).startswith("OK(")
    print("  families:", res["families"])
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 17:38
