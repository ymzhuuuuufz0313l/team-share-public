# -*- coding: utf-8 -*-
"""Motion Kit v4 中央校验：不变量 + v4 稳态结构检查。用法: python validate_kit_v4.py <name1> [name2 ...]

本站（hk1v11-lc-cpuwr-history）布局：静态版在 images/<name>.svg（SITE），
动画版与本校验器在 images/anim/（ROOT）——与 canonical 站（longcode）的
anim/-站点根 关系一致，ROOT/SITE 由本校验器文件位置自动推导，无需改动。
"""
import xml.etree.ElementTree as ET
from collections import Counter
import re, os, sys

NS = "{http://www.w3.org/2000/svg}"
ROOT = os.path.dirname(os.path.abspath(__file__))  # images/anim/
SITE = os.path.dirname(ROOT)                       # images/

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
    # v4.2: 列车元素时长下限（实例层，防 kit 默认合规而元素内联超速）
    fast = [m.group(1) for m in re.finditer(r'flow(?:dot|tail)[^"]*"[^>]*animation-duration:([0-9.]+)s', data)]
    r["train>=2.4s"] = "OK" if all(float(x) >= 2.4 for x in fast) else f"NG({','.join(fast)})"
    # 稳态族 ≥2（march/breathe 不计数）
    # 2026-11-17 加固（审查 finding R5）：旧判据只看 class 名出现次数，把整段 <style>（含 @keyframes）
    # 删掉后仍算「某族存在」——只靠 class 名就能骗过稳态检查。现要求：
    #   某族计数 > 0 **且** 该族真正依赖的 @keyframes 名在文件里被定义，才算一族生效；
    #   只有 class 实例、没有对应 keyframes 的族单独记进 steady_kf_missing，供定位。
    fam_spec = {
        "train":   (r'class="[^"]*(flowdot|flowtail)',       r"@keyframes\s+flow\s*\{"),
        "pulse":   (r'class="[^"]*pulse(-[tb])?',            r"@keyframes\s+pulse[TB]?\s*\{"),
        "sweep":   (r'class="[^"]*sweepband',                r"@keyframes\s+sweepMove\s*\{"),
        "grow":    (r'class="[^"]*dashgrow',                 r"@keyframes\s+dashgrow\s*\{"),
        "wave":    (r'class="[^"]*cellwave',                 r"@keyframes\s+wave\s*\{"),
        "step":    (r'class="[^"]*step"',                    r"@keyframes\s+stepLit\s*\{"),
    }
    fam, kf_missing = {}, []
    for name, (cls_re, kf_re) in fam_spec.items():
        n = len(re.findall(cls_re, data))
        if n == 0:
            fam[name] = 0
        elif re.search(kf_re, data):
            fam[name] = n
        else:                      # 有 class 实例但 CSS keyframes 缺失 → 该族不算生效
            fam[name] = 0
            kf_missing.append(name)
    n_fam = sum(1 for v in fam.values() if v > 0)
    r["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    if kf_missing:
        r["steady_kf_missing"] = ",".join(kf_missing)
    # 入场元素存在性（结构 sanity，不作硬门）
    for k, pat in (("draw", r'class="draw"'), ("row", r'class="row"'), ("march", r'class="(march|fade)"')):
        r[k] = str(len(re.findall(pat, data)))
    hard = ("xml", "text", "noscript", "nosmil", "keyframes", "svgtag", "size",
            "kit_train", "kit_pulse", "kit_sweep", "rmfix", "no_glow", "train>=2.4s")
    ok = all(str(r.get(k, "NG")) == "OK" or str(r.get(k, "NG")).startswith("OK(") for k in hard) \
        and str(r["steady>=2fam"]).startswith("OK")
    detail = " ".join(f"{k}={v}" for k, v in r.items() if k not in hard)
    ng = [k for k in hard
          if not (str(r.get(k, "NG")) == "OK" or str(r.get(k, "NG")).startswith("OK("))]
    if not str(r["steady>=2fam"]).startswith("OK"):
        ng.append("steady>=2fam")
    print(f"{'PASS' if ok else 'FAIL'} {t}  [{detail}]"
          + ("" if ok else "  <== NG: " + ",".join(ng)))
    return ok

def main(argv):
    """逐个校验、绝不短路；无参数时默认全量扫描 anim 目录。

    2026-11-17 修复（审查 finding）：
      · 旧版 `all(check(t) for t in sys.argv[1:])` 在**无参数**时 all(()) == True，
        空跑也打印 "OVERALL: ALL PASS" 并 exit 0 —— 假通过；
      · `all()` 短路，第一张 FAIL 就停，后面的图根本没校验、也没输出。
    """
    global ROOT, SITE
    anim_dir, site_dir, names = ROOT, SITE, []
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--anim-dir":
            anim_dir = os.path.abspath(args.pop(0))
        elif a == "--site-dir":
            site_dir = os.path.abspath(args.pop(0))
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            names.append(a)
    ROOT, SITE = anim_dir, site_dir
    if not names:
        names = sorted(os.path.splitext(f)[0] for f in os.listdir(ROOT) if f.endswith(".svg"))
        if not names:
            print("FATAL: 未给图名，且 %s 下没有 *.svg —— 拒绝空跑" % ROOT)
            return 2
        print("no-arg = 全量校验：%s 下 %d 个动画图" % (ROOT, len(names)))
        print("")
    results = [check(t) for t in names]      # 逐个跑完，不短路
    bad = [t for t, ok in zip(names, results) if not ok]
    print("")
    print("OVERALL: %d/%d PASS%s" % (len(names) - len(bad), len(names),
          "" if not bad else "  FAILED: " + ",".join(bad)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# ymzhu 2026-11-17 19:33
