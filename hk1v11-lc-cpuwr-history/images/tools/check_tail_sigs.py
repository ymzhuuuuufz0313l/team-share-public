# -*- coding: utf-8 -*-
# check_tail_sigs.py — 站点尾签名条数闸门（每页必须恰好 1 条；t30）
# 用法：python images/tools/check_tail_sigs.py [--root DIR] [--quiet]
#   --root  默认站点根（本文件上两级）；负向回归测试可指向临时目录
#   --quiet 只在不合规时输出（用于 CI/串接）
# 退出码：0 = 全部恰好 1 条；1 = 有条数异常或缺页
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import tail_sig_report, TAIL_SIG_RE  # noqa: E402

ROOT = str(Path(__file__).resolve().parents[2])
quiet = False
args = sys.argv[1:]
while args:
    a = args.pop(0)
    if a == "--root":
        ROOT = args.pop(0)
    elif a == "--quiet":
        quiet = True
    else:
        raise SystemExit("unknown arg: %s" % a)

rows = tail_sig_report(ROOT)
if not rows:
    raise SystemExit("FATAL 未找到任何 *.html（root=%s）" % ROOT)

bad = [(n, c) for n, c, ok in rows if not ok]
if not quiet:
    for name, cnt, ok in rows:
        print("  %-26s sigs=%d %s" % (name, cnt, "OK" if ok else "BAD"))
if bad:
    print("FATAL 尾签名条数异常：%s" % ", ".join("%s=%d" % b for b in bad))
    sys.exit(1)
print("[sig] %d 页全部恰好 1 条（root=%s）" % (len(rows), ROOT))

# ymzhu 2026-11-17 20:52
