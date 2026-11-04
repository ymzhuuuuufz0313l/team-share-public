#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_buf_type_anim.py — IO 首/末级 buffer type 统计：动画 SVG 确定性生成器。

数据源（只读，零手工录入）:
  server-reports/input_port_first_buf_type.tsv   (PORT/FIRST_CELL_TYPE/FIRST_CELL_INSTANCE/STATUS)
  server-reports/output_port_last_buf_type.tsv   (PORT/LAST_CELL_TYPE/LAST_CELL_INSTANCE/STATUS)

聚合口径:
  input 子表  = FIRST_CELL_TYPE 计数 + STATUS 计数，标题含唯一端口数/总行数
  output 子表 = LAST_CELL_TYPE 计数 + STATUS 计数，标题含唯一端口数/总行数
若聚合结果与参考 PNG（38_buf_type.png）转录的数字不一致，按 TSV 实际值出图并打印 DIFF 报告。

输出:
  image/anim/38_buf_type.svg  —— 纯 CSS 动画（无 <script>），重建 38_buf_type.png 的版式与文字。
可重跑、幂等：同一输入必然产生字节相同的输出（无时间戳/随机数，排序全部显式化）。

动画（与任务规范一致）:
  ① 两栏依次 reveal：标题带 delay 0，input 栏 delay 0，output 栏 delay 0.3s；
     0.4s 淡入 + 4px 上滑，forwards 终态 = 静态图。
  ② 记录数单元格呼吸：opacity 1↔0.55，2.8s，按阅读顺序 0.35s 错峰（infinite）。
  ③ MULTI_LOAD(2) 整行呼吸（参考 PNG 该行无特殊底色 → 保持白底，仅整行 opacity 呼吸；
     该行的数字不重复挂呼吸，避免同元素双动画）。

六项校验（脚本末尾自动执行 1-5；6 幂等由外部二次运行 md5 比对完成）:
  1 XML 良构  2 无 <script>  3 @keyframes 且含 infinite  4 转录核对（<text> 多重集）
  5 结构计数（rev/br/数据行）
"""
import hashlib
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent  # 站点根（2026-11-04 自 script/ 迁入 image/tools/，层级+1）
IN_TSV = BASE / "server-reports" / "input_port_first_buf_type.tsv"
OUT_TSV = BASE / "server-reports" / "output_port_last_buf_type.tsv"
OUT_SVG = BASE / "image" / "anim" / "38_buf_type.svg"

# 参考 PNG 转录数字（仅用于 DIFF 报告，不作为数据来源）
EXPECTED = {
    "input":  {"types": {"APR_CDM": 52, "CLKBUFX8AS9": 52},
               "status": {"MULTI_LOAD(2)": 104}, "ports": 52, "rows": 104},
    "output": {"types": {"CLKBUFX8AS9": 476},
               "status": {"OK": 476}, "ports": 476, "rows": 476},
}

# ---------------- 版式常量（自 38_buf_type.png 实采样 + _gen_be_review_images.py 原始字体） ----------------
W, H = 1318, 364
C_FRAME, C_BAR, C_GRID = "#c0c6c6", "#0e7c6b", "#d0d8d6"
C_ZEBRA, C_INK = "#f4f8f7", "#212529"
C_SECT, C_BAR_RIGHT = "#0b5e52", "#cdebe5"
C_WHITE = "#ffffff"

# 原始 PNG 由 _gen_be_review_images.py（PIL，S=2）生成：
#   标题 = Consolas Bold 26 + YaHei Bold 26；副标题 = YaHei 20；
#   小节标题 = YaHei Bold 24（整串，含 ASCII）；绿表头 = Consolas Bold 22 + YaHei Bold 22；
#   数据 = Consolas 22 + YaHei 22。字体栈按此对齐（CJK 逐字回退 YaHei，与 draw_mixed 等价）。
FONT_MONO = "Consolas, 'Microsoft YaHei', monospace"
FONT_YAHEI = "'Microsoft YaHei', Consolas, monospace"

BAR_RECT = (2, 2, 1314, 58)            # 顶部深青绿标题带（x,y,w,h）
TITLE_X, TITLE_Y, TITLE_FS = 20, 32, 26
BARR_X, BARR_Y, BARR_FS = 1298, 40, 20
SEC_Y, SEC_FS = 106, 24                # 小节标题基线 / 字号（YaHei Bold）
COL_X = (20, 683)                      # 左右两栏子表框 x
BOX_W = 616
GREEN_H, ROW_H, ROW_H_SINGLE = 39, 39, 38   # 绿表头 39px；数据行 39px（单子表单行时 38px，与原始 PIL 渲染实测一致）
BORDER, GAP = 2, 15                   # 2px 细网格边框；子表间 15px 白隙
TABLE_Y0 = 128                         # 子表顶部（上边框）
LABEL_DX, NUM_DX = 8, 543              # 标签 / 记录数列 x 偏移（20+543=563，683+543=1226）
GREEN_BASE, ROW_BASE = 24, 22
GREEN_FS = 22
DATA_FS = 22

HEADER_TITLE = "IO 首/末级 buffer type 统计（SVT 换库后）"
HEADER_RIGHT = "report_input_last_buf.tcl / report_output_last_buf.tcl 输出"
IN_NAME, OUT_NAME = "input_port_first_buf_type.tsv", "output_port_last_buf_type.tsv"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def read_tsv(path: Path):
    """返回 (header, rows)。只读。"""
    with open(path, "r", encoding="utf-8") as f:
        lines = [ln.rstrip("\r\n") for ln in f]
    header = lines[0].split("\t")
    rows = [ln.split("\t") for ln in lines[1:] if ln != ""]
    return header, rows


def aggregate(rows, type_i, status_i, port_i=0):
    """确定性聚合：计数降序、同名按字典序（与参考 PNG 行序一致）。"""
    types = Counter(r[type_i] for r in rows)
    status = Counter(r[status_i] for r in rows)
    ports = len({r[port_i] for r in rows})
    return {
        "types": types,
        "type_order": sorted(types, key=lambda k: (-types[k], k)),
        "status": status,
        "status_order": sorted(status, key=lambda k: (-status[k], k)),
        "ports": ports,
        "rows": len(rows),
    }


def diff_report(name, agg):
    """聚合 vs 参考 PNG 转录数字，返回差异行列表（空 = 完全一致）。"""
    exp = EXPECTED[name]
    out = []
    for label, got, want in (
        ("cell 类型计数", dict(agg["types"]), exp["types"]),
        ("STATUS 计数", dict(agg["status"]), exp["status"]),
        ("唯一端口数", agg["ports"], exp["ports"]),
        ("数据行数", agg["rows"], exp["rows"]),
    ):
        if got != want:
            out.append(f"  [DIFF] {name} {label}: TSV={got}  PNG={want}")
    return out


def text(x, y, s, fs, fill, anchor="start", weight=None, cls="", font=FONT_MONO):
    c = f' class="{cls}"' if cls else ""
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    return (f'<text x="{x}" y="{y}" font-size="{fs}" fill="{fill}"'
            f' font-family="{font}"{w}{a}{c}>{esc(s)}</text>')


def subtable(x, y0, header, rows, br_map):
    """一个子表（2px 细网格边框 + 绿表头行 + 数据行）。
    rows: [(label, count_str)]；br_map: {行号0基: ("num"|"row", cls)}。
    'num'  = 仅记录数单元格呼吸；'row' = 整行呼吸（含背景+两列文本）。
    返回 (svg 片段, 框高)。
    """
    n = len(rows)
    row_h = ROW_H if n > 1 else ROW_H_SINGLE
    box_h = BORDER * 2 + GREEN_H + row_h * n
    p = []
    p.append(f'<rect x="{x + 1}" y="{y0 + 1}" width="{BOX_W - 2}" height="{box_h - 2}" '
             f'fill="none" stroke="{C_GRID}" stroke-width="2"/>')
    p.append(f'<rect x="{x + 2}" y="{y0 + 2}" width="{BOX_W - 4}" height="{GREEN_H}" fill="{C_BAR}"/>')
    p.append(text(x + LABEL_DX, y0 + 2 + GREEN_BASE, header, GREEN_FS, C_WHITE, weight="bold"))
    p.append(text(x + NUM_DX, y0 + 2 + GREEN_BASE, "记录数", GREEN_FS, C_WHITE, weight="bold"))
    for i, (label, cnt) in enumerate(rows):
        ry = y0 + 2 + GREEN_H + i * row_h
        fill = C_ZEBRA if i % 2 == 1 else C_WHITE
        label_t = text(x + LABEL_DX, ry + ROW_BASE, label, DATA_FS, C_INK)
        kind = br_map.get(i)
        if kind and kind[0] == "row":
            p.append(f'<g class="{kind[1]}">'
                     f'<rect x="{x + 2}" y="{ry}" width="{BOX_W - 4}" height="{row_h}" fill="{fill}"/>'
                     f'{label_t}{text(x + NUM_DX, ry + ROW_BASE, cnt, DATA_FS, C_INK)}</g>')
        else:
            num_cls = kind[1] if kind else ""
            p.append(f'<rect x="{x + 2}" y="{ry}" width="{BOX_W - 4}" height="{row_h}" fill="{fill}"/>')
            p.append(label_t)
            p.append(text(x + NUM_DX, ry + ROW_BASE, cnt, DATA_FS, C_INK, cls=num_cls))
    return "\n".join(p), box_h


def build_svg(in_agg, out_agg, plan):
    """plan: [((col, sub), row_i, kind, cls)] 呼吸计划（阅读顺序）。"""
    s = []
    s.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    s.append("<style>")
    s.append(".rev{opacity:0;animation:revIn 0.4s ease forwards;}")
    s.append(".d0{animation-delay:0s;}")
    s.append(".d3{animation-delay:0.3s;}")
    s.append("@keyframes revIn{from{opacity:0;transform:translateY(4px);}to{opacity:1;transform:none;}}")
    s.append(".br{animation:br 2.8s ease-in-out infinite;}")
    for i in range(len(plan)):
        s.append(f".b{i}{{animation-delay:{i * 0.35:.2f}s;}}")
    s.append("@keyframes br{0%,100%{opacity:1;}50%{opacity:0.55;}}")
    s.append("</style>")
    # 静态底：画布 + 四边 2px 外框（#c0c6c6，与 PNG 一致）
    s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="{C_WHITE}"/>')
    for (fx, fy, fw, fh) in ((0, 0, W, 2), (0, H - 2, W, 2), (0, 0, 2, H), (W - 2, 0, 2, H)):
        s.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" fill="{C_FRAME}"/>')
    # 标题带（reveal delay 0）
    s.append('<g class="rev d0">')
    bx, by, bw, bh = BAR_RECT
    s.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="{C_BAR}"/>')
    s.append(text(TITLE_X, TITLE_Y, HEADER_TITLE, TITLE_FS, C_WHITE, weight="bold"))
    s.append(text(BARR_X, BARR_Y, HEADER_RIGHT, BARR_FS, C_BAR_RIGHT, anchor="end",
                  font=FONT_YAHEI))
    s.append("</g>")

    # 两栏：input（d0）→ output（d3）
    cols = (
        (IN_NAME, in_agg, COL_X[0], "d0"),
        (OUT_NAME, out_agg, COL_X[1], "d3"),
    )
    for name, agg, x, dcls in cols:
        title = f"{name}（{agg['ports']} 端口 / {agg['rows']} 行）"
        s.append(f'<g class="rev {dcls}">')
        s.append(text(x, SEC_Y, title, SEC_FS, C_SECT, weight="bold", font=FONT_YAHEI))
        br_cell = {i: (k, c) for (col, sub), i, k, c in plan
                   if col == (0 if name == IN_NAME else 1) and sub == "cell"}
        br_stat = {i: (k, c) for (col, sub), i, k, c in plan
                   if col == (0 if name == IN_NAME else 1) and sub == "status"}
        y = TABLE_Y0
        frag, bh = subtable(x, y, "cell 类型",
                            [(t, str(agg["types"][t])) for t in agg["type_order"]], br_cell)
        s.append(frag)
        y += bh + GAP
        frag, bh = subtable(x, y, "STATUS",
                            [(t, str(agg["status"][t])) for t in agg["status_order"]], br_stat)
        s.append(frag)
        s.append("</g>")
    s.append("</svg>")
    return "\n".join(s)


def make_plan(in_agg, out_agg):
    """呼吸计划（阅读顺序）：左 cell 行数字 → 左 STATUS 行（MULTI_LOAD 整行/其余数字）
    → 右 cell 行数字 → 右 STATUS 行数字。返回 [( (col,sub), row_i, kind, cls )]。
    """
    plan = []
    for i, t in enumerate(in_agg["type_order"]):
        plan.append(((0, "cell"), i, "num"))
    for i, t in enumerate(in_agg["status_order"]):
        plan.append(((0, "status"), i, "row" if "MULTI_LOAD" in t else "num"))
    for i, t in enumerate(out_agg["type_order"]):
        plan.append(((1, "cell"), i, "num"))
    for i, t in enumerate(out_agg["status_order"]):
        plan.append(((1, "status"), i, "num"))
    return [((cs), i, k, f"br b{n}") for n, ((cs), i, k) in enumerate(plan)]


def localname(tag):
    return tag.split("}")[-1].lower() if isinstance(tag, str) else ""


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    _, in_rows = read_tsv(IN_TSV)
    _, out_rows = read_tsv(OUT_TSV)
    in_agg = aggregate(in_rows, type_i=1, status_i=3)
    out_agg = aggregate(out_rows, type_i=1, status_i=3)

    diffs = diff_report("input", in_agg) + diff_report("output", out_agg)
    if diffs:
        print("== 聚合 vs 参考 PNG：存在差异（按 TSV 实际值出图）==")
        print("\n".join(diffs))
    else:
        print("== 聚合 vs 参考 PNG：完全一致 ==")
        print(f"  input  : cell 类型 {dict(in_agg['types'])} | STATUS {dict(in_agg['status'])}"
              f" | {in_agg['ports']} 端口 / {in_agg['rows']} 行")
        print(f"  output : cell 类型 {dict(out_agg['types'])} | STATUS {dict(out_agg['status'])}"
              f" | {out_agg['ports']} 端口 / {out_agg['rows']} 行")

    plan = make_plan(in_agg, out_agg)
    svg = build_svg(in_agg, out_agg, plan)

    OUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUT_SVG.write_text(svg, encoding="utf-8", newline="\n")
    md5 = hashlib.md5(OUT_SVG.read_bytes()).hexdigest()
    print(f"输出: {OUT_SVG}")
    print(f"md5 : {md5}")

    # ---------------- 校验 1-5（6 幂等由外部二次运行 md5 比对） ----------------
    ok = True
    raw = OUT_SVG.read_text(encoding="utf-8")

    # 1 XML 良构
    root = None
    try:
        root = ET.fromstring(raw)
        print("校验1 XML 良构         : PASS")
    except ET.ParseError as e:
        ok = False
        print(f"校验1 XML 良构         : FAIL ({e})")

    # 2 无 <script>
    has_script = raw.count("<script") > 0
    if root is not None:
        has_script = has_script or any(
            localname(e.tag) == "script" for e in root.iter())
    print(f"校验2 无 <script>       : {'FAIL' if has_script else 'PASS'}")
    ok = ok and not has_script

    # 3 @keyframes 且含 infinite
    kf = "@keyframes" in raw and "infinite" in raw
    print(f"校验3 keyframes+infinite : {'PASS' if kf else 'FAIL'}")
    ok = ok and kf

    # 4 转录核对：<text> 多重集 == 数据驱动期望
    if root is not None:
        texts = [(e.text or "") for e in root.iter() if localname(e.tag) == "text"]
        expected = [
            HEADER_TITLE, HEADER_RIGHT,
            f"{IN_NAME}（{in_agg['ports']} 端口 / {in_agg['rows']} 行）",
            f"{OUT_NAME}（{out_agg['ports']} 端口 / {out_agg['rows']} 行）",
            "cell 类型", "cell 类型", "STATUS", "STATUS",
            "记录数", "记录数", "记录数", "记录数",
        ]
        for t in in_agg["type_order"]:
            expected += [t, str(in_agg["types"][t])]
        for t in in_agg["status_order"]:
            expected += [t, str(in_agg["status"][t])]
        for t in out_agg["type_order"]:
            expected += [t, str(out_agg["types"][t])]
        for t in out_agg["status_order"]:
            expected += [t, str(out_agg["status"][t])]
        same = Counter(texts) == Counter(expected)
        if same:
            print(f"校验4 转录核对         : PASS ({len(texts)} 个 <text> 与 PNG 转录多重集一致)")
        else:
            print(f"校验4 转录核对         : FAIL (缺 {dict(Counter(expected) - Counter(texts))}"
                  f" 多 {dict(Counter(texts) - Counter(expected))})")
        ok = ok and same

    # 5 结构计数
    n_rev = raw.count('class="rev')
    n_br = raw.count('class="br ')
    n_rows = (len(in_agg["type_order"]) + len(in_agg["status_order"])
              + len(out_agg["type_order"]) + len(out_agg["status_order"]))
    p5 = (n_rev == 3 and n_br == len(plan) and n_rows == 5)
    print(f"校验5 结构计数         : {'PASS' if p5 else 'FAIL'} "
          f"(rev={n_rev}/3, br={n_br}/{len(plan)}, 数据行={n_rows}/5)")
    ok = ok and p5

    print("校验6 幂等             : 外部二次运行 md5 比对（见运行日志）")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-04 15:54
