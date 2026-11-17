# -*- coding: utf-8 -*-
# validate_kit_v4.py — 本站 MOTION_KIT v4 的机器校验（只看不写）
#
# 逐条对应 image/anim/MOTION_KIT.md §0 铁律。用法（站点根目录）：
#   python image/tools/validate_kit_v4.py            # 校验全部 image/anim/*.svg
#   python image/tools/validate_kit_v4.py 38_buf_type.svg ...   # 只校验指定图
# 退出码 0 = 全通过；1 = 有 FAIL。
import glob
import io
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
ANIM = os.path.join(GUIDE, "image", "anim")
STATIC = os.path.join(GUIDE, "image")


def texts(s):
    return Counter(re.findall(r"<text\b[^>]*>(.*?)</text>", s, re.S))


def validate(anim_path):
    name = os.path.basename(anim_path)
    res = []
    s = io.open(anim_path, encoding="utf-8").read()
    ok = True

    def add(label, good, detail=""):
        nonlocal ok
        ok = ok and good
        res.append((label, good, detail))

    # 1 XML 良构
    try:
        root = ET.parse(anim_path).getroot()
        add("XML 良构", True)
    except Exception as e:
        add("XML 良构", False, str(e))
        return name, res, False
    # 2 无 <script>、无外部资源
    add("无 <script>", "<script" not in s.lower())
    ext = re.findall(r'(?:href|xlink:href)\s*=\s*"(?!#)[^"]+"', s)
    add("无外部引用", not ext, ",".join(ext[:3]))
    add("无 SMIL <animate>", "<animate" not in s.lower())
    # 3 有 @keyframes（动画版）
    add("含 @keyframes", "@keyframes" in s,
        "keyframes=%d" % s.count("@keyframes"))
    # 4 reduced-motion 恰好一处
    n = s.count("prefers-reduced-motion")
    add("prefers-reduced-motion 唯一", n == 1, "count=%d" % n)
    # 5 根元素 width/height 为无单位数值或 px（禁 pt）
    bad_unit = re.search(r'<svg\b[^>]*?\b(width|height)="[\d.]+(pt|mm|cm|in)"', s)
    add("根元素单位合规", bad_unit is None, bad_unit.group(0) if bad_unit else "")
    # 6 与静态版几何/文字一致（width/height/viewBox + <text> 多重集）
    st = os.path.join(STATIC, name)
    if os.path.exists(st):
        ss = io.open(st, encoding="utf-8").read()
        try:
            sroot = ET.parse(st).getroot()
            geo_ok = all(root.get(a) == sroot.get(a) for a in ("width", "height", "viewBox"))
        except Exception:
            geo_ok = False
        add("几何与静态版一致", geo_ok,
            "anim=%sx%s static=%sx%s" % (root.get("width"), root.get("height"),
                                         (sroot.get("width") if 'sroot' in dir() else "?"),
                                         (sroot.get("height") if 'sroot' in dir() else "?")))
        add("<text> 多重集与静态版一致", texts(s) == texts(ss),
            "anim=%d static=%d" % (sum(texts(s).values()), sum(texts(ss).values())))
    else:
        add("静态版存在", False, "缺 image/%s" % name)
    return name, res, ok


def main():
    args = [a for a in sys.argv[1:]]
    paths = ([os.path.join(ANIM, a) for a in args] if args
             else sorted(glob.glob(os.path.join(ANIM, "*.svg"))))
    fails = 0
    for p in paths:
        name, res, ok = validate(p)
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            fails += 1
        for label, good, detail in res:
            if not good or detail:
                print("    %s %-26s %s" % ("O" if good else "X", label, detail))
    print("---- 合计 %d 张，FAIL %d 张" % (len(paths), fails))
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 19:43
