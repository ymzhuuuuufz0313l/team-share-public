#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate search-index.json for synthesis-integration-flow-guide.

Scans every *.html page in the guide directory, extracts the markdown stored
in <script type="text/template" id="md">, splits it into h2/h3 sections and
writes search-index.json. Section ids match the runtime anchor scheme used by
the pages: headings are numbered sec-0, sec-1, ... in document order.

Run: python generate_search_index.py
"""
import glob
import json
import os
import re

GUIDE_DIR = os.path.join(os.path.dirname(__file__), '..', 'synthesis-integration-flow-guide')


def extract_md(html):
    m = re.search(r'<script type="text/template" id="md">(.*?)</script>', html, re.S)
    return m.group(1) if m else ''


def extract_title(html):
    m = re.search(r'<title>(.*?)</title>', html, re.S)
    if not m:
        return ''
    # titles look like "环境与配置 · ASIC IP Synthesis ..." -> keep first part
    return re.split(r'[·|]', m.group(1))[0].strip()


def strip_md(text):
    text = re.sub(r'!\[[^\]]*\]\([^)]*\)', ' ', text)          # images
    text = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', text)       # links -> text
    text = re.sub(r'<[^>]+>', ' ', text)                       # inline html
    text = re.sub(r'[`*_~]', '', text)                         # emphasis marks
    return re.sub(r'\s+', ' ', text).strip()


def parse_sections(md):
    """Return list of dicts: id, level, title, text. h2/h3 only, code fences skipped."""
    sections = []
    cur = None
    in_code = False
    for line in md.splitlines():
        if line.strip().startswith('```'):
            in_code = not in_code
            continue
        m = None if in_code else re.match(r'^(#{2,3})\s+(.*\S)\s*$', line)
        if m:
            if cur:
                sections.append(cur)
            cur = {'level': len(m.group(1)), 'title': strip_md(m.group(2)), 'buf': []}
        elif cur is not None:
            cur['buf'].append(line)
    if cur:
        sections.append(cur)
    out = []
    for i, s in enumerate(sections):
        out.append({
            'id': 'sec-%d' % i,
            'level': s['level'],
            'title': s['title'],
            # Keep the full section text so long chapters stay searchable;
            # the frontend trims its own snippet for display.
            'text': strip_md(' '.join(s['buf'])),
        })
    return out


def main():
    index = []
    for path in sorted(glob.glob(os.path.join(GUIDE_DIR, '*.html'))):
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
    out = os.path.join(GUIDE_DIR, 'search-index.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    total = sum(len(p['sections']) for p in index)
    print('Generated %s: %d pages, %d sections' % (out, len(index), total))


if __name__ == '__main__':
    main()
