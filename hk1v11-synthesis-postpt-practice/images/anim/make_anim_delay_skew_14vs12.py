#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_delay_skew_14vs12.py — v4（Motion Kit v4，整体重写；旧版 tick 呼吸/行呼吸不沿用）

delay_skew_14vs12（1440×950，三面板 STA skew 讲解图，静态版=images/ 同名 svg）规格：
- 入场（总长 ≤2.5s，先容器→再内容→最后箭头）：
  · 页眉：kicker .head(0)、主标题 .head(0.05)、图例行簇 .row(0.15)
  · 面板① .row(0.2)：面板矩形随容器；注解框/坐标轴 .fade(0.25~0.6)；
    六支量测箭头 .draw（0.8/0.95/1.0/1.1/1.25/1.45，全部 ≥ 面板 0.2+0.55），
    箭头端帽/标签 .fade(1.45~1.75)
  · 面板② .row(0.5)：轴/表头 .fade(0.85~0.95)、阈值线对 .fade(1.0)、
    三行场景 .row(1.1/1.25/1.4)、结论 .fade(1.55)
  · 面板③ .row(0.8)：包络带 .fade(1.15/1.2)、阈值线对 .fade(1.3)、
    两支标记箭头 .draw(1.45/1.55 ≥ 0.8+0.55)、徽章框 .head(1.7)
  · 页脚 .fade(1.75)、角标铭牌 .head(1.8)；末项 1.8+0.55=2.35s
- 稳态（3 族）：
  · 列车：① 时钟 arrival 边（#1c2534）与数据 arrival 边（#0e7490）各 2 包+拖尾，
    1.5s/趟（时钟 phase 0/-0.75，数据 -0.4/-1.15）——两条 arrival 数据流；
    路径沿线无文字穿越（标签均在箭头线上/下方留白处）
  · 脉冲 ×3（错相位）：① slack 绿线组 .pulse-t(-0.7s)；② 12/14 阈值线对 .pulse-b(-2.1s)；
    ③ "STATUS: NOT YET CONFIRMED OK" .pulse(-1.4s)
  · 扫光 sweepband ×1（§4 配方，琥珀）：② 场景表三行区（x60..680 / y660..788，P=860）
    ——逐场景扫描语义；置于面板底色之上、行文字之下
- 源样式中和（assert 保护，均因 kit 定义了同名 keyframes）：
  · 6 条 class="march" 阈值虚线（源 dasharray 6,4 ≠ -16 位移周期，行进会跳变）
    → 行内 style="animation:none"
  · rowB 行洗矩形：静态剥离版漏带 opacity（静态中渲染为实心琥珀、盖住整表），
    输出恢复原动画设计的中值洗底 opacity:.08（仅动画版，静态版不改）
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs（marker/clipRows2/grid）/背景 rect 保留（assert 保护）；
  源字体 <style> 原样保留（.p1 残留 delay 由行内覆盖）；reduced-motion 双保险；
  确定性幂等（只依赖源 SVG）。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice")
SRC = BASE / "images" / "delay_skew_14vs12.svg"
OUT = BASE / "images" / "anim" / "delay_skew_14vs12.svg"

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

SWEEP = dict(x0=60, y=660, w=620, h=128, n=1)


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


def flow(d, color, delays, tail_delay):
    out = []
    for dl in delays:
        out.append(f'<path class="flowdot" d="{d}" stroke="{color}" pathLength="100" '
                   f'style="animation-duration:1.5s;animation-delay:{dl}s"/>')
    out.append(f'<path class="flowtail" d="{d}" stroke="{color}" pathLength="100" '
               f'style="animation-duration:1.5s;animation-delay:{tail_delay}s"/>')
    return out


def draw_wrap(delay):
    """.draw 箭头：fade 外壳（delay 前 + 延迟期隐藏）+ draw 线本体，同 delay。"""
    return (f'<g class="fade" style="animation-delay:{delay}s">',
            f'</g>')


def add_cls(line, cls, style):
    """给元素追加 kit class + 行内 delay；有 class 属性则并入，无则插到标签名后。"""
    m = re.search(r'<(\w+)([^>]*?)class="([^"]*)"([^>]*)>', line)
    if m:
        return line.replace(f'class="{m.group(3)}"',
                            f'class="{m.group(3)} {cls}" style="{style}"', 1)
    m2 = re.search(r'<(\w+) ', line)
    assert m2, f"无法加 class: {line[:80]}"
    tag = m2.group(1)
    return line.replace(f'<{tag} ', f'<{tag} class="{cls}" style="{style}" ', 1)


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
        raise AssertionError("anchor not found: " + getattr(pred, "key", "?"))

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
    style_i = find(lambda s: "</style>" in s and s.strip().startswith("<style"))
    defs_close = find(lambda s: s.strip() == "</defs>")
    assert any('id="clipRows2"' in lines[i] for i in range(0, defs_close)), "源 defs(clipRows2) 应保留"
    bg_i = find(lambda s: s.strip() == '<rect x="0" y="0" width="1440" height="950" fill="#f4f1ea"/>')

    kicker = find(lambda s: "STA SKEW CHAIN" in s)
    title_h = find(lambda s: "DELAY vs SKEW" in s)
    leg_a = find(lambda s: s.strip().startswith('<rect x="1040" y="38"'))
    leg_z = find(lambda s: ">check=14<" in s)

    p1 = find(lambda s: s.strip() == '<g class="p1">')
    p2 = find(lambda s: s.strip() == '<g class="p2">', p1)
    p3 = find(lambda s: s.strip() == '<g class="p3">', p2)
    p1c, p2c, p3c = group_close(p1), group_close(p2), group_close(p3)

    # 面板① 内容锚点
    glow1 = find(lambda s: 'class="glow"' in s, p1, p1c)
    t1 = find(lambda s: "① 同一时间轴" in s, p1, p1c)
    boxa = find(lambda s: 'x="1000" y="136"' in s, p1, p1c)
    boxz = find(lambda s: "真相对 skew" in s, p1, p1c)
    clka = find(lambda s: "时钟发散点" in s, p1, p1c)
    clkz = clka + 1
    assert "CLKGEN u_gate" in lines[clkz]
    dgr = find(lambda s: 'class="dGreen"' in s, p1, p1c)
    agr1 = find(lambda s: 'class="aGreen"' in s, p1, p1c)
    slackt = find(lambda s: "slack = 14" in s, p1, p1c)
    dch = find(lambda s: 'class="dClockH"' in s, p1, p1c)
    dcv = find(lambda s: 'class="dClockV"' in s, p1, p1c)
    clklab = find(lambda s: "时钟树 → CLKB_L arrival" in s, p1, p1c)
    ax1a = find(lambda s: 'x1="120" y1="300" x2="1320" y2="300"' in s, p1, p1c)
    ax1z = find(lambda s: s.strip() == '<rect x="114" y="294" width="12" height="12" fill="#1c2534"/>', p1, p1c)
    ddh = find(lambda s: 'class="dDataH"' in s, p1, p1c)
    ddv = find(lambda s: 'class="dDataV"' in s, p1, p1c)
    datalab = find(lambda s: "数据总线 → DB1 arrival" in s, p1, p1c)
    drd = find(lambda s: 'class="dRed"' in s, p1, p1c)
    ared1 = find(lambda s: 'class="aRed"' in s, p1, p1c)
    margt = find(lambda s: "margin = 4.098762" in s, p1, p1c)
    m12a = find(lambda s: 'class="march"' in s and 'x1="840"' in s, p1, p1c)
    m12lab = m12a + 1
    assert ">12<" in lines[m12lab]
    m14a = find(lambda s: 'class="march"' in s and 'x1="960"' in s, p1, p1c)
    m14lab = m14a + 1
    assert "ip_cons L222-225" in lines[m14lab]

    # 面板② 内容锚点
    t2 = find(lambda s: "② 14 vs 12" in s, p2, p2c)
    sub2 = find(lambda s: "同一时钟树 · 3 种" in s, p2, p2c)
    ax2a = find(lambda s: 'x1="90" y1="590" x2="650" y2="590"' in s, p2, p2c)
    ax2z = find(lambda s: 'x="662" y="594"' in s, p2, p2c)
    thr_a = find(lambda s: 'class="march"' in s and 'x1="426"' in s, p2, p2c)
    thr_z = find(lambda s: ">14<" in s and 'x="482"' in s, p2, p2c)
    mka = find(lambda s: 'x="296" y="586"' in s, p2, p2c)
    mkz = find(lambda s: "15.0 严重坏" in s, p2, p2c)
    div_a = find(lambda s: 'x1="60" y1="660"' in s, p2, p2c)
    div_z = find(lambda s: ">判定<" in s, p2, p2c)
    q_r1 = find(lambda s: s.strip() == '<g class="r1">', p2, p2c)
    q_r2 = find(lambda s: s.strip() == '<g class="r2">', p2, p2c)
    q_r3 = find(lambda s: s.strip() == '<g class="r3">', p2, p2c)
    rowb = find(lambda s: 'class="rowB"' in s, p2, p2c)
    con_a = find(lambda s: "结论：当前设计" in s, p2, p2c)
    con_z = con_a + 1
    assert "12 报警提前 2 ns" in lines[con_z]

    # 面板③ 内容锚点
    t3 = find(lambda s: "③ 为什么 14" in s, p3, p3c)
    sub3 = find(lambda s: "绿带 = 10 角" in s, p3, p3c)
    ax3a = find(lambda s: 'x1="770" y1="590" x2="1350" y2="590"' in s, p3, p3c)
    ax3z = find(lambda s: 'x="1362" y="594"' in s, p3, p3c)
    grna = find(lambda s: 'x="828" y="520"' in s, p3, p3c)
    grnz = find(lambda s: "1p ~2.0–6.5" in s, p3, p3c)
    reda = find(lambda s: 'x="1176" y="520"' in s, p3, p3c)
    redz = find(lambda s: "（漏失区）" in s, p3, p3c)
    thr3_a = find(lambda s: 'class="march"' in s and 'x1="1118"' in s, p3, p3c)
    thr3_z = find(lambda s: ">14<" in s and 'x="1176" y="691"' in s, p3, p3c)
    note_a = find(lambda s: "12/14 都在有效区" in s, p3, p3c)
    note_z = note_a + 1
    assert "12 更紧 · 14 已验证" in lines[note_z]
    ar1 = find(lambda s: 'x1="950" y1="692"' in s, p3, p3c)
    ar1lab = find(lambda s: "设在包络以上" in s, p3, p3c)
    ar2 = find(lambda s: 'x1="1200" y1="692"' in s, p3, p3c)
    ar2lab = find(lambda s: "设得过远" in s, p3, p3c)
    badge_a = find(lambda s: 'x="750" y="712"' in s, p3, p3c)
    badge_z = find(lambda s: "14 vs 12 不是" in s, p3, p3c)
    status = find(lambda s: "STATUS: NOT YET CONFIRMED" in s, p3, p3c)

    footer = find(lambda s: "全部数值：live 10-15" in s)
    plate_a = find(lambda s: 'x="1080" y="878"' in s)
    plate_z = find(lambda s: "DELAY BUDGET 14 vs 12" in s)

    # march 阈值线全集（6 条，行内中和）
    march_ls = [i for i in range(0, end) if 'class="march"' in lines[i]]
    assert len(march_ls) == 6, f"应有 6 条 march 线，实得 {len(march_ls)}"

    # ---- 行内修改 ----
    for i in march_ls:
        assert 'stroke-dasharray="6,4"/>' in lines[i]
        lines[i] = lines[i].replace('stroke-dasharray="6,4"/>',
                                    'stroke-dasharray="6,4" style="animation:none"/>', 1)
    # rowB：恢复原动画设计的洗底中值 opacity（静态剥离版漏带 → 实心琥珀盖表）
    lines[rowb] = lines[rowb].replace('<rect class="rowB" ',
                                      '<rect class="rowB" style="opacity:.08" ', 1)
    # .draw 线（class 追加 + pathLength + delay；fade 外壳见下）
    draw_ls = {dch: "0.8s", dcv: "0.95s", dgr: "1.0s", ddh: "1.1s", ddv: "1.25s", drd: "1.45s",
               ar1: "1.45s", ar2: "1.55s"}
    for i, dl in draw_ls.items():
        assert lines[i].strip().startswith("<line"), f"draw 目标应为 line: {lines[i][:60]}"
        m = re.search(r'<line class="([^"]*)"', lines[i])
        if m:
            lines[i] = lines[i].replace(
                f'<line class="{m.group(1)}"',
                f'<line class="{m.group(1)} draw" pathLength="100" style="animation-delay:{dl}"', 1)
        else:
            lines[i] = lines[i].replace(
                "<line ", f'<line class="draw" pathLength="100" style="animation-delay:{dl}" ', 1)

    # ---- before/after 插入表 ----
    before, after = {}, {}

    def ins_before(i, lst):
        before.setdefault(i, []).extend(lst)

    def ins_after(i, lst):
        after.setdefault(i, []).extend(lst)

    def wrap(s_, e_, opens, closes):
        ins_before(s_, [opens])
        ins_after(e_, [closes])

    # kit 样式 + 扫光 defs
    ins_after(style_i, ["<style>\n" + KIT_CSS + "\n</style>"])
    ins_before(defs_close, [sweep_defs(SWEEP)])

    # 页眉
    lines[kicker] = add_cls(lines[kicker], "head", "animation-delay:0s")
    lines[title_h] = add_cls(lines[title_h], "head", "animation-delay:0.05s")
    wrap(leg_a, leg_z, '<g class="row" style="animation-delay:0.15s">', "</g>")

    # 面板①②③ 容器
    lines[p1] = lines[p1].replace('<g class="p1">',
                                  '<g class="p1 row" style="animation-delay:0.2s">', 1)
    lines[p2] = lines[p2].replace('<g class="p2">',
                                  '<g class="p2 row" style="animation-delay:0.5s">', 1)
    lines[p3] = lines[p3].replace('<g class="p3">',
                                  '<g class="p3 row" style="animation-delay:0.8s">', 1)

    # 面板① 内容
    wrap(glow1, glow1, '<g class="fade" style="animation-delay:0.25s">', "</g>")
    lines[t1] = add_cls(lines[t1], "fade", "animation-delay:0.4s")
    wrap(boxa, boxz, '<g class="fade" style="animation-delay:0.5s">', "</g>")
    wrap(clka, clkz, '<g class="fade" style="animation-delay:0.55s">', "</g>")
    # slack 组：pulse-t 外壳（内含 draw 线 + 端帽 + 标签）
    wrap(dgr, slackt, '<g class="pulse-t" style="animation-delay:-0.7s">', "</g>")
    wo, wc = draw_wrap("1.0s")
    wrap(dgr, dgr, wo, wc)
    wrap(agr1, agr1 + 1, '<g class="fade" style="animation-delay:1.45s">', "</g>")
    lines[slackt] = add_cls(lines[slackt], "fade", "animation-delay:1.5s")
    for i, dl in ((dch, "0.8s"), (dcv, "0.95s")):
        wo, wc = draw_wrap(dl)
        wrap(i, i, wo, wc)
    ins_after(dcv, flow("M 120 248 L 571 248", "#1c2534", ["0", "-0.75"], "0"))
    lines[clklab] = add_cls(lines[clklab], "fade", "animation-delay:1.1s")
    wrap(ax1a, ax1z, '<g class="fade" style="animation-delay:0.6s">', "</g>")
    for i, dl in ((ddh, "1.1s"), (ddv, "1.25s")):
        wo, wc = draw_wrap(dl)
        wrap(i, i, wo, wc)
    ins_after(ddv, flow("M 120 344 L 366 344", "#0e7490", ["-0.4", "-1.15"], "-0.4"))
    lines[datalab] = add_cls(lines[datalab], "fade", "animation-delay:1.45s")
    wo, wc = draw_wrap("1.45s")
    wrap(drd, drd, wo, wc)
    wrap(ared1, ared1 + 1, '<g class="fade" style="animation-delay:1.7s">', "</g>")
    lines[margt] = add_cls(lines[margt], "fade", "animation-delay:1.75s")
    wrap(m12a, m12lab, '<g class="fade" style="animation-delay:1.5s">', "</g>")
    wrap(m14a, m14lab, '<g class="fade" style="animation-delay:1.55s">', "</g>")

    # 面板② 内容
    lines[t2] = add_cls(lines[t2], "fade", "animation-delay:0.75s")
    lines[sub2] = add_cls(lines[sub2], "fade", "animation-delay:0.8s")
    wrap(ax2a, ax2z, '<g class="fade" style="animation-delay:0.85s">', "</g>")
    wrap(thr_a, thr_z,
         '<g class="fade" style="animation-delay:1.0s"><g class="pulse-b" style="animation-delay:-2.1s">',
         "</g></g>")
    wrap(mka, mkz, '<g class="fade" style="animation-delay:1.05s">', "</g>")
    wrap(div_a, div_z, '<g class="fade" style="animation-delay:0.95s">', "</g>")
    ins_before(q_r1, [sweep_group(SWEEP)])                  # 场景表扫光（行文字之下）
    lines[q_r1] = lines[q_r1].replace('<g class="r1">',
                                      '<g class="r1 row" style="animation-delay:1.1s">', 1)
    lines[q_r2] = lines[q_r2].replace('<g class="r2">',
                                      '<g class="r2 row" style="animation-delay:1.25s">', 1)
    lines[q_r3] = lines[q_r3].replace('<g class="r3">',
                                      '<g class="r3 row" style="animation-delay:1.4s">', 1)
    wrap(con_a, con_z, '<g class="fade" style="animation-delay:1.55s">', "</g>")

    # 面板③ 内容
    lines[t3] = add_cls(lines[t3], "fade", "animation-delay:1.05s")
    lines[sub3] = add_cls(lines[sub3], "fade", "animation-delay:1.1s")
    wrap(ax3a, ax3z, '<g class="fade" style="animation-delay:1.1s">', "</g>")
    wrap(grna, grnz, '<g class="fade" style="animation-delay:1.15s">', "</g>")
    wrap(reda, redz, '<g class="fade" style="animation-delay:1.2s">', "</g>")
    wrap(thr3_a, thr3_z, '<g class="fade" style="animation-delay:1.3s">', "</g>")
    wrap(note_a, note_z, '<g class="fade" style="animation-delay:1.35s">', "</g>")
    wo, wc = draw_wrap("1.45s")
    wrap(ar1, ar1, wo, wc)
    lines[ar1lab] = add_cls(lines[ar1lab], "fade", "animation-delay:1.65s")
    wo, wc = draw_wrap("1.55s")
    wrap(ar2, ar2, wo, wc)
    lines[ar2lab] = add_cls(lines[ar2lab], "fade", "animation-delay:1.7s")
    wrap(badge_a, badge_z, '<g class="head" style="animation-delay:1.7s">', "</g>")
    wrap(status, status, '<g class="pulse" style="animation-delay:-1.4s">', "</g>")

    # 页脚 + 角标铭牌
    lines[footer] = add_cls(lines[footer], "fade", "animation-delay:1.75s")
    wrap(plate_a, plate_z, '<g class="head" style="animation-delay:1.8s">', "</g>")

    # ---- 发射（before 顺序：先加的在外层） ----
    o = []
    for i in range(len(lines)):
        for b in before.get(i, []):
            o.append(b)
        o.append(lines[i])
        for a in after.get(i, []):
            o.append(a)
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
    res["march_killed"] = "OK" if data.count('style="animation:none"') == 6 else "NG"
    res["rowb_wash"] = "OK" if 'class="rowB" style="opacity:.08"' in data else "NG"

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
    print("[make_anim_delay_skew_14vs12 v4]",
          "draw=", data.count(' draw"'),
          "row_g=", len(re.findall(r'class="p\d row"', data)) + len(re.findall(r'class="r\d row"', data)),
          "flowdot=", data.count('class="flowdot"'),
          "flowtail=", data.count('class="flowtail"'),
          "pulse=", len(re.findall(r'class="(pulse|pulse-t|pulse-b)"', data)),
          "sweepband=", data.count('class="sweepband"'))
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
# ymzhu 2026-10-28 17:45
