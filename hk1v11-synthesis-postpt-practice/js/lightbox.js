/* HK1V11 site — 图片查看器（lightbox v2）
   全站共用：正文/表格/详情内任意 <img> 点击后全屏查看。
   滚轮以光标为锚点缩放（0.5–12×）；按住拖动平移；双击复位（或按 0）；
   ←/→ 在同页图片间切换；ESC / × / 点击遮罩空白处关闭。
   由 site.js 动态加载。 */
(function () {
  'use strict';
  if (window.__HK11_LIGHTBOX) return;   /* 防重复初始化 */
  window.__HK11_LIGHTBOX = true;

  var overlay = document.createElement('div');
  overlay.className = 'lb-overlay';
  overlay.innerHTML =
    '<button class="lb-close" title="关闭 (ESC)">&times;</button>' +
    '<button class="lb-prev" title="上一张 (&larr;)">&#8249;</button>' +
    '<img class="lb-img" alt="" draggable="false">' +
    '<button class="lb-next" title="下一张 (&rarr;)">&#8250;</button>' +
    '<div class="lb-cap"></div>';
  document.body.appendChild(overlay);

  var img = overlay.querySelector('.lb-img');
  var cap = overlay.querySelector('.lb-cap');
  var list = [];   /* 当前页可放大图片 src 列表 */
  var idx = 0;

  /* 缩放/平移状态：transform = translate(tx,ty) scale(s)，origin 0 0 */
  var s = 1, tx = 0, ty = 0;
  function apply() {
    img.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + s + ')';
    var label = (list[idx] && list[idx].alt) ? list[idx].alt + ' · ' : '';
    cap.textContent = label + Math.round(s * 100) + '%' +
      '　滚轮缩放 · 拖动平移 · 双击复位 · ESC 关闭';
  }
  function reset() { s = 1; tx = 0; ty = 0; apply(); }

  function collect() {
    list = [];
    document.querySelectorAll('.article img, .content img').forEach(function (im) {
      list.push({ src: im.getAttribute('src'), alt: im.alt || '' });
      im.classList.add('lb-zoomable');
      /* 包 .lb-thumb：hover 显示 🔍 角标（UI 审 t61 可发现性） */
      if (im.parentNode && !im.parentNode.classList.contains('lb-thumb')) {
        var w = document.createElement('span');
        w.className = 'lb-thumb';
        im.parentNode.insertBefore(w, im);
        w.appendChild(im);
      }
    });
  }

  function show(i) {
    if (!list.length) return;
    idx = (i + list.length) % list.length;
    img.src = list[idx].src;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
    reset();
  }

  function hide() {
    overlay.classList.remove('open');
    img.src = '';
    img.style.transform = '';
    document.body.style.overflow = '';
  }

  /* ---------- 锚点缩放核心：光标/双指中点下的点缩放前后不动 ---------- */
  function zoomAt(cx, cy, f) {
    var ns = Math.min(12, Math.max(0.5, s * f));
    if (ns === s) return;
    var lx = img.offsetLeft, ly = img.offsetTop;   /* 布局位置，不受 transform 影响 */
    var ix = (cx - lx - tx) / s;
    var iy = (cy - ly - ty) / s;
    tx = cx - lx - ix * ns;
    ty = cy - ly - iy * ns;
    s = ns;
    apply();
  }

  /* ---------- 滚轮缩放（以光标为锚点） ---------- */
  overlay.addEventListener('wheel', function (e) {
    if (!overlay.classList.contains('open')) return;
    e.preventDefault();
    zoomAt(e.clientX, e.clientY, e.deltaY < 0 ? 1.2 : 1 / 1.2);
  }, { passive: false });

  /* ---------- 指针交互：单指/鼠标拖动平移 + 双指捏合缩放（缓办项实施） ---------- */
  var drag = null;
  var pointers = new Map();   /* pointerId -> {x,y} */
  var pinchDist = 0;
  img.addEventListener('pointerdown', function (e) {
    if (e.button !== 0) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    img.setPointerCapture(e.pointerId);
    if (pointers.size === 1) {
      drag = { x: e.clientX, y: e.clientY, tx0: tx, ty0: ty };
      img.classList.add('grabbing');
    } else {          /* 第二指落下 → 结束拖动，进入捏合 */
      drag = null;
      img.classList.remove('grabbing');
      pinchDist = 0;
    }
    e.preventDefault();
  });
  img.addEventListener('pointermove', function (e) {
    if (!pointers.has(e.pointerId)) return;
    pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (pointers.size >= 2) {
      var pts = Array.from(pointers.values());
      var d = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
      if (pinchDist > 0 && d > 0) zoomAt((pts[0].x + pts[1].x) / 2, (pts[0].y + pts[1].y) / 2, d / pinchDist);
      pinchDist = d;
      return;
    }
    if (!drag) return;
    tx = drag.tx0 + (e.clientX - drag.x);
    ty = drag.ty0 + (e.clientY - drag.y);
    apply();
  });
  function endPtr(e) {
    pointers.delete(e.pointerId);
    if (pointers.size < 2) pinchDist = 0;
    if (pointers.size === 1) {        /* 剩单指：重置拖动基线防跳变 */
      var p = Array.from(pointers.values())[0];
      drag = { x: p.x, y: p.y, tx0: tx, ty0: ty };
    } else if (pointers.size === 0) {
      drag = null;
      img.classList.remove('grabbing');
    }
  }
  img.addEventListener('pointerup', endPtr);
  img.addEventListener('pointercancel', endPtr);

  /* ---------- 双击复位 ---------- */
  img.addEventListener('dblclick', function (e) { e.preventDefault(); reset(); });

  /* ---------- 关闭：ESC / × / 点遮罩空白（点图片本体不关闭） ---------- */
  overlay.addEventListener('click', function (e) { if (e.target === overlay) hide(); });
  overlay.querySelector('.lb-close').addEventListener('click', hide);
  overlay.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(idx - 1); });
  overlay.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(idx + 1); });
  document.addEventListener('keydown', function (e) {
    if (!overlay.classList.contains('open')) return;
    if (e.key === 'Escape') hide();
    else if (e.key === 'ArrowLeft') show(idx - 1);
    else if (e.key === 'ArrowRight') show(idx + 1);
    else if (e.key === '0') reset();
  });

  /* ---------- 事件委托：正文渲染完（marked）后新增的图也能点 ---------- */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t && t.tagName === 'IMG' && !overlay.classList.contains('open')) {
      collect();
      var i = list.findIndex(function (x) { return x.src === t.getAttribute('src'); });
      if (i >= 0) { e.preventDefault(); show(i); }
    }
  });

  collect();
})();
// ymzhu 2026-10-21 12:08
