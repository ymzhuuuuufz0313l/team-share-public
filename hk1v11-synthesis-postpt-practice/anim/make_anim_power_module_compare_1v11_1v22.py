#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_power_module_compare_1v11_1v22.py — v4（Motion Kit v4，整体重写）

power_module_compare_1v11_1v22（1200×688，双条横向柱状图，静态版=站点根目录同名 svg）规格：
- 源样式中和（唯一一处偏离"逐字保留"，assert 保护）：源 .hdr 规则残留
  `animation:sweepMove 6s linear infinite`（静态中因无同名 keyframes 而惰性化）。
  kit CSS 定义了 @keyframes sweepMove，若不中和将使网格/模块名/图例/标题整体平移 160px
  —— 输出中删除该 animation 声明，其余字节不动。
- 入场（总长 ≤2.5s）：
  · 标题 .head(0)；网格/轴线组 .fade(0.05)；模块名双行列 .fade(0.1)
  · 11 组双条块（g0~g10，注释行起整块）.row，0.3s 起 0.1s 递进（末组 1.3+0.55=1.85s）
  · 柔光辉光矩形 .fade(1.5/1.55)；图例 .head(1.65)；基线扫光条 .fade(1.7)
  · 末项 1.7+0.6 = 2.3s ≤ 2.5s
- 稳态（2 族，纯呼吸系；用户 2026-10-28 验收：亮闪扫光极度影响视线，v4.1 数据图表
  不加整区扫光——sweepband 整体移除，生成器不再注入 sweepG 渐变/sweepC clipPath/
  扫光 rect，与 power_compare_hk11 同款处理；基线 .sweep 装饰条为源几何，原样保留）：
  · 行波：模块名标签中 3 个故事行各包一层 .cellwave（opacity .72 呼吸）——
    g0 短编码解码（峰值对）phase 0s、g9 rx_phy(EQ/LEQ)（1V22 独有大条）phase 0.6s、
    g10 MON_DISP（1V22 独有）phase 1.2s，相位错开，名行呼应条区 pulse；
  · pulse ×2（错相位）：g0 峰值对（短编码解码 10294 vs 8590，全图最大条）pulse-t(-0.9s)；
    g9（rx_phy(EQ/LEQ) 4196，1V22 独有大条）pulse(-2.3s)
- 铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无 script；
  kit CSS §2 逐字嵌入；源 defs（softGlow/sweepGrad marker 依赖）/背景 rect 保留；
  源字体 <style> 保留（除上述中和项）；reduced-motion 双保险；确定性幂等。
"""
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import re
import os

BASE = Path(r"E:\project\team-share-public\hk1v11-synthesis-postpt-practice")
SRC = BASE / "power_module_compare_1v11_1v22.svg"
OUT = BASE / "anim" / "power_module_compare_1v11_1v22.svg"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类；与 canonical 站一致）
KIT_CSS = "\n".join([
    ".row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    ".head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}",
    "@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}",
    ".draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}",
    "@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}",
    ".fade{opacity:0;animation:fadeIn .6s ease forwards}",
    "@keyframes fadeIn{to{opacity:1}}",
    ".flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}",
    "@keyframes flow{to{stroke-dashoffset:-100}}",
    ".flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}",
    ".pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}",
    "@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}",
    ".pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}",
    "@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}",
    ".pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}",
    "@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}",
    ".sweepband{opacity:.85;animation:sweepMove 8s linear infinite}",
    "@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}",
    ".dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}",
    "@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}",
    ".march{animation:march 1.5s linear infinite}",
    "@keyframes march{to{stroke-dashoffset:-16}}",
    ".cellwave{animation:wave 2.6s ease-in-out infinite}",
    "@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}",
    ".breathe{animation:br 3.2s ease-in-out infinite}",
    "@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}",
    ".step{animation:stepLit 6s ease-in-out infinite}",
    "@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}",
    "@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}",
])

WAVE_NAMES = {0: "0s", 9: "0.6s", 10: "1.2s"}


def name_wave(blk):
    """模块名标签行：3 个故事行标签（g0 峰值对 / g9 / g10 1V22 独有）各包一层
    .cellwave（opacity .72 呼吸），相位 0 / 0.6 / 1.2s 错开；其余行原样。
    确定性：只依赖源行文本。"""
    out = []
    hit = set()
    for s in blk:
        m = re.search(r'data-label="1" data-g="(\d+)"', s)
        if m and int(m.group(1)) in WAVE_NAMES:
            g = int(m.group(1))
            hit.add(g)
            out.append(f'<g class="cellwave" style="animation-delay:{WAVE_NAMES[g]}">')
            out.append(s)
            out.append("</g>")
        else:
            out.append(s)
    assert hit == set(WAVE_NAMES), f"模块名故事行标签缺失: {sorted(set(WAVE_NAMES) - hit)}"
    return out


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail_nl = raw.endswith(eol)
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[-1].strip() == "</svg>" or lines[-1].strip().startswith("<!--"), "末行异常"
    end = next(i for i, s in enumerate(lines) if s.strip() == "</svg>")

    def find(pred, start=0, stop=None):
        stop = end if stop is None else stop
        for i in range(start, stop):
            if pred(lines[i]):
                return i
        raise AssertionError("anchor not found")

    def find_in(seq, pred, start=0):
        for i in range(start, len(seq)):
            if pred(seq[i]):
                return i
        raise AssertionError("anchor not found in block")

    # ---- 结构锚点 ----
    style_close = find(lambda s: s.strip() == "</style>")
    # 源样式中和：.hdr 残留 animation:sweepMove（kit 定义同名 keyframes，必须去除）
    tgt = ";animation:sweepMove 6s linear infinite}"
    hits = [i for i in range(style_close) if tgt in lines[i]]
    assert len(hits) == 1, f".hdr sweepMove 残留应恰 1 处，实得 {len(hits)}"
    lines[hits[0]] = lines[hits[0]].replace(tgt, "}", 1)

    defs_close = find(lambda s: s.strip() == "</defs>")
    assert 'id="softGlow"' in lines[defs_close - 1] or any('id="softGlow"' in lines[i] for i in range(style_close, defs_close))
    bg_i = find(lambda s: s.strip() == '<rect x="0" y="0" width="1200" height="688" fill="#f4f1ea"/>')
    hdr_gs = [i for i in range(bg_i, end) if lines[i].strip().startswith('<g class="hdr"')]
    assert len(hdr_gs) == 3, f"应有 3 个 <g class=hdr>（网格/模块名/图例），实得 {len(hdr_gs)}"
    grid_g, names_g, legend_g = hdr_gs
    bars_g = find(lambda s: s.strip() == "<g>", names_g)
    bars_g_close = find(lambda s: s.strip() == "</g>", bars_g + 1)
    glow_ls = [i for i in range(bars_g_close + 1, end) if 'class="glow' in lines[i] and lines[i].strip().startswith("<rect")]
    assert len(glow_ls) == 2, f"应有 2 个 glow 矩形，实得 {len(glow_ls)}"
    title_t = find(lambda s: s.strip().startswith("<text") and 'class="hdr"' in s
                   and 'font-weight="bold"' in s, legend_g)
    sweep_r = find(lambda s: s.strip().startswith('<rect class="sweep"'))

    # 柱块：注释行 <!-- gN ... --> 起至下一注释/glow/bars 关闭
    blocks = []
    cmts = [i for i in range(bars_g + 1, bars_g_close) if lines[i].strip().startswith("<!-- g")]
    assert len(cmts) == 11, f"应有 11 个柱块注释，实得 {len(cmts)}"
    for j, c in enumerate(cmts):
        blocks.append((c, cmts[j + 1] if j + 1 < len(cmts) else bars_g_close))

    # ---- 组装（按源序） ----
    o = []
    o.extend(lines[0:style_close + 1])                       # <svg> + 源字体 <style>（已中和 sweepMove）
    o.append("<style>\n" + KIT_CSS + "\n</style>")
    o.extend(lines[style_close + 1:defs_close])              # 源 defs（softGlow/sweepGrad）
    o.append(lines[defs_close])                              # </defs>
    o.extend(lines[defs_close + 1:bg_i + 1])                 # 背景 rect（扫光带已移除）

    # 网格/轴线组 .fade(0.05)
    o.append(lines[grid_g].replace(
        '<g class="hdr">', '<g class="hdr fade" style="animation-delay:0.05s">', 1))
    o.extend(lines[grid_g + 1:names_g])

    # 模块名双行组 .fade(0.1)；3 个故事行标签包 .cellwave（0 / 0.6 / 1.2s）
    o.append(lines[names_g].replace(
        '<g class="hdr">', '<g class="hdr fade" style="animation-delay:0.1s">', 1))
    o.extend(name_wave(lines[names_g + 1:bars_g]))

    # 11 组双条块 .row(0.3+0.1i)；g0 加 pulse-t、g9 加 pulse（注释行之后包住条+值文本）
    o.append(lines[bars_g])                                  # <g>
    pulse_of = {0: ("pulse-t", "-0.9s"), 9: ("pulse", "-2.3s")}
    for i, (bs, be) in enumerate(blocks):
        d = 0.3 + 0.1 * i
        o.append(f'<g class="row" style="animation-delay:{d:.1f}s">')
        blk = lines[bs:be]
        assert blk[0].strip().startswith("<!-- g"), "块首应为注释行"
        o.append(blk[0])
        if i in pulse_of:
            cls, ph = pulse_of[i]
            o.append(f'<g class="{cls}" style="animation-delay:{ph}">')
            o.extend(blk[1:])
            o.append("</g>")
        else:
            o.extend(blk[1:])
        o.append("</g>")
    o.append(lines[bars_g_close])                            # </g>

    # glow 矩形 .fade(1.5 / 1.55)，其余间隔行原样
    for i in range(bars_g_close + 1, legend_g):
        if i == glow_ls[0]:
            o.append(lines[i].replace('class="glow"',
                                      'class="glow fade" style="animation-delay:1.5s"', 1))
        elif i == glow_ls[1]:
            o.append(lines[i].replace('class="glow glow2"',
                                      'class="glow glow2 fade" style="animation-delay:1.55s"', 1))
        else:
            o.append(lines[i])

    # 图例 .head(1.65)
    legend_close = find(lambda s: s.strip() == "</g>", legend_g + 1)
    o.append('<g class="hdr head" style="animation-delay:1.65s">')
    o.extend(lines[legend_g + 1:legend_close])
    o.append("</g>")
    o.extend(lines[legend_close + 1:title_t])                # 空行等

    # 标题 .head(0)（文档位置在尾部，动画时刻仍为最先）
    o.append(lines[title_t].replace('class="hdr"',
                                    'class="hdr head" style="animation-delay:0s"', 1))
    o.extend(lines[title_t + 1:sweep_r])

    # 基线扫光条 .fade(1.7)
    o.append(lines[sweep_r].replace('class="sweep"',
                                    'class="sweep fade" style="animation-delay:1.7s"', 1))
    o.extend(lines[sweep_r + 1:])                            # </svg> + 源尾注释

    text = eol.join(o)
    if tail_nl:
        text += eol
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG {e}"

    def texts(p):
        return Counter(el.text or "" for el in ET.parse(str(p)).getroot().iter(f"{NS}text"))

    try:
        res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    except Exception as e:
        res["text"] = f"NG {e}"

    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"
    res["neutralized"] = "OK" if data.count("animation:sweepMove 6s") == 0 else "NG"

    def svgtag(p):
        m = re.search(r"<svg[^>]*>", Path(p).read_text(encoding="utf-8"))
        return m.group(0) if m else ""

    res["svgtag"] = "OK" if svgtag(SRC) == svgtag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    res["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    res["rmfix"] = "OK" if ".flowdot,.flowtail,.sweepband{display:none!important}" in data else "NG"
    fam = {
        "train": len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
        "pulse": len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
        "sweep": len(re.findall(r'class="[^"]*sweepband', data)),
        "grow": len(re.findall(r'class="[^"]*dashgrow', data)),
        "wave": len(re.findall(r'class="[^"]*cellwave', data)),
        "step": len(re.findall(r'class="[^"]*step"', data)),
    }
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    res["families"] = fam
    return res


def main():
    build()
    res = check()
    data = OUT.read_text(encoding="utf-8")
    print("[make_anim_power_module_compare_1v11_1v22 v4]",
          "row=", len(re.findall(r'class="row"', data)),
          "cellwave=", data.count('class="cellwave"'),
          "pulse=", len(re.findall(r'class="(pulse|pulse-t)"', data)),
          "fade=", data.count('fade" style'))
    ok = True
    for k, v in res.items():
        if k != "families":
            print(f"  {k}: {v}")
            ok &= str(v) == "OK" or str(v).startswith("OK(")
    print("  families:", res["families"])
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-10-28 18:46
