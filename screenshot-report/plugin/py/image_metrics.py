#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""image_metrics.py — 尺寸 / 长宽比 / Laplacian 模糊度体检（§11.1）。

CLI：argv[1] = 输入 JSON 路径 {path, thresholds?}
stdout 恰好一行 JSON：{ok, width, height, short_edge_px, aspect_ratio, laplacian_var, too_small, flags}
flags 用 §8.2 三个枚举值：short_edge_lt_480 / aspect_gt_8 / laplacian_lt_50。
"""
import json
import sys

import numpy as np
import cv2
from PIL import Image


def read_input(argv):
    with open(argv[1], "r", encoding="utf-8") as f:
        return json.load(f)


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def compute_flags(w, h, lap, short_min, aspect_max, lap_min):
    short = min(w, h)
    aspect = (max(w, h) / float(min(w, h))) if min(w, h) > 0 else 0.0
    flags = []
    if short < short_min:
        flags.append("short_edge_lt_480")
    if aspect > aspect_max:
        flags.append("aspect_gt_8")
    if lap < lap_min:
        flags.append("laplacian_lt_50")
    return short, aspect, flags


def main():
    inp = read_input(sys.argv)
    path = inp["path"]
    th = inp.get("thresholds") or {}
    short_min = th.get("short_edge_min", 480)
    aspect_max = th.get("aspect_max", 8)
    lap_min = th.get("laplacian_min", 50.0)
    img = Image.open(path).convert("RGB")
    w, h = img.size
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    short, aspect, flags = compute_flags(w, h, lap, short_min, aspect_max, lap_min)
    emit({
        "ok": True, "width": w, "height": h, "short_edge_px": short,
        "aspect_ratio": round(aspect, 6), "laplacian_var": round(lap, 4),
        "too_small": len(flags) > 0, "flags": flags,
    })


if __name__ == "__main__":
    main()
