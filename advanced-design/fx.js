/* fx.js — PAGE FX v1 特效引擎（2026-10-28 ymzhu，v4 零重载切换架构）
   接管原内联 IIFE 的全部职责（模式解析 / #motionToggle / img src 交换 / 滚动重播）
   + 页面级特效：滚动进度条 / 滚动显现 / 蓝图底纹 / 导航阴影 / 返回顶部 /
     hero 网格漂移与光晕 / 标题字级升起（逐字 assert）/ 数字滚动 / 表格行级联 / 章节标题画线。
   v4 = blueprint-ui-style skill「动画/静态双版 SVG 站点架构 v4」§2 运行时切换契约（治切换错位/闪跳）：
     ① 布局锁定：SVG img 加载完成即写 aspect-ratio + width:100%/height:auto，此后任何
        src 变化盒子尺寸恒定 → 切换零位移；② 预载后交换：先 new Image() 预载目标版，
        onload 才赋 img.src（onerror 保持原 src 防断图），全程禁止 ?v=时间戳 强刷；
     (v4.1) scroll replay = same-src reassign (restart animations, zero network, node unchanged). Old clone-node approach dropped: replacing the node lost external listeners (lightbox zoom broke).
   纯原生、零依赖；隐藏基态 CSS 全部由 html.fx-on 前缀控制（无 JS = 完整静态页面），
   静态模式 = fx-on 移除 + page-static kill 块双保险。 */
(function () {
  'use strict';

  var root = document.documentElement;

  /* ===================== 1. 模式解析（原 IIFE 逻辑原样保留） =====================
     优先级：URL ?motion=static|anim > sessionStorage('motion-mode') > prefers-reduced-motion > anim；默认一律动画模式（2026-10-28 定稿：选择仅会话内记忆，关浏览器即重置为动画） */
  var mq = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : null;
  var param = new URLSearchParams(location.search).get('motion');
  var stored = null;
  try { stored = sessionStorage.getItem('motion-mode'); } catch (e) {}
  var mode = param === 'static' || param === 'anim' ? param
    : (stored === 'static' || stored === 'anim') ? stored
    : (mq && mq.matches ? 'static' : 'anim');

  var btn = document.getElementById('motionToggle');
  if (!btn) {
    /* 全仓库统一模板（2026-10-28 定稿）：按钮放顶部导航。规则见挂载点：
       横向 .navbar-links -> 内联小胶囊；纵向/下拉式 links（practice 站）-> 绝对定位于
       .navbar 右缘居中（不参与 links 布局，绝不独占一行）；无 .navbar -> 右上角固定兜底。 */
    btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'motionToggle';
    btn.title = '点击切换 动画 / 静态 版本';
    btn.setAttribute('aria-pressed', 'true');
    btn.className = 'navbar-motion';
  }

  /* ===================== 2. SVG img 零重载交换 + 布局锁定 + same-src 重播（v4 契约） =====================
     全站统一 /anim/ 目录约定：页面默认引用动画版；静态模式 = 路径去掉 /anim/ 段。
     首次交换前把原始 src 记入 img.dataset.fxAnim，回程动效模式原样恢复
     （修复 v2 缺陷：静态→动效时把 images/anim/ 错重建为 ./anim/ 导致断图）。
     无 /anim/ 的单文件图（无静态对照）两模式原样保留。
     v4 三铁律（SKILL「动画/静态双版 SVG 站点架构 v4」§2，2026-10-28）：
     a) 布局锁定：加载完成即锁 aspect-ratio，src 任何变化盒子尺寸恒定 → 切换零位移；
     b) 预载后交换：目标版 onload 才落 src，失败保持原 src；全程禁止 ?v=时间戳 强刷；
     (v4.1) scroll replay = same-src reassign (restart animations, zero network, node unchanged). Old clone-node approach dropped: replacing the node lost external listeners (lightbox zoom broke). */
  var svgIo = null;
  function isSvgImg(img) {
    /* 只处理 src 以 .svg 结尾（可带 ?query）的 img */
    return /\.svg(\?|$)/.test(img.getAttribute('src') || '');
  }
  function svgImgs() {
    return Array.prototype.filter.call(document.querySelectorAll('img'), isSvgImg);
  }
  function staticSrcOf(str) {
    /* 去掉 src 中的 /anim/ 段（anim/foo.svg → ./foo.svg；images/anim/foo.svg → images/foo.svg）；无 /anim/ 原样返回 */
    var s2 = (str || '').split('?')[0];
    var idx = s2.indexOf('/anim/');
    if (idx === -1) return s2;
    var prefix = s2.slice(0, idx).replace(/\/+$/, '');
    return (prefix ? prefix + '/' : './') + s2.split('/').pop();
  }
  function animSrcOf(img) {
    if (img.dataset.fxAnim) return img.dataset.fxAnim;
    var s2 = (img.getAttribute('src') || '').split('?')[0];
    img.dataset.fxAnim = s2;
    return s2;
  }
  /* a) 布局锁定：已加载完成（complete && naturalWidth>0）的立即锁；未加载的挂一次性
        load 后锁（listener 挂在元素上，中途换 src 不丢失）。静态/动画两版同 viewBox，
        比例一致 → 盒子在任何 src 变化下恒定，零位移。 */
  function lockBox(img) {
    if (img.dataset.fxLocked === '1') return;
    if (!(img.complete && img.naturalWidth > 0)) return;
    img.style.aspectRatio = img.naturalWidth + '/' + img.naturalHeight;
    img.style.width = '100%';
    img.style.height = 'auto';
    img.dataset.fxLocked = '1';
  }
  function armLock(img) {
    if (img.complete && img.naturalWidth > 0) { lockBox(img); return; }
    img.addEventListener('load', function () { lockBox(img); }, { once: true });
  }
  /* b) 预载后交换：new Image() 先把目标版拉进缓存，onload 后才赋 img.src（缓存命中时
        即时，无空白窗口）；onerror 保持原 src 不动（防断图）。__fxWant 记录最新意图，
        预载期间模式又切走则放弃过期写入。目标与当前 src 相同（含初始化 anim 模式）则
        完全不动 → 页面加载即播的动画不被打断。全程禁止 Date.now()/随机数 query。 */
  function swapSrc(img, target) {
    img.__fxWant = target;
    if ((img.getAttribute('src') || '').split('?')[0] === target) return;
    var pre = new Image();
    pre.onload = function () {
      if (img.__fxWant === target && (img.getAttribute('src') || '').split('?')[0] !== target) {
        img.src = target;
      }
    };
    pre.onerror = function () { /* 目标版缺失/不可读：保持原 src */ };
    pre.src = target;
  }
  function applySvg() {
    svgImgs().forEach(function (img) {
      img.loading = 'lazy';
      armLock(img);
      var a = animSrcOf(img);
      swapSrc(img, (mode === 'anim') ? a : staticSrcOf(a));
    });
    observe();
  }
  /* c) 滚动重播：rootMargin 240px 沿用。图片进入视口且当前是 anim 模式且尚未播过入场
        -> img.src = img.src: same-value reassign restarts CSS animations (zero network, node kept, listeners survive).
        dataset.fxPlayed 防重复：触发前打标，标记随克隆体延续；首屏内图片不重播（页面
        加载时动画本就在跑）；static 模式不注册 observer。 */
  function observe() {
    if (svgIo) { svgIo.disconnect(); svgIo = null; }
    if (mode !== 'anim') return;
    svgIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        svgIo.unobserve(e.target);
        var img = e.target;
        if (mode !== 'anim' || img.dataset.fxPlayed === '1') return;
        img.dataset.fxPlayed = '1';
        /* 同元素重播：aspect-ratio 锁在元素 style 上，src 重赋值不丢，无需重挂 */
        img.src = img.src;  /* v4.1: same-src reassign restarts in-SVG animations; node & external listeners (lightbox) survive; zero network */
      });
    }, { rootMargin: '240px 0px' });
    svgImgs().forEach(function (img) {
      if (img.dataset.fxPlayed === '1') return;
      var r = img.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) {
        img.dataset.fxPlayed = '1'; /* 首屏内：初始加载即播，不重播 */
        return;
      }
      svgIo.observe(img);
    });
  }
  /* ===================== 3. 滚动进度条 / 导航阴影 / 返回顶部（rAF 节流） ===================== */
  var progress = document.createElement('div');
  progress.id = 'fx-progress';
  var topBtn = document.createElement('button');
  topBtn.type = 'button';
  topBtn.id = 'fx-top';
  topBtn.title = '返回顶部';
  topBtn.setAttribute('aria-label', '返回顶部');
  topBtn.textContent = '\u2191';
  var navbar = document.querySelector('.navbar');
  var ticking = false;

  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () {
      ticking = false;
      var st = window.pageYOffset || root.scrollTop || 0;
      var max = Math.max(1, root.scrollHeight - window.innerHeight);
      progress.style.transform = 'scaleX(' + Math.min(1, st / max) + ')';
      if (navbar) navbar.classList.toggle('scrolled', st > 10);
      topBtn.classList.toggle('show', st > 600);
    });
  }

  /* ===================== 4. 滚动显现标记 + 表格行级联 + 章节标题画线 ===================== */
  var REVEAL_SEL = [
    '#article h2', '#article h3', '#article table', '#article figure',
    'main h2', 'main h3', 'main table', 'main figure',
    '.container h2', '.container h3', '.container table', '.container figure',
    '.article > p:first-of-type', '.stat', '.hero-hint', '.page-nav a'
  ];
  var revealEls = [];
  var revIo = null;

  function markReveals() {
    var els = [];
    REVEAL_SEL.forEach(function (sel) {
      Array.prototype.forEach.call(document.querySelectorAll(sel), function (el) {
        if (els.indexOf(el) === -1) els.push(el);
      });
    });
    els.forEach(function (el) {
      el.classList.add('fx-r');
      if (el.tagName === 'TABLE') {
        el.classList.add('fx-t');
        /* 行级联：表头行 delay 0，正文行 0.03s × i，上限 0.9s */
        var rows = el.rows;
        for (var i = 0; i < rows.length; i++) {
          var d = rows[i].querySelector('th') ? 0 : Math.min(0.03 * i, 0.9);
          rows[i].style.transitionDelay = d + 's';
        }
      }
      if (el.tagName === 'H2') {
        /* 已有 ::before 装饰的 h2 整体跳过 fx-hdr，避免双重装饰 */
        var cs = window.getComputedStyle(el, '::before');
        var c = cs ? cs.getPropertyValue('content') : 'none';
        if (!c || c === 'none' || c === 'normal') el.classList.add('fx-hdr');
      }
    });
    /* hero meta 行 chips 与 hero badge：fx-r + 0.1s 递增 delay（不存在则自然跳过） */
    var chips = document.querySelectorAll('.hero .meta > *, .hero .badge');
    Array.prototype.forEach.call(chips, function (chip, i) {
      chip.classList.add('fx-r');
      chip.style.transitionDelay = (0.1 * (i + 1)) + 's';
      els.push(chip);
    });
    return els;
  }

  function startReveals() {
    if (revIo) { revIo.disconnect(); revIo = null; }
    if (mode !== 'anim') return;
    revIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        revIo.unobserve(e.target);
        e.target.classList.add('fx-in');
      });
    }, { rootMargin: '120px 0px' });
    revealEls.forEach(function (el) {
      var r = el.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) {
        /* 加载时已在视口：rAF 后直接 fx-in，让 transition 播放入场 */
        requestAnimationFrame(function () { el.classList.add('fx-in'); });
      } else {
        revIo.observe(el);
      }
    });
  }

  /* ===================== 5. hero 标题字级升起（拆 span + 逐字 assert） ===================== */
  var heroH1 = null, heroHTML = null, heroText = null;

  function splitHero() {
    if (!heroH1 || heroHTML === null) return;
    heroH1.innerHTML = heroHTML; /* 每次从原文重建，支持重复重播 */
    var nodes = Array.prototype.slice.call(heroH1.childNodes);
    heroH1.textContent = '';
    var idx = 0;
    nodes.forEach(function (node) {
      if (node.nodeType !== 3) { heroH1.appendChild(node); return; } /* <br>/<span> 原样保留 */
      var text = node.nodeValue;
      var re = /[A-Za-z0-9]+|[\u3400-\u9fff\uf900-\ufaff\u3001-\u303f\uff01-\uff5e]/g;
      var m, last = 0, piece;
      while ((m = re.exec(text)) !== null) {
        if (m.index > last) heroH1.appendChild(document.createTextNode(text.slice(last, m.index)));
        piece = document.createElement('span');
        piece.className = 'fx-w';
        piece.textContent = m[0];
        piece.style.animationDelay = (0.06 * idx) + 's';
        idx++;
        heroH1.appendChild(piece);
        last = m.index + m[0].length;
      }
      if (last < text.length) heroH1.appendChild(document.createTextNode(text.slice(last)));
    });
    /* 铁律 assert：拆分后可见文本必须与原文逐字相等；不等则整体还原 */
    if (heroH1.textContent !== heroText) {
      heroH1.innerHTML = heroHTML;
      if (window.console) console.warn('[fx] hero split assert failed, restored original');
    }
  }

  /* ===================== 6. 数字滚动（结束值 = 原值） ===================== */
  var statEls = [], statHTML = [], numEpoch = 0;

  function stopNums() {
    numEpoch++;
    statEls.forEach(function (v, i) { v.innerHTML = statHTML[i]; });
  }

  function runNums() {
    var epoch = numEpoch;
    statEls.forEach(function (v, cardIdx) {
      /* "0720v1" 这类数字+字母后缀：跳过滚动（卡片仍走 reveal） */
      if (/^\d+[A-Za-z]/.test((v.textContent || '').trim())) return;
      Array.prototype.slice.call(v.childNodes).forEach(function (node) {
        if (node.nodeType !== 3) return; /* <em>/</em> 等结构原样保留 */
        var text = node.nodeValue;
        var re = /\d+/g, m, last = 0, parts = [];
        while ((m = re.exec(text)) !== null) {
          if (m.index > last) parts.push({ t: text.slice(last, m.index) });
          parts.push({ n: m[0] });
          last = m.index + m[0].length;
        }
        if (!parts.length) return;
        if (last < text.length) parts.push({ t: text.slice(last) });
        var frag = document.createDocumentFragment();
        parts.forEach(function (p) {
          if (p.t !== undefined) { frag.appendChild(document.createTextNode(p.t)); return; }
          var s = document.createElement('span');
          s.className = 'fx-n';
          s.textContent = '0';
          frag.appendChild(s);
          animateNum(s, p.n, cardIdx * 120, epoch);
        });
        v.replaceChild(frag, node);
      });
    });
  }

  function animateNum(el, targetStr, delayMs, epoch) {
    var target = parseInt(targetStr, 10) || 0;
    var dur = 900, start = null;
    function step(ts) {
      if (epoch !== numEpoch) return; /* 模式已切换/重置：停止写入（DOM 已还原） */
      if (start === null) start = ts;
      var p = Math.max(0, Math.min(1, (ts - start - delayMs) / dur));
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = String(Math.round(target * eased));
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = targetStr; /* 结束值 = 原值（含前导零等原样） */
    }
    requestAnimationFrame(step);
  }

  /* ===================== 7. 模式应用 / 一键切换 / 全量重放 ===================== */
  function applyMode(replay) {
    root.classList.toggle('fx-on', mode === 'anim');
    root.classList.toggle('page-static', mode === 'static');
    if (btn) {
      btn.textContent = mode === 'anim' ? '\ud83c\udfac 动效' : '\ud83d\uDDBC 静态';
      btn.setAttribute('aria-pressed', mode === 'anim' ? 'true' : 'false');
    }
    applySvg();
    /* 页面特效重置（还原数字与 hero 原文）后重新入场 */
    stopNums();
    revealEls.forEach(function (el) { el.classList.remove('fx-in'); });
    if (heroH1 && heroHTML !== null) heroH1.innerHTML = heroHTML;
    if (mode === 'anim') {
      splitHero();
      runNums();
      startReveals();
    }
  }

  /* ===================== 8. 初始化（body 末尾；marked.parse 已同步完成） ===================== */
  function init() {
    heroH1 = document.querySelector('.hero h1');
    if (heroH1) {
      heroHTML = heroH1.innerHTML;
      heroText = heroH1.textContent;
    }
    statEls = Array.prototype.slice.call(document.querySelectorAll('.stat .v'));
    statHTML = statEls.map(function (v) { return v.innerHTML; });

    document.body.appendChild(progress);
    if (btn && !btn.parentNode) {
      var nav = document.querySelector('.navbar');
      var links = document.querySelector('.navbar-links');
      var rowLinks = false;
      if (links) {
        try { rowLinks = /row/.test(getComputedStyle(links).flexDirection || ''); } catch (e) {}
      }
      if (rowLinks) {
        links.appendChild(btn);              /* 横向导航：内联胶囊 */
      } else if (nav) {
        try { if (getComputedStyle(nav).position === 'static') nav.style.position = 'relative'; } catch (e) {}
        btn.classList.add('navbar-abs');     /* 纵向/下拉式导航：绝对定位于导航条右缘 */
        nav.appendChild(btn);
      } else {
        btn.className = 'float-motion';      /* 无导航条兜底：右上角固定 */
        document.body.appendChild(btn);
      }
    }
    /* 站点已有自带返回顶部（如 #toTop）时跳过，避免双按钮 */
    if (!document.getElementById('toTop')) {
      document.body.appendChild(topBtn);
      topBtn.addEventListener('click', function () {
        window.scrollTo({ top: 0, behavior: mode === 'anim' ? 'smooth' : 'auto' });
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });

    if (btn) btn.addEventListener('click', function () {
      mode = (mode === 'anim') ? 'static' : 'anim';
      try { sessionStorage.setItem('motion-mode', mode); } catch (e) {}
      applyMode(true);
    });

    revealEls = markReveals();
    applyMode(false);
    onScroll();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

/* ymzhu 2026-10-28 15:42 */
