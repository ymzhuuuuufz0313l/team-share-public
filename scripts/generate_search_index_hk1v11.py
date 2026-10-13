#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate search-index.js / search-index.json for hk1v11-synthesis-postpt-practice.

Adapted from scripts/generate_search_index.py (flow-guide). Key difference:
hk1v11 pages (js/site.js) assign heading ids by SLUGIFYING the heading text
(trim, whitespace -> '-', strip chars outside [0-9A-Za-z_\\u4e00-\\u9fa5-],
duplicates get -2/-3), not sec-N. This generator reproduces that exact scheme
so search-result jumps (#anchor) land on the right heading.

Run: python scripts/generate_search_index_hk1v11.py
"""
import glob
import json
import os
import re

SITE_DIR = os.path.join(os.path.dirname(__file__), '..', 'hk1v11-synthesis-postpt-practice')


def extract_md(html):
    m = re.search(r'<script type="text/template" id="md">(.*?)</script>', html, re.S)
    return m.group(1) if m else ''


def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    if not m:
        return ''
    return re.split(r'[·|]', m.group(1))[0].strip()


def strip_md(text):
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)          # images
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)       # links -> text
    text = re.sub(r'<[^>]+>', ' ', text)                       # inline html
    text = re.sub(r'[`*~]', '', text)                          # emphasis marks (keep _: snake_case identifiers + makeId \w keeps it)
    return re.sub(r'\s+', ' ', text).strip()


def make_ids(titles):
    """Reproduce js/site.js makeId(): slug + per-page dedupe with -2/-3."""
    used = {}
    ids = []
    for t in titles:
        base = re.sub(r'\s+', '-', t.strip())
        base = re.sub(r'[^0-9A-Za-z_一-龥-]', '', base)
        i = base
        n = 2
        while i in used:
            i = '%s-%d' % (base, n)
            n += 1
        used[i] = True
        ids.append(i)
    return ids


def parse_sections(md):
    """h2/h3 sections, code fences skipped; ids per hk1v11 slug scheme."""
    raw = []
    cur = None
    in_code = False
    for line in md.splitlines():
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        m = None if in_code else re.match(r'^(#{2,3})\s+(.*\S)\s*$', line)
        if m:
            if cur:
                raw.append(cur)
            cur = {'level': len(m.group(1)), 'title': strip_md(m.group(2)), 'buf': []}
        elif cur is not None:
            cur['buf'].append(line)
    if cur:
        raw.append(cur)
    ids = make_ids([s['title'] for s in raw])
    out = []
    for s, i in zip(raw, ids):
        out.append({
            'id': i,
            'level': s['level'],
            'title': s['title'],
            'text': strip_md(' '.join(s['buf'])),
        })
    return out


def main():
    index = []
    for path in sorted(glob.glob(os.path.join(SITE_DIR, '*.html'))):
        fname = os.path.basename(path)
        with open(path, encoding='utf-8') as f:
            html = f.read()
        md = extract_md(html)
        sections = parse_sections(md)
        index.append({
            'page': fname,
            'pageTitle': extract_title(html) or fname,
            'sections': sections,
        })
    out_js = os.path.join(SITE_DIR, 'search-index.js')
    payload = json.dumps(index, ensure_ascii=False)
    with open(out_js, 'w', encoding='utf-8') as f:
        f.write('window.SEARCH_INDEX = ' + payload + ';\n')
    out_json = os.path.join(SITE_DIR, 'search-index.json')
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    total = sum(len(p['sections']) for p in index)
    print('Generated %s: %d pages, %d sections' % (out_js, len(index), total))


if __name__ == '__main__':
    main()

# ymzhu 2026-10-13 16:40
