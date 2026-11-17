# -*- coding: utf-8 -*-
# gen_power_0812.py — 从库内 PTPX 报告解析 0812 六组 Total Power，落 data/power_0812.json
#
# 背景（t20 · R1）：memory-power.html 正文曾手写「1L 14.3 / 15.0 / 15.0、2L 15.5 / 16.1 / 17.9 mW」，
# 而源就在库内 server-reports/power/px_85c_random/rep_dir_*_0812/HV2M23_digital_top_power.rpt
# （Time Based Power 层级表首行 HV2M23_digital_top 的 Total Power 列，单位 W）。
#
# 用法（站点根目录）：
#   python image/tools/gen_power_0812.py            # 解析 → 写 JSON
#   python image/tools/gen_power_0812.py --check    # 只校验 JSON 与报告是否仍一致（不一致 exit 1）
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
PWR = os.path.join(GUIDE, "server-reports", "power", "px_85c_random")
OUT = os.path.join(BASE, "data", "power_0812.json")

DIRS = [
    ("1l_normal", "rep_dir_1lane_fre1p7_tt_0812", "1L 1.7G normal"),
    ("1l_dplc", "rep_dir_1lane_fre1p7_tt_0812_dplc", "1L 1.7G dplc"),
    ("1l_drdod", "rep_dir_1lane_fre1p7_tt_0812_drdod", "1L 1.7G drdod"),
    ("2l_normal", "rep_dir_2lane_fre1p6_tt_0812", "2L 1.6G normal"),
    ("2l_dplc", "rep_dir_2lane_fre1p6_tt_dplc_0812", "2L 1.6G dplc"),
    ("2l_drdod", "rep_dir_2lane_fre1p6_tt_drdod_0812", "2L 1.6G drdod"),
]

# 层级表首行：HV2M23_digital_top  Int Switch Leak Total %
RE_TOP = re.compile(r"^HV2M23_digital_top\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+100\.0")
RE_RPT = "HV2M23_digital_top_power.rpt"


def parse_one(d):
    path = os.path.join(PWR, d, RE_RPT)
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            m = RE_TOP.match(line)
            if m:
                total_w = float(m.group(4))
                return total_w * 1000.0, ln, m.group(1), m.group(2), m.group(3)
    raise SystemExit("[power0812] %s 未找到 HV2M23_digital_top 层级首行" % path)


def parse():
    rows = {}
    for key, d, label in DIRS:
        mw, ln, int_w, sw_w, leak_w = parse_one(d)
        rows[key] = {
            "label": label,
            "dir": d,
            "rpt": "server-reports/power/px_85c_random/%s/%s" % (d, RE_RPT),
            "line": ln,
            "total_power_mW": "%.1f" % mw,
            "total_power_W_raw": "%.6g" % (mw / 1000.0),
        }
    return {
        "schema": "power_0812/v1",
        "unit": "mW",
        "rows": rows,
        "_meta": {
            "purpose": "0812 六组 PTPX Total Power 的单一事实源；memory-power.html 正文六组数字由 gen_param_blocks.py 渲染",
            "extract_rule": "Time Based Power 层级表首行 HV2M23_digital_top 的 Total Power 列（单位 W）×1000 取 1 位小数",
            "reproduce": "python image/tools/gen_power_0812.py",
            "gate": "python image/tools/gen_param_blocks.py --check",
        },
    }


def main():
    data = parse()
    body = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("[power0812] FAIL 缺少 %s（跑 python image/tools/gen_power_0812.py 生成）" % OUT)
            return 1
        cur = io.open(OUT, encoding="utf-8").read()
        if cur != body:
            got = {k: v["total_power_mW"] for k, v in data["rows"].items()}
            print("[power0812] FAIL power_0812.json 与报告不一致：%s" % got)
            return 1
        print("[power0812] PASS power_0812.json 与 6 份 PTPX 报告一致：%s"
              % " / ".join("%s=%s" % (k, v["total_power_mW"]) for k, v in data["rows"].items()))
        return 0
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print("[power0812] written %s：%s" % (OUT, " / ".join(
        "%s=%s mW" % (k, v["total_power_mW"]) for k, v in data["rows"].items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 20:50
