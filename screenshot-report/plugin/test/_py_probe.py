#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_py_probe.py — smoke 测试像素探针（S5 用）。
用法：python _py_probe.py pixel <path> <x> <y>      → 打印 [r,g,b]
      python _py_probe.py find  <path> <json-rgb> <tol> → 打印 1/0（是否某处出现该色 ±tol）
"""
import sys
import json
from PIL import Image
import numpy as np


def main():
    mode = sys.argv[1]
    p = sys.argv[2]
    if mode == "pixel":
        x, y = int(sys.argv[3]), int(sys.argv[4])
        print(json.dumps(list(Image.open(p).convert("RGB").getpixel((x, y)))))
    elif mode == "find":
        rgb = json.loads(sys.argv[3])
        tol = int(sys.argv[4])
        arr = np.array(Image.open(p).convert("RGB")).astype(int)
        d = np.abs(arr - np.array(rgb)).max(axis=2)
        print("1" if (d <= tol).any() else "0")
    else:
        print("0")


if __name__ == "__main__":
    main()
