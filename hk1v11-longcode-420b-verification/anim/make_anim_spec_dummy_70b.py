#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_spec_dummy_70b.py — v2（Motion Kit v2，整体重写，不基于 v1 逻辑）

按 MOTION_KIT.md §4.7 规格：
- 行序：标题(0) → ①(0.15) ②(0.3) ③(0.45) ④(0.6) → LSP(0.9) → Active(1.05)
        → Config(1.2) → 注释(1.4)
- draw：3 个 pipeline 箭头（delay 0.5/0.65/0.8）、3 个 Before→After 行箭头
        （delay 1.25/1.4/1.55）= 源面板 delay + 0.35
- step：4 个步骤框 .step，delay 0 / -1.5 / -3 / -4.5s（6s 循环）
- flow：3 个 pipeline 箭头 2 包列车（0.7s 周期，边间错 phase 0.23s）；
        3 个行箭头各 2 包（0.7s 周期，行间错 phase 0.23s）
- cellwave：After ENC 盒里的 D 格（"D · 70b×N"、"D · 140b"）+ K5~K8 格
        （Active/Config 各 1），0.3s 递增，2.8s 周期
- glow：Active 行 "D · 70b×N" 盒 glow-o（套在 cellwave 外层）
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  字体 <style> 保留在行 2，motion kit <style> 为行 3；reduced-motion 用 kit 原文。
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

MOTION_STYLE = (
    "<style>\n"
    ".row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}\n"
    ".head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}\n"
    "@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}\n"
    ".draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}\n"
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}\n"
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}\n"
    "@keyframes fadeIn{to{opacity:1}}\n"
    ".fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}\n"
    ".breathe{animation:br 3.2s ease-in-out infinite}\n"
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}\n"
    ".cellwave{animation:wave 3s ease-in-out infinite}\n"
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}\n"
    ".march{animation:march 1.8s linear infinite}\n"
    "@keyframes march{to{stroke-dashoffset:-16}}\n"
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}\n"
    "@keyframes flow{to{stroke-dashoffset:-100}}\n"
    ".glow-b{animation:glowB 2.8s ease-in-out infinite}\n"
    "@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}\n"
    ".glow-g{animation:glowG 2.8s ease-in-out infinite}\n"
    "@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}\n"
    ".glow-o{animation:glowO 2.8s ease-in-out infinite}\n"
    "@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}\n"
    ".step{animation:stepLit 6s ease-in-out infinite}\n"
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}\n"
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}\n"
    "</style>"
)

# 行箭头（Before→After）几何：源 line x1=630 x2=690，y = 220/340/460
ROW_ARROW_Y = {"LSP": 220, "Active": 340, "Config": 460}
# pipeline 箭头几何：x1/x2 对 + y=106
PIPE_ARROWS = [(314, 344), (604, 634), (894, 924)]


def flowdot(d, delay, dur="0.7s", width="2"):
    return (f'<path class="flowdot" d="{d}" stroke="#2563eb" stroke-width="{width}" '
            f'pathLength="100" style="animation-duration:{dur};animation-delay:{delay}s"/>')


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"
    end = len(lines) - 1

    def find_txt(prefix, start=2):
        for i in range(start, end):
            s = lines[i].strip()
            if s.startswith("<text") and f">{prefix}" in s and s.endswith("</text>"):
                return i
        raise AssertionError(f"text not found: {prefix}")

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
            if s.startswith("<text") and f">{label}<" in s:
                assert lines[i - 1].strip().startswith("<rect"), f"{label} 前应为 rect"
                return i - 1
        raise AssertionError(f"cell not found: {label}")

    # 行箭头（line x1="630" x2="690"）
    def row_arrow_idx(row_start, row_end):
        for i in range(row_start, row_end):
            s = lines[i].strip()
            if s.startswith("<line") and 'x1="630"' in s and 'x2="690"' in s:
                return i
        raise AssertionError("row arrow not found")

    lsp_arrow = row_arrow_idx(lsp_start, lsp_end)
    act_arrow = row_arrow_idx(act_start, act_end)
    cfg_arrow = row_arrow_idx(cfg_start, cfg_end)

    # cellwave 单元格（顺序 = 波传播序）：Active D·70b×N → Active K5~K8
    #   → Config D·140b → Config K5~K8；glow-o 套 Active D·70b×N 外层
    cells = [
        (cell_idx(act_start, act_end, "D · 70b×N"), "glow"),
        (cell_idx(act_start, act_end, "K5~K8"), None),
        (cell_idx(cfg_start, cfg_end, "D · 140b"), None),
        (cell_idx(cfg_start, cfg_end, "K5~K8"), None),
    ]

    def drawify(idx, delay):
        return lines[idx].replace(
            "<line ", f'<line class="draw" pathLength="100" style="animation-delay:{delay}s" ', 1)

    # ---- 组装 ----
    o = []
    o.append(lines[0])        # <svg>（开标签原样）
    o.append(lines[1])        # 行2：字体 <style>（保留）
    o.append(MOTION_STYLE)    # 行3：motion kit <style>
    o.extend(lines[2:title_i])  # defs + 白底

    # 标题 0
    o.append('<g class="head">')
    o.extend(lines[title_i:sub_i + 1])
    o.append("</g>")

    # ①②③④：row 入场 0.15/0.3/0.45/0.6 + .step 循环 0/-1.5/-3/-4.5
    #   ①~③ 各带 pipeline 箭头（draw + flow 2 包列车，边间错 phase 0.23s）
    step_rows = [(s1, 0.15, 0), (s2, 0.3, 1), (s3, 0.45, 2), (s4, 0.6, None)]
    step_phase = [0, -1.5, -3, -4.5]
    for n, (txt_i, rd, pipe_n) in enumerate(step_rows):
        o.append(f'<g class="row" style="animation-delay:{rd}s">')
        o.append(f'<g class="step" style="animation-delay:{step_phase[n]}s">')
        o.append(lines[txt_i - 1])  # 步骤框 rect
        o.append(lines[txt_i])      # 步骤标签 text
        o.append("</g>")
        o.append("</g>")
        if pipe_n is not None:
            ai = pipe_arrow_idx[pipe_n]
            base = 0.5 + pipe_n * 0.23  # 源面板 delay+0.35 = 0.5/0.65/0.8
            o.append(drawify(ai, f"{base}"))
            x1, x2 = PIPE_ARROWS[pipe_n]
            d = f"M {x1} 106 L {x2} 106"
            for dd in (base, base + 0.35):
                o.append(flowdot(d, dd))

    # 行发射器：行组内嵌 cellwave/glow，行箭头 draw+flow 移出行组（画在上层）
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
                delay = f"animation-duration:2.8s;animation-delay:{k * 0.3:.1f}s"
                if kind == "glow":
                    o.append(f'<g class="glow-o" style="animation-delay:-0.7s">')
                    o.append(f'<g class="cellwave" style="{delay}">')
                    o.append(lines[i])
                    o.append(lines[i + 1])
                    o.append("</g>")
                    o.append("</g>")
                else:
                    o.append(f'<g class="cellwave" style="{delay}">')
                    o.append(lines[i])
                    o.append(lines[i + 1])
                    o.append("</g>")
                i += 2
                continue
            o.append(lines[i])
            i += 1
        o.append("</g>")

    # LSP 0.9 / Active 1.05 / Config 1.2（行箭头原线跳过，改在行组外 draw 输出）
    emit_row(lsp_start, lsp_end, 0.9, [], skip={lsp_arrow})
    emit_row(act_start, act_end, 1.05, [cells[0], cells[1]], skip={act_arrow})
    emit_row(cfg_start, cfg_end, 1.2, [cells[2], cells[3]], skip={cfg_arrow})

    # 行箭头 draw（源面板 delay+0.35 = 1.25/1.4/1.55）+ flow 2 包（行间错 phase 0.23s）
    for n, (ai, rd, name) in enumerate(
            [(lsp_arrow, 1.25, "LSP"), (act_arrow, 1.4, "Active"), (cfg_arrow, 1.55, "Config")]):
        o.append(drawify(ai, f"{rd}"))
        y = ROW_ARROW_Y[name]
        d = f"M 630 {y} L 690 {y}"
        for dd in (rd, rd + 0.35):
            o.append(flowdot(d, dd))

    # 底部注释 1.4
    o.append('<g class="head" style="animation-delay:1.4s">')
    o.append(lines[note_i])
    o.append("</g>")

    o.append(lines[end])
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
    res["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["rmfix"] = "OK" if (
        re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
        and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)
    ) else "NG"
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_spec_dummy_70b]",
          f"draw={data.count('class=\"draw\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"cellwave={data.count('class=\"cellwave\"')}",
          f"glow-o={data.count('class=\"glow-o\"')}",
          f"step={data.count('class=\"step\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}")
    ok = True
    for k, v in res.items():
        print(f"  {k}: {v}")
        ok &= (v == "OK")
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-27 10:20
