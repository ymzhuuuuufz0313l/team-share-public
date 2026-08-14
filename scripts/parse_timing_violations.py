#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
parse_timing_violations.py

从仿真 log 中解析 "Timing violation in <instance>" 行，
提取实例名（去重，保持出现顺序），按 notimingcheck cfg 格式输出：

    //instance {} {noTiming};
    instance {chip_tb_top.xxx.reg} {noTiming};
    ...

用法:
    python parse_timing_violations.py <log文件> [输出文件]

默认输出: notimingcheck_dig_python.md (当前目录)
"""

import re
import sys

# "Timing violation in chip_tb_top.a.b.c_reg_1_" —— 实例名取到行尾（路径中无空格）
PATTERN = re.compile(r"Timing violation in\s+(\S+)")


def parse_violations(log_path):
    names = []
    seen = set()
    with open(log_path, "r", errors="ignore") as f:
        for line in f:
            m = PATTERN.search(line)
            if not m:
                continue
            name = m.group(1)
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    log_path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "notimingcheck_dig_python.md"

    names = parse_violations(log_path)

    lines = ["//instance {} {noTiming};"]
    for n in names:
        lines.append(f"instance {{{n}}} {{noTiming}};")

    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    print(f"共提取 {len(names)} 个实例, 输出到 {out_path}")


if __name__ == "__main__":
    main()
