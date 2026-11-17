# -*- coding: utf-8 -*-
# make_sync1106_html.py — 由 sync-1104.html 骨架 + images/data/sync-1106.md 生成 sync-1106.html
#
# 2026-11-17 返工（审查 finding R3 / R4）：旧版把正文内嵌脚本、且以**自己**（线上页）为模板读取后覆盖，
# 重跑会把 `?v=20261109r2` 回退成旧串 `?v=20261106r1`（浏览器拿旧图），并在尾签名后再追加一条。
# 现行做法与 A0（sync-1106v2 / reset-spec）同款：
#   · 正文（含 `?v=` 缓存串）唯一事实源 = images/data/sync-1106.md
#   · 骨架 = sync-1104.html（固定模块逐字保留），输出走 _siteio.out_path + write_text_lf（LF）
#   · title / page-nav（上一篇 sync-1104、下一篇 sync-1106v2）/ 尾签名 = 本文件常量
# 重跑幂等：产物与线上逐字节相同（唯一变量是 SIG）。
import io, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "..", "..")
DATA = Path(__file__).resolve().parents[1] / "data"

TITLE = "1106 服务器同步 · 寄存器变更（1106v1）· LC_CPUWR 修改记录"
PREV = ("sync-1104.html", "1104 服务器同步 · 1104v1")
NEXT = ("sync-1106v2.html", "1106v2 · 20261106 全链更新")
SIG = "<!-- ymzhu 2026-11-17 20:20 -->"


def build_page(skel, title, prev, next_, md, sig):
    html = skel
    # 1) <title>
    html = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, html, count=1)
    # 2) page-nav
    nav = '<div class="page-nav">\n      %s\n      %s\n      </div>' % (
        ('<a href="./%s"><span class="label">上一篇</span><span class="title">%s</span></a>' % prev)
        if prev else "<span></span>",
        ('<a href="./%s"><span class="label">下一篇</span><span class="title">%s</span></a>' % next_)
        if next_ else "<span></span>")
    html = re.sub(r'<div class="page-nav">.*?</div>', nav, html, count=1, flags=re.S)
    # 3) #md 正文（单一数据源）
    start = html.index('<script type="text/template" id="md">') + len('<script type="text/template" id="md">')
    end = html.index('</script>', start)
    html = html[:start] + "\n" + md + "\n\n" + html[end:]
    # 4) 尾签名（替换式，不累积）：先摘掉 </html>，再把尾部一条或多条 ymzhu 签名全剥掉，最后只放一条
    body = html.rstrip()
    has_html = body.endswith("</html>")
    if has_html:
        body = body[:-len("</html>")].rstrip()
    while True:
        m = re.search(r'<!--\s*ymzhu[^\n]*-->\s*$', body)
        if not m:
            break
        body = body[:m.start()].rstrip()
    if body.endswith("</html>"):          # 骨架把签名放在 </html> 之后（timeline.html 即如此）
        has_html = True
        body = body[:-len("</html>")].rstrip()
    html = (body + "\n%s\n</html>\n" % sig) if has_html else (body + "\n%s\n" % sig)
    return html


def main():
    skel = io.open(os.path.join(SITE, "sync-1104.html"), encoding="utf-8").read()
    md = io.open(DATA / "sync-1106.md", encoding="utf-8", newline="").read().rstrip("\n")
    dst = out_path("sync-1106.html")
    write_text_lf(dst, build_page(skel, TITLE, PREV, NEXT, md, SIG))
    print("written %s  %dB" % (dst, Path(dst).stat().st_size))


if __name__ == "__main__":
    main()

# ymzhu 2026-11-17 20:20
