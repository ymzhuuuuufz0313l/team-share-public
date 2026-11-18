#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_png_1118v1.py — 1118V1 PNG 快照程序化验收（2026-11-18）

沿用 verify_png_1104v2.py 的几何/采样口径（几何由生成器常量直算，×2 后采样），
本版把 1104V2 时代"按旧数据硬编码的定向格子断言"全部改为 csv 数据驱动：
  ① 尺寸 = 2×viewBox（DPR2 矢量重栅格化）
  ② 标题条带色（51/52 A 族 #157a6a；53/54/55 B 族 #0e7c6b；56 纸底 #f4f1ea）+ 底缘无截断
  ③ 红格全矩阵 vs csv 逐格比对（51 setup / 52 hold / 53 trans 按 violation number>0，
     55 sdskew 按出窗），行数由 csv 行数直取（不再硬编码 35/16）
  ④ 52 hold 全 0 违例（本代事实）→ 整图不得出现红底实填（≥40px 连续段，抗 ClearType 暖边）
  ⑤ 51 存在零值绿字 #1a7a3c（setup 有全零行）；54 浅蓝最紧格 + 无红底；56 三要素色
用法：python verify_png_1118v1.py [--png DIR]   （DIR 默认 %TEMP%/signoff_1118v1_png）
"""
import argparse, os, re, sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.dirname(BASE)   # .../images（SVG 主名所在）
DEF_PNG = os.path.join(os.environ.get("TEMP", "."), "signoff_1118v1_png")
NAMES = ["51_signoff_setup_hk11", "52_signoff_hold_hk11", "53_signoff_trans_hk11",
         "54_signoff_physkew_hk11", "55_signoff_sdskew_margin_hk11", "56_signoff_shift_window_hk11"]
BAND = {"51": (21, 122, 106), "52": (21, 122, 106), "53": (14, 124, 107),
        "54": (14, 124, 107), "55": (14, 124, 107), "56": (244, 241, 234)}

def near(px, ref, tol=14):
    return all(abs(a - b) <= tol for a, b in zip(px, ref))

def svg_size(path):
    m = re.search(r'width="(\d+)" height="(\d+)"', open(path, encoding="utf-8").read(400))
    return int(m.group(1)), int(m.group(2))

def has_color(img, ref, tol=16, region=None):
    w, h = img.size
    px = img.load()
    x0, y0, x1, y1 = region or (0, 0, w, h)
    step = 4
    for y in range(y0, min(y1, h), step):
        for x in range(x0, min(x1, w), step):
            if near(px[x, y], ref, tol):
                return True
    return False

def has_red_fill(img, min_run=40):
    """整图红底检测（抗 ClearType 干扰）：只认 ≥min_run 连续像素的横向实填带。
    违例格红底 #f8dede 宽 ≈390 device px；文字子像素抗锯齿暖边（如 (241,228,215)，
    与红底差 ≤8）只有 1~2 px 孤立段——逐行数最长连续命中即可区分。"""
    w, h = img.size
    px = img.load()
    for y in range(0, h, 3):
        run = 0
        for x in range(w):
            if near(px[x, y], (248, 222, 222), 8):
                run += 1
                if run >= min_run:
                    return True
            else:
                run = 0
    return False

def geom_A(n_rows):
    W = 2519; HEADER, COLHEAD, FIRST_R, M = 58, 54, 548, 25
    H = max(1169, HEADER + COLHEAD + n_rows * 54)
    col_w = (W - M - FIRST_R) / 10.0
    row_h = (H - HEADER - COLHEAD) / n_rows
    return W, H, FIRST_R, col_w, HEADER + COLHEAD, row_h

def red_matrix_A(n_rows, img):
    W, H, first_r, col_w, top, row_h = geom_A(n_rows)
    px = img.load()
    m = []
    for i in range(n_rows):
        row = []
        for k in range(10):
            cx = first_r + (k + 0.5) * col_w
            cy = top + (i + 0.5) * row_h
            hit = 0; tot = 0
            for dx in range(-40, 41, 8):
                for dy in range(-18, 19, 6):
                    tot += 1
                    if near(px[int((cx + dx) * 2), int((cy + dy) * 2)], (248, 222, 222), 10):
                        hit += 1
            row.append(hit / tot >= 0.25)
        m.append(row)
    return m

def red_matrix_B(label_w, n_rows, img):
    px = img.load()
    m = []
    for i in range(n_rows):
        row = []
        for k in range(10):
            cx = label_w + k * 192 + 96
            cy = 60 + 52 + i * 44 + 22
            hit = 0; tot = 0
            for dx in range(-36, 37, 8):
                for dy in range(-14, 15, 6):
                    tot += 1
                    if near(px[int((cx + dx) * 2), int((cy + dy) * 2)], (248, 222, 222), 10):
                        hit += 1
            row.append(hit / tot >= 0.25)
        m.append(row)
    return m

def expect_matrix_pairs(csv_path):
    import gen_signoff_1118v1 as G
    data = G.read_pairs(csv_path)
    labels = [d[0] for d in data]
    m = [[c > 0 for c in cnt] for _lb, _d, _r, cnt in data]
    return labels, m

CH = ["lt_cbest", "lt_cworst", "lt_typ", "ml", "tt_cbest", "tt_cworst", "tt_typ", "wc_cbest", "wc_cworst", "wc_typ"]

def cmp_matrix(got, exp, tag, labels):
    diff = [(labels[i], CH[k]) for i in range(len(exp)) for k in range(10) if got[i][k] != exp[i][k]]
    print("  [%s] %s red-cell matrix %d/%d match %s" % ("PASS" if not diff else "FAIL", tag,
          sum(1 for i in range(len(exp)) for k in range(10) if got[i][k] == exp[i][k]), len(exp) * 10,
          "" if not diff else str(diff[:6])))
    return not diff

def main():
    ok = True
    def chk(cond, msg):
        nonlocal ok
        print("  [%s] %s" % ("PASS" if cond else "FAIL", msg))
        ok = ok and cond

    _ap = argparse.ArgumentParser()
    _ap.add_argument("--png", default=DEF_PNG, help="PNG 目录（默认 %%TEMP%%/signoff_1118v1_png）")
    args = _ap.parse_args()
    import gen_signoff_1118v1 as G

    for name in NAMES:
        svg = os.path.join(IMG_DIR, name + ".svg")
        png = os.path.join(args.png, name + ".png")
        w, h = svg_size(svg)
        img = Image.open(png).convert("RGB")
        print(name + ":")
        chk(img.size == (2 * w, 2 * h), "size %s == 2x viewBox %dx%d" % (img.size, w, h))
        px = img.load()
        chk(near(px[40, 40], BAND[name[:2]]), "title band %s @ (20,20)css" % (BAND[name[:2]],))
        W2, H2 = img.size
        row_uni = len({px[x, H2 - 4] for x in range(10, W2 - 10, 50)}) <= 2
        chk(row_uni, "bottom edge uniform (no clipped content)")

    img = Image.open(os.path.join(args.png, "51_signoff_setup_hk11.png")).convert("RGB")
    print("51 targeted:")
    labels, exp = expect_matrix_pairs(os.path.join(G.DATA, "report_setup.csv"))
    chk(cmp_matrix(red_matrix_A(len(labels), img), exp, "51 setup", labels), "51 matrix == csv expectation")
    chk(has_color(img, (26, 122, 60), 24), "zero-cell green text #1a7a3c present")

    img = Image.open(os.path.join(args.png, "52_signoff_hold_hk11.png")).convert("RGB")
    print("52 targeted:")
    labels, exp = expect_matrix_pairs(os.path.join(G.DATA, "report_hold.csv"))
    chk(cmp_matrix(red_matrix_A(len(labels), img), exp, "52 hold", labels), "52 matrix == csv expectation")
    if not any(any(r) for r in exp):
        chk(not has_red_fill(img), "hold all-zero gen: no red fill anywhere (run>=40px)")

    img = Image.open(os.path.join(args.png, "53_signoff_trans_hk11.png")).convert("RGB")
    print("53 targeted:")
    labels, exp = expect_matrix_pairs(os.path.join(G.DATA, "report_trans.csv"))
    chk(cmp_matrix(red_matrix_B(430, len(labels), img), exp, "53 trans", labels), "53 matrix == csv expectation")

    img = Image.open(os.path.join(args.png, "54_signoff_physkew_hk11.png")).convert("RGB")
    print("54 targeted:")
    chk(has_color(img, (211, 227, 246), 10), "hl blue cell #d3e3f6 present")
    chk(not has_red_fill(img), "no red fill in phy table (per 2M23, run>=40px)")

    img = Image.open(os.path.join(args.png, "55_signoff_sdskew_margin_hk11.png")).convert("RGB")
    print("55 targeted:")
    sd = G.read_sdskew(os.path.join(G.DATA, "report_sd_busskew.csv"))
    exp = [[not (lo <= v <= hi) for v in raw] for _lb, _d, raw, lo, hi in sd]
    labels = [d[0] for d in sd]
    chk(cmp_matrix(red_matrix_B(430, len(sd), img), exp, "55 sdskew", labels), "55 matrix == csv expectation")

    img = Image.open(os.path.join(args.png, "56_signoff_shift_window_hk11.png")).convert("RGB")
    print("56 targeted:")
    chk(has_color(img, (29, 78, 216), 22), "blue arrow #1d4ed8 present")
    chk(has_color(img, (185, 28, 28), 26), "red bound line #b91c1c present")
    chk(has_color(img, (14, 116, 144), 22), "teal data window #0e7490 present")

    print("ALL", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
# ymzhu 2026-11-18 15:34
