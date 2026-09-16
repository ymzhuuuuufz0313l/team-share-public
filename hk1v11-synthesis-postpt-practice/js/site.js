/* HK1V11 synthesis/postpt practice site — shared page logic
   navbar + markdown render + TOC + prev/next page nav */
(function () {
  'use strict';

  var CHAPTERS = [
    ['index.html',            '首页'],
    ['ch01-env.html',         '一 环境与配置'],
    ['ch02-rtl-check.html',   '二 RTL 检查'],
    ['ch03-synthesis.html',   '三 综合'],
    ['ch04-lec.html',         '四 LEC 验证'],
    ['ch05-apr-signoff.html', '五 APR SIGNOFF'],
    ['ch06-postpt.html',      '六 POSTPT'],
    ['ch07-memory-power.html','七 Memory 与功耗'],
    ['ch08-powerpro.html',    '八 PowerPro'],
    ['ch09-to-signoff.html',  '九 TO SIGNOFF'],
    ['ch10-warstories.html',  '十 排障实录']
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

    headings.forEach(function (h) {
      var id = h.textContent.trim().replace(/\s+/g, '-').replace(/[^\w\u4e00-\u9fa5-]/g, '');
      h.id = id;
      var a = document.createElement('a');
      a.href = '#' + id;
      a.textContent = h.textContent;
      a.className = h.tagName === 'H2' ? 'toc-h2' : 'toc-h3';
      toc.appendChild(a);
      tocLinks.push(a);
    });

    if (window.IntersectionObserver) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          tocLinks.forEach(function (l) { l.classList.remove('active'); });
          var active = tocLinks.find(function (a) { return a.getAttribute('href') === '#' + entry.target.id; });
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
