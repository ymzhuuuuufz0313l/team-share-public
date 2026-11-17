# -*- coding: utf-8 -*-
"""图版归档快照助手（2026-11-17 审计 A9-1 / A9-5 修复）。

问题
----
本站图版标准（`images/tools/README.md`）：主名 = 当前采纳版；被替换/发布过的图必须
快照进 `images/archive/<日期>/`；**图永不删除**。但归档此前全靠人手 `cp`，
于是 `skew_probe_audit_1028` 静态 + 动画版**从未归档**（A9-1），且 archive 里
存在多组 md5 完全相同的重复快照（A6-2）。

本模块把「归档」变成生成器的自动收尾动作：
  * 拷贝到 `images/archive/<date_tag>/<name>`（可选版本标签）
  * **md5 去重**：archive 内已有同 md5 文件时不再复制第二份，直接复用并打印命中的旧路径
  * 往 `images/archive/README.md` 追加一行（文件名 + md5 + 说明），同一 (文件名, md5) 幂等
调用方（生成器）：
  * `images/anim/make_anim_skew_probe_audit_1028.py`（动画版）
  * `E:/project/HK1V11/docs/skew_probe_audit_1028/gen_audit_diagram.py`（静态版；
    该脚本还会把静态 SVG 发布到本站 `images/`，避免"改了源、站点没换、archive 也没记"）

用法（生成器内）：
    import archive_snapshot as AS
    AS.snapshot(out_path, date_tag="20261102", note="静态版")

注意：本模块只增不改 —— 已存在的归档文件不会被覆盖或删除。
"""
import hashlib
import io
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parents[2]
ARCHIVE = SITE / "images" / "archive"
README = ARCHIVE / "README.md"

_HEADER = """# images/archive/ — 图版快照与重复对账

> 规则：图**永不删除**；主名 = 当前采纳版；被替换/发布过的版本快照进 `<采纳日期>/`。
> 本文件的两张表都由 `images/tools/archive_snapshot.py` 在生成器收尾时自动追加：
> 1. **快照登记**（每归档一次 1 行，`文件名 + md5` 幂等）；2. **重复对账**见文末「同 md5 快照对账」表。
"""


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_same_md5(digest, exclude=None):
    """在整个 archive 树里找同 md5 的既有快照（返回第一个路径）。"""
    for p in sorted(ARCHIVE.rglob("*")):
        if not p.is_file() or p.name == "README.md":
            continue
        if exclude is not None and p.resolve() == Path(exclude).resolve():
            continue
        if md5_of(p) == digest:
            return p
    return None


def _append_row(name, digest, note, date_tag, size):
    text = README.read_text(encoding="utf-8") if README.is_file() else _HEADER
    row = "| %s | `%s` | `%s` | %d B | %s |" % (date_tag, name, digest, size, note)
    if row in text:
        return False
    if "| 日期 | 文件 | md5 | 大小 | 说明 |" not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += ("\n## 快照登记（自动追加）\n\n"
                 "| 日期 | 文件 | md5 | 大小 | 说明 |\n|---|---|---|---|---|\n")
    if not text.endswith("\n"):
        text += "\n"
    text += row + "\n"
    README.write_text(text, encoding="utf-8", newline="")
    return True


def snapshot(src, date_tag, version_tag=None, note="", verbose=True):
    """把 src 快照进 images/archive/<date_tag>/ 并登记；同 md5 已存在则复用不复制。"""
    src = Path(src)
    if not src.is_file():
        raise FileNotFoundError(src)
    digest = md5_of(src)
    name = src.name if not version_tag else "%s_%s%s" % (src.stem, version_tag, src.suffix)
    dst = ARCHIVE / date_tag / name

    same = find_same_md5(digest, exclude=dst if dst.exists() else None)
    if same is not None:
        if verbose:
            print("[archive] 已存在同 md5 快照，跳过重复拷贝：%s（md5 %s）"
                  % (same.relative_to(SITE).as_posix(), digest))
        return same
    if dst.exists() and md5_of(dst) == digest:
        if verbose:
            print("[archive] 已归档且内容一致：%s" % dst.relative_to(SITE).as_posix())
        return dst
    if dst.exists():
        # 归档只增不改：同名但内容不同的快照绝不覆盖（否则会静默丢历史版本）
        raise RuntimeError("archive_snapshot: 目标已存在且 md5 不同，拒绝覆盖 %s（请给 version_tag 区分）"
                           % dst.as_posix())

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    _append_row(dst.name, digest, note or "自动快照", date_tag, dst.stat().st_size)
    if verbose:
        print("[archive] 已快照 %s -> %s（md5 %s, %d B）"
              % (src.name, dst.relative_to(SITE).as_posix(), digest, dst.stat().st_size))
    return dst
# ymzhu 2026-11-17 19:24
