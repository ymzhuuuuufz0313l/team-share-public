# -*- coding: utf-8 -*-
"""make_static_30_postpt_trans_1p.py — 由动画版反向生成静态版（v4 双版契约补全，2026-11-02 ymzhu）

背景：scripts/check_anim_pairs.py 报本图只有动画版 anim/<NAME>.svg、缺同名静态版 → fx.js 切静态
模式（去掉路径中的 /anim/ 段）时 404。v4 契约（blueprint-ui-style「动画/静态双版 SVG 站点架构」章）：
静态版 = 事实源 + fallback，不含 animation / keyframes / 隐藏初态。本图静态源缺失，只能由动画版
反推（动画终态 = 静态图）。生成后静态版即事实源：已存在且内容不同则拒绝覆盖（--force 才覆盖）。

变换（只读 anim/<NAME>.svg，只写 ../<NAME>.svg）：
  1. 删装饰元素：class 含 flowdot / flowtail / sweepband 的自闭合元素（列车 / 光带，非事实内容）；
  2. <style> 内删动画 CSS：@keyframes 块、keyframes 外残留的步规则（from / to / NN%）、悬空 }、
     含 animation 声明的规则（连同其 opacity:0 入场隐藏初态）、prefers-reduced-motion 块；
     剩余为空 → 整个 <style> 元素删除，否则保留剩余（如字体）CSS；
  3. class 属性中删掉被动画规则选中的类名（本图 head / row），删空则删属性；语义类（lab / val）保留；
  4. 内联 style 中删 animation* 声明与 --sweep* 变量，删空则删属性；
  其余逐字保留：<svg> 开标签、全部 <text>、rect / line 几何、fill / stroke 配色。
自检（assert，任一不过即非 0 退出且不写文件）：XML 良构；<svg> 开标签一致；<text> 多重集一致
  （validate_kit_v4 口径 el.text + 严格口径 全文本×属性）；除 <style> / 装饰元素外全部元素的
  (tag, 属性去 class/style, 文本) 多重集一致；输出 CSS / 内联 style 无 animation / @keyframes / opacity:0。
确定性幂等：零第三方依赖（python 3.13），只依赖动画版，重跑输出字节一致。
用法：python make_static_30_postpt_trans_1p.py [--force]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter

NAME = '30_postpt_trans_1p'
HERE = os.path.dirname(os.path.abspath(__file__))          # .../image/anim
SRC = os.path.join(HERE, NAME + '.svg')                    # 动画版（只读）
DST = os.path.join(os.path.dirname(HERE), NAME + '.svg')   # 静态版 = 去掉 /anim/ 段
SIGN = '<!-- ymzhu 2026-11-02 19:00 -->'                   # 固定常量 → 重跑字节一致
NS = '{http://www.w3.org/2000/svg}'
DECOR = ('flowdot', 'flowtail', 'sweepband')
DECOR_EL = re.compile(r'[ \t]*<[A-Za-z]+\b[^>]*\bclass="[^"]*\b(?:%s)\b[^"]*"[^>]*/>\n?' % '|'.join(DECOR))
KF_STEP = re.compile(r'^(from|to|\d+(\.\d+)?%)(\s*,\s*(from|to|\d+(\.\d+)?%))*$')
ANIM_DECL = re.compile(r'(^|[;{\s])animation(-[a-z-]+)?\s*:')
ANIM_INLINE = re.compile(r'(animation(-[a-z-]+)?|--sweep[\w-]*)\s*:')


def split_css(css):
    """按顶层大括号切块 → ([(prelude, 原文)], 尾部残文)；悬空 '}' 的 prelude 记 None。"""
    out, buf, depth = [], '', 0
    for ch in css:
        if ch == '}' and depth == 0:
            out.append((None, buf + ch))
            buf = ''
            continue
        buf += ch
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append((buf[:buf.index('{')].strip(), buf))
                buf = ''
    return out, buf


def is_anim_chunk(prelude, chunk):
    if prelude is None:                                    # 悬空 }：被删 keyframes 的残片
        return True
    if re.match(r'@(-webkit-)?keyframes\b', prelude):
        return True
    if KF_STEP.match(prelude):                             # keyframes 外残留的步规则，如 50% {...}
        return True
    if prelude.startswith('@media') and 'prefers-reduced-motion' in prelude:
        return True
    return ANIM_DECL.search(chunk[chunk.index('{') + 1:]) is not None


def strip_style(svg, st):
    anim_classes = set()

    def fix(m):
        chunks, tail = split_css(m.group(2))
        assert not tail.strip(), '<style> 尾部有无法解析的残文：%r' % tail.strip()[:40]
        keep = []
        for prelude, chunk in chunks:
            if is_anim_chunk(prelude, chunk):
                st['css_chunks'] += 1
                if prelude and not prelude.startswith('@') and not KF_STEP.match(prelude):
                    anim_classes.update(re.findall(r'\.([A-Za-z_][\w-]*)', prelude))
            else:
                keep.append(chunk)
        rest = ''.join(keep)
        if not rest.strip():
            st['style_dropped'] += 1
            return ''
        return m.group(1) + rest + tail + '</style>' + m.group(3)

    return re.sub(r'(<style\b[^>]*>)(.*?)</style>(\n?)', fix, svg, flags=re.S), anim_classes


def strip_attr(svg, attr, keep_fn, st, key):
    """attr="..." 按 keep_fn 过滤条目；无条目被删则原样返回，删空则连前导空白一起删属性。"""
    sep = ' ' if attr == 'class' else ';'

    def fix(m):
        items = [x.strip() for x in m.group(2).split(sep) if x.strip()]
        keep = [x for x in items if keep_fn(x)]
        if len(keep) == len(items):
            return m.group(0)
        st[key] += 1
        return '%s%s="%s"' % (m.group(1), attr, sep.join(keep)) if keep else ''

    return re.sub(r'(\s+)%s="([^"]*)"' % attr, fix, svg)


def signatures(svg_text):
    root = ET.fromstring(svg_text.encode('utf-8'))
    bare = lambda el: tuple(sorted((k, v) for k, v in el.attrib.items() if k not in ('class', 'style')))
    texts = list(root.iter(NS + 'text'))
    kit = Counter(el.text or '' for el in texts)
    strict = Counter((''.join(el.itertext()), bare(el)) for el in texts)
    geo = Counter((el.tag, bare(el), (el.text or '').strip()) for el in root.iter()
                  if el.tag != NS + 'style' and not set((el.get('class') or '').split()) & set(DECOR))
    return kit, strict, geo


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    assert os.path.abspath(SRC) != os.path.abspath(DST)
    with open(SRC, encoding='utf-8', newline='') as f:
        src = f.read()
    st = Counter()

    s, n_decor = DECOR_EL.subn('', src)
    s, anim_classes = strip_style(s, st)
    s = strip_attr(s, 'class', lambda c: c not in anim_classes, st, 'class_attrs')
    s = strip_attr(s, 'style', lambda d: not ANIM_INLINE.match(d), st, 'style_attrs')
    out = s.rstrip('\n') + '\n' + SIGN + '\n'

    # ---- 自检 ----
    svgtag = lambda t: re.search(r'<svg\b[^>]*>', t).group(0)
    assert svgtag(src) == svgtag(out), '<svg> 开标签不一致'
    a_kit, a_strict, a_geo = signatures(src)
    s_kit, s_strict, s_geo = signatures(out)                 # 同时证明 XML 良构
    assert a_kit == s_kit, '<text> 多重集（el.text 口径）不一致'
    assert a_strict == s_strict, '<text> 多重集（严格口径）不一致'
    assert a_geo == s_geo, '几何 / 配色元素多重集不一致'
    css = ' '.join(re.findall(r'<style\b[^>]*>(.*?)</style>', out, re.S) + re.findall(r'\sstyle="([^"]*)"', out))
    assert not re.search(r'@(-webkit-)?keyframes|animation', css), '残留动画 CSS'
    assert not re.search(r'opacity\s*:\s*0(?![.\d])', css), '残留 opacity:0 隐藏初态'
    assert not re.search(r'class="[^"]*\b(?:%s)\b' % '|'.join(DECOR), out), '残留装饰元素（非自闭合？）'
    assert '<script' not in out and '<animate' not in out

    rel = lambda p: os.path.relpath(p, os.path.dirname(HERE)).replace(os.sep, '/')
    print('[make_static] %s -> %s' % (rel(SRC), rel(DST)))
    print('  removed: decor=%d css_chunks=%d style_elem=%d anim_classes=%s class_attrs=%d style_attrs=%d'
          % (n_decor, st['css_chunks'], st['style_dropped'], sorted(anim_classes), st['class_attrs'], st['style_attrs']))
    print('  verify : xml=OK svgtag=OK text(kit)=OK[%d] text(strict)=OK[%d] geo=OK[%d] no-anim-css=OK'
          % (sum(s_kit.values()), sum(s_strict.values()), sum(s_geo.values())))

    data = out.encode('utf-8')
    if os.path.isfile(DST):
        with open(DST, 'rb') as f:
            old = f.read()
        if old == data:
            print('  output : unchanged (byte-identical, %d bytes)' % len(data))
            return 0
        if '--force' not in sys.argv[1:]:
            print('  REFUSE : %s 已存在且内容不同（静态版是事实源）；确认要覆盖请加 --force' % rel(DST))
            return 1
    with open(DST, 'wb') as f:
        f.write(data)
    print('  output : wrote %d bytes' % len(data))
    return 0


if __name__ == '__main__':
    sys.exit(main())

# ymzhu 2026-11-02 19:00
