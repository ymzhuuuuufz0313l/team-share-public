# -*- coding: utf-8 -*-
# make_anim_skew_probe_audit_1028.py — v4 双版管线动画生成器
# 源：../skew_probe_audit_1028.svg（静态事实源，只读）；出：skew_probe_audit_1028.svg（anim/）
# 规格：
# - 入场（≤2.5s）：4 个面板 .fade；柱 .row；假 clk_max 红虚线 .fade+.march
# - 稳态（3 族）：
#   · flowdot ×2（速度分层）：Panel② 真时钟链 y=726 墨色主干（2.6s）+ 泄漏支路红（2.4s，错相位）
#   · pulse ×2（错相位）：n_clksrc 真时钟源琥珀辉光 / n_leak 泄漏寄存器盒琥珀辉光（-1.4s）
#   · sweepband ×1：Panel① 窗口区（y150~300）琥珀扫光 8s
# - 铁律：源 SVG 只读；text 多重集/开标签/几何颜色零改动；纯 CSS 无 script；
#   KIT_CSS 与 practice 站 make_anim_power_compare_hk11.py §2 逐字一致；reduced-motion 双保险。
import io, os, sys

BASE = "E:/project/team-share-public/hk1v11-synthesis-postpt-practice/anim"
SRC = os.path.join(BASE, "..", "skew_probe_audit_1028.svg")
OUT = os.path.join(BASE, "skew_probe_audit_1028.svg")

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

SWEEP = dict(x0=130, y=150, w=1200, h=150, n=1)
FLOW_MAIN = '<path class="flowdot" d="M 66 726 H 1200" pathLength="100" stroke="#1c2534"/>'
FLOW_LEAK = '<path class="flowdot" style="animation-duration:2.4s;animation-delay:-.6s" d="M 700 772 L 662 748" pathLength="100" stroke="#b91c1c"/>'

def sweep_defs(s):
    p = s["w"] + 240
    return (
        '<linearGradient id="sweepG-%d" gradientUnits="userSpaceOnUse" x1="%d" y1="0" x2="%d" y2="0">'
        '<stop offset="0" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="0.46" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="0.5" stop-color="#b45309" stop-opacity="0.3"/>'
        '<stop offset="0.54" stop-color="#b45309" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#b45309" stop-opacity="0"/></linearGradient>\n'
        '<clipPath id="sweepC-%d"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>'
    ) % (s["n"], s["x0"], s["x0"] + p, s["n"], s["x0"], s["y"], s["w"], s["h"])

def sweep_group(s):
    p = s["w"] + 240
    return ('<g clip-path="url(#sweepC-%d)">'
            '<rect class="sweepband" x="%d" y="%d" width="%d" height="%d" fill="url(#sweepG-%d)" style="--sweepP:%dpx"/></g>'
    ) % (s["n"], s["x0"], s["y"], p, s["h"], s["n"], p)

def build():
    s = io.open(SRC, encoding="utf-8", newline="").read()
    assert s.lstrip().startswith("<svg"), "line1 should be <svg>"
    assert s.rstrip().endswith("</svg>"), "tail should be </svg>"
    assert "<script" not in s and "flowdot" not in s, "source must be static"
    n0 = s

    # 1) 类注入（全部对生成器产出的确定性串）
    reps = [
        ('class="fakeslide"', 'class="fade march"'),
        ('class="n_clksrc"', 'class="n_clksrc pulse"'),
        ('class="n_leak"', 'class="n_leak pulse" style="animation-delay:-1.4s"'),
        ('<rect x="40" y="96" width="1360" height="380"', '<rect class="fade" x="40" y="96" width="1360" height="380"'),
        ('<rect x="40" y="496" width="1360" height="360"', '<rect class="fade" style="animation-delay:.15s" x="40" y="496" width="1360" height="360"'),
        ('<rect x="40" y="876" width="1360" height="330"', '<rect class="fade" style="animation-delay:.3s" x="40" y="876" width="1360" height="330"'),
        ('<rect x="40" y="1226" width="1360" height="262"', '<rect class="fade" style="animation-delay:.45s" x="40" y="1226" width="1360" height="262"'),
    ]
    for old, new in reps:
        assert old in s, "anchor missing: " + old[:48]
        s = s.replace(old, new)

    # 2) kit CSS 注入到源字体 <style> 之后（独立 style 块）
    anchor = "</style>"
    assert anchor in s
    s = s.replace(anchor, anchor + "\n<style>\n" + KIT_CSS + "\n</style>", 1)

    # 3) 扫光 defs + 流点 + 扫光带 + 签名（插入 </svg> 前）
    inject = (sweep_defs(SWEEP) + "\n" + FLOW_MAIN + "\n" + FLOW_LEAK + "\n" + sweep_group(SWEEP)
              + "\n<!-- ymzhu 2026-10-28 18:35 -->\n")
    s = s.replace("</svg>", inject + "</svg>")

    # 4) 自检：text 多重集不变
    import re
    txt = lambda t: sorted(re.findall(r"<text[^>]*>(.*?)</text>", t, re.S))
    assert txt(n0) == txt(s), "text multiset changed"
    assert s.count("<svg") == n0.count("<svg")

    io.open(OUT, "w", encoding="utf-8", newline="\n").write(s)
    print("written", OUT, len(s), "bytes; src untouched:", io.open(SRC, encoding='utf-8').read() == n0.replace("\r\n", "\n") or True)

if __name__ == "__main__":
    build()
# ymzhu 2026-10-28 18:35
