# -*- coding: utf-8 -*-
# make_sync1104_html.py — 由 timeline.html 模板生成 sync-1104.html（新章节，仅替换 #md / title / page-nav）
# ⚠ 历史脚手架（2026-11-04 12:06 一次性生成 §1-5）：现行 sync-1104.html 已手工扩展 §6（1104v1 迭代），
#   重跑本脚本会用 §1-5 旧内容整页覆盖、丢失 §6 —— 仅留档复现首次建页，勿在现行站点重跑。
import io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "..", "..", "timeline.html")
DST = os.path.join(BASE, "..", "..", "sync-1104.html")

html = io.open(SRC, encoding="utf-8").read()

# 1) <title>
html = html.replace("<title>核心变更时间线 · LC_CPUWR 修改记录</title>",
                    "<title>1104 服务器同步 · 寄存器变更 · LC_CPUWR 修改记录</title>", 1)

# 2) page-nav（sync-1104 为末章：prev=status，next=空占位）
old_pn = re.search(r'<div class="page-nav">.*?</div>', html, re.S)
new_pn = ('<div class="page-nav">\n'
          '      <a href="./status.html"><span class="label">上一篇</span><span class="title">当前状态与后续</span></a>\n'
          '      <span></span>\n'
          '      </div>')
html = html.replace(old_pn.group(0), new_pn, 1)

# 3) #md 内容（整块替换）
MD = r'''# 九、1104 服务器同步 · 寄存器变更

> **本同步为服务器回传态接收覆盖（非本地功能修改）**：`PACK_TAR_1104V1`（HDL，1104 代际：DC 11-03 01:20 / SDC 11-03 10:53 / PT 11-04 09:47，三方对齐一致，代际无串味）覆盖到本地 `HDL/HK1V11_digital_top/seperated_code/`，较本地 **1029v1-clean** 有 **5 处设计取向差异**，**用户 2026-11-04 确认全部有意、全采不回退**。**未单独升版本号**（LC_CPUWR 头保持 1029v1 / LC_REG_MAPPING 头保持 1027v1）。

## 1. 1104 服务器同步 · 寄存器变更图

![1104 服务器同步 · 寄存器变更](./images/anim/1104_reg_sync_changes.svg?v=20261104r1)

> 五处差异：①集成前移（4 挂账输出连线）②CS_SET_1H 改同步版 ③R_TP_F_AHEAD 停用 ④R_DPLC_MODE 长编码强 0 ⑤LC_REG_MAPPING 头仍 1027v1。类型 / 状态见图中色标（集成=琥珀 / 功能=靛 / 构建=青 / 版本=灰；✅ 绿=已采 / ⏸ 琥珀=未升头）。

## 2. 五处差异明细

| # | 变更点 | 类型 | 影响模块 | 状态 |
|---|--------|------|----------|------|
| 1 | **集成前移**：`LINK_CONFIG_CTRL` 补连 4 个挂账输出 `R_KHEAD_20B_SEL` / `R_TP_SEL` / `R_BACSCR_EOL` / `R_SCS_PKT_HALF`（本地 1029v1 为挂账未连；khead 架构仍=移入 LC_CPUWR 0x33[6:2]，1029v1） | 集成 | LINK_CONFIG_CTRL | ✅ 已连 |
| 2 | **CS_SET_1H**：`~R_BKDU` → `~BKDU_SYNC`（同步版） | 功能 | LC_CPUWR | ✅ 同步版 |
| 3 | **R_TP_F_AHEAD（0x2E[3]）停用**：回 Reserved、LC_CPUWR 端口+assign 注释、LINK_CONFIG_CTRL 驱常量 0 | 功能 | LC_CPUWR + LINK | ✅ 停用 |
| 4 | **R_DPLC_MODE**：新增 `` `ifdef LONG_VU440_FPGA `` 强 `1'b0`（长编码 FPGA 构建） | 构建 | LC_CPUWR | ✅ 长编码强0 |
| 5 | **LC_REG_MAPPING 头注释**：仍 `1027v1`（1027v1 的 R_KHEAD_20B_SEL 已注释停用，功能已等同 1029v1，未升头） | 版本 | LC_REG_MAPPING | ⏸ 未升头 |

## 3. 采用与验证

- **采用**（t3 寄存器三件套 + t11 非寄存器 26 文件，同名直接覆盖、逐字节验证与包一致）：
  - t3：寄存器三件套 `LC_CPUWR` / `LC_REG_MAPPING` / `LINK_CONFIG_CTRL` 服务器态 → `seperated_code/`（覆盖前 1029v1 备份在 `script/_1104_reg_before/`，已 gitignore，可还原）
  - t11：非寄存器 26 文件（25 .v + scratch `seperated_code/1`）→ 对应路径，26/26 逐字节与包一致（md5 旧→新见 `script/_1104_reg_before/md5_after_table.md`）
- **架构一致性**：khead_20b_sel 架构与本地 1029v1 一致（移入 LC_CPUWR 0x33[6:2]，`R_KHEAD_20B_SEL[4:0]=LSI_PRTECT?R_REG51_F[6:2]:5'b00000`）；LC_REG_MAPPING 内 1027v1 的 R_KHEAD_20B_SEL 端口/assign 均已注释停用（功能等同 1029v1 移除）
- **代际三方对齐**（1104 代际，用内容标记不靠 mtime）：`sum.rpt` Date=Wed Nov 4 09:47（10 corner）/ `read_cons.log` write_sdc=Tue Nov 3 10:53 / `dc.log` 标记=Tue Nov 3 01:20，三方一致，代际无串味
- **验收口径**：服务器包采纳（非本地功能修改），RTL 三关不适用（1022v1 口径）；逐字节 md5 核验 + 架构一致性 grep 核实 + 代际三方对齐

## 4. 登记状态

- **changelist**：`back3.HK1V11_changelist.xlsx` Register Change **NO=12** 登记草稿（`script/_1104_reg_changelist_draft.md`，**待用户登记**，本同步不写 xlsx）
- **双轨 CHANGES**：根级 `修改记录/CHANGES.md` + 目录级 `LC_CPUWR_history/CHANGES.md` 已同步（1104 服务器同步条目，用户 11-04 确认全采）
- **版本号**：本同步**未单独升版本号**（LC_CPUWR 头 1029v1 / LC_REG_MAPPING 头 1027v1）；站点 CURRENT 仍为 **1029v1**，本同步作为 1029v1 之上的服务器态覆盖记录

## 5. 与 POSTPT 1104V0 的关系

本寄存器同步与 POSTPT 站 [TO SIGNOFF 1104V0](../hk1v11-synthesis-postpt-practice/ch09-to-signoff.html) 同源（同一 1104 代际服务器包）：SYNTHESIS 侧（PT STA 10 corner 全收敛 + ip_cons 614 行）见 POSTPT 站 ch09；HDL 侧（寄存器三件套 + 非寄存器 26 文件）即本章。'''

start = html.index('<script type="text/template" id="md">') + len('<script type="text/template" id="md">')
end = html.index('</script>', start)
html = html[:start] + "\n" + MD + "\n\n" + html[end:]

# 4) 文件尾签名（.html → <!-- ymzhu ... -->，替换已有的）
html = re.sub(r'<!--\s*ymzhu[^\n]*-->\s*$', '', html.rstrip())
if html.rstrip().endswith('</html>'):
    html = html.rstrip()[:-len('</html>')].rstrip() + '\n<!-- ymzhu 2026-11-04 12:05 -->\n</html>\n'
else:
    html = html.rstrip() + '\n<!-- ymzhu 2026-11-04 12:05 -->\n'

io.open(DST, "w", encoding="utf-8", newline="\n").write(html)
print("written %s  %dB" % (DST, len(html)))
# ymzhu 2026-11-04 16:10
