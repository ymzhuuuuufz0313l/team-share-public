#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ocr_table.py — 本地 RapidOCR 表格抽取（§11.3）。表格数据不进 LLM。

CLI：argv[1] = 输入 JSON 路径 {path, region|null, confidence_min:0.70}
region = 分数框，先内联裁剪再 OCR（不落盘）。
引擎缺失 → {ok:false, code:"ENGINE_MISSING", message:<恢复命令原文>}（返回值，非 throw）。
stdout 恰好一行 JSON：{ok, engine, rows, n_rows, n_cols_max, cell_confidence_mean,
                       frac_low_confidence, warnings, unreliable, reason}
unreliable = mean<confidence_min ∥ 低置信占比>0.30 ∥ n_rows<2 ∥ 总格数<6（领域结果，ok 仍 true）。
"""
import json
import sys

import numpy as np
from PIL import Image

RESTORE = ("E:/project/team-share-public/synthesis-integration-flow-guide/script/.venv/"
           "Scripts/python.exe -m pip install rapidocr-onnxruntime==1.2.3")


def read_input(argv):
    with open(argv[1], "r", encoding="utf-8") as f:
        return json.load(f)


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def cy(box):
    ys = [p[1] for p in box]
    return (min(ys) + max(ys)) / 2.0


def lx(box):
    return min(p[0] for p in box)


def bh(box):
    ys = [p[1] for p in box]
    return max(ys) - min(ys)


def main():
    inp = read_input(sys.argv)
    path = inp["path"]
    region = inp.get("region")
    conf_min = float(inp.get("confidence_min", 0.70))

    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        emit({"ok": False, "code": "ENGINE_MISSING", "message": RESTORE})
        return

    img = Image.open(path).convert("RGB")
    if region:
        w, h = img.size
        x1 = max(0, min(w, int(region["left"] * w)))
        y1 = max(0, min(h, int(region["top"] * h)))
        x2 = max(0, min(w, int(region["right"] * w)))
        y2 = max(0, min(h, int(region["bottom"] * h)))
        if x2 <= x1 or y2 <= y1:
            emit({"ok": False, "code": "OCR_FAILED", "message": "region 无效（0 面积）"})
            return
        img = img.crop((x1, y1, x2, y2))

    try:
        engine = RapidOCR()
        out = engine(np.array(img))
        result = out[0] if isinstance(out, tuple) else out
    except Exception as e:  # noqa: BLE001
        emit({"ok": False, "code": "OCR_FAILED", "message": str(e)})
        return

    cells = []
    if result:
        for item in result:
            if not item or len(item) < 3:
                continue
            cells.append({"box": item[0], "text": str(item[1]), "score": float(item[2])})
    if not cells:
        emit({
            "ok": True, "engine": "rapidocr-onnxruntime", "rows": [], "n_rows": 0,
            "n_cols_max": 0, "cell_confidence_mean": 0.0, "frac_low_confidence": 1.0,
            "warnings": ["no_detection"], "unreliable": True,
            "reason": "OCR 未检测到任何文本",
        })
        return

    heights = [bh(c["box"]) for c in cells if bh(c["box"]) > 0]
    med_h = float(np.median(heights)) if heights else 10.0

    # 行聚类：按中心 y 排序，|y - cur_y| < 0.6×文本高中位数 归同行
    cells_sorted = sorted(cells, key=lambda c: cy(c["box"]))
    rows = []
    cur = []
    cur_y = None
    for c in cells_sorted:
        y = cy(c["box"])
        if cur_y is None or abs(y - cur_y) < 0.6 * med_h:
            cur.append(c)
            if cur_y is None:
                cur_y = y
        else:
            rows.append(cur)
            cur = [c]
            cur_y = y
    if cur:
        rows.append(cur)
    for r in rows:
        r.sort(key=lambda c: lx(c["box"]))

    rows_text = [[c["text"] for c in r] for r in rows]
    n_rows = len(rows_text)
    n_cols_max = max((len(r) for r in rows_text), default=0)
    scores = [c["score"] for r in rows for c in r]
    mean_conf = (sum(scores) / len(scores)) if scores else 0.0
    low = sum(1 for s in scores if s < 0.60)
    frac_low = (low / len(scores)) if scores else 1.0
    total = len(scores)

    warnings = []
    if len(set(len(r) for r in rows_text)) > 1:
        warnings.append("ragged_rows")
    if low > 0:
        warnings.append(f"low_confidence_cells:{low}")

    unreliable = (mean_conf < conf_min) or (frac_low > 0.30) or (n_rows < 2) or (total < 6)
    reason = None
    if unreliable:
        rr = []
        if mean_conf < conf_min:
            rr.append(f"平均置信度 {mean_conf:.3f} < {conf_min}")
        if frac_low > 0.30:
            rr.append(f"低置信格占比 {frac_low:.3f} > 0.30")
        if n_rows < 2:
            rr.append(f"行数 {n_rows} < 2")
        if total < 6:
            rr.append(f"总格数 {total} < 6")
        reason = "；".join(rr)

    emit({
        "ok": True, "engine": "rapidocr-onnxruntime", "rows": rows_text,
        "n_rows": n_rows, "n_cols_max": n_cols_max,
        "cell_confidence_mean": round(mean_conf, 4), "frac_low_confidence": round(frac_low, 4),
        "warnings": warnings, "unreliable": unreliable, "reason": reason,
    })


if __name__ == "__main__":
    main()
