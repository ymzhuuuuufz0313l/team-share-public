#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_power_composition_donut_1v11_1v22.py — v4（Motion Kit v4，整体重写）

power_composition_donut_1v11_1v22（1200×578，双环形图，静态版=站点根目录同名 svg）规格：
- 入场（总长 ≤2.5s）：
  · 标题 .head(0)、副标题 .head(0.1)
  · 1V11 图例行 .row(0.2)、1V22 图例行 .row(0.35)
  · 左环面板 .row(0.5)、右环面板 .row(0.75)
  · 环内扇区 circle 依次 .fade（左 9 扇区 0.65+0.07k，右 7 扇区 0.9+0.07k）——扇区按占比次序逐个点亮
    （注：扇区为 pathLength 弧线技巧，其 stroke-dasharray 是几何本身，禁用 .draw 覆盖）
  · 标签组 .fade（左 1.3+0.05k，右 1.45+0.05k）、中心总数 .fade（1.7 / 1.75）
  · 末项 1.75+0.6 = 2.35s ≤ 2.5s
- 稳态（2 族，纯呼吸系；用户 2026-10-28 验收：不需要行进效果，列车整体移除——
  donut 永不加行进列车；晚间二轮加密=扇区环向呼吸波）：
  · 行波 A（图例）：左右图例 top-3 图例行（色块 rect + 文字 text 成对）各包一层 .cellwave
    （opacity .72 呼吸，kit 默认 2.6s），相位错开 0.6s（左 0/0.6/1.2s；右 1.3/1.9/2.5s
    跨侧错拍）——top-3 行与两环 top1 扇区 pulse 呼应；
  · 行波 B（环向慢波）：两环非 top1 扇区（左 8 + 右 6）逐个包 .cellwave，按环向顺序
    （=源绘制顺序）相位递增 0.3s/扇区、duration 3.8s（左 delay -0.3k，k=1..8；
    右 delay -(1.9+0.3k)，k=1..6，右环基相 1.9s=半周期跨侧错拍）——形成绕环慢波；
    3.8s ≠ 图例 2.6s，两波永不锁相（不与图例行波同相）；top1 扇区已 pulse 不叠波；
  · 脉冲 ×2（错相位）：左环 top1 扇区（短编码解码 41.8%）pulse-t(-0.7s)；
    右环 top1 扇区（LC_CSPIF_L0 35.4%）pulse(-2.1s)
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs（glowF filter）/背景 rect 保留（assert 保护）；
  源字体 <style> 原样保留；reduced-motion 双保险；确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice")
SRC = BASE / "power_composition_donut_1v11_1v22.svg"
OUT = BASE / "anim" / "power_composition_donut_1v11_1v22.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类；与 canonical 站一致）
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


def legend_wave(blk, delays):
    """图例块：前 len(delays) 条图例行（色块 rect + 文字 text 成对）包 .cellwave。

    色块判定 = <rect 且带 fill-opacity（徽章 rect 无该属性，天然排除）；
    其余行原样输出。确定性：只依赖源块行序。
    """
    out, k, i = [], 0, 0
    while i < len(blk):
        if blk[i].strip().startswith("<rect") and "fill-opacity" in blk[i]:
            assert blk[i + 1].strip().startswith("<text"), "色块后应紧跟文字"
            if k < len(delays):
                out.append(f'<g class="cellwave" style="animation-delay:{delays[k]:g}s">')
                out.extend(blk[i:i + 2])
                out.append("</g>")
            else:
                out.extend(blk[i:i + 2])
            k += 1
            i += 2
        else:
            out.append(blk[i])
            i += 1
    assert k >= len(delays), f"图例行应 ≥{len(delays)}（供 cellwave），实得 {k}"
    return out


def sector_wave(line, fade_d, wave_d):
    """非 top1 扇区：入场 .fade 外壳 + 环向呼吸 .cellwave 内壳（duration 3.8s）。

    扇区 circle 本行零改动（class/几何/dasharray 原样）——入场与稳态分壳嵌套
    （§3 冲突规则）；wave_d = 负相位偏移，环向顺序每扇区 -0.3s 递增。
    """
    return [
        f'<g class="fade" style="animation-delay:{fade_d:.2f}s">',
        f'<g class="cellwave" style="animation-duration:3.8s;animation-delay:{wave_d:g}s">',
        line,
        "</g>",
        "</g>",
    ]


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>" or lines[-1].strip().startswith("<!--"), \
        "末行应为 </svg> 或尾注释"
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
            t = lines[i].strip()
            if t.startswith("<g ") or t == "<g>":
                depth += 1
            elif t == "</g>":
                if depth == 0:
                    return i
                depth -= 1
        raise AssertionError("group close not found")

    # ---- 结构锚点 ----
    style_close = find(lambda s: s.rstrip().endswith("</style>"))
    title_i = find(lambda s: 'class="f-cjk title"' in s)
    sub_i = find(lambda s: 'class="f-cjk subtitle"' in s)
    bg_i = find(lambda s: s.strip() == '<rect width="1200" height="578" fill="#f4f1ea"/>')
    leg1 = find(lambda s: s.strip() == '<g data-gen="1V11">', bg_i)
    leg2 = find(lambda s: s.strip() == '<g data-gen="1V22">', group_close(leg1) + 1)
    donL = find(lambda s: 'class="donut donutL"' in s, group_close(leg2) + 1)
    donR = find(lambda s: 'class="donut donutR"' in s, group_close(donL) + 1)
    donL_c, donR_c = group_close(donL), group_close(donR)
    assert 'filter id="glowF"' in "\n".join(lines[style_close + 1:title_i]), "源 defs(glowF) 应保留"

    # ---- 组装 ----
    o = []
    o.extend(lines[0:style_close + 1])
    o.append("<style>\n" + KIT_CSS + "\n</style>")
    o.extend(lines[style_close + 1:title_i])          # 源 defs + 背景 rect

    # 标题 / 副标题
    o.append(lines[title_i].replace('class="f-cjk title"',
                                    'class="f-cjk title head" style="animation-delay:0s"', 1))
    o.append(lines[sub_i].replace('class="f-cjk subtitle"',
                                  'class="f-cjk subtitle head" style="animation-delay:0.1s"', 1))
    o.extend(lines[sub_i + 1:leg1])                   # （无中间内容，防御性保留）

    # 图例行：top-3 图例行各包 .cellwave（呼吸，相位 0.6s 错开；跨侧错拍）
    o.append('<g data-gen="1V11" class="row" style="animation-delay:0.2s">')
    o.extend(legend_wave(lines[leg1 + 1:group_close(leg1)], (0.0, 0.6, 1.2)))
    o.append("</g>")
    o.append('<g data-gen="1V22" class="row" style="animation-delay:0.35s">')
    o.extend(legend_wave(lines[leg2 + 1:group_close(leg2)], (1.3, 1.9, 2.5)))
    o.append("</g>")

    # 左环：面板 row(0.5)；扫光环 fade；扇区依次 fade（top1 另包 pulse-t）；
    #        非 top1 扇区 fade 外壳 + cellwave 环向慢波（3.8s，delay -0.3k）；
    #        标签组 fade；中心 fade(1.7)
    o.append(lines[donL].replace('class="donut donutL"',
                                 'class="donut donutL row" style="animation-delay:0.5s"', 1))
    blk = lines[donL + 1:donL_c]
    # 白色扫光环（源 CSS .sweep{opacity:.08}）——fade 必须包外壳，禁直接加 class
    # （kit .fade 会使 opacity 终值强制为 1，覆盖源 0.08）
    o.append('<g class="fade" style="animation-delay:0.55s">')
    o.append(blk[0])
    o.append("</g>")
    sec = [i for i, s in enumerate(blk) if 'class="sector' in s]
    assert len(sec) == 9, f"左环 sector 应 9（含 top1），实得 {len(sec)}"
    first_lbl = min(i for i, s in enumerate(blk) if s.strip() == '<g class="lbl">')
    # 逐行发射扇区段
    o.append('<g class="fade" style="animation-delay:0.65s">')
    o.append('<g class="pulse-t" style="animation-delay:-0.7s">')
    o.append(blk[sec[0]])
    o.append("</g>")
    o.append("</g>")
    for k, i in enumerate(sec[1:], start=1):
        o.extend(sector_wave(blk[i], 0.65 + 0.07 * k, -0.3 * k))
    # 标签组（上限 = center 组行 ci）
    ci = [i for i, s in enumerate(blk) if 'class="center centerL"' in s][0]
    li = first_lbl
    k = 0
    while li < ci:
        if blk[li].strip() == '<g class="lbl">':
            lc = li
            depth = 0
            while True:
                t = blk[lc].strip()
                if lc > li and (t.startswith("<g ") or t == "<g>"):
                    depth += 1
                elif t == "</g>":
                    if depth == 0:
                        break
                    depth -= 1
                lc += 1
            o.append(f'<g class="fade" style="animation-delay:{1.3 + 0.05 * k:.2f}s">')
            o.extend(blk[li:lc + 1])
            o.append("</g>")
            k += 1
            li = lc + 1
        else:
            if not ('class="center centerL"' in blk[li]):
                o.append(blk[li])
            li += 1
    # 中心组
    cc = ci
    depth = 0
    while True:
        t = blk[cc].strip()
        if cc > ci and (t.startswith("<g ") or t == "<g>"):
            depth += 1
        elif t == "</g>":
            if depth == 0:
                break
            depth -= 1
        cc += 1
    o.append(blk[ci].replace('class="center centerL"',
                             'class="center centerL fade" style="animation-delay:1.7s"', 1))
    o.extend(blk[ci + 1:cc + 1])
    o.append("</g>")                                   # 关闭 donutL row

    # 右环：面板 row(0.75)；扇区 fade 0.9+0.07k（top1 pulse -2.1）；非 top1 扇区
    #        cellwave 环向慢波（3.8s，delay -(1.9+0.3k)，基相 1.9s=半周期跨侧错拍）；
    #        标签 1.45+0.05k；中心 1.75
    o.append(lines[donR].replace('class="donut donutR"',
                                 'class="donut donutR row" style="animation-delay:0.75s"', 1))
    blk = lines[donR + 1:donR_c]
    o.append('<g class="fade" style="animation-delay:0.8s">')
    o.append(blk[0])
    o.append("</g>")
    sec = [i for i, s in enumerate(blk) if 'class="sector' in s]
    assert len(sec) == 7, f"右环 sector 应 7（含 top1），实得 {len(sec)}"
    o.append('<g class="fade" style="animation-delay:0.9s">')
    o.append('<g class="pulse" style="animation-delay:-2.1s">')
    o.append(blk[sec[0]])
    o.append("</g>")
    o.append("</g>")
    for k, i in enumerate(sec[1:], start=1):
        o.extend(sector_wave(blk[i], 0.9 + 0.07 * k, -(1.9 + 0.3 * k)))
    ci = [i for i, s in enumerate(blk) if 'class="center centerR"' in s][0]
    li = min(i for i, s in enumerate(blk) if s.strip() == '<g class="lbl">')
    k = 0
    while li < ci:
        if blk[li].strip() == '<g class="lbl">':
            lc = li
            depth = 0
            while True:
                t = blk[lc].strip()
                if lc > li and (t.startswith("<g ") or t == "<g>"):
                    depth += 1
                elif t == "</g>":
                    if depth == 0:
                        break
                    depth -= 1
                lc += 1
            o.append(f'<g class="fade" style="animation-delay:{1.45 + 0.05 * k:.2f}s">')
            o.extend(blk[li:lc + 1])
            o.append("</g>")
            k += 1
            li = lc + 1
        else:
            if 'class="center centerR"' not in blk[li]:
                o.append(blk[li])
            li += 1
    cc = ci
    depth = 0
    while True:
        t = blk[cc].strip()
        if cc > ci and (t.startswith("<g ") or t == "<g>"):
            depth += 1
        elif t == "</g>":
            if depth == 0:
                break
            depth -= 1
        cc += 1
    o.append(blk[ci].replace('class="center centerR"',
                             'class="center centerR fade" style="animation-delay:1.75s"', 1))
    o.extend(blk[ci + 1:cc + 1])
    o.append("</g>")                                   # 关闭 donutR row

    o.extend(lines[donR_c + 1:])                       # </svg> + 源尾注释

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
    sector_waves = len(re.findall(r'class="cellwave" style="animation-duration:3\.8s', data))
    assert sector_waves == 14, f"环向扇区波应 14（左8+右6），实得 {sector_waves}"
    print("[make_anim_power_composition_donut_1v11_1v22 v4.1]",
          "head=", len(re.findall(r'class="f-cjk (title|subtitle) head"', data)),
          "row=", len(re.findall(r'class="[^"]*row"', data)),
          "cellwave=", data.count('class="cellwave"'),
          "(legend 6 + sector", sector_waves, ")",
          "pulse=", len(re.findall(r'class="(pulse|pulse-t)"', data)))
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
# ymzhu 2026-10-28 21:05
