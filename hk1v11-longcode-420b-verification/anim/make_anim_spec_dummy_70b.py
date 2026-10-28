#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_dummy_70b.py — v4（Motion Kit v4，整体重写；v2 类名/delay 逻辑不沿用）

MOTION_KIT.md §6.7 规格（1200×600）：
- 行序：标题(0) → ①(0.15) ②(0.3) ③(0.45) ④(0.6) → LSP(0.9) → Active(1.05)
        → Config(1.2) → 注释(1.4)。一次性总长 = 1.75(draw)+0.6 = 2.35s ≤ 2.5s。
- draw（§5：delay ≥ 两端面板 delay+0.55）：
  · 3 个 pipeline 箭头 delay 0.85/1.0/1.15（=步骤 0.3/0.45/0.6 + 0.55）
  · 3 个 Before→After 行箭头 delay 1.45/1.6/1.75（=行 0.9/1.05/1.2 + 0.55），
    各自的“413b/420b”标签随箭头同拍 fade（不再先于箭头出现）
- step：4 框循环 delay 0 / -1.5 / -3 / -4.5s（6s 周期）
- 列车：3 pipeline 箭头各 2 包 + flowtail（0.7s，边间错 phase 0.15s）；
  3 行箭头各 2 包（1.15s，行间错 phase 0.2s）。箭头均在盒间净空隙内，不穿文字。
- 行波：After ENC 盒 D 格（D·70b×N / D·140b）+ K5~K8（Active/Config 各 1）
  共 4 格 cellwave（0.3s 递增，2.8s）
- 脉冲：Active 行 “D · 70b×N” 盒 .pulse（琥珀，delay -0.7，套在 cellwave 外层）
- 扫光：底部 dummy 注释区 sweepband ×1（§4 配方：userSpaceOnUse 渐变跨 P，
  stops 0/.46/.5/.54/1，clipPath 区域副本，rect 宽 P + --sweepP）。
  区域 = 注释文本带 x[52,532] y[532,572]，R=480 → P=R+240=720；
  rect/gradient 起点 X0=52-0.54P=-337，光带 t=0 完整藏在区域左侧，随 translateX(P)
  从左到右扫过区域（约 6s 扫完，8s 循环）——即 §4 声明的效果。
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无
  script；kit CSS §2 逐字嵌入；源 defs（marker 箭头）+ 背景 rect 保留，扫光
  渐变/clipPath 按铁律 3 v4 新增项插入源 defs 内；reduced-motion 用 kit 原文；
  确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "spec_dummy_70b.svg"
OUT = BASE / "anim" / "spec_dummy_70b.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类）
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

# 行箭头（Before→After）几何：源 line x1=630 x2=690，y = 220/340/460
ROW_ARROW_Y = [220, 340, 460]
# pipeline 箭头几何：x1/x2 对 + y=106
PIPE_ARROWS = [(314, 344), (604, 634), (894, 924)]
# 列车相位（负 delay = 相位偏移，|d| ≤ 周期；同族错相位）
PIPE_PHASE = [("-0.05s", "-0.4s"), ("-0.2s", "-0.55s"), ("-0.35s", "-0.7s")]
ROW_PHASE = [("-0.1s", "-0.65s"), ("-0.3s", "-0.85s"), ("-0.5s", "-1.05s")]

# 扫光带（§4 配方）：区域 = 底部注释带 x[52,532] y[532,572]（宽 R=480）
SWEEP = {"RL": 52, "R": 480, "Y": 532, "H": 40}
SWEEP["P"] = SWEEP["R"] + 240                       # 720
SWEEP["X0"] = SWEEP["RL"] - int(0.54 * SWEEP["P"])  # -337：t=0 光带藏于区域左外侧


def flowdot(d, delay, dur):
    return ('<path class="flowdot" d="%s" stroke="#2563eb" pathLength="100" '
            'style="animation-duration:%s;animation-delay:%s"/>' % (d, dur, delay))


def flowtail(d, delay, dur):
    return ('<path class="flowtail" d="%s" stroke="#2563eb" pathLength="100" '
            'style="animation-duration:%s;animation-delay:%s"/>' % (d, dur, delay))


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def find_txt(prefix, start=2):
        for i in range(start, end):
            s = lines[i].strip()
            if s.startswith("<text") and f">{prefix}" in s and s.endswith("</text>"):
                return i
        raise AssertionError(f"text not found: {prefix}")

    # ---- 结构锚点（源行号，0 基；全部 assert 保护） ----
    title_i = find_txt("非 413b 整数倍数据处理")
    sub_i = find_txt("编码后去掉补齐的 dummy", title_i)
    s1 = find_txt("① 补 Dmy(0) 至 413b 整数倍", sub_i)
    s2 = find_txt("② 加扰（SCR EN=1）", s1)
    s3 = find_txt("③ 413b/420b 编码", s2)
    s4 = find_txt("④ 去 dummy · 70b 对齐发送", s3)
    lsp = find_txt("LSP", s4)
    active = find_txt("Active Line", lsp)
    config = find_txt("Config Line", active)
    note_i = find_txt("多通道对齐示例", config)
    assert title_i < sub_i < s1 < s2 < s3 < s4 < lsp < active < config < note_i, "锚点顺序异常"

    # pipeline 箭头 = 步骤 text 的下一行 <line>（断言 x 坐标匹配）
    pipe_arrow_idx = []
    for k, (txt_i, (ax1, ax2)) in enumerate(zip((s1, s2, s3), PIPE_ARROWS)):
        li = txt_i + 1
        assert lines[li].strip().startswith("<line"), f"步骤{k+1} 后应为箭头 line"
        assert f'x1="{ax1}"' in lines[li] and f'x2="{ax2}"' in lines[li], f"pipeline 箭头 {k+1} 坐标异常"
        pipe_arrow_idx.append(li)

    # 行范围：左标签 rect（text 前一行）起，至下一行标签 rect 前
    lsp_start, lsp_end = lsp - 1, active - 1
    act_start, act_end = active - 1, config - 1
    cfg_start, cfg_end = config - 1, note_i
    for st in (lsp_start, act_start, cfg_start):
        assert lines[st].strip().startswith("<rect"), "行标签 text 前一行应为 rect"

    def cell_idx(row_start, row_end, label):
        """row 内 rect+text 单元格对（text 内容精确匹配 label）。"""
        for i in range(row_start, row_end):
            s = lines[i].strip()
            if s.startswith("<text") and f">{label}</text>" in s:
                assert lines[i - 1].strip().startswith("<rect"), f"{label} 前应为 rect"
                return i - 1
        raise AssertionError(f"cell not found: {label}")

    def row_arrow_idx(row_start, row_end):
        for i in range(row_start, row_end):
            s = lines[i].strip()
            if s.startswith("<line") and 'x1="630"' in s and 'x2="690"' in s:
                return i
        raise AssertionError("row arrow not found")

    def label413_idx(row_start, row_end):
        for i in range(row_start, row_end):
            s = lines[i].strip()
            if s.startswith("<text") and ">413b/420b</text>" in s:
                return i
        raise AssertionError("413b/420b label not found")

    lsp_arrow, lsp_413 = row_arrow_idx(lsp_start, lsp_end), label413_idx(lsp_start, lsp_end)
    act_arrow, act_413 = row_arrow_idx(act_start, act_end), label413_idx(act_start, act_end)
    cfg_arrow, cfg_413 = row_arrow_idx(cfg_start, cfg_end), label413_idx(cfg_start, cfg_end)
    assert len({lsp_413, act_413, cfg_413}) == 3, "三个 413b/420b 标签应互异"

    # cellwave 单元格（顺序 = 波传播序）：Active D·70b×N → Active K5~K8
    #   → Config D·140b → Config K5~K8；pulse 套 Active D·70b×N 外层
    cells = [
        (cell_idx(act_start, act_end, "D · 70b×N"), "pulse"),
        (cell_idx(act_start, act_end, "K5~K8"), None),
        (cell_idx(cfg_start, cfg_end, "D · 140b"), None),
        (cell_idx(cfg_start, cfg_end, "K5~K8"), None),
    ]

    def drawify(i, delay):
        return lines[i].replace(
            "<line ", f'<line class="draw" pathLength="100" style="animation-delay:{delay}s" ', 1)

    # 源 defs 收尾 </defs> 行号（扫光渐变/clipPath 插在其前，铁律 3/4）
    dclose = next(i for i in range(2, title_i) if lines[i].strip() == "</defs>")
    sp = SWEEP
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

    # ---- 组装 ----
    o = []
    o.append(lines[0])        # <svg> 开标签原样
    o.append(lines[1])        # 行2：字体 <style>（保留）
    o.append("<style>\n" + KIT_CSS + "\n</style>")  # 行3：kit CSS §2 逐字
    o.extend(lines[2:dclose])  # 源 defs 内容（marker 箭头）
    o.extend(sweep_defs)       # v4 新增：扫光渐变 + clipPath（仅扫光带用）
    o.extend(lines[dclose:title_i])  # </defs> + 白底

    # 标题 head(0)
    o.append('<g class="head">')
    o.extend(lines[title_i:sub_i + 1])
    o.append("</g>")

    # ①②③④：row 入场 0.15/0.3/0.45/0.6 + .step 循环 0/-1.5/-3/-4.5；
    # ①→②②→③③→④ pipeline 箭头：draw（0.85/1.0/1.15 = 下游步骤+0.55）
    # + 列车 2 包 + flowtail（0.7s，错 phase），随 fade 同拍显形
    step_rows = [(s1, 0.15), (s2, 0.3), (s3, 0.45), (s4, 0.6)]
    step_phase = ["0s", "-1.5s", "-3s", "-4.5s"]
    for n, (txt_i, rd) in enumerate(step_rows):
        o.append(f'<g class="row" style="animation-delay:{rd}s">')
        o.append(f'<g class="step" style="animation-delay:{step_phase[n]}">')
        o.append(lines[txt_i - 1])  # 步骤框 rect
        o.append(lines[txt_i])      # 步骤标签 text
        o.append("</g>")
        o.append("</g>")
        if n < 3:
            delay = round(0.85 + 0.15 * n, 2)
            x1, x2 = PIPE_ARROWS[n]
            d = f"M {x1} 106 L {x2} 106"
            o.append(f'<g class="fade" style="animation-delay:{delay}s">')
            o.append(drawify(pipe_arrow_idx[n], delay))
            o.append(flowdot(d, PIPE_PHASE[n][0], "0.7s"))
            o.append(flowdot(d, PIPE_PHASE[n][1], "0.7s"))
            o.append(flowtail(d, PIPE_PHASE[n][0], "0.7s"))
            o.append("</g>")

    # 行发射器：行组内嵌 cellwave/pulse；行箭头线与其 413b/420b 标签移出行组
    def emit_row(start, stop, rd, cellset, skip=()):
        o.append(f'<g class="row" style="animation-delay:{rd}s">')
        cellmap = {c[0]: (c[1], k) for k, c in enumerate(cellset)}
        i = start
        while i < stop:
            if i in skip:
                i += 1
                continue
            if i in cellmap:
                kind, k = cellmap[i]
                cw = (f'<g class="cellwave" style="animation-duration:2.8s;'
                      f'animation-delay:{k * 0.3:.1f}s">')
                if kind == "pulse":
                    o.append('<g class="pulse" style="animation-delay:-0.7s">')
                    o.append(cw)
                    o.append(lines[i])
                    o.append(lines[i + 1])
                    o.append("</g>")
                    o.append("</g>")
                else:
                    o.append(cw)
                    o.append(lines[i])
                    o.append(lines[i + 1])
                    o.append("</g>")
                i += 2
                continue
            o.append(lines[i])
            i += 1
        o.append("</g>")

    # LSP 0.9 / Active 1.05 / Config 1.2
    emit_row(lsp_start, lsp_end, 0.9, [], skip={lsp_arrow, lsp_413})
    emit_row(act_start, act_end, 1.05, [cells[0], cells[1]], skip={act_arrow, act_413})
    emit_row(cfg_start, cfg_end, 1.2, [cells[2], cells[3]], skip={cfg_arrow, cfg_413})

    # 行箭头：draw 1.45/1.6/1.75（=行 delay+0.55）+ 列车 2 包（1.15s，错 phase）
    # + 413b/420b 标签同拍 fade（§5：先容器后内容再箭头）
    for n, (ai, ti) in enumerate([(lsp_arrow, lsp_413), (act_arrow, act_413), (cfg_arrow, cfg_413)]):
        delay = round(1.45 + 0.15 * n, 2)
        y = ROW_ARROW_Y[n]
        d = f"M 630 {y} L 690 {y}"
        o.append(f'<g class="fade" style="animation-delay:{delay}s">')
        o.append(drawify(ai, delay))
        o.append(lines[ti])
        o.append(flowdot(d, ROW_PHASE[n][0], "1.15s"))
        o.append(flowdot(d, ROW_PHASE[n][1], "1.15s"))
        o.append("</g>")

    # 扫光带：区域内容（注释文字）之下、白底之上；随后注释 head(1.4) 压在其上
    o.append(f'<g clip-path="url(#sweepC-1)"><rect class="sweepband" x="{sp["X0"]}" '
             f'y="{sp["Y"]}" width="{sp["P"]}" height="{sp["H"]}" fill="url(#sweepG-1)" '
             f'style="--sweepP:{sp["P"]}px"/></g>')

    # 底部注释 head(1.4)
    o.append('<g class="head" style="animation-delay:1.4s">')
    o.append(lines[note_i])
    o.append("</g>")

    o.append(lines[end])
    text = eol.join(o).replace("\n", eol)
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
    res["kit_train"] = "OK" if ".flowdot{" in data and "stroke-width:3.5" in data else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data and 'class="sweepband"' in data else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    res["rmfix"] = "OK" if ".flowdot,.flowtail,.sweepband{display:none!important}" in data else "NG"
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_spec_dummy_70b v4]",
          f"draw={data.count('class=\"draw\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"flowtail={data.count('class=\"flowtail\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"pulse={data.count('class=\"pulse\"')}",
          f"sweepband={data.count('class=\"sweepband\"')}",
          f"step={data.count('class=\"step\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}",
          f"fade={data.count('class=\"fade\"')}")
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 16:58
