# -*- coding: utf-8 -*-
"""生成 hk1v11-longcode-420b-verification 报告用的三张结构框图 SVG：
1. longcode_verification_architecture.svg  —— 验证环境整体架构（0717v1 现状）
2. pydec_tx_rx_structure.svg               —— 收发结构框图（不看 RTL、脚本离线解码比对）
3. 8b10b_vs_420b_architecture.svg          —— 8B/10B vs 420B 对比（修正位序等过时内容）

输出目录：hk1v11-longcode-420b-verification/
"""
import os

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "hk1v11-longcode-420b-verification")

FONT = ("'Helvetica Neue', Helvetica, Arial, 'PingFang SC', 'Microsoft YaHei',"
        " 'Microsoft JhengHei', 'SimHei', sans-serif")

# 配色（与站点 teal 主题一致）
C = dict(
    dark="#1e293b", muted="#64748b", container="#f8fafc", line="#e2e8f0",
    blue="#2563eb", green="#059669", purple="#7c3aed", orange="#ea580c",
    teal="#0f766e", teal_soft="#ccfbf1", gray="#9ca3af",
)


def head(w, h):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',
        f'  <style>text {{ font-family: {FONT}; }}</style>',
        '  <defs>',
        '    <marker id="ar-blue" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{C["blue"]}"/></marker>',
        '    <marker id="ar-green" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{C["green"]}"/></marker>',
        '    <marker id="ar-purple" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{C["purple"]}"/></marker>',
        '    <marker id="ar-orange" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        f'<polygon points="0 0, 10 3.5, 0 7" fill="{C["orange"]}"/></marker>',
        '    <marker id="ar-gray" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">'
        '<polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af"/></marker>',
        '  </defs>',
        f'  <rect width="{w}" height="{h}" fill="#ffffff"/>',
    ]


def rect(x, y, w, h, fill="#ffffff", stroke="#d1d5db", rx=8, sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def text(x, y, s, size=12, fill=C["dark"], weight=None, anchor="middle"):
    wt = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{wt}>{s}</text>'


def box(x, y, w, h, title, subs=(), fill="#ffffff", stroke="#d1d5db",
        tfill=C["dark"], sfill=C["muted"], tsize=11.5, ssize=9.5, sw=1.5):
    """标题+若干副标题行的圆角盒子（垂直居中排布）"""
    out = [rect(x, y, w, h, fill, stroke, 8, sw)]
    n = len(subs)
    line_h, gap = 13, 16
    total = line_h + n * gap
    ty = y + (h - total) / 2 + line_h - 3
    out.append(text(x + w / 2, ty, title, tsize, tfill, "600"))
    for i, s in enumerate(subs):
        out.append(text(x + w / 2, ty + (i + 1) * gap, s, ssize, sfill))
    return out


def container(x, y, w, h, label, lfill="#475569", fill=C["container"], stroke=C["line"]):
    return [rect(x, y, w, h, fill, stroke, 10, 2),
            text(x + 16, y + 22, label, 13, lfill, "600", "start")]


def arrow(x1, y1, x2, y2, color="blue", sw=1.5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{C[color]}" '
            f'stroke-width="{sw}"{d} marker-end="url(#ar-{color})"/>')


def path(d, color="blue", sw=1.5, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" stroke="{C[color]}" stroke-width="{sw}" fill="none"'
            f'{dd} marker-end="url(#ar-{color})"/>')


# ---------------------------------------------------------------------------
# 图 1：验证环境整体架构（0717v1）
# ---------------------------------------------------------------------------
def gen_architecture():
    L = head(1200, 980)
    A = L.append
    A(text(600, 40, "HK1V11 420b 长编码验证环境 · 整体架构", 22, C["dark"], "600"))
    A(text(600, 64, "0717v1 现状 · 基于 DV_TCON_C 8B/10B 环境重建 · `CHPI_MODE_420B` 宏隔离 · 新增接收端离线验证路径（不看 RTL 解码器）",
           12, C["muted"]))

    # ---- Row1 Test / Config ----
    L += container(40, 88, 1120, 86, "Test / Config Layer")
    L += box(70, 118, 250, 48, "t_H3840_V16_FPS120_420b", ("当前主调 case（bind tap + pydec）",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11)
    L += box(340, 118, 200, 48, "t_8b1lane_420b_basic", ("smoke case",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11)
    L += box(560, 118, 200, 48, "user_def.sv", ("`define CHPI_MODE_420B",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11.5)
    L += box(780, 118, 350, 48, "env_cfg", ("SCREN · HACT · VACT · LANE_NUM · get_ctrlL/F_reg",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11.5)

    # ---- Row2 TX sequence ----
    L += container(40, 192, 696, 292, "发送端 TX · isptx_sequence.sv（420b 分支）", C["teal"])
    tasks = [
        ("send_420b_lsp()", "K2 + 0xEA~ED×8 + Dmy + K3 · 不加扰"),
        ("send_420b_active_line()", "K1 + CTRL_L + Video + K2"),
        ("send_420b_ctrl_f_line()", "K4 + CTRL_F(ENC) + Dmy + K2 · 单独成行"),
        ("send_420b_vblank_line()", "K1 + CTRL_L + VBK + K2"),
        ("send_420b_idle_pattern()", "K5~K8 IDLE · 不加扰"),
    ]
    for i, (t1, s1) in enumerate(tasks):
        L += box(64, 226 + i * 52, 280, 42, t1, (s1,), tsize=11, ssize=9)
    mids = [
        ("build_bit_stream_from_bytes()", "byte → bit stream"),
        ("pad_bit_stream()", "跨 lane 70-bit dummy 对齐"),
        ("encode_with_70b_alignment()", "scramble_en = env_cfg.SCREN"),
        ("dump_raw_bytes()", "编码前 raw byte 转储 ↓"),
    ]
    for i, (t1, s1) in enumerate(mids):
        L += box(360, 226 + i * 52, 180, 42, t1, (s1,), fill="#f0fdfa", stroke="#99f6e4",
                 tsize=8.5 if len(t1) > 24 else 10.5, ssize=8.5)
    # ref model
    A(rect(556, 226, 156, 198, "#faf5ff", "#e9d5ff", 8, 1.5))
    A(text(634, 248, "long_encoding", 10.5, C["dark"], "600"))
    A(text(634, 262, "ref_model.sv", 10.5, C["dark"], "600"))
    for i, s in enumerate(["encode_413b_to_420b()", "tag 替换 · 全 0/全 1", "G16(X) 16-bit LFSR",
                           "K1~K4 40-bit 常量", "K5~K8 10-bit 常量", "encoded_bits_", "70aligned()"]):
        A(text(634, 284 + i * 16, s, 9, C["muted"]))

    # ---- Row3 Transaction / Driver ----
    L += container(40, 504, 696, 106, "Transaction / Driver")
    L += box(64, 534, 300, 56, "isptx_transaction.sv",
             ("bit[19:0] one_pkt_20b", "bit[39:0] k1_420b ~ k4_420b"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=11.5, ssize=9.5)
    L += box(404, 534, 308, 56, "isptx_driver.sv（420b）",
             ("drv_one_pkt_20b() · LSB-first", "drv_kx_key_420b() → vif.rxn0/rxp0"),
             tsize=11.5, ssize=9.5)

    # ---- Right DUT ----
    L += container(776, 192, 384, 418, "接收端 RX · DUT（HDL long_encoding）", "#991b1b")
    A(rect(800, 226, 336, 62, "#ffffff", C["green"], 8, 2))
    A(text(968, 248, "CHPI_KCODE_ALIGN_LONG_L0", 11, C["dark"], "600"))
    A(text(968, 264, "K1~K4 检测 · 20-bit 对齐", 9.5, C["muted"]))
    A(text(968, 280, "DATA_ALIGN_PRE → tap", 9.5, C["green"], "600"))
    A(rect(1072, 232, 52, 18, C["green"], C["green"], 9, 1))
    A(text(1098, 245, "TAP", 10, "#ffffff", "700"))
    L += box(800, 304, 336, 54, "long_decoding_top.v",
             ("din_20b_aligned ← DATA0_ALIGN_LONG（0717 修复）", "42-bit buffer · 8/16/24-bit 打包"),
             tsize=11, ssize=9)
    L += box(800, 374, 336, 54, "decoder_7b.v",
             ("420b → 413b · tag 还原", "decode_en 窗口（K1/K4 开 · K2/K3 关）"), tsize=11, ssize=9)
    L += box(800, 444, 336, 54, "descramble_7b.v",
             ("G16(X) 解扰 · K3 上升沿复位", "scramble_en=0 旁路"), tsize=11, ssize=9)
    L += box(800, 514, 336, 54, "dout_24b + 2-bit valid", ("→ 后级像素通路",),
             tsize=11, ssize=9)
    A(rect(792, 298, 352, 278, "none", "#9ca3af", 8, 1.2, "6,3"))
    A(text(968, 594, "灰框内：RTL 解码链 —— 排障焦点，离线验证不依赖", 9.5, "#6b7280"))

    # ---- Row4 离线验证 ----
    L += container(40, 650, 1120, 192, "接收端离线验证路径 · 不看 RTL 解码器（0717 新增）",
                   C["green"], "#f0fdf4", "#bbf7d0")
    L += box(64, 688, 230, 60, "long_rtl_tap_debug.sv",
             ("bind 注入 KCODE_ALIGN · 零 RTL 修改", "抓 DATA_ALIGN_PRE"), tsize=10.5, ssize=9)
    L += box(330, 688, 196, 60, "long_rtl_dap_lane0.md",
             ("每拍 20-bit 对齐数据", "全量转储"), tsize=10, ssize=9)
    L += box(562, 688, 246, 60, "decode_dap.py",
             ("离线 413b/420b 解码", "K 码对定位 · tag 替换 · G16 解扰"), tsize=11, ssize=9)
    L += box(844, 688, 200, 60, "long_pydec_lane0.md",
             ("离线解码字节流", "区域：LSP / CTRL_F / LINE"), tsize=10, ssize=9)
    L += box(64, 768, 280, 48, "long_rawbyte_seq_lane0.md",
             ("发送端编码前 raw byte（期望值）",), tsize=10, ssize=9)
    A(rect(566, 768, 380, 48, "#ecfdf5", C["green"], 8, 2))
    A(text(756, 788, "long_pydec_report_lane0.md", 10.5, "#047857", "600"))
    A(text(756, 806, "逐区域比对 verdict：LSP / CTRL_F / LINE 全对 ✅", 9.5, "#047857"))

    # ---- Row5 版本管理 ----
    L += container(40, 862, 1120, 58, "版本管理 · longcode_ver/")
    A(text(300, 896, "0717v1 当前工作目录 · 文件统一命名 *_20260717_v1 · CHANGELOG.md / README.md / migration_checklist.md 同步维护",
           10.5, "#475569", None, "start"))

    # ---- arrows（最后画，压在线条层上方）----
    A(arrow(375, 174, 375, 192, "blue"))
    A(arrow(660, 174, 660, 192, "blue"))
    A(arrow(955, 174, 955, 192, "orange", 1.5, "5,3"))
    A(arrow(540, 320, 556, 320, "blue"))
    A(arrow(375, 484, 375, 504, "blue"))
    A(arrow(364, 562, 404, 562, "blue"))
    A(path("M 712 562 L 756 562 L 756 257 L 800 257", "blue", 2))
    A(f'<text transform="rotate(-90 748 420)" x="748" y="420" font-size="10" fill="{C["blue"]}" text-anchor="middle">20-bit 包流 / 40-bit K 码 · 串行链路</text>')
    for y1, y2 in [(288, 304), (358, 374), (428, 444), (498, 514)]:
        A(arrow(968, y1, 968, y2, "blue"))
    # tap 绿色路径：KCODE_ALIGN → 右侧外廊 → 底部走廊 → tap 模块
    A(path("M 1136 257 L 1178 257 L 1178 632 L 179 632 L 179 688", "green", 2, "6,3"))
    A(text(700, 624, "tap DATA_ALIGN_PRE（每拍 20-bit 对齐数据）", 10, C["green"]))
    # 发送端 raw byte（期望值）紫色路径，跨越绿色走廊处加跳线弧
    A(path("M 204 610 L 204 768", "purple", 1.5, "5,3"))
    A(f'<path d="M 204 626 A 5.5 5.5 0 0 1 204 638" stroke="{C["purple"]}" stroke-width="1.5" fill="none"/>')
    # 离线链路内部箭头
    A(arrow(294, 718, 330, 718, "green"))
    A(arrow(526, 718, 562, 718, "green"))
    A(arrow(808, 718, 844, 718, "green"))
    A(arrow(944, 748, 944, 768, "green"))
    A(arrow(344, 792, 566, 792, "purple", 1.5, "5,3"))
    A(text(455, 784, "逐区域 diff", 9.5, C["purple"]))

    # ---- legend ----
    ly = 956
    A(f'<line x1="60" y1="{ly-4}" x2="92" y2="{ly-4}" stroke="{C["blue"]}" stroke-width="2" marker-end="url(#ar-blue)"/>')
    A(text(98, ly, "主数据流", 11, C["muted"], None, "start"))
    A(f'<line x1="180" y1="{ly-4}" x2="212" y2="{ly-4}" stroke="{C["purple"]}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ar-purple)"/>')
    A(text(218, ly, "期望值 / 比对", 11, C["muted"], None, "start"))
    A(f'<line x1="340" y1="{ly-4}" x2="372" y2="{ly-4}" stroke="{C["green"]}" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#ar-green)"/>')
    A(text(378, ly, "离线验证路径（不看 RTL 解码器）", 11, C["muted"], None, "start"))
    A(f'<line x1="640" y1="{ly-4}" x2="672" y2="{ly-4}" stroke="{C["orange"]}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ar-orange)"/>')
    A(text(678, ly, "配置 / 控制", 11, C["muted"], None, "start"))

    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 图 2：收发结构框图 —— 接收端不看 RTL，脚本离线解码比对
# ---------------------------------------------------------------------------
def gen_pydec():
    L = head(1200, 680)
    A = L.append
    A(text(600, 40, "420b 收发结构框图 · 接收端不看 RTL 的脚本离线验证", 21, C["dark"], "600"))
    A(text(600, 64, "在 K 码对齐点 tap 线上 20-bit 数据（DATA_ALIGN_PRE），Python 直接做 413b/420b 解码，与发送端原始字节逐区域比对",
           12, C["muted"]))

    # ---- 发送端 TX ----
    L += container(40, 100, 380, 340, "发送端 TX（UVM）", C["teal"])
    L += box(64, 128, 332, 60, "isptx_sequence.sv",
             ("组帧：LSP / CTRL_F / Active / VBK / IDLE", "K1~K4 40-bit · K5~K8 10-bit"), tsize=11.5, ssize=9)
    L += box(64, 204, 332, 60, "long_encoding_ref_model.sv",
             ("413b → 420b 编码 · tag 替换", "G16(X) 加扰（scramble_en = SCREN）"), tsize=11, ssize=9)
    L += box(64, 284, 332, 60, "isptx_driver.sv",
             ("20-bit 包 / 40-bit K 码 · LSB-first", "→ vif.rxn0 / rxp0"), tsize=11.5, ssize=9)
    L += box(64, 364, 332, 60, "dump_raw_bytes() → long_rawbyte_seq_lane0.md",
             ("编码前 raw byte 转储（期望值）",), fill="#faf5ff", stroke="#e9d5ff",
             tfill=C["purple"], tsize=9.5, ssize=9)

    # ---- 串行链路（差分对）----
    A(path("M 396 292 L 452 292 L 452 152 L 524 152", "blue", 2))
    A(path("M 396 304 L 468 304 L 468 164 L 524 164", "blue", 2))
    A(f'<text transform="rotate(-90 438 227)" x="438" y="227" font-size="9.5" fill="{C["blue"]}" text-anchor="middle">CHPI 串行链路（rxp / rxn）</text>')

    # ---- 接收端 RX ----
    L += container(500, 100, 660, 340, "接收端 RX（DUT + 脚本）", "#991b1b")
    A(rect(524, 128, 300, 64, "#ffffff", C["green"], 8, 2))
    A(text(674, 150, "CHPI_KCODE_ALIGN_LONG", 11, C["dark"], "600"))
    A(text(674, 166, "K1~K4 检测 · 20-bit 对齐", 9, C["muted"]))
    A(text(674, 182, "DATA_ALIGN_PRE → tap", 9.5, C["green"], "600"))
    A(rect(784, 134, 34, 16, C["green"], C["green"], 8, 1))
    A(text(801, 146, "TAP", 9, "#ffffff", "700"))
    # 不看的 RTL 段
    A(rect(524, 214, 300, 120, "#f9fafb", "#9ca3af", 8, 1.5, "6,3"))
    A(text(674, 238, "RTL 解码链（不看 · 不依赖）", 11, "#6b7280", "600"))
    A(text(674, 256, "long_decoding_top · decoder_7b", 9, "#6b7280"))
    A(text(674, 272, "descramble_7b → dout_24b + 2-bit valid", 9, "#6b7280"))
    A(text(674, 296, "排障焦点在 RTL 解码链（3.6 节）", 9, "#9ca3af"))
    A(text(674, 312, "但验证线上数据不依赖它", 9, "#9ca3af"))
    # 脚本链
    L += box(870, 128, 266, 64, "long_rtl_tap_debug.sv",
             ("bind 注入 · 零 RTL 修改", "→ long_rtl_dap_lane0.md（每拍 20-bit）"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=10.5, ssize=8.5)
    L += box(870, 212, 266, 64, "decode_dap.py（Python）",
             ("离线 413b/420b 解码", "K 码对定位 · tag 替换 · G16 解扰"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=10.5, ssize=9)
    L += box(870, 300, 266, 64, "long_pydec_lane0.md",
             ("离线解码字节流", "分区域：LSP / CTRL_F / LINE"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=10.5, ssize=9)

    # ---- 底部比对区 ----
    L += container(40, 480, 1120, 130, "离线比对（脚本完成 · 不依赖 DUT 解码结果）",
                   C["purple"], "#faf5ff", "#e9d5ff")
    L += box(64, 520, 300, 64, "long_rawbyte_seq_lane0.md", ("发送端原始字节（期望值）",),
             tsize=10, ssize=9)
    A(rect(470, 520, 360, 64, "#ecfdf5", C["green"], 8, 2))
    A(text(650, 544, "long_pydec_report_lane0.md", 10.5, "#047857", "600"))
    A(text(650, 562, "逐区域 diff · verdict：LSP / CTRL_F / LINE 全对 ✅", 9.5, "#047857"))
    A(text(650, 578, "⇒ 线上数据正确 · 发送端排除", 9, "#047857"))
    L += box(846, 520, 290, 64, "long_pydec_lane0.md", ("线上数据离线解码（实际值）",),
             tsize=10, ssize=9)

    # ---- arrows ----
    A(arrow(230, 188, 230, 204, "blue"))
    A(arrow(230, 264, 230, 284, "blue"))
    A(arrow(674, 192, 674, 214, "gray", 1.5, "5,3"))
    A(text(700, 206, "传统路径", 9, "#9ca3af", None, "start"))
    A(arrow(824, 160, 870, 160, "green", 2))
    A(arrow(1003, 192, 1003, 212, "green", 2))
    A(arrow(1003, 276, 1003, 300, "green", 2))
    A(path("M 214 424 L 214 520", "purple", 1.5, "5,3"))
    A(path("M 1003 364 L 1003 440 L 1003 520", "green", 1.5, "6,3"))
    A(arrow(364, 552, 470, 552, "purple", 1.5, "5,3"))
    A(text(417, 544, "期望值", 9, C["purple"]))
    A(arrow(846, 552, 830, 552, "green", 2))
    A(text(838, 544, "实际值", 9, C["green"], None, "end"))

    # ---- legend ----
    ly = 652
    A(f'<line x1="60" y1="{ly-4}" x2="92" y2="{ly-4}" stroke="{C["blue"]}" stroke-width="2" marker-end="url(#ar-blue)"/>')
    A(text(98, ly, "主数据流（线上）", 11, C["muted"], None, "start"))
    A(f'<line x1="240" y1="{ly-4}" x2="272" y2="{ly-4}" stroke="{C["green"]}" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#ar-green)"/>')
    A(text(278, ly, "脚本离线验证路径", 11, C["muted"], None, "start"))
    A(f'<line x1="430" y1="{ly-4}" x2="462" y2="{ly-4}" stroke="{C["purple"]}" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ar-purple)"/>')
    A(text(468, ly, "期望值（发送端 dump）", 11, C["muted"], None, "start"))
    A(f'<line x1="640" y1="{ly-4}" x2="672" y2="{ly-4}" stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#ar-gray)"/>')
    A(text(678, ly, "不看的 RTL 路径", 11, C["muted"], None, "start"))

    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 图 3：8B/10B vs 420B 架构对比（0717v1 修正）
# ---------------------------------------------------------------------------
def gen_compare():
    L = head(1400, 1210)
    A = L.append
    A(text(700, 42, "8B/10B vs 420B 长编码 · 验证架构对比", 22, C["dark"], "600"))
    A(text(700, 66, "0717v1 修正：420b 发送方向为 LSB-first（0715 起与 8B/10B 一致）；新增接收端离线验证路径",
           12, C["muted"]))

    # ---- 左列 8B/10B ----
    L += container(40, 88, 640, 566, "8B/10B 模式（无 CHPI_MODE_420B 宏）", "#9a3412")
    L += box(70, 118, 580, 56, "Test Layer",
             ("t_8b1lane · base_vseq · user_def.sv · env_cfg",), tsize=11.5, ssize=9.5)
    A(rect(70, 190, 580, 126, "#ffffff", "#d1d5db", 8, 1.5))
    A(text(84, 212, "isptx_sequence.sv", 11.5, C["dark"], "600", "start"))
    for i, s in enumerate(["send_LSP_seq()", "send_CTRLF_seq()", "send_CTRLL_seq()", "send_ppm()"]):
        L += box(90 + (i % 4) * 140, 222, 130, 34, s, (), fill="#f0fdfa", stroke="#99f6e4",
                 tfill=C["teal"], tsize=9.5)
    A(rect(90, 266, 540, 38, "#f0fdfa", "#99f6e4", 6, 1.5))
    A(text(360, 290, "8-bit pixel / reg → G24(X) 24-bit scramble() → encode_8b10b() → 10-bit symbol",
           9.5, C["teal"]))
    L += box(70, 332, 580, 60, "isptx_transaction.sv",
             ("bit[9:0] one_pkt · bit[9:0] k1/k2/k3/k4", "TYPE_DRV_ONE_PKT / TYPE_DRV_Kx_KEY"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=11, ssize=9)
    L += box(70, 408, 580, 56, "isptx_driver.sv",
             ("drv_one_pkt() / drv_k1_key() · LSB-first（pkt[0] 先发） → vif.rxn0/rxp0",),
             tsize=11.5, ssize=9.5)
    L += box(70, 480, 580, 78, "DUT：8B/10B RX",
             ("10-bit symbol / K-code → 8B/10B decode → 8-bit data → descramble G24(X)",
              "输出：8-bit data"), fill="#fef2f2", stroke="#fecaca", tfill="#991b1b",
             sfill="#991b1b", tsize=11.5, ssize=9.5)
    L += box(70, 574, 580, 64, "线上数据验证",
             ("C model / scoreboard 对比",), fill="#f9fafb", stroke="#d1d5db",
             tsize=11, ssize=9.5)

    # ---- 右列 420B ----
    L += container(720, 88, 640, 566, "420B 长编码模式（`define CHPI_MODE_420B）", "#6b21a8")
    L += box(750, 118, 580, 56, "Test Layer",
             ("t_H3840_V16_FPS120_420b · t_8b1lane_420b_basic · user_def.sv",), tsize=11.5, ssize=9)
    A(rect(750, 190, 580, 126, "#ffffff", "#d1d5db", 8, 1.5))
    A(text(764, 212, "isptx_sequence.sv（420b 分支）", 11.5, C["dark"], "600", "start"))
    tasks420 = ["send_420b_lsp()", "send_420b_active_line()", "send_420b_ctrl_f_line()",
                "send_420b_vblank_line()", "send_420b_idle_pattern()"]
    for i, s in enumerate(tasks420):
        L += box(770 + (i % 3) * 185, 222 + (i // 3) * 44, 175, 34, s, (),
                 fill="#f0fdfa", stroke="#99f6e4", tfill=C["teal"], tsize=9)
    L += box(750, 332, 280, 60, "long_encoding_ref_model.sv",
             ("encode_413b_to_420b · G16(X)", "70-bit 对齐 · K 常量"),
             fill="#faf5ff", stroke="#e9d5ff", tsize=9.5, ssize=8.5)
    L += box(1050, 332, 280, 60, "isptx_transaction.sv（420b）",
             ("bit[19:0] one_pkt_20b", "bit[39:0] k1_420b ~ k4_420b"),
             fill="#f0fdf4", stroke="#bbf7d0", tsize=10, ssize=8.5)
    L += box(750, 408, 580, 56, "isptx_driver.sv（420b）",
             ("drv_one_pkt_20b() / drv_kx_key_420b() · LSB-first → vif.rxn0/rxp0",),
             tsize=11.5, ssize=9.5)
    L += box(750, 480, 580, 78, "DUT：420b RX（HDL long_encoding）",
             ("KCODE_ALIGN_LONG → long_decoding_top → decoder_7b → descramble_7b",
              "输出：24-bit + 2-bit valid"), fill="#fef2f2", stroke="#fecaca",
             tfill="#991b1b", sfill="#991b1b", tsize=11, ssize=9.5)
    L += box(750, 574, 580, 64, "线上数据验证（0717 新增）",
             ("bind tap DATA_ALIGN_PRE → decode_dap.py 离线 413b/420b 解码 → 逐区域 diff（不看 RTL 解码器）",),
             fill="#f0fdf4", stroke="#86efac", tfill="#047857", sfill="#047857",
             tsize=10.5, ssize=9)

    # ---- 列内箭头 ----
    for x in (360, 1040):
        A(arrow(x, 174, x, 190, "blue"))
        A(arrow(x, 316, x, 332, "blue"))
        A(arrow(x, 392, x, 408, "blue"))
        A(arrow(x, 464, x, 480, "blue"))
        A(arrow(x, 558, x, 574, "blue"))

    # ---- 差异对照表 ----
    L += container(40, 690, 1320, 484, "关键差异对照", C["dark"])
    x0, c1, c2, c3 = 60, 210, 470, 580
    y0, hh, rh = 726, 36, 32
    A(rect(x0, y0, c1, hh, "#e2e8f0", "#cbd5e1", 4, 1))
    A(rect(x0 + c1, y0, c2, hh, "#e2e8f0", "#cbd5e1", 4, 1))
    A(rect(x0 + c1 + c2, y0, c3, hh, "#e2e8f0", "#cbd5e1", 4, 1))
    A(text(x0 + c1 / 2, y0 + 23, "项目", 12.5, C["dark"], "600"))
    A(text(x0 + c1 + c2 / 2, y0 + 23, "8B/10B 模式", 12.5, C["dark"], "600"))
    A(text(x0 + c1 + c2 + c3 / 2, y0 + 23, "420B 长编码模式", 12.5, "#6b21a8", "600"))
    rows = [
        ("模式开关", "无宏", "`define CHPI_MODE_420B"),
        ("输入粒度", "8-bit byte", "8-bit byte → 7-bit group（413b = 59 组）"),
        ("编码", "8B/10B 表 → 10-bit symbol", "413b → 420b tag 替换 + 70-bit 对齐"),
        ("K-code 宽度", "10-bit K1~K4", "40-bit K1~K4"),
        ("IDLE", "无独立 IDLE", "10-bit K5~K8"),
        ("加扰 LFSR", "24-bit G24(X)", "16-bit G16(X)（7-bit / 步）"),
        ("LSP 训练数据", "训练序列一部分", "直接 413b/420b 编码 · 不加扰"),
        ("发送方向", "LSB-first", "LSB-first（0715 起对齐，曾误为 MSB-first）"),
        ("跨 lane 对齐", "字节对齐", "70-bit dummy 对齐"),
        ("参考模型", "encode_8b10b() 内嵌 sequence", "独立 long_encoding_ref_model.sv"),
        ("DUT 解码", "8B/10B decode", "long_decoding_top / decoder_7b / descramble_7b"),
        ("输出", "8-bit data", "24-bit + 2-bit valid"),
        ("线上数据验证", "C model / checker 对比", "bind tap + decode_dap.py 离线比对（不看 RTL）"),
    ]
    for i, (a, b, c3v) in enumerate(rows):
        ry = y0 + hh + i * rh
        fill = "#ffffff" if i % 2 == 0 else "#f9fafb"
        A(rect(x0, ry, c1, rh, fill, "#cbd5e1", 2, 1))
        A(rect(x0 + c1, ry, c2, rh, fill, "#cbd5e1", 2, 1))
        A(rect(x0 + c1 + c2, ry, c3, rh, fill, "#cbd5e1", 2, 1))
        A(text(x0 + 10, ry + 21, a, 11, C["dark"], "600", "start"))
        A(text(x0 + c1 + 10, ry + 21, b, 11, "#374151", None, "start"))
        A(text(x0 + c1 + c2 + 10, ry + 21, c3v, 11, "#6b21a8", None, "start"))

    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# 通用小件：等宽字体文本 / 段块
# ---------------------------------------------------------------------------
def mtext(x, y, s, size=12, fill=C["dark"], weight=None, anchor="middle"):
    wt = f' font-weight="{weight}"' if weight else ""
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}"{wt} '
            f'font-family="Consolas, Menlo, monospace">{s}</text>')


def seg(x, y, w, h, label, fill, stroke, tfill, tsize=10):
    return box(x, y, w, h, label, (), fill=fill, stroke=stroke, tfill=tfill, tsize=tsize)


# 段块配色
K_FILL, K_STROKE, K_TXT = "#dcfce7", "#86efac", "#166534"      # K1~K4
I_FILL, I_STROKE, I_TXT = "#fef9c3", "#fde047", "#854d0e"      # IDLE K5~K8
D_FILL, D_STROKE, D_TXT = "#dbeafe", "#93c5fd", "#1e40af"      # 数据
CL_FILL, CL_STROKE, CL_TXT = "#cffafe", "#67e8f9", "#155e75"   # CTRL_L
CF_FILL, CF_STROKE, CF_TXT = "#fce7f3", "#f9a8d4", "#9d174d"   # CTRL_F
DM_FILL, DM_STROKE, DM_TXT = "#e5e7eb", "#d1d5db", "#6b7280"   # Dmy
HB_FILL, HB_STROKE, HB_TXT = "#f3f4f6", "#d1d5db", "#6b7280"   # HBP / H blanking


# ---------------------------------------------------------------------------
# D1：413b → 420b 分组标签替换
# ---------------------------------------------------------------------------
def gen_spec_tag():
    L = head(1200, 460)
    A = L.append
    A(text(600, 40, "413b → 420b 分组标签替换", 21, C["dark"], "600"))
    A(text(600, 64, "59 组 × 7-bit · 选取未出现的 6-bit 样式作 tag · 全 0/全 1 组替换为 tag+type · 编码效率 98.33%（413/420）· 最大连 0/连 1 ≤ 12",
           12, C["muted"]))
    # 输入行
    L += box(60, 108, 110, 40, "输入 413b", (), fill="#f8fafc", stroke=C["line"], tsize=12)
    x = 190
    for i, g in enumerate(["1001101", "1110000", "0000000"]):
        hl = (g == "0000000")
        L += seg(x + i * 92, 108, 86, 40, g, "#fee2e2" if hl else "#ffffff",
                 "#fca5a5" if hl else "#d1d5db", "#991b1b" if hl else C["dark"], 11)
    A(text(x + 3 * 92 + 22, 134, "……", 13, C["muted"]))
    L += seg(x + 3 * 92 + 50, 108, 86, 40, "1111111", "#fee2e2", "#fca5a5", "#991b1b", 11)
    L += seg(x + 3 * 92 + 142, 108, 86, 40, "1010010", "#ffffff", "#d1d5db", C["dark"], 11)
    A(text(x + 2 * 92 + 43, 164, "全 0", 9.5, "#dc2626"))
    A(text(x + 3 * 92 + 93, 164, "全 1", 9.5, "#dc2626"))
    A(arrow(442, 172, 442, 204, "blue", 2))
    # 输出行
    L += box(60, 208, 110, 40, "输出 420b", (), fill="#f8fafc", stroke=C["line"], tsize=12)
    outs = [(190, 40, "0/1", "#e9d5ff", "#c4b5fd", "#5b21b6"), (236, 64, "101010", "#fef08a", "#fde047", "#854d0e"),
            (306, 86, "1001101", "#ffffff", "#d1d5db", C["dark"]), (398, 86, "1110000", "#ffffff", "#d1d5db", C["dark"]),
            (490, 64, "101010", "#fef08a", "#fde047", "#854d0e"), (560, 30, "0", "#fecaca", "#fca5a5", "#991b1b")]
    for x0, w0, s0, f0, st0, t0 in outs:
        L += seg(x0, 208, w0, 40, s0, f0, st0, t0, 11)
    A(text(618, 234, "……", 13, C["muted"]))
    L += seg(646, 208, 64, 40, "101010", "#fef08a", "#fde047", "#854d0e", 11)
    L += seg(716, 208, 30, 40, "1", "#fecaca", "#fca5a5", "#991b1b", 11)
    L += seg(752, 208, 86, 40, "1010010", "#ffffff", "#d1d5db", C["dark"], 11)
    A(f'<line x1="655" y1="196" x2="830" y2="196" stroke="{C["blue"]}" stroke-width="1.5" marker-end="url(#ar-blue)"/>')
    A(text(742, 188, "发送顺序 A → B", 9.5, C["blue"]))
    A(text(678, 264, "A", 10, C["blue"], "700"))
    A(text(795, 264, "B", 10, C["blue"], "700"))
    # 图例
    for i, (f0, s0, t0) in enumerate([("#e9d5ff", "#c4b5fd", "1 比特跳变沿（前一数据包尾部取反）"),
                                      ("#fef08a", "#fde047", "6 比特标签（本包未出现的样式）"),
                                      ("#fecaca", "#fca5a5", "1 比特类型指示符（替换的是什么就放什么）")]):
        A(rect(890, 104 + i * 32, 18, 18, f0, s0, 4, 1))
        A(text(916, 118 + i * 32, t0, 11, C["muted"], None, "start"))
    # 四步说明
    steps = [("① 分组", "413b 分成 59 组 × 7-bit；保证每组都不是全 0/全 1，就一定不会出现 13 个连 0/连 1"),
             ("② 选 tag", "记录每组前 6-bit 样式（共 2⁶=64 种），59 组必能找到未出现的样式作标签"),
             ("③ 替换", "全 0/全 1 组用 tag + 1-bit 类型指示符替换；tag 放到头部，解码时检测还原"),
             ("④ 直通", "若每组都不需要替换，头部放 1000000 / 0111111，表示该包不编码")]
    for i, (t0, s0) in enumerate(steps):
        bx = 60 + i * 285
        A(rect(bx, 300, 270, 120, "#f8fafc", C["line"], 10, 1.5))
        A(text(bx + 14, 326, t0, 12, C["teal"], "700", "start"))
        # 手工换行
        lines = {"① 分组": ["413b 分成 59 组 × 7-bit；保证每组都", "不是全 0/全 1，就一定不会出现 13 个", "连 0/连 1"],
                 "② 选 tag": ["记录每组前 6-bit 样式（共 64 种），", "59 组必能找到未出现的样式作标签"],
                 "③ 替换": ["全 0/全 1 组用 tag + 1-bit 类型指示符", "替换；tag 放到头部，解码时检测还原"],
                 "④ 直通": ["若每组都不需要替换，头部放 1000000", "/ 0111111，表示该包不编码"]}[t0]
        for j, ln in enumerate(lines):
            A(text(bx + 14, 350 + j * 18, ln, 10.5, C["muted"], None, "start"))
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D2：数据传输方向（byte → bit 串行，LSB-first）
# ---------------------------------------------------------------------------
def gen_spec_bitorder():
    L = head(1200, 560)
    A = L.append
    A(text(600, 40, "数据传输方向：byte → bit 串行（LSB-first）", 21, C["dark"], "600"))
    A(text(600, 64, "Packet Data 按 byte 依次发送（byte0 → byte1 → byte2 …）；每个 byte 内 Bit0 最先发出",
           12, C["muted"]))
    # 左侧 3×8 网格
    cols = [("R0", "#fce7f3", "#f9a8d4", "#9d174d"), ("G0", "#dcfce7", "#86efac", "#166534"),
            ("B0", "#dbeafe", "#93c5fd", "#1e40af")]
    for ci, (cn, f0, st0, t0) in enumerate(cols):
        for r in range(8):
            bit = 7 - r
            L += seg(110 + ci * 68, 104 + r * 34, 64, 30, f"{cn}[{bit}]", f0, st0, t0, 10)
    A(text(316, 250, "…", 14, C["muted"]))
    A(text(100, 122, "Bit7", 10, C["muted"], None, "end"))
    A(text(100, 360, "Bit0", 10, C["muted"], None, "end"))
    A(f'<text transform="rotate(-90 52 244)" x="52" y="244" font-size="10.5" fill="{C["muted"]}" text-anchor="middle">Packet Data</text>')
    A(path("M 74 356 L 74 122", "blue", 2))
    A(f'<text transform="rotate(-90 88 240)" x="88" y="240" font-size="9.5" fill="{C["blue"]}" text-anchor="middle">发送顺序（Bit0 先发）</text>')
    for i, bn in enumerate(["byte0", "byte1", "byte2"]):
        A(text(142 + i * 68, 404, bn, 9.5, C["muted"]))
        if i < 2:
            A(text(176 + i * 68, 404, ">>", 9.5, C["muted"]))
    A(arrow(230, 420, 230, 446, "blue", 2))
    A(text(240, 436, "串行化", 9.5, C["blue"], None, "start"))
    # 底部串行流
    A(text(60, 470, "Case1 · 413b data（bit 串行流）", 10.5, C["dark"], "600", "start"))
    order = [("R0", "#fce7f3", "#f9a8d4", "#9d174d"), ("B0", "#dbeafe", "#93c5fd", "#1e40af"),
             ("G0", "#dcfce7", "#86efac", "#166534")]
    x = 60
    for cn, f0, st0, t0 in order:
        for b in range(8):
            L += seg(x, 482, 40, 32, f"{cn}[{b}]", f0, st0, t0, 8.5)
            x += 43
    A(text(x + 14, 502, "…", 13, C["muted"]))
    A(f'<line x1="60" y1="540" x2="1140" y2="540" stroke="{C["blue"]}" stroke-width="1.5" marker-end="url(#ar-blue)"/>')
    A(text(1140, 532, "传输时间轴方向", 10, C["blue"], None, "end"))
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D3：Scramble key 滚动机制
# ---------------------------------------------------------------------------
def gen_spec_scramble():
    L = head(1200, 520)
    A = L.append
    A(text(600, 40, "Scramble key 滚动机制", 21, C["dark"], "600"))
    A(text(600, 64, "K 码不加扰，K 码期间 scramble 停止滚动；第 n+1 行 scramble 起始状态顺承第 n 行截止状态",
           12, C["muted"]))
    # 编码前
    A(text(50, 138, "编码前", 10.5, C["muted"], None, "end"))
    L += seg(60, 112, 56, 40, "K1", K_FILL, K_STROKE, K_TXT)
    L += seg(120, 112, 90, 40, "CTR_L", CL_FILL, CL_STROKE, CL_TXT)
    L += seg(214, 112, 416, 40, "RGB Data", D_FILL, D_STROKE, D_TXT, 11)
    L += seg(634, 112, 56, 40, "K2", K_FILL, K_STROKE, K_TXT)
    L += seg(694, 112, 300, 40, "HBP", HB_FILL, HB_STROKE, HB_TXT, 11)
    A(arrow(470, 158, 470, 204, "blue", 2))
    A(text(480, 186, "编码后", 10, C["blue"], None, "start"))
    # 编码后
    A(text(50, 236, "编码后", 10.5, C["muted"], None, "end"))
    L += seg(60, 210, 56, 40, "K1", K_FILL, K_STROKE, K_TXT)
    L += seg(120, 210, 90, 40, "CTR_L", CL_FILL, CL_STROKE, CL_TXT)
    L += seg(214, 210, 356, 40, "Enc Data", D_FILL, D_STROKE, D_TXT, 11)
    L += seg(574, 210, 86, 40, "Dmy", DM_FILL, DM_STROKE, DM_TXT)
    L += seg(664, 210, 56, 40, "K2", K_FILL, K_STROKE, K_TXT)
    for i, kn in enumerate(["K5", "K6", "K7", "K8"]):
        L += seg(724 + i * 44, 210, 40, 40, kn, I_FILL, I_STROKE, I_TXT)
    A(text(910, 236, "…", 13, C["muted"]))
    L += seg(936, 210, 40, 40, "K5", I_FILL, I_STROKE, I_TXT)
    # 时间轴条
    A(rect(120, 282, 540, 10, "#16a34a", "#16a34a", 5, 1))
    A(rect(120, 304, 540, 10, "#ea580c", "#ea580c", 5, 1))
    A(rect(214, 326, 356, 10, "#2563eb", "#2563eb", 5, 1))
    A(text(120, 274, "加扰区间（CTR_L ~ Dmy）", 9.5, "#16a34a", None, "start"))
    A(text(730, 282, "K 码期间 scramble 停止滚动", 9.5, "#9ca3af", None, "start"))
    for i, (c0, n0) in enumerate([("#16a34a", "SCR_KEY update"), ("#ea580c", "SCR_XOR"), ("#2563eb", "413/420 ENC")]):
        A(rect(1010, 282 + i * 22, 14, 10, c0, c0, 3, 1))
        A(text(1030, 291 + i * 22, n0, 10, C["muted"], None, "start"))
    # 顺承箭头 + n+1 行
    A(path("M 660 292 C 700 320 660 360 620 372 L 220 372 L 220 388", "green", 2, "6,3"))
    A(text(560, 364, "n 行截止状态 → n+1 行起始状态（LFSR 连续）", 10, "#16a34a"))
    A(text(50, 414, "n+1 行", 10.5, C["muted"], None, "end"))
    L += seg(60, 390, 56, 40, "K1", K_FILL, K_STROKE, K_TXT)
    L += seg(120, 390, 90, 40, "CTR_L", CL_FILL, CL_STROKE, CL_TXT)
    L += seg(214, 390, 300, 40, "Enc Data", D_FILL, D_STROKE, D_TXT, 11)
    A(text(524, 414, "…", 13, C["muted"]))
    A(rect(120, 444, 394, 8, "#16a34a", "#16a34a", 4, 1))
    A(text(524, 452, "scramble 继续滚动", 9.5, "#16a34a", None, "start"))
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D4：非 413b 整数倍数据处理（Dmy → 加扰 → 编码 → 70b 对齐）
# ---------------------------------------------------------------------------
def gen_spec_dummy70b():
    L = head(1200, 600)
    A = L.append
    A(text(600, 40, "非 413b 整数倍数据处理", 21, C["dark"], "600"))
    A(text(600, 64, "编码后去掉补齐的 dummy，但发送数据长度须为 70b 整数倍；通道数不同时按最大 70-bit 整数倍填充",
           12, C["muted"]))
    # 顶部流程
    steps = ["① 补 Dmy(0) 至 413b 整数倍", "② 加扰（SCR EN=1）", "③ 413b/420b 编码", "④ 去 dummy · 70b 对齐发送"]
    for i, s0 in enumerate(steps):
        L += box(60 + i * 290, 84, 250, 44, s0, (), fill="#f0fdfa", stroke="#99f6e4",
                 tfill=C["teal"], tsize=11.5)
        if i < 3:
            A(arrow(314 + i * 290, 106, 344 + i * 290, 106, "blue"))
    rows = [
        ("LSP", K_FILL, K_STROKE, K_TXT,
         [("K2", 56, K_FILL, K_STROKE, K_TXT), ("0xEA/EB/EC/ED ×8（32 Byte）", 280, "#ffffff", "#d1d5db", C["dark"]), ("K3", 56, K_FILL, K_STROKE, K_TXT)],
         [("K2", 56, K_FILL, K_STROKE, K_TXT), ("LSP(ENC) · 280b", 340, D_FILL, D_STROKE, D_TXT), ("K3", 56, K_FILL, K_STROKE, K_TXT)],
         "训练数据不加扰"),
        ("Active Line", D_FILL, D_STROKE, D_TXT,
         [("K1", 50, K_FILL, K_STROKE, K_TXT), ("CL", 50, CL_FILL, CL_STROKE, CL_TXT), ("RGB（CL+RGB）", 176, D_FILL, D_STROKE, D_TXT), ("K2", 50, K_FILL, K_STROKE, K_TXT), ("HBP", 56, HB_FILL, HB_STROKE, HB_TXT)],
         [("K1", 44, K_FILL, K_STROKE, K_TXT), ("CL", 44, CL_FILL, CL_STROKE, CL_TXT), ("RGB(ENC) · 420b×N", 170, D_FILL, D_STROKE, D_TXT), ("D · 70b×N", 80, DM_FILL, DM_STROKE, DM_TXT), ("K2", 44, K_FILL, K_STROKE, K_TXT), ("K5~K8", 56, I_FILL, I_STROKE, I_TXT)],
         "像素 / VBK payload 加扰"),
        ("Config Line", CF_FILL, CF_STROKE, CF_TXT,
         [("K4", 50, K_FILL, K_STROKE, K_TXT), ("C.F（6x Byte）", 180, CF_FILL, CF_STROKE, CF_TXT), ("K2", 50, K_FILL, K_STROKE, K_TXT), ("HBP", 100, HB_FILL, HB_STROKE, HB_TXT)],
         [("K4", 44, K_FILL, K_STROKE, K_TXT), ("C.F(ENC) · 420b", 190, CF_FILL, CF_STROKE, CF_TXT), ("D · 140b", 90, DM_FILL, DM_STROKE, DM_TXT), ("K2", 44, K_FILL, K_STROKE, K_TXT), ("K5~K8", 56, I_FILL, I_STROKE, I_TXT)],
         "Dmy 内嵌于 413b 零补齐"),
    ]
    for ri, (label, lf, ls, lt, before, after, note) in enumerate(rows):
        y = 170 + ri * 120
        L += box(60, y + 22, 120, 44, label, (), fill=lf, stroke=ls, tfill=lt, tsize=11)
        A(rect(200, y, 420, 100, "#fff7ed", "#fdba74", 10, 1.5))
        A(text(214, y + 22, "Before ENC", 10, "#9a3412", "600", "start"))
        x = 214
        for s0, w0, f0, st0, t0 in before:
            L += seg(x, y + 34, w0, 38, s0, f0, st0, t0, 9.5)
            x += w0 + 4
        A(rect(700, y, 490, 100, "#fff7ed", "#fdba74", 10, 1.5))
        A(text(714, y + 22, "After ENC", 10, "#9a3412", "600", "start"))
        x = 714
        for s0, w0, f0, st0, t0 in after:
            L += seg(x, y + 34, w0, 38, s0, f0, st0, t0, 9.5)
            x += w0 + 4
        A(arrow(630, y + 50, 690, y + 50, "blue", 2))
        A(text(660, y + 88, "413b/420b", 8.5, C["blue"]))
        A(text(410, y + 88, note, 9, C["muted"]))
    A(text(60, 552, "多通道对齐示例：720 通道 Dmy = N bit、726 通道 Dmy = N+70 bit → 统一按 N+70 bit 填充",
           11, C["muted"], None, "start"))
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D5：420b 帧数据流
# ---------------------------------------------------------------------------
def gen_spec_frameflow():
    L = head(1200, 700)
    A = L.append
    A(text(600, 40, "420b 帧数据流", 21, C["dark"], "600"))
    A(text(600, 64, "LSP 训练 → Active Lines（Video） → Config Line 单独成行（下一帧配置） → V blanking",
           12, C["muted"]))
    X0, W = 210, 800
    cols = [(X0, 90), (X0 + 90, 150), (X0 + 240, 300), (X0 + 540, 120), (X0 + 660, 134)]
    y = 100

    def full_row(yy, label, fill, stroke, tfill):
        L_ = [rect(X0, yy, W, 40, fill, stroke, 6, 1.5), text(X0 + W / 2, yy + 26, label, 11.5, tfill, "600")]
        return L_

    def seg_row(yy, cells):
        L_ = []
        for (cx, cw), (s0, f0, st0, t0) in zip(cols, cells):
            if s0:
                L_ += seg(cx, yy, cw - 6, 40, s0, f0, st0, t0, 10)
        return L_

    L += full_row(y, "Clock training pattern", "#f3f4f6", "#d1d5db", "#374151"); y += 46
    L += full_row(y, "LSP（K2 + 0xEA~ED×8 + Dmy + K3）× ≥5 次 · ≥1us", "#ccfbf1", "#5eead4", "#0f766e"); y += 46
    L += seg_row(y, [("K4", K_FILL, K_STROKE, K_TXT), ("CTRL_F", CF_FILL, CF_STROKE, CF_TXT),
                     ("Dmy", DM_FILL, DM_STROKE, DM_TXT), ("K2", K_FILL, K_STROKE, K_TXT),
                     ("H blanking", HB_FILL, HB_STROKE, HB_TXT)])
    A(text(X0 + W + 10, y + 25, "Config Line（Frame c 配置）", 9.5, C["muted"], None, "start")); y += 46
    # Video Active 行
    active_top = y
    for i, ln in enumerate(["Video data-line1 + Dmy", "Video data-line2 + Dmy", "……", "Video data-last line + Dmy"]):
        if ln == "……":
            A(text(X0 + W / 2, y + 26, "……", 13, C["muted"])); y += 34
            continue
        L += seg_row(y, [("K1", K_FILL, K_STROKE, K_TXT), ("CTRL_L", CL_FILL, CL_STROKE, CL_TXT),
                         (ln, D_FILL, D_STROKE, D_TXT), ("K2 or K3", K_FILL, K_STROKE, K_TXT),
                         ("H blanking", HB_FILL, HB_STROKE, HB_TXT)])
        y += 46
    # Active 括号
    A(f'<path d="M {X0-16} {active_top+4} q -10 0 -10 10 l 0 {(y-active_top-14)//2-8} q 0 8 -8 8 q 8 0 8 8 l 0 {(y-active_top-14)//2-8} q 0 10 10 10" stroke="{C["teal"]}" stroke-width="2" fill="none"/>')
    A(f'<text transform="rotate(-90 {X0-40} {(active_top+y)//2})" x="{X0-40}" y="{(active_top+y)//2}" font-size="11" fill="{C["teal"]}" text-anchor="middle" font-weight="600">Video Active</text>')
    y += 8
    # Config Line 单独成行（高亮）
    A(rect(X0 - 8, y - 6, W + 16, 52, "#ecfdf5", "#34d399", 8, 2))
    L += seg_row(y, [("K4", K_FILL, K_STROKE, K_TXT), ("CTRL_F", CF_FILL, CF_STROKE, CF_TXT),
                     ("Dmy", DM_FILL, DM_STROKE, DM_TXT), ("K2", K_FILL, K_STROKE, K_TXT),
                     ("H blanking", HB_FILL, HB_STROKE, HB_TXT)])
    A(text(X0 + W + 10, y + 18, "Config Line · Frame c+1 配置", 9.5, "#047857", "600", "start"))
    A(text(X0 + W + 10, y + 34, "0717v1：单独成行", 9.5, "#047857", None, "start"))
    y += 58
    vbk_top = y
    for i in range(2):
        L += seg_row(y, [("K1", K_FILL, K_STROKE, K_TXT), ("CTRL_L", CL_FILL, CL_STROKE, CL_TXT),
                         ("VBK dummy line", D_FILL, D_STROKE, D_TXT), ("K2", K_FILL, K_STROKE, K_TXT),
                         ("H blanking", HB_FILL, HB_STROKE, HB_TXT)])
        y += 46
    A(text(X0 + W / 2, y + 24, "……", 13, C["muted"]))
    A(f'<path d="M {X0-16} {vbk_top+4} q -10 0 -10 10 l 0 {y-vbk_top-30} q 0 10 10 10" stroke="{C["muted"]}" stroke-width="2" fill="none"/>')
    A(f'<text transform="rotate(-90 {X0-40} {(vbk_top+y)//2})" x="{X0-40}" y="{(vbk_top+y)//2}" font-size="11" fill="{C["muted"]}" text-anchor="middle" font-weight="600">V blanking</text>')
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D6：LSP 序列与 K 码（K1~K4）
# ---------------------------------------------------------------------------
def gen_spec_lsp_kcode():
    L = head(1200, 620)
    A = L.append
    A(text(600, 40, "LSP 序列与 K 码（K1 ~ K4）", 21, C["dark"], "600"))
    A(text(600, 64, "LSP：K3 放在序列最后；至少发送 5 次，连续发送 ≥ 1us · K 码 40-bit · 不加扰",
           12, C["muted"]))
    # LSP 编码前
    A(text(52, 140, "编码前", 10, C["muted"], None, "end"))
    x = 60
    L += seg(x, 114, 56, 38, "K2", K_FILL, K_STROKE, K_TXT, 11); x += 60
    for i in range(8):
        L += seg(x, 114, 46, 38, f"0x{['EA','EB','EC','ED'][i%4]}", "#ffedd5", "#fdba74", "#9a3412", 9.5)
        x += 50
    A(text(x + 16, 140, "…", 13, C["muted"])); x += 36
    for i in range(4):
        L += seg(x, 114, 46, 38, f"0x{['EA','EB','EC','ED'][i]}", "#ffedd5", "#fdba74", "#9a3412", 9.5)
        x += 50
    L += seg(x + 4, 114, 56, 38, "K3", K_FILL, K_STROKE, K_TXT, 11)
    A(f'<path d="M 120 158 L 120 166 L {120+400} 166 L {120+400} 158" stroke="{C["muted"]}" stroke-width="1" fill="none"/>')
    A(text(320, 180, "0xEA/EB/EC/ED × 8 = 32 Byte", 9.5, C["muted"]))
    # LSP 编码后
    A(text(52, 236, "编码后", 10, C["muted"], None, "end"))
    x = 60
    L += seg(x, 210, 56, 38, "K2", K_FILL, K_STROKE, K_TXT, 11); x += 60
    for i in range(8):
        L += seg(x, 210, 46, 38, f"0x{['EA','EB','EC','ED'][i%4]}", "#ffedd5", "#fdba74", "#9a3412", 9.5)
        x += 50
    A(text(x + 16, 236, "…", 13, C["muted"])); x += 36
    for i in range(4):
        L += seg(x, 210, 46, 38, f"0x{['EA','EB','EC','ED'][i]}", "#ffedd5", "#fdba74", "#9a3412", 9.5)
        x += 50
    L += seg(x + 4, 210, 70, 38, "dmy", DM_FILL, DM_STROKE, DM_TXT, 10)
    L += seg(x + 78, 210, 56, 38, "K3", K_FILL, K_STROKE, K_TXT, 11)
    A(text(x + 41, 272, "编码后末尾补 dmy → 280b（70×4）", 9.5, C["muted"]))
    # K 码表
    A(text(60, 330, "K 码（K1 ~ K4）· 40-bit · 不加扰", 13, C["dark"], "600", "start"))
    kcodes = [("K1", "11 0000000000 11110000 1111111111 0011111100"),
              ("K2", "00 1111111111 00001100 1111111111 0011001100"),
              ("K3", "11 0000000000 11000011 0000000000 1100000011"),
              ("K4", "00 1111111111 00110011 0000000000 1111000000")]
    for i, (kn, bits) in enumerate(kcodes):
        ry = 350 + i * 46
        A(rect(60, ry, 70, 40, K_FILL, K_STROKE, 6, 1.5))
        A(text(95, ry + 26, kn, 12, K_TXT, "700"))
        A(rect(134, ry, 860, 40, "#ffffff" if i % 2 == 0 else "#f9fafb", "#d1d5db", 6, 1.5))
        A(mtext(564, ry + 26, bits, 14, C["dark"]))
    # 先发 / 后发
    ay = 350 + 4 * 46 + 8
    A(f'<line x1="950" y1="{ay}" x2="950" y2="{ay-14}" stroke="{C["blue"]}" stroke-width="1.5" marker-end="url(#ar-blue)"/>')
    A(text(950, ay + 18, "先发", 11, C["blue"], "700"))
    A(f'<line x1="178" y1="{ay}" x2="178" y2="{ay-14}" stroke="{C["blue"]}" stroke-width="1.5" marker-end="url(#ar-blue)"/>')
    A(text(178, ay + 18, "后发", 11, C["blue"], "700"))
    A(text(564, ay + 18, "串行发送方向：右 → 左（LSB-first，与 8B/10B 一致）", 10.5, C["blue"]))
    A('</svg>')
    return "\n".join(L)


# ---------------------------------------------------------------------------
# D7：H/V blanking 与 IDLE（K5~K8）+ Config Line 单独成行
# ---------------------------------------------------------------------------
def gen_spec_blanking():
    L = head(1200, 660)
    A = L.append
    A(text(600, 40, "H/V blanking 与 IDLE（K5 ~ K8）", 21, C["dark"], "600"))
    A(text(600, 64, "H blanking 采用固定 pattern K5/K6/K7/K8 替代；为优化 EMI，不同 lane 采用不同发送顺序",
           12, C["muted"]))
    # 左：K5~K8 码值表
    A(text(60, 106, "IDLE pattern · 10-bit · 不加扰", 12, C["dark"], "600", "start"))
    idles = [("K5", "1100110011"), ("K6", "0011001100"), ("K7", "1111000011"), ("K8", "0000111100")]
    for i, (kn, bits) in enumerate(idles):
        ry = 120 + i * 42
        A(rect(60, ry, 60, 36, I_FILL, I_STROKE, 6, 1.5))
        A(text(90, ry + 24, kn, 11.5, I_TXT, "700"))
        A(rect(124, ry, 200, 36, "#ffffff" if i % 2 == 0 else "#f9fafb", "#d1d5db", 6, 1.5))
        A(mtext(224, ry + 24, bits, 13, C["dark"]))
    # 右：lane 轮换
    A(text(420, 106, "lane 间轮换（EMI 优化）", 12, C["dark"], "600", "start"))
    lanes = [["K5", "K6", "K7", "K8"], ["K6", "K7", "K8", "K5"],
             ["K7", "K8", "K5", "K6"], ["K8", "K5", "K6", "K7"]]
    for i, seq in enumerate(lanes):
        ry = 120 + i * 42
        A(text(420, ry + 24, f"Lane{i+1}", 11, C["dark"], "600", "start"))
        for j, kn in enumerate(seq):
            L += seg(490 + j * 58, ry, 40, 30, kn, I_FILL, I_STROKE, I_TXT, 10)
            if j < 3:
                A(text(539 + j * 58, ry + 20, "→", 10, C["muted"]))
    # V blanking 行
    A(text(60, 330, "V blanking 行结构（VBK dummy line 内容可配置）", 12, C["dark"], "600", "start"))
    L += seg(60, 348, 56, 40, "K1", K_FILL, K_STROKE, K_TXT, 11)
    L += seg(120, 348, 110, 40, "CTRL_L", CL_FILL, CL_STROKE, CL_TXT, 11)
    L += seg(234, 348, 380, 40, "VBK dummy line", D_FILL, D_STROKE, D_TXT, 11)
    L += seg(618, 348, 56, 40, "K2", K_FILL, K_STROKE, K_TXT, 11)
    L += seg(678, 348, 200, 40, "H-IDLE", HB_FILL, HB_STROKE, HB_TXT, 11)
    # Config Line 单独成行
    A(text(60, 436, "Config Line 单独成行：K4 + CTRL_F + Dmy + K2（VACT 结束后单独发送一行）", 12, C["dark"], "600", "start"))
    A(text(52, 482, "末行", 9.5, C["muted"], None, "end"))
    L += seg(60, 456, 56, 38, "K1", K_FILL, K_STROKE, K_TXT, 10)
    L += seg(120, 456, 90, 38, "CTR_L", CL_FILL, CL_STROKE, CL_TXT, 10)
    L += seg(214, 456, 320, 38, "Enc Data", D_FILL, D_STROKE, D_TXT, 10.5)
    L += seg(538, 456, 90, 38, "Dmy", DM_FILL, DM_STROKE, DM_TXT, 10)
    L += seg(632, 456, 56, 38, "K2", K_FILL, K_STROKE, K_TXT, 10)
    for i, kn in enumerate(["K5", "K6", "K7", "K8"]):
        L += seg(692 + i * 44, 456, 40, 38, kn, I_FILL, I_STROKE, I_TXT, 10)
    A(text(874, 480, "…", 13, C["muted"]))
    L += seg(898, 456, 40, 38, "K5", I_FILL, I_STROKE, I_TXT, 10)
    A(text(52, 540, "VBP 首行", 9.5, C["muted"], None, "end"))
    L += seg(60, 514, 56, 38, "K4", K_FILL, K_STROKE, K_TXT, 10)
    L += seg(120, 514, 180, 38, "CTR_F", CF_FILL, CF_STROKE, CF_TXT, 10)
    L += seg(304, 514, 90, 38, "Dmy", DM_FILL, DM_STROKE, DM_TXT, 10)
    L += seg(398, 514, 56, 38, "K2", K_FILL, K_STROKE, K_TXT, 10)
    for i, kn in enumerate(["K5", "K6", "K7", "K8"]):
        L += seg(458 + i * 44, 514, 40, 38, kn, I_FILL, I_STROKE, I_TXT, 10)
    A(text(644, 538, "…", 13, C["muted"]))
    L += seg(668, 514, 40, 38, "K5", I_FILL, I_STROKE, I_TXT, 10)
    A(text(60, 600, "注：Active Line（含最后一行）统一以 K2 结束，不再嵌入 K4+CTRL_F；Config Line 于 VACT 结束后单独发送。",
           10.5, C["muted"], None, "start"))
    A('</svg>')
    return "\n".join(L)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, gen in [
        ("longcode_verification_architecture.svg", gen_architecture),
        ("pydec_tx_rx_structure.svg", gen_pydec),
        ("8b10b_vs_420b_architecture.svg", gen_compare),
        ("spec_tag_replacement.svg", gen_spec_tag),
        ("spec_bit_order.svg", gen_spec_bitorder),
        ("spec_scramble_rolling.svg", gen_spec_scramble),
        ("spec_dummy_70b.svg", gen_spec_dummy70b),
        ("spec_frame_flow.svg", gen_spec_frameflow),
        ("spec_lsp_kcode.svg", gen_spec_lsp_kcode),
        ("spec_blanking_idle.svg", gen_spec_blanking),
    ]:
        p = os.path.join(OUT, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(gen())
        print("written:", p)
