"""check_skill_pointers.py — 校验 team-share skill 里的"指向"是否都真实存在（2026-11-02）

用途：team-share SKILL.md 精简后，大量细节改为指向其它 skill / 模板文件 / 仓库文件。
指向只是文字，目标被改名或删除时不会报错——本脚本把"断链"变成可机检的失败。

检查项：
  1. skill 引用   ：正文里 `name` skill 形式的引用，name 必须是 ~/.zcode/skills 下可加载的 skill（目录内有 SKILL.md）
  2. 章节引用     ：同一行内 `name` skill 之后出现的「XXX」章，XXX 必须是该 skill SKILL.md 某个 #/##/### 标题的子串
  3. 文件引用     ：反引号内的仓库/模板/绝对路径（含 <slug> 等占位符的跳过），文件或目录必须存在
  4. 组件类名     ：「组件速查表」表格里的 .class 必须能在 site-template/css/style.css 中找到

用法：python check_skill_pointers.py [SKILL.md 路径]   （缺省 = ~/.zcode/skills/team-share/SKILL.md）
退出码：0 = 全部通过；1 = 有断链（逐条列出）
"""
import os
import re
import sys

HOME = os.path.expanduser('~')
SKILLS = os.path.join(HOME, '.zcode', 'skills')
REPO = r'E:\project\team-share-public'
TEMPLATE_CSS = os.path.join(REPO, 'site-template', 'css', 'style.css')
# 本机未 clone 的外部仓库（Workflow A 主知识库）：路径缺失只告警，不算断链
KNOWN_EXTERNAL = [os.path.join('E:' + os.sep, 'project', 'team-share')]



def loadable_skills():
    out = {}
    for name in os.listdir(SKILLS):
        p = os.path.join(SKILLS, name, 'SKILL.md')
        if os.path.isfile(p):
            out[name] = p
    return out


def headings(path):
    hs = []
    with open(path, encoding='utf-8') as f:
        for line in f:
            m = re.match(r'^#{1,4}\s+(.*)$', line.strip())
            if m:
                hs.append(m.group(1))
    return hs


def resolve_path(raw):
    """把反引号里的路径映射到磁盘路径；返回 None 表示不是可检查的路径。"""
    if '<' in raw or '*' in raw or ' ' in raw.strip():
        return None
    p = raw.strip().rstrip('/\\')
    if re.match(r'^[A-Za-z]:\\', p):
        return p
    if p.startswith('team-share-public/'):
        return os.path.join(REPO, p[len('team-share-public/'):])
    if p.startswith('site-template/'):
        return os.path.join(REPO, p)
    if p in ('PAGE_FX.md', 'ROLLOUT_FX.md'):
        return os.path.join(REPO, p)
    if p.startswith(('js/', 'css/')):
        return os.path.join(REPO, 'site-template', p)
    if p in ('README.md', 'page.html', 'index.html'):
        return os.path.join(REPO, 'site-template', p)
    if re.match(r'^hk1v11-[\w-]+/', p):
        return os.path.join(REPO, p)
    return None


def main():
    skill_md = sys.argv[1] if len(sys.argv) > 1 else os.path.join(SKILLS, 'team-share', 'SKILL.md')
    text = open(skill_md, encoding='utf-8').read()
    lines = text.splitlines()
    skills = loadable_skills()
    errors, warns, checked = [], [], {'skill': 0, 'section': 0, 'file': 0, 'class': 0}

    in_fence = False
    for no, line in enumerate(lines, 1):
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        # 1 + 2: skill 引用与章节引用
        # `name` skill …「X」章，或 `name`「X」章（不带 skill 字样）都算引用
        for m in re.finditer(r'`([a-z0-9][a-z0-9-]+)`(?=\s*(?:skill|「))', line):
            name = m.group(1)
            checked['skill'] += 1
            if name not in skills:
                errors.append(f'L{no}: skill `{name}` 不可加载（~/.zcode/skills/{name}/SKILL.md 不存在）')
                continue
            hs = headings(skills[name])
            # 该 skill 引用之后、下一个 skill 引用之前的「...」章
            tail = line[m.end():]
            nxt = re.search(r'`[a-z0-9][a-z0-9-]+`(?=\s*(?:skill|「))', tail)
            seg = tail[:nxt.start()] if nxt else tail
            for sm in re.finditer(r'「([^」]+)」章', seg):
                sec = sm.group(1)
                checked['section'] += 1
                if not any(sec in h for h in hs):
                    errors.append(f'L{no}: skill `{name}` 中找不到章节「{sec}」')
        # 3: 文件引用
        for m in re.finditer(r'`([^`]+)`', line):
            p = resolve_path(m.group(1))
            if p is None:
                continue
            checked['file'] += 1
            if not os.path.exists(p):
                if any(p.lower() == x.lower() or p.lower().startswith(x.lower() + os.sep) for x in KNOWN_EXTERNAL):
                    warns.append(f'L{no}: 外部仓库未 clone 到本机 `{m.group(1)}`（不判失败）')
                else:
                    errors.append(f'L{no}: 文件不存在 `{m.group(1)}` → {p}')

    # 4: 组件速查表类名
    css = open(TEMPLATE_CSS, encoding='utf-8').read()
    sec = re.search(r'## 组件速查表.*?\n(.*?)\n## ', text, re.S)
    if not sec:
        errors.append('找不到「## 组件速查表」章节')
    else:
        for row in sec.group(1).splitlines():
            if not row.startswith('|') or '---' in row:
                continue
            cells = row.split('|')
            if len(cells) < 3:
                continue
            for cls in set(re.findall(r'\.([a-z][a-z0-9-]*)', cells[2])):
                checked['class'] += 1
                if not re.search(r'\.' + re.escape(cls) + r'(?![a-z0-9-])', css):
                    errors.append(f'组件类名 .{cls} 不在 {TEMPLATE_CSS}')

    print(f'[check_skill_pointers] {skill_md}')
    print('  已检查：' + '，'.join(f'{k} {v}' for k, v in checked.items()))
    for w in warns:
        print('   ⚠ ' + w)
    if errors:
        print(f'  FAIL — {len(errors)} 处断链：')
        for e in errors:
            print('   ✗ ' + e)
        sys.exit(1)
    print('  PASS — 0 断链')


if __name__ == '__main__':
    main()

# ymzhu 2026-11-02 17:15
