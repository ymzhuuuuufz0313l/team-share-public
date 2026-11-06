# -*- coding: utf-8 -*-
# make_sync1106v2_reset_html.py — 由 sync-1106.html 骨架生成 sync-1106v2.html（20261106 表全链）+ reset-spec.html（复位规格）
# 仅替换 title / page-nav / #md 内容 / 尾签名（骨架 = 固定模块，逐字保留）；并更新 sync-1106.html 下一篇指向 sync-1106v2
import io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(BASE, "..", "..")
SKEL = os.path.join(SITE, "sync-1106.html")
html0 = io.open(SKEL, encoding="utf-8").read()

def build_page(dst, title, prev, next, md, sig):
    html = html0
    # 1) <title>（替换 sync-1106 的 title）
    html = re.sub(r"<title>1106 服务器同步[^<]*</title>", "<title>%s</title>" % title, html, count=1)
    # 2) page-nav（替换 sync-1106 的 page-nav：prev=sync-1104）
    nav = '<div class="page-nav">\n      %s\n      %s\n      </div>' % (
        ('<a href="./%s"><span class="label">上一篇</span><span class="title">%s</span></a>' % prev) if prev else "<span></span>",
        ('<a href="./%s"><span class="label">下一篇</span><span class="title">%s</span></a>' % next) if next else "<span></span>")
    html = re.sub(r'<div class="page-nav">.*?</div>', nav, html, count=1, flags=re.S)
    # 3) #md 内容
    start = html.index('<script type="text/template" id="md">') + len('<script type="text/template" id="md">')
    end = html.index('</script>', start)
    html = html[:start] + "\n" + md + "\n" + html[end:]
    # 4) 尾签名
    html = re.sub(r'<!--\s*ymzhu[^\n]*-->\s*$', '', html.rstrip())
    html = html.rstrip()
    if html.endswith('</html>'):
        html = html[:-len('</html>')].rstrip() + "\n%s\n</html>\n" % sig
    else:
        html = html + "\n%s\n" % sig
    io.open(dst, "w", encoding="utf-8", newline="\n").write(html)
    print("written %s  %dB" % (dst, len(html)))

SIG = "<!-- ymzhu 2026-11-06 21:02 -->"

# ===== sync-1106v2.html（新表变更内容页）=====
MD_V2 = r'''# 十一、1106v2 · 寄存器表 20261106 全链更新

> **本同步为 20261106 新表全链更新（非服务器回传包，本地功能迭代）**：对象 = 寄存器表 `HK1V11_Register_20261106.xlsm`（较 20261103 的字段变更 + 用户补充复位规格三条）。经 **GLM+Qwen 双盲审 → 并集实施 → 双交叉验证 → captain 裁决修复 → RTL 三关** 全链落地，三件套升 **1106v2**（HDL/ 与 LC_CPUWR_history/ 逐字节一致），changelist **NO57@R59**。

## 1. 20261106 表变更图（字段迁址 + 复位维度）

![1106v2 · 20261106 表字段变更](./images/anim/1106v1_reg_changes.svg?v=20261106r1)

> 字段迁址（VPS_EN_0 / SP_S / reg_eq_rbc / reg_eol）+ unlock reset 6 组迁 RSTN。类型 / 状态见色标（恒直出=青 / 新增=蓝 / 归属=靛 / 收窄=琥珀 / env=紫 / 删除=红）。

## 2. 字段迁址明细（20261106 表 → 1106v2）

| # | 字段 | 旧（1106v1 / 1104 代） | 新（20261106 表） | 落位 |
|---|------|------------------------|-------------------|------|
| 1 | **VPS_EN_0** | R_REG40_F[6]（0x28[6]，LSI 门控） | R_REG29_F[0]（0x1D[0]，**去 LSI 门控**，0x1D=Checksum_prtect 段） | LC_CPUWR；0x28[6] 回 Reserved |
| 2 | **SP_S[2:0]** | R_REG29_F[2:0]（0x1D[2:0]） | R_REG29_F[3:1]（0x1D[3:1]） | LC_REG_MAPPING |
| 3 | **reg_eq_rbc0/1** | R_REG08_F[1:0]（0x08[1:0]，ungated） | R_REG35_F[1:0]（0x23[1:0]，**带出 LSI 门控**，>31 规则） | 输出口迁 LC_CPUWR；LINK_CONFIG_CTRL 实例换接 |
| 4 | **reg_eol** | R_REG56_F[6]（0x38[6]） | R_REG57_F[6]（0x39[6]，LSI 保留） | LC_CPUWR |
| 5 | **unlock reset 例外 6 组** | N_RST_NLOCK 域 | **RSTN 域**（6 组迁 + 7 组原符合 = 13 组全 RSTN） | 详见[复位规格](./reset-spec.html) |
| 6 | **env 同步** | auto_script 1106 包版 / 运行时 1022 代 | auto_script 补 0x23/0x39 + 运行时自 1022 代整体追平（两副本 md5 同）+ checker 键位同步 | DV_TCON_C/isprx_env |

**SMART_CS**：20261106 表仅改名 SMART_CS_3/2/1/0（语义未变，恒直出符合表）；RTL 保留总线名 `SMART_CS[3:0]` 并注明 1:1 对照（**不改信号名**，避免 DV `check_cfg_signal("SMART_CS")` / cfg_frame 键 / env case 键连锁 churn）。

## 3. 双盲审 + 交叉验证（方法论）

| 轮 | 任务 | 结果 |
|----|------|------|
| t7 | **GLM 盲审**（20261106 vs 20261103 全量 diff，含静默坑） | 语义级 15 / 静默 5 / 应改 13 / 复位 RTL 不一致 6 |
| t8 | **Qwen 盲审**（独立，未看 t7） | 变更 8 字段级（5 组）/ 静默 4 / 应改 10 / 复位不一致 2 |
| t9 | **并集实施**（RTL + env_cfg + 双轨 CHANGES + changelist） | 三件套 1106v2 + env 追平 + NO57@R59 |
| t10 | **交叉验证①**（Qwen 复核 t9 实施，git diff 对照查漏/多/错改） | PASS 0/0/0/3；复位 finding=0 |
| t11 | **交叉验证②**（GLM 复核 Qwen 盲审 + 分歧终表） | Qwen 漏报 7 / 误报 4 / 分歧终表 9 条（X1-X9）|
| t12 | **裁决修复 R1-R4 + RTL 三关** | 日期 14 处 / 键位零错位 / TP_F_AHEAD 18 行 / 死引用 1 行；三关全过 |

**分歧终表 9 条裁定**：X1 复位取 GLM / X2 表不代改取 GLM / X3 SMART_CS 不改名取 GLM / X4 去门控取 GLM / X5 password reset 0 项 RTL 改动取 GLM / X6 0x03[7] 非静默取 GLM / X7 env 双重滞后取 GLM / X8 变更总数口径差无对错 / **X9 history R3 日期取 Qwen**（serial 46330 换算复核实为 2026-11-04，GLM 自查披露 t7 标 11-05 有误）。

## 4. RTL 三关（t12，门禁 pass）

| 关 | 工具 | 结果 |
|----|------|------|
| ① 语法 | Icarus Verilog 13.0 | 三件套 syntax_err=0（豁免：20×CLKINVX4AL9 + 20×INVX2 + 3×子模块）+ 10 个 UVM SV 结构校验 PASS |
| ② 对抗评审 | rtl-code-review（ruthless） | **critical=0 / high=0 / medium=0 / low=3 → pass**；重定时审计判定未触发（同域源位重指 + 复位替换，生效拍零位移）|
| ③ 链路 | rtl-signal-trace | 四信号（VPS_EN_0 / SP_S / reg_eq_rbc / reg_eol）源→消费全链连通 + 消费端方程与表一致；复位扇出不出 LC_CPUWR；三层端口零失配 |

## 5. 静默变更清单处置

| 静默项 | 处置 |
|--------|------|
| S1 表主表 0X1D 漏落位 SP_S | **实现取 [3:1]**（描述页+history+env 三方一致）；DLP 权威表不代改 → 反馈清单 |
| S2 0x30 保护范围重定义（0x90~0x93 新进） | RTL 门控集已符合（144-147 本就 gated）→ 零改动 |
| S3 0x07 checksum disable 注释简化 | 文档级；checker 以 X 列清单为准（已同步键位）|
| S4 R 列 BWDL unlock-reset-all → register | RTL 已无 RSTN_BWDL 全局门 → 零改动 |
| S5 X 列逐字段 checksum 清单 | checker 键位已对齐（0x1D 四键 / 0x08 TP_SEL / reg_eq_rbc 出集）|

## 6. 登记与反馈

- **changelist**：`back3.HK1V11_changelist.xlsx` **NO57@R59**（fresh-load 回读 PASS）。
- **双轨 CHANGES**：目录级 + 根级 CHANGES 1106v2 条目；README 速查 1106v2×3。
- **表作者反馈 5 项**（不代改 DLP 权威表）：①主表 0X1D 补 SP_S@[3:1] ②CTRL_L O 列 "Password NG reset"@0X42 注解消歧 ③0x40~0x43 端点明确 0x40~0x44 ④0xA0~0xA1 只读注明 ⑤服务器侧 flat+env+cfg_frame+test 副本重生成 + 补建模 VPS_EN_1@0x43[7]。
- **版本号**：三件套 = **1106v2**；站点 CURRENT 升至 1106v2。
'''
build_page(os.path.join(SITE, "sync-1106v2.html"),
           "1106v2 · 寄存器表 20261106 全链更新 · LC_CPUWR 修改记录",
           ("sync-1106.html", "1106 服务器同步 · 1106v1"),
           ("reset-spec.html", "复位规格 · 20261106"),
           MD_V2, SIG)

# ===== reset-spec.html（复位规格页）=====
MD_RS = r'''# 十二、复位规格 · 20261106（1106v2 落地）

> 用户补充复位规格三条（11/06）已全部落地/核实：① unlock reset 例外清单 ② PORSD 不受 password&checksum 保护 ③ password error reset 例外地址段。本轮（t12）复位相关**零新增修复项**——t10 复位专项 finding=0、t11 复位分歧 2 条裁定均无需 RTL 改动；t9 的复位改动经 RTL 三关复核维持正确。**本节为用户亲自 review 材料。**

## 1. 复位规格图（四维度）

![复位规格 · 20261106（1106v2 落地）](./images/anim/reset_spec_1106v2.svg?v=20261106r1)

> 四复位规格维度：unlock reset 例外清单 / I2C_EN=1 全免 / PORSD 不受 password&checksum 保护 / password error reset 例外地址段。

## 2. unlock reset 例外清单（13 组 CTRL_F 信号，全 RSTN 域）

| 组 | 字段 | 位段 | 状态 |
|----|------|------|------|
| 1 | AVE_RGBW | 0x00[7:5] | t9 迁 RSTN |
| 2 | AVE_LAST | 0x01[7] | t9 迁 RSTN |
| 3 | DPLC_GROUP | 0x05[7:5] | t9 迁 RSTN |
| 4 | DPOLINV / AVE_MODE | 0x06[7,5,3,2,1] | t9 迁 RSTN |
| 5 | CTRLF_CHECKSUM | 0x07[3:0] | t9 迁 RSTN（跨 unlock 保持 chksum_mode）|
| 6 | 0x20 组 | 0x20[5:0] | 原符合 RSTN |
| 7 | 0x21 组 | 0x21[5:4] | 原符合 RSTN |
| 8 | 0x30 组 | 0x30[7:0] | 原符合 RSTN |
| 9 | I2C HIT0 / HIT1 | 0xF0 / 0xF1 | 原符合 RSTN |

- **13 组全部落在 RSTN 域**；**6 组由 t9 迁 RSTN**（模式照抄既有 PORSD/CH_SEL/SDC 例外块：写译码带 `(!chksum_mode || unlock_one_shot_a)` 门控、shadow 随迁、默认值不变），**7 组原本已符合**（CH_SEL / SDC / DPLC_MODE / TEST_PRTCT / R_UTC / R_TESTO_SEL / I2C HIT0&1）。
- **语义**：unlock 时值保持 = 表 R 列例外意图（"显示/unlock 期间操作需维持"）；CTRLF_CHECKSUM 跨 unlock 保持 = chksum_mode 状态维持、AVE/DPLC 保持 = 画面保持。

## 3. I2C_EN=1 全免 unlock reset

- **RTL 零改动**（链路已存在）：`I2C_EN_CTL → TEST_EN → I_TEST_REG_EN → RSTNGEN:50`；I2C_EN=1 时寄存器不进入 unlock reset 语义。

## 4. PORSD 不受 password & checksum 保护

- **RTL 零改动**：PORSD = RSTN 域 + 不在 LSI（password 保护）集。
- **checksum 排除**属 BCC 主端软件口径（非 RTL）；DV checker 按 0x01 字节追踪不受影响（PORSD 位在 expected 中保持，与 RTL 读回一致）——已注明。

## 5. password error reset 例外地址段

- **RTL 门控集与表 AC 列逐一致 → 零改动**：受门控地址段 = **32-38 / 40-47 / 51 / 53-57 / 144-147（dec）**，与 20261106 表 AC 列逐一致。
- **0x40~0x43（dec 64~68）端点消歧**：AC 列不含任何 CTRL_L 地址、RTL 所有 `_L` 寄存器全无门控 → **判 0x40~0x44 整块（dec 64~68）不做 password error reset**，两读法行为等价、零改动。
- **0xA0~0xA1（dec 160/161）**：只读 BCC 监视寄存器（RTL 无存储、直通输入，L138 注释 "reg160/161 have no mask per register map"）→ 无复位语义、零改动；是否应入表口径列入表作者反馈。

## 6. 用户 review 材料入口

- 本文件（复位规格四维度 + 13 组明细）
- `xverify_glm.md` §三 复位专节
- `CHANGES.md` 1106v2 (5) 条
- 每日记录_1109 §四
'''
build_page(os.path.join(SITE, "reset-spec.html"),
           "复位规格 · 20261106（1106v2）· LC_CPUWR 修改记录",
           ("sync-1106v2.html", "1106v2 · 20261106 全链更新"),
           None,
           MD_RS, SIG)

# ===== 更新 sync-1106.html 下一篇指向 sync-1106v2 =====
sp = io.open(SKEL, encoding="utf-8").read()
sp = sp.replace(
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <span></span>',
    '      <a href="./sync-1104.html"><span class="label">上一篇</span><span class="title">1104 服务器同步 · 1104v1</span></a>\n      <a href="./sync-1106v2.html"><span class="label">下一篇</span><span class="title">1106v2 · 20261106 全链更新</span></a>', 1)
io.open(SKEL, "w", encoding="utf-8", newline="\n").write(sp)
print("updated sync-1106.html page-nav next -> sync-1106v2")
