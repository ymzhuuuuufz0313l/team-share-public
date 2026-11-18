<!-- §4.7 长短编码模式对比（2026-11-18 合流版：t4 数据矩阵 + t5 RTL 根因 + t6 双图）。
     待 ds-review 后再入 ch08-powerpro.html；本文所有功耗数字均出自 hier_pwr_detail.csv
     的 ;total; 行（文件+行号见注），RTL 行号经现场核对。 -->

# 4.7 长短编码模式对比：1V11 长编码（420b）vs 短编码（4G / 3G 双档）

> **口径**：仅 **1V11 自家**长短编码模块——`LC_CHPI_DECODE` 层级下 `LONG_ENCODING`
> 与 `SHORT_ENCODING` 的**全子块**（ALIGN / DECODE / DESCRAMBLE / ERROR_CTRL / OUTPUT）。
> 数据源（PowerPro `hier_pwr_detail.csv`，Initial Design top total 口径，Top = 各文件 L11 `u_LOGIC_CENTER;total`）：
> * **长码 4G** = `PACK_TAR_1118V0/.../powerpro/rep_dir_1lane_4g_420b_1118/`，Top **35218.89 µW**
> * **长码 3G** = `PACK_TAR_1118V0/.../powerpro/rep_dir_1lane_3g_420b_1118/`，Top **26225.24 µW**
> * **短码 4G** = `rep_dir_1lane_4g_1117/`，Top **24153.53 µW**
> * **短码 3G** = `rep_dir_1lane_3g_1117/`，Top **18474.64 µW**（csv 原值 18474.63x）
> 解析入口 `script/_power1117/parse_longcode.py`（--json 落盘 `longcode_{4g,3g}_data.json`）。

## 4.7.1 功耗矩阵（µW，csv ;total; 行原值两位）

| 子块 | 短码@4G | 短码@3G | 长码@4G | 长码@3G |
|---|---:|---:|---:|---:|
| **LONG_ENCODING（组级）** | **790.50** | **617.19** | **18704.72** | **13913.32** |
| ├ LONG_ENCODING_ALIGN | 319.85 | 259.73 | 6136.41 | 4609.82 |
| ├ LONG_ENCODING_DECODE | 0.52 | 0.52 | 4668.24 | 3454.84 |
| ├ LONG_ENCODING_DESCRAMBLE | 0.23 | 0.23 | 1046.55 | 775.38 |
| ├ LONG_ENCODING_ERROR_CTRL | 0.16 | 0.16 | 381.86 | 282.53 |
| └ LONG_ENCODING_OUTPUT | 469.74 | 356.55 | 6146.87 | 4548.89 |
| **SHORT_ENCODING（组级）** | **9621.91** | **7346.01** | **1232.62** | **920.44** |
| ├ SHORT_ENCODING_ALIGN | 2917.23 | 2220.49 | 282.99 | 211.77 |
| ├ SHORT_ENCODING_DECODE | 1688.30 | 1287.89 | 0.44 | 0.44 |
| ├ SHORT_ENCODING_ERROR_CTRL | 137.80 | 104.71 | 0.08 | 0.08 |
| └ SHORT_ENCODING_OUTPUT | 4562.69 | 3493.37 | 949.11 | 708.15 |

> 子块行号（四个 csv 布局相同，文件根
> `C:/Users/zhuyanming/Downloads/PACK_TAR_1118V0/XXW_PRJ01/HK1V11/designer/DD/ymzhu/HK1V11/SYNTHESIS/ip/syn_HK1V11_digital_top/powerpro/rep_dir_1lane_{4g,3g}_{420b_1118,1117}/hier_pwr_detail.csv`）：
> ERROR_CTRL=L20、OUTPUT=L29、DESCRAMBLE=L38、DECODE=L47、ALIGN=L56、LONG 组级=L65、
> SHORT_ERROR=L74、SHORT_OUTPUT=L83、SHORT_DECODE=L92、SHORT_ALIGN=L101、SHORT 组级=L110。
> 组级行 = 该子树 total（含子块），与子块行同 csv 不同 total 行，未做加减。
> **口径注（组级 ≠ 子块和）**：组级 total 略大于子块之和，差额 = 组级共享时钟树
> （clock_network）分配，出现在**该模式下活跃**的组：长码报告 LONG 组（csv L65）
> 4G **324.79** / 3G **241.86** µW；短码报告 SHORT 组（csv L1117 侧 L110）4G **315.89** /
> 3G **239.55** µW；对方（静默）组差额仅 0.006–0.008 µW（数值按 csv 全精度重算，
> 与评审 F5 所引 324.80/241.84/315.88/239.58 差 ≤0.03，以 csv 为准）。
> 读法：对角外的「小值列」即残留——长码模式下 SHORT 组 1232.62（4G）/920.44（3G），
> 短码模式下 LONG 组 790.50（4G）/617.19（3G）；DECODE/DESCRAMBLE/ERROR_CTRL 残留
> 均在 1 µW 量级以下（漏电水平）。

## 4.7.2 可视化

![1V11 Long vs Short Encoding Module Power Comparison](./images/anim/power_module_compare_long_short.svg?v=20261118)

![1V11 Long vs Short Encoding Power Composition Donut](./images/anim/power_composition_donut_long_short.svg?v=20261118)

> 双图口径与 §4.5.1/§4.6.1 一致（组级对齐、按差额降序、蓝图风），数据取自 4.7.1 矩阵；
> 条形图第三系列参照统一为**短码@4G**（`rep_dir_1lane_4g_1117`，与 4.7.1 矩阵同源，
> json 已补 `short_ref_4g` 全 11 子块）。如后续需保留 4.46G（`rep_dir_1lane_4g5_1117`）
> 参照，须另列说明，默认不保留。

## 4.7.3 未门控清单（残留模块 → 根因 → 方案 → 预期回收）

**残留功耗（对方模式，按占比降序）**：长码下 SHORT 组级 1232.62/920.44 µW（占自身满负荷 12.8%/12.5%，其中 OUTPUT 20.8%/20.3%、ALIGN 9.7%/9.5%）；短码下 LONG 组级 790.50/617.19 µW（4.2%/4.4%，OUTPUT 7.6%/7.8%、ALIGN 5.2%/5.6%）。

| # | 模块（残留档） | 残留 µW（csv 行号） | RTL 根因 | 方案 | 预期回收 |
|---|---|---|---|---|---|
| 1 | SHORT_ENCODING_OUTPUT（长码@4G/@3G） | 949.11 / 708.15（L83） | OUTPUT 内部共享 `DCLK_DATA`/`DCLK_CONFIG` 域，时钟经 CLKGEN mux 常开（`SHORT_ENCODING_OUTPUT.v:240-283`；LONG 侧同构 `LONG_ENCODING_OUTPUT.v:443-461`） | CG_CELLX4 模式级门控：按编码模式关断对方域时钟（参照既有工程注释 ICG 写法，见 4.7.4 勘误注） | 残留全额为上限：@4G ≤949.11、@3G ≤708.15 µW |
| 2 | SHORT_ENCODING_ALIGN（长码@4G/@3G） | 282.99 / 211.77（L101） | DCLK 已被上游 ICG 关断，组合输入无使能掩蔽——残留来自输入引脚活动直接穿透组合网络翻转（`SHORT_ENCODING_ALIGN.v:105-146`；`LONG_ENCODING_ALIGN.v:266-330`） | ALIGN 输入掩蔽：对方模式下将输入钳到常量，消除组合翻转 | 残留全额为上限：@4G ≤282.99、@3G ≤211.77 µW |
| 3 | SHORT_ENCODING_DECODE / ERROR_CTRL（长码模式） | 0.44 / 0.08（L92/L74） | 整链 ICG 已生效，仅剩漏电 | 无需动作 | —（已达标） |
| 4 | LONG_ENCODING 各子块（短码模式） | 组级 790.50 / 617.19（L65） | 同 #1/#2 两类根因（OUTPUT 469.74 + ALIGN 319.85 为主）；另 `LC_CHPI_DECODE.v:38` 已有 SP（sleep/模式控制）但未下传到编码子块（`:116-220` 实例化区） | SP 下传 + 同 #1/#2 | 残留全额为上限：@4G ≤790.50、@3G ≤617.19 µW |

> 判据：对方模式功耗 > 自身同档满负荷 10% 判「未门控候选」——过阈者仅
> SHORT_ENCODING_OUTPUT（20.8%/20.3%）；SHORT_ENCODING_ALIGN 9.5–9.7% 为边界项随 #1 一并处理。
> 两类根因归纳（t5 RTL 根因分析）：①OUTPUT 类 = 共享时钟域常开；②ALIGN 类 = 时钟已被上游 ICG 关断、但组合输入无使能掩蔽，引脚活动穿透组合网络。
> DECODE/DESCRAMBLE/ERROR_CTRL 残留只剩漏电，证明整链 ICG 在对方模式下生效。
> 方案合计理论回收上限：长码模式 1232.62 µW（SHORT 残留全额，t5 口径 ≈6.1%）、
> 短码模式 790.50 µW（LONG 残留全额，t5 口径 ≈7.4%）。

## 4.7.4 解决建议（含优先级）

> 本节为**只读分析 + 改动草稿**（2026-11-18 现场核对行号），未改任何 RTL。
> 「收益上限」= 4.7.3 的对方模式残留全额（理论值，非实测回收量）。

| 优先级 | 建议（可实施化） | 具体改动点（文件:行） | 收益上限 µW（4G/3G） | 变更级别 | 主要风险 |
|---|---|---|---|---|---|
| P1 | SP 下传：两个编码 wrapper 加 `input SP`，`LC_CHPI_DECODE` 实例补 `.SP(SP)` | `SHORT_ENCODING.v:1-6` 端口 + `LC_CHPI_DECODE.v:116-119`；`LONG_ENCODING.v:1-10` 端口 + `:167-172` | 0（本身无收益，解锁 P2/P3） | **L2**（纯端口/连线） | 端口新增需核对 `file_list`（无新增文件）；SP 已在 `LC_CHPI_DECODE.v:38`，不跨层 |
| P2 | CG_CELLX4 模式级门控 OUTPUT 侧共享时钟：**在两个 wrapper 内**对送 OUTPUT 的 `DCLK_DATA`/`DCLK_CONFIG` 插 ICG（SHORT `ENA=SP`，LONG `ENA=N_SP`） | `SHORT_ENCODING.v:4-5,101-104`；`LONG_ENCODING.v:8-9,169-172` | 长码 ≤949.11 / 708.15；短码 ≤469.74 / 356.55 | **L3**（时钟路径结构变更） | ①ICG 成为该块 flop 时钟根，CTS/STA 需重跑；②`SCAN_EN` 沿既有惯例接 `1'b0`，DFT 需确认扫描可测性；③正确性依赖 SP 为静态 strap（4.7.4.2） |
| P3 | ALIGN 输入掩蔽：**只改实例端连接**（不动 ALIGN 文件），送 ALIGN 的三条输入总线按模式钳位 | `LC_CHPI_DECODE.v:122-124`（SHORT）、`:177-179`（LONG） | 长码 ≤282.99 / 211.77；短码 ≤319.85 / 259.73 | **L3**（原估 L2 **上调**：落点在 G13 敏感 ALIGN 输入锥，活跃模式多一级 AND2） | ①活跃模式 ALIGN 输入锥 +1 级门延时，需复跑该路径时序；②掩蔽常量取 0 需确认不与 K 码比较常量冲突 [待确认] |
| P4 | DECODE / DESCRAMBLE / ERROR_CTRL 无动作 | — | — | — | 残留为漏电水平，整链 ICG 已生效 |

### 4.7.4.1 P2 落地：ICG 插入点与代码形态

**事实链（为什么是「两个 wrapper 内」而不是 CLKGEN 内）**：ASIC 分支里 `CLKGEN.v:252-264` 的两个 `CLKMUX2X2`（u_gate_MUX_DCLK_DATA/CONFIG）把 `PIX_CLK_LONG` 与 `DCLK_DIV1P5_SHORT`（CONFIG 同构）合成**单一** `DCLK_DATA`/`DCLK_CONFIG` 网，再由 `LC_CHPI_DECODE.v:118-119`（SHORT）与 `:173-174`（LONG）**同时**接到两个编码块。非选中模式的 OUTPUT 因此仍被有效时钟打拍 —— 这就是残留根因；**一条网无法按模式分别关断**，必须在分支之后拆成两条按模式门控的时钟。

| 方案 | 改动面 | 文件数 | 结论 |
|---|---|---|---|
| A：CLKGEN 内新增 4 个 ICG + 4 个新时钟输出 | 需穿过 `CLKGEN → LC_CLK_RST_GEN → LOGIC_CENTER → LINK_LOGIC → LC_CHPI_DECODE` 四层端口 | ≥5 | 放弃：diff 过大且动顶层时钟端口 |
| **B：wrapper 内插 ICG（推荐）** | 两个 wrapper 各 2 个 ICG + `LC_CHPI_DECODE` 两处 `.SP(SP)` | **3** | 采纳：端口不动，ICG 写法与 `CLKGEN.v:100-111` 的 `u_gate_ICG_DCLK_SE/LE` 同构 |

**代码草稿（仅草稿，未落盘）**：

```verilog
// ---- SHORT_ENCODING.v ----
module SHORT_ENCODING(
     input          DCLK
    ,input          DCLK_DATA
    ,input          DCLK_CONFIG
    ,input          SP              // P1 新增：与 CLKGEN.v:4 / LC_CHPI_DECODE.v:38 同一静态 strap
    ...
);
wire DCLK_DATA_SE, DCLK_CONFIG_SE;

CG_CELLX4 u_gate_ICG_SE_DATA(       // 长码模式（SP=0）关断短码 OUTPUT 数据时钟
     .ENA     (SP)
    ,.CLKIN   (DCLK_DATA)
    ,.SCAN_EN (1'b0)
    ,.CG_CLK  (DCLK_DATA_SE)
);
CG_CELLX4 u_gate_ICG_SE_CONFIG(
     .ENA     (SP)
    ,.CLKIN   (DCLK_CONFIG)
    ,.SCAN_EN (1'b0)
    ,.CG_CLK  (DCLK_CONFIG_SE)
);

SHORT_ENCODING_OUTPUT SHORT_ENCODING_OUTPUT(
     .DCLK        (DCLK)
    ,.DCLK_DATA   (DCLK_DATA_SE)     // 原 :103 .DCLK_DATA(DCLK_DATA)
    ,.DCLK_CONFIG (DCLK_CONFIG_SE)   // 原 :104 .DCLK_CONFIG(DCLK_CONFIG)
    ...
);

// ---- LONG_ENCODING.v（同构，ENA 取非）----
wire N_SP = ~SP;                     // 与 CLKGEN.v:68 同写法
CG_CELLX4 u_gate_ICG_LE_DATA(   .ENA(N_SP), .CLKIN(DCLK_DATA),   .SCAN_EN(1'b0), .CG_CLK(DCLK_DATA_LE)   );
CG_CELLX4 u_gate_ICG_LE_CONFIG( .ENA(N_SP), .CLKIN(DCLK_CONFIG), .SCAN_EN(1'b0), .CG_CLK(DCLK_CONFIG_LE) );
// LONG_ENCODING_OUTPUT 实例（:169-172）改接 DCLK_DATA_LE / DCLK_CONFIG_LE

// ---- LC_CHPI_DECODE.v（两处实例补 SP）----
SHORT_ENCODING SHORT_ENCODING( ... ,.SP(SP) );   // :116 块内
LONG_ENCODING  LONG_ENCODING ( ... ,.SP(SP) );   // :167 块内
```

**正确性论证（反馈环不会断）**：三条模式相关反馈都只在本模式内被消费，冻结非选中侧不会自锁。
① `SHORT_ENCODING_PHASE_DATA` → `CLKGEN.v:69-70` 生成 `DCLK_DIV1P5_SHORT_pre`（1P5/DPLC 两相 pre），`CLKGEN.v:252-256` mux（.S=SP）选为 `DCLK_DATA`；短码模式下 SHORT 侧 `ENA=SP=1` 导通，环闭合。
② `PIX_CLK_EN_LONG`/`CONFIG_CLK_EN_LONG` → `CLKGEN.v:238-245` 的 ICG，仅 SP=0（长码）经 mux 被选中；长码模式下 LONG 侧 `ENA=N_SP=1` 导通。
③ 两 wrapper 输出在 `LC_CHPI_DECODE.v:227-243` 由 SP mux 二选一，SP 静态 ⇒ 同时只有一侧在动。

**DFT 注意**：现存 15 处 `CG_CELLX4` 实例（`CLKGEN.v`/`DTCTL.v`/`PAT_DET.v` 等）全部 `.SCAN_EN(1'b0)`，本方案沿用；但新增 ICG 使非选中模式 flop 在扫描态仍无时钟，需 DFT 侧确认是否接全局 scan enable（该层当前无此信号，故接 0 并标注待 DFT 评审）。

### 4.7.4.2 SP 扇出与打拍评估

- **SP 现状**：芯片输入脚静态 strap——ASIC 侧 `SP_I` 是 `TOP/HK1V11_digital_top.v:561` 顶层输入端口（`BUFFER_I.v:140` 缓冲为 `SP_buf` 分发）；`TOP/HK1V11.v:412` 只是 wire 声明、`:51` 是 kiwi 注释，唯一 assign 在 `:876` `` `ifdef VU440_FPGA `` 内（FPGA-only）；`CLKGEN.v:209` 明确注释「SP is a static protocol selection during normal operation」。当前扇出：`LC_CHPI_DECODE` 内 19 处（`:108-109` 2 处 + `:227-243` 17 处）、`CLKGEN` 内 8 处，另分发至 `CHPI_SD_CTRL`/`LC_CHPIF_L0`/`LC_CLK_RST_GEN`/`LC_MONBLOCK`/`LENB_CTRL`/`LINK_IO_CTRL`/`LINK_PANEL_CTRL` 等 14 个以上子模块。
- **新增负载**：4 个 ICG `ENA` + 120 个掩蔽 AND 输入（20 bit × 6 总线），相对既有扇出 <1%；层次边界由综合/CTS 插 buffer。**不需要为 SP 打拍。**
- **G13 重定时敏感区**：本方案**不新增寄存器、不打拍**，不触发 AGENTS §3.1 的「重定时消费者审计」；G13 两处敏感区（`SHORT_ENCODING_ALIGN.v` 的 `_TYP*_M` 掩蔽比较器组、`SHORT_ENCODING_DECODE.v:78-101` 的 `KEY_CODE_C[0..23]` 钥旋转）**本次 0 改动**。
- **前提条件（须确认为真）**：若 SP 存在运行中改写路径，裸 ICG 的 `ENA` 可能在时钟高电平期变化而截断脉冲，此时应改用 2FF 同步门控（`HDL/clk_rst/cell/kv_sync_clkgated.v`：2FF + `kv_gclk`，端口 `in_clk/clk_en/test_en/out_clk`）。本设计 SP 为封装 strap，按静态处理，故沿用 `CG_CELLX4`。

### 4.7.4.3 P3 落地：ALIGN 输入掩蔽方案对比

**关键事实（决定最优插入点）**：`I_INDATA`/`I_INDATA_D1`/`I_INDATA_D2` 在 `SHORT_ENCODING.v` 内**只**送 `SHORT_ENCODING_ALIGN`（`:59-61`，全文件无其他消费者），`LONG_ENCODING.v:92-94` 同构；`SHORT_ENCODING_DECODE`/`SHORT_ENCODING_OUTPUT` 均无该端口。⇒ 在**实例端**钳位与在 ALIGN **内部**钳位逻辑等价，但实例端方案完全不触碰 G13 敏感文件，也不给 DECODE/OUTPUT 活跃路径加延时。

| 方案 | 改动 | 文件·行数 | 触碰 G13 文件 | 活跃模式附加延时 | 结论 |
|---|---|---|---|---|---|
| **M1：`LC_CHPI_DECODE` 实例端掩蔽（推荐）** | 两处实例的 `.I_INDATA*` 换成掩蔽后网 | 1 文件 · ≈8 行 | 否 | +1 级 AND2（仅 ALIGN 锥） | **采纳** |
| M2：wrapper 内掩蔽（新增 3 条 masked wire 再送 ALIGN） | 两个 wrapper 各 3 条 assign | 2 文件 · ≈8 行 | 否 | 同 M1 | 备选（等价，文件更多） |
| M3：ALIGN 内部在三级比较器组前掩蔽 | 改 `_TYP*_M` 掩蔽 bank 上游 | 2 文件 · 多处 | **是**（G13 v3 反重触发几何 `SHORT_ENCODING_ALIGN.v:105-146,196-237`） | 同 M1，风险面最大 | 否决 |

**代码草稿（M1，仅草稿）**：

```verilog
// ---- LC_CHPI_DECODE.v ----
wire [19:0] I_INDATA_SE    = {20{ SP  }} & I_INDATA;      // 长码模式（SP=0）钳零
wire [19:0] I_INDATA_D1_SE = {20{ SP  }} & I_INDATA_D1;
wire [19:0] I_INDATA_D2_SE = {20{ SP  }} & I_INDATA_D2;
wire [19:0] I_INDATA_LE    = {20{~SP  }} & I_INDATA;      // 短码模式（SP=1）钳零
wire [19:0] I_INDATA_D1_LE = {20{~SP  }} & I_INDATA_D1;
wire [19:0] I_INDATA_D2_LE = {20{~SP  }} & I_INDATA_D2;

SHORT_ENCODING SHORT_ENCODING(
     ...
    ,.I_INDATA    (I_INDATA_SE)        // 原 :122 .I_INDATA(I_INDATA)
    ,.I_INDATA_D1 (I_INDATA_D1_SE)     // 原 :123
    ,.I_INDATA_D2 (I_INDATA_D2_SE)     // 原 :124
);
LONG_ENCODING LONG_ENCODING(
     ...
    ,.I_INDATA    (I_INDATA_LE)        // 原 :173
    ,.I_INDATA_D1 (I_INDATA_D1_LE)     // 原 :174
    ,.I_INDATA_D2 (I_INDATA_D2_LE)     // 原 :175
);
```

**为什么掩蔽有效且不与 P2 重复**：ALIGN 残留是**组合逻辑裸翻**（输入总线自身在翻转，与时钟无关；`DCLK_SE` 早已被 `CLKGEN.v:100-111` 的 ASIC 分支 ICG（u_gate_ICG_DCLK_SE/LE）门控（`:91-92` 的 `assign DCLK_SE=DCLK&SP` 属 FPGA `else` 分支）），P2 关时钟对它无效；掩蔽把输入钳成常量、比较器树静态，才是它唯一的消除手段。
**掩蔽常量取 0 的确认项 [待确认]**：需核对 `_TYP*_M` 比较常量是否含全 0 图样；即使命中，非选中侧 `K*_FIND`/`DATA_ALIGN`/`DATA_POINT_LAT` 也只被 `:227-243` 模式 mux 丢弃，且该侧时钟已被 P2 关断，不改变有效状态机 —— 但按 G13 双事故教训，须以最小对拍 TB 实测事件序列，不接受静态推演结论。
**G13 探针不受影响**：`script/gates/probes.json` 的 `_TYP1_M>0`（SHORT ALIGN）与 `DATA_POINT_LAT_D>0`（SHORT DECODE）两文件均不改，`overlay_check.py post` 可自证未被旧版覆盖。

### 4.7.4.4 实施顺序与闸门

- **变更包**：P1 单独落（`SHORT_ENCODING.v`/`LONG_ENCODING.v`/`LC_CHPI_DECODE.v` 三文件纯端口连线，L2）；P2+P3 合并为一个 **L3** 变更包（同三文件，时钟结构 + ALIGN 输入锥变更，建议一次过最小对拍 TB，避免两轮 L3 证据）。
- **闸门**：`python script/gates/preflight.py --level L3 --files <三路径>`；需具备 `rtl-code-review`（critical==0 && high≤1）、最小对拍 TB 证据、`rtl-signal-trace` Workflow C 三份机器输入。
- **TB 观测点**：SP=0/1 两态下 `K1..K4_FIND`、`KCODE_TOG`、`DATA_ALIGN`、`DATA_POINT_LAT`、`PIX_DATA`、`CONFIG_DATA` 事件序列（新旧 RTL 差分），并确认非选中侧 `SHORT_ENCODING_PHASE_DATA` 冻结后短码模式仍能正常相位生成。
- **明确不做**：不改 `SHORT_ENCODING_ALIGN.v` / `SHORT_ENCODING_DECODE.v`（G13 敏感）、不改 `CLKGEN` 端口、不新增寄存器、不为 SP 打拍。

> **勘误注**：工程内旧注释引用的 ICG（CG_CELL）实例位置行号已移位——现行
> `HDL/HK1V11_digital_top/seperated_code/CHPI_SD_CTRL.v:323-324` 为注释态 CG_CELL 写法参照
> （旧文档 270/271 行号作废）；本节 RTL 行号均为 2026-11-18 现场核对值。

## 4.7.5 结论

**长码@4G Top 35218.89 µW vs 短码@4G Top 24153.53 µW，长码高 11065.36 µW（×1.46）。逐块对账（同 csv total 行差值）：**

| 对账项 | Δ（长码@4G − 短码@4G）µW |
|---|---:|
| LONG_ENCODING（组级，L65） | **+17914.22** |
| SHORT_ENCODING（组级，L110） | **−8389.29** |
| LC_CHPI_DECODE 两组之外（Top 差 − 两组差） | **+1540.43** |
| **合计 = Top 差（L11）** | **+11065.36 ✓** |

**长码@3G Top 26225.24 µW vs 短码@3G Top 18474.64 µW，高 7750.60 µW（×1.42）**：
LONG_ENCODING **+13296.13**，SHORT_ENCODING **−6425.57**，两组之外 **+880.04**，合计 ✓。
（3G 组外精确值 = 26225.24 − 18474.635…，两位呈现为 880.04；早稿 880.05 系舍入误差，F9 已修。）
（口径一致化 F10：短码 3G Top 统一写 **18474.64**（csv 原值 18474.63x 四舍五入）；§4.6 现行
ch08 正文写 18474.63/18474.635 存在同数异写，ch08 侧修正归集成任务统一为 18474.64。）

**「两组之外」模块级归属闭环（2026-11-18 补，全层级 diff；四个 csv 行号布局完全相同：
Top=L11、LC_CHPI_DECODE=L119、SMT_CS=L173、LINK_PANEL_CTRL=L182、CHPI_SD_CTRL=L191、
LINK_CONFIG_CTRL=L245、LINK_LOGIC=L290、DTCTL=L326、ANCTL=L344、CENTER1=L353、
LC_CLK_RST_GEN=L371、BUFFER_I=L380）——4G 组外 +1540.43 µW：**

| 组外模块（行号） | Δ@4G µW | Δ@3G µW | 机理判读（推断，待确认） |
|---|---:|---:|---|
| BUFFER_I（L380） | **+1260.04** | +896.58 | 输入缓冲侧：长码真实 payload 数据率/翻转率高于短码测试图样 |
| CENTER1（L353，其中 DTCTL L326 / ANCTL L344） | **+1156.51**（DTCTL +1133.84、ANCTL +22.65） | +748.51（+745.75 / +2.75） | DTCTL 显示时序数据通路随解码后数据活动率上升；ANCTL 基本不变 |
| LINK_PANEL_CTRL（L182，其中 SMT_CS L173 +147.72 / CHPI_SD_CTRL L191 +67.91） | +229.63 | +126.03（+90.47 / +29.43） | 面板 SD 时序与 SMT 采样随输出负荷增加 |
| LINK_FAULT_CTRL（L281）/ LINK_IO_CTRL（L200） | +34.35 / +25.56 | +22.66 / +16.07 | 随数据活动小幅上升 |
| LINK_CONFIG_CTRL（L245） | **−1193.64** | −929.45 | 长码 run 下配置通路安静得多（配置写活动差），为主要负项 |
| LC_CLK_RST_GEN（L371） | −103.74 | −83.39 | 时钟生成侧净降 [待确认：与 CONFIG 项关联] |
| 各级裸单元（CHPI 两组外 +40.31 / LINK_LOGIC +66.80 / u_LOGIC_CENTER +24.61） | +131.72 | +83.03 | 层级直属单元随邻接数据活动上升 |
| **合计 = Top 差 − 两组差** | **+1540.43 ✓** | **+880.04 ✓** | 逐模块全精度闭环，Σ分项=组外总额（脚本核对） |

> 组外主结构：BUFFER_I + CENTER1（DTCTL 为主）+ PANEL 三项正贡献 ≈ +2646（4G），
> 被 LINK_CONFIG_CTRL −1194 部分抵消，净 +1540.43。机理判读为活动率差推断
> （长码真实 payload vs 短码测试图样），未经波形核对处标 [待确认]。

要点：① **主因是长编码引擎本体**——同为满负荷时 LONG 组 18704.72 vs SHORT 组 9621.91 µW（4G，**1.95×**），DECODE（0.52→4668.24 µW）为最大激活项，ALIGN/OUTPUT 次之；② 未门控残留只占次要地位：长码@4G SHORT 残留 1232.62 µW ≈ Top 差的 **11%**；③ 短码模式下 LONG 残留 4.2–4.4%，门控状态相对更好；④ 修复路径按 P1→P4（SP 下传 → OUTPUT 门控 → ALIGN 掩蔽），理论回收上限长码 1232.62 / 短码 790.50 µW；⑤ 「两组之外」+1540.43（4G）/+880.04（3G）µW **已闭环到模块级**（BUFFER_I +1260.04 / CENTER1·DTCTL +1133.84 / LINK_CONFIG_CTRL −1193.64 等，见上表）。全部结论以两侧 top total 为锚，子块明细供逐项复核。

<!-- ymzhu 2026-11-18 11:47 -->
