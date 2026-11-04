#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_png_1104v2.py — 1104V2 独立版 PNG 快照渲染器（2026-11-04）

对 ./51…56_signoff_*.svg（静态版=事实源）逐张 Edge 无头截图出同名 PNG：
  msedge --headless=new --disable-gpu --force-device-scale-factor=2
         --window-size=<viewBox 宽,高> --virtual-time-budget=3000 --screenshot=…
  · 窗口尺寸=SVG viewBox（1:1 布局），DPR2 → PNG 为 2× 尺寸（矢量重栅格化，PPT 缩放不糊）
  · 静态版无动画 CSS，budget 仅等字体/布局就绪
  · SVG 截图文件延迟落盘（1~30s）：轮询最多 40s 再判失败（blueprint-ui-style skill 实测口径）
  · 一次浏览器调用只渲染一张（skill 铁律）
复跑：python render_png_1104v2.py
"""
import os, re, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
NAMES = ["51_signoff_setup_hk11", "52_signoff_hold_hk11", "53_signoff_trans_hk11",
         "54_signoff_physkew_hk11", "55_signoff_sdskew_margin_hk11", "56_signoff_shift_window_hk11"]

def svg_size(path):
    head = open(path, encoding="utf-8").read(400)
    m = re.search(r'width="(\d+)" height="(\d+)"', head)
    return int(m.group(1)), int(m.group(2))

def render(name):
    svg = os.path.join(BASE, name + ".svg")
    png = os.path.join(BASE, name + ".png")
    if os.path.exists(png):
        os.remove(png)
    w, h = svg_size(svg)
    url = "file:///" + svg.replace("\\", "/")
    prof = os.path.join(os.environ.get("TEMP", "."), "dsh_png_1104v2_" + name)
    cmd = [EDGE, "--headless=new", "--disable-gpu", "--user-data-dir=" + prof,
           "--force-device-scale-factor=2", "--window-size=%d,%d" % (w, h),
           "--virtual-time-budget=3000", "--screenshot=" + png, url]
    subprocess.run(cmd, capture_output=True, timeout=120)
    for _ in range(80):  # 延迟落盘轮询（最多 40s）
        if os.path.exists(png) and os.path.getsize(png) > 0:
            break
        time.sleep(0.5)
    if not os.path.exists(png):
        print("  [FAIL] %s.png 未落盘" % name)
        return False
    print("  [ok] %s.png  (%dx%d svg -> %s B)" % (name, w, h, format(os.path.getsize(png), ",")))
    return True

if __name__ == "__main__":
    print("render_png_1104v2 (Edge headless, DPR2):")
    ok = all(render(n) for n in NAMES)
    print("ALL", "PASS" if ok else "FAIL")
# ymzhu 2026-11-04 11:42
