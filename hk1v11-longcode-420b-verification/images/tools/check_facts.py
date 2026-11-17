#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""单一数据源一致性闸门（facts.json ↔ 生成器产物 ↔ 页面文字）。

背景（审查项 F02：业务数字硬编码散落在生成器与页面里）
------------------------------------------------------
本站在多处写了同一批业务数字（192 个 case、分辨率/FPS/PORT 分布、维度族计数）。
历史上这些数字被手工抄进生成器、SVG 与 HTML，一处改动就要人肉同步，于是出现了
`DPLC_MODE1 ×173` 这种与事实源（case 目录名计数 104）不符的漂移。

修复后的事实源是 `images/tools/data/facts.json`，由 `extract_facts.py` 从 case 源统计生成：

    python images/tools/extract_facts.py --src <HK1V11 根或 DV_TCON_C/top/tests> \
                                         --out images/tools/data/facts.json

本闸门不生成任何东西，只做 **只读核对**，十几毫秒跑完，适合塞进交付检查：

  1. facts.json 内部自洽：各维度计数合计必须等于 case_count；
  2. 生成器产物：`images/delta_case_matrix.svg` 与 `images/anim/delta_case_matrix.svg`
     里的分辨率/FPS/PORT/维度族/合计文字必须与 facts.json 一致（静/动两版同源）；
  3. 页面文字：`cases.html` 的维度表必须与 facts.json 一致；
  4. 全站禁止再出现已知的漂移值 `DPLC_MODE1 ×173` / `（173 处标注）`。

用法：
    python images/tools/check_facts.py            # 默认站点根由 site_paths 解析
    python images/tools/check_facts.py --site <dir>

退出码：0 = 全一致；1 = 有不一致（逐条打印）。

"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_paths import site_base  # noqa: E402

RES_ORDER = ["1440", "1920", "2560", "2880", "3456", "3840"]
FPS_ORDER = ["60", "120", "144", "165", "180", "240", "280", "360"]
PORT_ORDER = ["6", "8", "12", "24"]

# 已知的历史漂移值：全站不允许再出现（docs/ 不在站点内，另行标记待用户修笔误）
FORBIDDEN = [
    ("DPLC_MODE1 ×173", "维度族计数据应为 facts.json 的 name_counts.DPLC_MODE1"),
    ("（173 处标注）", "cases.html 维度表口径应为 case 目录名计数"),
]


def load_facts(site: Path):
    p = site / "images" / "tools" / "data" / "facts.json"
    if not p.exists():
        raise SystemExit(f"[check_facts] 缺少事实源：{p}")
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def check_internal(facts):
    """1) facts.json 内部自洽。"""
    errs = []
    n = facts["case_count"]
    for dim, order in (("resolution", RES_ORDER), ("fps", FPS_ORDER)):
        got = sum(facts[dim][k] for k in order)
        if got != n:
            errs.append(f"facts.{dim} 合计 {got} != case_count {n}")
    port = facts["port"]
    got = sum(port.get(k, 0) for k in PORT_ORDER) + port.get("other", 0)
    if got != n:
        errs.append(f"facts.port 合计 {got} != case_count {n}")
    for key in ("DPLC_MODE1", "DPLC_GROUP1", "SDC0"):
        if key not in facts["name_counts"]:
            errs.append(f"facts.name_counts 缺少 {key}")
    return errs


def expected_strings(facts):
    """2/3) 由 facts 推导出「必须逐字出现」的串。"""
    n = facts["case_count"]
    nc = facts["name_counts"]
    exp = []
    for k in RES_ORDER:
        exp.append(f"H{k}")
    for k in FPS_ORDER:
        exp.append(f"{k} · {facts['fps'][k]}")
    for k in PORT_ORDER:
        exp.append(f"{k} · {facts['port'].get(k, 0)}")
    exp.append(f"DPLC_MODE1 ×{nc['DPLC_MODE1']}")
    exp.append(f"DPLC_GROUP1 ×{nc['DPLC_GROUP1']}")
    exp.append(f"SDC0 ×{nc['SDC0']}")
    res_sum = "+".join(str(facts["resolution"][k]) for k in RES_ORDER)
    exp.append(f"合计 {res_sum} = {n}")
    return exp


def check_svg(path: Path, exp):
    errs = []
    if not path.exists():
        return [f"{path} 不存在"]
    text = path.read_text(encoding="utf-8")
    for e in exp:
        if e not in text:
            errs.append(f"{path.name}: 缺少期望串 {e!r}")
    return errs


def check_cases_page(path: Path, facts):
    """cases.html 维度表逐项核对。"""
    errs = []
    if not path.exists():
        return ["cases.html 不存在"]
    text = path.read_text(encoding="utf-8")
    nc = facts["name_counts"]
    rows = {
        "分辨率": "| 分辨率 ×6 | " + " / ".join(
            f"H{k}（{facts['resolution'][k]}）" for k in RES_ORDER),
        "FPS": "| FPS ×8 | " + " / ".join(
            f"{k}（{facts['fps'][k]}）" for k in FPS_ORDER),
        "PORT": "| PORT_NUM ×4 | " + " / ".join(
            f"{k}（{facts['port'].get(k, 0)}）" for k in PORT_ORDER),
        "DPLC": f"`DPLC_MODE1`（{nc['DPLC_MODE1']} 处标注）× `DPLC_GROUP1`（{nc['DPLC_GROUP1']}）",
        "SDC": f"`SDC0` 变体 {nc['SDC0']}",
    }
    # 表格单元格里的空格排版不影响语义，比对前压缩空白（数字与标点仍逐字核对）
    flat = re.sub(r"\s+", "", text)
    for label, frag in rows.items():
        if re.sub(r"\s+", "", frag) not in flat:
            errs.append(f"cases.html 维度表[{label}] 期望片段缺失：{frag!r}")
    return errs


def check_forbidden(site: Path):
    errs = []
    for p in sorted(site.glob("*.html")):
        t = p.read_text(encoding="utf-8")
        for bad, why in FORBIDDEN:
            if bad in t:
                errs.append(f"{p.name}: 出现禁用漂移值 {bad!r}（{why}）")
    for p in sorted((site / "images").rglob("*.svg")):
        t = p.read_text(encoding="utf-8")
        for bad, why in FORBIDDEN:
            if bad in t:
                errs.append(f"{p.relative_to(site)}: 出现禁用漂移值 {bad!r}（{why}）")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", default=None)
    a = ap.parse_args()
    site = Path(a.site) if a.site else site_base()

    facts = load_facts(site)
    exp = expected_strings(facts)

    sections = [
        ("1) facts.json 内部自洽", check_internal(facts)),
        ("2) 生成器产物（静/动两版）",
         check_svg(site / "images" / "delta_case_matrix.svg", exp)
         + check_svg(site / "images" / "anim" / "delta_case_matrix.svg", exp)),
        ("3) 页面文字 cases.html", check_cases_page(site / "cases.html", facts)),
        ("4) 全站禁用漂移值", check_forbidden(site)),
    ]

    n_err = 0
    print(f"[check_facts] site = {site}")
    print(f"[check_facts] facts: case_count={facts['case_count']} "
          f"name_counts={facts['name_counts']}")
    for title, errs in sections:
        if errs:
            n_err += len(errs)
            print(f"[check_facts] {title}: FAIL ({len(errs)})")
            for e in errs:
                print(f"    - {e}")
        else:
            print(f"[check_facts] {title}: PASS")

    print(f"[check_facts] RESULT: {'FAIL' if n_err else 'ALL PASS'} "
          f"({n_err} problem(s))")
    return 1 if n_err else 0


if __name__ == "__main__":
    sys.exit(main())
# ymzhu 2026-11-17 19:55
