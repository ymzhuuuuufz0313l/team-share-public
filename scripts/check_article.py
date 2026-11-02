"""check_article.py — team-share-public 文章站点发布前门禁（2026-11-02）

team-share skill Workflow B 第 9 步强制：exit 0 才能提交。规则来源 = team-share SKILL.md 的
Important Rules / 自查清单；把"模型记不记得规则"变成"过不过门禁"。

检查项（逐页）：
  F  fx 双 tag     ：fx.css 与 fx.js 引用各恰 1 次，且站点目录内两个引擎文件存在
  L  lightbox      ：页面内有 id="lightbox"，或引用了站内 lightbox.js（文件须存在）
  T  TOC 折叠      ：有正文 markdown（id="md"）的页面，须在页面或其引用的站内 js 中含 toc-arrow
  H  标题编号      ：markdown 正文中 h2 须为 `## N.`、h3 须为 `### N.M`、h4 须为 `#### N.M.K`（代码块内跳过）
  S  尾签名        ：最后一个非空行是 <!-- ymzhu YYYY-MM-DD HH:MM ... -->
站点级：
  P  页面存在      ：站点目录内至少 1 个 .html 页面
  N  导航数量      ：js/site.js 的 NAV 数组条目数（或 index.html .navbar-links 内链接数）≤ 10（首页 + 9）

用法：python check_article.py <站点目录名或路径> [--only F,L,...]
退出码：0 = 全过；1 = 有失败（逐条列出）；2 = 用法错误
"""
import os
import re
import sys

REPO = r'E:\project\team-share-public'


def read(p):
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


def local_js(site, html):
    """页面引用的站内 js 文件路径（去掉 ?v=）"""
    out = []
    for src in re.findall(r'<script[^>]+src="([^"]+)"', html):
        if src.startswith(('http:', 'https:', '//')):
            continue
        p = os.path.normpath(os.path.join(site, src.split('?')[0]))
        if os.path.isfile(p):
            out.append(p)
    return out


def md_body(html):
    m = re.search(r'<script type="text/template" id="md">(.*?)</script>', html, re.S)
    return m.group(1) if m else None


def check_headings(md):
    bad, fence = [], False
    for line in md.splitlines():
        s = line.strip()
        if s.startswith('```'):
            fence = not fence
            continue
        if fence:
            continue
        if re.match(r'^## ', s) and not re.match(r'^## \d+\.\s', s):
            bad.append(s[:60])
        elif re.match(r'^### ', s) and not re.match(r'^### \d+\.\d+\s', s):
            bad.append(s[:60])
        elif re.match(r'^#### ', s) and not re.match(r'^#### \d+\.\d+\.\d+\s', s):
            bad.append(s[:60])
    return bad


def nav_count(site):
    sj = os.path.join(site, 'js', 'site.js')
    if os.path.isfile(sj):
        m = re.search(r'NAV\s*=\s*\[(.*?)\];', read(sj), re.S)
        if m:
            return len(re.findall(r'href\s*:', m.group(1))), 'js/site.js NAV'
    idx = os.path.join(site, 'index.html')
    if os.path.isfile(idx):
        m = re.search(r'class="navbar-links"[^>]*>(.*?)</(?:div|nav|ul)>', read(idx), re.S)
        if m:
            return len(re.findall(r'<a\s', m.group(1))), 'index.html .navbar-links'
    return None, '未找到导航定义'


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    only = None
    for a in sys.argv[1:]:
        if a.startswith('--only='):
            only = set(a.split('=', 1)[1].split(','))
    if not args:
        print(__doc__)
        sys.exit(2)
    site = args[0] if os.path.isdir(args[0]) else os.path.join(REPO, args[0])
    if not os.path.isdir(site):
        print(f'站点目录不存在：{site}')
        sys.exit(2)
    want = lambda k: only is None or k in only

    pages = sorted(f for f in os.listdir(site) if f.endswith('.html'))
    fails = []
    if not pages:
        fails.append('[P] 站点目录内没有任何 .html 页面（未完成发布）')
    if want('F'):
        for eng in ('fx.css', 'fx.js'):
            if not os.path.isfile(os.path.join(site, eng)):
                fails.append(f'[F] 站点缺引擎文件 {eng}')
    for pg in pages:
        html = read(os.path.join(site, pg))
        jss = local_js(site, html)
        if want('F'):
            nc = len(re.findall(r'href="\./fx\.css(?:\?[^"]*)?"', html))
            nj = len(re.findall(r'src="\./fx\.js(?:\?[^"]*)?"', html))
            if nc != 1 or nj != 1:
                fails.append(f'[F] {pg}: fx.css ×{nc}、fx.js ×{nj}（应各 1）')
        if want('L'):
            has_lb = 'id="lightbox"' in html or any(os.path.basename(j) == 'lightbox.js' for j in jss)
            # 图片既可能是 HTML <img>，也可能是正文 markdown 的 ![](...)（运行时才渲染成 <img>）
            mdb = md_body(html) or ''
            if not has_lb and ('<img' in html or re.search(r'!\[[^\]]*\]\(', mdb)):
                fails.append(f'[L] {pg}: 含图片但无 lightbox')
        md = md_body(html)
        if want('T') and md is not None:
            if 'toc-arrow' not in html and not any('toc-arrow' in read(j) for j in jss):
                fails.append(f'[T] {pg}: 有正文但无 TOC 折叠（toc-arrow）')
        if want('H') and md is not None:
            bad = check_headings(md)
            if bad:
                fails.append(f'[H] {pg}: {len(bad)} 个标题未编号，如「{bad[0]}」')
        if want('S'):
            last = [l for l in html.splitlines() if l.strip()][-1].strip() if html.strip() else ''
            if not re.match(r'^<!-- ymzhu \d{4}-\d{2}-\d{2} \d{2}:\d{2}', last):
                fails.append(f'[S] {pg}: 末行不是 ymzhu 签名（{last[:50]}）')
    if want('N'):
        n, src = nav_count(site)
        if n is None:
            fails.append(f'[N] {src}')
        elif n > 10:
            fails.append(f'[N] 导航 {n} 项 > 10（首页 + 9），来源 {src}')

    name = os.path.basename(os.path.normpath(site))
    print(f'[check_article] {name}：{len(pages)} 页')
    if fails:
        print(f'  FAIL — {len(fails)} 项：')
        for f in fails:
            print('   ✗ ' + f)
        sys.exit(1)
    print('  PASS')


if __name__ == '__main__':
    main()

# ymzhu 2026-11-02 19:30
