# -*- coding: utf-8 -*-
# gen_clkperiod_image.py — regenerate image/26_clk_period.png from the real clk_period.tcl
# Active config (2026-08): MARGIN 0.80/1.00, DPSEL_I=0 (1P), RX0=10.08ns, RX1=17.1ns
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _gen_be_review_images as G

SRC = r"E:/project/HV2M23/SYNTHESIS/common/tcl_dir/common/clk_period.tcl"
lines = G.read_lines(SRC, 1, 8) + [(None, "        ……")] + G.read_lines(SRC, 14, 25)

G.render_code(
    "26_clk_period.png",
    "clk_period.tcl — MARGIN 0.80/1.00、DPSEL_I=0（1P）、RX0 10.08 / RX1 17.1",
    "高亮行 = 当前生效配置（按真实文件行号）",
    lines,
    hl_lines=(1, 2, 3, 4, 5, 16, 20, 21),
)
print("done")
