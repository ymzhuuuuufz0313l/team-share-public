#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_chip_sel0.py — chip_sel0_register_map.svg 动画版生成器
（Motion Kit v4；整体重写 v1，v1 类名/delay/呼吸逻辑不沿用）。

源（只读）:  ../chip_sel0_register_map.svg
输出:        chip_sel0_register_map.svg

v4 规格（1100×2842，chip_sel=0 寄存器默认字节映射 · 49 行）：
- 入场：head 标题+位号列+POR 表头(0) → 49 个寄存器行 0.15 起 0.03s 递进
  （至 1.59）→ 底部图例+脚注 head(1.8)。一次性总长 2.35s ≤ 2.5s。
- 稳态（3 族，肉眼可辨；取代 v1 的 233 处低幅呼吸）：
  · 行波 cellwave×49（主角）：全部寄存器行（含行尾 POR pill）整行组波，
    自上而下 0.2s/行 错相位（周期 9.8s）= 地址扫描波。
  · 脉冲 pulse×1：0x1D 行 khead_20b_sel[4:0] 单元格（rect+2text 三连）
    pulse（琥珀，-0.7s，LC_CPUWR 1027v1 变更格）。
  · 语义扫光 sweepband×1：POR 默认值列（右侧 pill 列，x[836,912]，
    y 覆盖全部 pill）——§4 配方（P=316，8s 循环），位于内容之下、
    白底之上，pill 间缝隙与列空白带可见 = 默认值列周期巡检。
- 铁律：源 SVG 只读；<text> 多重集 / svg 开标签 / 几何颜色零改动；
  纯 CSS 无 script 无 SMIL；kit CSS §2 逐字嵌入；背景 rect 保留；
  扫光渐变/clipPath 为 v4 新增 defs 项；reduced-motion 用 kit 原文；
  确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images")
SRC = BASE / "chip_sel0_register_map.svg"
OUT = BASE / "anim" / "chip_sel0_register_map.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类）
KIT_CSS = "\n".join([
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

LABEL_X = "158"
N_ROWS = 49
ROW_STEP = 0.03
WAVE_STEP = 0.2
ROW_PULSES = {}                                   # 本图无行级脉冲
CELL_PULSES = {"0x1D": ("khead_20b_sel[4:0]", "pulse", "-0.7s")}


def attrs_of(line):
    m = re.match(r'^\s*<([A-Za-z][\w-]*)((?:\s+[\w-]+="[^"]*")*)\s*/?>', line)
    if not m:
        return None, None
    return m.group(1), dict(re.findall(r'([\w-]+)="([^"]*)"', m.group(2)))


def text_of(line):
    m = re.match(r'^\s*<text\b[^>]*>(.*?)</text>\s*$', line)
    return m.group(1) if m else None


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tail_nl = raw.endswith(eol)
    lines = raw.split(eol)
    if tail_nl:
        lines = lines[:-1]
    assert lines[0].startswith("<?xml"), "line1 应为 XML 声明"
    assert lines[1].lstrip().startswith("<svg"), "line2 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1
    assert attrs_of(lines[2])[0] == "rect", "line3 应为背景 rect"
    for i in range(2, end):                       # 源为每元素一行的扁平 SVG
        assert attrs_of(lines[i])[0] in ("rect", "text", "circle"), f"line{i+1} 非预期元素"

    def is_row_label(line):
        tag, at = attrs_of(line)
        return (tag == "text" and at.get("x") == LABEL_X
                and at.get("font-weight") == "600"
                and (text_of(line) or "").startswith("0x"))

    row_starts = [i for i in range(3, end) if is_row_label(lines[i])]
    assert len(row_starts) == N_ROWS, f"应 {N_ROWS} 行，实际 {len(row_starts)}"
    legend = next(i for i in range(row_starts[-1] + 1, end) if text_of(lines[i]) == "图例")
    assert "POR 默认值" in lines[row_starts[0] - 1] or \
        any("POR 默认值" in lines[i] for i in range(3, row_starts[0])), "POR 表头缺失"

    rows = []
    for k, s in enumerate(row_starts):
        e = row_starts[k + 1] if k + 1 < len(row_starts) else legend
        label = text_of(lines[s]) or ""
        prefix = label.split(" ")[0]
        rows.append((s, e, prefix, label))
    row_pulse_map = {(s, e): ROW_PULSES[p] for s, e, p, _ in rows if p in ROW_PULSES}
    cell_pulse_map = {}
    for s, e, p, _label in rows:
        if p in CELL_PULSES:
            field, kind, delay = CELL_PULSES[p]
            t = next((i for i in range(s + 1, e) if field in (text_of(lines[i]) or "")), None)
            assert t is not None, f"{p} 行未找到 {field}"
            assert attrs_of(lines[t - 1])[0] == "rect", f"{field} 前应为 rect"
            assert attrs_of(lines[t + 1])[0] == "text", f"{field} 后应为 value text"
            cell_pulse_map[t - 1] = (kind, delay, t + 1)
    assert len(cell_pulse_map) == 1, "khead 脉冲格应恰 1 处"

    # ---- POR 列扫光带（§4 配方）：pill 列 x[842,906]，区域含边距 ----
    pill_re = re.compile(r'^<rect x="842" y="([\d.]+)" width="64" height="26"')
    pill_ys = [float(pill_re.match(lines[i].strip()).group(1))
               for i in range(3, legend) if pill_re.match(lines[i].strip())]
    n_pill_rows = len([lb for _, _, _, lb in rows if "~" not in lb])  # 波段行无 POR pill
    assert len(pill_ys) == n_pill_rows, f"pill 数应 {n_pill_rows}，实际 {len(pill_ys)}"
    sp = {"RL": 836, "R": 76}
    sp["Y"] = int(min(pill_ys)) - 6
    sp["H"] = int(max(pill_ys)) + 26 - sp["Y"] + 6
    sp["P"] = sp["R"] + 240                        # 316
    sp["X0"] = sp["RL"] - int(0.54 * sp["P"])      # t=0 光带藏于区域左外侧
    sweep_defs = [
        f'<linearGradient id="sweepG-1" gradientUnits="userSpaceOnUse" x1="{sp["X0"]}" y1="0" x2="{sp["X0"] + sp["P"]}" y2="0">',
        '<stop offset="0" stop-color="#b45309" stop-opacity="0"/>',
        '<stop offset="0.46" stop-color="#b45309" stop-opacity="0"/>',
        '<stop offset="0.5" stop-color="#b45309" stop-opacity="0.3"/>',
        '<stop offset="0.54" stop-color="#b45309" stop-opacity="0"/>',
        '<stop offset="1" stop-color="#b45309" stop-opacity="0"/>',
        '</linearGradient>',
        f'<clipPath id="sweepC-1"><rect x="{sp["RL"]}" y="{sp["Y"]}" width="{sp["R"]}" height="{sp["H"]}"/></clipPath>',
    ]
    sweep_g = (f'<g clip-path="url(#sweepC-1)"><rect class="sweepband" x="{sp["X0"]}" '
               f'y="{sp["Y"]}" width="{sp["P"]}" height="{sp["H"]}" fill="url(#sweepG-1)" '
               f'style="--sweepP:{sp["P"]}px"/></g>')

    # ---- 组装 ----
    o = []
    o.append(lines[0])                              # <?xml?>
    o.append(lines[1])                              # <svg ...>
    o.append("<style>\n" + KIT_CSS + "\n</style>")  # kit CSS（§2 逐字）
    o.append(lines[2])                              # 白底 rect
    o.append("<defs>")
    o.extend(sweep_defs)                            # v4 新增：扫光渐变 + clipPath
    o.append("</defs>")
    o.append(sweep_g)                               # 白底之上、内容之下

    o.append('<g class="head">')                    # 标题 + 位号列 + POR 表头 (0)
    o.extend(lines[3:row_starts[0]])
    o.append("</g>")

    n = len(rows)
    wave_dur = round(WAVE_STEP * n, 1)              # 9.8s
    for k, (s, e, _p, _lb) in enumerate(rows):
        delay = round(0.15 + ROW_STEP * k, 2)
        o.append(f'<g class="row" style="animation-delay:{delay}s">')
        if (s, e) in row_pulse_map:
            kind, pd = row_pulse_map[(s, e)]
            o.append(f'<g class="{kind}" style="animation-delay:{pd}">')
        ph = WAVE_STEP * k
        wd = "0s" if ph == 0 else f"-{ph:.1f}s"
        o.append(f'<g class="cellwave" style="animation-duration:{wave_dur}s;animation-delay:{wd}">')
        i = s
        while i < e:
            if i in cell_pulse_map:
                kind, pd, stop = cell_pulse_map[i]
                o.append(f'<g class="{kind}" style="animation-delay:{pd}">')
                o.extend(lines[i:stop + 1])
                o.append("</g>")
                i = stop + 1
                continue
            o.append(lines[i])
            i += 1
        o.append("</g>")
        if (s, e) in row_pulse_map:
            o.append("</g>")
        o.append("</g>")

    o.append('<g class="head" style="animation-delay:1.8s">')  # 图例 + 脚注
    o.extend(lines[legend:end])
    o.append("</g>")

    o.append(lines[end])  # </svg>
    text = eol.join(o)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")
    return {"cellwave": text.count('class="cellwave"'),
            "pulse": len(re.findall(r'class="pulse(-[tb])?"', text)),
            "sweepband": text.count('class="sweepband"'),
            "row": text.count('class="row"'), "head": text.count('class="head"')}


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
    rm = re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
    res["rmfix"] = "OK" if (rm and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    fam = {"train": len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
           "pulse": len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
           "sweep": len(re.findall(r'class="[^"]*sweepband', data)),
           "grow": len(re.findall(r'class="[^"]*dashgrow', data)),
           "wave": len(re.findall(r'class="[^"]*cellwave', data)),
           "step": len(re.findall(r'class="[^"]*step"', data))}
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    return res


def main():
    stats = build()
    res = check()
    print("[make_anim_chip_sel0 v4]", stats)
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK" or v.startswith("OK("))
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 17:32
