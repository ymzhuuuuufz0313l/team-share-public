# -*- coding: utf-8 -*-
# archive_history.py — 为 image/ 下的图片补"历史版本归档快照"（自动落地 + 清单）
#
# 背景：本站点图片每次重新生成都会原地覆盖（30_/31_*.png 与 image/anim/*.svg 尤其频繁），
#       旧版本只存在于 git 历史里，没有可浏览的快照。本脚本把每个图片路径在 git 历史中
#       出现过的"每个不同版本"（按 md5 去重）导出到：
#           image/archive/<提交日期 YYYYMMDD>/<stem>_<commit7>.<ext>
#       并生成 image/archive/MANIFEST.md（路径 / 来源提交 / 日期 / 大小 / md5 全映射）。
#
# 规则：
#   - 不删除任何文件，只新增快照；同名已存在且 md5 相同则跳过（可重复运行）。
#   - 与"当前工作区版本"相同的版本不导出（当前版就在原位，导出会造成"归档=当前"的假历史）。
#   - image/archive/ 自身不参与扫描。
#   - 单文件 >5MB 不导出（仓库体积约束），只在清单里记为 skipped。
#
# 用法（站点根目录）：
#   python image/tools/archive_history.py --check    # 只报告缺哪些快照
#   python image/tools/archive_history.py --apply    # 实际导出 + 重写 MANIFEST.md
import hashlib
import io
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
ARCH = os.path.join(GUIDE, "image", "archive")
MAX_BYTES = 5 * 1024 * 1024


def sh(args, binary=False):
    out = subprocess.check_output(args, cwd=GUIDE, stderr=subprocess.DEVNULL)
    return out if binary else out.decode("utf-8")


# git show <commit>:<path> 的 path 必须是仓库根相对路径（站点是仓库子目录）
PREFIX = subprocess.check_output(["git", "rev-parse", "--show-prefix"], cwd=GUIDE,
                                 stderr=subprocess.DEVNULL).decode("utf-8").strip()


def tracked_images():
    files = sh(["git", "ls-files", "image"]).splitlines()
    return [f for f in files
            if f.endswith((".png", ".svg")) and not f.startswith("image/archive/")]


def md5b(b):
    return hashlib.md5(b).hexdigest()


# 站点内曾发生"文件搬家"的图片：旧路径下的历史版本同样要归档（git log -- path 不会跨改名，
# 所以这里显式登记；新增搬家时补一行即可）。
LEGACY_PATHS = {
    "image/script-flow-overview.svg": ["script-flow-overview.svg"],  # 2026-10-27 C100 从站点根移入 image/
}


def history(path):
    """[(commit, date, blob_bytes, md5)] 按时间正序，每个 md5 只留最早一次出现。"""
    # 注意：--follow 与 --reverse 不能同时用（git 会退化成非 follow），所以取新→旧后再手工反转
    recs = sh(["git", "log", "--follow", "--format=%H|%ad", "--date=short", "--", path]).splitlines()
    recs = list(reversed(recs))
    cand = [path] + LEGACY_PATHS.get(path, [])
    seen = {}
    order = []
    for line in recs:
        if not line.strip():
            continue
        commit, date = line.split("|")
        blob = None
        for c in cand:
            try:
                blob = sh(["git", "show", "%s:%s%s" % (commit, PREFIX, c)], binary=True)
                break
            except subprocess.CalledProcessError:
                continue
        if blob is None:
            continue
        h = md5b(blob)
        if h in seen:
            continue
        seen[h] = True
        order.append((commit, date, blob, h))
    return order


def target_path(path, date, commit, blob_md5):
    stem, ext = os.path.splitext(os.path.basename(path))
    tag = commit[:7]
    fn = "%s_%s%s" % (stem, tag, ext)
    if ext == ".svg":
        pass  # svg 文本，名字不带 md5 后缀
    return os.path.join(ARCH, date.replace("-", ""), fn)


def existing_archive_index():
    """md5 -> 已存在的 archive 内相对路径（用于去重：同内容只存一份）。"""
    idx = {}
    for root, _dirs, names in os.walk(ARCH):
        for n in names:
            if not n.lower().endswith((".png", ".svg")):
                continue
            p = os.path.join(root, n)
            h = md5b(open(p, "rb").read())
            idx.setdefault(h, os.path.relpath(p, GUIDE).replace("\\", "/"))
    return idx


def main():
    apply_ = "--apply" in sys.argv
    if not apply_ and "--check" not in sys.argv:
        print("用法: python image/tools/archive_history.py --check | --apply")
        return 2

    idx = existing_archive_index()
    rows = []
    missing = 0
    written = 0
    reused = 0
    skipped_big = []
    for path in tracked_images():
        cur = os.path.join(GUIDE, path)
        cur_md5 = md5b(open(cur, "rb").read()) if os.path.exists(cur) else None
        hist = history(path)
        for commit, date, blob, h in hist:
            if h == cur_md5:
                continue  # 当前版，不归档
            if len(blob) > MAX_BYTES:
                skipped_big.append((path, commit[:7], len(blob)))
                continue
            if h in idx:
                # 同内容快照已在 archive 内，只记录映射，不重复存储
                rel = idx[h]
                reused += 1
                rows.append((path, commit, date, rel, len(blob), h, True))
                continue
            dst = target_path(path, date, commit, h)
            rel = os.path.relpath(dst, GUIDE).replace("\\", "/")
            missing += 1
            if apply_:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, "wb") as f:
                    f.write(blob)
                written += 1
                idx[h] = rel
            rows.append((path, commit, date, rel, len(blob), h, False))
        if not hist:
            rows.append((path, "-", "-", "(无历史提交)", 0, cur_md5 or "-", True))

    if apply_:
        write_manifest(rows, skipped_big)
        print("APPLY: 新增快照 %d 个，复用已有快照 %d 个，清单 image/archive/MANIFEST.md 已重写"
              % (written, reused))
    else:
        print("CHECK: 缺失快照 %d 个，可复用已有快照 %d 个（覆盖 %d 个图片路径的历史版本记录）"
              % (missing, reused, len(tracked_images())))
    if skipped_big:
        print("SKIP(>5MB): %d 项" % len(skipped_big))
    return 0


def write_manifest(rows, skipped_big):
    lines = []
    lines.append("# image/archive — 图片历史版本快照清单")
    lines.append("")
    lines.append("> 本目录由 `image/tools/archive_history.py --apply` 生成，手工改动会被下次运行覆盖。")
    lines.append("> 命名规则：`<目录日期 = 该版本首次出现的提交日期 YYYYMMDD>/<原文件名主干>_<commit7>.<ext>`。")
    lines.append("> 只导出**与当前工作区版本不同**的历史版本；当前版在原位（`image/` 或 `image/anim/`），不重复归档。")
    lines.append("")
    lines.append("| 现用路径 | 快照路径 | 来源提交 | 提交日期 | 字节 | md5 |")
    lines.append("|---|---|---|---|---|---|")
    for path, commit, date, rel, size, h, ok in rows:
        lines.append("| `%s` | `%s` | `%s` | %s | %d | `%s` |" % (path, rel, commit[:7], date, size, h))
    if skipped_big:
        lines.append("")
        lines.append("## 未导出（单文件 >5MB，仅记来源）")
        lines.append("")
        lines.append("| 现用路径 | 来源提交 | 字节 |")
        lines.append("|---|---|---|")
        for path, commit, size in skipped_big:
            lines.append("| `%s` | `%s` | %d |" % (path, commit, size))
    with io.open(os.path.join(ARCH, "MANIFEST.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 19:43
