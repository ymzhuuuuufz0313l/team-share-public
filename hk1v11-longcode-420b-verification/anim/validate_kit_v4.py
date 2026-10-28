# -*- coding: utf-8 -*-
"""Motion Kit v4 中央校验：不变量 + v4 稳态结构检查。用法: python validate_kit_v4.py <name1> [name2 ...]"""
import xml.etree.ElementTree as ET
from collections import Counter
import re, os, sys

NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.abspath(__file__))  # anim/
SITE = os.path.dirname(ROOT)

def texts(p):
    return Counter(el.text or "" for el in ET.parse(p).getroot().iter(f"{NS}text"))

def check(t):
    s = os.path.join(SITE, f"{t}.svg")
    a = os.path.join(ROOT, f"{t}.svg")
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
    for k, pat in (("draw", r'class="draw"'), ("row", r'class="row"'), ("march", r'class="(march|fade)"')):
        r[k] = str(len(re.findall(pat, data)))
    hard = ("xml", "text", "noscript", "nosmil", "keyframes", "svgtag", "size",
            "kit_train", "kit_pulse", "kit_sweep", "rmfix", "no_glow")
    ok = all(str(r.get(k, "NG")) == "OK" or str(r.get(k, "NG")).startswith("OK(") for k in hard) \
        and str(r["steady>=2fam"]).startswith("OK")
    detail = " ".join(f"{k}={v}" for k, v in r.items() if k not in hard)
    print(f"{'PASS' if ok else 'FAIL'} {t}  [{detail}]")
    return ok

if __name__ == "__main__":
    allok = all(check(t) for t in sys.argv[1:])
    print("\nOVERALL:", "ALL PASS" if allok else "SOME FAILED")
    sys.exit(0 if allok else 1)
