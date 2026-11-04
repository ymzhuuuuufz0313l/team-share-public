#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
gen_postpt_skew_tables_anim.py
==============================
把 postPT trans / physkew / sdskew-margin 六张 PNG 表重建成**动画 SVG**（数据直接读 CSV，零手工录入）。

规范（fireworks-tech-graph skill, "## Animated SVG"）：
  - 纯 CSS（无 <script>、无外部资源），@keyframes + animation，<img> 嵌入即可播放
  - 零数据变更：每个数值单元格逐字来自源 CSV，严禁编造
  - 终态 = 静态表格（reveal 用 forwards；infinite 特效只动 opacity / stroke-opacity）
  - 至少一个常驻 infinite 特效（规则 5）
  - 确定性生成器：幂等，连跑两遍 md5 一致

动画（模型决策已定）：
  ① 行 reveal：每数据行 <g class="row"> 错开 0.025s（sdskew 0.02s），0.4s 淡入 + 4px 上滑；
     标题带 + 列头行 <g class="head">（delay 0）
  ② 呼吸（常驻）：非零单元格 infinite opacity 1↔0.55，2.8s，逐格错开 delay；零值绿格保持静态
  ③ trans 表全零（无呼吸对象）→ 外框 border breathing（stroke-opacity 1↔0.45，2.8s）满足规则 5
  不加扫光/流向。

用法：
  python gen_postpt_skew_tables_anim.py --all
  python gen_postpt_skew_tables_anim.py --metric trans|physkew|sdskew --mode 2P|1P

内置六项校验（每次生成自动执行并打印）：
  ① XML 良构  ② 无 <script>  ③ @keyframes 存在
  ④ 转录核对：从生成 SVG 提取全部数值/标签单元格，与源 CSV 逐值逐数比对（数量与值全等）
  ⑤ 行数 = 源数据行数  ⑥ 幂等：同一输入连生成两遍，输出 md5 一致
"""
import argparse
import csv
import hashlib
import os
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 站点根（2026-11-04 自 script/ 迁入 image/tools/，层级+1）
DATA_DIR = os.path.join(ROOT, "server-reports", "postpt_summary")
OUT_DIR = os.path.join(ROOT, "image", "anim")

# ---------------------------------------------------------------- 常量（全部取自参考 PNG 采样）
# 颜色（PIL 采样自 30/31/33 号参考 PNG）
BAND   = "#0e7c6b"   # 标题带 + 列头行（深青绿）
ZEBRA  = "#f4f8f7"   # 斑马行浅绿灰
GRID   = "#d0d8d6"   # 内部细网格
BORDER = "#c0c6c6"   # 外框 2px
GREEN  = "#1e8449"   # 零值绿
DARK   = "#212529"   # 非零深灰黑 / 标签
WHITE  = "#ffffff"
FONT   = "Consolas, 'Cascadia Mono', 'Courier New', monospace"

TITLE_H, HEADER_H, ROW_H = 60, 52, 44          # 参考 PNG 实测
COL_W = 192                                      # 参考 PNG 实测值列宽（10 列）
FS_TITLE, FS_HDR, FS_TXT = 26, 20, 20
PAD_L, PAD_R = 12, 14                            # 标签左距 / 数值右距

CORNER_HDR = ["lt_cbest_m40", "lt_cworst_m40", "lt_typical_m40", "ml_cbest_125",
              "tt_cbest_25", "tt_cworst_25", "tt_typical_25", "wc_cbest_125",
              "wc_cworst_125", "wc_typical_125"]

REVEAL_STEP = {"trans": 0.025, "physkew": 0.025, "sdskew": 0.02}


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


# ---------------------------------------------------------------- 数据装载（只读，绝不改源文件）
def load_trans(csv_path):
    """trans：CSV 前两行 header；每行 = metric + 10×(violation number, biggest violation)。
    参考 PNG 每 corner 只展示 biggest violation 一个值 → 返回 (labels, values) 各 4×10。"""
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    labels, values = [], []
    for r in rows[2:]:
        labels.append("%s (biggest violation)" % r[0])
        values.append([r[2 + 2 * k] for k in range(10)])   # biggest violation 列
    return labels, values, 4


def load_physkew(csv_path):
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    labels, values = [], []
    for r in rows[1:]:
        labels.append(r[0])
        values.append(r[1:11])
    return labels, values, len(rows) - 1


def load_sdskew(csv_path):
    """sdskew-margin：只取 CSV 中的 margin 段（label 含 '_margin_'，共 24 行），
    label 去掉 ' : [-1:6] ' 后缀（规格已写入副标题），与参考 PNG 一致。"""
    with open(csv_path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    labels, values = [], []
    for r in rows[1:]:
        if not r or "_margin_" not in r[0]:
            continue
        labels.append(r[0].split(" : ")[0].strip())
        values.append(r[1:11])
    return labels, values, len(labels)


# ---------------------------------------------------------------- 表规格
TABLES = {
    ("trans", "2P"): dict(out="30_postpt_trans_2p.svg",
                          csv=os.path.join(DATA_DIR, "POST_PT_2P", "report_trans.csv"),
                          load=load_trans, W=2350, label_w=430,
                          first_hdr="metric",
                          title="report_trans.csv (2P)",
                          subtitle="max_trans/cap 约束违例总表", zero_frame=True),
    ("trans", "1P"): dict(out="30_postpt_trans_1p.svg",
                          csv=os.path.join(DATA_DIR, "POST_PT_1P", "report_trans.csv"),
                          load=load_trans, W=2350, label_w=430,
                          first_hdr="metric",
                          title="report_trans.csv (1P)",
                          subtitle="max_trans/cap 约束违例总表", zero_frame=True),
    ("physkew", "2P"): dict(out="30_postpt_physkew_2p.svg",
                            csv=os.path.join(DATA_DIR, "POST_PT_2P", "report_phy_busskew.csv"),
                            load=load_physkew, W=2337, label_w=417,
                            first_hdr="report_files",
                            title="report_phy_busskew.csv (2P)",
                            subtitle="PHY bus skew 各组 slack (ns)"),
    ("physkew", "1P"): dict(out="30_postpt_physkew_1p.svg",
                            csv=os.path.join(DATA_DIR, "POST_PT_1P", "report_phy_busskew.csv"),
                            load=load_physkew, W=2337, label_w=417,
                            first_hdr="report_files",
                            title="report_phy_busskew.csv (1P)",
                            subtitle="PHY bus skew 各组 slack (ns)"),
    ("sdskew", "2P"): dict(out="33_postpt_sdskew_margin_2p.svg",
                           csv=os.path.join(DATA_DIR, "POST_PT_2P", "report_sd_busskew.csv"),
                           load=load_sdskew, W=2241, label_w=321,
                           first_hdr="report_files",
                           title="report_sd_busskew.csv (2P)",
                           subtitle="SD skew margin, 规格 [-1, +6] ns"),
    ("sdskew", "1P"): dict(out="34_postpt_sdskew_margin_1p.svg",
                           csv=os.path.join(DATA_DIR, "POST_PT_1P", "report_sd_busskew.csv"),
                           load=load_sdskew, W=2241, label_w=321,
                           first_hdr="report_files",
                           title="report_sd_busskew.csv (1P)",
                           subtitle="SD skew margin, 规格 [-1, +6] ns"),
}

CSS = """<style>
.head { opacity:0; animation: rowIn 0.4s ease forwards; }
.row  { opacity:0; animation: rowIn 0.4s ease forwards; }
@keyframes rowIn { from { opacity:0; transform: translateY(4px); }
                   to   { opacity:1; transform: none; } }
.breath { animation: breathe 2.8s ease-in-out infinite; }
@keyframes breathe { 0%,100% { opacity:1; } 50% { opacity:0.55; } }
.frameBreath { animation: frameB 2.8s ease-in-out infinite; }
@keyframes frameB { 0%,100% { stroke-opacity:1; } 50% { stroke-opacity:0.45; } }
</style>"""


def is_zero(v: str) -> bool:
    return float(v.strip()) == 0.0


# ---------------------------------------------------------------- SVG 生成（纯函数：同输入 → 同字符串）
def build_svg(spec: dict) -> str:
    labels, values, n_rows = spec["load"](spec["csv"])
    W, label_w = spec["W"], spec["label_w"]
    H = TITLE_H + HEADER_H + n_rows * ROW_H + 2
    step = REVEAL_STEP[spec["metric"]]
    col_x = [label_w + k * COL_W for k in range(11)]   # 11 条纵向边界
    y_head, y0 = TITLE_H, TITLE_H + HEADER_H

    p = []
    p.append('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
             'viewBox="0 0 %d %d" font-family="%s">' % (W, H, W, H, esc(FONT)))
    p.append(CSS)

    # ---- head：标题带 + 列头行（delay 0）
    p.append('<g class="head">')
    p.append('<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (W, TITLE_H, BAND))
    p.append('<text x="16" y="38.5" font-size="%d" font-weight="bold" fill="%s">%s</text>'
             % (FS_TITLE, WHITE, esc(spec["title"])))
    p.append('<text x="%d" y="36.5" font-size="%d" fill="%s" text-anchor="end">%s</text>'
             % (W - 16, 20, WHITE, esc(spec["subtitle"])))
    p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (y_head, W, HEADER_H, BAND))
    p.append('<text x="%d" y="%d" font-size="%d" font-weight="bold" fill="%s">%s</text>'
             % (PAD_L, y_head + 32.5, FS_HDR, WHITE, esc(spec["first_hdr"])))
    for k in range(10):
        cx = (col_x[k] + col_x[k + 1]) / 2.0
        p.append('<text x="%s" y="%d" font-size="%d" font-weight="bold" fill="%s" '
                 'text-anchor="middle">%s</text>' % (("%d" % int(cx)) if cx == int(cx) else "%g" % cx,
                                                      y_head + 32.5, FS_HDR, WHITE,
                                                      esc(CORNER_HDR[k])))
    p.append('</g>')

    # ---- 数据行（逐行 reveal）
    for i in range(n_rows):
        ry = y0 + i * ROW_H
        delay = (i + 1) * step
        fill = WHITE if i % 2 == 0 else ZEBRA
        p.append('<g class="row" style="animation-delay:%.3fs">' % delay)
        p.append('<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (ry, W, ROW_H, fill))
        p.append('<text class="lab" x="%d" y="%d" font-size="%d" fill="%s">%s</text>'
                 % (PAD_L, ry + 28.5, FS_TXT, DARK, esc(labels[i])))
        for k in range(10):
            v = values[i][k]
            if is_zero(v):
                cls_attr = ' class="val"'
                color = GREEN
            else:
                cls_attr = ' class="val breath" style="animation-delay:%.2fs"' % ((i + k) * 0.15)
                color = DARK
            p.append('<text%s x="%d" y="%d" font-size="%d" fill="%s" '
                     'text-anchor="end">%s</text>' % (cls_attr, col_x[k + 1] - PAD_R, ry + 28.5,
                                                      FS_TXT, color, esc(v)))
        p.append('</g>')

    # ---- 网格（静态）
    for k in range(1, 11):
        p.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (col_x[k], y_head, col_x[k], H - 2, GRID))
    for i in range(n_rows):
        p.append('<line x1="1" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1"/>'
                 % (y0 + i * ROW_H, W - 1, y0 + i * ROW_H, GRID))

    # ---- 外框（trans 全零表 → 框呼吸满足规则 5；其余静态）
    frame_cls = ' class="frameBreath"' if spec.get("zero_frame") else ""
    p.append('<rect%s x="1" y="1" width="%d" height="%d" fill="none" stroke="%s" stroke-width="2"/>'
             % (frame_cls, W - 2, H - 2, BORDER))
    p.append('</svg>')
    return "\n".join(p)


# ---------------------------------------------------------------- 校验
def validate(spec: dict, svg: str, path: str) -> dict:
    ok = {}
    # ① XML 良构
    try:
        ET.parse(path)
        ok["xml"] = True
    except ET.ParseError as e:
        ok["xml"] = False
        ok["xml_err"] = str(e)
    # ② 无 <script>
    ok["no_script"] = ("<script" not in svg.lower())
    # ③ @keyframes 存在
    ok["keyframes"] = svg.count("@keyframes")
    # ④ 转录核对（数值 + 标签，逐值逐数、顺序全等）
    root = ET.parse(path).getroot()
    got_vals, got_labs = [], []
    for t in root.iter():
        if not t.tag.endswith("text"):
            continue
        cls = (t.get("class") or "").split()
        if "val" in cls:
            got_vals.append(t.text)
        elif "lab" in cls:
            got_labs.append(t.text)
    labels, values, n_rows = spec["load"](spec["csv"])
    exp_vals = [v for row in values for v in row]
    ok["transcript_vals"] = (got_vals == exp_vals)
    ok["transcript_labs"] = (got_labs == labels)
    ok["n_vals"] = len(got_vals)
    ok["n_vals_exp"] = len(exp_vals)
    if not ok["transcript_vals"]:
        for j, (a, b) in enumerate(zip(got_vals, exp_vals)):
            if a != b:
                ok["val_mismatch_at"] = (j, a, b)
                break
    # ⑤ 行数 = 源数据行数
    n_row_groups = sum(1 for g in root.iter()
                       if g.tag.endswith("g") and (g.get("class") or "") == "row")
    ok["row_count"] = n_row_groups == n_rows
    ok["n_rows"] = n_row_groups
    ok["n_rows_exp"] = n_rows
    ok["n_labs"] = len(got_labs)
    # 常驻 infinite 特效存在（规则 5）
    ok["infinite"] = ("infinite" in svg)
    return ok


def run_one(metric: str, mode: str) -> dict:
    spec = dict(TABLES[(metric, mode)])
    spec["metric"] = metric
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, spec["out"])

    s1, s2 = build_svg(spec), build_svg(spec)          # ⑥ 幂等：同输入两遍
    md5a, md5b = hashlib.md5(s1.encode("utf-8")).hexdigest(), hashlib.md5(s2.encode("utf-8")).hexdigest()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s1)
    md5c = hashlib.md5(open(path, "rb").read()).hexdigest()
    ok = validate(spec, s1, path)
    ok["md5"] = md5a
    ok["idempotent"] = (md5a == md5b == md5c)
    ok["path"] = path
    return ok


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--metric", choices=["trans", "physkew", "sdskew"])
    ap.add_argument("--mode", choices=["2P", "1P"])
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    keys = list(TABLES) if args.all else [(args.metric, args.mode)]
    if not args.all and (not args.metric or not args.mode):
        ap.error("需要 --metric 和 --mode（或 --all）")

    allpass = True
    for k in keys:
        r = run_one(*k)
        res = (r["xml"] and r["no_script"] and r["keyframes"] >= 1
               and r["transcript_vals"] and r["transcript_labs"]
               and r["row_count"] and r["infinite"] and r["idempotent"])
        allpass &= res
        print("=" * 72)
        print("[%s %s] %s" % (k[0], k[1], os.path.relpath(r["path"], ROOT)))
        print("  ① XML 良构        : %s" % ("PASS" if r["xml"] else "FAIL %s" % r.get("xml_err")))
        print("  ② 无 <script>     : %s" % ("PASS" if r["no_script"] else "FAIL"))
        print("  ③ @keyframes      : %s (n=%d)" % ("PASS" if r["keyframes"] >= 1 else "FAIL", r["keyframes"]))
        print("  ④ 转录核对        : %s  (vals %d/%d 全等, 标签 %d/%d 全等)"
              % ("PASS" if r["transcript_vals"] and r["transcript_labs"] else "FAIL",
                 r["n_vals"], r["n_vals_exp"], r["n_labs"], r["n_rows_exp"]))
        if not r["transcript_vals"]:
            print("     首个不一致: %s" % r.get("val_mismatch_at"))
        print("  ⑤ 行数=源数据行数 : %s  (row 组 %d/%d)" % ("PASS" if r["row_count"] else "FAIL",
                                                         r["n_rows"], r["n_rows_exp"]))
        print("  ⑥ 幂等 md5       : %s  (%s)" % ("PASS" if r["idempotent"] else "FAIL", r["md5"]))
        print("  规则5 infinite   : %s" % ("PASS" if r["infinite"] else "FAIL"))
        print("  => %s" % ("ALL PASS" if res else "FAILED"))
    print("=" * 72)
    print("SUMMARY: %s" % ("ALL PASS (6/6)" if args.all and allpass else
                           ("PASS" if allpass else "FAILED")))
    sys.exit(0 if allpass else 1)


if __name__ == "__main__":
    main()

# ymzhu 2026-11-04 15:54
