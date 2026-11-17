# -*- coding: utf-8 -*-
"""backfill_archive.py — 一次性补齐「从未归档过」的图版基线（审查 finding F21）。

背景：站点 8 个图族（4 静态图表图 + 1 LSI 图 + 1 checksum 图 + 1 checksum 逻辑图
+ 1 beat 重排图）自建站以来换过多轮内容，但 images/archive/ 下只有 1104/1109/1110
三批快照，这 8 族（12 个 SVG 文件里 8+8=16 个文件）**从未归档过任一历史版本**，
一旦再次改动或误跑生成器，就没有回滚基线。

做法：从 **git HEAD**（= 当前已提交、正在服务的版本，站点口径 1106v4）取原件，
落到 images/archive/20261117/<stem>_1106v4.svg（动画版加 anim_ 前缀，沿用站内惯例）。
幂等：目标已存在且字节相同则跳过。

用法：python tools/backfill_archive.py [--dry-run]
"""
import io
import subprocess
import sys
from pathlib import Path

IMAGES = Path(__file__).resolve().parents[1]
SITE_ROOT = IMAGES.parent
TAG = "1106v4"
DATE = "20261117"

FAMILIES = [
    "1104_reg_sync_changes",
    "checksum_address_map",
    "chip_sel0_register_map",
    "chip_sel1_register_map",
    "checksum_logic_flow",
    "config_data_beat_regroup_0721",
    "lsi_unprotected_address_map",
    "reset_domain_address_map",
]


def head_bytes(rel):
    """取 git HEAD 版本（相对仓库根）。仓库根 = 向上找一个含 .git 的目录。"""
    root = SITE_ROOT
    while not (root / ".git").exists() and root.parent != root:
        root = root.parent
    full = rel.relative_to(root).as_posix()
    r = subprocess.run(["git", "show", "HEAD:" + full], cwd=str(root), capture_output=True)
    if r.returncode != 0:
        raise SystemExit("FATAL: git show 失败 %s: %s" % (full, r.stderr.decode("utf-8", "replace")))
    return r.stdout


def main(argv):
    dry = "--dry-run" in argv
    added = skipped = 0
    for fam in FAMILIES:
        for sub, prefix in (("images", ""), ("images/anim", "anim_")):
            rel = IMAGES / (fam + ".svg") if sub == "images" else IMAGES / "anim" / (fam + ".svg")
            if not rel.exists():
                print("MISSING-SRC %s" % rel)
                continue
            data = head_bytes(rel)
            dst = IMAGES / "archive" / DATE / ("%s%s_%s.svg" % (prefix, fam, TAG))
            if dst.exists() and dst.read_bytes() == data:
                skipped += 1
                continue
            if dry:
                print("WOULD  %s  (%dB)" % (dst.name, len(data)))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(data)
                print("BACKFILLED  %s  (%dB)" % (dst.name, len(data)))
            added += 1
    print("\nRESULT: backfilled=%d skipped(idempotent)=%d of %d expected"
          % (added, skipped, 2 * len(FAMILIES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

# ymzhu 2026-11-17 19:33