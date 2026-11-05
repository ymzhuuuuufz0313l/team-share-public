#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_delta_frame_structure.py — 前后对比组图 1/3（Motion Kit v4 契约）

delta_frame_structure：420b 帧结构演进（基线 07-13 vs 现状 0924 起）。
事实源：docs/HK1V11_longcode_420b_delta_audit_20261105.md（t1 差异审计 §1/§2.1/§4.4/§5.5）。

与既有 make_anim_*（升级既有图）不同：本图是全新图，生成器从同一 scene
一次性产出「静态 + 动画」双版（任务允许：生成器同时产静动两版）：
- 静态：images/delta_frame_structure.svg（无 kit class，纯几何/文本）
- 动画：images/anim/delta_frame_structure.svg（同几何/文本 + kit CSS + class）
两版 text 多重集与 <svg> 开标签逐字节一致（写盘前 selfcheck 强制断言）。

内容（左 panel 基线 / 右 panel 现状 / 中列 3 个变化徽章 + 主箭头）：
- ① Config Line 位置：VACT 后单独成行（+1 行）→ 第一条 VFP 行承载（帧内不加行）
- ② 配置行行尾：恒 K2 → SCREN=1 时 K3（锁 SCREN + 共享 key 复位 0XFFFF）｜SCREN=0 时 K2
- ③ CTRL_F 加扰：随加扰域推进 key（07-13 原文论断）→ 恒不加扰 · 不推进 SCR_KEY

动效规格（MOTION_KIT v4/v4.2/v4.3）：
- 入场：head(0) → 左 panel 容器(0.15)/行(0.3~0.78) → 右 panel 容器(0.45)/行(0.6~1.08)
  → 中列 pill(1.4)/徽章(1.45/1.6/1.75) → 主箭头 draw(1.85 ≥ 两端面板 max+0.55)
  → 底部证据带(2.1)。一次性 delay ≤2.5s。
- 稳态 3 族（≤4）：行波 cellwave（每行 strip 组，0.15s 递增，4.2s）/
  脉冲 pulse（左 Config 行 · 琥珀 0s）+ pulse-t（右 K3/K2 格 -1.4s）+
  pulse-b（右 LSP K3 格 0.7s）/ 列车 flowdot 3 包 + 2 flowtail（主箭头 176px ≥80px，
  2.6s ≥2.4s，0/-0.87/-1.73s 错相）。
- 无 march/breathe（持续族恰 3）；无 <script>/<animate>；reduced-motion 用 kit 媒体块。

铁律：纯 CSS in-SVG；确定性幂等（无时间戳进产物）；零第三方依赖。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
OUT_STATIC = BASE / "images" / "delta_frame_structure.svg"
OUT_ANIM = BASE / "images" / "anim" / "delta_frame_structure.svg"

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")
C = dict(
    dark="#1e293b", muted="#64748b", container="#f8fafc", line="#e2e8f0",
    blue="#2563eb", green="#059669", purple="#7c3aed", orange="#ea580c",
    teal="#0f766e", teal_soft="#ccfbf1", gray="#9ca3af",
)
# 单元格配色（沿用站点 spec_* 系列约定：K 码绿格 / payload 橙格 / 普通数据蓝格）
CELL_K = ("#dcfce7", "#86efac", "#166534")          # K 码
CELL_PAY = ("#eff6ff", "#bfdbfe", "#1e40af")        # CTRL_L / Video / VBK
CELL_DMY = ("#f1f5f9", "#cbd5e1", "#475569")        # Dmy / IDLE
CELL_LSP = ("#ffedd5", "#fdba74", "#9a3412")        # LSP payload（EA→ED）
CELL_OLD = ("#fef3c7", "#fcd34d", "#92400e")        # 基线 Config 行（琥珀=已过时）
CELL_NEW = ("#ccfbf1", "#5eead4", "#0f766e")        # 现状 VFP[0] 配置行（青）

W, H = 1200, 780

# —— Motion Kit v4 CSS（MOTION_KIT.md §2 逐字，不增删类）——
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


class E:
    """场景元素：static 渲染忽略全部动画元数据；anim 渲染应用 wrap/cls/sty。"""
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


def R(x, y, w, h, fill="#ffffff", stroke="#d1d5db", rx=8, sw=1.5,
      dash=None, wrap=None, **kw):
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


def ARROW(x1, y1, x2, y2, stroke, marker, draw_delay=None):
    d = f"M {fx(x1)} {fx(y1)} H {fx(x2)}"
    a = dict(d=d, fill="none", stroke=stroke)
    a["stroke-width"] = 2
    a["marker-end"] = f"url(#{marker})"
    cls = sty = None
    if draw_delay is not None:
        cls, pl, sty = "draw", True, f"animation-delay:{sec(draw_delay)}"
    e = E("path", cls=cls, sty=sty, pl=bool(cls), **a)
    dots = []
    if draw_delay is not None:  # 主箭头列车（≥80px 才挂；3 包 + 2 拖尾，2.6s）
        for i, dl in enumerate((0.0, -0.87, -1.73)):
            dots.append(E("path", d=d, stroke=C["teal"], cls="flowdot", pl=True,
                          sty=f"animation-duration:2.6s;animation-delay:{sec(dl)}",
                          animonly=True))
        for dl in (0.0, -0.87):
            dots.append(E("path", d=d, stroke=C["teal"], cls="flowtail", pl=True,
                          sty=f"animation-duration:2.6s;animation-delay:{sec(dl)}",
                          animonly=True))
    return [e] + dots


def cell(x, y, w, label, pal, size=9.5, wrap=None, h=26):
    fill, stroke, tfill = pal
    return [R(x, y, w, h, fill=fill, stroke=stroke, rx=6, sw=1.5),
            T(x + w / 2, y + h / 2 + 3.5, label, size, tfill, 600, wrap=None)]


# ----------------------------------------------------------------------------
# 场景组装
# ----------------------------------------------------------------------------
def frame_row(px, y, label, cells, notes, row_wrap, strip_wrap,
              strip_extra_wrap=None, note_fill=C["muted"]):
    """一行：左侧 label（anchor=end）+ 右侧 strip 单元格 + 下方注释行。"""
    kids = [T(px + 122, y + 17, label, 10, C["dark"], 600, "end")]
    x = px + 132
    inner = []
    for c in cells:
        cw, lab, pal = c[0], c[1], c[2]
        cw_wrap = c[3] if len(c) > 3 else None
        parts = cell(x, y, cw, lab, pal)
        if cw_wrap:
            inner.append(G(parts, wrap=[cw_wrap]))
        else:
            inner.extend(parts)
        x += cw + 5
    wraps = [strip_wrap] if strip_wrap else []
    if strip_extra_wrap:
        wraps = [strip_extra_wrap] + wraps
    kids.append(G(inner, wrap=wraps or None))
    for i, note in enumerate(notes):
        kids.append(T(px + 56, y + 40 + 12 * i, note, 9.5, note_fill, None, "start"))
    return G(kids, wrap=row_wrap)


def panel(px, header, header_fill, rows, chip_text, footnotes, wrap):
    cx = px + 230
    kids = [R(px, 92, 460, 566, fill=C["container"], stroke=C["line"], rx=10),
            T(cx, 118, header, 13, header_fill, 600),
            LINE(px + 16, 130, px + 444, 130, C["line"])]
    kids.extend(rows)
    kids.append(G([R(px + 56, 512, 348, 26, fill="#ffffff", stroke=C["line"], rx=6),
                   T(cx, 529, chip_text, 9.5, C["dark"], 600)]))
    fn = [T(px + 56, 566 + 18 * i, s, 10, C["muted"], None, "start")
          for i, s in enumerate(footnotes)]
    kids.append(G(fn))
    return G(kids, wrap=wrap)


def build_scene():
    S = []
    # —— 头部 ——
    S.append(G([
        T(600, 38, "420b 帧结构演进：Config Line 位置与行尾语义", 21, C["dark"], 600),
        T(600, 62, "基线 66ecf97d（07-13 文章 · 0720v1 实现）→ 现状 a7130ba7"
                   "（0924 44e48592 起生效 · 1028 包后）· 差异审计 2026-11-05",
          11.5, C["muted"]),
    ], wrap=("head", 0, None)))

    # —— 左 panel（基线）——
    lrows = [
        frame_row(40, 150, "LSP ×≥5", [
            (40, "K2", CELL_K), (126, "EA→ED ×8", CELL_LSP),
            (54, "Dmy", CELL_DMY), (40, "K3", CELL_K)],
            ["LSP · K 码恒不加扰"],
            ("row", 0.3, None), ("cellwave", 0.15, 4.2)),
        frame_row(40, 214, "VBP 行 ×vbp", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "VBK", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["帧 c 消隐首段"],
            ("row", 0.42, None), ("cellwave", 0.3, 4.2)),
        frame_row(40, 278, "Active 行 ×vact", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "Video", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["首行 FSYNC=1 · 行尾统一 K2"],
            ("row", 0.54, None), ("cellwave", 0.45, 4.2)),
        frame_row(40, 342, "Config Line（帧 c+1）", [
            (40, "K4", CELL_K), (84, "CTRL_F", CELL_OLD), (54, "Dmy", CELL_DMY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["① VACT 后单独成行 · 帧内 +1 行",
             "② 行尾恒 K2（无 SCREN 锁存分支）",
             "③ CTRL_F 随加扰域推进 key（07-13 原文论断）"],
            ("row", 0.66, None), ("cellwave", 0.6, 4.2),
            strip_extra_wrap=("pulse", 0, None)),
        frame_row(40, 446, "VFP 行 ×vfp", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "VBK", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["消隐尾段（Config Line 之后）"],
            ("row", 0.78, None), ("cellwave", 0.75, 4.2)),
    ]
    S.append(panel(
        40, "基线 · 2026-07-13（0720v1 实现）", "#b45309", lrows,
        "帧时长 = vbp + vact + 1（Config 行）+ vfp",
        ["Config Line = 帧配置行：K4 + CTRL_F + Dmy + K2",
         "CTRL_F payload 随加扰域推进（07-13 原文论断，0924 起不再成立）",
         "Active 行尾统一 K2 · LSP / IDLE / K 码恒不加扰"],
        ("row", 0.15, None)))
    # 左 panel 尾部 fade 组（chip / 脚注在 panel() 内，作为整体 row 入场即可）

    # —— 右 panel（现状）——
    rrows = [
        frame_row(700, 150, "LSP ×≥5", [
            (40, "K2", CELL_K), (126, "EA→ED ×8", CELL_LSP),
            (54, "Dmy", CELL_DMY), (40, "K3", CELL_K, ("pulse-b", 0.7, None))],
            ["LSP · K 码恒不加扰 · 字节序 EA→ED（0720 修正后口径）"],
            ("row", 0.6, None), ("cellwave", 0.9, 4.2)),
        frame_row(700, 214, "VBP 行 ×vbp（帧 c）", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "VBK", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["get_ctrlL_reg(frame, phase, line_idx) 相位感知"],
            ("row", 0.72, None), ("cellwave", 1.05, 4.2)),
        frame_row(700, 278, "Active 行 ×vact", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "Video", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["首行 FSYNC=1 · 行尾统一 K2"],
            ("row", 0.84, None), ("cellwave", 1.2, 4.2)),
        frame_row(700, 342, "VFP[0] = 下一帧配置行", [
            (40, "K4", CELL_K), (84, "CTRL_F", CELL_NEW), (54, "Dmy", CELL_DMY),
            (62, "K3/K2", CELL_NEW, ("pulse-t", -1.4, None)), (50, "IDLE", CELL_DMY)],
            ["① 第一条 VFP 行承载 · 帧内不加行（帧时长不变）",
             "② SCREN=1 → K3（锁 SCREN · key 复位 0XFFFF）· SCREN=0 → K2",
             "③ CTRL_F 恒不加扰 · 不推进 SCR_KEY"],
            ("row", 0.96, None), ("cellwave", 1.35, 4.2)),
        frame_row(700, 446, "其余 VFP 行（同 VBP）", [
            (40, "K1", CELL_K), (84, "CTRL_L", CELL_PAY), (70, "VBK", CELL_PAY),
            (40, "K2", CELL_K), (50, "IDLE", CELL_DMY)],
            ["消隐尾段 · 与 VBP 行同构"],
            ("row", 1.08, None), ("cellwave", 1.5, 4.2)),
    ]
    S.append(panel(
        700, "现状 · 0924 起（a7130ba7 · 1028 包后）", C["teal"], rrows,
        "帧时长 = vbp + vact + vfp（Config 并入 VFP[0]，不加行）",
        ["K3：锁存 SCREN + 共享加扰 key 复位 0XFFFF（TX 侧 lfsr_key_420b 同步）",
         "RTL 解码侧：K3 延 4 拍生效（K3_FIND_rp_d[3]）· dec_data_buf 42→44 bit",
         "Active 行尾仍统一 K2 · LSP / IDLE / K 码恒不加扰（两版一致）"],
        ("row", 0.45, None)))

    # —— 中列：pill + 3 徽章 + 主箭头 ——
    S.append(G([R(528, 118, 144, 24, fill=C["teal_soft"], stroke="#5eead4", rx=12),
                T(600, 134, "0924 · 44e48592 重定义", 10.5, C["teal"], 600)],
               wrap=("fade", 1.4, None)))

    def badge(y, h, title, lines, delay):
        kids = [T(600, y + 18, title, 10.5, C["dark"], 600)]
        for i, s in enumerate(lines):
            fill = C["orange"] if s == "→" else C["muted"]
            kids.append(T(600, y + 38 + 16 * i, s, 9.5, fill, None))
        return G([R(516, y, 168, h, fill="#fffbeb", stroke="#fcd34d", rx=8)] + kids,
                 wrap=("fade", delay, None))

    S.append(badge(166, 104, "① Config Line 位置",
                   ["VACT 后单独成行（+1 行）", "→", "第一条 VFP 行承载",
                    "帧内不加行 · 帧时长不变"], 1.45))
    S.append(badge(296, 110, "② 配置行行尾",
                   ["恒 K2", "→", "SCREN=1 → K3 · SCREN=0 → K2",
                    "锁 SCREN · key 复位 0XFFFF"], 1.6))
    S.append(badge(436, 96, "③ CTRL_F 加扰策略",
                   ["随加扰域 · 推进 SCR_KEY", "→", "恒不加扰 · 不推进 SCR_KEY"], 1.75))

    S.append(G([T(600, 552, "基线 → 现状", 10.5, C["muted"], 600)], wrap=("fade", 1.85, None)))
    S.extend(ARROW(512, 566, 688, 566, C["gray"], "ar-gray", draw_delay=1.85))

    # —— 底部证据带 ——
    S.append(G([
        R(40, 680, 1120, 76, fill=C["container"], stroke=C["line"], rx=8),
        T(56, 700, "证据与联动", 10.5, C["dark"], 600, "start"),
        T(56, 720, "git diff f54f8d67..44e48592 -- isptx_sequence.sv：CTRL_F 1'b0（不加扰）/ K3_CODE / VFP hunk",
          10, C["muted"], None, "start"),
        T(56, 738, "SCREN=1 前置已落地：t_H3840_V16_FPS120_SCREN1_420b_for_chengli_test（1022 入库 · BYTE0_BIT3_0=0100）",
          10, C["muted"], None, "start"),
        T(56, 756, "不变项：Active 行尾统一 K2 · LSB-first 位序 · LSP / IDLE / K 码恒不加扰（差异审计 §4.4）",
          10, C["muted"], None, "start"),
    ], wrap=("fade", 2.1, None)))
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
