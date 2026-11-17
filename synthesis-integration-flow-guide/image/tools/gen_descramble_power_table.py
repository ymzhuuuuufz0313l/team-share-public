# -*- coding: utf-8 -*-
# gen_descramble_power_table.py — 把 descramble 功耗数值的唯一事实源（JSON）渲染进页面
#
# 单一事实源：image/tools/data/descramble_power.json（含数值 + provenance + 原始报告缺失标记）
# 消费方：
#   1) memory-power.html 中 AUTO-GEN 标记块（本脚本渲染 markdown 表格 + 说明）
#   2) gen_power_compare_descramble.py 读同一 JSON 出图（ROWS / TITLE）
#
# 用法（在站点根目录下）：
#   python image/tools/gen_descramble_power_table.py           # 重新渲染页面块
#   python image/tools/gen_descramble_power_table.py --check   # 只校验页面块与 JSON 是否一致（QA）
import io
import json
import os
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
DATA = os.path.join(BASE, "data", "descramble_power.json")
PAGE = os.path.join(GUIDE, "memory-power.html")
IMG_REF = "./image/power_compare_descramble_1106.png"
BEGIN = "<!-- AUTO-GEN:descramble_power BEGIN（源 image/tools/data/descramble_power.json，勿手改） -->"
END = "<!-- AUTO-GEN:descramble_power END -->"


def load():
    with io.open(DATA, encoding="utf-8") as f:
        return json.load(f)


def fmt_cell(v):
    return "-" if v is None else v


def render(d):
    prov = d["provenance"]
    rows = d["rows"]
    lines = []
    lines.append("**1106 新增：descramble 2lane 1.6G 实测**（PTPX Time-Based，`t_8b2lane_descramble*` 后仿 case）：")
    lines.append("")
    lines.append("| " + " | ".join(d["columns"]) + " |")
    lines.append("|" + "|".join(["------"] * len(d["columns"])) + "|")
    for r in rows:
        cells = [
            "`%s`" % r["key"],
            fmt_cell(r.get("internal")),
            fmt_cell(r.get("switching")),
            fmt_cell(r.get("leakage")),
            "**%s mW**" % r["total_power_mW"],
            r.get("note", ""),
        ]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("![%s](%s)" % (d["title"], IMG_REF))
    lines.append("")
    note = ["> 数值单一事实源：`image/tools/data/descramble_power.json`（本表格与对比图均由它渲染）。"]
    if prov.get("source_status") != "ok":
        note.append("原始 PTPX 报告未随站点归档（`source_status: %s`，%s），此处只保留实测数值与出处标记，不做溯源补全。"
                    % (prov.get("source_status"), prov.get("source_dir_hint", "")))
    voided = prov.get("voided") or {}
    if voided:
        note.append("%s（曾误测 %s mW），1106 复跑定稿 %s mW。"
                    % (voided.get("reason", ""), voided.get("value_mW"), voided.get("superseded_by_mW")))
    ref = prov.get("same_generation_reference") or {}
    if ref.get("range_mW"):
        note.append("对比%s（%s~%s mW），descramble 负载略低。"
                    % (ref.get("desc", ""), ref["range_mW"][0], ref["range_mW"][1]))
    lines.append(" ".join(note))
    return "\n".join(lines)


def main():
    check = "--check" in sys.argv
    d = load()
    block = BEGIN + "\n\n" + render(d) + "\n\n" + END
    with io.open(PAGE, encoding="utf-8", newline="") as f:
        s = f.read()
    i, j = s.find(BEGIN), s.find(END)
    if i < 0 or j < 0:
        print("FAIL: memory-power.html 缺少 AUTO-GEN:descramble_power 标记块")
        return 1
    j += len(END)
    cur = s[i:j]
    if check:
        if cur == block:
            print("PASS: memory-power.html 的 descramble 块与 descramble_power.json 完全一致")
            print("      rows=%d，总计=%s mW" % (len(d["rows"]), "/".join(str(r["total_power_mW"]) for r in d["rows"])))
            return 0
        print("FAIL: 页面块与 JSON 不一致，请运行 python image/tools/gen_descramble_power_table.py")
        return 1
    if cur != block:
        with io.open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(s[:i] + block + s[j:])
        print("OK: memory-power.html 已按 JSON 重新渲染 descramble 块")
    else:
        print("OK: 页面块已是最新，无改动")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 19:43
