# -*- coding: utf-8 -*-
# add_nav_sync1106.py — 在全部 *.html 的 chapters 数组中，sync-1104 之后追加 sync-1106 导航项
import io, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "..", "..")

OLD = "['sync-1104', '1104同步']"
NEW = "['sync-1104', '1104同步'],\n      ['sync-1106', '1106同步']"

for path in sorted(glob.glob(os.path.join(SITE, "*.html"))):
    txt = io.open(path, encoding="utf-8").read()
    if OLD in txt and NEW not in txt:
        txt = txt.replace(OLD, NEW, 1)
        io.open(path, "w", encoding="utf-8", newline="\n").write(txt)
        print("updated %s" % os.path.basename(path))
    elif NEW in txt:
        print("already  %s" % os.path.basename(path))
    else:
        print("NO-ENTRY %s" % os.path.basename(path))
