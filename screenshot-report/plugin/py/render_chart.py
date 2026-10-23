#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""render_chart.py — 固定模板重绘（§11.5）。fork back_ppt 同族模板渲染器（不修改原库）。

CLI：argv[1]=输入 JSON {data, out}，argv[2]=themes.json 路径，argv[3]=theme 名，argv[4]=backppt 脚本目录。
流程：sys.path 插 backppt 目录 → import _gen_be_review_images as G；G.S=4 →
读 themes.json 选主题 hex→RGB → 二次校验 data 长度 → render_site_table（动态列宽/1-2 层表头/斑马线/判色/右对齐）
→ self_check（numpy 3px 边框无墨 + 右内带仅基色）→ img.save(out)。
stdout 恰好一行 JSON：{ok:true, path, width, height, bytes, self_check:"passed"} 或
{ok:false, code:"SELF_CHECK_FAILED"|DATA_INVALID, detail}。
"""
import json
import os
import re
import sys

import numpy as np

WINDOW_RE = re.compile(r"(-?\+?[\d.]+)\s*:\s*(-?\+?[\d.]+)")


def read_input(argv):
    with open(argv[1], "r", encoding="utf-8") as f:
        return json.load(f)


def emit(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")


def hex_to_rgb(h):
    h = str(h).lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def fmt5(s):
    """浮点 → 最多 5 位小数去尾零；整数去小数点；非数字原样。"""
    s = str(s).strip()
    try:
        v = float(s)
    except ValueError:
        return s
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.5f}".rstrip("0").rstrip(".")


def render_site_table(G, P, data):
    S = G.S
    title = data["title"]
    subtitle = data.get("subtitle", "")
    headers = data["headers"]
    rows = data["rows"]
    mode = data.get("mode", "plain")
    num_layers = len(headers)
    n_rows = len(rows)
    n_col = len(headers[0])

    f_h = G.F_MONO_B(11)
    f_m = G.F_MONO(11)
    f_c = G.F_CJK(11)
    mono_w = f_m.getlength("M")
    pad = 10 * S
    rh = 22 * S
    hh = 26 * S

    texts = [[fmt5(c) for c in r] for r in rows]

    # 动态列宽：表头 + 单元格 mixed_len 最大值 + 2*pad
    col_w = [0] * n_col
    for layer in headers:
        for j, h in enumerate(layer):
            col_w[j] = max(col_w[j], int(G.mixed_len(str(h), f_h, f_c, mono_w)) + pad * 2)
    for r in texts:
        for j, c in enumerate(r):
            col_w[j] = max(col_w[j], int(G.mixed_len(c, f_m, f_c, mono_w)) + pad * 2)
    W = sum(col_w) + 1
    bar_h = 30 * S
    H = bar_h + hh * num_layers + rh * n_rows + 1

    img = G.Image.new("RGB", (W, H), P["bg"])
    d = G.ImageDraw.Draw(img)

    # 标题栏（header 底，标题/副标题 ink_on_dark）
    d.rectangle([0, 0, W, bar_h], fill=P["header"])
    f_t = G.F_MONO_B(13)
    f_tc = G.F_CJK_B(13)
    G.draw_mixed(d, (10 * S, 6 * S), title, f_t, f_tc, P["ink_on_dark"], f_t.getlength("M"))
    if subtitle:
        f_s = G.F_CJK(10)
        sw = f_s.getlength(subtitle)
        d.text((W - sw - 10 * S, 9 * S), subtitle, font=f_s, fill=P["ink_on_dark"])

    # 表头（1-2 层，header 底，ink_on_dark，首列左 / 其余右对齐）
    y = bar_h
    d.rectangle([0, y, W, y + hh * num_layers], fill=P["header"])
    for li in range(num_layers):
        x = 0
        for j, h in enumerate(headers[li]):
            hw = G.mixed_len(str(h), f_h, f_c, mono_w)
            ty = y + li * hh + 6 * S
            if j == 0:
                G.draw_mixed(d, (x + pad, ty), str(h), f_h, f_c, P["ink_on_dark"], mono_w)
            else:
                G.draw_mixed(d, (x + col_w[j] - pad - hw, ty), str(h), f_h, f_c, P["ink_on_dark"], mono_w)
            x += col_w[j]
    y += hh * num_layers

    def style_fn(i, j, raw):
        """判色：首列(行标签)不染色；数值格按 mode。返回 (fg, bg, bold)。"""
        if j == 0:
            return P["ink"], None, False
        try:
            v = float(raw)
        except (ValueError, TypeError):
            return P["ink"], None, False
        if mode == "violation":
            if v < 0:
                return P["bad"], P["bad_bg"], True
            if v > 0:
                return P["ink"], None, False
            return P["ok"], None, False
        if mode == "window":
            m = WINDOW_RE.search(str(rows[i][0]))
            if m:
                lo = float(m.group(1))
                hi = float(m.group(2))
                if v < lo or v > hi:
                    return P["bad"], P["bad_bg"], True
                return P["ok"], None, False
            return P["ink"], None, False
        return P["ink"], None, False  # plain

    # 数据行（斑马线，首列左 / 其余右对齐，判色整格 bad_bg）
    for i, r in enumerate(texts):
        if r == []:  # 半高分隔缝
            d.rectangle([0, y, W, y + rh // 2], fill=P["border"])
            y += rh
            continue
        if i % 2 == 1:
            d.rectangle([0, y, W, y + rh], fill=P["zebra"])
        x = 0
        for j, c in enumerate(r):
            fg, bg, bold = style_fn(i, j, rows[i][j])
            if bg:
                d.rectangle([x + 1, y + 1, x + col_w[j] - 1, y + rh - 1], fill=bg)
            fnt = G.F_MONO_B(11) if bold else f_m
            if j == 0:
                G.draw_mixed(d, (x + pad, y + 4 * S), c, fnt, f_c, fg, mono_w)
            else:
                cw = G.mixed_len(c, fnt, f_c, mono_w)
                G.draw_mixed(d, (x + col_w[j] - pad - cw, y + 4 * S), c, fnt, f_c, fg, mono_w)
            x += col_w[j]
        y += rh

    # 网格
    x = 0
    for j in range(n_col + 1):
        d.line([x, bar_h, x, H], fill=P["grid"], width=1)
        if j < n_col:
            x += col_w[j]
    yy = bar_h
    for k in range(num_layers + n_rows + 1):
        d.line([0, yy, W, yy], fill=P["grid"], width=1)
        yy += hh if k < num_layers else rh

    # 外边框
    d.rectangle([0, 0, W - 1, H - 1], outline=P["border"], width=S)
    data_start_y = bar_h + hh * num_layers
    return img, bar_h, data_start_y


def self_check(img, P, data_start_y, S=4):
    """numpy 自检（T7 合稿：移植 impl-b 的向量化实现——四路最严，逐 §11.5 字面）。
    ① 数据区四边 3px 环带（外框 frame=S 以内）不允许出现 ink 文字色（ink 距离 <30 判文字，
       底色类 bg/zebra/bad_bg/border/grid 天然远离 ink，无需逐色白名单）；
    ② 右内缘竖带（文字右界 pad=10·S 再留 2px 抗锯齿容差 → 右环带之间）只允许底色（同 ink 检查）。
    返回 None=通过，str=失败原因。
    """
    arr = np.array(img)
    ink = np.array(P["ink"], dtype=np.int64)
    ink_dist = np.abs(arr.astype(np.int64) - ink).sum(axis=2)
    b = 3
    frame = S  # 外框描边宽（border 色，允许）
    hgt, wid = arr.shape[:2]
    ring_mask = np.zeros((hgt, wid), dtype=bool)
    ring_mask[data_start_y + frame:data_start_y + frame + b, :] = True               # 顶环带（数据区顶）
    ring_mask[hgt - frame - b:hgt - frame, :] = True                                 # 底环带（外框以内）
    ring_mask[data_start_y + frame:hgt - frame, frame:frame + b] = True              # 左环带
    ring_mask[data_start_y + frame:hgt - frame, wid - frame - b:wid - frame] = True  # 右环带
    if (ink_dist[ring_mask] < 30).any():
        return "border ring contains ink pixels"
    band_mask = np.zeros((hgt, wid), dtype=bool)
    # 右内缘竖带只盯数据区，且从文字右界（pad=10·S）再留 2px 抗锯齿容差
    band_mask[data_start_y + frame:hgt - frame, wid - 10 * S + 2:wid - frame - b] = True
    if (ink_dist[band_mask] < 30).any():
        return "right inner band contains ink pixels"
    return None


def main():
    inp = read_input(sys.argv)
    data = inp["data"]
    out = inp["out"]
    themes_path = sys.argv[2]
    theme_name = sys.argv[3]
    backppt_dir = sys.argv[4]

    sys.path.insert(0, backppt_dir)
    import _gen_be_review_images as G  # noqa: E402  （fork-import，不修改原库）
    G.S = 4

    with open(themes_path, "r", encoding="utf-8") as f:
        themes = json.load(f)
    t = themes[theme_name]
    P = {
        "bg": hex_to_rgb(t["bg"]), "ink": hex_to_rgb(t["ink"]), "header": hex_to_rgb(t["header"]),
        "bad": hex_to_rgb(t["bad"]), "bad_bg": hex_to_rgb(t["bad_bg"]), "warn": hex_to_rgb(t["warn"]),
        "zebra": hex_to_rgb(t["zebra"]), "grid": hex_to_rgb(t["grid"]), "border": hex_to_rgb(t["border"]),
        "ink_on_dark": hex_to_rgb(t["ink_on_dark"]), "ok": hex_to_rgb(t["ok"]),
        "categorical": [hex_to_rgb(c) for c in (t.get("categorical") or [])],
    }

    # py 二次校验长度（DATA_INVALID）
    headers = data["headers"]
    rows = data["rows"]
    cols = len(headers[0])
    for li in range(len(headers)):
        if len(headers[li]) != cols:
            emit({"ok": False, "code": "DATA_INVALID", "detail": f"headers 层 {li} 长度 {len(headers[li])} != {cols}"})
            return
    for ri in range(len(rows)):
        if len(rows[ri]) == 0:
            continue
        if len(rows[ri]) != cols:
            emit({"ok": False, "code": "DATA_INVALID", "detail": f"rows {ri} 长度 {len(rows[ri])} != {cols}"})
            return

    img, bar_h, data_start_y = render_site_table(G, P, data)
    detail = self_check(img, P, data_start_y, S=G.S)
    if detail:
        emit({"ok": False, "code": "SELF_CHECK_FAILED", "detail": detail})
        return
    out_dir = os.path.dirname(out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    img.save(out, "PNG")
    emit({"ok": True, "path": out, "width": img.width, "height": img.height,
          "bytes": os.path.getsize(out), "self_check": "passed"})


if __name__ == "__main__":
    main()
