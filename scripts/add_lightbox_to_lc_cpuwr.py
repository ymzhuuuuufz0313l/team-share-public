import os
import glob

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sorted(glob.glob(os.path.join(BASE, 'hk1v11-lc-cpuwr-history', '*.html')))

LIGHTBOX_CSS = '''
    /* Image lightbox */
    .lightbox {
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.92);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      visibility: hidden;
      transition: opacity 0.25s ease, visibility 0.25s ease;
      cursor: grab;
    }
    .lightbox.active {
      opacity: 1;
      visibility: visible;
    }
    .lightbox img {
      max-width: none;
      max-height: none;
      border: none;
      border-radius: 4px;
      cursor: grab;
      transform-origin: center center;
      transition: none;
      margin: 0;
    }
    .lightbox img.grabbing { cursor: grabbing; }
    .lightbox .hint {
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      color: rgba(255,255,255,0.7);
      font-size: 13px;
      pointer-events: none;
      user-select: none;
      background: rgba(0,0,0,0.4);
      padding: 6px 14px;
      border-radius: 20px;
    }
    .lightbox .close {
      position: absolute;
      top: 20px;
      right: 24px;
      color: rgba(255,255,255,0.8);
      font-size: 32px;
      line-height: 1;
      cursor: pointer;
      user-select: none;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 50%;
      transition: background 0.2s;
    }
    .lightbox .close:hover { background: rgba(255,255,255,0.15); color: #fff; }
'''

LIGHTBOX_HTML = '''
  <div class="lightbox" id="lightbox">
    <span class="close" id="lightbox-close">&times;</span>
    <img id="lightbox-img" src="" alt="">
    <div class="hint">滚轮缩放 · 拖拽移动 · 点击空白处或右上角关闭</div>
  </div>
'''

LIGHTBOX_JS = '''
  <script>
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightbox-img');
    const lightboxClose = document.getElementById('lightbox-close');
    let scale = 1, translateX = 0, translateY = 0;
    let isDragging = false, startX = 0, startY = 0, initialTranslateX = 0, initialTranslateY = 0;
    function updateTransform() { lightboxImg.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`; }
    function resetTransform() { scale = 1; translateX = 0; translateY = 0; updateTransform(); }
    function openLightbox(src) { lightboxImg.src = src; resetTransform(); lightbox.classList.add('active'); document.body.style.overflow = 'hidden'; }
    function closeLightbox() { lightbox.classList.remove('active'); document.body.style.overflow = ''; setTimeout(() => { lightboxImg.src = ''; }, 250); }
    document.querySelectorAll('.article img').forEach(img => img.addEventListener('click', () => openLightbox(img.src)));
    lightboxClose.addEventListener('click', (e) => { e.stopPropagation(); closeLightbox(); });
    lightbox.addEventListener('click', (e) => { if (e.target === lightbox) closeLightbox(); });
    lightbox.addEventListener('wheel', (e) => { e.preventDefault(); scale = Math.min(Math.max(0.5, scale + (e.deltaY > 0 ? -0.15 : 0.15)), 5); updateTransform(); }, { passive: false });
    lightboxImg.addEventListener('mousedown', (e) => { e.preventDefault(); isDragging = true; lightboxImg.classList.add('grabbing'); startX = e.clientX; startY = e.clientY; initialTranslateX = translateX; initialTranslateY = translateY; });
    window.addEventListener('mousemove', (e) => { if (!isDragging) return; translateX = initialTranslateX + (e.clientX - startX); translateY = initialTranslateY + (e.clientY - startY); updateTransform(); });
    window.addEventListener('mouseup', () => { isDragging = false; lightboxImg.classList.remove('grabbing'); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeLightbox(); });
  </script>
'''

for page in pages:
    with open(page, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'id="lightbox"' in content:
        print(f'Skip (already has lightbox): {os.path.basename(page)}')
        continue

    if '  </style>' not in content:
        print(f'Warning: no </style> in {os.path.basename(page)}')
        continue

    if '  </script>\n</body>' not in content:
        print(f'Warning: expected closing pattern not found in {os.path.basename(page)}')
        continue

    content = content.replace('  </style>', LIGHTBOX_CSS.rstrip() + '\n  </style>', 1)
    content = content.replace('  </script>\n</body>', '  </script>\n' + LIGHTBOX_HTML + LIGHTBOX_JS + '</body>', 1)

    with open(page, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated: {os.path.basename(page)}')
