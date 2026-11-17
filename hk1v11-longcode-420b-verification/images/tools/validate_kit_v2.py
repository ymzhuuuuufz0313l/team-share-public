# -*- coding: utf-8 -*-
"""!! DEPRECATED —— 请勿用于新校验 !!
============================================================
本脚本是 MOTION_KIT **v2** 规范的中央校验器，仅作历史存档保留。

**当前规范是 v4**，对应校验器为同目录 `validate_kit_v4.py`：
    python images/tools/validate_kit_v4.py <name1> [name2 ...]

为什么废弃（v2 与 v4 规范冲突，用 v2 跑现行图只会得到相反结论）：
  * v2 校验的是 v2 kit（`glow-*` 类、`<animate>` 驱动的旧动效）；
  * v4 明令禁止 `<script>` / `<animate>` / `glow-*`，改为纯 CSS `@keyframes`，
    并要求 >=10 个 keyframes、>=2 个稳态族、`.flowdot` stroke-width 3.5、
    `.pulse{transform-box:fill-box}`、`var(--sweepP)`、reduced-motion 兜底。

保留原因：溯源 2026-10-28~11-04 期间的 v2 图版审计结论。任务书 N4 明令
**不可删除、不可改名**，故只加本横幅。台账见 `images/anim/MOTION_KIT.md`
「校验器代际」小节。

已知缺陷（历史脚本，不再修；v4 校验器里已修）：
  * `all(check(t) for t in sys.argv[1:])` 短路 —— 第一个 FAIL 后不再校验其余文件；
  * 无参数运行时不校验任何文件，却打印 `OVERALL: ALL PASS` 并返回 0。
============================================================
Motion Kit v2 中央校验：7 点 + 动效结构检查。用法: python validate_kit_v2.py <name1> [name2 ...]"""
import xml.etree.ElementTree as ET
from collections import Counter
import re, os, sys

NS = "{http://www.w3.org/2000/svg}"
TOOLS = os.path.dirname(os.path.abspath(__file__))  # images/tools/
IMAGES = os.path.dirname(TOOLS)  # images/
ROOT = os.path.join(IMAGES, "anim")  # images/anim/
SITE = IMAGES  # images/

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
# ymzhu 2026-11-17 19:55
