#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_delta_env_components.py — 前后对比组图 3/3（Motion Kit v4 契约）

delta_env_components：激励源体系组件演进（isptx_agent 及周边，基线 07-13 vs HEAD）。
事实源：docs/HK1V11_longcode_420b_delta_audit_20261105.md（§1 波次表 / §2 逐文件
审计 / §2.6 RTL 侧事实）。

生成器从同一 scene 产出「静态 + 动画」双版：
- 静态：images/delta_env_components.svg
- 动画：images/anim/delta_env_components.svg（text 多重集与 <svg> 开标签一致）

三色标注（右 panel = 现状状态）：
- 灰 = 未变（isptx_transaction/if/agent/sequencer/bus_monitor、checker_420b 77 行零变更）
- 琥珀 = 已变（isptx_sequence 1456→1865、isptx_driver +222、ref model 0807 三修、
  checker_for_checksum、env_cfg +267 / env.sv）
- 青 = 新增（训练包序列、BCC 体系、BOE 回放、MULTI_CHIP/multi4、故障注入与恢复、
  auto_script + dplc.pl）
中列 = 7+1 波次时间线（0721v1/0807v1/0825/0924/1010/1013-14/1022/1028）；
底部 = RTL 侧联动事实带（decode_ignore 已修 / K3 延 4 拍 / 44bit / TX 通路 / tag_value 待证）。

动效规格（MOTION_KIT v4/v4.2/v4.3）：
- 入场：head(0) → 左 panel(0.15)+L 盒(0.25~0.81) → 右 panel(0.4)+R 盒(0.55~1.41)
  → 波次 chips(0.7~1.54) → 顶箭头 draw(1.6 ≥ 两端面板+0.55) → RTL 带(1.75)。
- 稳态 4 族（≤4 上限，无 march/breathe）：步骤 step（6 个青色新增盒接力点亮
  0/-1/-2/-3/-4/-5s）/ 行波 cellwave（8 波次 chips 0.15s 递增 3.8s）/
  脉冲 pulse-t（BCC 盒 -1.4s · BOE 盒 0s）/ 列车 flowdot 3 包 + 2 tail（顶箭头
  238px ≥80px，2.6s ≥2.4s）。
- 组件盒文字均为非数据 chrome + 波次 chips 8×3 行（低密度，行 < 20）。

铁律：纯 CSS in-SVG；确定性幂等；零第三方依赖。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
OUT_STATIC = BASE / "images" / "delta_env_components.svg"
OUT_ANIM = BASE / "images" / "anim" / "delta_env_components.svg"

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")
C = dict(
    dark="#1e293b", muted="#64748b", container="#f8fafc", line="#e2e8f0",
    blue="#2563eb", green="#059669", purple="#7c3aed", orange="#ea580c",
    teal="#0f766e", teal_soft="#ccfbf1", gray="#9ca3af",
)
PAL_GRAY = ("#f1f5f9", "#cbd5e1", "#475569")     # 未变
PAL_AMBER = ("#fffbeb", "#fcd34d", "#92400e")    # 已变
PAL_TEAL = ("#f0fdfa", "#5eead4", "#0f766e")     # 新增
W, H = 1200, 960

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


def cbox(x, y, w, h, title, subs, pal, badge=None, dash=None, tsize=11, ssize=9):
    """组件盒：标题 + 副标题行（自动按 pal 着色）。"""
    fill, stroke, tfill = pal
    kids = [R(x, y, w, h, fill=fill, stroke=stroke, rx=8, dash=dash)]
    kids.append(T(x + 12, y + 17, title, tsize, tfill, 600, "start"))
    yy = y + 17 + 15
    for s in subs:
        kids.append(T(x + 12, yy, s, ssize, C["muted"], None, "start"))
        yy += 13
    if badge:
        kids.append(T(x + w - 10, y + 17, badge, 8.5, tfill, 600, "end"))
    return G(kids)


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
    # —— 头部 + 图例 ——
    S.append(G([
        T(600, 38, "激励源体系组件演进：isptx_agent 及周边（基线 → HEAD）", 21, C["dark"], 600),
        T(600, 62, "66ecf97d（07-13）→ a7130ba7（1028 包后）· 差异审计 2026-11-05 · "
                   "右列颜色 = 现状状态", 11.5, C["muted"]),
        R(348, 74, 12, 12, fill=PAL_GRAY[0], stroke=PAL_GRAY[1], rx=3),
        T(366, 84, "未变（基线 = HEAD 逐字节相同）", 9.5, C["muted"], None, "start"),
        R(580, 74, 12, 12, fill=PAL_AMBER[0], stroke=PAL_AMBER[1], rx=3),
        T(598, 84, "已变", 9.5, C["muted"], None, "start"),
        R(660, 74, 12, 12, fill=PAL_TEAL[0], stroke=PAL_TEAL[1], rx=3),
        T(678, 84, "新增（0924 / 1022 为主）", 9.5, C["muted"], None, "start"),
    ], wrap=("head", 0, None)))

    # —— 左 panel：基线 ——
    lk = [R(40, 96, 330, 680, fill=C["container"], stroke=C["line"], rx=10),
          T(205, 122, "基线 · 07-13", 13, "#b45309", 600),
          LINE(56, 134, 354, 134, C["line"])]
    L = [
        ("isptx_sequence.sv（1456 行）",
         ["send_ppm_420b 主流程", "CTRL_F / Config Line 为 0717 版语义"]),
        ("isptx_driver.sv", ["常规驱动主循环"]),
        ("isptx_transaction · if · agent · sequencer",
         ["另 bus_monitor.sv", "六文件基线 = HEAD 逐字节相同"]),
        ("checker_420b.sv · 77 行",
         ["display-only · check_all() 硬编码", "scramble_en=1 + 每块 LFSR 复位 0XFFFF"]),
        ("long_encoding_ref_model.sv",
         ["编码 / 解码 ref（0807 三修前状态）"]),
        ("checker_for_checksum.sv",
         ["LC_CPUWR 直挂层次", "0X35 FSEL 追踪前 · 无 POST_SIM 桩"]),
        ("env_cfg.sv / env.sv", ["基线寄存器域与标志族"]),
    ]
    y = 150
    for i, (title, subs) in enumerate(L):
        lk.append(E("g", kids=[cbox(56, y, 298, 52, title, subs,
                                    ("#ffffff", "#d1d5db", C["dark"]))],
                    wrap=[("row", 0.25 + 0.08 * i, None)]))
        y += 66
    lk.append(E("g", kids=[
        cbox(56, y, 298, 64, "基线不存在（虚线 = 缺位）",
             ["训练包序列 / BCC 体系 / BOE 回放 / MULTI_CHIP",
              "故障注入与恢复 / auto_script / dplc.pl"],
             ("#ffffff", "#cbd5e1", C["dark"]), dash="6 4"),
    ], wrap=[("fade", 0.9, None)]))
    S.append(G(lk, wrap=("row", 0.15, None)))

    # —— 中列：波次时间线 + 顶箭头 ——
    S.append(G([T(505, 108, "演进方向", 10.5, C["muted"], 600)], wrap=("fade", 1.6, None)))
    S.extend(ARROW(386, 122, 624, 122, C["gray"], "ar-gray", draw_delay=1.6))
    S.append(LINE(505, 152, 505, 690, "#cbd5e1", 1.2, dash="4 4"))
    WAVES = [
        ("0721v1 · 1b574b63", ["CONFIG_DATA 16→24bit", "420b 编码链不受影响"], False),
        ("0807v1 · 179486aa", ["全量替换 · ref model 三修入库", "debug 日志族 · auto_script 起步"], False),
        ("0825 · f54f8d67", ["相位感知 CTRL_L（VBP/VACT/VFP）", "UTC 槽位 0-3 → 10-13"], False),
        ("0924 · 44e48592", ["CTRL_F 不加扰 · VFP[0] 承载 · 训练包", "EOL / 恢复 · case 1→190"], True),
        ("1010 · 6f94d19f", ["MULTI_CHIP fork · CH_SEL subpix 表", "drive_idle_ct"], False),
        ("1013 / 1014", ["checker POST_SIM 桩", "与 420b 激励无直接关系"], False),
        ("1022 · 5bf35dcf", ["BCC 体系 · BOE 回放 · dplc.pl", "case → 192"], True),
        ("1028 · 08befa71", ["overlay：HDL 21 + DV 51 改 / 24 新", "isptx_agent 内无 .sv 变更"], False),
    ]
    wy = 152
    for i, (t, subs, big) in enumerate(WAVES):
        fill, stroke = (C["teal_soft"], "#5eead4") if big else ("#ffffff", C["line"])
        kids = [R(392, wy, 226, 52, fill=fill, stroke=stroke, rx=8),
                T(505, wy + 17, t, 9.5, C["dark"], 600),
                T(505, wy + 32, subs[0], 8.5, C["muted"]),
                T(505, wy + 44, subs[1], 8.5, C["muted"])]
        S.append(E("g", kids=kids, wrap=[("fade", 0.7 + 0.12 * i, None),
                                         ("cellwave", 0.2 + 0.15 * i, 3.8)]))
        wy += 62
    S.append(G([T(505, wy + 16, "波次 = 差异审计 §1 表", 8.5, C["muted"])],
               wrap=("fade", 1.7, None)))

    # —— 右 panel：现状 ——
    rk = [R(640, 96, 520, 680, fill=C["container"], stroke=C["line"], rx=10),
          T(900, 122, "现状 · 1028 包后（HEAD a7130ba7）", 13, C["teal"], 600),
          LINE(656, 134, 1144, 134, C["line"])]
    RX = 656
    RW = 488
    amber = [
        ("isptx_sequence.sv：1456 → 1865 行（+409）",
         ["CTRL_F 恒不加扰 · VFP[0] 承载 · 相位感知 CTRL_L（0825）",
          "EOL 注入 · unlock 优雅停止 · send_recovery_image · MULTI_CHIP fork · exec_c C-model golden"], 54, None),
        ("isptx_driver.sv（+222 · 1022 为主）",
         ["BOE 回放 stream_drive_from_file · drive_idle_ct · drive_post_bcc_training（LOCK 稳 4us）"], 42, None),
        ("long_encoding_ref_model.sv（0807 三修）",
         ["LSP 字节序 EA→ED · tag 搜索跳 0/63 · decode_420b_to_413b 重写（先判替换再统一解扰）"], 42, None),
        ("checker_for_checksum.sv",
         ["0X35 FSEL 跟踪（0721）· LINK_CONFIG_CTRL 层次（0807）· POST_SIM 桩（1013）"], 42, None),
        ("env_cfg.sv（+267）/ env.sv",
         ["eol / bcc / unlock 标志族 · 新寄存器域 0X02-04 · 24 / 28 / 29 / 33 / 35 / 36 / 38",
          "MULTI_CHIP 下 config_db 相对路径"], 54, None),
    ]
    gray = [
        ("isptx_transaction · if · agent · sequencer · bus_monitor",
         ["基线 = HEAD 逐字节相同（零变更）"], 36, "未变"),
        ("checker_420b.sv · 77 行（自建库以来未改）",
         ["display-only · check_all() 硬编码 scramble_en=1 · 每块 LFSR 复位 0XFFFF",
          "正式比对启用前的改造点（站点 5.3 论断至今成立）"], 54, "未变"),
    ]
    teal = [
        ("＋ chpi_training_packet_sequence.sv",
         ["8B/10B 与 420b 双模式训练包 · bcc_continuous_ct 门控"], 40, "新增 · 0924"),
        ("＋ BCC 训练体系",
         ["bcc_monitor · bcc_scoreboard（covergroup + 70us 超时）· bcc_sequence"], 40, "新增 · 1022"),
        ("＋ BOE 回放",
         ["BOE_420B_TEST · sim_data_BOE_opt 12 Pat × 2 doc 逐符号回放"], 40, "新增 · 1022"),
        ("＋ MULTI_CHIP / multi4",
         ["PPM chip 切片 + fork 隔离 · CH_SEL subpix_cnt 表 · lane_delay_reverse"], 40, "新增 · 1010/1022"),
        ("＋ 故障注入与恢复",
         ["eol_missing_test · send_invalid_eol_slots · unlock_recovery · send_recovery_image"], 40, "新增 · 0924/1022"),
        ("＋ auto_script 生成链 + cmodel/dplc.pl",
         ["gen_cfg_frame / run_all 等 · --ave_rgbw / --ave_last / --dplc_group"], 40, "新增 · 0807/1022"),
    ]
    y, idx = 150, 0
    GAP = 4
    for title, subs, h, badge in amber:
        rk.append(E("g", kids=[cbox(RX, y, RW, h, title, subs, PAL_AMBER, badge)],
                    wrap=[("row", 0.55 + 0.07 * idx, None)]))
        y += h + GAP
        idx += 1
    for title, subs, h, badge in gray:
        rk.append(E("g", kids=[cbox(RX, y, RW, h, title, subs, PAL_GRAY, badge)],
                    wrap=[("row", 0.55 + 0.07 * idx, None)]))
        y += h + GAP
        idx += 1
    for k, (title, subs, h, badge) in enumerate(teal):
        wraps = [("row", 0.55 + 0.07 * idx, None), ("step", -float(k), None)]
        if k == 1:      # BCC 体系
            wraps.append(("pulse-t", -1.4, None))
        if k == 2:      # BOE 回放
            wraps.append(("pulse-t", 0, None))
        rk.append(E("g", kids=[cbox(RX, y, RW, h, title, subs, PAL_TEAL, badge)],
                    wrap=wraps))
        y += h + GAP
        idx += 1
    S.append(G(rk, wrap=("row", 0.4, None)))
    # （BCC/BOE 的 pulse-t 通过补充组包裹：在 teal 列表序 1/2 上加 wrap）

    # —— 底部 RTL 联动带 ——
    S.append(G([
        R(40, 796, 1120, 134, fill=C["container"], stroke=C["line"], rx=8),
        T(56, 820, "RTL 侧联动事实（差异审计 §2.6 · 只读核对）", 10.5, C["dark"], 600, "start"),
        T(56, 842, "decode_ignore 已修：decoder_7b.v:353 判 6-bit {0,63}（基线 7-bit 常量，tag=0 漏判）—— 站点 3.9 论断过时",
          10, C["muted"], None, "start"),
        T(56, 862, "header_mismatch 位段 [15:7] → [12:7] · dec_data_buf 42 → 44 bit · K3 复位/使能延 4 拍（K3_FIND_rp_d[3]）",
          10, C["muted"], None, "start"),
        T(56, 882, "新 TX 编码通路：LONG_ENCODING_ALIGN / ERROR_CTRL / OUTPUT（long_encoding/ +1323 行 · 站点原只画解码链）",
          10, C["muted"], None, "start"),
        T(56, 902, "tag_value 块边界时序：RTL 加载逻辑同基线 · 未见修复证据 —— 保留待修，需最新波形确认",
          10, C["muted"], None, "start"),
    ], wrap=("fade", 1.75, None)))
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
