# -*- coding: utf-8 -*-
# make_sync1106v2_reset_html.py — 由 sync-1106.html 骨架生成 sync-1106v2.html（20261106 表全链）+ reset-spec.html（复位规格）
# 仅替换 title / page-nav / #md 内容 / 尾签名（骨架 = 固定模块，逐字保留）；并更新 sync-1106.html 下一篇指向 sync-1106v2
import io, os, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import (out_path, write_text_lf, is_dry_run, out_root,  # noqa: E402
                     write_page_one_sig, assert_tail_sigs)

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
    # 4) 尾签名：交 _siteio.write_page_one_sig（先剥 `</html>` 再剥签名 → 归一为恰好 1 条）
    #    旧实现 re.sub(r'<!--\s*ymzhu[^\n]*-->\s*$', ...) 锚在字符串末尾，看不见骨架里
    #    `</html>` **之前**那条签名 → 稳定产出 2 条（t30 病理，已在此治根）。
    write_page_one_sig(dst, html, sig)
    print("written %s  %dB" % (dst, os.path.getsize(dst)))

SIG = "<!-- ymzhu 2026-11-17 20:52 -->"

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

# ===== 尾签名断言：每页必须恰好 1 条（任何回归立刻非 0 退出）=====
# 预演只校验预演产物；就地写完才在全站 17 页上校验（顺序不能颠倒，否则预演会被线上旧态误拦）
if is_dry_run():
    assert_tail_sigs(out_root())
    print("dry-run: 跳过 sync-1106.html page-nav 更新")
    sys.exit(0)
sp = io.open(SKEL, encoding="utf-8").read()
sp = sp.replace(
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <span></span>',
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <a href="./sync-1106v2.html"><span class="label">下一篇</span><span class="title">1106v2 · 20261106 全链更新</span></a>', 1)
write_text_lf(SKEL, sp)
print("updated sync-1106.html page-nav next -> sync-1106v2")

# ===== 落盘后全站尾签名断言（17 页每页恰好 1 条）=====
assert_tail_sigs(SITE)

# ymzhu 2026-11-17 20:52
