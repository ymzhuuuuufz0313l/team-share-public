#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_checksum.py — checksum_address_map.svg 动画版生成器
（Motion Kit v4；整体重写 v1，v1 类名/delay/呼吸逻辑不沿用）。

源（只读）:  ../checksum_address_map.svg
输出:        checksum_address_map.svg

v4 规格（940×1764，LC_CPUWR 1023v1 参与 checksum 的地址 · chip_sel=0/1 对照）：
- 入场：head 标题+位号列头(0) → 15 个地址行 0.15 起 0.08s 递进（至 1.27）
  → 底部图例+脚注 head(1.5)。一次性总长 1.5+0.55 = 2.05s ≤ 2.5s。
- 稳态（2 族 + v4.1 加密脉冲；取代 v1 的 233 处低幅呼吸）：
  · 行波 cellwave×15（主角）：全部地址行整行组波，自上而下 0.4s/行 错相位
    （周期 6.0s）= 地址扫描波。
  · 脉冲 pulse×4（v4.1 +1；相位 0 / -0.7 / -1.4 / -2.1 均布）：
    0x0A cs=1 的 PWRC_P[1:0] 单元格 pulse（琥珀，LC_CPUWR 1027v1 checksum
    覆盖修复受影响字节）；0x02 行组 pulse-b（蓝，唯一 chip_sel=0/1 对照行）；
    0x27 行组 pulse-t（深青，frame end 校验字节边界行）；
    0x1F 行组 pulse（琥珀，0s，PWRC 控制字节双行 PWRC_P1..N3/CTRL+NB/NA/PB/PA
    —— 0x27 已有脉冲后按"PWRC 相关另一关键行"选定）。
- 铁律：源 SVG 只读；<text> 多重集 / svg 开标签 / 几何颜色零改动；
  纯 CSS 无 script 无 SMIL；kit CSS §2 逐字嵌入；背景 rect 保留；
  reduced-motion 用 kit 原文；确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path("E:/project/team-share-public/hk1v11-lc-cpuwr-history/images")
SRC = BASE / "checksum_address_map.svg"
OUT = BASE / "anim" / "checksum_address_map.svg"

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

LABEL_X = "170"        # 行标签列 x
ROW_STEP = 0.08        # 入场递进（15 行）
WAVE_STEP = 0.4        # 行波相位步进
ROW_PULSES = {"0x02": ("pulse-b", "-1.4s"), "0x27": ("pulse-t", "-2.1s"),
              "0x1F": ("pulse", "0s")}          # v4.1：PWRC 控制字节双行
CELL_PULSES = {"0x0A": ("PWRC_P[1:0]", "pulse", "-0.7s")}


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

    def is_row_label(line):
        tag, at = attrs_of(line)
        return (tag == "text" and at.get("x") == LABEL_X
                and at.get("text-anchor") == "end" and at.get("font-weight") == "600"
                and (text_of(line) or "").startswith("0x"))

    row_starts = [i for i in range(3, end) if is_row_label(lines[i])]
    assert len(row_starts) == 15, f"应 15 个地址行，实际 {len(row_starts)}"
    legend = next(i for i in range(row_starts[-1] + 1, end) if text_of(lines[i]) == "图例")

    # 脉冲定位：行级（标签前缀）与单元格级（rect+2text 三连）
    rows = []
    for k, s in enumerate(row_starts):
        e = row_starts[k + 1] if k + 1 < len(row_starts) else legend
        label = text_of(lines[s])
        prefix = label.split(" ")[0]
        rows.append((s, e, prefix))
    row_pulse_map = {}
    for s, e, prefix in rows:
        if prefix in ROW_PULSES:
            row_pulse_map[(s, e)] = ROW_PULSES[prefix]
    cell_pulse_map = {}
    for s, e, prefix in rows:
        if prefix in CELL_PULSES:
            field, kind, delay = CELL_PULSES[prefix]
            t = next((i for i in range(s + 1, e) if field in (text_of(lines[i]) or "")), None)
            assert t is not None, f"{prefix} 行未找到 {field}"
            assert attrs_of(lines[t - 1])[0] == "rect", f"{field} 前应为 rect"
            assert attrs_of(lines[t + 1])[0] == "text", f"{field} 后应为 value text"
            cell_pulse_map[t - 1] = (kind, delay, t + 1)
    assert len(row_pulse_map) == 3 and len(cell_pulse_map) == 1, "脉冲定位数异常"

    # ---- 组装 ----
    o = []
    o.append(lines[0])                              # <?xml?>
    o.append(lines[1])                              # <svg ...>
    o.append("<style>\n" + KIT_CSS + "\n</style>")  # kit CSS（§2 逐字）
    o.append(lines[2])                              # 白底 rect

    o.append('<g class="head">')                    # 标题 + 位号列头 (0)
    o.extend(lines[3:row_starts[0]])
    o.append("</g>")

    n = len(rows)
    wave_dur = round(WAVE_STEP * n, 1)              # 6.0s
    for k, (s, e, _) in enumerate(rows):
        delay = round(0.15 + ROW_STEP * k, 2)
        o.append(f'<g class="row" style="animation-delay:{delay}s">')
        if (s, e) in row_pulse_map:
            kind, pd = row_pulse_map[(s, e)]
            o.append(f'<g class="{kind}" style="animation-delay:{pd}">')
        ph = WAVE_STEP * k
        wd = f"0s" if ph == 0 else f"-{ph:.1f}s"
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

    o.append('<g class="head" style="animation-delay:1.5s">')  # 图例 + 脚注
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
    print("[make_anim_checksum v4]", stats)
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK" or v.startswith("OK("))
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 19:14
