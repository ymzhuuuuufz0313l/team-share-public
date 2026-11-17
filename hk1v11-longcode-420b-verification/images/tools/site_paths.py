# -*- coding: utf-8 -*-
"""站点路径与写文件 helper —— 供 images/tools/make_anim_*.py 统一使用。

解决两个历史缺陷（2026-11-17 修复）：
  1. 生成器把站点根写成绝对路径 `E:\\project\\team-share-public\\...`，
     导致「在任何目录运行都会改写线上文件」——审查期间已实际误写一次。
     现在按优先级解析：--out <dir> > 环境变量 SITE_ROOT > 脚本位置推导。
  2. 输出换行由源文件 EOL 决定（8 个脚本保留 CRLF），造成仓库内 LF/CRLF 分裂。
     现在统一 LF：eol 常量固定 "\\n"，写文件一律 newline=""（不做平台转换）。

用法:
    from site_paths import site_base, src_base, write_svg
    BASE = site_base()                 # 站点根
    OUT  = BASE / "images" / "anim" / "x.svg"
    write_svg(OUT, text)               # 统一 UTF-8 + LF

    # 想写别处（绝不碰线上）：
    python make_anim_x.py --out /tmp/preview
"""
import sys
from pathlib import Path

EOL = "\n"


def _argv_out(argv):
    """从 argv 里取 --out <dir> / --out=<dir>；没有则返回 None。"""
    for i, a in enumerate(argv):
        if a == "--out" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--out="):
            return a.split("=", 1)[1]
    return None


def site_base(argv=None):
    """站点根目录：--out > env SITE_ROOT > 由脚本位置推导（images/tools/x.py → 上两级）。"""
    import os

    argv = list(sys.argv if argv is None else argv)
    out = _argv_out(argv)
    if out:
        return Path(out).resolve()
    env = os.environ.get("SITE_ROOT")
    if env:
        return Path(env).resolve()
    # __file__ = <site>/images/tools/site_paths.py → parents[0]=tools [1]=images [2]=site
    return Path(__file__).resolve().parents[2]


def src_base(argv=None):
    """输入根目录（只读源 SVG 所在站点）：**永不受 --out 影响**。

    历史坑（2026-11-17 自查修复）：最初 `--out` 直接改写 `site_base()`，而生成器把
    同一个 BASE 同时当作「源 SVG 所在目录」和「输出目录」——于是 `--out` 一给，
    源文件就去目标目录找，直接 FileNotFoundError（10 个读源图的生成器全挂）。
    现在职责拆开：src_base() 只看脚本自身位置；site_base() 才是可被 --out 覆盖的输出根。
    """
    return Path(__file__).resolve().parents[2]


def write_svg(path, text, argv=None):
    """写 SVG 文本：UTF-8 无 BOM、LF 换行、不做平台换行转换。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(normalized)
    return path


def read_text(path):
    """读文本并归一为 LF（供生成器解析源 SVG 用）。"""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n").replace("\r", "\n")
# ymzhu 2026-11-17 19:55
