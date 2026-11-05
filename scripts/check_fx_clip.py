# -*- coding: utf-8 -*-
"""check_fx_clip.py — fx 引擎 clip:text 特效完整性门禁（2026-11-05，fxFlowShine 事故后新增）

背景：fxFlowShine v2.1 用单层 no-repeat 渐变 + color:transparent，始/终态各 ~24% 落图外
导致标题残缺不可见（PAGE_FX §4 铁律「双层背景恒定着色」被违反但无门禁拦截，2026-11-05
ymzhu 报告两页复现）。本脚本把铁律变成检查：

规则：fx.css 中任何同时含 `background-clip: text` 与 `color: transparent` 的声明块，
必须满足：
  R1. background-image 至少 2 层（逗号分隔）；
  R2. 存在一层"恒定着色层"——纯色 linear-gradient（起止同色）且对应 background-size
      为 100% 100%（或该层无显式 size 时按 auto=元素尺寸亦视为恒定覆盖，本仓约定
      要求显式 100% 100% 以防歧义）；
  R3. 动画若改 background-position（fxFlowShine 型），keyframes 目标值的层数须与
      声明块层数一致。

用法：python check_fx_clip.py [fx.css 路径，默认扫描全仓 9 处字节一致副本的代表=根级]
退出码：0=全过；1=有违反（逐条列出）
"""
import re
import sys
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent


def strip_comments(css: str) -> str:
    return re.sub(r'/\*.*?\*/', '', css, flags=re.S)


def iter_blocks(css: str):
    """产出 (selector, body) 规则块；@supports/@media 等条件组递归进入内层。"""
    depth = 0
    buf = []
    start = None
    sel_start = None
    i = 0
    n = len(css)
    while i < n:
        ch = css[i]
        if ch == '{':
            if depth == 0:
                sel = ''.join(buf).strip()
                start = i
                buf = []
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                body = css[start + 1:i]
                if sel.startswith('@keyframes'):
                    yield sel, body  # keyframes 内部由 collect_keyframes 单独递归
                elif sel.startswith('@') and '{' in body:
                    # 条件组（@supports/@media）：递归产出内层真规则
                    yield from iter_blocks(body)
                else:
                    yield sel, body
                buf = []
            elif depth < 0:
                depth = 0
        elif depth == 0:
            buf.append(ch)
        i += 1


def decls(body: str) -> dict:
    out = {}
    for part in body.split(';'):
        if ':' in part:
            k, v = part.split(':', 1)
            out[k.strip()] = v.strip()
    return out


def bg_layers(value: str):
    """按顶层逗号切分 background-image 层（忽略函数内逗号）。"""
    layers, depth, cur = [], 0, []
    for ch in value:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        if ch == ',' and depth == 0:
            layers.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    if cur:
        layers.append(''.join(cur).strip())
    return layers


def is_solid_layer(layer: str) -> bool:
    """纯色渐变层：linear-gradient 起止色标同色（比较颜色 token，忽略 0%/100% 位置后缀）。"""
    m = re.match(r'linear-gradient\((.*)\)$', layer, flags=re.S)
    if not m:
        return False
    stops = [s.strip() for s in bg_layers(m.group(1))]
    color_keys = []
    for s in stops:
        t = s.split()[0] if s else ''
        if re.match(r'^(#|rgba?\(|hsla?\(|var\()', t) or re.match(r'^[a-zA-Z]+$', t):
            color_keys.append(t)
    return len(color_keys) >= 2 and color_keys[0] == color_keys[-1]


def check(fx_css: pathlib.Path, css: str, keyframes: dict) -> list:
    issues = []
    for sel, body in iter_blocks(css):
        d = decls(body)
        if 'background-clip' not in d or 'color' not in d:
            continue
        if 'text' not in d['background-clip'] or d['color'] != 'transparent':
            continue
        layers = bg_layers(d.get('background-image', ''))
        # R1 层数
        if len(layers) < 2:
            issues.append(f"[R1] {sel}: clip:text + color:transparent 但 background-image 仅 {len(layers)} 层（单层 no-repeat 位移动画始/终态必残缺）")
            continue
        # R2 恒定着色层
        sizes = [s.strip() for s in d.get('background-size', '').split(',')]
        solid = False
        for idx, layer in enumerate(layers):
            if is_solid_layer(layer):
                sz = sizes[idx].strip() if idx < len(sizes) else 'auto'
                if sz in ('100% 100%', '100%'):
                    solid = True
        if not solid:
            issues.append(f"[R2] {sel}: 双层背景中无『纯色渐变 + size 100%』恒定着色层（始/终/中断定格态文字可能不可见）")
        # R3 keyframes position 层数
        anim = d.get('animation', '')
        m = re.search(r'(fx\w+)', anim)
        if m and m.group(1) in keyframes:
            kf = keyframes[m.group(1)]
            for kf_sel, kf_body in kf:
                kd = decls(kf_body)
                if 'background-position' in kd:
                    n = len([p for p in bg_layers_positions(kd['background-position'])])
                    if n != len(layers):
                        issues.append(f"[R3] {sel}: 动画 {m.group(1)} 的 background-position {n} 层 ≠ 声明块 {len(layers)} 层")
    return issues


def bg_layers_positions(value: str):
    return [p for p in value.split(',') if p.strip()]


def collect_keyframes(css: str) -> dict:
    kf = {}
    for sel, body in iter_blocks(css):
        m = re.match(r'@keyframes\s+([\w-]+)', sel)
        if m:
            kf[m.group(1)] = list(iter_blocks(body))
    return kf


def main():
    target = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / 'fx.css'
    css = strip_comments(target.read_text(encoding='utf-8'))
    kf = collect_keyframes(css)
    issues = check(target, css, kf)
    print(f"[check_fx_clip] {target} — clip:text 规则完整性")
    if issues:
        for it in issues:
            print('  FAIL', it)
        sys.exit(1)
    print('  PASS（所有 clip:text + transparent 块均有恒定着色层，动画层数一致）')
    sys.exit(0)


if __name__ == '__main__':
    main()

# ymzhu 2026-11-05 14:55
