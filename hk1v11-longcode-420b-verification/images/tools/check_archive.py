#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""归档完整性闸门（F05/V1 根因修复）：被替换的图版必须有快照。

背景（t15 验收 V1）
-------------------
本站 `images/archive/20261117/README.md` 写了「任何被替换的版本必须在同一提交内
`git show <上一版 rev>:<path>` 取出并落到 `images/archive/<日期>/`」，但这条规范
**只是文本约定**：没有任何机器检查，于是 2026-11-17 的修复把 3 个图版
（`images/delta_case_matrix.svg`、`images/anim/delta_case_matrix.svg`、
`images/anim/spec_tag_replacement.svg`）原地覆盖掉而没留快照，直到 t15 验收才被发现。

本闸门把那条规范变成机器可判的红线：

  对 `images/`（不含 `images/archive/`）下每个被改动的图文件，
  要求 `images/archive/` 里存在一份**内容等于改动前版本**的快照（按 LF 归一后逐字节比对）。

比对口径与站点 EOL 卫生一致：归档快照落盘时统一把 CRLF/CR 归一为 LF，
故这里把两侧都归一后比较（不因换行差异误判为「缺归档」）。

用法（**`--base` 必须显式给出**）：
    python images/tools/check_archive.py --base HEAD      # 比对 HEAD 与工作区（提交前自查）
    python images/tools/check_archive.py --base 818ca97   # 事后追查：某历史版本之后被改动的图
    python images/tools/check_archive.py --base HEAD~1 --site <dir>

退出码：0 = 被改动的图都有快照；1 = 有缺失；2 = 无法判定（未给 --base / 不在 git 仓库内等）。

2026-11-17 t28 修复（R2，闸门自伤）：
    旧版 `--base` 默认 `HEAD`，于是在干净工作树上「被改动的图 = 0」→ 直接打印
    `RESULT: ALL PASS (无图被改动)` 并 exit 0 —— 等于什么都没检查却给绿灯（静默空跑 PASS）。
    现在：未显式给 `--base` 一律拒绝运行（exit 2 + 用法提示），绝不返回 PASS；
    即便给了 `--base` 而差异为 0，也显式打印「本次未检查任何图」的提示，不再静默绿灯。
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_paths import site_base  # noqa: E402

ARCHIVE_DIRNAME = "archive"


def _norm(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def git(site: Path, *args, check=True):
    r = subprocess.run(["git", "-C", str(site), *args],
                       capture_output=True)
    if check and r.returncode != 0:
        raise SystemExit(f"[check_archive] git {' '.join(args)} 失败："
                         f"{r.stderr.decode('utf-8', 'replace').strip()}")
    return r


def repo_root(site: Path) -> Path:
    r = git(site, "rev-parse", "--show-toplevel", check=False)
    if r.returncode != 0:
        raise SystemExit(f"[check_archive] {site} 不在 git 仓库内，无法判定")
    return Path(r.stdout.decode("utf-8").strip())


def blobs_at(site: Path, root: Path, rev: str, paths):
    """批量取多个路径在 rev 的内容：{repo-relative path: bytes 或 None（该 rev 下不存在）}。"""
    out = {}
    for p in paths:
        r = git(site, "show", f"{rev}:{p}", check=False)
        out[p] = r.stdout if r.returncode == 0 else None
    return out


def changed_images(site: Path, root: Path, base: str):
    """返回 images/ 下（排除 archive/）在 base ↔ 工作区 之间有变化的路径列表。"""
    rel_site = site.resolve().relative_to(root.resolve()).as_posix()
    # 注意：paths 一律以**仓库根**为基准（git -C root），否则 pathspec 会被 cwd 二次前缀
    diff = git(root, "diff", "--name-only", base, "--", f"{rel_site}/images")
    work = git(root, "ls-files", "--others", "--exclude-standard", "--",
               f"{rel_site}/images")
    names = [x for x in (diff.stdout + work.stdout).decode("utf-8", "replace").splitlines() if x]
    keep = []
    for n in names:
        p = Path(n)
        if not p.name.lower().endswith((".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif")):
            continue
        if ARCHIVE_DIRNAME in p.parts:
            continue
        keep.append(n)
    return sorted(set(keep))


def archive_index(site: Path) -> dict:
    """{归一化后 md5: [归档相对路径…]}"""
    import hashlib
    idx = {}
    adir = site / "images" / ARCHIVE_DIRNAME
    if not adir.exists():
        return idx
    for f in sorted(adir.rglob("*")):
        if not f.is_file() or f.suffix.lower() not in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif"):
            continue
        h = hashlib.md5(_norm(f.read_bytes())).hexdigest()
        idx.setdefault(h, []).append(f.relative_to(site).as_posix())
    return idx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=None)
    ap.add_argument("--base", default=None,
                    help="对比基线 rev（必填；提交前自查用 HEAD，事后追查给具体 rev）")
    a = ap.parse_args()
    for _f in (sys.stdout, sys.stderr):
        try:
            _f.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if not a.base:
        # R2（2026-11-17）：不给基线就无从判定。旧版默认 HEAD，干净树上直接空跑 PASS，
        # 等于「闸门什么都没查却给绿灯」。这里宁可不跑，也不给假绿。
        print("[check_archive] ERROR: 必须显式指定 --base <rev>（本闸门不做空跑放行）", file=sys.stderr)
        print("[check_archive]   提交前自查：python images/tools/check_archive.py --base HEAD",
              file=sys.stderr)
        print("[check_archive]   事后追查：  python images/tools/check_archive.py --base <rev>",
              file=sys.stderr)
        print("[check_archive] RESULT: 未运行（缺少 --base）", file=sys.stderr)
        return 2
    site = Path(a.site).resolve() if a.site else site_base()
    root = repo_root(site)

    changed = changed_images(site, root, a.base)
    print(f"[check_archive] site  = {site}")
    print(f"[check_archive] base  = {a.base}")
    print(f"[check_archive] 被改动的图 = {len(changed)}")

    if not changed:
        # 给了 --base 且差异为 0：合法，但必须说清「本次没检查任何图」，避免被读成强绿。
        print("[check_archive] 注意：base 与工作区之间没有图文件差异 —— 本次未检查任何图"
              "（这不代表归档完整，只代表这段区间没动图）")
        print("[check_archive] RESULT: ALL PASS (0 张图被改动，无可检查项)")
        return 0

    before = blobs_at(site, root, a.base, changed)
    idx = archive_index(site)
    import hashlib
    missing = []
    for p in changed:
        b = before.get(p)
        if b is None:
            # base 里不存在 = 新增图，无「被替换的旧版」→ 不需要快照
            print(f"  NEW      {p}（{a.base} 中不存在，无需快照）")
            continue
        work = root / p
        if work.exists() and _norm(work.read_bytes()) == _norm(b):
            print(f"  EOLONLY  {p}（仅换行变化）")
        h = hashlib.md5(_norm(b)).hexdigest()
        hits = idx.get(h, [])
        if hits:
            print(f"  OK       {p}  <= {hits[0]}")
        else:
            print(f"  MISSING  {p}  <== {a.base} 版本 md5 {h} 在 images/archive/ 下无快照")
            missing.append((p, h))

    if missing:
        print(f"[check_archive] RESULT: FAIL ({len(missing)} 张图被替换但无归档快照)")
        print("[check_archive] 修复：git show %s:<path> > images/archive/<YYYYMMDD>/<stem>_before_<rev>.svg" % a.base)
        return 1
    print("[check_archive] RESULT: ALL PASS (被改动的图均有归档快照)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
# ymzhu 2026-11-17 21:05
