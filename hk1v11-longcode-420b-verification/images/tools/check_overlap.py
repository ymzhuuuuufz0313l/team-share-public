#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_overlap.py — SVG 图版「成图后」全元素对重叠检测门禁（真浏览器渲染度量）

背景：team-share 站点 SVG 图版反复出现文字↔文字 / 文字↔连线 / 文字↔组件重叠（老毛病）。
本工具在图真正被浏览器渲染之后做几何度量（Chrome headless + 逐元素 getBBox /
getExtentOfChar / getPointAtLength + CTM 映射到根 SVG 坐标系），不是对生成器源码的静态推演，
因此能量出「实际渲染出来」的墨迹盒，接住字体度量偏差导致的隐性重叠。

检测三类重叠 + 一组盲区审计：
  A. text↔text   两段文字墨迹盒相交（逐字符级交叉计数，防 bbox 虚警）
  B. text↔stroke 连线（line/path/polyline/polygon 描边）采样点穿过文字墨迹盒；
                  若文字有不透明背景矩形（文档序在连线之后）遮挡则判"有意标签底"
  C. text↔rect   文字跨越矩形边框带（压组件边界）；文字完全在盒内=正常标签不报
  D. audit       文字超出 viewBox（裁切风险）、空文本、字体可用性（tofu 风险提示）

像素级复核（默认开启，--no-pixel-verify 关闭）：对全部 BLOCKER/HIGH 发现做
双掩膜渲染（只渲 A / 只渲 B，DPR 2x），PIL 统计墨迹像素交集或边界带墨迹命中；
几何判级与像素证据矛盾（如 em 盒擦边但墨迹未触）时自动降级为 LOW 并留痕——
相当于可复现的"机器视觉复核"，替代人眼抽查。

输出：
  --json  机器可读全量结果（默认 images/tools/overlap_report_<date>.json）
  --md    人读清单（默认 images/tools/overlap_report_<date>.md）
  --evidence-dir 证据截图目录（每图全页 PNG + BLOCKER/HIGH 发现的放大裁剪 PNG）
  --gate-severity {blocker,high,low,none}  门禁：存在不低于该级别的发现时退出码 1
                                           （默认 none=只产报告不拦截）

用法（幂等，可反复跑；建议接入图版生成流水线末尾）：
  python check_overlap.py                      # 扫描本目录 images/*.svg（静态）
  python check_overlap.py --anim               # 额外扫描 anim/*.svg（冻结在布局终帧）
  python check_overlap.py --files a.svg b.svg  # 指定文件
  python check_overlap.py --gate-severity high # 门禁模式：任何 BLOCKER/HIGH → exit 1

依赖：本机 Chrome / Edge（headless），无第三方 Python 包。
动画 SVG 处理：注入 CSS 将所有动画跳到终态并暂停（animation-delay:-86400s + paused），
度量的是静态布局终帧；流光/呼吸类纯视觉动画不改变几何，不影响结果。
"""

import argparse
import datetime as _dt
import html as _html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEFAULT_REPORT_DATE = _dt.date.today().strftime("%Y%m%d")

# ----------------------------------------------------------------------------
# Chrome 发现
# ----------------------------------------------------------------------------

_CHROME_CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]


def find_chrome(explicit=None):
    for cand in ([explicit] if explicit else []) + _CHROME_CANDIDATES:
        if cand and os.path.isfile(cand):
            return cand
    if explicit:
        raise SystemExit(f"[check_overlap] 指定的浏览器不存在: {explicit}")
    raise SystemExit("[check_overlap] 未找到 Chrome/Edge，请用 --chrome 指定路径")


def chrome_version(chrome):
    try:
        out = subprocess.run([chrome, "--version"], capture_output=True, text=True,
                             timeout=20, creationflags=0x08000000)
        return (out.stdout or out.returncode and "" or "").strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------
# 度量 harness（HTML + JS，Chrome headless --dump-dom 取回 JSON）
# ----------------------------------------------------------------------------

_FREEZE_CSS = (
    "*,*::before,*::after{animation-delay:-86400s!important;"
    "animation-play-state:paused!important;transition:none!important}"
)

_HARNESS_TMPL = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
html,body{margin:0;padding:0;background:#fff}
#target-svg{display:block}
__FREEZE__
</style></head>
<body>
__SVG__
<pre id="__OVERLAP_JSON__" style="display:none"></pre>
<script>
(function(){
  "use strict";
  var svg = document.getElementById('target-svg');
  var NS = 'http://www.w3.org/2000/svg';
  var vb = svg.viewBox && svg.viewBox.baseVal
      ? {x: svg.viewBox.baseVal.x, y: svg.viewBox.baseVal.y,
         w: svg.viewBox.baseVal.width, h: svg.viewBox.baseVal.height}
      : null;

  // ---- 文档序（SVG 无 z-index，文档序即绘制序）----
  var all = svg.querySelectorAll('*');
  var docIdx = new Map();
  for (var i = 0; i < all.length; i++) docIdx.set(all[i], i);

  function inDefs(el){
    for (var p = el; p && p.nodeType === 1; p = p.parentNode)
      { var t = p.tagName; if (t === 'defs' || t === 'marker') return true; }
    return false;
  }
  function isWs(c){ return c === ' ' || c === '\t' || c === '\n' || c === '\r' || c === '\u3000'; }

  // ---- 坐标映射：元素局部坐标 → 根 SVG 用户坐标（viewBox 坐标）----
  function rootMatrix(el){
    var m = el.getScreenCTM(), r = svg.getScreenCTM();
    if (!m || !r) return null;
    try { return r.inverse().multiply(m); } catch(e){ return null; }
  }
  function mapPt(x, y, M){
    var p = svg.createSVGPoint(); p.x = x; p.y = y;
    var q = p.matrixTransform(M); return {x: q.x, y: q.y};
  }
  function mapRect(r, M){ // r={x,y,width,height}（局部）→ 根坐标轴对齐包围盒
    if (!M) return null;
    var ps = [mapPt(r.x, r.y, M), mapPt(r.x + r.width, r.y, M),
              mapPt(r.x, r.y + r.height, M), mapPt(r.x + r.width, r.y + r.height, M)];
    var xs = ps.map(function(p){return p.x}), ys = ps.map(function(p){return p.y});
    return {x: Math.min.apply(null, xs), y: Math.min.apply(null, ys),
            w: Math.max.apply(null, xs) - Math.min.apply(null, xs),
            h: Math.max.apply(null, ys) - Math.min.apply(null, ys)};
  }
  function union(a, b){
    var x1 = Math.min(a.x, b.x), y1 = Math.min(a.y, b.y);
    var x2 = Math.max(a.x + a.w, b.x + b.w), y2 = Math.max(a.y + a.h, b.y + b.h);
    return {x: x1, y: y1, w: x2 - x1, h: y2 - y1};
  }
  function inter(a, b){
    var x1 = Math.max(a.x, b.x), y1 = Math.max(a.y, b.y);
    var x2 = Math.min(a.x + a.w, b.x + b.w), y2 = Math.min(a.y + a.h, b.y + b.h);
    return {x: x1, y: y1, w: x2 - x1, h: y2 - y1};
  }
  function shrink(b, d){
    return {x: b.x + d, y: b.y + d, w: Math.max(0, b.w - 2 * d), h: Math.max(0, b.h - 2 * d)};
  }
  function ptIn(p, b, d){ // d: 内缩容差
    return p.x > b.x + d && p.x < b.x + b.w - d && p.y > b.y + d && p.y < b.y + b.h - d;
  }
  function r1(n){ return Math.round(n * 10) / 10; }
  function box(b){ return {x: r1(b.x), y: r1(b.y), w: r1(b.w), h: r1(b.h)}; }
  function snippet(s, n){ s = (s || '').replace(/\s+/g, ' ').trim(); return s.length > n ? s.slice(0, n) + '…' : s; }

  // ---- 收集文字元素：逐字符墨迹盒（真实 advance + em 高）----
  var texts = [];
  var allTextEls = Array.prototype.slice.call(svg.querySelectorAll('text'));
  var emptyText = 0;
  allTextEls.forEach(function(t){
    if (inDefs(t)) return;
    if (!t.textContent || !t.textContent.trim()) { emptyText++; return; }
    var M = rootMatrix(t);
    if (!M) return;
    var cs = getComputedStyle(t);
    var chars = [];
    try {
      var n = t.getNumberOfChars();
      var s = t.textContent;
      var lead = 0, trail = s.length - 1;
      while (lead < s.length && isWs(s[lead])) lead++;
      while (trail >= 0 && isWs(s[trail])) trail--;
      for (var i = lead; i <= trail; i++){
        if (isWs(s[i])) continue;
        var ext = t.getExtentOfChar(i);          // 本地坐标 {x,y,w,h}
        var cb = mapRect({x: ext.x, y: ext.y, width: ext.width, height: ext.height}, M);
        if (cb) chars.push({ch: s[i], b: cb});
      }
    } catch (e) { chars = []; }
    var ink = null;
    chars.forEach(function(c){ ink = ink ? union(ink, c.b) : c.b; });
    if (!ink) { var bb = t.getBBox(); ink = mapRect({x: bb.x, y: bb.y, width: bb.width, height: bb.height}, M); }
    texts.push({
      di: docIdx.get(t),
      text: snippet(t.textContent, 40),
      ink: ink, chars: chars,
      fontSize: parseFloat(cs.fontSize) || 0,
      fill: cs.fill && cs.fill !== 'none' ? String(cs.fill).slice(0, 24) : null,
      family: cs.fontFamily.slice(0, 80)
    });
  });
  texts.sort(function(a, b){ return a.di - b.di; });

  // ---- 收集形状元素 ----
  var SHAPES = 'rect,line,path,polyline,polygon,circle,ellipse,use';
  var shapes = [];
  Array.prototype.slice.call(svg.querySelectorAll(SHAPES)).forEach(function(el){
    if (inDefs(el)) return;
    var cs = getComputedStyle(el);
    if (cs.display === 'none' || parseFloat(cs.opacity) === 0) return;
    var M = rootMatrix(el); if (!M) return;
    var di = docIdx.get(el);
    var sw = parseFloat(cs.strokeWidth) || 0;
    var hasStroke = cs.stroke && cs.stroke !== 'none' && sw > 0;
    var fill = cs.fill && cs.fill !== 'none' ? String(cs.fill).slice(0, 24) : null;
    var fillOp = (fill && cs.fillOpacity !== '') ? parseFloat(cs.fillOpacity) : 1;
    if (isNaN(fillOp)) fillOp = 1;
    var pts = [];      // 路径采样点（根坐标）
    var closed = null; // 轴对齐盒（rect/use 类）
    var tag = el.tagName;

    try {
      if (tag === 'rect'){
        var bb = el.getBBox();
        closed = mapRect({x: bb.x, y: bb.y, width: bb.width, height: bb.height}, M);
      } else if (tag === 'use'){
        var bu = el.getBBox();
        closed = mapRect({x: bu.x, y: bu.y, width: bu.width, height: bu.height}, M);
      } else if (tag === 'line'){
        var la = mapPt(+el.getAttribute('x1'), +el.getAttribute('y1'), M);
        var lb = mapPt(+el.getAttribute('x2'), +el.getAttribute('y2'), M);
        var llen = Math.hypot(lb.x - la.x, lb.y - la.y);
        var lstep = Math.max(0.7, llen / 600);
        for (var dd = 0; dd <= llen + 1e-6; dd += lstep){
          var lu = Math.min(dd, llen) / (llen || 1);
          pts.push({x: la.x + (lb.x - la.x) * lu, y: la.y + (lb.y - la.y) * lu});
        }
      } else if (tag === 'path'){
        var L = el.getTotalLength();
        if (L > 0){
          var step = Math.max(0.7, L / 6000);
          for (var d = 0; d <= L + 1e-6; d += step){
            var p = el.getPointAtLength(Math.min(d, L));
            var q = mapPt(p.x, p.y, M); pts.push(q);
          }
        }
      } else if (tag === 'polyline' || tag === 'polygon'){
        var raw = (el.getAttribute('points') || '').trim().split(/[\s,]+/).map(parseFloat);
        for (var k = 0; k + 3 < raw.length; k += 2){
          var a = mapPt(raw[k], raw[k + 1], M), b2 = mapPt(raw[k + 2], raw[k + 3], M);
          var seg = Math.hypot(b2.x - a.x, b2.y - a.y), sd = Math.max(0.7, seg / 60);
          for (var u = 0; u <= 1 + 1e-9; u += sd / Math.max(seg, 1e-6))
            pts.push({x: a.x + (b2.x - a.x) * u, y: a.y + (b2.y - a.y) * u});
        }
      } else if (tag === 'circle' || tag === 'ellipse'){
        var cx = +el.getAttribute('cx'), cy = +el.getAttribute('cy');
        var rx = +(el.getAttribute('r') || el.getAttribute('rx')) || 0;
        var ry = +(el.getAttribute('r') || el.getAttribute('ry')) || 0;
        for (var a2 = 0; a2 < Math.PI * 2; a2 += Math.PI / 36){
          var p2 = mapPt(cx + rx * Math.cos(a2), cy + ry * Math.sin(a2), M); pts.push(p2);
        }
        closed = mapRect({x: cx - rx, y: cy - ry, width: 2 * rx, height: 2 * ry}, M);
      }
    } catch (e) { /* 单个形状失败不致命 */ }

    if (!closed && !pts.length) return;
    shapes.push({
      di: di, tag: tag, hasStroke: hasStroke, stroke: hasStroke ? String(cs.stroke).slice(0, 24) : null,
      sw: sw, fill: fill, fillOp: fillOp, opacity: parseFloat(cs.opacity) || 1,
      box: closed, pts: pts, el: el
    });
  });

  // 画布底色矩形（覆盖 ≥98% viewBox）与 defs 装饰不参与 text↔rect 检测；
  // 越出 viewBox >30px 的盒视为装饰带（sweepband/裁切框等），同样排除
  shapes.forEach(function(s){
    s.isCanvasBg = !!(vb && s.box && s.box.w * s.box.h >= 0.98 * vb.w * vb.h);
    s.isDecorative = !!(vb && s.box && (
      s.box.x < vb.x - 30 || s.box.y < vb.y - 30 ||
      s.box.x + s.box.w > vb.x + vb.w + 30 || s.box.y + s.box.h > vb.y + vb.h + 30));
  });

  // 不透明遮挡候选（文字标签底）：实心填充、文档序在连线之后 → 遮住连线属有意设计
  var occluders = shapes.filter(function(s){
    return s.tag !== 'line' && s.tag !== 'path' && s.tag !== 'polyline' &&
           !s.isCanvasBg && !s.isDecorative && s.box && s.fill && s.fill !== 'none' &&
           s.fill.indexOf('url') !== 0 &&
           s.fillOp >= 0.85 && s.opacity >= 0.85;
  });

  // ---- A. text ↔ text ----
  // 墨迹近似盒：em 盒上下内缩 15%、左右内缩 2%（CJK 墨迹约占 em 盒 12%~88%，
  // 行距紧排时 em 盒相交但墨迹不相交 → 不算真重叠）
  function inkShrinkBox(b){
    var dx = Math.max(0.2, b.w * 0.02), dy = b.h * 0.15;
    return {x: b.x + dx, y: b.y + dy, w: Math.max(0, b.w - 2 * dx), h: Math.max(0, b.h - 2 * dy)};
  }
  function charInk(cb){
    var h = cb.h * 0.15;
    return {x: cb.x + cb.w * 0.02, y: cb.y + h, w: cb.w * 0.96, h: Math.max(0, cb.h - 2 * h)};
  }
  var findings = [];
  for (var i = 0; i < texts.length; i++){
    for (var j = i + 1; j < texts.length; j++){
      var A = texts[i], B = texts[j];
      var ovRaw = inter(A.ink, B.ink);
      if (ovRaw.w <= 0.05 || ovRaw.h <= 0.05) continue;
      var sA = inkShrinkBox(A.ink), sB = inkShrinkBox(B.ink);
      var ov = inter(sA, sB);
      var area = (ov.w > 0 && ov.h > 0) ? ov.w * ov.h : 0;
      if (area < 0.8 && ovRaw.w * ovRaw.h < 3) continue; // 墨迹与 em 双重微小：不记
      var ca = 0, cb2 = 0;
      A.chars.forEach(function(ac){
        if (B.chars.some(function(bc){ var q = inter(charInk(ac.b), charInk(bc.b)); return q.w > 0.1 && q.h > 0.1; })) ca++;
      });
      B.chars.forEach(function(bc){
        if (A.chars.some(function(ac){ var q = inter(charInk(ac.b), charInk(bc.b)); return q.w > 0.1 && q.h > 0.1; })) cb2++;
      });
      var minInkH = Math.min(sA.h, sB.h) || 1, minInkA = Math.min(sA.w * sA.h, sB.w * sB.h) || 1;
      findings.push({
        kind: 'text-text',
        a: {di: A.di, text: A.text, box: box(A.ink)},
        b: {di: B.di, text: B.text, box: box(B.ink)},
        overlapW: r1(Math.max(0, ov.w)), overlapH: r1(Math.max(0, ov.h)),
        overlapArea: r1(area), rawOverlapArea: r1(ovRaw.w * ovRaw.h),
        inkDepthFrac: r1(Math.max(0, ov.h) / minInkH),
        inkAreaFrac: r1(area / minInkA),
        charOverlap: ca + cb2
      });
    }
  }

  // ---- B. text ↔ stroke（连线穿字）----
  texts.forEach(function(T){
    shapes.forEach(function(S){
      if (!S.hasStroke || !S.pts.length) return;
      var inset = 0.35;
      var hits = S.pts.filter(function(p){ return ptIn(p, T.ink, inset); });
      if (hits.length < 2) return;
      var first = hits[0], last = hits[hits.length - 1];
      var span = Math.hypot(last.x - first.x, last.y - first.y);
      if (span < 1.2) return; // 只是端点擦到文字边缘
      var maxPen = 0;
      hits.forEach(function(p){
        var d = Math.min(p.x - T.ink.x, T.ink.x + T.ink.w - p.x,
                         p.y - T.ink.y, T.ink.y + T.ink.h - p.y);
        if (d > maxPen) maxPen = d;
      });
      var occ = 0;
      hits.forEach(function(p){
        for (var k = 0; k < occluders.length; k++){
          var o = occluders[k];
          if (o.di > S.di && p.x > o.box.x && p.x < o.box.x + o.box.w &&
              p.y > o.box.y && p.y < o.box.y + o.box.h){ occ++; break; }
        }
      });
      findings.push({
        kind: 'text-stroke',
        a: {di: T.di, text: T.text, box: box(T.ink)},
        shape: {di: S.di, tag: S.tag, stroke: S.stroke, sw: S.sw},
        hits: hits.length, spanPx: r1(span), maxPen: r1(maxPen),
        occludedFrac: r1(occ / hits.length),
        hitFrom: {x: r1(first.x), y: r1(first.y)}, hitTo: {x: r1(last.x), y: r1(last.y)}
      });
    });
  });

  // ---- C. text ↔ rect（文字压组件边界 / 墨迹逃出填充盒）----
  texts.forEach(function(T){
    shapes.forEach(function(S){
      if (!S.box || S.isCanvasBg || S.isDecorative) return;
      if (S.tag === 'line' || S.tag === 'polyline' || S.tag === 'path') return;
      var outer = S.box, TB = T.ink;
      var ovOut = inter(TB, outer);
      if (ovOut.w <= 0.05 || ovOut.h <= 0.05) return;      // 完全不相交
      var insideFrac = (ovOut.w * ovOut.h) / Math.max(1e-6, TB.w * TB.h);
      // (1) 墨迹伸出盒外：无论有无描边都是真问题（底盒盖不住字 / 文字跨界压组件）
      var outL = outer.x - TB.x, outR = TB.x + TB.w - (outer.x + outer.w);
      var outT = outer.y - TB.y, outB = TB.y + TB.h - (outer.y + outer.h);
      var escape = Math.max(outL, outR, outT, outB);
      if (escape > 0.8){
        var es = [];
        if (outL > 0.4) es.push('left'); if (outR > 0.4) es.push('right');
        if (outT > 0.4) es.push('top');  if (outB > 0.4) es.push('bottom');
        findings.push({
          kind: 'text-rect', mode: 'escape', insideFrac: r1(insideFrac),
          a: {di: T.di, text: T.text, box: box(TB)},
          shape: {di: S.di, tag: S.tag, box: box(outer), fill: S.fill},
          sides: es, maxPen: r1(escape)
        });
        return;
      }
      // (2) 有可见描边时：文字完全在盒内但压到边框带 → 视觉"贴边/压线"
      if (!S.hasStroke) return; // 无描边底盒 + 墨迹全在盒内 = 正常标签
      var bandW = Math.max(2.4, S.sw / 2 + 1.6);
      var inner = {x: outer.x + bandW, y: outer.y + bandW,
                   w: Math.max(0, outer.w - 2 * bandW), h: Math.max(0, outer.h - 2 * bandW)};
      var ovIn = inter(TB, inner);
      if (ovIn.w > 0 && ovIn.h > 0 && ovIn.w >= TB.w - 0.3 && ovIn.h >= TB.h - 0.3) return; // 远离边框
      var sides = [];
      function bandHit(bx1, by1, bx2, by2){
        var x1 = Math.max(TB.x, bx1), y1 = Math.max(TB.y, by1);
        var x2 = Math.min(TB.x + TB.w, bx2), y2 = Math.min(TB.y + TB.h, by2);
        return Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
      }
      if (bandHit(outer.x, outer.y, outer.x + outer.w, outer.y + bandW) > 0.4) sides.push('top');
      if (bandHit(outer.x, outer.y + outer.h - bandW, outer.x + outer.w, outer.y + outer.h) > 0.4) sides.push('bottom');
      if (bandHit(outer.x, outer.y, outer.x + bandW, outer.y + outer.h) > 0.4) sides.push('left');
      if (bandHit(outer.x + outer.w - bandW, outer.y, outer.x + outer.w, outer.y + outer.h) > 0.4) sides.push('right');
      if (!sides.length) return;
      var pen = 0;
      if (sides.indexOf('top') >= 0)    pen = Math.max(pen, Math.min(TB.y + TB.h, outer.y + bandW) - Math.max(TB.y, outer.y));
      if (sides.indexOf('bottom') >= 0) pen = Math.max(pen, Math.min(TB.y + TB.h, outer.y + outer.h) - Math.max(TB.y, outer.y + outer.h - bandW));
      if (sides.indexOf('left') >= 0)   pen = Math.max(pen, Math.min(TB.x + TB.w, outer.x + bandW) - Math.max(TB.x, outer.x));
      if (sides.indexOf('right') >= 0)  pen = Math.max(pen, Math.min(TB.x + TB.w, outer.x + outer.w) - Math.max(TB.x, outer.x + outer.w - bandW));
      findings.push({
        kind: 'text-rect', mode: 'band', insideFrac: r1(insideFrac),
        a: {di: T.di, text: T.text, box: box(TB)},
        shape: {di: S.di, tag: S.tag, box: box(outer), fill: S.fill},
        sides: sides, maxPen: r1(pen)
      });
    });
  });

  // ---- D. 盲区审计 ----
  var audit = {outOfViewbox: [], emptyText: emptyText, fonts: []};
  if (vb){
    texts.forEach(function(T){
      var e = {l: Math.max(0, r1(vb.x - T.ink.x)), t: Math.max(0, r1(vb.y - T.ink.y)),
               r: Math.max(0, r1(T.ink.x + T.ink.w - (vb.x + vb.w))),
               b: Math.max(0, r1(T.ink.y + T.ink.h - (vb.y + vb.h)))};
      if (e.l > 0.5 || e.t > 0.5 || e.r > 0.5 || e.b > 0.5)
        audit.outOfViewbox.push({di: T.di, text: T.text, box: box(T.ink), out: e});
    });
  }
  var famSeen = {};
  texts.forEach(function(T){
    var f = T.family.split(',')[0].replace(/['"]/g, '').trim();
    if (!f || famSeen[f]) return;
    famSeen[f] = 1;
    var ok = null;
    try { ok = document.fonts.check('12px "' + f + '"'); } catch (e) {}
    audit.fonts.push({family: f, available: ok});
  });

  var result = {
    file: '__FILE__', viewBox: vb ? [vb.x, vb.y, vb.w, vb.h] : null,
    textCount: texts.length, shapeCount: shapes.length,
    findings: findings, audit: audit
  };
  function emit(){
    var pre = document.getElementById('__OVERLAP_JSON__');
    if (pre) pre.textContent = JSON.stringify(result);
    document.title = 'OVERLAP_DONE';
  }
  if (document.fonts && document.fonts.ready){
    var done = false;
    document.fonts.ready.then(function(){ done = true; emit(); });
    setTimeout(function(){ if (!done) emit(); }, 600);
  } else emit();
})();
</script>
</body></html>
""".replace("__FREEZE__", "<style>" + _FREEZE_CSS + "</style>")

_ZOOM_TMPL = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
html,body{margin:0;padding:0;background:#fff;overflow:hidden}
#clip{position:relative;width:__W__px;height:__H__px;overflow:hidden}
#off{position:absolute;left:__OX__px;top:__OY__px}
#target-svg{display:block}
__FREEZE__
</style></head>
<body><div id="clip"><div id="off">
__SVG__
</div></div></body></html>
""".replace("__FREEZE__", "<style>" + _FREEZE_CSS + "</style>")

# 截图/掩膜 harness 不注入冻结 CSS——screenshot 模式改用 --virtual-time-budget
# 让动画快进到布局终态（.fade/.row 等 forwards 动画落定，不再停在 opacity:0）。
_SHOT_TMPL = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
html,body{margin:0;padding:0;background:#fff;overflow:hidden}
#clip{position:relative;width:__W__px;height:__H__px;overflow:hidden}
#off{position:absolute;left:__OX__px;top:__OY__px}
#target-svg{display:block;visibility:hidden}
</style></head>
<body><div id="clip"><div id="off">
__SVG__
</div></div>
<script>
(function(){
  var m = location.hash.slice(1).split('&'), show = -1;
  m.forEach(function(kv){ if (kv.indexOf('show=') === 0) show = parseInt(kv.slice(5), 10); });
  var svg = document.getElementById('target-svg');
  var all = svg.querySelectorAll('*');
  if (show >= 0 && show < all.length) all[show].style.visibility = 'visible';
  document.title = 'MASK_READY';
})();
</script>
</body></html>"""


def _read_svg(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _viewbox_of(svg_text):
    m = re.search(r'viewBox\s*=\s*"([^"]+)"', svg_text)
    if not m:
        return None
    try:
        vals = [float(v) for v in m.group(1).replace(",", " ").split()]
        if len(vals) == 4 and vals[2] > 0 and vals[3] > 0:
            return vals
    except ValueError:
        pass
    return None


def _ensure_svg_id(svg_text):
    """harness 依赖 id=target-svg；没有就注入一个。"""
    if "target-svg" in svg_text:
        return svg_text
    m = re.search(r"<svg\b[^>]*>", svg_text)
    if not m:
        raise ValueError("no <svg> root tag")
    tag = m.group(0)
    if tag.endswith("/>"):
        return svg_text.replace(tag, tag[:-2] + ' id="target-svg">', 1)
    return svg_text.replace(tag, tag[:-1] + ' id="target-svg">', 1)


def measure_file(chrome, svg_path, workdir, freeze=True, vt_budget=None):
    """headless 渲染 + JS 度量，返回结果 dict。
    freeze=False 时不注入冻结 CSS，配合 vt_budget 可测动画中途帧（入场位移态）的布局。"""
    svg_text = _ensure_svg_id(_read_svg(svg_path))
    harness = os.path.join(workdir, "h.html")
    tmpl = _HARNESS_TMPL if freeze else _HARNESS_TMPL.replace(
        "__SVG__", "__SVG__").replace("<style>" + _FREEZE_CSS + "</style>", "<style>/*no-freeze*/</style>")
    with open(harness, "w", encoding="utf-8") as f:
        f.write(tmpl.replace("__SVG__", svg_text).replace("__FILE__", os.path.basename(svg_path)))
    url = "file:///" + harness.replace("\\", "/")
    budgets = (vt_budget,) if vt_budget else (15000, 40000)
    for budget in budgets:
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
               "--force-device-scale-factor=1", "--allow-file-access-from-files",
               f"--virtual-time-budget={budget}", "--dump-dom", url]
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                               encoding="utf-8", errors="replace",
                               creationflags=0x08000000)
        except subprocess.TimeoutExpired:
            continue
        m = re.search(r'<pre id="__OVERLAP_JSON__"[^>]*>(.*?)</pre>', p.stdout or "", re.S)
        if not m:
            continue
        try:
            r = json.loads(_html.unescape(m.group(1)))
            r["_vtBudget"] = budget
            r["_frozen"] = freeze
            return r
        except json.JSONDecodeError:
            continue
    raise RuntimeError(f"测量失败（无法从 harness 取回 JSON）: {svg_path}; "
                       f"stderr 尾部: {(p.stderr or '')[-400:] if p else 'n/a'}")


def screenshot_svg(chrome, svg_path, out_png, vb, crop=None):
    """全页截图（vb 尺寸）或裁剪截图（crop=[x,y,w,h]，viewBox 坐标）。
    一律带 --virtual-time-budget，动画版渲染到布局终态。"""
    svg_text = _ensure_svg_id(_read_svg(svg_path))
    tmp_html = out_png + ".h.html"
    if crop:
        x, y, w, h = crop
        page = (_SHOT_TMPL.replace("visibility:hidden", "")
                .replace("__W__", str(int(round(w))))
                .replace("__H__", str(int(round(h))))
                .replace("__OX__", str(round(-x, 2))).replace("__OY__", str(round(-y, 2)))
                .replace("__SVG__", svg_text))
        win = f"{int(round(w))},{int(round(h))}"
    else:
        page = ('<!DOCTYPE html><html><head><meta charset="utf-8"><style>html,body{margin:0}'
                '#target-svg{display:block}</style></head><body>__SVG__</body></html>'
                ).replace("__SVG__", svg_text)
        w = vb[2] if vb else 1200
        h = vb[3] if vb else 560
        win = f"{int(round(min(w, 4000)))},{int(round(min(h, 4000)))}"
    with open(tmp_html, "w", encoding="utf-8") as f:
        f.write(page)
    url = "file:///" + tmp_html.replace("\\", "/")
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           "--force-device-scale-factor=1", "--default-background-color=FFFFFFFF",
           "--virtual-time-budget=8000",
           f"--window-size={win}", "--screenshot=" + out_png, url]
    subprocess.run(cmd, capture_output=True, timeout=120, creationflags=0x08000000)
    try:
        os.remove(tmp_html)
    except OSError:
        pass


def r1g(v):
    return round(v, 1)


# ----------------------------------------------------------------------------
# 像素级复核（视觉等价的客观验证）：双掩膜渲染 + PIL 墨迹交集
# ----------------------------------------------------------------------------

def _render_mask(chrome, svg_text, workdir, di, crop, scale, tag):
    """只显示文档序为 di 的元素，渲染 crop 区域（viewBox 坐标）。返回 PNG 路径。"""
    x, y, w, h = crop
    page = (_SHOT_TMPL.replace("__W__", str(int(round(w))))
            .replace("__H__", str(int(round(h))))
            .replace("__OX__", str(round(-x, 2))).replace("__OY__", str(round(-y, 2)))
            .replace("__SVG__", svg_text))
    hpath = os.path.join(workdir, f"mask_{tag}.html")
    with open(hpath, "w", encoding="utf-8") as f:
        f.write(page)
    png = os.path.join(workdir, f"mask_{tag}.png")
    url = "file:///" + hpath.replace("\\", "/") + f"#show={di}"
    cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--force-device-scale-factor={scale}", "--default-background-color=FFFFFFFF",
           "--virtual-time-budget=8000",
           f"--window-size={int(round(w))},{int(round(h))}",
           "--screenshot=" + png, url]
    subprocess.run(cmd, capture_output=True, timeout=120, creationflags=0x08000000)
    return png if os.path.isfile(png) else None


def _ink_mask(png, bg_tol=28):
    """返回 (ink 布尔集, 尺寸)；ink=与背景色差>bg_tol 的像素。背景取最常见色。"""
    from PIL import Image
    im = Image.open(png).convert("RGB")
    colors = im.getcolors(maxcolors=1 << 24)
    bg = max(colors, key=lambda c: c[0])[1]
    px = im.load()
    w, h = im.size
    mask = bytearray(w * h)
    for yy in range(h):
        for xx in range(w):
            r, g, b = px[xx, yy]
            if (abs(r - bg[0]) > bg_tol or abs(g - bg[1]) > bg_tol or abs(b - bg[2]) > bg_tol):
                mask[yy * w + xx] = 1
    return mask, (w, h), bg


def _clamped_crop(bbox, vb, pad):
    x, y, w, h = bbox
    if vb:
        x = max(vb[0], x - pad); y = max(vb[1], y - pad)
        x2 = min(vb[0] + vb[2], x + w + 2 * pad); y2 = min(vb[1] + vb[3], y + h + 2 * pad)
        return [x, y, max(8, x2 - x), max(8, y2 - y)]
    return [max(0, x - pad), max(0, y - pad), w + 2 * pad, h + 2 * pad]


def pixel_verify_result(chrome, r, svg_path, workdir, scale=2):
    """对 BLOCKER/HIGH 发现做像素级复核；与几何判定矛盾时降级（记录 pixel 段落）。"""
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        print("[pixel] PIL 不可用，跳过像素复核")
        return
    svg_text = _ensure_svg_id(_read_svg(svg_path))
    vb = r.get("viewBox")
    for fid, f in enumerate(r.get("findings", [])):
        if f.get("_sev") not in ("BLOCKER", "HIGH"):
            continue
        bb = finding_bbox(f)
        if not bb:
            continue
        crop = _clamped_crop(bb, vb, 10)
        try:
            if f["kind"] in ("text-text", "text-stroke"):
                pa = _render_mask(chrome, svg_text, workdir, f["a"]["di"], crop, scale, f"a{fid}")
                di_b = f["b"]["di"] if f["kind"] == "text-text" else f["shape"]["di"]
                pb = _render_mask(chrome, svg_text, workdir, di_b, crop, scale, f"b{fid}")
                if not pa or not pb:
                    continue
                ma, size, _ = _ink_mask(pa)
                mb, _, _ = _ink_mask(pb)
                n = size[0] * size[1]
                collide = sum(1 for i in range(n) if ma[i] and mb[i])
                f["pixel"] = {"mode": "mask-intersect", "scale": scale,
                              "inkA": sum(ma), "inkB": sum(mb), "collisionPx": collide}
                if collide == 0:
                    f["_pixelVerdict"] = "no-ink-collision"
                    f["_sev"] = "LOW"
                else:
                    f["_pixelVerdict"] = "ink-collision"
            elif f["kind"] == "text-rect":
                pa = _render_mask(chrome, svg_text, workdir, f["a"]["di"], crop, scale, f"a{fid}")
                if not pa:
                    continue
                ma, size, _ = _ink_mask(pa)
                bx = f["shape"]["box"]
                band = 1.5
                L, R = bx["x"], bx["x"] + bx["w"]
                T, B = bx["y"], bx["y"] + bx["h"]
                hit = 0
                for yy in range(size[1]):
                    sy = crop[1] + yy / scale
                    for xx in range(size[0]):
                        if not ma[yy * size[0] + xx]:
                            continue
                        sx = crop[0] + xx / scale
                        near_v = L - band <= sx <= R + band and (abs(sy - T) <= band or abs(sy - B) <= band)
                        near_h = T - band <= sy <= B + band and (abs(sx - L) <= band or abs(sx - R) <= band)
                        if near_v or near_h:
                            hit += 1
                f["pixel"] = {"mode": "border-band", "scale": scale,
                              "inkA": sum(ma), "borderInkPx": hit}
                if hit >= 4:
                    f["_pixelVerdict"] = "ink-on-border"
                else:
                    f["_pixelVerdict"] = "no-border-ink"
                    f["_sev"] = "LOW"
        except Exception as e:
            f["pixelError"] = str(e)[:120]


# ----------------------------------------------------------------------------
# 分级
# ----------------------------------------------------------------------------

def classify(f):
    """依据度量值给发现定级：BLOCKER / HIGH / LOW。"""
    k = f["kind"]
    if k == "text-text":
        depth = f.get("inkDepthFrac", 0)
        area = f.get("inkAreaFrac", 0)
        if depth >= 0.22 and area >= 0.10:
            return "BLOCKER"          # 墨迹深度互叠：语义受损
        if (depth >= 0.06 and area >= 0.01) or f.get("charOverlap", 0) >= 2:
            return "HIGH"             # 墨迹确有相交，肉眼可见
        return "LOW"                  # 仅 em 盒擦边（行距紧），视觉可接受
    if k == "text-stroke":
        if f["occludedFrac"] >= 0.8:
            return "LOW"           # 连线被标签底遮断：有意设计
        if f["maxPen"] >= 2.5 or f["spanPx"] >= 8:
            return "HIGH"
        return "LOW"
    if k == "text-rect":
        if f.get("mode") == "escape":
            if f["maxPen"] >= 6:
                return "HIGH"      # 深度伸出盒外
            if f["maxPen"] >= 2.0 and f.get("insideFrac", 0) >= 0.10:
                return "HIGH"      # 骑跨边界（内外皆有可观占比）
            return "LOW"
        return "HIGH" if f["maxPen"] >= 1.5 else "LOW"  # band：压边框带
    return "LOW"


def merge_dup_strokes(findings):
    """动画版 flowdot/flowtail 等发光副本与基线共享几何 → 同文字同轨迹（±1.5px）归并为一条。"""
    seen = {}
    out = []
    for f in findings:
        if f["kind"] == "text-stroke":
            key = (f["a"]["di"], round(f["hitFrom"]["x"] / 3), round(f["hitFrom"]["y"] / 3),
                   round(f["hitTo"]["x"] / 3), round(f["hitTo"]["y"] / 3))
            if key in seen:
                seen[key]["dupCount"] = seen[key].get("dupCount", 1) + 1
                continue
            f["dupCount"] = 1
            seen[key] = f
        out.append(f)
    return out


def classify_audit(a):
    """盲区审计条目 → (级别, 类型) 或 None。"""
    out = []
    for e in a.get("outOfViewbox", []):
        worst = max(e["out"].values())
        lvl = "BLOCKER" if worst > 4 else "HIGH"
        out.append((lvl, "text-out-of-viewbox", e))
    if a.get("emptyText"):
        out.append(("LOW", "empty-text", {"count": a["emptyText"]}))
    return out


SEV_ORDER = {"BLOCKER": 3, "HIGH": 2, "LOW": 1}


# ----------------------------------------------------------------------------
# 报告
# ----------------------------------------------------------------------------

def fmt_box(b):
    return f"({b['x']},{b['y']}) {b['w']}×{b['h']}"


def build_md(results, argv_note, chrome, ev_dir, date_str):
    lines = []
    lines.append(f"# SVG 图版重叠扫描报告 {date_str}")
    lines.append("")
    lines.append("- 工具：`images/tools/check_overlap.py`（真浏览器渲染度量，Chrome headless "
                 "getExtentOfChar/getPointAtLength + CTM 归一）")
    lines.append(f"- 运行：`{argv_note}`")
    lines.append(f"- 浏览器：`{chrome}`")
    lines.append("- 分级标准：**BLOCKER**＝文字语义被遮挡/不可读（两段文字墨迹深度互叠≥22% 且面积≥10%，"
                 "或文字越出 viewBox >4px）；**HIGH**＝连线明显穿字（无标签底遮挡、侵入≥2.5px 或跨≥8px）、"
                 "文字压组件边界/伸出组件盒（侵入≥6px 或骑跨≥2px 且盒内占比≥10%）、墨迹确有相交的文字对；"
                 "**LOW**＝轻微擦边（em 盒交叠但墨迹未触、贴边框带<1.5px、被标签底有意遮断的连线），视觉可接受。")
    lines.append("- 动画版说明：CSS 动画被冻结到布局终帧后度量；流光/呼吸类纯视觉动画不影响几何。")
    lines.append("- 像素复核：对全部 BLOCKER/HIGH 发现做双掩膜渲染（只渲 A / 只渲 B，2x 缩放），"
                 "PIL 统计墨迹像素交集（文字↔文字、文字↔连线）或边界带墨迹命中（文字↔组件）；"
                 "几何判级与像素证据矛盾时自动降级为 LOW 并在明细中留痕。")
    lines.append("")
    # 汇总
    lines.append("## 汇总")
    lines.append("")
    lines.append("| 文件 | 文字数 | BLOCKER | HIGH | LOW | 越界文字 | 空文本 |")
    lines.append("|---|---|---|---|---|---|---|")
    tot = {"BLOCKER": 0, "HIGH": 0, "LOW": 0}
    for r in results:
        sev = {"BLOCKER": 0, "HIGH": 0, "LOW": 0}
        for f in r.get("findings", []):
            sev[f["_sev"]] += 1
            tot[f["_sev"]] += 1
        oov = len(r.get("audit", {}).get("outOfViewbox", []))
        for lvl, _k, _e in classify_audit(r.get("audit", {})):
            sev[lvl] += 1
            tot[lvl] += 1
        lines.append(f"| {r['label']} | {r.get('textCount', '?')} | {sev['BLOCKER']} | "
                     f"{sev['HIGH']} | {sev['LOW']} | {oov} | {r.get('audit', {}).get('emptyText', 0)} |")
    lines.append(f"| **合计** |  | **{tot['BLOCKER']}** | **{tot['HIGH']}** | **{tot['LOW']}** |  |  |")
    lines.append("")

    for r in results:
        lines.append(f"## {r['label']}")
        lines.append("")
        fs = r.get("findings", [])
        audit_items = classify_audit(r.get("audit", {}))
        if not fs and not audit_items:
            lines.append("未检出重叠。✔")
            lines.append("")
            continue
        fid = 0
        lines.append("| ID | 级别 | 类型 | 描述 | 证据 |")
        lines.append("|---|---|---|---|---|")
        for f in sorted(fs, key=lambda x: -SEV_ORDER[x["_sev"]]):
            fid += 1
            desc = describe_finding(f)
            ev = f"`{ev_dir}/{r['stem']}.F{fid:03d}.png`" if f["_sev"] in ("BLOCKER", "HIGH") else "—"
            lines.append(f"| F{fid:03d} | {f['_sev']} | {zh_kind(f['kind'])} | {desc} | {ev} |")
        for lvl, kind, e in audit_items:
            fid += 1
            if kind == "text-out-of-viewbox":
                sides = "、".join(f"{k}侧 {v}px" for k, v in e["out"].items() if v > 0.5)
                desc = f"「{e['text']}」 越出 viewBox：{sides}（盒 {fmt_box(e['box'])}）"
            else:
                desc = f"空文本元素 {e['count']} 个"
            lines.append(f"| F{fid:03d} | {lvl} | {zh_kind(kind)} | {desc} | 全页图 |")
        lines.append("")
        fonts = r.get("audit", {}).get("fonts", [])
        if fonts:
            fdesc = "；".join(f"{x['family']}={'可用' if x['available'] else '不可用(回退)'}" for x in fonts)
            lines.append(f"- 字体审计：{fdesc}")
            lines.append("")
    lines.append("## 证据说明")
    lines.append("")
    lines.append(f"- 证据目录：`{ev_dir}/`（本报告同级）。")
    lines.append("- 每图一张 `<stem>.full.png`＝Chrome headless 1:1 全页渲染；"
                 "每个 BLOCKER/HIGH 发现一张 `<stem>.F###.png`＝以发现坐标为中心放大裁剪（含上下文约 ±26px）。")
    lines.append("- 复跑命令：`python images/tools/check_overlap.py --anim`（详见工具头部文档）。")
    lines.append("")
    lines.append("## 门禁接入")
    lines.append("")
    lines.append("```bash")
    lines.append("# 生成图后强制校验：任何 BLOCKER/HIGH 直接失败")
    lines.append("python images/tools/check_overlap.py --anim --gate-severity high")
    lines.append("```")
    lines.append("")
    lines.append(f"<!-- ymzhu {_dt.datetime.now().strftime('%Y-%m-%d %H:%M')} -->")
    return "\n".join(lines) + "\n"


def zh_kind(k):
    return {"text-text": "文字↔文字", "text-stroke": "文字↔连线",
            "text-rect": "文字↔组件", "text-out-of-viewbox": "越界/裁切",
            "empty-text": "空文本"}.get(k, k)


def describe_finding(f):
    k = f["kind"]
    desc = _describe_core(f)
    px = f.get("pixel")
    if px:
        if px.get("mode") == "mask-intersect":
            desc += f"｜像素复核：{f.get('_pixelVerdict')}（墨迹交集 {px['collisionPx']}px @{px['scale']}x）"
        elif px.get("mode") == "border-band":
            desc += f"｜像素复核：{f.get('_pixelVerdict')}（边界带墨迹 {px['borderInkPx']}px @{px['scale']}x）"
    elif f.get("pixelError"):
        desc += f"｜像素复核失败：{f['pixelError']}"
    return desc


def _describe_core(f):
    k = f["kind"]
    if k == "text-text":
        raw = f"，em 盒交叠 {f['rawOverlapArea']}px²" if f.get("rawOverlapArea", 0) > f.get("overlapArea", 0) else ""
        return (f"「{f['a']['text']}」{fmt_box(f['a']['box'])} ↔ 「{f['b']['text']}」"
                f"{fmt_box(f['b']['box'])}；墨迹交叠 {f['overlapW']}×{f['overlapH']}px"
                f"（面积 {f['overlapArea']}px²，深度占小字高 {f.get('inkDepthFrac', 0) * 100:.0f}%，"
                f"字符级互叠 {f['charOverlap']}{raw}）")
    if k == "text-stroke":
        occ = "，连线被不透明标签底遮断" if f["occludedFrac"] >= 0.8 else ""
        dup = f"（含 {f['dupCount']} 条重合线，动画流光副本已归并）" if f.get("dupCount", 1) > 1 else ""
        return (f"「{f['a']['text']}」{fmt_box(f['a']['box'])} 被 {f['shape']['tag']}"
                f"(stroke={f['shape']['stroke']}, w={f['shape']['sw']}) 穿过："
                f"{f['hitFrom']['x']},{f['hitFrom']['y']}→{f['hitTo']['x']},{f['hitTo']['y']}"
                f" 跨 {f['spanPx']}px，最大侵入 {f['maxPen']}px{occ}{dup}")
    if k == "text-rect":
        return (f"「{f['a']['text']}」{fmt_box(f['a']['box'])} 压 {f['shape']['tag']}"
                f"{fmt_box(f['shape']['box'])} 的 {'/'.join(f['sides'])} 边框，侵入 {f['maxPen']}px")
    return json.dumps(f, ensure_ascii=False)


def finding_bbox(f):
    k = f["kind"]
    if k == "text-text":
        a, b = f["a"]["box"], f["b"]["box"]
        x1 = min(a["x"], b["x"]); y1 = min(a["y"], b["y"])
        x2 = max(a["x"] + a["w"], b["x"] + b["w"]); y2 = max(a["y"] + a["h"], b["y"] + b["h"])
        return x1, y1, x2 - x1, y2 - y1
    if k == "text-stroke":
        a = f["a"]["box"]
        x1 = min(a["x"], f["hitFrom"]["x"]); y1 = min(a["y"], f["hitFrom"]["y"])
        x2 = max(a["x"] + a["w"], f["hitTo"]["x"]); y2 = max(a["y"] + a["h"], f["hitTo"]["y"])
        return x1, y1, x2 - x1, y2 - y1
    if k == "text-rect":
        a, s = f["a"]["box"], f["shape"]["box"]
        x1 = min(a["x"], s["x"]); y1 = min(a["y"], s["y"])
        x2 = max(a["x"] + a["w"], s["x"] + s["w"]); y2 = max(a["y"] + a["h"], s["y"] + s["h"])
        return x1, y1, x2 - x1, y2 - y1
    return None


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------

def collect_files(args):
    base = args.images_dir or os.path.dirname(os.path.abspath(__file__))
    out = []
    if args.files:
        for f in args.files:
            p = f if os.path.isabs(f) else os.path.join(base, f)
            if not os.path.isfile(p):
                raise SystemExit(f"[check_overlap] 文件不存在: {p}")
            out.append(p)
    else:
        for f in sorted(os.listdir(base)):
            if f.lower().endswith(".svg"):
                out.append(os.path.join(base, f))
        if args.anim:
            anim_dir = os.path.join(base, "anim")
            if os.path.isdir(anim_dir):
                for f in sorted(os.listdir(anim_dir)):
                    if f.lower().endswith(".svg"):
                        out.append(os.path.join(anim_dir, f))
    if not out:
        raise SystemExit("[check_overlap] 没有找到任何 SVG（检查 --images-dir / --files）")
    return base, out


def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser(description="SVG 成图后重叠检测门禁（真浏览器渲染度量）")
    ap.add_argument("--images-dir", default=os.path.dirname(here), help="SVG 所在目录（默认=images/）")
    ap.add_argument("--files", nargs="*", help="指定 SVG（相对 images-dir 或绝对）")
    ap.add_argument("--anim", action="store_true", help="额外扫描 anim/ 子目录")
    ap.add_argument("--no-freeze", action="store_true",
                    help="不冻结动画（配合 --vt-budget 测动画中途帧布局，如入场位移态抽查）")
    ap.add_argument("--vt-budget", type=int, default=None,
                    help="虚拟时钟预算 ms（如 1200 = 度量动画开始后 1.2s 时刻的布局）")
    ap.add_argument("--json", default=None, help="JSON 输出路径")
    ap.add_argument("--md", default=None, help="Markdown 报告路径")
    ap.add_argument("--evidence-dir", default=None, help="证据截图目录")
    ap.add_argument("--no-evidence", action="store_true", help="不生成截图证据")
    ap.add_argument("--no-pixel-verify", action="store_true",
                    help="跳过像素级复核（默认对 BLOCKER/HIGH 做双掩膜墨迹交集验证）")
    ap.add_argument("--force", action="store_true",
                    help="允许覆盖已存在的同名报告（默认拒绝，防止后跑的门禁把历史问题清单冲掉）")
    ap.add_argument("--chrome", default=None, help="Chrome/Edge 可执行文件路径")
    ap.add_argument("--gate-severity", choices=["blocker", "high", "low", "none"], default="none",
                    help="门禁级别：存在不低于该级别的发现时 exit 1")
    ap.add_argument("--keep-harness", action="store_true", help="保留临时 harness（调试）")
    args = ap.parse_args(argv)

    chrome = find_chrome(args.chrome)
    base, files = collect_files(args)
    date_str = DEFAULT_REPORT_DATE
    json_path = args.json or os.path.join(here, f"overlap_report_{date_str}.json")
    md_path = args.md or os.path.join(here, f"overlap_report_{date_str}.md")
    ev_dir = args.evidence_dir or os.path.join(here, f"overlap_evidence_{date_str}")
    if not args.no_evidence:
        os.makedirs(ev_dir, exist_ok=True)
    for _target in (json_path, md_path):
        if os.path.exists(_target) and not args.force:
            raise SystemExit(f"[check_overlap] 报告已存在：{_target}\n"
                             f"  同日重复跑门禁请用 --json/--md 指定新名字（如 *_after_fix），或 --force 显式覆盖。")

    workdir = tempfile.mkdtemp(prefix="check_overlap_")
    results = []
    try:
        for p in files:
            try:
                rel = os.path.relpath(p, base).replace("\\", "/")
            except ValueError:  # 跨盘符（如自检样本放 C: 临时目录）
                rel = p.replace("\\", "/")
            print(f"[measure] {rel}", flush=True)
            r = measure_file(chrome, p, workdir, freeze=not args.no_freeze, vt_budget=args.vt_budget)
            stem = re.sub(r"[^A-Za-z0-9_.-]+", "_", rel.replace("/", "__"))
            r["label"] = rel
            r["stem"] = stem
            r["path"] = p
            r["findings"] = merge_dup_strokes(r.get("findings", []))
            for f in r.get("findings", []):
                f["_sev"] = classify(f)
            results.append(r)

        # 像素级复核（视觉等价客观验证）：矛盾时降级
        if not args.no_pixel_verify:
            for r in results:
                print(f"[pixel] {r['label']}", flush=True)
                pixel_verify_result(chrome, r, r["path"], workdir)
    finally:
        if args.keep_harness:
            print(f"[harness] 保留于 {workdir}")
        else:
            shutil.rmtree(workdir, ignore_errors=True)

    # 证据截图（全页 + BLOCKER/HIGH 裁剪）
    if not args.no_evidence:
        for r in results:
            vb = r.get("viewBox")
            full = os.path.join(ev_dir, r["stem"] + ".full.png")
            try:
                screenshot_svg(chrome, r["path"], full, vb)
                print(f"[evidence] {os.path.basename(full)}")
            except Exception as e:
                print(f"[evidence] 全页截图失败 {r['label']}: {e}")
            ordered = sorted(r.get("findings", []), key=lambda x: -SEV_ORDER[x["_sev"]])
            fid = 0
            for f in ordered:
                fid += 1
                if f["_sev"] not in ("BLOCKER", "HIGH"):
                    continue
                bb = finding_bbox(f)
                if not bb or not vb:
                    continue
                pad = 26
                x = max(vb[0], bb[0] - pad); y = max(vb[1], bb[1] - pad)
                x2 = min(vb[0] + vb[2], bb[0] + bb[2] + pad); y2 = min(vb[1] + vb[3], bb[1] + bb[3] + pad)
                crop = [x, y, max(8, x2 - x), max(8, y2 - y)]
                out_png = os.path.join(ev_dir, f"{r['stem']}.F{fid:03d}.png")
                try:
                    screenshot_svg(chrome, r["path"], out_png, vb, crop=crop)
                except Exception as e:
                    print(f"[evidence] 裁剪失败 {r['label']} F{fid:03d}: {e}")

    # 输出
    for r in results:
        r.pop("path", None)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"generated": _dt.datetime.now().isoformat(timespec="seconds"),
                   "chrome": chrome, "results": results}, f, ensure_ascii=False, indent=1)

    argv_note = "python images/tools/check_overlap.py" + (" --anim" if args.anim else "") + \
                (" --files " + " ".join(args.files) if args.files else "")
    md = build_md(results, argv_note, chrome, os.path.relpath(ev_dir, here).replace("\\", "/"), date_str)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # 摘要 + 门禁
    worst = 0
    for r in results:
        sevs = [f["_sev"] for f in r.get("findings", [])] + \
               [lvl for lvl, _k, _e in classify_audit(r.get("audit", {}))]
        for s in sevs:
            worst = max(worst, SEV_ORDER[s])
    counts = {"BLOCKER": 0, "HIGH": 0, "LOW": 0}
    for r in results:
        for f in r.get("findings", []):
            counts[f["_sev"]] += 1
        for lvl, _k, _e in classify_audit(r.get("audit", {})):
            counts[lvl] += 1
    print(f"\n[summary] files={len(results)} BLOCKER={counts['BLOCKER']} HIGH={counts['HIGH']} LOW={counts['LOW']}")
    print(f"[output]  json={json_path}\n[output]  md={md_path}")
    if not args.no_evidence:
        print(f"[output]  evidence={ev_dir}/")
    gate_map = {"blocker": 3, "high": 2, "low": 1, "none": 0}
    if args.gate_severity != "none" and worst >= gate_map[args.gate_severity]:
        print(f"[gate] FAIL：存在不低于 {args.gate_severity.upper()} 级别的重叠发现")
        return 1
    print("[gate] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-05 15:52
