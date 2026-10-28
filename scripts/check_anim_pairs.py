#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_anim_pairs.py — 动画/静态双版 SVG 成对完整性扫描（v4 契约验证门，2026-10-28 ymzhu）

背景：team-share-public 采用「动画/静态双版 SVG 站点架构 v4」（blueprint-ui-style skill）。
HTML 引用一律指向动画版（<dir>/anim/<name>.svg，含 images/anim/），fx.js 切静态模式时
把路径中的 /anim/ 段去掉还原静态版 → 每个动画版必须有同名静态版，否则切换后 404 断图。

本脚本递归扫描仓库，对每个路径中含有 /anim/ 目录段的 .svg：
  检查去掉该 /anim/ 段后的同名静态版文件是否存在，输出缺失清单 + 总计。
  （与 fx.js staticSrcOf 语义一致：只去掉第一处 /anim/ 段，例：
    anim/foo.svg            -> foo.svg
    images/anim/foo.svg     -> images/foo.svg
    ./anim/foo.svg          -> ./foo.svg）

跳过目录：.git / node_modules / .venv / 任意路径中含 site-packages 的目录。

用法：python scripts/check_anim_pairs.py [repo_root]   （缺省 = 本脚本上两级 = 仓库根）
退出码：0 = 全部配对；1 = 存在缺失静态版的孤儿动画版；2 = 仓库根不存在。
只扫描报告，不做任何修复。
"""
import sys
from pathlib import Path

SKIP_NAMES = {'.git', 'node_modules', '.venv'}


def iter_anim_svgs(root: Path):
    """产出 (anim_svg 绝对路径, 相对路径)；只挑目录段里含 'anim' 的 .svg。"""
    for p in sorted(root.rglob('*.svg')):
        rel = p.relative_to(root)
        parts = rel.parts
        if any(part in SKIP_NAMES or 'site-packages' in part for part in parts):
            continue
        if 'anim' in parts[:-1]:  # 'anim' 必须是目录段，不是文件名
            yield p, rel


def static_of(rel: Path) -> Path:
    """去掉相对路径中第一处 /anim/ 目录段（与 fx.js staticSrcOf 语义一致）。"""
    parts = list(rel.parts)
    parts.remove('anim')  # remove 只删第一个匹配项
    return Path(*parts)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print('[check_anim_pairs] ERROR repo root not found: %s' % root)
        return 2
    try:  # Windows 控制台 CJK 输出保险
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    total = 0
    missing = []
    for _p, rel in iter_anim_svgs(root):
        total += 1
        expect = static_of(rel)
        if not (root / expect).is_file():
            missing.append((rel.as_posix(), expect.as_posix()))

    print('[check_anim_pairs] repo: %s' % root)
    print('[check_anim_pairs] anim svg total: %d' % total)
    if missing:
        print('[check_anim_pairs] MISSING static counterpart: %d' % len(missing))
        for anim, expect in missing:
            print('  ORPHAN  %s  -> expected static: %s' % (anim, expect))
        print('[check_anim_pairs] RESULT: FAIL (%d orphan anim svg, %d paired)' % (len(missing), total - len(missing)))
        return 1
    print('[check_anim_pairs] RESULT: OK — all %d anim svgs have static counterparts' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
