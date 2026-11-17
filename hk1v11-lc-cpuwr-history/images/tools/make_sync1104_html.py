# -*- coding: utf-8 -*-
# make_sync1104_html.py — 由 timeline.html 骨架 + images/data/sync-1104.md 生成 sync-1104.html
#
# 2026-11-17 返工（审查 finding R2 / R4）：旧版把 §1-5 旧正文内嵌在脚本里、直接覆盖线上页，
# 而线上页早已手工扩展到 §6（1104v1 迭代）并勘误 NO54 —— 任何人重跑一次就会删 56 行、把错值打回。
# 现行做法与 A0（sync-1106v2 / reset-spec）同款：
#   · 正文（含 §6 与勘误）唯一事实源 = images/data/sync-1104.md
#   · 输出走 _siteio.out_path（支持 --out 预演）+ write_text_lf（LF）
#   · title / page-nav（上一篇 status、下一篇 sync-1106）/ 尾签名 = 本文件常量，单一处
# 重跑幂等：与本文件常量一致时，产物与线上逐字节相同（唯一变量是 SIG，改时间才变）。
import io, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "..", "..")
DATA = Path(__file__).resolve().parents[1] / "data"

TITLE = "1104 服务器同步 · 寄存器变更 · LC_CPUWR 修改记录"
PREV = ("status.html", "当前状态与后续")
NEXT = ("sync-1106.html", "1106 服务器同步 · 1106v1")
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
    skel = io.open(os.path.join(SITE, "timeline.html"), encoding="utf-8").read()
    md = io.open(DATA / "sync-1104.md", encoding="utf-8", newline="").read().rstrip("\n")
    dst = out_path("sync-1104.html")
    write_text_lf(dst, build_page(skel, TITLE, PREV, NEXT, md, SIG))
    print("written %s  %dB" % (dst, Path(dst).stat().st_size))


if __name__ == "__main__":
    main()

# ymzhu 2026-11-17 20:20
