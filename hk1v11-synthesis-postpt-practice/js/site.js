/* HK1V11 synthesis/postpt practice site — shared page logic
   navbar + markdown render + TOC + prev/next page nav */
(function () {
  'use strict';

  /* 骨架屏兜底：marked CDN 失败时 4s 后强制摘除 .loading，不留永挂占位（复审 t73 #2） */
  setTimeout(function () {
    var a = document.getElementById('article');
    if (a) a.classList.remove('loading');
  }, 4000);

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
      ['ch19-skew-audit.html',          '10-15 审计'],
      ['ch20-half-cycle-mutual-blocking.html', 'Setup-Hold互卡']
      ['ch21-skew-probe-audit.html', '10-28 定案']
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

    /* 移动端导航抽屉：≤768px hamburger（缓办项实施） */
    var burger = document.createElement('button');
    burger.className = 'nav-burger';
    burger.type = 'button';
    burger.setAttribute('aria-label', '菜单');
    burger.setAttribute('aria-expanded', 'false');
    burger.innerHTML = '<span></span><span></span><span></span>';
    document.querySelector('.navbar-inner').appendChild(burger);
    burger.addEventListener('click', function () {
      /* 与 TOC 抽屉互斥（复审 t75） */
      var tocW = document.querySelector('.toc-wrapper');
      if (tocW) tocW.classList.remove('open');
      var open = document.body.classList.toggle('nav-open');
      burger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    navBox.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { document.body.classList.remove('nav-open'); });
    });
    /* 点导航区外任意处关闭抽屉（复审 t75） */
    document.addEventListener('click', function (e) {
      if (!document.body.classList.contains('nav-open')) return;
      var nav = document.querySelector('.navbar');
      if (!nav.contains(e.target)) {
        document.body.classList.remove('nav-open');
        burger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  /* ---------- markdown render + TOC ---------- */
  var mdEl = document.getElementById('md');
  if (mdEl && document.getElementById('article')) {
    var art = document.getElementById('article');
    /* 导语 kicker 豁免页：首个块引用是口径/出处注记而非章节导语（复审 t67） */
    var NO_LEAD = { 'ch03-synthesis.html': 1, 'ch06-postpt.html': 1, 'ch08-powerpro.html': 1 };
    if (NO_LEAD[currentPage()]) art.classList.add('no-lead');
    art.innerHTML = marked.parse(mdEl.textContent);
    art.classList.remove('loading');

    /* 表格增强：滚动容器 + 超长表(>40 行)内部滚动+sticky 表头 + 纯数字列右对齐（UI 审 t62） */
    art.querySelectorAll('table').forEach(function (t) {
      var rows = t.querySelectorAll('tr');
      var wrap = document.createElement('div');
      wrap.className = 'table-wrap' + (rows.length > 40 ? ' table-tall' : '');
      t.parentNode.insertBefore(wrap, t);
      wrap.appendChild(t);
      var cols = rows.length ? rows[0].children.length : 0;
      for (var ci = 0; ci < cols; ci++) {
        var numeric = 0, total = 0;
        rows.forEach(function (r, ri) {
          if (ri === 0 || !r.children[ci]) return;
          total++;
          var txt = (r.children[ci].textContent || '').trim();
          if (txt !== '' && /^[-−+]?[\d,.]+\s*(?:%|MHz|GHz|ns|ps|ms|µs|µW|nW|mW|kW|W|µm²|µm|nm|KB|MB|GB|TB|G|M|k)?$/.test(txt)) numeric++;
        });
        if (total > 0 && numeric / total >= 0.8) {
          rows.forEach(function (r) { if (r.children[ci]) r.children[ci].classList.add('num'); });
        }
      }
    });

    /* 代码块增强：语言标签 + log/text 浅底 + 复制按钮（UI 审 t62） */
    art.querySelectorAll('pre > code').forEach(function (c) {
      var lang = (c.className.match(/language-([\w-]+)/) || [])[1];
      var pre = c.parentNode;
      if (lang) {
        pre.setAttribute('data-lang', (lang === 'text') ? 'log' : lang);
        if (lang === 'text' || lang === 'log') pre.classList.add('log-view');
      }
      var btn = document.createElement('button');
      btn.className = 'code-copy';
      btn.type = 'button';
      btn.textContent = 'copy';
      btn.addEventListener('click', function () {
        var mark = function (txt, ok) {
          btn.textContent = txt;
          btn.classList.toggle('done', !!ok);
          setTimeout(function () { btn.textContent = 'copy'; btn.classList.remove('done'); }, 1600);
        };
        var fallback = function () {   /* 非安全上下文 / 权限拒：execCommand 降级（复审 t70） */
          try {
            var ta = document.createElement('textarea');
            ta.value = c.textContent;
            ta.style.cssText = 'position:fixed;opacity:0';
            document.body.appendChild(ta);
            ta.select();
            var ok = document.execCommand('copy');
            document.body.removeChild(ta);
            mark(ok ? '已复制' : '复制失败', ok);
          } catch (e) { mark('复制失败', false); }
        };
        if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
          navigator.clipboard.writeText(c.textContent).then(function () { mark('已复制', true); }, fallback);
        } else fallback();
      });
      pre.appendChild(btn);
    });

    /* 动画 SVG 滚动重播：长页面里 SVG 多为下方图，一次性入场动画在加载时就播完、用户滚到时看不到
       → 首进视口前 240px 重播（src 加 query 强制 <img> 内 SVG 重新渲染，标准技巧）；
       配合 lazy-load 延迟加载；加载时已在视口内的不重播（入场动画正在自然播放）（2026-10-26 ymzhu） */
    art.querySelectorAll('img[src$=".svg"]').forEach(function (img) {
      var r = img.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) return;
      img.loading = 'lazy';
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          io.unobserve(img);
          var base = (img.getAttribute('src') || '').split('?')[0];
          img.src = base + '?v=' + Date.now();
        });
      }, { rootMargin: '240px 0px' });
      io.observe(img);
    });

    /* mermaid 流程图：marked 把 ```mermaid 渲成 pre>code.language-mermaid
       → 转成 pre.mermaid 交给 mermaid 渲染（站点色板主题）；
       滚动到视口前 240px 加 .play 启动动画：节点阶梯淡入 + 边线画线（一次性 ≤2.5s）
       + 节点接力柔光（infinite 6s，纯装饰，reduced-motion 时整段跳过=完整静态图）（2026-10-26 ymzhu） */
    if (window.mermaid) {
      var mmNodes = [];
      art.querySelectorAll('pre code.language-mermaid').forEach(function (code) {
        var pre = document.createElement('pre');
        pre.className = 'mermaid';
        pre.textContent = code.textContent;
        code.parentElement.replaceWith(pre);
        mmNodes.push(pre);
      });
      if (mmNodes.length) {
        mermaid.initialize({
          startOnLoad: false,
          theme: 'default',
          themeVariables: {
            fontFamily: '"Microsoft YaHei", "PingFang SC", sans-serif',
            fontSize: '15px',
            background: '#f4f1ea',
            primaryColor: '#fffdf7',
            primaryTextColor: '#1c2534',
            primaryBorderColor: '#b45309',
            lineColor: '#5b6675',
            secondaryColor: '#f7e8d4',
            tertiaryColor: '#f4f1ea',
            edgeLabelBackground: '#fffdf7'
          }
        });
        mermaid.run({ nodes: mmNodes }).then(function () {
          var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
          mmNodes.forEach(function (pre) {
            var arm = function () {
              if (reduced) return;
              /* mmRelay 不给 fill-mode：delay 前不生效（否则它会以 0%关键帧 opacity:1 覆盖 mmNode 的淡入）；
                 delay 2.8s 起=入场(≤2s)播完后才接管；周期 8s 容纳 ≤11 节点按序接力（2.8+10*0.45=7.3<8） */
              var i = 0;
              pre.querySelectorAll('g.node').forEach(function (g) {
                g.style.animation = 'mmNode .6s ease-out ' + (0.1 + i * 0.12) + 's both, mmRelay 8s ease-in-out ' + (2.8 + i * 0.45) + 's infinite';
                i++;
              });
              pre.querySelectorAll('.edgePath path, .flowchart-link').forEach(function (p, j) {
                p.style.strokeDasharray = '1400';
                p.style.strokeDashoffset = '1400';
                p.style.animation = 'mmDash .9s ease-out ' + (0.3 + j * 0.12) + 's forwards';
              });
            };
            var r = pre.getBoundingClientRect();
            if (r.top < window.innerHeight && r.bottom > 0) { pre.classList.add('play'); arm(); return; }
            var mio = new IntersectionObserver(function (entries) {
              entries.forEach(function (e) {
                if (!e.isIntersecting) return;
                mio.unobserve(pre);
                pre.classList.add('play');
                arm();
              });
            }, { rootMargin: '240px 0px' });
            mio.observe(pre);
          });
        });
      }
    }

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
          if (active) {
            active.classList.add('active');
            /* TOC 当前项自动滚入视野；用户手动滚目录后 4s 内不打扰（复审 t73 #1） */
            var tocEl = document.getElementById('toc');
            if (tocEl && Date.now() > (tocEl.__userUntil || 0)) {
              tocEl.__progMark = Date.now() + 80;   /* 标记接下来的滚动是程序设置 */
              tocEl.scrollTop = active.offsetTop - tocEl.clientHeight / 2;
            }
          }
        });
      }, { rootMargin: '-10% 0px -75% 0px' });
      headings.forEach(function (h) { observer.observe(h); });
      /* TOC 用户手动滚动检测：程序设置的滚动带 __progMark 标记，其余视为用户操作，4s 内暂停自动滚入 */
      var tocEl0 = document.getElementById('toc');
      if (tocEl0) {
        tocEl0.addEventListener('scroll', function () {
          if (Date.now() > (this.__progMark || 0)) this.__userUntil = Date.now() + 4000;
        }, { passive: true });
      }
    }
  }

  /* ---------- 阅读进度条（UI 审 t58） ---------- */
  var prog = document.createElement('div');
  prog.className = 'read-progress';
  document.body.appendChild(prog);
  var progTick = false;
  window.addEventListener('scroll', function () {
    if (progTick) return;
    progTick = true;
    requestAnimationFrame(function () {
      var de = document.documentElement;
      var max = de.scrollHeight - de.clientHeight;
      prog.style.width = (max > 0 ? (de.scrollTop / max) * 100 : 0) + '%';
      progTick = false;
    });
  }, { passive: true });

  /* ---------- 移动端 TOC 抽屉：≤768px 右下角按钮唤出（UI 审 t64） ---------- */
  var tocWrap = document.querySelector('.toc-wrapper');
  if (tocWrap) {
    var tocBtn = document.createElement('button');
    tocBtn.className = 'toc-toggle';
    tocBtn.type = 'button';
    tocBtn.innerHTML = '<span aria-hidden="true">☰</span> 本页目录';
    document.body.appendChild(tocBtn);
    tocBtn.addEventListener('click', function () {
      document.body.classList.remove('nav-open');   /* 与导航抽屉互斥（复审 t75） */
      tocWrap.classList.toggle('open');
    });
    tocWrap.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { tocWrap.classList.remove('open'); });
    });
    /* 点抽屉外任意处关闭（复审 t72） */
    document.addEventListener('click', function (e) {
      if (!tocWrap.classList.contains('open')) return;
      if (!tocWrap.contains(e.target) && !tocBtn.contains(e.target)) tocWrap.classList.remove('open');
    });
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

// ymzhu 2026-10-26 16:50
