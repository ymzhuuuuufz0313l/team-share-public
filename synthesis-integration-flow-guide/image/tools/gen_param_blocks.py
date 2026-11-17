# -*- coding: utf-8 -*-
# gen_param_blocks.py — 页面里的「业务参数段落」统一由数据源渲染（t20 · R1/R2/R4/R5）
#
# 管的三件事（全部读 data/*.json，页面不再手写数字）：
#   R2 SVT 规模：environment.html §3.1 段、pt-intro.html §9.6 图注   ← data/svt_summary.json（由 gen_svt_summary.py 解析库内 rpt 生成）
#   R4 时钟周期/工艺参数：pt-intro.html §3.3 三处、script-dict.html 结论行、图注、metric 卡片
#                                                              ← data/clk_params.json（clk_period.tcl 摘录）
#   R1/R5 功耗正文行：memory-power.html 六组 0812 行 ← data/power_0812.json + data/descramble_power.json
#                     powerpro.html §3/§4.1 的 0826/0720 bullet ← data/powerpro_0826.json
#
# 用法（站点根目录）：
#   python image/tools/gen_param_blocks.py            # 就地重渲染（幂等，渲染文本零变化）
#   python image/tools/gen_param_blocks.py --check    # 只校验：任一区块与数据源漂移即 exit 1
import io
import json
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
DATA = os.path.join(BASE, "data")


def load(name):
    with io.open(os.path.join(DATA, name), encoding="utf-8") as fh:
        return json.load(fh)


SVT = load("svt_summary.json")
CLK = load("clk_params.json")
P0812 = load("power_0812.json")
PP0826 = load("powerpro_0826.json")
DESC = load("descramble_power.json")

SVT_SRC = "%s:%d/: %d"  # 帮助阅读：出处写法
A = CLK["active"]
S = CLK["spec"]
M = CLK["margin"]
U = CLK["uncertainty"]
OPTS = " / ".join(CLK["options_ns"])


# ---------------------------------------------------------------- 渲染函数
def env_svt():
    """environment.html §3.1：SVT 规模段（出处行号可见标注，R2 要求）。"""
    return ("**当前状态（HV2M23，已换 SVT）**：本项目已从 **LVT 换到 SVT**（标准阈值库）。综合报告 "
            "`report_vt_cell_usage` 输出 **`SVT 100%%`**（cell 数 %d、面积 %s 全部 100%% SVT），证明换库成功。"
            "（数值出处：`%s` 第 %d 行 `Leaf Cell Count`、第 %d 行 `Total cell area`）"
            % (SVT["leaf_cell_count"], SVT["area_display"], SVT["source_file"],
               SVT["leaf_cell_line"], SVT["area_line"]))


def pt_svt_caption():
    """pt-intro.html §9.6：SVT 图注。"""
    return ("![综合报告 Threshold Voltage Group Report：SVT 100%%（cell 数 %d、面积 %s；出处 `%s`:%d/%d）]"
            "(./image/27_svt_100.png)"
            % (SVT["leaf_cell_count"], SVT["area_display"], SVT["source_file"],
               SVT["leaf_cell_line"], SVT["area_line"]))


def upf_dc_qor_line():
    """synthesis-upf.html §DC QoR：Total cell area 与 svt_summary 同源（R3）。"""
    return ("HV2M23 实测结果（接近 TO 版本）：QoR 各 timing path group slack ≥ 0、violating paths = 0、"
            "hold violation = 0；Design Rules 共 **8663 nets**，仅少量 max_trans / max_cap 违规（留给 APR 阶段修）；"
            "Total cell area **%d**（宏/黑盒 0）。" % int(round(SVT["total_cell_area_um2"])))


def clk_active_bullet():
    return ("- **当前生效（HV2M23，接近 TO，1P 模式）**：`set_case_analysis 0 [get_ports %s]` + "
            "`RX0_CLKP = %sns`（%s SPEC：`%s×%s/%s = %s ≈ %sns`）/ `RX1_CLKP = %sns`（%s：`%s×%s/%s = %s ≈ %sns`）。"
            "一组可选周期：`%s ns`（%s）。"
            % (A["dpsel_port"], A["rx0_ns"], S["rx0_g"], S["rx0_g"], S["spread"], S["divisor"],
               S["rx0_div_mhz"], A["rx0_ns"], A["rx1_ns"], S["rx1_g"], S["rx1_g"], S["spread"],
               S["divisor"], S["rx1_div_mhz"], A["rx1_ns"], OPTS, CLK["options_note"]))


def clk_spread_bullet():
    return ("- 展频（spread spectrum）：**×%s**（5%%），体现在注释换算 `%s*%s/%s = 105M = %sns`、"
            "`%s*%s/%s = %sns`。"
            % (S["spread"], S["slow_clock_g"], S["spread"], S["divisor"], CLK["options_ns"][0],
               S["rx0_g"], S["spread"], S["divisor"], A["rx0_ns"]))


def clk_slow_bullet():
    return ("- 另有一条慢 clock（教学示例，端口名 `CLKA_L`）周期约 %s ns（会议经验值；包内最接近的慢时钟是 "
            "RX1_CLK 备选 %sns，当前注释保留）。" % (CLK["slow_clock_sample_ns"], A["rx1_ns"]))


def clk_caption():
    return ("![clk_period.tcl：MARGIN %s/%s、DPSEL_I=%s（%s）、RX0 %sns / RX1 %sns、展频 %s 注释]"
            "(./image/26_clk_period.png)"
            % (M["syn"], M["pt"], A["dpsel_value"], A["mode"], A["rx0_ns"], A["rx1_ns"], S["spread"]))


def clk_metric_cards():
    return [
        '<div class="metric-grid">',
        '  <div class="metric-card">',
        '    <div class="metric-value">%s ns</div>' % A["rx0_ns"],
        '    <div class="metric-label">RX0 时钟周期（当前生效，1P）</div>',
        '    <div class="metric-note">clk_period.tcl 实际值；%s SPEC（RX1 = %sns）</div>' % (S["rx0_g"], A["rx1_ns"]),
        '  </div>',
        '  <div class="metric-card">',
        '    <div class="metric-value">×%s</div>' % S["spread"],
        '    <div class="metric-label">展频（spread spectrum）</div>',
        '    <div class="metric-note">clk_period.tcl 注释换算系数</div>',
        '  </div>',
        '  <div class="metric-card">',
        '    <div class="metric-value">%s / %s</div>' % (M["syn"], M["pt"]),
        '    <div class="metric-label">MARGIN（综合 / PT）</div>',
        '    <div class="metric-note">clk_period.tcl 开头的 margin</div>',
        '  </div>',
        '</div>',
    ]


def clk_uncertainty_line():
    return ("uncertainty 来源于历史经验值：hold uncertainty 全表统一 %s ps；setup uncertainty 按时钟不同为 %s ns 不等，"
            "只有高速 lane 时钟是 %s ps（脚本包 sdc_pr 展开产物实证）。"
            % (U["hold_ps"], U["setup_other_ns_range_ptintro"], U["setup_fast_lane_ps"]))


def clk_uncertainty_cards():
    rng = U["setup_other_ns_range_ptintro"].replace(" ", "")
    return [
        '<div class="metric-grid">',
        '  <div class="metric-card">',
        '    <div class="metric-value">%s ps</div>' % U["setup_fast_lane_ps"],
        '    <div class="metric-label">setup uncertainty</div>',
        '    <div class="metric-note">仅高速 lane 时钟；其余 %s ns 不等</div>' % rng,
        '  </div>',
        '  <div class="metric-card">',
        '    <div class="metric-value">%s ps</div>' % U["hold_ps"],
        '    <div class="metric-label">hold uncertainty</div>',
        '    <div class="metric-note">放宽需高层签字，不跨项目继承</div>',
        '  </div>',
        '</div>',
    ]


def scriptdict_conclusion():
    return ("结论：**hold uncertainty 全部 %s ns = %s ps 统一；setup %s ps 只对高速 lane 时钟成立，其余 %s ns 不等**。"
            "时钟周期定义见 `clk_period.tcl`：当前生效 `RX0_CLKP = %sns`（%s SPEC：`%s*%s/%s = %sns`）/ "
            "`RX1_CLKP = %sns`（%s：`%s*%s/%s = %s ≈ %sns`；1P 模式，`set_case_analysis 0 DPSEL_I`），"
            "综合 `MARGIN=%s` / PT `MARGIN=%s`。"
            % (U["hold_ns"], U["hold_ps"], U["setup_fast_lane_ps"],
               U["setup_other_ns_range_scriptdict"], A["rx0_ns"], S["rx0_g"], S["rx0_g"], S["spread"],
               S["divisor"], A["rx0_ns"], A["rx1_ns"], S["rx1_g"], S["rx1_g"], S["spread"], S["divisor"],
               S["rx1_div_mhz"], A["rx1_ns"], M["syn"], M["pt"]))


def mempower_0812_line():
    """memory-power.html 正文：0812 六组 + 1106 三组（descramble_power.json 侧取）。"""
    r = P0812["rows"]
    d = {row["key"]: row for row in DESC["rows"]}
    return ("- HV2M23 SVT 当前值与本章 §2.3 的 0812 六组实测一致（1L %s / %s / %s、2L %s / %s / %s mW）；"
            "1106 新增 descramble 2lane 1.6G 实测（24b %s / 8b %s / noscramble %s mW，见 §2.3 descramble 对比图）；"
            % (r["1l_normal"]["total_power_mW"], r["1l_dplc"]["total_power_mW"], r["1l_drdod"]["total_power_mW"],
               r["2l_normal"]["total_power_mW"], r["2l_dplc"]["total_power_mW"], r["2l_drdod"]["total_power_mW"],
               d["2lane_descramble24b_1106"]["total_power_mW"],
               d["2lane_descramble8b_1106"]["total_power_mW"],
               d["2lane_noscramble_1106"]["total_power_mW"]))


def pp(row, keys=("normal", "dplc", "drdod")):
    r = PP0826["rows"][row]
    return " / ".join("%s %s" % (k, r[k]) for k in keys if k in r)


def pp_1l18_bullet():
    return ("- 1L 1.8G：normal %s / dplc %s / drdod %s mW（较 1.7G 的 %s 升约 8%%，符合频率 1.8/1.7 ≈ +6%% 的量级）"
            % (PP0826["rows"]["svt_1l_1p8g"]["normal"], PP0826["rows"]["svt_1l_1p8g"]["dplc"],
               PP0826["rows"]["svt_1l_1p8g"]["drdod"], PP0826["rows"]["svt_1l_1p7g"]["normal"]))


def pp_2l09_bullet():
    return ("- 2L 0.9G：normal %s / dplc %s / drdod %s mW（较 1.6G 的 %s 降约 49%%，符合 0.9/1.6 ≈ 频率减半的量级）"
            % (PP0826["rows"]["svt_2l_0p9g"]["normal"], PP0826["rows"]["svt_2l_0p9g"]["dplc"],
               PP0826["rows"]["svt_2l_0p9g"]["drdod"], PP0826["rows"]["svt_2l_1p6g"]["normal"]))


def pp_inversion_bullet():
    return ("- 对比口径反转了 1P/2P 关系：同 total 吞吐下 2 lane 每 lane 频率减半 → **2P（0.9G）%s < 1P（1.8G）%s**，"
            "功耗接近减半、频率是主因；同 lane 下 normal < dplc ≈ drdod 仍成立；leakage 占比极小（SVT 库）"
            % (PP0826["rows"]["svt_2l_0p9g"]["normal"], PP0826["rows"]["svt_1l_1p8g"]["normal"]))


def pp_vs_lvt_bullet():
    return ("- 与 LVT 0720 同速率对比：1L 1.8G normal %s vs LVT %s；2L 0.9G normal %s vs LVT %s"
            "——SVT 在 2L 0.9G 下与 LVT 相当，1L 1.8G 下 SVT 更优（SVT leakage 低）"
            % (PP0826["rows"]["svt_1l_1p8g"]["normal"], PP0826["rows"]["lvt_1l_1p8g"]["normal"],
               PP0826["rows"]["svt_2l_0p9g"]["normal"], PP0826["rows"]["lvt_2l_0p9g"]["normal"]))


def pp_same_caliber_bullet():
    return ("- 同口径对比（1L normal）：SVT %s mW 较 LVT %s mW 下降；LVT 时期 opt 优化版曾做到 %s mW"
            "（APR 绕不出未采用）；"
            % (PP0826["rows"]["svt_1l_1p7g"]["normal"], PP0826["rows"]["lvt_1l_1p8g"]["normal"],
               PP0826["rows"]["lvt_opt_1l"]["normal"]))


def pp_0826_same_rate_bullet():
    return ("- 同速率 1L 1.8G：SVT 0826 %s vs LVT %s mW（SVT 低 ~9%%）；2L 0.9G：SVT 0826 %s vs LVT %s mW（基本相当）"
            % (PP0826["rows"]["svt_1l_1p8g"]["normal"], PP0826["rows"]["lvt_1l_1p8g"]["normal"],
               PP0826["rows"]["svt_2l_0p9g"]["normal"], PP0826["rows"]["lvt_2l_0p9g"]["normal"]))


# ---------------------------------------------------------------- 区块登记表
# kind="line"：anchor 正则命中唯一一行，整行替换
# kind="block"：anchor 命中起始行，end 为结束行的精确文本（含），整段替换
REGIONS = [
    dict(f="environment.html", kind="line", name="SVT 规模段",
         anchor=r"^\*\*当前状态（HV2M23，已换 SVT）\*\*", build=lambda: [env_svt()]),
    dict(f="pt-intro.html", kind="line", name="SVT 图注",
         anchor=r"^!\[综合报告 Threshold Voltage Group Report：SVT 100%", build=lambda: [pt_svt_caption()]),
    dict(f="synthesis-upf.html", kind="line", name="DC QoR · Total cell area",
         anchor=r"^HV2M23 实测结果（接近 TO 版本）", build=lambda: [upf_dc_qor_line()]),
    dict(f="pt-intro.html", kind="line", name="uncertainty 说明段",
         anchor=r"^uncertainty 来源于历史经验值", build=lambda: [clk_uncertainty_line()]),
    dict(f="pt-intro.html", kind="block", name="uncertainty metric 卡片",
         anchor=r'^<div class="metric-grid">$', end='</div>',
         contains='仅高速 lane 时钟；其余', build=clk_uncertainty_cards),
    dict(f="pt-intro.html", kind="line", name="时钟·当前生效 bullet",
         anchor=r"^- \*\*当前生效（HV2M23，接近 TO，1P 模式）\*\*", build=lambda: [clk_active_bullet()]),
    dict(f="pt-intro.html", kind="line", name="时钟·展频 bullet",
         anchor=r"^- 展频（spread spectrum）：", build=lambda: [clk_spread_bullet()]),
    dict(f="pt-intro.html", kind="line", name="时钟·慢时钟 bullet",
         anchor=r"^- 另有一条慢 clock（教学示例", build=lambda: [clk_slow_bullet()]),
    dict(f="pt-intro.html", kind="line", name="时钟·图注",
         anchor=r"^!\[clk_period\.tcl：", build=lambda: [clk_caption()]),
    dict(f="pt-intro.html", kind="block", name="时钟·metric 卡片",
         anchor=r'^<div class="metric-grid">$', end='</div>',
         contains='RX0 时钟周期（当前生效，1P）', build=clk_metric_cards),
    dict(f="script-dict.html", kind="line", name="时钟/uncertainty 结论行",
         anchor=r"^结论：\*\*hold uncertainty 全部", build=lambda: [scriptdict_conclusion()]),
    dict(f="memory-power.html", kind="line", name="0812 六组 + 1106 三组正文行",
         anchor=r"^- HV2M23 SVT 当前值与本章 §2\.3", build=lambda: [mempower_0812_line()]),
    dict(f="powerpro.html", kind="line", name="0826 · 1L 1.8G bullet",
         anchor=r"^- 1L 1\.8G：normal", build=lambda: [pp_1l18_bullet()]),
    dict(f="powerpro.html", kind="line", name="0826 · 2L 0.9G bullet",
         anchor=r"^- 2L 0\.9G：normal", build=lambda: [pp_2l09_bullet()]),
    dict(f="powerpro.html", kind="line", name="0826 · 1P/2P 反转 bullet",
         anchor=r"^- 对比口径反转了 1P/2P 关系", build=lambda: [pp_inversion_bullet()]),
    dict(f="powerpro.html", kind="line", name="0826 · vs LVT bullet",
         anchor=r"^- 与 LVT 0720 同速率对比", build=lambda: [pp_vs_lvt_bullet()]),
    dict(f="powerpro.html", kind="line", name="§3.1 · 同口径对比 bullet",
         anchor=r"^- 同口径对比（1L normal）", build=lambda: [pp_same_caliber_bullet()]),
    dict(f="powerpro.html", kind="line", name="§4.1 · 同速率对比 bullet",
         anchor=r"^- 同速率 1L 1\.8G：SVT 0826", build=lambda: [pp_0826_same_rate_bullet()]),
]


def read_lines(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read().split("\n")


def apply_region(lines, reg):
    """返回 (start, end_exclusive, new_lines)；找不到/不唯一则抛错。"""
    rx = re.compile(reg["anchor"])
    if reg["kind"] == "line":
        hits = [i for i, l in enumerate(lines) if rx.search(l)]
        if len(hits) != 1:
            raise SystemExit("[params] %s :: %s 锚点命中 %d 次（应为 1）"
                             % (reg["f"], reg["name"], len(hits)))
        s = hits[0]
        return s, s + 1, reg["build"]()
    # block：先按 contains 唯一定位块内特征行，再往回找最近的 anchor 起始行，
    # 往后再找第一条精确等于 end 的行（避免多个同名 metric-grid 锚点互相冲突）
    chits = [i for i, l in enumerate(lines) if reg["contains"] in l]
    if len(chits) != 1:
        raise SystemExit("[params] %s :: %s contains=%r 命中 %d 次（应为 1）"
                         % (reg["f"], reg["name"], reg["contains"], len(chits)))
    ci = chits[0]
    s = None
    for i in range(ci, max(-1, ci - 80), -1):
        if rx.search(lines[i]):
            s = i
            break
    if s is None:
        raise SystemExit("[params] %s :: %s 未在 contains 行之前 80 行内找到 anchor"
                         % (reg["f"], reg["name"]))
    ei = None
    for i in range(ci, min(len(lines), ci + 60)):
        if lines[i] == reg["end"]:
            ei = i
            break
    if ei is None:
        raise SystemExit("[params] %s :: %s 未找到结束行 %r" % (reg["f"], reg["name"], reg["end"]))
    return s, ei + 1, reg["build"]()


def main():
    check = "--check" in sys.argv
    by_file = {}
    for reg in REGIONS:
        by_file.setdefault(reg["f"], []).append(reg)
    drift = []
    for f, regs in sorted(by_file.items()):
        path = os.path.join(GUIDE, f)
        lines = read_lines(path)
        changed = 0
        for reg in reversed(regs):           # 从后往前替换，避免行号漂移
            s, e, new = apply_region(lines, reg)
            old = lines[s:e]
            if old != new:
                drift.append("%s :: %s（第 %d-%d 行）" % (f, reg["name"], s + 1, e))
                lines[s:e] = new
                changed += 1
        if changed and not check:
            with io.open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write("\n".join(lines))
            print("[params] %-18s 重渲染 %d 个区块" % (f, changed))
        elif changed:
            print("[params] %-18s 漂移 %d 个区块" % (f, changed))
        else:
            print("[params] %-18s 全部区块与数据源一致（%d 个）" % (f, len(regs)))
    if check:
        if drift:
            print("[params] RESULT: FAIL —— %d 个区块与数据源漂移（跑 python image/tools/gen_param_blocks.py 重渲染）" % len(drift))
            for d in drift:
                print("    X", d)
            return 1
        print("[params] RESULT: PASS —— %d 个区块均与 data/*.json 一致" % len(REGIONS))
        return 0
    print("[params] done（%d 个区块）" % len(REGIONS))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 20:50
