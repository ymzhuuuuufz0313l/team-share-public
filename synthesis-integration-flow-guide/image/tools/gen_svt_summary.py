# -*- coding: utf-8 -*-
# gen_svt_summary.py — 从库内综合报告解析 SVT/规模摘要，落 data/svt_summary.json（页面的唯一事实源）
#
# 背景（t20 · R2）：站点曾在 environment.html 与 pt-intro.html 各手写一遍「cell 数 / 面积」，
# 而真正的源就在库内 server-reports/HV2M23_digital_top.rpt——不需要「库外」解释。
#
# 用法（站点根目录）：
#   python image/tools/gen_svt_summary.py            # 解析 → 写 JSON
#   python image/tools/gen_svt_summary.py --check    # 只校验 JSON 与 rpt 是否仍一致（不一致 exit 1）
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
RPT = os.path.join(GUIDE, "server-reports", "HV2M23_digital_top.rpt")
OUT = os.path.join(BASE, "data", "svt_summary.json")

RE_LEAF = re.compile(r"^\s*Leaf Cell Count:\s+(\d+)\s*$")
RE_AREA = re.compile(r"^\s*Total cell area:\s+([0-9.]+)\s*$")


def parse():
    leaf = area = None
    leaf_ln = area_ln = None
    with io.open(RPT, encoding="utf-8", errors="replace") as fh:
        for ln, line in enumerate(fh, 1):
            m = RE_LEAF.match(line)
            if m and leaf is None:
                leaf, leaf_ln = int(m.group(1)), ln
            m = RE_AREA.match(line)
            if m and area is None:
                area, area_ln = float(m.group(1)), ln
            if leaf is not None and area is not None:
                break
    if leaf is None or area is None:
        raise SystemExit("[svt] 未能在 %s 中定位 Leaf Cell Count / Total cell area" % RPT)
    return {
        "schema": "svt_summary/v1",
        "leaf_cell_count": leaf,
        "leaf_cell_line": leaf_ln,
        "total_cell_area_um2": area,
        "area_display": "%.2f" % area,
        "area_line": area_ln,
        "vt_group": "SVT",
        "vt_percent": 100,
        "source_file": "server-reports/HV2M23_digital_top.rpt",
        "_meta": {
            "purpose": "SVT 换库结论（cell 数 / 面积 / VT 占比）的单一事实源；environment.html、pt-intro.html 由 gen_param_blocks.py 渲染",
            "reproduce": "python image/tools/gen_svt_summary.py（解析 server-reports/HV2M23_digital_top.rpt 的 Leaf Cell Count 与 Total cell area 两行）",
            "note": "VT 分组百分比（SVT 100%）来自 report_vt_cell_usage 报告页（image/27_svt_100.png），本 JSON 只固化其结论字符串，不重新推导",
            "gate": "python image/tools/gen_param_blocks.py --check",
        },
    }


def main():
    data = parse()
    body = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if "--check" in sys.argv:
        if not os.path.exists(OUT):
            print("[svt] FAIL 缺少 %s（跑 python image/tools/gen_svt_summary.py 生成）" % OUT)
            return 1
        cur = io.open(OUT, encoding="utf-8").read()
        if cur != body:
            print("[svt] FAIL svt_summary.json 与 rpt 不一致：rpt 侧 leaf=%d area=%s(%d 行)"
                  % (data["leaf_cell_count"], data["area_display"], data["area_line"]))
            return 1
        print("[svt] PASS svt_summary.json 与 rpt 一致：leaf=%d area=%.2f（rpt:%d / :%d）"
              % (data["leaf_cell_count"], data["total_cell_area_um2"],
                 data["leaf_cell_line"], data["area_line"]))
        return 0
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        fh.write(body)
    print("[svt] written %s：leaf=%d area=%.2f（rpt:%d / :%d）"
          % (OUT, data["leaf_cell_count"], data["total_cell_area_um2"],
             data["leaf_cell_line"], data["area_line"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 20:50
