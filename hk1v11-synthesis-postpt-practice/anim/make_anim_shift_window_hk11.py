#!/usr/bin/env python
# -*- coding: utf-8 -*-
# make_anim_shift_window_hk11.py — v4 双版管线动画生成器
# 源：../56_signoff_shift_window_hk11.svg（静态事实源，只读）
# 出：56_signoff_shift_window_hk11.svg（anim/，动画版）
# 动画（v4.1 口径）：无 scale，只用 opacity + drop-shadow + stroke-dashoffset
#   入场：面板/行错峰浮现（≤2.5s）
#   稳态：左右箭头虚线生长（6s）+ 碰界红线辉光呼吸（3s）——2 族
import io, os, hashlib

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "..", "56_signoff_shift_window_hk11.svg")
OUT = os.path.join(BASE, "56_signoff_shift_window_hk11.svg")

CSS = """<style>
.head, .panel { opacity:0; animation: rowIn .5s cubic-bezier(.22,.7,.3,1) forwards; }
.row { opacity:0; animation: rowIn .4s ease forwards; }
@keyframes rowIn { from { opacity:0; transform:translateY(4px); } to { opacity:1; transform:none; } }
.arrowDash { stroke-dasharray: 8,5; animation: arrowGrow 6s linear infinite; }
@keyframes arrowGrow { 0% { stroke-dashoffset:0; } 100% { stroke-dashoffset:-52; } }
.boundPulse { animation: boundGlow 3s ease-in-out infinite; }
@keyframes boundGlow { 0%,100% { opacity:1; filter:drop-shadow(0 0 0 rgba(185,28,28,0)); } 50% { opacity:.7; filter:drop-shadow(0 0 6px rgba(185,28,28,.8)); } }
.formulaGlow { animation: fGlow 4s ease-in-out infinite; }
@keyframes fGlow { 0%,100% { opacity:1; } 50% { opacity:.75; } }
@media (prefers-reduced-motion:reduce) { *{animation:none!important} .head,.panel,.row{opacity:1!important} .arrowDash{stroke-dasharray:none!important} }
</style>"""

def build():
    svg = io.open(SRC, encoding="utf-8", newline="").read()
    assert svg.lstrip().startswith("<svg"), "bad source"
    assert "<style>" not in svg, "source must be static"
    assert "arrowDash" not in svg, "already anim"

    # 1) 注入 CSS
    svg = svg.replace("<svg ", "<svg ", 1)  # no-op, keep structure
    # 在 </svg> 前面插 style + class 标记
    inject = CSS + "\n"

    # 2) 给箭头线加 class（通过 marker-end 或 stroke 色匹配）
    # 左右容限箭头：蓝色 stroke，有 marker-end
    svg = svg.replace('stroke="#1d4ed8" stroke-width="3" marker-end',
                      'stroke="#1d4ed8" stroke-width="3" class="arrowDash" marker-end')
    # 碰界红线：红色 stroke-dasharray
    svg = svg.replace('stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="5,3"',
                      'stroke="#b91c1c" stroke-width="2.5" stroke-dasharray="5,3" class="boundPulse"')
    # 公式面板：底部公式 rect
    svg = svg.replace('fill="%s" stroke="%s" stroke-width="1.2"' % ("#f4f1ea", "#c9bfa8"),
                      'fill="#f4f1ea" stroke="#c9bfa8" stroke-width="1.2" class="formulaGlow"')

    # 3) 面板入场 class
    svg = svg.replace('<rect x="40" y="90"', '<rect class="panel" x="40" y="90"')
    svg = svg.replace('<rect x="40" y="540"', '<rect class="panel" style="animation-delay:.3s" x="40" y="540"')

    # 4) 注入 CSS 在 </svg> 前
    svg = svg.replace("</svg>", inject + "</svg>")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
    m1 = hashlib.md5(svg.encode()).hexdigest()
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(svg)
    m2 = hashlib.md5(io.open(OUT, encoding="utf-8").read().encode()).hexdigest()
    print("written %s  %dB  idem=%s" % (OUT, len(svg), "✓" if m1 == m2 else "✗"))

if __name__ == "__main__":
    build()
# ymzhu 2026-10-30 20:50
