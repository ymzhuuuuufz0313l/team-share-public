#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_power_compare_hk11.py — v4（Motion Kit v4，整体重写；旧版类名/delay 逻辑不沿用）

power_compare_hk11（605×444，柱状对比表，静态版=站点根目录同名 svg）规格：
- 入场（总长 ≤2.5s）：
  · 表头组 .head(0)
  · 数据行 r0~r16 .row，0.15s 起 0.09s 递进（末行 1.59s）
  · 每行数值条簇（bar rect [+峰值三角 path] + dot circle）再包一层 .row（行 delay+0.12s，
    末簇 1.71+0.55=2.26s）= 先文字行、后数值条的分层入场
  · 网格线组 .fade(0.05)
- 稳态（2 族）：
  · sweepband ×2（§4 配方，琥珀）：A=HV1V22 1015 两行 vs 1027 行（y232..298）；
    B=HK1V11 1015 vs 1027 行（y386..430）——"同芯片新旧版本对比"语义扫光，8s 周期
  · pulse ×3（错相位）：r12 峰值行 37.9（峰值徽章+条+dot，pulse 琥珀 -0.5s）；
    r10 HV1V22(1027) 蓝条 pulse-b(-1.9s)；r16 HK1V11(1027) 蓝条 pulse-b(-2.6s)
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs + 背景 rect 保留（assert 保护）；源字体 <style> 原样保留；
  reduced-motion 双保险（源块 + kit 块都在）；确定性幂等（只依赖源 SVG）。
- 旧版遗留说明：源图内 .breath/.breath2/.cmpband/.cmpband2/.zeband/.peakglow/.dot 等
  class 的旧动画 CSS 不再进入输出（它们在静态版中本就无动画），仅作静态外观保留。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice")
SRC = BASE / "power_compare_hk11.svg"
OUT = BASE / "anim" / "power_compare_hk11.svg"

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

# §4 扫光带配方（区域宽 + 240 = P；琥珀 rgba(180,83,9,.30)）
SWEEP_A = dict(x0=0, y=232, w=605, h=66, n=1)   # HV1V22 1015×2 + 1027 行
SWEEP_B = dict(x0=0, y=386, w=605, h=44, n=2)   # HK1V11 1015 + 1027 行


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
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def find(pred, start=0, stop=None):
        stop = end if stop is None else stop
        for i in range(start, stop):
            if pred(lines[i]):
                return i
        raise AssertionError("anchor not found")

    def find_in(seq, pred, start=0, stop=None):
        stop = len(seq) if stop is None else stop
        for i in range(start, stop):
            if pred(seq[i]):
                return i
        raise AssertionError("anchor not found in block")

    # ---- 结构锚点（全部 assert 保护） ----
    style_close = find(lambda s: s.strip() == "]]></style>")
    defs_close = find(lambda s: s.strip() == "</defs>")
    bg_i = find(lambda s: s.strip() == '<rect x="0" y="0" width="605" height="444" fill="#f4f1ea"/>')
    in_g = find(lambda s: s.strip() == '<g class="in">')
    in_g_close = find(lambda s: s.strip() == "</g>", in_g + 1)
    grid_g = find(lambda s: s.strip() == '<g stroke="#ddd6c8" stroke-width="1">')
    grid_g_close = find(lambda s: s.strip() == "</g>", grid_g + 1)

    row_spans = {}  # n -> (open_idx, close_idx)
    def group_close(open_i):
        depth = 0
        for i in range(open_i + 1, end):
            t = lines[i].strip()
            if t.startswith("<g ") or t == "<g>":
                depth += 1
            elif t == "</g>":
                if depth == 0:
                    return i
                depth -= 1
        raise AssertionError("group close not found")

    for n in range(17):
        o = find(lambda s, n=n: s.strip() == f'<g class="r{n}">',
                 row_spans[n - 1][1] + 1 if n else in_g_close + 1)
        row_spans[n] = (o, group_close(o))
    assert row_spans[16][1] < grid_g, "行组应全部位于网格组之前"

    # ---- 组装 ----
    o = []
    o.extend(lines[0:style_close + 1])                      # <svg> + 源字体/遗留 class <style>（原样）
    o.append("<style>\n" + KIT_CSS + "\n</style>")          # kit CSS §2 逐字
    o.extend(lines[style_close + 1:defs_close])             # 源 defs（铁律 4：marker/clip 依赖）
    o.append(sweep_defs(SWEEP_A))
    o.append(sweep_defs(SWEEP_B))
    o.append(lines[defs_close])                             # </defs>
    o.extend(lines[defs_close + 1:bg_i + 1])                # 背景 rect
    o.append(sweep_group(SWEEP_A))                          # 扫光带：内容之下、底色之上
    o.append(sweep_group(SWEEP_B))

    # 表头 .head(0)
    o.append('<g class="in head">')
    o.extend(lines[in_g + 1:in_g_close])
    o.append("</g>")

    # 数据行：行组 .row(0.15+0.09n)；数值条簇内层 .row(+0.12)；r10/r12/r16 簇加 pulse
    pulse_of = {12: ("pulse", "-0.5s"), 10: ("pulse-b", "-1.9s"), 16: ("pulse-b", "-2.6s")}
    for n in range(17):
        ro, rc = row_spans[n]
        d = 0.15 + 0.09 * n
        o.append(f'<g class="r{n} row" style="animation-delay:{d:.2f}s">')
        blk = lines[ro + 1:rc]
        if n == 12:
            cs = find_in(blk, lambda s: 'class="peakglow"' in s)
        else:
            cs = find_in(blk, lambda s: 'class="bar b' in s and f'b{n}"' in s)
        ce = find_in(blk, lambda s: f'class="dot d{n}"' in s, cs)
        assert blk[cs].strip().startswith("<rect") and blk[ce].strip().startswith("<circle")
        o.extend(blk[:cs])
        o.append(f'<g class="row" style="animation-delay:{d + 0.12:.2f}s">')
        if n in pulse_of:
            cls, ph = pulse_of[n]
            o.append(f'<g class="{cls}" style="animation-delay:{ph}">')
            o.extend(blk[cs:ce + 1])
            o.append("</g>")
        else:
            o.extend(blk[cs:ce + 1])
        o.append("</g>")
        o.extend(blk[ce + 1:])
        o.append("</g>")

    # 网格线组 .fade(0.05)
    o.append('<g class="fade" style="animation-delay:0.05s">')
    o.extend(lines[grid_g:grid_g_close + 1])
    o.append("</g>")

    # 其余原样（zeband/呼吸高亮/cmpband 遗留覆盖层 + 边框 + 源尾注释 + </svg>）
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
    # 稳态族 ≥2
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
    print("[make_anim_power_compare_hk11 v4]",
          "row_g=", len(re.findall(r'class="r\d+ row"', data)),
          "sweepband=", data.count('class="sweepband"'),
          "pulse=", len(re.findall(r'class="(pulse|pulse-b)"', data)),
          "fade=", data.count('class="fade"'))
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
# ymzhu 2026-10-28 17:12
