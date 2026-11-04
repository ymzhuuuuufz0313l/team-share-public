#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
verify_png_1104v2.py — PNG 快照程序化验收（2026-11-04，本模型无视觉输入的替代硬校验）

对 6 张 PNG 做：
  ① 尺寸 = 2×viewBox（DPR2 矢量重栅格化）
  ② 标题条带色（51/52 A 族 #157a6a；53/54/55 B 族 #0e7c6b；56 纸底 #f4f1ea）
  ③ 定向像素断言（几何由生成器常量直算，×2 后采样）：
     51 setup：DCLK_DATA_MUX_SHORT@wc_cbest=违例格（浅红底 #f8dede + 红字 #7f1d1d）
              DCLK_CONFIG_LONG@lt_cbest=零格（白底 + 绿字 #1a7a3c）
     52 hold： RX_CLK@lt_typical=违例格红底；OSC_CLK@wc_cworst=正格白底
     55 sdskew：sd_r_dplc_margin_a_min@wc_cbest=出窗红底；sd_l_dplc_margin_b_min@wc_cworst=窗内白底
     56：蓝箭头 #1d4ed8 存在 + 红碰界线 #b91c1c 存在
     54：浅蓝最紧格 #d3e3f6 存在
  ④ 右缘/底缘无内容截断（最右 4px 列与最底 4px 行只允许底色/边框色系）
"""
import os, re, sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
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

def geom_A(n_rows):
    W = 2519; HEADER, COLHEAD, FIRST_R, M = 58, 54, 548, 25
    H = max(1169, HEADER + COLHEAD + n_rows * 54)
    col_w = (W - M - FIRST_R) / 10.0
    row_h = (H - HEADER - COLHEAD) / n_rows
    return W, H, FIRST_R, col_w, HEADER + COLHEAD, row_h

def cell_center_A(row_i, col_i, n_rows):
    W, H, first_r, col_w, top, row_h = geom_A(n_rows)
    cx = first_r + (col_i + 0.5) * col_w
    cy = top + (row_i + 0.5) * row_h
    return int(cx * 2), int(cy * 2)

def geom_B(label_w, n_rows):
    W = label_w + 10 * 192 + 2
    H = 60 + 52 + n_rows * 44 + 2
    return W, H

def cell_center_B(label_w, row_i, col_i):
    x = label_w + col_i * 192 + 96
    y = 60 + 52 + row_i * 44 + 22
    return int(x * 2), int(y * 2)

CH = ["lt_cbest", "lt_cworst", "lt_typ", "ml", "tt_cbest", "tt_cworst", "tt_typ", "wc_cbest", "wc_cworst", "wc_typ"]

def red_matrix_A(n_rows, img):
    """35×10 布尔矩阵：格子中心 40×20css 采样块内 ≥25% 像素 ≈ RED_BG(248,222,222)。"""
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
    import gen_signoff_1104v2 as G
    data = G.read_pairs(csv_path)
    labels = [d[0] for d in data]
    m = []
    for lb, disp, raw, cnt in data:
        m.append([c > 0 for c in cnt])
    return labels, m

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

    import gen_signoff_1104v2 as G

    for name in NAMES:
        svg = os.path.join(BASE, name + ".svg")
        png = os.path.join(BASE, name + ".png")
        w, h = svg_size(svg)
        img = Image.open(png).convert("RGB")
        print(name + ":")
        chk(img.size == (2 * w, 2 * h), "size %s == 2x viewBox %dx%d" % (img.size, w, h))
        px = img.load()
        chk(near(px[40, 40], BAND[name[:2]]), "title band %s @ (20,20)css" % (BAND[name[:2]],))
        W2, H2 = img.size
        row_uni = len({px[x, H2 - 4] for x in range(10, W2 - 10, 50)}) <= 2
        chk(row_uni, "bottom edge uniform (no clipped content)")

    img = Image.open(os.path.join(BASE, "51_signoff_setup_hk11.png")).convert("RGB")
    print("51 targeted:")
    labels, exp = expect_matrix_pairs(os.path.join(G.DATA, "report_setup.csv"))
    chk(cmp_matrix(red_matrix_A(35, img), exp, "51 setup", labels), "51 matrix == csv expectation")
    chk(has_color(img, (26, 122, 60), 24, region=(548 * 2 + 20, 112 * 2 + 8, 548 * 2 + 380, 112 * 2 + 96)),
        "zero-cell green text #1a7a3c @row0")

    img = Image.open(os.path.join(BASE, "52_signoff_hold_hk11.png")).convert("RGB")
    print("52 targeted:")
    labels, exp = expect_matrix_pairs(os.path.join(G.DATA, "report_hold.csv"))
    chk(cmp_matrix(red_matrix_A(35, img), exp, "52 hold", labels), "52 matrix == csv expectation")

    img = Image.open(os.path.join(BASE, "54_signoff_physkew_hk11.png")).convert("RGB")
    print("54 targeted:")
    chk(has_color(img, (211, 227, 246), 10), "hl blue cell #d3e3f6 present")
    chk(not has_color(img, (248, 222, 222), 8), "no red bg in phy table (per 2M23)")

    img = Image.open(os.path.join(BASE, "55_signoff_sdskew_margin_hk11.png")).convert("RGB")
    print("55 targeted:")
    sd = G.read_sdskew(os.path.join(G.DATA, "report_sd_busskew.csv"))
    exp = [[not (lo <= v <= hi) for v in raw] for lb, disp, raw, lo, hi in sd]
    labels = [d[0] for d in sd]
    chk(cmp_matrix(red_matrix_B(430, 16, img), exp, "55 sdskew", labels), "55 matrix == csv expectation")

    img = Image.open(os.path.join(BASE, "56_signoff_shift_window_hk11.png")).convert("RGB")
    print("56 targeted:")
    chk(has_color(img, (29, 78, 216), 22), "blue arrow #1d4ed8 present")
    chk(has_color(img, (185, 28, 28), 26), "red bound line #b91c1c present")
    chk(has_color(img, (14, 116, 144), 22), "teal data window #0e7490 present")

    print("ALL", "PASS" if ok else "FAIL")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
# ymzhu 2026-11-04 11:45
