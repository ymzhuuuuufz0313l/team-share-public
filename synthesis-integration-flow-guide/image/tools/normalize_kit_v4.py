# -*- coding: utf-8 -*-
# normalize_kit_v4.py — 把 image/anim/*.svg 对齐 MOTION_KIT v4 契约（幂等，可重复运行）
#
# 处理三件事（其余字节保持不变）：
#   1) 删掉游离的 CSS 残片（形如 " 50% { opacity: 0.25; } }" —— 之前删 @keyframes 头行留下的尾巴，
#      浏览器会整条丢弃，属于"生成器拼串残留"，不是效果）；
#   2) 缺 @media (prefers-reduced-motion: reduce) 的补一个（必须是块内唯一一处）；
#   3) 根元素 width/height 带 pt 的换成 px 数值（viewBox 不动，CSS 单位不一致会让栅格化尺寸漂移）。
#
# 用法（站点根目录）：
#   python image/tools/normalize_kit_v4.py --check    # 只报告不合规项
#   python image/tools/normalize_kit_v4.py --apply    # 就地修正
import glob
import io
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
ANIM_DIR = os.path.join(GUIDE, "image", "anim")
STATIC_DIR = os.path.join(GUIDE, "image")

RM_BLOCK = ("@media (prefers-reduced-motion: reduce){"
            "*, *::before, *::after{animation:none !important;transition:none !important;}}")
ORPHAN = re.compile(r"^[ \t]*\d+%\s*\{[^{}\n]*\}\s*\}\s*$\n?", re.M)
UNIT = re.compile(r'(<svg\b[^>]*?\bwidth=")([\d.]+)pt(")')


def files():
    out = sorted(glob.glob(os.path.join(ANIM_DIR, "*.svg")))
    return out


def fix_text(s, need_prm=True):
    notes = []
    n = len(ORPHAN.findall(s))
    if n:
        s = ORPHAN.sub("", s)
        notes.append("删除游离 CSS 残片 %d 处" % n)
    if need_prm and "prefers-reduced-motion" not in s:
        i = s.rfind("]]></style>")
        if i < 0:
            i = s.rfind("</style>")
        if i >= 0:
            s = s[:i] + RM_BLOCK + "\n" + s[i:]
            notes.append("补 prefers-reduced-motion")
    # 根元素 width 的 pt → px
    def _u(m):
        return m.group(1) + ("%g" % float(m.group(2))) + m.group(3)
    if 'width="' in s:
        m = UNIT.search(s)
        if m:
            s = UNIT.sub(_u, s)
            notes.append("width pt→px")
    for attr in ("height",):
        pat = re.compile(r'(<svg\b[^>]*?\b%s=")([\d.]+)pt(")' % attr)
        if pat.search(s):
            s = pat.sub(lambda m: m.group(1) + ("%g" % float(m.group(2))) + m.group(3), s)
            notes.append("%s pt→px" % attr)
    return s, notes


def check(s, need_prm=True):
    """need_prm=True 用于动画版（必须有且只有一处）；静态版无动画，不要求 media 块。"""
    bad = []
    if ORPHAN.search(s):
        bad.append("游离 CSS 残片")
    if need_prm and s.count("prefers-reduced-motion") != 1:
        bad.append("prefers-reduced-motion 数量=%d" % s.count("prefers-reduced-motion"))
    if re.search(r'<svg\b[^>]*?\b(width|height)="[\d.]+pt"', s):
        bad.append("根元素 pt 单位")
    return bad


def main():
    apply_ = "--apply" in sys.argv
    if not apply_ and "--check" not in sys.argv:
        print("用法: python image/tools/normalize_kit_v4.py --check | --apply")
        return 2
    targets = [(p, True) for p in files()]
    targets.append((os.path.join(STATIC_DIR, "script-flow-overview.svg"), False))
    total_bad = 0
    changed = 0
    for p, need_prm in targets:
        if not os.path.exists(p):
            continue
        s = io.open(p, encoding="utf-8", newline="").read()
        bad = check(s, need_prm)
        if not bad:
            continue
        total_bad += 1
        rel = os.path.relpath(p, GUIDE).replace("\\", "/")
        if apply_:
            s2, notes = fix_text(s, need_prm)
            if s2 != s:
                io.open(p, "w", encoding="utf-8", newline="").write(s2)
                changed += 1
                print("FIX  %-45s %s" % (rel, "、".join(notes)))
            else:
                print("WARN %-45s 未自动修复: %s" % (rel, "、".join(bad)))
        else:
            print("BAD  %-45s %s" % (rel, "、".join(bad)))
    if apply_:
        print("APPLY: 修正 %d 个文件" % changed)
        # 修完再自检一遍
        left = [p for p, np_ in targets
                if os.path.exists(p) and check(io.open(p, encoding="utf-8").read(), np_)]
        print("自检: 仍不合规 %d 个" % len(left))
        for p in left:
            print("  ", os.path.relpath(p, GUIDE))
        return 0 if not left else 1
    print("CHECK: 不合规 %d 个文件 / 扫描 %d 个" % (total_bad, len(targets)))
    return 0 if total_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 19:43
