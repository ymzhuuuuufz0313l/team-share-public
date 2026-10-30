#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make_anim_shift_window_hk11.py — v4 双版管线动画生成器
# v2 2026-10-30：修 SRC path bug（../56_*.svg → ../images/56_*.svg）；
#   全面提速（ymzhu 反馈"太慢"）：入场 .5s→.35s、箭头虚线 6s→2.4s、
#   红线辉光 3s→1.5s、公式辉光 4s→2s
# 源：../images/56_signoff_shift_window_hk11.svg（静态事实源，只读）
# 出：56_signoff_shift_window_hk11.svg（anim/，动画版）
# 动画（v4.1 口径）：无 scale，只用 opacity + drop-shadow + stroke-dashoffset
import io, os, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "..", "images", "56_signoff_shift_window_hk11.svg")
OUT = os.path.join(BASE, "56_signoff_shift_window_hk11.svg")

CSS = """<style>
.head, .panel { opacity:0; animation: rowIn .35s cubic-bezier(.22,.7,.3,1) forwards; }
.row { opacity:0; animation: rowIn .3s ease forwards; }
@keyframes rowIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:none; } }
.arrowDash { stroke-dasharray: 8,5; animation: arrowGrow 2.4s linear infinite; }
@keyframes arrowGrow { 0% { stroke-dashoffset:0; } 100% { stroke-dashoffset:-52; } }
.boundPulse { animation: boundGlow 1.5s ease-in-out infinite; }
@keyframes boundGlow { 0%,100% { opacity:1; filter:drop-shadow(0 0 0 rgba(185,28,28,0)); } 50% { opacity:.7; filter:drop-shadow(0 0 6px rgba(185,28,28,.8)); } }
.formulaGlow { animation: fGlow 2s ease-in-out infinite; }
@keyframes fGlow { 0%,100% { opacity:1; } 50% { opacity:.75; } }
@media (prefers-reduced-motion:reduce) { *{animation:none!important} .head,.panel,.row{opacity:1!important} .arrowDash{stroke-dasharray:none!important} }
</style>"""

def build():
    svg = io.open(SRC, encoding="utf-8", newline="").read()
    assert svg.lstrip().startswith("<svg"), "bad source"
    assert "animation" not in svg and "@keyframes" not in svg, "source must be static"
    assert "arrowDash" not in svg, "already anim"

    # 1) 箭头线（蓝 stroke + marker-end）→ 虚线生长
    n1 = svg.count('stroke="#1d4ed8" stroke-width="3" marker-end')
    svg = svg.replace('stroke="#1d4ed8" stroke-width="3" marker-end',
                      'stroke="#1d4ed8" stroke-width="3" class="arrowDash" marker-end')
    # 2) 碰界红线（红 stroke-dasharray）→ 辉光呼吸
    n2 = svg.count('stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="5,3"')
    svg = svg.replace('stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="5,3"',
                      'stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="5,3" class="boundPulse"')
    # 3) 公式面板 → 慢辉光
    n3 = svg.count('fill="#f4f1ea" stroke="#c9bfa8" stroke-width="1.2"')
    svg = svg.replace('fill="#f4f1ea" stroke="#c9bfa8" stroke-width="1.2"',
                      'fill="#f4f1ea" stroke="#c9bfa8" stroke-width="1.2" class="formulaGlow"')

    # 4) 面板入场 class
    svg = svg.replace('<rect x="40" y="90"', '<rect class="panel" x="40" y="90"')
    svg = svg.replace('<rect x="40" y="540"', '<rect class="panel" style="animation-delay:.15s" x="40" y="540"')

    # 5) 注入 CSS 在 </svg> 前
    svg = svg.replace("</svg>", CSS + "\n</svg>")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
    back = io.open(OUT, encoding="utf-8", newline="").read()
    ok = back == svg
    print("written %s  %dB  idem=%s  inj: arrow=%d bound=%d formula=%d" % (
        OUT, len(svg), "OK" if ok else "NG", n1, n2, n3))
    assert n1 == 2 and n2 == 2 and n3 == 1, "inject count mismatch"

if __name__ == "__main__":
    build()
# ymzhu 2026-10-30 21:05
