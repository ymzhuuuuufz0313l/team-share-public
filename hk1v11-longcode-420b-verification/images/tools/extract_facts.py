# -*- coding: utf-8 -*-
"""420b 站点事实抽取器：从 DV_TCON_C case 源统计站点图文使用的业务数字，产出 data/facts.json。

用法:
    python images/tools/extract_facts.py [--src <HK1V11 根>] [--out data/facts.json]

    # 复现站点锚点 a7130ba7 的口径（推荐）：
    git -C <HK1V11> archive a7130ba7 DV_TCON_C/top/tests | tar -x -C /tmp/anchor
    python images/tools/extract_facts.py --src /tmp/anchor --out /tmp/facts_anchor.json

口径（**唯一口径**，与站点图内并列项自洽）：
    ×N = case 目录名中含该标记的目录数（同一 case 只计 1 次）。
    该口径由站点图内三个并列项共同锁定，可直接校验：
        DPLC_GROUP1 ×33、SDC0 ×55 —— 二者只有"目录名计数"口径能同时得到 33/55。
    因此 DPLC_MODE1 必须同口径读取，得 104（站点原写 173，不可复现，已更正）。

只读源树；输出路径可由 --out 覆盖（默认 images/tools/data/facts.json）。
"""
import argparse
import json
import os
import re
import sys
from collections import Counter, OrderedDict

TOKEN = "420b"

# 文件行数族（V2 / t15 验收）：站点 architecture.html + delta_env_components 图内用到的行数。
# 事实源在 HK1V11 仓，故与 case 统计分开取源：`--lines-src` 指向 anchor 快照解包目录。
FILE_LINE_FILES = OrderedDict([
    ("checker_420b", "DV_TCON_C/top/agents/isprx_env/isptx_agent/checker_420b.sv"),
    ("isptx_sequence", "DV_TCON_C/top/agents/isprx_env/isptx_agent/isptx_sequence.sv"),
    ("long_encoding_align", "HDL/HK1V11_digital_top/long_encoding/LONG_ENCODING_ALIGN.v"),
    ("long_encoding_error_ctrl",
     "HDL/HK1V11_digital_top/long_encoding/LONG_ENCODING_ERROR_CTRL.v"),
    ("long_encoding_output", "HDL/HK1V11_digital_top/long_encoding/LONG_ENCODING_OUTPUT.v"),
])
HEAD_COMMIT = "a7130ba7"
BASELINE_COMMIT = "66ecf97d"


def line_count(path):
    """与 `wc -l` 同口径：数 '\\n' 的个数（末行无换行则不计）。"""
    with open(path, "rb") as fh:
        return fh.read().count(b"\n")

# 名称标记 → 统计项名（图内 "×N" 项）
NAME_TOKENS = [
    ("DPLC_MODE1", r"DPLC_MODE"),      # 名称里出现 DPLC_MODE(=1)
    ("DPLC_GROUP1", r"DPLC_GROUP"),
    ("SDC0", r"SDC0"),
]


def find_tests_root(src):
    cand = os.path.join(src, "DV_TCON_C", "top", "tests")
    if os.path.isdir(cand):
        return cand
    # --src 直接指向 tests 目录
    if os.path.isdir(src) and any(TOKEN in d for d in os.listdir(src)):
        return src
    raise SystemExit("tests dir not found under %s" % src)


def case_dirs(tests_root):
    return sorted(
        d for d in os.listdir(tests_root)
        if TOKEN in d and os.path.isdir(os.path.join(tests_root, d))
    )


def name_counts(cases):
    out = OrderedDict()
    for label, pat in NAME_TOKENS:
        rx = re.compile(pat)
        out[label] = sum(1 for c in cases if rx.search(c))
    return out


def dim_dist(cases, rx):
    c = Counter()
    for n in cases:
        m = re.search(rx, n)
        c[m.group(1) if m else "other"] += 1
    return OrderedDict(sorted(c.items()))


def cfg_field_union(tests_root, cases):
    """cfg_frame0..8.txt 首列字段名 ∪ user_def.sv 中的 CHPI 宏相关字段名。"""
    names = set()
    for c in cases:
        d = os.path.join(tests_root, c)
        for i in range(9):
            p = os.path.join(d, "cfg_frame%d.txt" % i)
            if not os.path.exists(p):
                continue
            with open(p, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    tok = re.split(r"[\s,;=]+", line)[0]
                    if re.match(r"^[A-Z][A-Z0-9_]*$", tok):
                        names.add(tok)
        u = os.path.join(d, "user_def.sv")
        if os.path.exists(u):
            with open(u, encoding="utf-8", errors="replace") as fh:
                for line in fh:
                    for m in re.finditer(r"cfg_register\.([A-Z][A-Z0-9_]*)", line):
                        names.add(m.group(1))
    return sorted(names)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.environ.get("HK11_SRC"),
                    help="HK1V11 仓根（或直接指向 tests 目录）。不给则读环境变量 HK11_SRC；"
                         "两者都没有则报错退出（不再回落到某个人的本机绝对路径）")
    ap.add_argument("--out", default=None,
                    help="facts.json 输出路径（默认 images/tools/data/facts.json，相对本脚本）")
    ap.add_argument("--lines-src", default=os.environ.get("HK11_LINES_SRC"),
                    help="文件行数族的源树根（anchor 快照解包目录，需含 DV_TCON_C/ 与 HDL/）；"
                         "不给则沿用现有 facts.json 里的 file_lines（不臆造）")
    ap.add_argument("--baseline-src", default=os.environ.get("HK11_LINES_BASELINE_SRC"),
                    help="基线版本源树根（默认沿用现有 file_lines 的基线值）")
    ap.add_argument("--head-commit", default=HEAD_COMMIT)
    ap.add_argument("--baseline-commit", default=BASELINE_COMMIT)
    a = ap.parse_args()

    if not a.src:
        raise SystemExit(
            "[extract_facts] 需要 case 源：\n"
            "  python images/tools/extract_facts.py --src <HK1V11 仓根 或 DV_TCON_C/top/tests>\n"
            "  或设环境变量 HK11_SRC。\n"
            "  （历史缺陷：此处曾硬编码 r\"E:/project/HK1V11\"，换机器即失效。）")
    tests_root = find_tests_root(a.src)
    cases = case_dirs(tests_root)
    if not cases:
        raise SystemExit("no *%s* case dirs under %s" % (TOKEN, tests_root))

    facts = OrderedDict()
    facts["_meta"] = OrderedDict([
        ("generator", "images/tools/extract_facts.py"),
        ("src_root", os.path.abspath(a.src).replace("\\", "/")),
        ("tests_root", os.path.abspath(tests_root).replace("\\", "/")),
        ("count_rule", "×N = case 目录名中含该标记的目录数（同一 case 只计 1 次）"),
        ("count_rule_check", "DPLC_GROUP1=33 且 SDC0=55 时该口径成立（站点图内并列项自洽）"),
    ])

    facts["case_count"] = len(cases)
    facts["name_counts"] = name_counts(cases)
    facts["resolution"] = dim_dist(cases, r"H(\d{4})")
    facts["fps"] = dim_dist(cases, r"FPS(\d+)")
    facts["port"] = dim_dist(cases, r"PORT_NUM(\d+)")
    facts["cfg_field_union"] = cfg_field_union(tests_root, cases)
    facts["cfg_field_count"] = len(facts["cfg_field_union"])

    covered = [c for c in cases
               if os.path.exists(os.path.join(tests_root, c, "ctrl_l_line_cfg.txt"))]
    facts["ctrl_l_line_cfg"] = OrderedDict([
        ("covered", len(covered)),
        ("total", len(cases)),
        ("missing", [c for c in cases if c not in covered]),
    ])

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "facts.json")

    # —— 文件行数族（V2）：有源则重算，无源则沿用旧值（绝不臆造一个数字）——
    prev = {}
    if os.path.exists(out):
        try:
            with open(out, encoding="utf-8") as fh:
                prev = json.load(fh)
        except Exception:
            prev = {}
    if a.lines_src:
        fl = OrderedDict()
        root_ = os.path.abspath(a.lines_src).replace("\\", "/")
        fl["_source"] = ("HK1V11 仓 anchor %s 的 wc -l 实测（基线列取 %s）；"
                         "由 extract_facts.py --lines-src 可重算" % (a.head_commit, a.baseline_commit))
        fl["_reproduce"] = (
            "git -C <HK1V11> archive %s DV_TCON_C/top/agents/isprx_env/isptx_agent/checker_420b.sv "
            "DV_TCON_C/top/agents/isprx_env/isptx_agent/isptx_sequence.sv "
            "HDL/HK1V11_digital_top/long_encoding | tar -xf - -C <tmp> && "
            "python images/tools/extract_facts.py --lines-src <tmp> --src <anchor tests 目录> "
            "--out images/tools/data/facts.json" % a.head_commit)
        fl["paths"] = OrderedDict(FILE_LINE_FILES)
        fl["baseline_commit"] = a.baseline_commit
        fl["head_commit"] = a.head_commit
        counts = {}
        for key, rel in FILE_LINE_FILES.items():
            fp = os.path.join(a.lines_src, rel)
            if not os.path.exists(fp):
                raise SystemExit("[extract_facts] 行数源缺失：%s（--lines-src 需含 DV_TCON_C/ 与 HDL/）"
                                 % fp)
            counts[key] = line_count(fp)
        fl["checker_420b"] = counts["checker_420b"]
        fl["isptx_sequence_head"] = counts["isptx_sequence"]
        fl["long_encoding_align"] = counts["long_encoding_align"]
        fl["long_encoding_error_ctrl"] = counts["long_encoding_error_ctrl"]
        fl["long_encoding_output"] = counts["long_encoding_output"]
        base = None
        if a.baseline_src:
            bp = os.path.join(a.baseline_src, FILE_LINE_FILES["isptx_sequence"])
            if not os.path.exists(bp):
                raise SystemExit("[extract_facts] 基线源缺失：%s" % bp)
            base = line_count(bp)
        elif "file_lines" in prev:
            base = prev["file_lines"].get("isptx_sequence_baseline")
        if base is None:
            raise SystemExit("[extract_facts] 缺基线行数：给 --baseline-src 或先有一份含 "
                             "file_lines.isptx_sequence_baseline 的 facts.json")
        fl["isptx_sequence_baseline"] = base
        fl["isptx_sequence_delta"] = fl["isptx_sequence_head"] - base
        facts["file_lines"] = fl
    elif "file_lines" in prev:
        facts["file_lines"] = prev["file_lines"]
        print("[extract_facts] 未给 --lines-src：沿用现有 facts.json 的 file_lines（行数族来自 HK1V11 仓）")
    else:
        raise SystemExit("[extract_facts] facts.json 无 file_lines 且未给 --lines-src，"
                         "拒绝产出缺行数族的事实源")

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="") as fh:
        json.dump(facts, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print("written:", out)
    print("case_count:", facts["case_count"])
    print("name_counts:", json.dumps(facts["name_counts"], ensure_ascii=False))
    print("resolution:", json.dumps(facts["resolution"], ensure_ascii=False))
    print("fps:", json.dumps(facts["fps"], ensure_ascii=False))
    print("port:", json.dumps(facts["port"], ensure_ascii=False))
    print("cfg_field_count:", facts["cfg_field_count"])
    print("ctrl_l_line_cfg:", json.dumps(
        {"covered": facts["ctrl_l_line_cfg"]["covered"],
         "total": facts["ctrl_l_line_cfg"]["total"],
         "missing": facts["ctrl_l_line_cfg"]["missing"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
# ymzhu 2026-11-17 19:55
