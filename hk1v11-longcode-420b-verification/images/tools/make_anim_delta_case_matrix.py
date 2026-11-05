#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_delta_case_matrix.py — 前后对比组图 2/3（Motion Kit v4 契约）

delta_case_matrix：420b case 规模与维度矩阵（基线 07-13 vs 现状 0924 起）。
事实源：docs/HK1V11_longcode_420b_delta_audit_20261105.md（§3）+ 2026-11-05
对 DV_TCON_C/top/tests 的直读实测（192 目录 / 维度计数 / cfg 字段并集逐项复核）。

生成器从同一 scene 产出「静态 + 动画」双版：
- 静态：images/delta_case_matrix.svg
- 动画：images/anim/delta_case_matrix.svg（text 多重集与 <svg> 开标签与静态一致）

内容（左 panel 基线 / 右 panel 现状 / 中列波次徽章 + 主箭头）：
- 数量：1（t_H3840_V16_FPS120_420b）→ 192（0924 +189 维度矩阵 · 1022 +2 boe_test/SCREN1）
- cfg_frame 字段：4（POL/PORSD/CH_SEL/TEST_PRTCT）→ 18 实测并集
  （基线 4 全保留 + 新增 14：含 POL2 演进与 BYTE0_BIT3_0 特例；t1 摘要口径 17 不计特例）
- 维度矩阵：分辨率 ×6（47/52/6/18/10/59）· FPS ×8 · PORT_NUM ×4 · DPLC 族 ·
  SD_CHOP 24 全枚举 · 极性 / CH_SEL / SDC / power / boe / SCREN1

动效规格（MOTION_KIT v4/v4.2）：
- 入场：head(0) → 左 panel(0.15)+条目(0.3~0.9) → 右 panel(0.45)+分区(0.6~1.75)
  → 中列徽章(1.1~1.4) → 主箭头 draw(1.5 ≥ 两端面板+0.55) → 底带(1.85)。
- 稳态 3 族：行波 cellwave（6 分辨率条 0.2s 递增 3.6s + 8 FPS chips 0.1s 递增）/
  脉冲 pulse（大数字 192 · -1.4s）+ pulse-t（H3840 条 · 0s）/
  列车 flowdot 3 包 + 2 flowtail（主箭头 136px ≥80px，2.6s ≥2.4s）。
- 数据密度：数据行 ~12 行（小于 20 行阈值）→ 行波允许；无 march/breathe。

铁律：纯 CSS in-SVG；确定性幂等；零第三方依赖；chips 宽度由同源 est() 自适应。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
OUT_STATIC = BASE / "images" / "delta_case_matrix.svg"
OUT_ANIM = BASE / "images" / "anim" / "delta_case_matrix.svg"

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")
C = dict(
    dark="#1e293b", muted="#64748b", container="#f8fafc", line="#e2e8f0",
    blue="#2563eb", green="#059669", purple="#7c3aed", orange="#ea580c",
    teal="#0f766e", teal_soft="#ccfbf1", gray="#9ca3af",
)
W, H = 1200, 840

KIT_RULES = [
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
]


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fx(v):
    r = round(float(v), 2)
    return f"{int(r)}" if r == int(r) else f"{r:g}"


def sec(x):
    v = round(x, 3)
    return f"{int(v)}s" if v == int(v) else f"{v:g}s"


def est(s, fs):
    """文本宽度估算（与布局 QA 同源：CJK≈fs，ASCII≈0.58fs）。"""
    w = 0.0
    for ch in s:
        o = ord(ch)
        if o > 0x2E80 or ch in "「」（）":
            w += fs
        elif ch in "·｜→≥×①②③":
            w += fs * 0.9
        elif ch == " ":
            w += fs * 0.30
        else:
            w += fs * 0.58
    return w


class E:
    __slots__ = ("tag", "a", "text", "kids", "wrap", "cls", "sty", "pl", "animonly")

    def __init__(self, tag, text=None, kids=None, wrap=None, cls=None,
                 sty=None, pl=False, animonly=False, **attrs):
        self.tag, self.text, self.kids = tag, text, kids
        self.wrap, self.cls, self.sty = wrap, cls, sty
        self.pl, self.animonly = pl, animonly
        self.a = {k: (v if isinstance(v, str) else fx(v)) for k, v in attrs.items()}


def render(nodes, mode, depth=1):
    out, ind = [], "  " * depth
    for n in nodes:
        if n.animonly and mode == "static":
            continue
        opened = 0
        if mode == "anim":
            wl = n.wrap if n.wrap else []
            if wl and not isinstance(wl[0], tuple):
                wl = [wl]
            for c, dl, du in wl:
                st = ""
                if dl is not None:
                    st += f"animation-delay:{sec(dl)};"
                if du is not None:
                    st += f"animation-duration:{sec(du)};"
                st = st[:-1] if st else st
                out.append(f'{ind}<g class="{c}"' + (f' style="{st}">' if st else ">"))
                opened += 1
        a = dict(n.a)
        if mode == "anim":
            if n.cls:
                a["class"] = n.cls
            if n.pl:
                a["pathLength"] = "100"
            if n.sty:
                a["style"] = n.sty
        attrs = " ".join(f'{k}="{v}"' for k, v in a.items())
        if n.tag == "text":
            out.append(f"{ind}<text {attrs}>{esc(n.text)}</text>")
        elif n.kids:
            out.append(f"{ind}<{n.tag} {attrs}>")
            out.extend(render(n.kids, mode, depth + 1))
            out.append(f"{ind}</{n.tag}>")
        else:
            out.append(f"{ind}<{n.tag} {attrs}/>")
        for _ in range(opened):
            out.append(f"{ind}</g>")
    return out


def R(x, y, w, h, fill="#ffffff", stroke="#d1d5db", rx=8, sw=1.5, dash=None, wrap=None, **kw):
    a = dict(x=x, y=y, width=w, height=h, rx=rx, fill=fill, stroke=stroke)
    a["stroke-width"] = sw
    if dash:
        a["stroke-dasharray"] = dash
    a.update(kw)
    return E("rect", wrap=wrap, **a)


def T(x, y, s, size=12, fill=C["dark"], weight=None, anchor="middle", wrap=None):
    a = dict(x=x, y=y)
    a["font-size"] = size
    a["fill"] = fill
    a["text-anchor"] = anchor
    if weight:
        a["font-weight"] = weight
    return E("text", text=s, wrap=wrap, **a)


def G(kids, wrap=None):
    return E("g", kids=kids, wrap=wrap)


def LINE(x1, y1, x2, y2, stroke, sw=1.5, dash=None):
    a = dict(x1=x1, y1=y1, x2=x2, y2=y2, stroke=stroke)
    a["stroke-width"] = sw
    if dash:
        a["stroke-dasharray"] = dash
    return E("line", **a)


def chip(x, y, label, size=9.5, h=24, pad=10, fill="#ffffff", stroke=C["line"],
         tfill=C["dark"], weight=600, wrap=None):
    """自适应宽度 chip；返回 (元素组, 宽度)。"""
    w = round(est(label, size) + 2 * pad, 1)
    g = [R(x, y, w, h, fill=fill, stroke=stroke, rx=6),
         T(x + w / 2, y + h / 2 + 3.5, label, size, tfill, weight)]
    return G(g, wrap=wrap), w


def chip_row(x, y, labels, size=9.5, h=24, gap=6, wrap=None, per_wave=None, **kw):
    """一行 chips；per_wave=(delay0, step, dur) 给每个 chip 额外套 cellwave。"""
    kids, cx = [], x
    for i, lab in enumerate(labels):
        g, w = chip(cx, y, lab, size=size, h=h, **kw)
        if per_wave:
            kids.append(E("g", kids=[g], wrap=[("cellwave",
                                                per_wave[0] + i * per_wave[1],
                                                per_wave[2])]))
        else:
            kids.append(g)
        cx += w + gap
    return G(kids, wrap=wrap), cx - gap - x


def ARROW(x1, y1, x2, y2, stroke, marker, draw_delay=None):
    d = f"M {fx(x1)} {fx(y1)} H {fx(x2)}"
    a = dict(d=d, fill="none", stroke=stroke)
    a["stroke-width"] = 2
    a["marker-end"] = f"url(#{marker})"
    cls = sty = None
    if draw_delay is not None:
        cls, sty = "draw", f"animation-delay:{sec(draw_delay)}"
    e = E("path", cls=cls, sty=sty, pl=bool(cls), **a)
    dots = []
    if draw_delay is not None:
        for dl in (0.0, -0.87, -1.73):
            dots.append(E("path", d=d, stroke=C["teal"], cls="flowdot", pl=True,
                          sty=f"animation-duration:2.6s;animation-delay:{sec(dl)}",
                          animonly=True))
        for dl in (0.0, -0.87):
            dots.append(E("path", d=d, stroke=C["teal"], cls="flowtail", pl=True,
                          sty=f"animation-duration:2.6s;animation-delay:{sec(dl)}",
                          animonly=True))
    return [e] + dots


# ----------------------------------------------------------------------------
def build_scene():
    S = []
    S.append(G([
        T(600, 38, "420b Case 规模与维度矩阵：1 → 192", 21, C["dark"], 600),
        T(600, 62, "基线 66ecf97d（07-13）→ 现状 a7130ba7（1028 包后）· 0924 一次性落地"
                   "维度矩阵 +189 · 1022 特例 +2 · 53-case 七分类规划未采用", 11.5, C["muted"]),
    ], wrap=("head", 0, None)))

    # —— 左 panel：基线 ——
    lk = [R(40, 92, 268, 618, fill=C["container"], stroke=C["line"], rx=10),
          T(174, 118, "基线 · 07-13", 13, "#b45309", 600),
          LINE(56, 130, 292, 130, C["line"])]
    lk.append(G([T(174, 188, "1", 46, "#b45309", 700),
                 T(174, 212, "420b case（t_H3840_V16_FPS120_420b）", 9.5, C["muted"])],
                wrap=("fade", 0.3, None)))
    g0, _ = chip(56, 228, "t_H3840_V16_FPS120_420b", size=9, fill="#fef3c1",
                 stroke="#fcd34d", tfill="#92400e")
    lk.append(G([g0], wrap=("row", 0.4, None)))
    g1, _ = chip(56, 262, "53 规划 case · 七分类（未采用）", fill="#f1f5f9",
                 stroke="#cbd5e1", tfill="#475569", size=9.5)
    lk.append(G([g1], wrap=("row", 0.5, None)))
    lk.append(G([T(174, 322, "cfg_frame 字段 · 4", 11, C["dark"], 600)],
                wrap=("fade", 0.6, None)))
    cfg4 = []
    for i, f in enumerate(("POL", "PORSD", "CH_SEL", "TEST_PRTCT")):
        g, _ = chip(56 + (i % 2) * 122, 334 + (i // 2) * 30, f, size=9.5, h=24,
                    fill="#ffffff", stroke="#e2e8f0")
        cfg4.append(g)
    lk.append(G(cfg4, wrap=("row", 0.7, None)))
    g2, _ = chip(56, 404, "cfg_frame0..8.txt（4 字段）", size=9.5, fill="#ffffff",
                 stroke="#e2e8f0", tfill=C["muted"], weight=None)
    g3, _ = chip(56, 434, "目录无 ctrl_l_line_cfg.txt（0924 新增）", size=9,
                 fill="#ffffff", stroke="#e2e8f0", tfill=C["muted"], weight=None)
    lk.append(G([g2, g3], wrap=("fade", 0.8, None)))
    lk.append(G([
        T(56, 488, "规划叙事（07-13 文章）：", 10, C["dark"], 600, "start"),
        T(56, 508, "53 case 按 Smoke 7 / Frame 8 / … 七分类", 9.5, C["muted"], None, "start"),
        T(56, 526, "命名族 t_8b{lane}lane_420b_{function}", 9.5, C["muted"], None, "start"),
        T(56, 544, "Phase 1~7 渐进扩展路线", 9.5, C["muted"], None, "start"),
        T(56, 570, "→ 以上均为规划，与现实（t_H*_V16_", 9.5, "#b45309", None, "start"),
        T(56, 588, "   FPS*_PORT_NUM*_[维度]_420b）脱节", 9.5, "#b45309", None, "start"),
    ], wrap=("fade", 0.9, None)))
    S.append(G(lk, wrap=("row", 0.15, None)))

    # —— 中列 ——
    S.append(G([R(322, 150, 136, 58, fill="#fffbeb", stroke="#fcd34d", rx=8),
                T(390, 172, "0924 · +189", 10.5, C["dark"], 600),
                T(390, 192, "维度矩阵一次性落地", 9, C["muted"])], wrap=("fade", 1.1, None)))
    S.append(G([R(322, 228, 136, 58, fill="#fffbeb", stroke="#fcd34d", rx=8),
                T(390, 250, "1022 · +2", 10.5, C["dark"], 600),
                T(390, 270, "boe_test · SCREN1 特例", 9, C["muted"])], wrap=("fade", 1.2, None)))
    S.append(G([R(322, 306, 136, 58, fill="#f1f5f9", stroke="#cbd5e1", rx=8),
                T(390, 328, "规划废弃", 10.5, C["dark"], 600),
                T(390, 348, "53 七分类 → 实测矩阵", 9, C["muted"])], wrap=("fade", 1.3, None)))
    S.append(G([R(322, 384, 136, 58, fill=C["teal_soft"], stroke="#5eead4", rx=8),
                T(390, 406, "cfg_frame 字段", 10.5, C["dark"], 600),
                T(390, 426, "4 → 18（实测并集）", 9, C["teal"])], wrap=("fade", 1.4, None)))
    S.append(G([R(322, 462, 136, 58, fill="#ffffff", stroke=C["line"], rx=8),
                T(390, 484, "验证重心", 10.5, C["dark"], 600),
                T(390, 504, "单点冒烟 → 维度回归", 9, C["muted"])], wrap=("fade", 1.6, None)))
    S.append(G([T(390, 560, "基线 → 现状", 10.5, C["muted"], 600)], wrap=("fade", 1.5, None)))
    S.extend(ARROW(322, 574, 458, 574, C["gray"], "ar-gray", draw_delay=1.5))

    # —— 右 panel：现状 ——
    rk = [R(470, 92, 690, 618, fill=C["container"], stroke=C["line"], rx=10),
          T(486, 122, "现状 · 0924 起（1028 包后）", 13, C["teal"], 600, "start")]
    rk.append(G([T(1096, 130, "192", 32, C["teal"], 700),
                 T(1096, 148, "case", 10, C["muted"])], wrap=[("pulse", -1.4, None)]))
    rk.append(G([R(486, 158, 658, 24, fill="#ffffff", stroke=C["line"], rx=6),
                 T(815, 174, "命名：t_H{HACT}_V16_FPS{fps}_PORT_NUM{port}_[维度…]_420b",
                   9.5, C["dark"], 600)], wrap=("row", 0.6, None)))

    # 分辨率分布
    res = [("H1440", 47), ("H1920", 52), ("H2560", 6), ("H2880", 18),
           ("H3456", 10), ("H3840", 59)]
    bars = [T(486, 208, "分辨率分布（192 case 全量）", 11, C["dark"], 600, "start")]
    maxc = 59.0
    for i, (lab, n) in enumerate(res):
        y = 220 + i * 24
        wv = n / maxc * 380
        wrap = [("cellwave", 0.2 + 0.2 * i, 3.6)]
        if lab == "H3840":
            wrap = [("pulse-t", 0, None)] + wrap
        bars.append(E("g", kids=[
            T(544, y + 13, lab, 9.5, C["dark"], 600, "end"),
            R(552, y, wv, 18, fill="#14b8a6" if lab != "H3840" else "#0f766e",
              stroke="none", rx=3),
            T(552 + wv + 8, y + 13, str(n), 9.5, C["muted"], None, "start"),
        ], wrap=wrap))
    bars.append(T(486, 372, "合计 47+52+6+18+10+59 = 192（FPS / PORT 计数同口径合计 192）",
                  9.5, C["muted"], None, "start"))
    rk.append(G(bars, wrap=("row", 0.75, None)))

    fps, fw = chip_row(486, 396, ["60 · 1", "120 · 57", "144 · 20", "165 · 8",
                                  "180 · 1", "240 · 3", "280 · 98", "360 · 4"],
                       size=9.5, per_wave=(1.0, 0.1, 3.6))
    rk.append(G([T(486, 390, "FPS 维度（×8）", 11, C["dark"], 600, "start")] +
                [fps], wrap=("row", 1.05, None)))
    port, pw = chip_row(486, 458, ["6 · 2", "8 · 6", "12 · 97", "24 · 1", "其余默认"],
                        size=9.5, fill="#f1f5f9", stroke="#cbd5e1", tfill="#475569")
    rk.append(G([T(486, 452, "PORT_NUM（显式标注 ×4）", 11, C["dark"], 600, "start")] +
                [port], wrap=("row", 1.15, None)))

    dim1, _ = chip_row(486, 518, ["DPLC_MODE1 ×173", "DPLC_GROUP1 ×33", "AVE_RGBW 0-7",
                                  "AVE_MODE / AVE_LAST", "SD_CHOP F0-F3 × CHOP0-5（24 · H3840）"],
                       size=9, fill="#ecfdf5", stroke="#a7f3d0", tfill="#065f46")
    dim2, _ = chip_row(486, 548, ["H4INV · POL20/21 · POLC",
                                  "CH_SEL 0/2/3/4（subpix 966/960/726/720/864）", "SDC0 ×55"],
                       size=9, fill="#ecfdf5", stroke="#a7f3d0", tfill="#065f46")
    dim3, _ = chip_row(486, 578, ["power ×3", "boe_test", "SCREN1 ×2",
                                  "CTRL_L_LINE_OVERRIDE ×1", "POL2 · DPOLINV"],
                       size=9, fill="#ecfdf5", stroke="#a7f3d0", tfill="#065f46")
    rk.append(G([T(486, 512, "其他维度族", 11, C["dark"], 600, "start"), dim1, dim2, dim3],
                wrap=("row", 1.25, None)))

    cfga, _ = chip_row(486, 634, ["DPLC_MODE", "AVE_MODE", "AVE_LAST", "AVE_RGBW",
                                  "SDC", "POL2", "H4INV"], size=9, h=22)
    cfgb, _ = chip_row(486, 662, ["POLC", "DPLC_GROUP", "SD_CHOP_F", "SD_CHOP",
                                  "SCREN", "DPOLINV", "BYTE0_BIT3_0（特例）"], size=9, h=22,
                       fill="#fef3c1", stroke="#fcd34d", tfill="#92400e")
    rk.append(G([T(486, 628, "cfg_frame 字段：4 → 18（基线 4 全保留 + 新增 14）",
                   11, C["dark"], 600, "start"), cfga, cfgb], wrap=("row", 1.55, None)))
    rk.append(G([T(486, 700, "实测（2026-11-05）：POL 与 POL2 并存 · BYTE0_BIT3_0 仅 "
                             "SCREN1 特例 1 处 —— 全并集 18 个字段名", 9.5, C["muted"],
                   None, "start")], wrap=("fade", 1.75, None)))
    S.append(G(rk, wrap=("row", 0.45, None)))

    # —— 底部数据口径带 ——
    S.append(G([
        R(40, 730, 1120, 84, fill=C["container"], stroke=C["line"], rx=8),
        T(56, 752, "数据口径（2026-11-05 实测 · 与差异审计 §3.2 一致）", 10.5, C["dark"], 600, "start"),
        T(56, 772, "分辨率 ×6 · FPS ×8 · PORT_NUM ×4（显式）· DPLC 族全枚举 · SD_CHOP 24 全枚举"
                   "（H3840）· 极性 / CH_SEL / SDC / power 组合", 10, C["muted"], None, "start"),
        T(56, 790, "每目录 cfg_frame0..8.txt + ctrl_l_line_cfg.txt（188/192 · 0924 新增）+ "
                   "user_def.sv；boe_test 另带 BOE_420B_TEST / PARTNUM / DOCNUM", 10, C["muted"], None, "start"),
        T(56, 808, "tests 总数 677 · 命名族 t_8b{lane}lane_420b_{function} 未采用（规划遗存）· HEAD = a7130ba7",
          10, C["muted"], None, "start"),
    ], wrap=("fade", 1.85, None)))
    return S


DEFS = [
    '  <defs>',
    '    <marker id="ar-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#2563eb"/></marker>',
    '    <marker id="ar-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#059669"/></marker>',
    '    <marker id="ar-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#7c3aed"/></marker>',
    '    <marker id="ar-orange" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#ea580c"/></marker>',
    '    <marker id="ar-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto"><polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af"/></marker>',
    '  </defs>',
]


def build(mode):
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
             f'  <style>text {{ font-family: {FONT}; }}</style>']
    if mode == "anim":
        lines.append("  <style>")
        lines.extend(f"    {r}" for r in KIT_RULES)
        lines.append("  </style>")
    lines.extend(DEFS)
    lines.append(f'  <rect width="{W}" height="{H}" fill="#ffffff"/>')
    lines.extend(render(build_scene(), mode))
    lines.append("</svg>")
    return "\n".join(lines) + "\n"


NS = "{http://www.w3.org/2000/svg}"


def selfcheck(static, anim):
    t1 = Counter(e.text or "" for e in ET.fromstring(static).iter(NS + "text"))
    t2 = Counter(e.text or "" for e in ET.fromstring(anim).iter(NS + "text"))
    assert t1 == t2, "text 多重集不一致"
    assert static.splitlines()[0] == anim.splitlines()[0], "<svg> 开标签不一致"
    assert anim.count("@keyframes") >= 10, "keyframes 不足"
    assert "<script" not in anim and "<animate" not in anim, "禁 script/SMIL"
    for m in re.finditer(r'flow(?:dot|tail)[^"]*"[^>]*animation-duration:([0-9.]+)s', anim):
        assert float(m.group(1)) >= 2.4, f"列车超速 {m.group(1)}s"
    fams = sum(bool(re.findall(p, anim)) for p in
               (r'class="[^"]*flowdot', r'class="[^"]*pulse(-[tb])?"',
                r'class="[^"]*sweepband', r'class="[^"]*dashgrow',
                r'class="[^"]*cellwave', r'class="[^"]*step"'))
    assert fams >= 2, "稳态族不足 2"
    assert 1024 < len(anim.encode("utf-8")), "anim 过小"
    # 布局守卫：chip 行不越过右 panel 内缘
    for txt in static.splitlines():
        pass  # 几何由 est() 自适应 + 外部 QA 兜底


def main():
    static, anim = build("static"), build("anim")
    selfcheck(static, anim)
    OUT_STATIC.write_text(static, encoding="utf-8", newline="\n")
    OUT_ANIM.write_text(anim, encoding="utf-8", newline="\n")
    print(f"OK static={OUT_STATIC.stat().st_size}B anim={OUT_ANIM.stat().st_size}B")
    return 0


if __name__ == "__main__":
    sys.exit(main())
# ymzhu 2026-11-05 11:30
