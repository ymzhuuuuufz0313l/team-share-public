#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crop_image.py — 分数框裁剪 / 自动裁白边（§11.2）。

CLI：argv[1] = 输入 JSON 路径 {source, out, box|null, auto_trim, margin, thresholds?}
box = 分数 {left,top,right,bottom}（0..1 相对原图，含端点）。
auto_trim：灰度阈值 ≥245 视为背景，先二值化再 getbbox()（陷阱：直接灰度 getbbox 会把暗背景当前景）。
stdout 恰好一行 JSON：{ok, path, width, height, bytes} + metrics；0 面积 → {ok:false, code:"CROP_EMPTY"}。
"""
import json
import os
import sys

import numpy as np
import cv2
from PIL import Image


def read_input(argv):
    with open(argv[1], "r", encoding="utf-8") as f:
        return json.load(f)


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def clamp01(v):
    return max(0.0, min(1.0, float(v)))


def metrics(img, short_min, aspect_max, lap_min):
    w, h = img.size
    gray = cv2.cvtColor(np.array(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    lap = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    short = min(w, h)
    aspect = (max(w, h) / float(min(w, h))) if min(w, h) > 0 else 0.0
    flags = []
    if short < short_min:
        flags.append("short_edge_lt_480")
    if aspect > aspect_max:
        flags.append("aspect_gt_8")
    if lap < lap_min:
        flags.append("laplacian_lt_50")
    return {
        "width": w, "height": h, "short_edge_px": short,
        "aspect_ratio": round(aspect, 6), "laplacian_var": round(lap, 4),
        "too_small": len(flags) > 0, "flags": flags,
    }


def main():
    inp = read_input(sys.argv)
    source = inp["source"]
    out = inp["out"]
    box = inp.get("box")
    auto_trim = bool(inp.get("auto_trim"))
    margin = int(inp.get("margin", 0) or 0)
    th = inp.get("thresholds") or {}
    short_min = th.get("short_edge_min", 480)
    aspect_max = th.get("aspect_max", 8)
    lap_min = th.get("laplacian_min", 50.0)

    img = Image.open(source).convert("RGB")
    w, h = img.size

    if box is not None:
        x1 = int(clamp01(box["left"]) * w)
        y1 = int(clamp01(box["top"]) * h)
        x2 = int(clamp01(box["right"]) * w)
        y2 = int(clamp01(box["bottom"]) * h)
    else:
        # auto_trim：灰度阈值 ≥245 视为背景，先二值化再 getbbox
        gray = np.array(img.convert("L"))
        binary = np.where(gray >= 245, 0, 255).astype("uint8")
        bbox = Image.fromarray(binary).getbbox()
        if bbox is None:
            emit({"ok": False, "code": "CROP_EMPTY", "message": "全背景，无可裁剪前景"})
            return
        x1, y1, x2, y2 = bbox

    if margin > 0:
        x1 = max(0, x1 - margin)
        y1 = max(0, y1 - margin)
        x2 = min(w, x2 + margin)
        y2 = min(h, y2 + margin)
    x1 = max(0, min(w, x1))
    y1 = max(0, min(h, y1))
    x2 = max(0, min(w, x2))
    y2 = max(0, min(h, y2))
    if x2 <= x1 or y2 <= y1:
        emit({"ok": False, "code": "CROP_EMPTY", "message": "裁剪结果为 0 面积"})
        return

    cropped = img.crop((x1, y1, x2, y2))
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    cropped.save(out, "PNG")
    res = metrics(cropped, short_min, aspect_max, lap_min)
    res["ok"] = True
    res["path"] = out
    res["bytes"] = os.path.getsize(out)
    emit(res)


if __name__ == "__main__":
    main()
