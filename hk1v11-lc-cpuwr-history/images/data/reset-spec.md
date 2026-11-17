# 十二、复位规格 · 20261106（1106v2→v4 终版）

> 用户补充复位规格三条（11/06）已全部落地/核实：① unlock reset 例外清单 ② PORSD 不受 password&checksum 保护 ③ password error reset 例外地址段。本轮（t12）复位相关**零新增修复项**——t10 复位专项 finding=0、t11 复位分歧 2 条裁定均无需 RTL 改动；t9 的复位改动经 RTL 三关复核维持正确。**本节为用户亲自 review 材料。**

> **1106v4 注记（2026-11-10，用户拍板，NO59）**：**复位规格补丁——PORSD 写门控漏改终版修复**。1106v2 断言「PORSD 不受 password &amp; checksum 保护」，但 RTL `CHKSUM_A_EN` 分支下 `PORSD@0x01[5]` 直写仍被 `if(!chksum_mode||unlock_one_shot_a)` 门控——checksum 锁定态写 PORSD 只进 shadow 不生效，与规格矛盾。**修复**：① `R_REG01_F[5]` 直写**移出门控**（任意 `ADDR01_F` 拍生效）；② **`update_en_a` 提交路径 [5] shadow 回填移除**（用户拍板：PORSD 完全不参与 checksum 提交机制，消除未来 shadow↔直写冲突隐患）；AVE_LAST[7] 保持门控+回填、shadow 记录保留、非 `CHKSUM_A_EN` else 分支本就 ungated。仅 `LC_CPUWR.v` 单文件迭代（另两件维持 1106v3）；RTL 三关全过（iverilog 0 err / 对抗自审全绿 / 链路未动）；changelist **NO59**。**三路 DS 独立盲审**（ds1/ds2/ds3）四维度（复位选择/密码保护/checksum 参与/位置）全过，两项裁定关闭（#6 LSI 输出掩蔽现状正确 / #7 SCREN 独立复位），详见 `script/_ds_audit_1106/summary.md`。

## 1. 复位规格图（四维度）

![复位规格 · 20261106（1106v2→v4 终版）](./images/anim/reset_spec_1106v2.svg?v=20261110r3)

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
