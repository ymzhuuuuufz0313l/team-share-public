/* HK1V11 site — 图片点击放大（lightbox）
   全站共用：正文/表格/详情内任意 <img> 点击后全屏放大查看，
   点击遮罩或按 ESC 关闭；支持 ←/→ 在同页图片间切换。
   由 site.js 动态加载（ch17/index 等未引 site.js 的页面直接 <script> 引入）。 */
(function () {
  'use strict';
  if (window.__HK11_LIGHTBOX) return;   /* 防重复初始化 */
  window.__HK11_LIGHTBOX = true;

  var overlay = document.createElement('div');
  overlay.className = 'lb-overlay';
  overlay.innerHTML =
    '<button class="lb-close" title="关闭 (ESC)">&times;</button>' +
    '<button class="lb-prev" title="上一张 (&larr;)">&#8249;</button>' +
    '<img class="lb-img" alt="">' +
    '<button class="lb-next" title="下一张 (&rarr;)">&#8250;</button>' +
    '<div class="lb-cap"></div>';
  document.body.appendChild(overlay);

  var img = overlay.querySelector('.lb-img');
  var cap = overlay.querySelector('.lb-cap');
  var list = [];   /* 当前页可放大图片 src 列表 */
  var idx = 0;

  function collect() {
    list = [];
    document.querySelectorAll('.article img, .content img').forEach(function (im) {
      list.push({ src: im.getAttribute('src'), alt: im.alt || '' });
      im.classList.add('lb-zoomable');
    });
  }

  function show(i) {
    if (!list.length) return;
    idx = (i + list.length) % list.length;
    img.src = list[idx].src;
    cap.textContent = list[idx].alt;
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function hide() {
    overlay.classList.remove('open');
    img.src = '';
    document.body.style.overflow = '';
  }

  overlay.addEventListener('click', function (e) {
    if (e.target === overlay || e.target.classList.contains('lb-img')) hide();
  });
  overlay.querySelector('.lb-close').addEventListener('click', hide);
  overlay.querySelector('.lb-prev').addEventListener('click', function (e) { e.stopPropagation(); show(idx - 1); });
  overlay.querySelector('.lb-next').addEventListener('click', function (e) { e.stopPropagation(); show(idx + 1); });
  document.addEventListener('keydown', function (e) {
    if (!overlay.classList.contains('open')) return;
    if (e.key === 'Escape') hide();
    else if (e.key === 'ArrowLeft') show(idx - 1);
    else if (e.key === 'ArrowRight') show(idx + 1);
  });

  /* 事件委托：正文渲染完（marked）后新增的图也能点 */
  document.addEventListener('click', function (e) {
    var t = e.target;
    if (t && t.tagName === 'IMG') {
      collect();
      var i = list.findIndex(function (x) { return x.src === t.getAttribute('src'); });
      if (i >= 0) { e.preventDefault(); show(i); }
    }
  });

  collect();
})();
// ymzhu 2026-10-08 12:55
