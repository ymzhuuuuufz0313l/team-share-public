# -*- coding: utf-8 -*-
import io, os
SITE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # images/tools -> site
PAGES = ["index.html","intro.html","diagrams.html","timeline.html","checksum.html","regmap.html","register-research.html","verification.html","status.html","sync-1104.html","sync-1106.html","sync-1106v2.html","reset-spec.html"]
ANCHOR = "  ['sync-1106', '1106同步']"
NEW = "  ['sync-1106', '1106同步'],\n  ['sync-1106v2', '1106v2全链'],\n  ['reset-spec', '复位规格']"
for f in PAGES:
    p = os.path.join(SITE, f)
    t = io.open(p, encoding="utf-8").read()
    if "['sync-1106v2', '1106v2全链']" in t:
        print("skip  %s" % f); continue
    if ANCHOR not in t:
        print("MISS  %s (no sync-1106 anchor)" % f); continue
    t = t.replace(ANCHOR, NEW, 1)
    io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print("nav   %s" % f)
print("done")
# ymzhu 2026-11-06 21:08
