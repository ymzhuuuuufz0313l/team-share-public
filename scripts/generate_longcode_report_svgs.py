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
    L += box(70, 112, 250, 48, "t_H3840_V16_FPS120_420b", ("当前主调 case（bind tap + pydec）",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11)
    L += box(340, 112, 200, 48, "t_8b1lane_420b_basic", ("smoke case",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11)
    L += box(560, 112, 200, 48, "user_def.sv", ("`define CHPI_MODE_420B",),
             fill="#fff7ed", stroke="#fed7aa", tfill="#9a3412", sfill="#9a3412", tsize=11.5)
    L += box(780, 112, 350, 48, "env_cfg", ("SCREN · HACT · VACT · LANE_NUM · get_ctrlL/F_reg",),
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
    L += box(64, 124, 332, 60, "isptx_sequence.sv",
             ("组帧：LSP / CTRL_F / Active / VBK / IDLE", "K1~K4 40-bit · K5~K8 10-bit"), tsize=11.5, ssize=9)
    L += box(64, 204, 332, 60, "long_encoding_ref_model.sv",
             ("413b → 420b 编码 · tag 替换", "G16(X) 加扰（scramble_en = SCREN）"), tsize=11, ssize=9)
    L += box(64, 284, 332, 60, "isptx_driver.sv",
             ("20-bit 包 / 40-bit K 码 · LSB-first", "→ vif.rxn0 / rxp0"), tsize=11.5, ssize=9)
    L += box(64, 364, 332, 60, "dump_raw_bytes() → long_rawbyte_seq_lane0.md",
             ("编码前 raw byte 转储（期望值）",), fill="#faf5ff", stroke="#e9d5ff",
             tfill=C["purple"], tsize=9.5, ssize=9)

    # ---- 串行链路（差分对）----
    A(path("M 396 292 L 452 292 L 452 150 L 524 150", "blue", 2))
    A(path("M 396 304 L 468 304 L 468 162 L 524 162", "blue", 2))
    A(f'<text transform="rotate(-90 438 227)" x="438" y="227" font-size="9.5" fill="{C["blue"]}" text-anchor="middle">CHPI 串行链路（rxp / rxn）</text>')

    # ---- 接收端 RX ----
    L += container(500, 100, 660, 340, "接收端 RX（DUT + 脚本）", "#991b1b")
    A(rect(524, 124, 300, 64, "#ffffff", C["green"], 8, 2))
    A(text(674, 146, "CHPI_KCODE_ALIGN_LONG", 11, C["dark"], "600"))
    A(text(674, 162, "K1~K4 检测 · 20-bit 对齐", 9, C["muted"]))
    A(text(674, 178, "DATA_ALIGN_PRE → tap", 9.5, C["green"], "600"))
    A(rect(784, 130, 34, 16, C["green"], C["green"], 8, 1))
    A(text(801, 142, "TAP", 9, "#ffffff", "700"))
    # 不看的 RTL 段
    A(rect(524, 214, 300, 120, "#f9fafb", "#9ca3af", 8, 1.5, "6,3"))
    A(text(674, 238, "RTL 解码链（不看 · 不依赖）", 11, "#6b7280", "600"))
    A(text(674, 256, "long_decoding_top · decoder_7b", 9, "#6b7280"))
    A(text(674, 272, "descramble_7b → dout_24b + 2-bit valid", 9, "#6b7280"))
    A(text(674, 296, "排障焦点在 RTL 解码链（3.6 节）", 9, "#9ca3af"))
    A(text(674, 312, "但验证线上数据不依赖它", 9, "#9ca3af"))
    # 脚本链
    L += box(870, 124, 266, 64, "long_rtl_tap_debug.sv",
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
    A(arrow(230, 184, 230, 204, "blue"))
    A(arrow(230, 264, 230, 284, "blue"))
    A(arrow(674, 188, 674, 214, "gray", 1.5, "5,3"))
    A(text(700, 206, "传统路径", 9, "#9ca3af", None, "start"))
    A(arrow(824, 156, 870, 156, "green", 2))
    A(arrow(1003, 188, 1003, 212, "green", 2))
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


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for name, gen in [
        ("longcode_verification_architecture.svg", gen_architecture),
        ("pydec_tx_rx_structure.svg", gen_pydec),
        ("8b10b_vs_420b_architecture.svg", gen_compare),
    ]:
        p = os.path.join(OUT, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(gen())
        print("written:", p)
