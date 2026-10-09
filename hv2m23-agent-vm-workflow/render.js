// shared renderer: markdown -> article, TOC (collapsible + scrollspy), lightbox
(function () {
  var mdEl = document.getElementById('md');
  var art = document.getElementById('article');
  if (!mdEl || !art) return;
  var md = mdEl.textContent;
  art.innerHTML = marked.parse(md);

  // heading ids
  var hCounter = { h2: 0 };
  art.querySelectorAll('h2, h3').forEach(function (h) {
    var txt = h.textContent.trim().replace(/\s+/g, '-').replace(/[^\w\u4e00-\u9fff.-]/g, '');
    h.id = 'h-' + txt.toLowerCase().slice(0, 40) + '-' + Math.random().toString(36).slice(2, 6);
  });

  // TOC
  var toc = document.getElementById('toc');
  if (toc) {
    var headings = art.querySelectorAll('h2, h3');
    headings.forEach(function (h) {
      var a = document.createElement('a');
      a.href = '#' + h.id;
      a.textContent = h.textContent;
      a.className = h.tagName === 'H2' ? 'toc-h2' : 'toc-h3';
      toc.appendChild(a);
    });
    var links = Array.from(toc.querySelectorAll('a'));
    links.forEach(function (link, i) {
      if (!link.classList.contains('toc-h2')) return;
      var children = [];
      for (var j = i + 1; j < links.length && links[j].classList.contains('toc-h3'); j++) children.push(links[j]);
      if (!children.length) return;
      link.classList.add('toc-parent');
      var arrow = document.createElement('span');
      arrow.className = 'toc-arrow'; arrow.textContent = '▸';
      link.prepend(arrow);
      children.forEach(function (c) { c.parentLink = link; });
      arrow.addEventListener('click', function (e) {
        e.preventDefault(); e.stopPropagation();
        var collapsed = link.classList.toggle('collapsed');
        children.forEach(function (c) { c.style.display = collapsed ? 'none' : ''; });
      });
    });
    var tocLinks = links;
    window.addEventListener('scroll', function () {
      var current = null;
      headings.forEach(function (h) { if (h.getBoundingClientRect().top < 90) current = h.id; });
      tocLinks.forEach(function (a) { a.classList.remove('active'); });
      if (current) {
        var active = tocLinks.find(function (a) { return a.getAttribute('href') === '#' + current; });
        if (active && active.style.display === 'none' && active.parentLink) active = active.parentLink;
        if (active) active.classList.add('active');
      }
    });
  }

  // lightbox
  var lb = document.getElementById('lightbox');
  if (lb) {
    var lbImg = document.getElementById('lightbox-img');
    var lbClose = document.getElementById('lightbox-close');
    var scale = 1, tx = 0, ty = 0, dragging = false, sx = 0, sy = 0, itx = 0, ity = 0;
    function upd() { lbImg.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')'; }
    function reset() { scale = 1; tx = 0; ty = 0; upd(); }
    function openLb(src) { lbImg.src = src; reset(); lb.classList.add('active'); document.body.style.overflow = 'hidden'; }
    function closeLb() { lb.classList.remove('active'); document.body.style.overflow = ''; setTimeout(function () { lbImg.src = ''; }, 250); }
    art.querySelectorAll('img').forEach(function (img) { img.addEventListener('click', function () { openLb(img.src); }); });
    lbClose.addEventListener('click', function (e) { e.stopPropagation(); closeLb(); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    lb.addEventListener('wheel', function (e) { e.preventDefault(); scale = Math.min(Math.max(0.5, scale + (e.deltaY > 0 ? -0.15 : 0.15)), 5); upd(); }, { passive: false });
    lbImg.addEventListener('mousedown', function (e) { e.preventDefault(); dragging = true; lbImg.classList.add('grabbing'); sx = e.clientX; sy = e.clientY; itx = tx; ity = ty; });
    window.addEventListener('mousemove', function (e) { if (!dragging) return; tx = itx + (e.clientX - sx); ty = ity + (e.clientY - sy); upd(); });
    window.addEventListener('mouseup', function () { dragging = false; });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeLb(); });
  }
})();
