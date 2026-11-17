#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_power_composition_donut_1v11_1v22_3g.py — 3G 档环形图动画 SVG 生成器。

做法：**不复制**动画逻辑，直接复用 §4.5.1 的 canonical 生成器
`make_anim_power_composition_donut_1v11_1v22.py`（Motion Kit v4），只把 SRC/OUT 指向 3G 档：

  源   images/power_composition_donut_1v11_1v22_3g.svg        （gen_donut_svg.py，PWRCASE=3g）
  产物 images/anim/power_composition_donut_1v11_1v22_3g.svg   （本脚本产）

3G 侧环仍是 9 扇区（1V11）+ 7 扇区（1V22 已闭合），与 canonical 生成器的结构断言一致，
故入场时序（图例/面板/扇区/标签/中心）与稳态呼吸族和 4.46G 版完全相同。

运行：cd E:/project/team-share-public/hk1v11-synthesis-postpt-practice/images/anim && \\
      python make_anim_power_composition_donut_1v11_1v22_3g.py
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANON = HERE / "make_anim_power_composition_donut_1v11_1v22.py"
BASE = Path(r"E:/project/team-share-public/hk1v11-synthesis-postpt-practice")

spec = importlib.util.spec_from_file_location("make_anim_donut_canon", CANON)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

mod.SRC = BASE / "images" / "power_composition_donut_1v11_1v22_3g.svg"
mod.OUT = HERE / "power_composition_donut_1v11_1v22_3g.svg"

if __name__ == "__main__":
    assert mod.SRC.exists(), f"缺 3G 静态源: {mod.SRC}"
    print(f"[3G] SRC={mod.SRC.name}  OUT={mod.OUT.name}")
    mod.main()
# ymzhu 2026-11-17 17:35
