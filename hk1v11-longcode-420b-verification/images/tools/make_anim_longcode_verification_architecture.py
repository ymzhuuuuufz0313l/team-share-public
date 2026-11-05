#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_anim_longcode_verification_architecture.py — v4（1105 · 2026-11 现状重绘版）

新版静态图（generate_longcode_report_svgs.py · gen_architecture，1200×1150）：
Test/Config（192 case 维度矩阵）→ TX（任务族+故障注入+训练包+C-model 闭环）
→ Transaction/Driver（BOE 回放）→ RX DUT（解码链 44-bit/K3 延 4 拍 + RTL 编码
TX 通路）→ 体系扩展（MULTI_CHIP / BCC / checker_420b 遗留）→ 离线验证路径
（0717 建立存续）→ 版本基线条（0721→1028 波次 → HEAD a7130ba7）。
旧版 0720v1 组件框已归档（archive/20260720/）。

动效规格（沿 MOTION_KIT.md §6.1 骨架，按新版 7 行结构重排）：
- 入场：标题(0) → Test(.15) → TX(.35) → Trans(.55) → RX(.6) → 体系(.8)
  → 离线(1.0) → 版本(1.2) → 箭头 draw/fade（0.75~1.55，= max(两端面板)+0.55）
  → 图例 head(1.5)。一次性总长 ≤2.15s ≤2.5s。
- draw：实线箭头（Test→TX/RX、TX 内部、TX→Trans、Trans→Driver、Driver→RX、
  RX 内部 5 段、离线内部 4 段）；虚线（橙配置/tap 绿廊/紫期望值）用 fade，
  不覆盖 dasharray。
- 稳态·列车：Driver→RX 串行链路 path（≈290px ≥80px 规则内）蓝 2 包+链色
  flowtail（4.2s，-0.6/-2.7）；tap 绿色外廊（≈950px）绿 2 包（4.2s，
  -1.7/-3.8 与蓝错相）。离线链内部箭头仅 36px <80px → 按 v4.3 短箭头规则
  不挂列车（不回归 0720 版行为）。
- 稳态·脉冲：TAP 徽章 pulse-b(-1.4s)；✅ verdict 盒 pulse-t(-0.7s)；
  checker_420b 遗留改造盒 pulse(-2.1s 琥珀警示)。
- 稳态·生长：紫色「期望值」两段连接器（dump 走廊 + 逐区域 diff）.dashgrow
  （3.2s/-1.6s 与 2.8s/-0.5s 相位错开）。
- 稳态族：列车 / 脉冲 / 生长 = 3 族（≤4 上限内）；不加 cellwave/breathe/sweep。

铁律：源 SVG 只读；text 多重集 / svg 开标签 / 几何颜色零改动；纯 CSS 无
script；kit CSS §2 逐字嵌入为行 3；源 defs + 背景 rect 保留；reduced-motion
用 kit 原文；确定性幂等（只依赖源 SVG）。
"""
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

BASE = Path(r"E:\project\team-share-public\hk1v11-longcode-420b-verification")
SRC = BASE / "images" / "longcode_verification_architecture.svg"
OUT = BASE / "images" / "anim" / "longcode_verification_architecture.svg"
NAME = "make_anim_longcode_verification_architecture"

# MOTION_KIT.md §2 — Motion Kit CSS v4（逐字嵌入，不增删类）
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


def idx(lines, *subs, lo=0):
    hits = [i for i in range(lo, len(lines)) if all(s in lines[i] for s in subs)]
    assert len(hits) == 1, f"锚点非唯一命中 {subs}: {hits}"
    return hits[0]


def tag_draw(line, delay):
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return (line.rstrip()[:-2].rstrip()
            + f' class="draw" pathLength="100" style="animation-delay:{delay}s"/>')


def tag_class(line, cls, extra=""):
    assert line.rstrip().endswith("/>"), f"非自闭合元素: {line}"
    return line.rstrip()[:-2].rstrip() + f' class="{cls}"{extra}/>'


def build():
    raw = SRC.read_text(encoding="utf-8", newline="")
    eol = "\r\n" if "\r\n" in raw else "\n"
    lines = raw.split(eol)
    tail = raw.endswith(eol)
    assert lines[0].lstrip().startswith("<svg"), "line1 应为 <svg>"
    assert lines[1].lstrip().startswith("<style"), "line2 应为字体 <style>"
    assert lines[-1].strip() == "</svg>", "末行应为 </svg>"

    # ---- 结构锚点（0 基；全部 assert 保护） ----
    title = idx(lines, "整体架构（2026-11 现状）")
    subtitle = title + 1
    test_c = idx(lines, '<rect x="40" y="88"')
    tx_c = idx(lines, '<rect x="40" y="204"')
    trans_c = idx(lines, '<rect x="40" y="572"')
    rx_c = idx(lines, '<rect x="776" y="204"')
    sys_c = idx(lines, '<rect x="40" y="694"')
    off_c = idx(lines, '<rect x="40" y="842"')
    ver_c = idx(lines, '<rect x="40" y="1050"')
    assert title < test_c < tx_c < trans_c < rx_c < sys_c < off_c < ver_c
    tap_badge = idx(lines, '<rect x="1072" y="244"')
    tap_txt = tap_badge + 1
    assert ">TAP<" in lines[tap_txt]
    checker_box = idx(lines, '<rect x="796" y="724"')   # 1106：Row4 三盒 726→724
    checker_end = idx(lines, "正式比对启用前的改造点")
    report_box = idx(lines, '<rect x="566" y="960"')
    report_end = idx(lines, "全对 ✅")
    leg1 = idx(lines, '<line x1="60" y1="1144"')      # 1106：图例 1140→1148
    a_test_tx = idx(lines, '<line x1="375" y1="188"')
    a_test_rx = idx(lines, '<line x1="955" y1="188"')
    a_txin1 = idx(lines, '<line x1="336" y1="330"')
    a_txin2 = idx(lines, '<line x1="534" y1="320"')
    a_tx_trans = idx(lines, '<line x1="375" y1="556"')
    a_trans_drv = idx(lines, '<line x1="364" y1="628"')
    a_link = idx(lines, "<path", "M 712 628")
    a_link_label = a_link + 1
    assert "串行链路" in lines[a_link_label]
    a_rxin = [idx(lines, f'<line x1="968" y1="{y}"') for y in (300, 370, 440, 510, 598)]  # 1106：末两段随 dout/RTL TX 下移
    a_tap = idx(lines, "<path", "M 1136 269")
    a_tap_label = a_tap + 1
    assert "tap DATA_ALIGN_PRE" in lines[a_tap_label]
    a_purp = idx(lines, "<path", "M 204 678")
    a_off1 = idx(lines, '<line x1="294" y1="910"')
    a_off2 = idx(lines, '<line x1="526" y1="910"')
    a_off3 = idx(lines, '<line x1="808" y1="910"')
    a_off4 = idx(lines, '<line x1="944" y1="940"')
    a_diff = idx(lines, '<line x1="344" y1="984"')
    a_diff_label = idx(lines, "逐区域 diff")
    end = len(lines) - 1

    # ---- 组装 ----
    o = [lines[0], lines[1], "<style>\n" + KIT_CSS + "\n</style>"]
    o.extend(lines[2:title])          # defs + 背景白 rect（铁律 4）

    def emit_range(a, b):
        o.extend(lines[a:b])

    # 标题 head(0)
    o.append('<g class="head">')
    emit_range(title, subtitle + 1)
    o.append("</g>")

    # Test/Config row(.15)
    o.append('<g class="row" style="animation-delay:0.15s">')
    emit_range(test_c, tx_c)
    o.append("</g>")

    # TX row(.35)
    o.append('<g class="row" style="animation-delay:0.35s">')
    emit_range(tx_c, trans_c)
    o.append("</g>")

    # Transaction/Driver row(.55)
    o.append('<g class="row" style="animation-delay:0.55s">')
    emit_range(trans_c, rx_c)
    o.append("</g>")

    # RX row(.6)：TAP 徽章 pulse-b 嵌套
    o.append('<g class="row" style="animation-delay:0.6s">')
    emit_range(rx_c, tap_badge)
    o.append('<g class="pulse-b" style="animation-delay:-1.4s">')
    emit_range(tap_badge, tap_txt + 1)
    o.append("</g>")
    emit_range(tap_txt + 1, sys_c)
    o.append("</g>")

    # 体系扩展 row(.8)：checker_420b 遗留盒 pulse（琥珀警示）嵌套
    o.append('<g class="row" style="animation-delay:0.8s">')
    emit_range(sys_c, checker_box)
    o.append('<g class="pulse" style="animation-delay:-2.1s">')
    emit_range(checker_box, checker_end + 1)
    o.append("</g>")
    emit_range(checker_end + 1, off_c)
    o.append("</g>")

    # 离线验证 row(1.0)：✅ verdict 盒 pulse-t 嵌套
    o.append('<g class="row" style="animation-delay:1.0s">')
    emit_range(off_c, report_box)
    o.append('<g class="pulse-t" style="animation-delay:-0.7s">')
    emit_range(report_box, report_end + 1)
    o.append("</g>")
    emit_range(report_end + 1, ver_c)
    o.append("</g>")

    # 版本基线 row(1.2)
    o.append('<g class="row" style="animation-delay:1.2s">')
    emit_range(ver_c, a_test_tx)
    o.append("</g>")

    # ---- 箭头区（delay = max(两端面板)+0.55；虚线不 draw 只 fade） ----
    o.append('<g class="fade" style="animation-delay:0.75s">')
    o.append(tag_draw(lines[a_test_tx], 0.75))
    o.append(tag_draw(lines[a_test_tx + 1], 0.75))          # x1=660 同拍
    o.append(lines[a_test_rx])                               # 橙虚线：fade 原样
    o.append("</g>")
    o.append('<g class="fade" style="animation-delay:0.9s">')
    o.append(tag_draw(lines[a_txin1], 0.9))
    o.append(tag_draw(lines[a_txin2], 0.9))
    o.append("</g>")
    o.append('<g class="fade" style="animation-delay:1.1s">')
    o.append(tag_draw(lines[a_tx_trans], 1.1))
    o.append(tag_draw(lines[a_trans_drv], 1.1))
    o.append("</g>")
    # Driver→RX 串行链路（draw 1.15）+ 蓝色列车 2 包 + 链色拖尾（4.2s）
    o.append('<g class="fade" style="animation-delay:1.15s">')
    o.append(tag_draw(lines[a_link], 1.15))
    o.append(lines[a_link_label])
    for dl in (-0.6, -2.7):
        o.append('<path class="flowdot" d="M 712 628 L 760 628 L 760 269 L 800 269" '
                 f'stroke="#2563eb" pathLength="100" style="animation-duration:4.2s;animation-delay:{dl}s"/>')
        o.append('<path class="flowtail" d="M 712 628 L 760 628 L 760 269 L 800 269" '
                 f'stroke="#2563eb" pathLength="100" style="animation-duration:4.2s;animation-delay:{dl}s"/>')
    o.append("</g>")
    # RX 内部 5 段 draw 1.15
    o.append('<g class="fade" style="animation-delay:1.15s">')
    for i in a_rxin:
        o.append(tag_draw(lines[i], 1.15))
    o.append("</g>")
    # tap 绿色外廊（虚线 → fade 原样 1.15）+ 绿色列车 2 包（4.2s，与蓝错相）
    o.append('<g class="fade" style="animation-delay:1.15s">')
    o.append(lines[a_tap])
    o.append(lines[a_tap_label])
    for dl in (-1.7, -3.8):
        o.append('<path class="flowdot" d="M 1136 269 L 1178 269 L 1178 834 L 50 834 L 50 910 L 62 910" '
                 f'stroke="#059669" pathLength="100" style="animation-duration:4.2s;animation-delay:{dl}s"/>')
    o.append("</g>")
    # 紫色期望值走廊（虚线）：dashgrow 稳态生长（3.2s/-1.6s）
    o.append('<g class="fade" style="animation-delay:1.15s">')
    o.append(tag_class(lines[a_purp], "dashgrow",
                        ' style="animation-duration:3.2s;animation-delay:-1.6s"'))
    o.append("</g>")
    # 离线链内部 4 段 draw 1.55 + 逐区域 diff（紫虚线 dashgrow 2.8s/-0.5s）+ 标签
    o.append('<g class="fade" style="animation-delay:1.55s">')
    for i in (a_off1, a_off2, a_off3, a_off4):
        o.append(tag_draw(lines[i], 1.55))
    o.append(tag_class(lines[a_diff], "dashgrow",
                        ' style="animation-duration:2.8s;animation-delay:-0.5s"'))
    o.append(lines[a_diff_label])
    o.append("</g>")

    # 图例 head(1.5)
    o.append('<g class="head" style="animation-delay:1.5s">')
    emit_range(leg1, end)
    o.append("</g>")

    o.append(lines[end])
    text = eol.join(o).replace("\n", eol) + (eol if tail else "")
    OUT.write_text(text, encoding="utf-8", newline="")


NS = "{http://www.w3.org/2000/svg}"


def check():
    import os
    res = {}
    try:
        ET.parse(str(OUT))
        res["xml"] = "OK"
    except ET.ParseError as e:
        res["xml"] = f"NG {e}"
    texts = lambda p: Counter(el.text or "" for el in
                              ET.parse(str(p)).getroot().iter(f"{NS}text"))
    res["text"] = "OK" if texts(SRC) == texts(OUT) else "NG"
    data = OUT.read_text(encoding="utf-8")
    res["noscript"] = "OK" if "<script" not in data else "NG"
    res["nosmil"] = "OK" if "<animate" not in data else "NG"
    res["keyframes"] = "OK" if data.count("@keyframes") >= 10 else "NG"
    tag = lambda p: re.search(r"<svg[^>]*>", p.read_text(encoding="utf-8")).group(0)
    res["svgtag"] = "OK" if tag(SRC) == tag(OUT) else "NG"
    res["size"] = "OK" if os.path.getsize(OUT) > 1024 else "NG"
    res["kit_train"] = "OK" if re.search(r"\.flowdot\{[^}]*stroke-width:3\.5", data) else "NG"
    res["kit_pulse"] = "OK" if re.search(r"\.pulse(-[tb])?\{[^}]*transform-box:fill-box", data) else "NG"
    res["kit_sweep"] = "OK" if "var(--sweepP" in data else "NG"
    rm = re.search(r"prefers-reduced-motion.*?flowdot,.flowtail,.sweepband\{display:none!important\}", data, re.S)
    res["rmfix"] = "OK" if (rm and re.search(r"prefers-reduced-motion.*?opacity:1!important", data, re.S)) else "NG"
    res["no_glow"] = "OK" if not re.search(r'class="[^"]*glow-[bgo]', data) else "NG"
    fast = [m.group(1) for m in re.finditer(r'flow(?:dot|tail)[^"]*"[^>]*animation-duration:([0-9.]+)s', data)]
    res["train>=2.4s"] = "OK" if all(float(x) >= 2.4 for x in fast) else f"NG({','.join(fast)})"
    fam = {
        "train":   len(re.findall(r'class="[^"]*(flowdot|flowtail)', data)),
        "pulse":   len(re.findall(r'class="[^"]*pulse(-[tb])?', data)),
        "sweep":   len(re.findall(r'class="[^"]*sweepband', data)),
        "grow":    len(re.findall(r'class="[^"]*dashgrow', data)),
        "wave":    len(re.findall(r'class="[^"]*cellwave', data)),
        "step":    len(re.findall(r'class="[^"]*step"', data)),
    }
    n_fam = sum(1 for v in fam.values() if v > 0)
    res["steady>=2fam"] = f"OK({n_fam})" if n_fam >= 2 else f"NG({n_fam})"
    for k, v in res.items():
        print(f"  {k}: {v}")
    hard = ("xml", "text", "noscript", "nosmil", "keyframes", "svgtag", "size",
            "kit_train", "kit_pulse", "kit_sweep", "rmfix", "no_glow", "train>=2.4s")
    ok = all(str(res.get(k, "NG")) == "OK" or str(res.get(k, "NG")).startswith("OK(") for k in hard) \
        and str(res["steady>=2fam"]).startswith("OK")
    return ok


def main():
    build()
    data = OUT.read_text(encoding="utf-8")
    print(f"[{NAME} v4]",
          f"draw={data.count('class=\"draw\"')}",
          f"dashgrow={data.count('class=\"dashgrow\"')}",
          f"flowdot={data.count('class=\"flowdot\"')}",
          f"flowtail={data.count('class=\"flowtail\"')}",
          f"pulse={data.count('class=\"pulse\"')}",
          f"row={data.count('class=\"row\"')}",
          f"head={data.count('class=\"head\"')}",
          f"fade={data.count('class=\"fade\"')}")
    ok = check()
    print("  RESULT:", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
# ymzhu 2026-11-05 15:39
