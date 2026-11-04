# -*- coding: utf-8 -*-
"""BE Review PPT / 网站结果图重新生成脚本（高清版）。

数据源全部为真实报告文件（server-reports/ 与 HV2M23/SYNTHESIS/），
读数据 -> PIL 2x 超采样绘制 -> 覆盖 image/ 下同名 PNG。

运行（在站点根目录下）：script/.venv/Scripts/python.exe image/tools/_gen_be_review_images.py
"""
import csv
import os
import re
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))          # .../image/tools（2026-11-04 自 script/ 迁入）
GUIDE = os.path.dirname(os.path.dirname(BASE))             # 站点根
IMG_DIR = os.path.join(GUIDE, "image")
SR = os.path.join(GUIDE, "server-reports")
HV = r"E:/project/HV2M23"

S = 2  # supersample factor

FONT_DIR = "C:/Windows/Fonts"
def _font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size * S)

F_MONO = lambda sz: _font("consola.ttf", sz)
F_MONO_B = lambda sz: _font("consolab.ttf", sz)
F_CJK = lambda sz: _font("msyh.ttc", sz)
F_CJK_B = lambda sz: _font("msyhbd.ttc", sz)

TEAL = (14, 124, 107)
TEAL_DK = (11, 94, 82)
TEAL_HI = (217, 242, 236)      # key-line highlight
RED_BG = (253, 226, 226)
RED_TX = (192, 0, 0)
GREEN_TX = (30, 132, 73)
GRAY_TX = (150, 150, 150)
INK = (33, 37, 41)
BORDER = (192, 198, 198)
ZEBRA = (244, 248, 247)
GRID = (208, 216, 214)


def has_cjk(ch):
    return ord(ch) >= 0x2E80 or ch in "≥≤±→⇒✓×÷·…—–‘’“”"


def draw_mixed(draw, xy, text, mono_font, cjk_font, fill, mono_w):
    """逐字符绘制：ASCII 用等宽字体（保证代码对齐），其余回退中文字体。
    两种字体按基线对齐（getmetrics 的 ascent 换算），避免中文下沉/上浮。"""
    x, y = xy
    m_asc = mono_font.getmetrics()[0]
    c_asc = cjk_font.getmetrics()[0]
    dy = m_asc - c_asc  # CJK 字体的纵向补偿
    for ch in text:
        if not has_cjk(ch):
            draw.text((x, y), ch, font=mono_font, fill=fill)
            x += mono_w
        else:
            draw.text((x, y + dy), ch, font=cjk_font, fill=fill)
            x += cjk_font.getlength(ch)
    return x


def mixed_len(text, mono_font, cjk_font, mono_w):
    w = 0
    for ch in text:
        w += cjk_font.getlength(ch) if has_cjk(ch) else mono_w
    return w


def title_bar(draw, W, title, subtitle=""):
    bar_h = 30 * S
    draw.rectangle([0, 0, W, bar_h], fill=TEAL)
    f_t, f_tc = F_MONO_B(13), F_CJK_B(13)
    draw_mixed(draw, (10 * S, 6 * S), title, f_t, f_tc, (255, 255, 255),
               f_t.getlength("M"))
    if subtitle:
        f_s = F_CJK(10)
        sw = f_s.getlength(subtitle)
        tw = mixed_len(title, f_t, f_tc, f_t.getlength("M"))
        if 10 * S + tw + 12 * S + sw + 10 * S <= W:  # 不与标题重叠才画
            draw.text((W - sw - 10 * S, 9 * S), subtitle, font=f_s, fill=(205, 235, 229))
    return bar_h


def save(img, name):
    out = os.path.join(IMG_DIR, name)
    img.save(out)
    print(f"  {name}: {img.width}x{img.height}")


def fmt_num(s):
    """浮点格式化为最多 6 位小数，去尾零；非数字原样返回。"""
    s = s.strip()
    try:
        v = float(s)
    except ValueError:
        return s
    if v == int(v) and abs(v) < 1e15:
        return str(int(v))
    return f"{v:.6f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- code images
def render_code(name, title, subtitle, lines, hl_lines=(), red_lines=(), green_lines=(),
                min_w_in=0.0):
    """lines: list of (lineno, text)。hl_lines 等使用真实行号。"""
    f_m, f_c = F_MONO(12), F_CJK(12)
    mono_w = f_m.getlength("M")
    lh = 19 * S
    pad_x = 12 * S
    nums = [str(n) for n, _ in lines if n is not None]
    gut_w = int(f_m.getlength(max(nums, key=len, default=""))) + 22 * S
    body_w = 0
    for _, t in lines:
        body_w = max(body_w, mixed_len(t.expandtabs(4), f_m, f_c, mono_w))
    W = int(gut_w + body_w + pad_x * 2)
    if min_w_in:
        W = max(W, int(min_w_in * 144 * S))
    bar_h = 30 * S
    H = bar_h + lh * len(lines) + 12 * S
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, title, subtitle)
    # gutter
    d.rectangle([0, bar_h, gut_w, H], fill=(245, 246, 246))
    d.line([gut_w, bar_h, gut_w, H], fill=(222, 226, 226), width=S)
    y = bar_h + 6 * S
    for n, t in lines:
        t = t.expandtabs(4)
        if n in hl_lines:
            d.rectangle([gut_w, y - 2 * S, W, y + lh - 4 * S], fill=TEAL_HI)
        if n is not None:
            ns = str(n)
            nw = f_m.getlength(ns)
            d.text((gut_w - nw - 8 * S, y), ns, font=f_m, fill=(160, 168, 168))
        color = INK
        if n in red_lines:
            color = RED_TX
        elif n in green_lines:
            color = GREEN_TX
        draw_mixed(d, (gut_w + pad_x, y), t, f_m, f_c, color, mono_w)
        y += lh
    d.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=S)
    save(img, name)


# ---------------------------------------------------------------- table images
def render_table(name, title, subtitle, headers, rows, style_fn, first_col_w_min=0):
    f_h, f_m, f_c = F_MONO_B(11), F_MONO(11), F_CJK(11)
    mono_w = f_m.getlength("M")
    pad = 10 * S
    rh, hh = 22 * S, 26 * S
    n_col = len(headers)
    col_w = [0] * n_col
    texts = [[fmt_num(c) for c in r] for r in rows]
    for j, h in enumerate(headers):
        col_w[j] = int(mixed_len(str(h), f_h, f_c, mono_w)) + pad * 2
    for r in texts:
        for j, c in enumerate(r):
            col_w[j] = max(col_w[j], int(mixed_len(c, f_m, f_c, mono_w)) + pad * 2)
    if first_col_w_min:
        col_w[0] = max(col_w[0], first_col_w_min * S)
    W = sum(col_w) + 1
    bar_h = 30 * S
    H = bar_h + hh + rh * len(rows) + 1
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, title, subtitle)
    # header
    y = bar_h
    d.rectangle([0, y, W, y + hh], fill=TEAL)
    x = 0
    for j, h in enumerate(headers):
        hw = mixed_len(str(h), f_h, f_c, mono_w)
        if j == 0:
            draw_mixed(d, (x + pad, y + 6 * S), str(h), f_h, f_c, (255, 255, 255), mono_w)
        else:
            draw_mixed(d, (x + col_w[j] - pad - hw, y + 6 * S), str(h), f_h, f_c,
                       (255, 255, 255), mono_w)
        x += col_w[j]
    y += hh
    for i, r in enumerate(texts):
        if i % 2 == 1:
            d.rectangle([0, y, W, y + rh], fill=ZEBRA)
        x = 0
        for j, c in enumerate(r):
            fg, bg, bold = style_fn(i, j, rows[i][j], c)
            if bg:
                d.rectangle([x + 1, y + 1, x + col_w[j] - 1, y + rh - 1], fill=bg)
            fnt = F_MONO_B(11) if bold else f_m
            if j == 0:
                draw_mixed(d, (x + pad, y + 4 * S), c, fnt, f_c, fg, mono_w)
            else:
                cw = mixed_len(c, fnt, f_c, mono_w)
                draw_mixed(d, (x + col_w[j] - pad - cw, y + 4 * S), c, fnt, f_c, fg, mono_w)
            x += col_w[j]
        y += rh
    # grid
    x = 0
    for j in range(n_col + 1):
        d.line([x, bar_h, x, H], fill=GRID, width=1)
        if j < n_col:
            x += col_w[j]
    yy = bar_h
    for _ in range(len(rows) + 1):
        d.line([0, yy, W, yy], fill=GRID, width=1)
        yy += hh if yy == bar_h else rh
    d.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=S)
    save(img, name)


# ---------------------------------------------------------------- CSV helpers
def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return [r for r in csv.reader(f) if any(c.strip() for c in r)]


def paired_table(csv_path):
    """report_setup/hold/trans.csv：两列表头（corner 跨 violation number / biggest violation）。
    返回 (corners, rows)，rows = (metric_label, kind, values)，kind ∈ {'vn','bv'}。"""
    rows_raw = read_csv(csv_path)
    corners = [c for c in rows_raw[0] if c.strip()]
    out = []
    for r in rows_raw[2:]:
        name = r[0].strip()
        vals = r[1:]
        vn = [vals[i * 2] if i * 2 < len(vals) else "" for i in range(len(corners))]
        bv = [vals[i * 2 + 1] if i * 2 + 1 < len(vals) else "" for i in range(len(corners))]
        if any(v.strip() not in ("", "0") for v in vn):
            out.append((f"{name} (violation number)", "vn", vn))
        out.append((f"{name} (biggest violation)", "bv", bv))
    return corners, out


def style_violation(i, j, raw, disp):
    if j == 0:
        return INK, None, False
    s = str(raw).strip()
    try:
        v = float(s)
    except ValueError:
        return INK, None, False
    if v < 0:
        return RED_TX, RED_BG, True
    if v == 0:
        return GREEN_TX, None, False
    if "violation number" in str(disp):
        return RED_TX, RED_BG, True
    return INK, None, False


def make_violation_style(kinds):
    def fn(i, j, raw, disp):
        if j == 0:
            return INK, None, False
        try:
            v = float(str(raw).strip())
        except ValueError:
            return INK, None, False
        if kinds[i] == "vn":
            return (RED_TX, RED_BG, True) if v != 0 else (GREEN_TX, None, False)
        return (RED_TX, RED_BG, True) if v < 0 else (INK if v != 0 else GREEN_TX, None, False)
    return fn


def gen_setup_hold_trans():
    for mode, tag in (("2P", "2p"), ("1P", "1p")):
        for kind in ("setup", "hold", "trans"):
            csv_path = os.path.join(SR, "postpt_summary", f"POST_PT_{mode}",
                                    f"report_{kind}.csv")
            corners, rows = paired_table(csv_path)
            kinds_l = [k for _, k, _ in rows]
            label = {"setup": "setup/max 路径违例总表", "hold": "hold/min 路径违例总表",
                     "trans": "max_trans/cap 约束违例总表"}[kind]
            if kind == "setup" and mode == "1P":
                label = "setup/max 路径违例总表"
            render_table(
                f"3{0 if mode=='2P' else 1}_postpt_{kind}_{tag}.png",
                f"report_{kind}.csv ({mode})", label,
                ["metric"] + corners,
                [[m] + v for m, _, v in rows],
                make_violation_style(kinds_l),
            )


def gen_physkew():
    for mode, tag in (("2P", "2p"), ("1P", "1p")):
        rows_raw = read_csv(os.path.join(SR, "postpt_summary", f"POST_PT_{mode}",
                                         "report_phy_busskew.csv"))
        headers = rows_raw[0]
        rows = rows_raw[1:]

        def style(i, j, raw, disp):
            if j == 0:
                return INK, None, False
            try:
                v = float(str(raw).strip())
            except ValueError:
                return INK, None, False
            if v < 0:
                return RED_TX, RED_BG, True
            return (GREEN_TX, None, False) if v == 0 else (INK, None, False)

        render_table(f"3{0 if mode=='2P' else 1}_postpt_physkew_{tag}.png",
                     f"report_phy_busskew.csv ({mode})", "PHY bus skew 各组 slack（ns）",
                     headers, rows, style)


def gen_sd_margin():
    for mode, tag in (("2P", "2p"), ("1P", "1p")):
        rows_raw = read_csv(os.path.join(SR, "postpt_summary", f"POST_PT_{mode}",
                                         "report_sd_busskew.csv"))
        headers = rows_raw[0]
        rows = []
        for r in rows_raw[1:]:
            name = r[0].strip()
            if "margin" not in name:
                continue
            name = re.sub(r"\s*:\s*\[-1:6\]\s*$", "", name)
            rows.append([name] + r[1:])

        def style(i, j, raw, disp):
            if j == 0:
                return INK, None, False
            try:
                v = float(str(raw).strip())
            except ValueError:
                return INK, None, False
            if v == 0:
                return GRAY_TX, None, False          # 无该 lane 数据
            if -1.0 <= v <= 6.0:
                return GREEN_TX, None, False          # 满足规格 [-1, 6]
            return RED_TX, RED_BG, True

        render_table(f"3{3 if mode=='2P' else 4}_postpt_sdskew_margin_{tag}.png",
                     f"report_sd_busskew.csv ({mode})", "SD skew margin，规格 [-1, +6] ns",
                     headers, rows, style)


# ---------------------------------------------------------------- code screenshots
def read_lines(path, a, b):
    with open(path, encoding="utf-8", errors="replace") as f:
        ls = f.read().splitlines()
    return [(i, ls[i - 1]) for i in range(a, min(b, len(ls)) + 1)]


def gen_code_images():
    # 24 design.set VT 开关
    render_code("24_design_set_vt.png", "design.set", "LVT_EN=0 / SVT_EN=1",
                read_lines(f"{HV}/SYNTHESIS/ip/syn_HV2M23_digital_top/design.set", 71, 75),
                hl_lines=(73, 75))
    # 25 common_db.tcl 145nm 库定义
    render_code("25_common_db_145.png", "common_db.tcl", "nexchip_145_9t 库定义（SL=LVT / SS=SVT）",
                read_lines(f"{HV}/SYNTHESIS/common/tcl_dir/common/common_db.tcl", 744, 750),
                hl_lines=(749, 750))
    # 26 clk_period.tcl
    render_code("26_clk_period.png", "clk_period.tcl",
                "MARGIN 0.80 · DPSEL_I=1（2P）· RX_CLKP 10.71ns",
                read_lines(f"{HV}/SYNTHESIS/common/tcl_dir/common/clk_period.tcl", 1, 30),
                hl_lines=(2, 4, 16, 29, 30))
    # 27 SVT 100%（VT group report）
    render_code("27_svt_100.png", "HV2M23_digital_top.rpt",
                "Threshold Voltage Group Report — SVT 100%",
                read_lines(f"{SR}/HV2M23_digital_top.rpt", 15386, 15401),
                hl_lines=(15392, 15398))
    # 35 DC QoR（两个 path group 段）
    render_code("35_dc_qor.png", "HV2M23_digital_top.rpt",
                "DC QoR：slack ≥ 0 · 违例 0 · hold 0",
                read_lines(f"{SR}/HV2M23_digital_top.rpt", 15077, 15102),
                hl_lines=(15081, 15084, 15094, 15097))
    # 36 ckf.rpt（跳过 black box cell 列表）
    ckf = read_lines(f"{HV}/SYNTHESIS/ip/syn_HV2M23_digital_top/ckf/rep_dir/ckf.rpt", 1, 7)
    ckf += read_lines(f"{HV}/SYNTHESIS/ip/syn_HV2M23_digital_top/ckf/rep_dir/ckf.rpt", 21, 26)
    render_code("36_ckf_rpt.png", "ckf.rpt", "Floating / Latch / Other 为空 = 通过",
                ckf, hl_lines=(2, 22, 25))
    # 37 nlint.log 末尾
    render_code("37_nlint_rpt.png", "nlint.log",
                "Total 89 Error(s), 11 Warning(s)（缺标准单元库所致，与设计功能无关）",
                read_lines(f"{HV}/SYNTHESIS/ip/syn_HV2M23_digital_top/nlint/rep_dir/nlint.log",
                           441, 456),
                hl_lines=(453, 454))
    # 32 PTPX 功耗报告 Hierarchy 段
    render_code("32_ptpx_power_rpt.png", "HV2M23_digital_top_power.rpt（1lane_fre1p8_tt_0812）",
                "Hierarchy 表：顶层 Total Power",
                read_lines(f"{SR}/power/px_85c_random/rep_dir_1lane_fre1p8_tt_0812/"
                           "HV2M23_digital_top_power.rpt", 903, 912),
                hl_lines=(907,))


# ---------------------------------------------------------------- buf type (slide 30)
def gen_buf_type():
    def agg(path, type_col):
        with open(path, encoding="utf-8", errors="replace") as f:
            rd = csv.reader(f, delimiter="\t")
            header = next(rd)
            rows = [r for r in rd if len(r) >= 4]
        types = Counter(r[type_col] for r in rows)
        status = Counter(r[3] for r in rows)
        ports = len(set(r[0] for r in rows))
        return rows, types, status, ports

    in_rows, in_types, in_status, in_ports = agg(
        os.path.join(SR, "input_port_first_buf_type.tsv"), 1)
    out_rows, out_types, out_status, out_ports = agg(
        os.path.join(SR, "output_port_last_buf_type.tsv"), 1)

    f_h, f_m, f_c = F_MONO_B(11), F_MONO(11), F_CJK(11)
    f_hb, f_sec = F_CJK_B(11), F_CJK_B(12)
    mono_w = f_m.getlength("M")
    pad = 10 * S

    # 预期例外端口（setcase 常量传播的正常结果，非 error）
    EXPECTED = {"DPSEL_I", "reg_lane_pd_L1"}

    def exceptions(rows):
        """cell 类型为 '-' 的端口（无首/末级 buf 的例外端口）。"""
        return [(r[0], r[3]) for r in rows if r[1].strip() == "-"]

    def panel_rows(types, status):
        t = [("cell 类型", "记录数")] + sorted(types.items(), key=lambda x: -x[1])
        s = [("STATUS", "记录数")] + sorted(status.items(), key=lambda x: -x[1])
        return t, s

    panels = [
        (f"input_port_first_buf_type.tsv（{in_ports} 端口 / {len(in_rows)} 行）",
         *panel_rows(in_types, in_status), exceptions(in_rows)),
        (f"output_port_last_buf_type.tsv（{out_ports} 端口 / {len(out_rows)} 行）",
         *panel_rows(out_types, out_status), exceptions(out_rows)),
    ]
    # 尺寸
    col1 = int(max(f_m.getlength(str(c)) for p in panels for tb in (p[1], p[2])
                   for c, _ in tb)) + pad * 2
    col2 = int(f_m.getlength("记录数")) + pad * 2
    bar_h = 30 * S
    sec_h = 24 * S
    rh = 20 * S
    note_h = 20 * S
    gap = 24 * S
    pan_w = col1 + col2
    for ptitle, _, _, _ in panels:  # 面板至少装得下小节标题
        pan_w = max(pan_w, int(f_sec.getlength(ptitle)) + 4 * S)
    col1 = pan_w - col2
    W = pan_w * 2 + gap + pad * 2
    H = bar_h + pad
    for title, t, s, exc in panels:  # 与下方绘制逻辑保持一致的高度累加
        h = bar_h + pad + sec_h + rh * len(t) + 8 * S + rh * len(s) + pad
        if exc:
            h += note_h
        H = max(H, h)
    img = Image.new("RGB", (W, H), (255, 255, 255))
    d = ImageDraw.Draw(img)
    title_bar(d, W, "IO 首/末级 buffer type 统计（SVT 换库后）",
              "report_input_last_buf.tcl / report_output_last_buf.tcl 输出")
    for k, (ptitle, t_rows, s_rows, exc) in enumerate(panels):
        x0 = pad + k * (pan_w + gap)
        y = bar_h + pad
        d.text((x0, y), ptitle, font=f_sec, fill=TEAL_DK)
        y += sec_h
        for tb in (t_rows, s_rows):
            for i, (c, n) in enumerate(tb):
                if i == 0:
                    d.rectangle([x0, y, x0 + pan_w, y + rh], fill=TEAL)
                    draw_mixed(d, (x0 + 4 * S, y + 3 * S), str(c), f_h, f_hb,
                               (255, 255, 255), mono_w)
                    draw_mixed(d, (x0 + col1 + 2 * S, y + 3 * S), str(n), f_h, f_hb,
                               (255, 255, 255), mono_w)
                else:
                    if i % 2 == 0:
                        d.rectangle([x0, y, x0 + pan_w, y + rh], fill=ZEBRA)
                    if str(c) == "-" or str(c).startswith("NO_"):
                        fg, bold_it = RED_TX, True   # 例外项标红
                    else:
                        fg, bold_it = INK, False
                    draw_mixed(d, (x0 + 4 * S, y + 3 * S), str(c),
                               f_h if bold_it else f_m, f_c, fg, mono_w)
                    d.text((x0 + col1 + 2 * S, y + 3 * S), str(n),
                           font=f_h if bold_it else f_m, fill=fg)
                y += rh
            d.rectangle([x0, y - rh * len(tb), x0 + pan_w, y], outline=GRID, width=S)
            y += 8 * S
        for port, st in exc:  # 例外端口说明
            if port in EXPECTED:
                note = f"预期例外：{port} — {st}（setcase 常量传播，确认无误）"
                draw_mixed(d, (x0 + 2 * S, y), note, f_m, f_c, GREEN_TX, mono_w)
            else:
                note = f"例外：{port} — {st}"
                draw_mixed(d, (x0 + 2 * S, y), note, f_m, f_c, RED_TX, mono_w)
            y += note_h
    d.rectangle([0, 0, W - 1, H - 1], outline=BORDER, width=S)
    save(img, "38_buf_type.png")


if __name__ == "__main__":
    print("code images:")
    gen_code_images()
    print("table images:")
    gen_setup_hold_trans()
    gen_physkew()
    gen_sd_margin()
    print("buf type:")
    gen_buf_type()
    print("done.")

# ymzhu 2026-11-04 15:54
