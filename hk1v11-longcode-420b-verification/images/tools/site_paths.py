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

# 归档根（相对站点根）：被替换的图版快照统一落这里，目录名 = 更新日期
ARCHIVE_ROOT = ("images", "archive")


def _git_short_rev(site):
    """取站点所在仓库的短 rev；不在 git 仓库内则回退 'worktree'。

    用途：自动归档文件名里的 `<rev>` 段，标明「这份快照替代的是哪个提交的版本」。
    """
    import subprocess

    try:
        r = subprocess.run(["git", "-C", str(site), "rev-parse", "--short", "HEAD"],
                           capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode("utf-8", "replace").strip() or "worktree"
    except Exception:  # git 缺失等：归档文件名退化为 worktree，不阻断生成
        pass
    return "worktree"


def archive_before_overwrite(path, site=None, date=None, tag=None):
    """覆盖写之前，把**当前磁盘上的旧版**快照到 images/archive/<YYYYMMDD>/<rel>_before_<rev>.<ext>。

    这是 `images/archive/20261117/README.md`「归档规范（新）」的机械化版本（F05/V1 根因修复）：
    规范原文只写在 README 里、没有任何代码执行它，于是 2026-11-17 那次修复把 3 个图版
    原地覆盖掉而没留快照，直到 t15 验收才发现。

    行为：
      - 目标不存在 → 什么都不做（无「被替换的旧版」）；
      - 旧版内容与新内容相同 → 什么都不做（幂等重跑不产生噪声快照）；
      - `--out` / `SITE_ROOT` 预览模式（site_base() != 脚本站点）→ 什么都不做（不污染仓库）；
      - 已存在内容相同的快照 → 跳过（二次运行幂等）。
    返回落盘路径或 None。
    """
    from pathlib import Path
    import datetime
    import shutil

    path = Path(path)
    if not path.exists():
        return None
    site = Path(site) if site else src_base()          # 预览模式判据用脚本站点根
    try:
        rel = path.resolve().relative_to((site / "images").resolve())
    except ValueError:
        return None                                    # 不在 images/ 下，不管
    if rel.parts and rel.parts[0] == ARCHIVE_ROOT[1]:
        return None                                    # 已在归档目录内，避免自我归档
    tag = tag or ("before_" + _git_short_rev(site))
    date = date or datetime.date.today().strftime("%Y%m%d")
    dst = site.joinpath(*ARCHIVE_ROOT) / date / rel.parent / f"{rel.stem}_{tag}{rel.suffix}"
    cur = path.read_bytes()
    if dst.exists() and _norm_bytes(dst.read_bytes()) == _norm_bytes(cur):
        return dst                                     # 幂等
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, dst)
    return dst


def _norm_bytes(b):
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def is_preview(path=None):
    """当前是否在「预览到别处」模式（--out / SITE_ROOT 生效）。"""
    return bool(_argv_out(list(sys.argv)) or __import__("os").environ.get("SITE_ROOT"))


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


def write_svg(path, text, argv=None, archive=None):
    """写 SVG 文本：UTF-8 无 BOM、LF 换行、不做平台换行转换。

    `archive`（默认 None = 自动判断）：
      - True  → 覆盖前先 `archive_before_overwrite()` 留旧版快照（F05/V1 根因修复）；
      - False → 不留快照（导出/一次性工具）；
      - None  → 仅当旧版内容与新内容**不同**且不在预览模式时留快照。
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if archive is None:
        archive = True
    if archive and not is_preview() and path.exists():
        try:
            same = _norm_bytes(path.read_bytes()) == _norm_bytes(normalized.encode("utf-8"))
        except OSError:
            same = False
        if not same:
            archive_before_overwrite(path)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(normalized)
    return path


def read_text(path):
    """读文本并归一为 LF（供生成器解析源 SVG 用）。"""
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read().replace("\r\n", "\n").replace("\r", "\n")


# ---------------------------------------------------------------------------
# 单一事实源（V2 修复：行数族不再散落在生成器里）
# ---------------------------------------------------------------------------
FACTS_REL = ("images", "tools", "data", "facts.json")


def load_facts(site=None):
    """读 `images/tools/data/facts.json`（唯一事实源），返回 dict。

    生成器一律从这里取业务数字，不得在源码里写字面量；页面（静态 HTML，
    本站无构建步骤）由 `check_facts.py` 反向核对，属于同一套单一事实源约定。
    """
    import json

    p = Path(site if site is not None else site_base()) / Path(*FACTS_REL)
    if not p.exists():
        raise SystemExit(f"[site_paths] 缺少事实源：{p}")
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def file_lines(site=None):
    """`facts.json` 的 `file_lines` 块（RTL/checker 行数族）。"""
    facts = load_facts(site)
    if "file_lines" not in facts:
        raise SystemExit("[site_paths] facts.json 缺少 file_lines 块"
                         "（用 extract_facts.py --lines-src 生成）")
    return facts["file_lines"]
# ymzhu 2026-11-17 20:35
