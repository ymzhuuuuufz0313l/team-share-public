# -*- coding: utf-8 -*-
# make_sync1106v2_reset_html.py — 由 sync-1106.html 骨架生成 sync-1106v2.html（20261106 表全链）+ reset-spec.html（复位规格）
# 仅替换 title / page-nav / #md 内容 / 尾签名（骨架 = 固定模块，逐字保留）；并更新 sync-1106.html 下一篇指向 sync-1106v2
import io, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf, is_dry_run  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "..", "..")
SKEL = os.path.join(SITE, "sync-1106.html")
html0 = io.open(SKEL, encoding="utf-8").read()

def build_page(dst, title, prev, next, md, sig):
    html = html0
    # 1) <title>（替换 sync-1106 的 title）
    html = re.sub(r"<title>1106 服务器同步[^<]*</title>", "<title>%s</title>" % title, html, count=1)
    # 2) page-nav（替换 sync-1106 的 page-nav：prev=sync-1104）
    nav = '<div class="page-nav">\n      %s\n      %s\n      </div>' % (
        ('<a href="./%s"><span class="label">上一篇</span><span class="title">%s</span></a>' % prev) if prev else "<span></span>",
        ('<a href="./%s"><span class="label">下一篇</span><span class="title">%s</span></a>' % next) if next else "<span></span>")
    html = re.sub(r'<div class="page-nav">.*?</div>', nav, html, count=1, flags=re.S)
    # 3) #md 内容
    start = html.index('<script type="text/template" id="md">') + len('<script type="text/template" id="md">')
    end = html.index('</script>', start)
    html = html[:start] + "\n" + md + "\n" + html[end:]
    # 4) 尾签名
    html = re.sub(r'<!--\s*ymzhu[^\n]*-->\s*$', '', html.rstrip())
    html = html.rstrip()
    if html.endswith('</html>'):
        html = html[:-len('</html>')].rstrip() + "\n%s\n</html>\n" % sig
    else:
        html = html + "\n%s\n" % sig
    write_text_lf(dst, html)
    print("written %s  %dB" % (dst, len(html)))

SIG = "<!-- ymzhu 2026-11-17 19:33 -->"

# ===== sync-1106v2.html（新表变更内容页）=====
MD_V2 = io.open(Path(__file__).resolve().parents[1] / "data" / "sync-1106v2.md",
               encoding="utf-8").read()   # A0：正文单一数据源 images/data/sync-1106v2.md
build_page(out_path("sync-1106v2.html"),
           "1106v2 · 寄存器表 20261106 全链更新 · LC_CPUWR 修改记录",
           ("sync-1106.html", "1106 服务器同步 · 1106v1"),
           ("reset-spec.html", "复位规格 · 20261106"),
           MD_V2, SIG)

# ===== reset-spec.html（复位规格页）=====
MD_RS = io.open(Path(__file__).resolve().parents[1] / "data" / "reset-spec.md",
               encoding="utf-8").read()   # A0：正文单一数据源 images/data/reset-spec.md
build_page(out_path("reset-spec.html"),
           "复位规格 · 20261106（1106v4 终版）· LC_CPUWR 修改记录",
           ("sync-1106v2.html", "1106v2 · 20261106 全链更新"),
           None,
           MD_RS, SIG)

# ===== 更新 sync-1106.html 下一篇指向 sync-1106v2（--out 预演时跳过，避免改线上骨架）=====
if is_dry_run():
    print("dry-run: 跳过 sync-1106.html page-nav 更新")
    sys.exit(0)
sp = io.open(SKEL, encoding="utf-8").read()
sp = sp.replace(
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <span></span>',
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <a href="./sync-1106v2.html"><span class="label">下一篇</span><span class="title">1106v2 · 20261106 全链更新</span></a>', 1)
write_text_lf(SKEL, sp)
print("updated sync-1106.html page-nav next -> sync-1106v2")

# ymzhu 2026-11-17 19:33