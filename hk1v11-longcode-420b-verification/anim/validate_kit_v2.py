# -*- coding: utf-8 -*-
"""Motion Kit v2 中央校验：7 点 + 动效结构检查。用法: python validate_kit_v2.py <name1> [name2 ...]"""
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
    r["keyframes"] = "OK" if data.count("@keyframes") >= 4 else "NG"
    m1 = re.search(r"<svg[^>]*>", open(s, encoding="utf-8").read())
    m2 = re.search(r"<svg[^>]*>", data)
    r["svgtag"] = "OK" if m1 and m2 and m1.group(0) == m2.group(0) else "NG"
    r["size"] = "OK" if os.path.getsize(a) > 1024 else "NG"
    rm = re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}", data, re.S)
    ok_rm = (rm is not None
             and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S) is not None)
    r["rmfix"] = "OK" if ok_rm else "NG"
    # v2 结构检查
    r["draw"] = str(len(re.findall(r'class="draw"', data)))
    r["flowdot"] = str(len(re.findall(r'class="flowdot"', data)))
    r["cellwave"] = str(len(re.findall(r'class="cellwave"', data)))
    r["glow"] = str(len(re.findall(r'class="glow-[bgo]"', data)))
    r["step"] = str(len(re.findall(r'class="step"', data)))
    r["march"] = str(len(re.findall(r'class="(march|fademarch)"', data)))
    r["row"] = str(len(re.findall(r'class="row"', data)))
    ok = all(str(v) == "OK" for k, v in r.items() if k in
             ("xml", "text", "noscript", "keyframes", "svgtag", "size", "rmfix"))
    detail = " ".join(f"{k}={v}" for k, v in r.items() if k not in ("xml", "text", "noscript", "keyframes", "svgtag", "size", "rmfix") or str(v) != "OK")
    print(f"{'PASS' if ok else 'FAIL'} {t}  [{detail}]")
    return ok

if __name__ == "__main__":
    allok = all(check(t) for t in sys.argv[1:])
    print("\nOVERALL:", "ALL PASS" if allok else "SOME FAILED")
    sys.exit(0 if allok else 1)
