/* fx.js — PAGE FX v1 特效引擎（2026-10-27 ymzhu）
   接管原内联 IIFE 的全部职责（模式解析 / #motionToggle / img src 交换 / 滚动重播，v2 修复保留）
   + 页面级特效：滚动进度条 / 滚动显现 / 蓝图底纹 / 导航阴影 / 返回顶部 /
     hero 网格漂移与光晕 / 标题字级升起（逐字 assert）/ 数字滚动 / 表格行级联 / 章节标题画线。
   纯原生、零依赖；隐藏基态 CSS 全部由 html.fx-on 前缀控制（无 JS = 完整静态页面），
   静态模式 = fx-on 移除 + page-static kill 块双保险。 */
(function () {
  'use strict';

  var root = document.documentElement;

  /* ===================== 1. 模式解析（原 IIFE 逻辑原样保留） =====================
     优先级：URL ?motion=static|anim > localStorage('motion-mode') > prefers-reduced-motion > anim */
  var mq = window.matchMedia ? matchMedia('(prefers-reduced-motion: reduce)') : null;
  var param = new URLSearchParams(location.search).get('motion');
  var stored = null;
  try { stored = localStorage.getItem('motion-mode'); } catch (e) {}
  var mode = param === 'static' || param === 'anim' ? param
    : (stored === 'static' || stored === 'anim') ? stored
    : (mq && mq.matches ? 'static' : 'anim');

  var btn = document.getElementById('motionToggle');
  var btnFloat = false;
  if (!btn) {
    /* 多站点通用：页面无既有按钮时自动注入（导航链接栏优先，否则浮动按钮） */
    btn = document.createElement('button');
    btn.type = 'button';
    btn.id = 'motionToggle';
    btn.title = '点击切换 动画 / 静态 版本';
    btn.setAttribute('aria-pressed', 'true');
    btnFloat = !document.querySelector('.navbar-links');
    btn.className = btnFloat ? 'float-motion' : 'navbar-motion';
  }

  /* ===================== 2. SVG img src 交换 + 滚动重播（原样搬入） =====================
     anim/ 动画版 ↔ 根目录静态原版（零额外资源）；
     保留 v2 修复：匹配 img[src*=".svg"] 含 query 的写法，不退回 src$= */
  var svgIo = null;
  function nameOf(img) {
    var p = new URL(img.getAttribute('src') || '', location.href).pathname;
    return p.split('/').pop();
  }
  function svgImgs() {
    return Array.prototype.filter.call(document.querySelectorAll('img'), function (img) {
      return /\.svg(\?|$)/.test(img.getAttribute('src') || '');
    });
  }
  function baseAnim(img) {
    var s = img.getAttribute('src') || '';
    var p = new URL(s, location.href).pathname;
    return (p.indexOf('/anim/') !== -1 ? s.split('?')[0] : './anim/' + nameOf(img));
  }
  function staticSrc(img) {
    /* 通用静态回退：去掉 src 中的 /anim/ 段（anim/foo.svg → ./foo.svg；images/anim/foo.svg → images/foo.svg） */
    var s = (img.getAttribute('src') || '').split('?')[0];
    var idx = s.indexOf('/anim/');
    if (idx === -1) return s;
    var prefix = s.slice(0, idx).replace(/\/+$/, '');
    return (prefix ? prefix + '/' : './') + nameOf(img);
  }
  function applySvg(replayNow) {
    svgImgs().forEach(function (img) {
      img.loading = 'lazy';
      img.src = (mode === 'anim')
        ? baseAnim(img) + (replayNow ? '?v=' + Date.now() : '')
        : staticSrc(img);
    });
    observe();
  }
  function observe() {
    if (svgIo) { svgIo.disconnect(); svgIo = null; }
    if (mode !== 'anim') return;
    svgIo = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        svgIo.unobserve(e.target);
        if (mode === 'anim') e.target.src = baseAnim(e.target) + '?v=' + Date.now();
      });
    }, { rootMargin: '240px 0px' });
    svgImgs().forEach(function (img) {
      var r = img.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) return;
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
    applySvg(replay);
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
      (btnFloat ? document.body : document.querySelector('.navbar-links')).appendChild(btn);
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
      try { localStorage.setItem('motion-mode', mode); } catch (e) {}
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

/* ymzhu 2026-10-27 15:22 */
