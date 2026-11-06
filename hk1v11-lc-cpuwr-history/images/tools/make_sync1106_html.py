# -*- coding: utf-8 -*-
# make_sync1106_html.py — 由 sync-1104.html 骨架生成 sync-1106.html（1106 服务器回传包 · 寄存器变更 1106v1）
# 仅替换 title / page-nav / #md 内容 / 尾签名（骨架 = 固定模块，逐字保留）
import io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
DST = os.path.join(BASE, "..", "..", "sync-1106.html")

html = io.open(DST, encoding="utf-8").read()

# 1) <title>
html = html.replace("<title>1104 服务器同步 · 寄存器变更 · LC_CPUWR 修改记录</title>",
                    "<title>1106 服务器同步 · 寄存器变更（1106v1）· LC_CPUWR 修改记录</title>", 1)

# 2) page-nav（sync-1106 为末章：prev=sync-1104，next=空）
html = re.sub(
    r'<div class="page-nav">\s*<a href="\./status\.html">.*?</a>\s*<span></span>\s*</div>',
    '<div class="page-nav">\n      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <span></span>\n      </div>',
    html, count=1, flags=re.S)

# 3) #md 内容（整块替换 <script type="text/template" id="md"> ... </script>）
MD = r'''# 十、1106 服务器同步 · 寄存器变更（1106v1）

> **本同步为服务器回传包批准覆盖（他人修改、diff-first 全采，非本地功能修改）**：内网工作站 1106 代三包 `PACK_TAR_1106V1`（HDL）/ `PACK_TAR_1106V0`（SYNTHESIS）/ `PACK_TAR_1106V2`（DV_TCON_C）覆盖到本地 `HDL/` / `SYNTHESIS/` / `DV_TCON_C/`，基线 = 本机 **1104v1**。三件套（LC_CPUWR / LC_REG_MAPPING / LINK_CONFIG_CTRL）md5 前 8 位 `604350ad` / `452041d4` / `2002f606`，**均与 V1 tar 原字节一致**。**三件套升版 1106v1**（文件头升版 + 双轨登记 + changelist NO56）。

## 1. 1106v1 服务器回传包 · 寄存器变更图

![1106v1 服务器回传包 · 寄存器变更](./images/anim/1106v1_reg_changes.svg?v=20261106r1)

> 服务器端 (a)~(j) 十项变更（图列 7 项 = RTL/DV 主要寄存器变更）：类型 / 状态见图中色标（恒直出=青 / 新增=蓝 / 归属=靛 / 收窄=琥珀 / env=紫 / 删除=红；✅ 绿=已采）。

## 2. 寄存器变更明细（服务器端）

| # | 变更点 | 类型 | 影响模块 | 状态 |
|---|--------|------|----------|------|
| (a) | **SMART_CS 恒直出**：去 CHIP_SEL 门控，`assign SMART_CS[3:0] = {R_REG02_F[7:6],R_REG02_F[3:2]};`（cs=0 也直通，0708v1「仅 chip_sel=1 有效」语义取消） | 恒直出 | LC_REG_MAPPING | ✅ 符合表 |
| (b) | **LINK_CONFIG_CTRL 新增输出 `VPS_EN_0`**（164 行）：0x28[6] low-power（`VPS_EN_0=R_REG40_F[6]`）上抛供上层消费；四根寄存器输出连接（VPS_EN_1/khead/TP_SEL/BACSCR，`// 1104` 短注释）移至 LC_REG_MAPPING 实例**尾部**（590-593 行，**挂法与 1104v1 完全相同——仍挂 LC_REG_MAPPING 实例，非挂回 LC_CPUWR**） | 新增/归属 | LINK_CONFIG_CTRL | ✅ 功能零变化 |
| (c) | **VPS_EN_0 穿线链**：LOGIC_CENTER / CENTER1 / ANCTL / LINK_LOGIC 逐层穿线；ANCTL 新增 `VPS_EN_1_ENABLE_CS/POFF/POL_OFF` | 穿线 | 多层 | ✅ |
| (d) | **R_KHEAD_20B_SEL 消费链 [4:0]→[2:0] 全链收窄**：CHPI_DECODE / SHORT_ENCODING / LONG_ENCODING / SHORT_ENCODING_ALIGN / long_encoding / LONG_ENCODING_ALIGN——清 1104v1「khead 上层消费链改宽挂账」的宽度半边（极性半边 1104v1 已随移址定案 3'b101=40bit） | 收窄 | 全链 6 文件 | ✅ 清 1104 挂账 |
| (e) | **K4_FIND_1 新信号链**：SHORT_ENCODING_ALIGN 新增输出 → SHORT_ENCODING_OUTPUT 输入，驱动 `config_mode_k4_1` | 新增 | SHORT_ENCODING | ✅ |
| (f) | **LC_CPUWR 删一行旧日期注释**（`//20260702_1426`），无功能变化 | 注释 | LC_CPUWR | ✅ |
| (j) | **LENB_CTRL 删 `BIT_ALIGN_PT_DLY` 打拍寄存器**（任务书 (a)~(i) 之外、t4 自查补充的 V1 服务器项，少一拍延迟） | 删除 | LENB_CTRL | ✅ 自查补充 |

## 3. SMART_CS 恒直出 · 寄存器表核对（t1）

> 读 `HK1V11_Register_20261103.xlsm`（DLP 加密，经 Excel COM）核对：**恒直出符合表**。

- **history R10（2026-10-01）** 显式声明 *"Address 0x02 is not controlled by CHIP_SEL; SMART_CS[3:0] unaffected by CHIP_SEL"*
- **Reg_1V11 R13 0X02 单行无 CHIP_SEL 拆分**（对照 0x09/0x0A/0x1F 双行拆分）：SMART_CS[3:2]@[7:6]、SMART_CS[1:0]@[3:2]、默认 0X00
- **Reg_description_F_CHIP_SEL=1 与 =0 两页 R13/R15 对 SMART_CS 定义逐字相同**（R/W、默认 2'b00、[0111]:256 packet / [1111]:128 packet）；对照组 chip_sel=0 页 R41 把 0x09 整字节标 Reserved，证明表会用 Reserved 标记 chip_sel=1 专属功能而 SMART_CS 未标
- **20261106 新表交叉验证语义未变**（仅改名 SMART_CS_3/2/1/0）；改动前「三态版（chip_sel=0 强制 0000）」反而与表不符

## 4. DV / SYNTHESIS 侧（V2 / V0 包）

- **(g) DV env_cfg.sv 寄存器表 19 hunk**：TP_SEL[1:0]@0X08[5:4]（默认 2'b11，与 1104v1 RTL 对齐）；0X1D 行重排 = khead_20b_sel[2:0]@[7:5] / BACSCR_EOL@[4] / **SP_S 挪 [3:1]** / VPS_EN[0]@[0]；删 TP_F_AHEAD@0X2E[3]；**新增 SCS_PKT_HALF@0X2F[0]**（RTL 1023v1 既有，env 补齐）；SMART_CS 打包去 chip_sel 分支（与 (a) 联动）；cfg_frame 生成物群联动再生
- **(h) SYNTHESIS ip_cons**：DPLC 组 `set_max_delay 8.0 → $DPLC_CLKP` 变量化×2组（映射前后组）；新增 `DATA_END_BY_DTCTL*` `set_multicycle_path 2 -start -setup` + `1 -start -hold`（from-only）一对；`set_size_only [get_cells -hier *u_gate*]` 守卫 `!= "dc_shell"` → `!= "pt_shell"` 反转
- **(i) clk_period.tcl**：仅注释差异、**未采纳**（PRISTINE 保持本机，git 零改动）

## 5. 覆盖执行与验证

- **覆盖（t2）**：V0(SYNTHESIS) approved 4595 = applied 3454 + skipped 1141（全为 powerpro `Batch::`/`process::` Windows 非法名，留痕 `.skipped.txt`）+ MISS 0；V1(HDL) 15/15/0；V2(DV) 1000/1000/0；三件套 md5 与 V1 tar 原字节一致
- **SYNTHESIS 覆盖后验证（t3）**：setup wc_cworst 53 / wc_cbest 66 / wc_typical 62 / lt_cworst 15、hold 仅 lt/ml 角（≥-0.036）；SEL-004=0、/D1 /D2=0（10 corner 全 0，遗留项未复现）；BKDU=R_REG03_L 28 条单拍可见（PIX_DATA_ASYNC 24 位+4，含全局 worst）、cpuwr 组（100pin/28bank，无 R_REG03_L）成员违例全消
- **代际判定（t3）**：报表 = 「$DPLC_CLKP 变量化 + R_REG03_L 排除 + UTC 移除」代（≈1106 包版主体，非 local 1104 的 8.0 代），但未吃到包版 DATA_END_BY_DTCTL 通配修正（run 中 get_pins 字面量 UITE-216 失效）

## 6. 登记状态

- **changelist**：`back3.HK1V11_changelist.xlsx` Register Change **NO56**（R58，`script/add_regchange_1106v1.py`，openpyxl 写前备份读后核对；SMART_CS 恒直出 / VPS_EN_0 / TP_SEL@0x08 / khead / BACSCR_EOL / SCS_PKT_HALF / TP_F_AHEAD 删除）
- **双轨 CHANGES**：目录级 `LC_CPUWR_history/CHANGES.md` + 根级 `修改记录/CHANGES.md` 已同步（1106v1 条目，服务器端 (a)~(j) 十项）
- **三件套同步**：`LC_CPUWR_history/{LC_CPUWR,LC_REG_MAPPING,LINK_CONFIG_CTRL}.v` ← 覆盖后 HDL 同名文件逐字节 + 文件头升 1106v1（英文，CJK 检查 0 命中）+ 尾签名 `// ymzhu 2026-11-06 18:26`（不建快照目录，git 即备份）
- **版本号**：三件套 = **1106v1**；站点 CURRENT 升至 1106v1

## 7. 遗留待反馈

| 项 | 侧 | 说明 |
|----|-----|------|
| **env↔RTL 0x1D 打包不一致** | spec owner | env 0X1D 打包 SP_S[3:1]/VPS_EN[0]@bit0 与 RTL `SP_S=R_REG29_F[2:0]`（0x1D[2:0]）/ `VPS_EN_0=R_REG40_F[6]`（0x28[6]）不一致（0x1D[3]/[0] RTL 侧无消费者） |
| **站点注释陈旧** | 后续修 | 包版 LC_REG_MAPPING.v 头/端口注释仍写 "chip_sel=1 only"（功能正确、注释未同步） |
| **20261106 表复位需求三条** | 最终批 | unlock reset 例外清单 / PORSD 不受 password&checksum 保护 / password error reset 例外地址段（ymzhu 11-06 补充，20261106 表更新关键规格） |
'''

start = html.index('<script type="text/template" id="md">') + len('<script type="text/template" id="md">')
end = html.index('</script>', start)
html = html[:start] + "\n" + MD + "\n" + html[end:]

# 4) 尾签名（.html → <!-- ymzhu ... -->，替换已有的）
html = re.sub(r'<!--\s*ymzhu[^\n]*-->\s*$', '', html.rstrip())
if html.rstrip().endswith('</html>'):
    html = html.rstrip()[:-len('</html>')].rstrip() + '\n<!-- ymzhu 2026-11-06 19:15 -->\n</html>\n'
else:
    html = html.rstrip() + '\n<!-- ymzhu 2026-11-06 19:15 -->\n'

io.open(DST, "w", encoding="utf-8", newline="\n").write(html)
print("written %s  %dB" % (DST, len(html)))
# ymzhu 2026-11-06 19:15
