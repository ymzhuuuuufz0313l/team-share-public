#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_beat.py — config_data_beat_regroup_0721.svg 动画版生成器
（Motion Kit v4；整体重写 v1，v1 类名/delay 逻辑不沿用）。

源（只读）:  ../config_data_beat_regroup_0721.svg
输出:        config_data_beat_regroup_0721.svg

v4 规格（1240×848，0721v1 配置拍重组对照）：
- 入场（先容器→再内容，一次性总长 ≤2.5s）：
  · head 标题+副标题(0) / 图例色块(0.15) / 两栏列头+中缝线(0.3)
  · 行：区域标签与拍盒按源行序 0.45 起 0.05s 递进（26 行，至 1.70）
  · 绿色 XOR 总量不变汇总框(1.75) / 橙色过渡依赖汇总框(1.85)
- 稳态（3 族，肉眼可辨）：
  · 行波 cellwave×22 拍盒（主角）：左栏（0716 2B/拍，13 盒）按拍序
    0.35s/盒 错相位；右栏（0721 3B/拍，9 盒）同参数但整体相位 +0.175s
    = 两列波半拍错位（分组变化、节拍推进可视化）。周期 4.55s。
  · 脉冲 pulse×2：绿色汇总框 pulse-t（深青，-2.1s）、橙色过渡依赖框
    pulse（琥珀，-0.7s）——取代 v1 的低幅呼吸。
  · 语义扫光 sweepband×1：右栏（0721 新分组侧）区域 x[648,1224]
    y[176,762]，§4 配方（P=816，光带 t=0 藏于区域左外侧，8s 循环）；
    位于拍盒内容之下、白底之上（canonical 分层，缝隙间可见）。
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
SRC = BASE / "config_data_beat_regroup_0721.svg"
OUT = BASE / "anim" / "config_data_beat_regroup_0721.svg"

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

# 行波相位（负 delay = 相位偏移，|d| ≤ 周期 4.55s）
WAVE_STEP = 0.35
WAVE_DUR = 4.55


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    tail_nl = raw.endswith(eol)
    lines = raw.split(eol)
    if tail_nl:
        lines = lines[:-1]
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1
    assert lines[1].strip().startswith("<rect"), "line2 应为背景 rect"

    # ---- 结构锚点（0 基；源每行 = 一个元素或一个完整拍盒行） ----
    title_i = 2           # 标题
    legend_i = 4          # 第一个图例色块 rect
    headers_i = 12        # 左栏列头 text（0716_v1_work）
    divider_i = 14        # 中缝 line
    assert "LC_CPUWR 0721v1 配置拍重组对照" in lines[title_i]
    assert lines[legend_i].strip().startswith("<rect") and 'fill="#ecfdf5"' in lines[legend_i]
    assert "0716_v1_work" in lines[headers_i]
    assert "0721_v1" in lines[headers_i + 1]
    assert lines[divider_i].strip().startswith("<line"), "中缝 line 异常"

    # 行区：line16(0 基 15) 区域A 标签 … line41(0 基 40) 右栏 D 末盒
    region_re = re.compile(r'^<text x="60" y="\d+" font-size="13" font-weight="700" '
                           r'fill="#0f172a">区域 ')
    rows = list(range(15, 41))
    labels = [i for i in rows if region_re.match(lines[i].strip())]
    assert len(labels) == 4, f"应 4 个区域标签，实际 {len(labels)}"
    left_boxes = [16, 17, 18, 19, 20, 21, 27, 28, 29, 33, 36, 37, 38]
    right_boxes = [22, 23, 24, 25, 30, 31, 34, 39, 40]
    for i in left_boxes + right_boxes:
        assert lines[i].strip().startswith("<rect"), f"line{i+1} 应为拍盒行"
        assert i not in labels
    assert sorted(labels + left_boxes + right_boxes) == list(range(15, 41)), "行区覆盖缺口"

    # 汇总框：绿 = "XOR 总量不变"，橙 = "过渡依赖"
    green_i = next(i for i in range(41, end) if "XOR 总量不变" in lines[i])
    assert lines[green_i - 1].strip().startswith("<rect"), "绿框 rect 异常"
    orange_i = next(i for i in range(green_i + 1, end) if ">过渡依赖<" in lines[i])
    assert lines[orange_i - 1].strip().startswith("<rect"), "橙框 rect 异常"

    # ---- 扫光带（§4 配方）：右栏 0721 新分组侧 ----
    # 从右栏拍盒行内解析 rect 坐标定区域边界（含盒上标签/下参与式文字）
    ys = []
    for i in right_boxes:
        for m in re.finditer(r'<rect x="(\d+)" y="(\d+)" width="(\d+)" height="(\d+)"', lines[i]):
            ys.append(int(m.group(2)))
        for m in re.finditer(r'<text x="[\d.]+" y="(\d+)"', lines[i]):
            ys.append(int(m.group(1)) - 14)  # 文字基线 → 近似盒顶
    sp = {"RL": 648, "R": 576}
    sp["Y"] = min(ys) - 4
    sp["H"] = max(ys) + 18 - sp["Y"]
    sp["P"] = sp["R"] + 240                        # 816
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
    o.append(lines[0])                              # <svg ...>
    o.append("<style>\n" + KIT_CSS + "\n</style>")  # kit CSS（§2 逐字）
    o.append(lines[1])                              # 白底 rect
    o.append("<defs>")
    o.extend(sweep_defs)                            # v4 新增：扫光渐变 + clipPath
    o.append("</defs>")
    o.append(sweep_g)                               # 白底之上、内容之下

    def head(span, delay):
        o.append(f'<g class="head" style="animation-delay:{delay}s">')
        o.extend(lines[span[0]:span[1]])
        o.append("</g>")

    head((title_i, legend_i), 0)          # 标题+副标题
    head((legend_i, headers_i), 0.15)     # 图例色块 4 组
    head((headers_i, divider_i + 1), 0.3)  # 两栏列头 + 中缝线

    # 行：0.45 起 0.05s 递进；拍盒嵌 cellwave（左/右栏两列波半拍错位）
    for k, i in enumerate(rows):
        delay = round(0.45 + 0.05 * k, 2)
        o.append(f'<g class="row" style="animation-delay:{delay}s">')
        if i in left_boxes:
            ph = WAVE_STEP * left_boxes.index(i)
            o.append(f'<g class="cellwave" style="animation-duration:{WAVE_DUR}s;animation-delay:-{ph:.2f}s">')
            o.append(lines[i])
            o.append("</g>")
        elif i in right_boxes:
            ph = WAVE_STEP * right_boxes.index(i) + 0.175
            o.append(f'<g class="cellwave" style="animation-duration:{WAVE_DUR}s;animation-delay:-{ph:.2f}s">')
            o.append(lines[i])
            o.append("</g>")
        else:
            o.append(lines[i])
        o.append("</g>")

    # 绿框(1.75, pulse-t) / 橙框(1.85, pulse)
    o.append(f'<g class="row" style="animation-delay:1.75s">')
    o.append('<g class="pulse-t" style="animation-delay:-2.1s">')
    o.extend(lines[green_i - 1:orange_i - 1])
    o.append("</g>")
    o.append("</g>")
    o.append(f'<g class="row" style="animation-delay:1.85s">')
    o.append('<g class="pulse" style="animation-delay:-0.7s">')
    o.extend(lines[orange_i - 1:end])
    o.append("</g>")
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
    print("[make_anim_beat v4]", stats)
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK" or v.startswith("OK("))
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 17:26
