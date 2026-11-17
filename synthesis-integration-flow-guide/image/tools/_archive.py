# -*- coding: utf-8 -*-
# _archive.py — 生成脚本的"覆盖前自动归档"动作（单一入口）
#
# 为什么需要：本站点图片是"原地覆盖"更新的（同一路径反复重写），旧版本只落在 git 历史里。
# 生成脚本在写文件前调用 snapshot()，就会先把"当前磁盘上的旧版本"存成可浏览快照：
#     image/archive/<今天 YYYYMMDD>/<文件名主干>_<当前 HEAD 短哈希>.<ext>
# 若旧版本与历史快照内容重复（md5 已存在），不重复写，只在控制台提示。
#
# 用法（在生成脚本里）：
#     from _archive import snapshot
#     snapshot(out_path)      # 写文件之前调用
#
# 也可命令行对一批路径做同样动作：
#     python image/tools/_archive.py image/30_postpt_hold_2p.png image/anim/30_postpt_hold_2p.svg
import hashlib
import os
import shutil
import subprocess
import sys
import time

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
ARCH = os.path.join(GUIDE, "image", "archive")


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _head():
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"],
                                      cwd=GUIDE, stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "nogit"


def _existing_md5():
    idx = set()
    for root, _dirs, names in os.walk(ARCH):
        for n in names:
            if n.lower().endswith((".png", ".svg")):
                idx.add(_md5(os.path.join(root, n)))
    return idx


def snapshot(path, note=""):
    """把 path 当前内容存档为历史快照；path 不存在则跳过。返回快照路径或 None。"""
    if not os.path.exists(path):
        return None
    h = _md5(path)
    if h in _existing_md5():
        print("[archive] skip（同内容快照已存在）: %s" % os.path.basename(path))
        return None
    day = time.strftime("%Y%m%d")
    stem, ext = os.path.splitext(os.path.basename(path))
    dst_dir = os.path.join(ARCH, day)
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, "%s_%s%s" % (stem, _head(), ext))
    if os.path.exists(dst):
        dst = os.path.join(dst_dir, "%s_%s_%s%s" % (stem, _head(), h[:7], ext))
    shutil.copy2(path, dst)
    print("[archive] 覆盖前快照 -> %s%s" % (os.path.relpath(dst, GUIDE).replace("\\", "/"),
                                       ("（%s）" % note) if note else ""))
    return dst


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__ or "用法: python image/tools/_archive.py <path> [<path> ...]")
        sys.exit(2)
    for p in sys.argv[1:]:
        snapshot(p)

# ymzhu 2026-11-17 19:43
