# -*- coding: utf-8 -*-
# gen_clkperiod_image.py — regenerate image/26_clk_period.png from the real clk_period.tcl
# R4（t20）：周期/margin 不再写死在本文件，统一从 image/tools/data/clk_params.json 读数（与页面同源）。
# 渲染标题与旧硬编码逐字符一致（零变化），数据源改动会自动反映到图题。
import sys, os, io, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gen_be_review_images as G

_HERE = os.path.dirname(os.path.abspath(__file__))
with io.open(os.path.join(_HERE, "data", "clk_params.json"), encoding="utf-8") as _f:
    _C = json.load(_f)
_A, _M = _C["active"], _C["margin"]
TITLE = ("clk_period.tcl — MARGIN %s/%s、DPSEL_I=%s（%s）、RX0 %s / RX1 %s"
         % (_M["syn"], _M["pt"], _A["dpsel_value"], _A["mode"], _A["rx0_ns"], _A["rx1_ns"]))

SRC = os.path.join(G.HV, "SYNTHESIS", "common", "tcl_dir", "common", "clk_period.tcl")
lines = G.read_lines(SRC, 1, 8) + [(None, "        ……")] + G.read_lines(SRC, 14, 25)

G.render_code(
    "26_clk_period.png",
    TITLE,
    "高亮行 = 当前生效配置（按真实文件行号）",
    lines,
    hl_lines=(1, 2, 3, 4, 5, 16, 20, 21),
)
print("done")

# ymzhu 2026-11-17 20:50
