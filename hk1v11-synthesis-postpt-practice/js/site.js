/* HK1V11 synthesis/postpt practice site — shared page logic
   navbar + markdown render + TOC + prev/next page nav */
(function () {
  'use strict';

  /* 顶部导航：平铺项 + 两个 hover 下拉组（排障/复盘/学习子章收进下拉，不占顶部）
     item 形态：['file.html', '标签'] 平铺；{ label, href, children: [[file, 标签], ...] } 下拉组 */
  var NAV = [
    ['index.html',            '首页'],
    ['ch01-env.html',         '环境与配置'],
    ['ch02-rtl-check.html',   'RTL 检查'],
    ['ch03-synthesis.html',   '综合'],
    ['ch04-lec.html',         'LEC 验证'],
    ['ch05-apr-signoff.html', 'APR SIGNOFF'],
    ['ch06-postpt.html',      'POSTPT'],
    ['ch07-memory-power.html','Memory 与功耗'],
    ['ch08-powerpro.html',    'PowerPro'],
    ['ch09-to-signoff.html',  'TO SIGNOFF'],
    { label: '实战与复盘', href: 'cases.html', children: [
      ['ch10-warstories.html',          '排障实录'],
      ['ch11-violation-atlas.html',     '违例归因'],
      ['ch14-violation-disposition.html','违例处置'],
      ['ch15-memory-jogger.html',       '记忆唤醒'],
      ['ch16-dc1004-review.html',       '1004复核'],
      ['ch17-rtl-1006-sync.html',       '1006同步'],
      ['ch18-skew.html',                'Skew'],
      ['ch19-skew-audit.html',          '10-15 审计']
    ]},
    { label: '学习路径', href: 'learning-path.html', children: [
      ['ch12-constraint-tutorial.html', '约束教学'],
      ['ch13-toolchain-map.html',       '工具链']
    ]}
  ];
  /* 平铺序列表（prev/next 导航用）：下拉组按 父项 → 子章 顺序展开 */
  var FLAT_NAV = [];
  NAV.forEach(function (item) {
    if (typeof item[0] === 'string') { FLAT_NAV.push(item); }
    else {
      FLAT_NAV.push([item.href, item.label]);
      item.children.forEach(function (c) { FLAT_NAV.push(c); });
    }
  });

  function currentPage() {
    return location.pathname.split('/').pop() || 'index.html';
  }

  /* ---------- navbar（两行：一行=平铺章节+搜索，二行=下拉组+GitHub）
     下拉交互：hover 展开（CSS）+ 点 ▾ 钉开/关（JS，触屏可用），点外部 / Esc 关闭 */
  var navBox = document.getElementById('navbar-links');
  if (navBox) {
    var cur = currentPage();
    var rowMain = document.createElement('div');
    rowMain.className = 'nav-row nav-row-main';
    var rowSub = document.createElement('div');
    rowSub.className = 'nav-row nav-row-sub';
    navBox.appendChild(rowMain);
    navBox.appendChild(rowSub);

    function closeDrops(root) {
      root.querySelectorAll('.nav-drop.open').forEach(function (w) {
        w.classList.remove('open');
        var b = w.querySelector('.nav-drop-btn');
        if (b) b.setAttribute('aria-expanded', 'false');
      });
    }

    NAV.forEach(function (item) {
      if (typeof item[0] === 'string') { /* 平铺链接 → 第一行 */
        var a = document.createElement('a');
        a.href = item[0] === 'index.html' ? './' : './' + item[0];
        a.textContent = item[1];
        if (cur === item[0]) a.classList.add('active');
        rowMain.appendChild(a);
        return;
      }
      /* 下拉组 → 第二行：点父项标签进 hub 页；点 ▾ 钉开/关 */
      var wrap = document.createElement('div');
      wrap.className = 'nav-drop';
      var pa = document.createElement('a');
      pa.className = 'nav-drop-btn';
      pa.href = './' + item.href;
      pa.textContent = item.label;
      var caret = document.createElement('span');
      caret.className = 'caret';
      caret.textContent = '▾';
      caret.title = '展开 / 收起';
      pa.appendChild(caret);
      var childActive = cur === item.href;
      item.children.forEach(function (c) { if (cur === c[0]) childActive = true; });
      if (childActive) wrap.classList.add('active-parent');
      var menu = document.createElement('div');
      menu.className = 'nav-drop-menu';
      item.children.forEach(function (c) {
        var a2 = document.createElement('a');
        a2.href = './' + c[0];
        a2.textContent = c[1];
        if (cur === c[0]) a2.classList.add('active');
        menu.appendChild(a2);
      });
      wrap.appendChild(pa);
      wrap.appendChild(menu);
      rowSub.appendChild(wrap);
      pa.setAttribute('aria-expanded', 'false');
      caret.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        var open = wrap.classList.toggle('open');
        pa.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
      menu.addEventListener('click', function () { closeDrops(navBox); }); /* 子项跳走后收起钉开的菜单 */
    });

    document.addEventListener('click', function (e) {
      if (!navBox.contains(e.target)) closeDrops(navBox);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeDrops(navBox);
    });

    /* 第二行右侧：GitHub 仓库入口 */
    var gh = document.createElement('a');
    gh.className = 'nav-gh';
    gh.href = 'https://github.com/ymzhuuuuufz0313l/team-share-public';
    gh.target = '_blank';
    gh.rel = 'noopener';
    gh.innerHTML = 'GitHub';
    rowSub.appendChild(gh);
  }

  /* ---------- markdown render + TOC ---------- */
  var mdEl = document.getElementById('md');
  if (mdEl && document.getElementById('article')) {
    document.getElementById('article').innerHTML = marked.parse(mdEl.textContent);

    var toc = document.getElementById('toc');
    var headings = document.querySelectorAll('.article h2, .article h3');
    var tocLinks = [];
    var h3ToH2 = {};   /* h3 id -> 父 h2 id（折叠组激活时高亮回父级） */
    var usedIds = {};  /* 标题 id 去重（如 ch10 多个同名「现象」小节） */

    /* 标题 id（去重）：首次出现用原名，之后同名追加 -2/-3，锚点语义不变 */
    function makeId(h) {
      var base = h.textContent.trim().replace(/\s+/g, '-').replace(/[^\w\u4e00-\u9fa5-]/g, '');
      var id = base, n = 2;
      while (usedIds[id]) { id = base + '-' + n; n++; }
      usedIds[id] = true;
      return id;
    }
    headings.forEach(function (h) { h.id = makeId(h); });

    /* 页标题作为左侧目录的第一条（对齐 cpuwr / longcode 站的 toc-h1 形式） */
    var pageH1 = document.querySelector('.article h1');
    if (pageH1) {
      var t1 = document.createElement('a');
      t1.className = 'toc-h1';
      t1.href = '#';
      t1.textContent = pageH1.textContent;
      t1.addEventListener('click', function (e) { e.preventDefault(); window.scrollTo({ top: 0, behavior: 'smooth' }); });
      toc.appendChild(t1);
    }

    /* h2/h3 层级缩进：带 h3 子标题的 h2 挂 ▸ 箭头（点击折叠/展开），h3 缩进成组跟随 */
    headings.forEach(function (h, i) {
      if (h.tagName !== 'H2') return;
      var children = [];
      var j = i + 1;
      while (j < headings.length && headings[j].tagName === 'H3') { children.push(headings[j]); j++; }

      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.className = 'toc-h2' + (children.length > 0 ? ' toc-parent' : '');
      toc.appendChild(a);
      tocLinks.push(a);
      if (children.length === 0) return;

      var group = document.createElement('div');
      group.className = 'toc-h3-group';
      group.setAttribute('data-parent', h.id);
      children.forEach(function (c) {
        h3ToH2[c.id] = h.id;
        var link = document.createElement('a');
        link.href = '#' + c.id;
        link.textContent = c.textContent;
        link.className = 'toc-h3';
        group.appendChild(link);
        tocLinks.push(link);
      });
      toc.appendChild(group);

      var arrow = document.createElement('span');
      arrow.className = 'toc-arrow';
      arrow.textContent = '▸';
      a.insertBefore(arrow, a.firstChild);
      arrow.addEventListener('click', function (e) {
        e.preventDefault(); /* 箭头 = 折叠/展开，不跳转 */
        var nowCollapsed = a.classList.toggle('collapsed');
        group.classList.toggle('collapsed', nowCollapsed);
        if (nowCollapsed) { /* 折叠时高亮移回父 h2 */
          var activeInGroup = group.querySelector('a.active');
          if (activeInGroup) {
            activeInGroup.classList.remove('active');
            a.classList.add('active');
          }
        }
      });
    });

    if (window.IntersectionObserver) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var targetId = entry.target.id;
          var parentId = h3ToH2[targetId];
          if (parentId) {
            var group = toc.querySelector('.toc-h3-group[data-parent="' + parentId + '"]');
            if (group && group.classList.contains('collapsed')) targetId = parentId;
          }
          tocLinks.forEach(function (l) { l.classList.remove('active'); });
          var active = tocLinks.find(function (x) { return x.getAttribute('href') === '#' + targetId; });
          if (active) active.classList.add('active');
        });
      }, { rootMargin: '-10% 0px -75% 0px' });
      headings.forEach(function (h) { observer.observe(h); });
    }
  }

  /* ---------- prev / next page nav ---------- */
  var pageNav = document.getElementById('page-nav');
  if (pageNav) {
    var cur = currentPage();
    var i = FLAT_NAV.findIndex(function (p) { return p[0] === cur; });
    if (i >= 0) {
      var html = '';
      if (i > 0) {
        html += '<a class="prev" href="./' + FLAT_NAV[i - 1][0] + '"><span class="label">&larr; 上一篇</span><span class="title">' + FLAT_NAV[i - 1][1] + '</span></a>';
      }
      if (i < FLAT_NAV.length - 1) {
        html += '<a class="next" href="./' + FLAT_NAV[i + 1][0] + '"><span class="label">下一篇 &rarr;</span><span class="title">' + FLAT_NAV[i + 1][1] + '</span></a>';
      }
      pageNav.innerHTML = html;
    }
  }
  /* ---------- image lightbox（全站图片点击放大，js/lightbox.js） ---------- */
  var lb = document.createElement('script');
  lb.src = './js/lightbox.js';
  document.head.appendChild(lb);
  /* ---------- site search（全站搜索，根目录 search.js + search-index.js） ---------- */
  var ss = document.createElement('script');
  ss.src = './search.js';
  document.head.appendChild(ss);
})();

// ymzhu 2026-10-19 17:52
