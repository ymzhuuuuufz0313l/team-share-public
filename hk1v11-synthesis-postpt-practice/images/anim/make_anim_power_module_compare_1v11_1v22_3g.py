#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_power_module_compare_1v11_1v22_3g.py — 3G 档动画 SVG 生成器（复用 v4 Motion Kit）。

做法：**不复制**动画逻辑，直接复用 §4.5.1 的 canonical 生成器
`make_anim_power_module_compare_1v11_1v22.py`（Motion Kit v4，逐字嵌入 kit CSS、
源 SVG 只读、text 多重集零改动、确定性幂等），只把它的 SRC/OUT 指向 3G 档静态源与动画产物：

  源   images/power_module_compare_1v11_1v22_3g.svg        （gen_power_module_compare_svg.py --write 产）
  产物 images/anim/power_module_compare_1v11_1v22_3g.svg   （本脚本产）

因此 3G 动画版与 4.46G 版是同一套入场时序 / 稳态呼吸族 / reduced-motion 守卫，
几何逐字节来自静态源（条宽、标签、颜色零改动），只有档位文字不同。

运行：cd E:/project/team-share-public/hk1v11-synthesis-postpt-practice/images/anim && \\
      python make_anim_power_module_compare_1v11_1v22_3g.py
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANON = HERE / "make_anim_power_module_compare_1v11_1v22.py"
BASE = Path(r"E:/project/team-share-public/hk1v11-synthesis-postpt-practice")

spec = importlib.util.spec_from_file_location("make_anim_module_canon", CANON)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.SRC = BASE / "images" / "power_module_compare_1v11_1v22_3g.svg"
mod.OUT = HERE / "power_module_compare_1v11_1v22_3g.svg"

if __name__ == "__main__":
    assert mod.SRC.exists(), f"缺 3G 静态源: {mod.SRC}"
    print(f"[3G] SRC={mod.SRC.name}  OUT={mod.OUT.name}")
    mod.main()
# ymzhu 2026-11-17 17:35
