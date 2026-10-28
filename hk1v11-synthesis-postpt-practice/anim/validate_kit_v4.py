# -*- coding: utf-8 -*-
"""Motion Kit v4 中央校验（本站双 anim 目录版）：不变量 + v4 稳态结构检查。

本站布局（与 canonical longcode 站不同）：
  anim/<name>.svg        ← 静态版 <site>/<name>.svg        （功耗类 3 张）
  images/anim/<name>.svg ← 静态版 <site>/images/<name>.svg  （表格类 3 张）
用法: python validate_kit_v4.py <name1> [name2 ...]
（在 anim/ 或站点根目录下运行均可；自动按两个 anim 目录解析路径。）
"""
import xml.etree.ElementTree as ET
from collections import Counter
import re, os, sys

NS = "{http://www.w3.org/2000/svg}"
HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE) if os.path.basename(HERE) == "anim" else HERE
ANIM_DIRS = [os.path.join(SITE, "anim"), os.path.join(SITE, "images", "anim")]
STATIC_DIRS = [SITE, os.path.join(SITE, "images")]


def resolve(name):
    """返回 (static_path, anim_path)；两个 anim 目录都找。"""
    for d in ANIM_DIRS:
        a = os.path.join(d, f"{name}.svg")
        if os.path.isfile(a):
            # anim/ → 站根；images/anim/ → images/
            s = os.path.join(os.path.dirname(os.path.dirname(a)), f"{name}.svg")
            if os.path.isfile(s):
                return s, a
            raise FileNotFoundError(f"{a} 无对应静态版（去 /anim/ 段路径不存在）")
    for d in STATIC_DIRS:
        s = os.path.join(d, f"{name}.svg")
        if os.path.isfile(s):
            raise FileNotFoundError(f"找到静态版 {s} 但动画版不存在于任一 anim 目录")
    raise FileNotFoundError(f"{name}.svg: 静态版与动画版均未找到")


def texts(p):
    return Counter(el.text or "" for el in ET.parse(p).getroot().iter(f"{NS}text"))


def check(t):
    s, a = resolve(t)
    data = open(a, encoding="utf-8").read()
    r = {}
    try:
        ET.parse(a); r["xml"] = "OK"
    except Exception as e:
        r["xml"] = f"NG {e}"
    try:
        r["text"] = "OK" if texts(s) == texts(a) else "NG"
    except Exception as e:
        r["text"] = f"NG {e}"
    r["noscript"] = "OK" if "<script" not in data else "NG"
    r["nosmil"] = "OK" if "<animate" not in data else "NG"
    r["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"
    m1 = re.search(r"<svg[^>]*>", open(s, encoding="utf-8").read())
    m2 = re.search(r"<svg[^>]*>", data)
    r["svgtag"] = "OK" if m1 and m2 and m1.group(0) == m2.group(0) else "NG"
    r["size"] = "OK" if os.path.getsize(a) > 1024 else "NG"
    # kit v4 签名：列车粗细 / 脉冲 transform-box / 扫光 CSS 变量 / reduced-motion 双保险
    r["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    r["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    r["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    rm = re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
    r["rmfix"] = "OK" if (rm and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    # v4 废除 glow-*（由 pulse* 取代）
    r["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    # 稳态族 ≥2（march/breathe 不计数）
    fam = {
        "train":   len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
        "pulse":   len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
        "sweep":   len(re.findall(r'class="[^"]*sweepband', data)),
        "grow":    len(re.findall(r'class="[^"]*dashgrow', data)),
        "wave":    len(re.findall(r'class="[^"]*cellwave', data)),
        "step":    len(re.findall(r'class="[^"]*step"', data)),
    }
    n_fam = sum(1 for v in fam.values() if v > 0)
    r["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    # 入场元素存在性（结构 sanity，不作硬门）
    for k, pat in (("draw", r'class="[^"]*\bdraw\b'), ("row", r'class="[^"]*\brow\b'), ("march", r'class="(march|fade)"')):
        r[k] = str(len(re.findall(pat, data)))
    hard = ("xml", "text", "noscript", "nosmil", "keyframes", "svgtag", "size",
            "kit_train", "kit_pulse", "kit_sweep", "rmfix", "no_glow")
    ok = all(str(r.get(k, "NG")) == "OK" for k in hard) \
        and str(r["steady>=2fam"]).startswith("OK")
    detail = " ".join(f"{k}={v}" for k, v in r.items() if k not in hard)
    print(f"{'PASS' if ok else 'FAIL'} {t}  [{detail}]")
    return ok


if __name__ == "__main__":
    allok = all(check(t) for t in sys.argv[1:])
    print("\nOVERALL:", "ALL PASS" if allok else "SOME FAILED")
    sys.exit(0 if allok else 1)
# ymzhu 2026-10-28 17:50
