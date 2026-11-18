#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_chip_sel_map.py — chip_sel0/1 寄存器默认字节映射（静态事实源）生成器（1111v1 代）。

数据源（唯一事实源）:  images/data/chip_sel{0,1}_register_map_1111v1.json
  （由 HK1V11/script/reg_site_1111/derive_chip_sel_from_excel.py 从
    HK1V11_Register_20261111.xlsm 的 Reg_1V11 + Reg_description_F_CHIP_SEL={0,1}
    机器派生：位图骨架取自 Reg_1V11，位级明细与复位值以 F 页为准；不再使用任何
    从旧 SVG 反向提取的数据）
输出:                  images/chip_sel{0,1}_register_map.svg（主名位=当前采纳版）

单源分层：数据 json → 本生成器 → 静态 SVG；动画版由 images/anim/make_anim_chip_sel{0,1}.py
从本输出派生（源只读）。数字全部来自 json：每行的地址/dec/POR 字节/字段名/复位值逐项指名；
生成器断言每行位 7..0 恰好被字段覆盖一次（Σ片 == 8 bit，无重叠无空洞）。
几何从位区间推导：x=170+82*(7-bit_high)，w=82*n-1；行 y 由 idx 推导（间距 52）。
复跑幂等：内容未变时 SKIPPED 不写（--force 可强制）；--out DIR 预演到目录。

用法: python images/tools/gen_chip_sel_map.py [--out DIR] [--force]
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # = images/
from _siteio import out_path, write_text_lf, is_dry_run  # noqa: E402

BASE = Path(__file__).resolve().parents[1]          # images/
X0, PITCH, Y0, RH = 170, 82, 152, 52
WIDTH = 1100

SELF_SIG = "<!-- gen_chip_sel_map.py 1111v1 -->"


def render(d):
    h = d["height"]
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{h}" '
           f'viewBox="0 0 {WIDTH} {h}" style="background:#ffffff">',
           f'<rect width="{WIDTH}" height="{h}" fill="#ffffff"/>']
    out.extend(d["header"])
    for r in d["rows"]:
        idx = r["idx"]
        ay = Y0 + RH * idx                     # addr text y
        top = ay - 28                          # cell top
        if r.get("kind") == "gap":
            # 折叠行（整段无有效字段）：只有地址区间标签，无位格、无 POR 字节
            out.append(f'<text x="158" y="{ay}.0" text-anchor="end" '
                       f'font-size="{r["label_fs"]}" font-weight="600" '
                       f'fill="{r["label_fill"]}">{r["addr"]}</text>')
            for kind, payload in r["items"]:
                out.append(payload)
            continue
        out.append(f'<text x="158" y="{ay}.0" text-anchor="end" font-size="14" '
                   f'font-weight="600" fill="#1e293b">{r["addr"]} ({r["dec"]})</text>')
        out.append(f'<rect x="842" y="{ay-18}.0" width="64" height="26" fill="#f8fafc" '
                   f'stroke="#e2e8f0" stroke-width="1" rx="13"/>')
        out.append(f'<circle cx="854" cy="{ay-5}.0" r="3.5" fill="{r["por_color"]}"/>')
        out.append(f'<text x="877.0" y="{ay-1}.0" text-anchor="middle" font-size="12" '
                   f'font-weight="700" fill="#1e293b" font-family="Consolas, Monaco, monospace">'
                   f'{r["por_byte"]}</text>')
        # Σ片断言：位 7..0 恰好一次（折叠行无字段，跳过）
        cov = []
        for f in r["fields"]:
            cov.extend(range(f["bit_low"], f["bit_high"] + 1))
        if r["fields"]:
            assert sorted(cov) == list(range(8)), (r["addr"], sorted(cov))
        fi = 0
        for kind, payload in r["items"]:
            if kind == "raw":
                out.append(payload)
                continue
            f = r["fields"][fi]; fi += 1
            n = f["bit_high"] - f["bit_low"] + 1
            x = X0 + PITCH * (7 - f["bit_high"])
            w = PITCH * n - 1
            cx = x + w / 2
            sw = f'stroke-width="{f["stroke_width"]}"' if f["stroke_width"] != "1" else 'stroke-width="1"'
            out.append(f'<rect x="{x}" y="{top}" width="{w}" height="46" fill="{f["fill"]}" '
                       f'stroke="{f["stroke"]}" {sw} rx="4"/>')
            out.append(f'<text x="{cx:.1f}" y="{top+21}.0" text-anchor="middle" font-size="{f["name_fs"]}" '
                       f'font-weight="500" fill="#1e293b">{f["name"]}</text>')
            out.append(f'<text x="{cx:.1f}" y="{top+35}.0" text-anchor="middle" font-size="{f["value_fs"]}" '
                       f'fill="#64748b">{f["value"]}</text>')
        assert fi == len(r["fields"]), r["addr"]
    out.extend(d["tail"])
    out.append("</svg>")
    return "\n".join(out)


def _derive_dir():
    """找 HK1V11/script/reg_site_1111（与 team-share-public 同级的工作区）。"""
    import os
    env = os.environ.get("CPUWR_DERIVE_DIR")
    cands = [Path(env)] if env else []
    for p in [BASE] + list(BASE.parents):
        cands.append(p / "HK1V11" / "script" / "reg_site_1111")
    for c in cands:
        if (c / "derive_chip_sel_from_excel.py").exists():
            return c
    return None


def assert_single_source(d, sel):
    """F8 闸门：渲染前断言「数据 JSON == 现场从 excel 提取重新派生的结果」。

    这是把「图内容 ↔ 指定数据源」的一致性从人工审查搬进生成器自检：
    JSON 若被手改、或 excel 已换代而 JSON 未重派生，生成器直接失败，不再出图。
    """
    ddir = _derive_dir()
    if ddir is None:
        raise SystemExit("[gen_chip_sel_map] FAIL: 找不到 HK1V11/script/reg_site_1111"
                         "（excel→JSON 派生脚本），无法执行单源断言；"
                         "请设置 CPUWR_DERIVE_DIR 指向该目录")
    sys.path.insert(0, str(ddir))
    import derive_chip_sel_from_excel as D          # noqa: E402
    extract = json.loads(D.EXTRACT.read_text(encoding="utf-8"))
    exp = D.derive(extract)[sel]
    if exp != d:
        D.flatten  # noqa: B018  (保持 import 语义清晰)
        cur_f, exp_f = D.flatten(d), D.flatten(exp)
        diffs = [k for k in sorted(set(cur_f) | set(exp_f)) if cur_f.get(k) != exp_f.get(k)][:10]
        raise SystemExit("[gen_chip_sel_map] FAIL: sel%d 数据 JSON 与 excel 派生件不一致：%s"
                         % (sel, diffs))
    print(f"[gen_chip_sel_map] sel{sel}: 单源断言 OK（JSON == excel 派生，{d['n_rows']} 行）")
    # 行数断言：真实寄存器行数必须等于 excel 侧「有非 Reserved 字段」的地址数。
    # 防的是「某地址在 excel 有字段但图里整行消失」（0x1F 在 cs=0 曾整行缺失）。
    n_real = sum(1 for r in d["rows"] if r.get("kind") != "gap")
    n_expect = len(D.excel_expected_addrs(extract, sel))
    if n_real != n_expect:
        missing = sorted(D.excel_expected_addrs(extract, sel)
                         - {int(r["addr"], 16) for r in d["rows"]
                            if r.get("kind") != "gap"})
        raise SystemExit("[gen_chip_sel_map] FAIL: sel%d 行数断言失败："
                         "图内真实行 %d != excel 应有行 %d，缺 %s"
                         % (sel, n_real, n_expect,
                            ", ".join("0x%02X" % a for a in missing) or "（重复/多余）"))
    print(f"[gen_chip_sel_map] sel{sel}: 行数断言 OK（真实行 {n_real} == excel 应有 {n_expect}）")


def main():
    for sel in (0, 1):
        data_p = BASE / "data" / f"chip_sel{sel}_register_map_1111v1.json"
        d = json.loads(data_p.read_text(encoding="utf-8"))
        assert_single_source(d, sel)
        svg = render(d)
        dst = out_path(f"images/chip_sel{sel}_register_map.svg")
        if dst.exists() and dst.read_text(encoding="utf-8") == svg and not is_dry_run():
            print(f"[gen_chip_sel_map] sel{sel}: SKIPPED (byte-identical)")
            continue
        write_text_lf(dst, svg)
        print(f"[gen_chip_sel_map] sel{sel}: wrote {dst} ({len(svg)} bytes)")


if __name__ == "__main__":
    main()
# ymzhu 2026-11-18 17:13