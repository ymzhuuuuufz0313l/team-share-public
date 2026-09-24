/* HK1V11 synthesis/postpt practice site — shared page logic
   navbar + markdown render + TOC + prev/next page nav */
(function () {
  'use strict';

  var CHAPTERS = [
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
    ['ch10-warstories.html',  '排障实录']
  ];

  function currentPage() {
    return location.pathname.split('/').pop() || 'index.html';
  }

  /* ---------- navbar ---------- */
  var navBox = document.getElementById('navbar-links');
  if (navBox) {
    var cur = currentPage();
    CHAPTERS.forEach(function (pair) {
      var a = document.createElement('a');
      a.href = pair[0] === 'index.html' ? './' : './' + pair[0];
      a.textContent = pair[1];
      if (cur === pair[0]) a.classList.add('active');
      navBox.appendChild(a);
    });
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
    var i = CHAPTERS.findIndex(function (p) { return p[0] === cur; });
    if (i >= 0) {
      var html = '';
      if (i > 0) {
        html += '<a class="prev" href="./' + CHAPTERS[i - 1][0] + '"><span class="label">&larr; 上一篇</span><span class="title">' + CHAPTERS[i - 1][1] + '</span></a>';
      }
      if (i < CHAPTERS.length - 1) {
        html += '<a class="next" href="./' + CHAPTERS[i + 1][0] + '"><span class="label">下一篇 &rarr;</span><span class="title">' + CHAPTERS[i + 1][1] + '</span></a>';
      }
      pageNav.innerHTML = html;
    }
  }
})();

// ymzhu 2026-09-24 16:45
