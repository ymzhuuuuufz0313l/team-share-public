#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
render_png_1118v1.py — 1118V1 站点换版 PNG 快照渲染器（2026-11-18）

流程逐字节沿用 render_png_1104v2.py（Edge 无头 DPR2，一次浏览器调用只渲染一张，
PNG 延迟落盘轮询最多 40s），仅改两处：
  ① 源 = ../5{1..6}_signoff_*.svg（站点主名静态版=事实源，1118V1 代，
     gen_signoff_1118v1.py 产物）
  ② 出 = --out DIR（默认 %TEMP%/signoff_1118v1_png）：PNG 只进日期夹、不占主名，
     verify_png_1118v1.py 验毕后经 archive_snapshot 移入 images/archive/20261118/
复跑：python render_png_1118v1.py [--out DIR]
"""
import argparse, os, re, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.dirname(BASE)   # .../hk1v11-synthesis-postpt-practice/images
DEF_OUT = os.path.join(os.environ.get("TEMP", "."), "signoff_1118v1_png")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
NAMES = ["51_signoff_setup_hk11", "52_signoff_hold_hk11", "53_signoff_trans_hk11",
         "54_signoff_physkew_hk11", "55_signoff_sdskew_margin_hk11", "56_signoff_shift_window_hk11"]

def svg_size(path):
    m = re.search(r'width="(\d+)" height="(\d+)"', open(path, encoding="utf-8").read(400))
    return int(m.group(1)), int(m.group(2))

def render(name, out_dir):
    svg = os.path.join(SRC_DIR, name + ".svg")
    png = os.path.join(out_dir, name + ".png")
    if os.path.exists(png):
        os.remove(png)
    w, h = svg_size(svg)
    url = "file:///" + svg.replace("\\", "/")
    prof = os.path.join(os.environ.get("TEMP", "."), "dsh_png_1118v1_" + name)
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
    _ap = argparse.ArgumentParser()
    _ap.add_argument("--out", default=DEF_OUT, help="PNG 输出目录（默认 %%TEMP%%/signoff_1118v1_png）")
    args = _ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    print("render_png_1118v1 (Edge headless, DPR2):")
    ok = all(render(n, args.out) for n in NAMES)
    print("ALL", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)
# ymzhu 2026-11-18 15:30
