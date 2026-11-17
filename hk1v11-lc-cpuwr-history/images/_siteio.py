# -*- coding: utf-8 -*-
"""hk1v11-lc-cpuwr-history 站点生成脚本的统一输出层（2026-11-17 新增）。

解决的问题（对应审查 finding F04 / F12 / F21）：
- F04：原来 9 个生成脚本把 `E:\\project\\team-share-public\\...` 绝对路径写死，
  在任意目录运行都会改写线上站点文件；本模块把输出根目录改为「默认站点根 + --out 覆盖」。
- F04b：原来部分脚本用 Path.write_text 在 Windows 下默认写 CRLF，导致工作树被换行符污染；
  本模块 write_text_lf() 统一 newline="\\n"。
- F21：原来归档靠人工 cp，skew/全景图反复漏归档；本模块 archive_snapshot() 提供生成期自动归档。
- F12：5 张表格型动画图只有入场动画、无机 Kit v4 稳态族；本模块 table_anim() 统一注入
  Kit v4 全套 CSS + sweepband（扫光）+ cellwave（行波）两族稳态，且**不触碰任何 <text> 内容**。

用法（各生成脚本内）：
    import sys; from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
    from _siteio import out_path, write_text_lf, archive_snapshot, table_anim
    p = out_path("images/xxx.svg")        # 默认 SITE/images/xxx.svg；--out DIR 时落到 DIR/xxx.svg
    write_text_lf(p, svg)
命令行可用 `--out <目录>` 预演到临时目录（此时不写 archive）。
"""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

IMAGES = Path(__file__).resolve().parent          # images/
SITE_ROOT = IMAGES.parent                         # 站点根


# ---------------------------------------------------------------- 输出路径
def _argv_out():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--out", default=None,
                    help="输出根目录（默认=站点根）；给定时所有产物落到该目录下（同名文件）")
    ns, _ = ap.parse_known_args()
    return ns.out or os.environ.get("CPUWR_OUT_DIR")


def out_root():
    o = _argv_out()
    return Path(o).resolve() if o else SITE_ROOT


def is_dry_run():
    return out_root() != SITE_ROOT


def out_path(rel):
    """rel 相对站点根（如 images/a.svg、checksum.html）。

    默认落到 SITE_ROOT/rel；--out DIR 时落到 DIR/rel（**保留子目录结构**，
    这样 images/x.svg 与 images/anim/x.svg 不会互相覆盖，便于整站预演 + 逐文件比对）。
    """
    rel = Path(rel)
    p = out_root() / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def read_text_lf(p):
    """读文本并强制 LF：源 SVG 若是 CRLF（历史遗留），不把 \\r 传染给产物。"""
    return Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def write_text_lf(p, text):
    """唯一写盘入口：UTF-8 + LF（不产生 CRLF）。"""
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


# ---------------------------------------------------------------- 自动归档
def archive_snapshot(rel, tag, date=None):
    """把「当前（即将被替换的）版本」快照到 images/archive/<YYYYMMDD>/<stem>_<tag><suffix>。

    - 幂等：目标已存在且内容相同则跳过；
    - --out 预演模式不写归档（不污染仓库）；
    - 命名沿用站点既有惯例 `<图名>_<代际>rN`，tag 由调用方给（如 "1106v4r0"）。
    """
    if is_dry_run():
        return None
    src = SITE_ROOT / rel
    if not src.exists():
        return None
    date = date or datetime.date.today().strftime("%Y%m%d")
    # 动画版与静态版同主名，归档名沿用站内既有惯例加 anim_ 前缀，避免互相覆盖
    prefix = "anim_" if src.parent.name == "anim" else ""
    dst = IMAGES / "archive" / date / f"{prefix}{src.stem}_{tag}{src.suffix}"
    if dst.exists():
        if dst.read_bytes() == src.read_bytes():
            return dst
        # 2026-11-17 加固（审查 R1 返工时实测）：旧版这里直接 shutil.copy2 覆盖，
        # 生成器**重跑一次**就会把「即将被替换的旧版本」快照换成当前版本 —— 归档静默丢历史。
        # 现改为：绝不覆盖既有快照，改用内容指纹后缀（同内容幂等复用）。
        digest = hashlib.md5(src.read_bytes()).hexdigest()[:8]
        dst = dst.with_name(f"{prefix}{src.stem}_{tag}_{digest}{src.suffix}")
        if dst.exists() and dst.read_bytes() == src.read_bytes():
            return dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


# ---------------------------------------------------------------- Kit v4 CSS
# 从已 PASS 的 checksum_address_map.svg 抽取的 canonical 片段（§2 逐字），新增 .title 别名。
KIT_CSS = """.row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
.title{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}
.pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}
@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}
.pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}
@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}
.sweepband{opacity:.85;animation:sweepMove 8s linear infinite}
@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}
.dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}
@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}
.march{animation:march 1.5s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.cellwave{animation:wave 2.6s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.title{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}"""

ROW_RECT_RE = re.compile(r'<rect x="40" y="(\d+)" width="1020" height="(\d+)" fill="#(?:ffffff|f8fafc)"')


def table_anim(svg, title_anchor='font-size="22" font-weight="bold" fill="#1e293b"'):
    """把表格型静态 SVG 变成 Kit v4 合规动画版。

    - 入场：标题 .title / 表头 .head / 数据行 .row（0.12s 递进）
    - 稳态族 1：sweepband 扫光（覆盖表体区域，置于内容之下）
    - 稳态族 2：cellwave 行波（包裹第 2..n-1 行行组，0.4s 错相位）
    - **不新增/删除/修改任何 <text> 节点**（A2 双版文本一致由调用方 assert）
    """
    out = svg

    # 1) 标题入场
    if title_anchor in out:
        out = out.replace(title_anchor, 'class="title" ' + title_anchor, 1)

    # 2) 数据行 rect → class="row" + 递进 delay
    rows = list(ROW_RECT_RE.finditer(out))
    for i, m in enumerate(rows):
        tag = m.group(0)
        new = tag.replace('<rect ', '<rect class="row" style="animation-delay:%.2fs" ' % (0.15 + i * 0.12), 1)
        out = out.replace(tag, new, 1)

    # 3) 表头 rect → class="head"
    head = '<rect x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>'
    if head in out:
        out = out.replace(head, '<rect class="head" x="40" y="100" width="1020" height="34" fill="#f1f5f9"/>', 1)

    # 4) 扫光带（region = 表体，从表头顶到末行底）
    if rows:
        rx, ry, rw = 40, 100, 1020
        rh = (int(rows[-1].group(1)) + int(rows[-1].group(2))) - ry
        P = rw + 240
        X0 = rx - int(0.54 * P)
        defs = (
            '<defs>'
            '<linearGradient id="sweepG-1" gradientUnits="userSpaceOnUse" x1="%d" y1="0" x2="%d" y2="0">'
            '<stop offset="0" stop-color="#b45309" stop-opacity="0"/>'
            '<stop offset="0.46" stop-color="#b45309" stop-opacity="0"/>'
            '<stop offset="0.5" stop-color="#b45309" stop-opacity="0.30"/>'
            '<stop offset="0.54" stop-color="#b45309" stop-opacity="0"/>'
            '<stop offset="1" stop-color="#b45309" stop-opacity="0"/>'
            '</linearGradient>'
            '<clipPath id="sweepC-1"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath>'
            '</defs>'
            '<g clip-path="url(#sweepC-1)"><rect class="sweepband" x="%d" y="%d" width="%d" height="%d" '
            'fill="url(#sweepG-1)" style="--sweepP:%dpx"/></g>'
        ) % (X0, X0 + P, rx, ry, rw, rh, X0, ry, P, rh, P)
        anchor = '<rect class="head" x="40" y="100"'
        if anchor in out:
            out = out.replace(anchor, defs + anchor, 1)
        else:
            out = out.replace("</svg>", defs + "</svg>", 1)

    # 5) 行波：包裹第 2..n-1 行行组（避开首行与末行，末行后接底注不便定界）
    starts = [m.start() for m in re.finditer(r'<rect class="row"', out)]
    if len(starts) >= 3:
        for k in range(len(starts) - 2, 0, -1):
            s, e = starts[k], starts[k + 1]
            out = (out[:s] + '<g class="cellwave" style="animation-delay:%.1fs">' % (-(k * 0.4))
                   + out[s:e] + '</g>' + out[e:])

    # 6) CSS
    out = out.replace("</svg>", "<style>\n" + KIT_CSS + "\n</style>\n</svg>", 1)
    return out

# ymzhu 2026-11-17 20:28
