# Motion Kit v4 — 电影感纯 CSS in-SVG 动效规范（本站 7 图，2026-10-28 v4 升级定稿；v4.1 动效加密；v4.2 列车降速 + 数据密集清效）

> 本文件从 canonical 站 `hk1v11-longcode-420b-verification/anim/MOTION_KIT.md`（v4）复制结构；
> §0/§2/§3/§4/§5 与 canonical 逐字一致（kit CSS 与铁律禁改），§1 路径与 §6 分图规格为本站实际。
> 上位架构 = `blueprint-ui-style` skill「动画/静态双版 SVG 站点架构（v4）」章。
> 用户对旧动效（v1）的判定：稳态效果不明显（POR 默认值列/参与字节/受保护域/关键总结框统一低幅呼吸）。
> v4 方向：**稳态肉眼可辨（行波/脉冲/扫光/列车）+ 入场先容器后内容再箭头 + 不要怕炫技**。
> 本文件是本站 7 张图 v4 动效的唯一事实源。

## 0. 铁律（不变量，违反即 FAIL）

1. **源 SVG 一律只读**。输出只写 `images/anim/<name>.svg`；生成器只写 `images/anim/make_anim_<name>.py`。
2. **数据/几何/颜色零改动**：`<text>` 多重集与源图完全一致；`<svg>` 开标签（width/height/viewBox）与源图完全一致；所有 rect/text/line/path 的坐标、尺寸、fill、stroke、stroke-width、stroke-dasharray 原样保留。
3. **纯 CSS in-SVG**：不允许 `<script`、不允许 SMIL `<animate>`、不允许外部资源。新增允许项：`class` 属性、`pathLength` 属性、`style` 内联（animation-delay/duration/opacity 初值/CSS 变量）、`<style>` 块（kit CSS）、复制箭头得到的装饰路径（`.flowdot`/`.flowtail`）、**v4 新增：`<defs>` 内渐变 + `<clipPath>`（仅扫光带用）**。
4. **生成器必须保留源图 `<defs>`（marker-end 箭头依赖）与背景 rect**（v2.1 回归教训：漏带 defs → 箭头端丢失）。组装段用 assert 保护。本站仅 checksum_logic_flow 有源 defs（3 个 marker）；beat 的扫光 `<defs>` 为 v4 新增项（chip_sel0/1 的扫光 defs 已随 v4.2 密集清效移除）。
5. 本站源图无字体 `<style>` 行（与 canonical 不同）；kit `<style>` 紧跟 `<svg>` 开标签之后。
6. **reduced-motion 安全**：kit CSS 自带媒体块，原样保留。
7. 生成器**确定性、幂等**：只读源 SVG，重跑输出字节一致；零第三方依赖；`python`（3.13）运行；脚本内路径用正斜杠。
8. 生成器文件尾签名：`# ymzhu 2026-10-28 <HH:MM>`。
9. 不动其他图的文件、**不动任何 HTML**（引用 bump 由主代理统一做）、不建临时目录、不 git 操作。

## 1. 路径（本站 images/ 布局）

- 源 SVG（只读）：`E:\project\team-share-public\hk1v11-lc-cpuwr-history\images\<name>.svg`
- 输出：`...\hk1v11-lc-cpuwr-history\images\anim\<name>.svg`
- 生成器：`...\images\anim\make_anim_<name>.py`
- 校验器：`...\images\anim\validate_kit_v4.py`（ROOT=images/anim、SITE=images，按文件位置自动推导，与 canonical 的 anim/-站根 关系同构）
- v1 生成器已重写为 v4（beat/checksum/chip_sel0/chip_sel1/lsi/reset 共 6 个）；`make_checksum_logic.py` 是 checksum_logic_flow 的**静态版**生成器（只读参考，不碰）；`make_anim_checksum_logic.py` 为 v4 新建。
- HTML 引用一律指向动画版 `images/anim/<name>.svg`（由主代理统一管理）。

## 2. Motion Kit CSS v4（逐字嵌入生成器，作为新增 `<style>` 行内容）

```css
.row{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .55s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .6s cubic-bezier(.4,0,.2,1) forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:9 91;stroke-width:3.5;animation:flow 2.6s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.flowtail{fill:none;stroke-linecap:round;stroke-dasharray:4 96;stroke-width:8;opacity:.25;animation:flow 2.6s linear infinite}
.pulse{transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-in-out infinite}
@keyframes pulse{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(180,83,9,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(180,83,9,.75))}}
.pulse-t{transform-box:fill-box;transform-origin:center;animation:pulseT 2.8s ease-in-out infinite}
@keyframes pulseT{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(14,116,144,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(14,116,144,.75))}}
.pulse-b{transform-box:fill-box;transform-origin:center;animation:pulseB 2.8s ease-in-out infinite}
@keyframes pulseB{0%,100%{opacity:1;filter:drop-shadow(0 0 0 rgba(29,78,216,0))}50%{opacity:.8;filter:drop-shadow(0 0 10px rgba(29,78,216,.75))}}
.sweepband{opacity:.85;animation:sweepMove 8s linear infinite}
@keyframes sweepMove{to{transform:translateX(var(--sweepP,160px))}}
.dashgrow{stroke-dasharray:7 5;animation:dashgrow 2.6s linear infinite}
@keyframes dashgrow{from{stroke-dashoffset:72}to{stroke-dashoffset:0}}
.march{animation:march 1.5s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.cellwave{animation:wave 2.6s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.72}}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}24%,92%{filter:drop-shadow(0 0 0 rgba(29,78,216,0))}100%{filter:drop-shadow(0 0 9px rgba(29,78,216,.85))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade{opacity:1!important}.flowdot,.flowtail,.sweepband{display:none!important}}
```

## 3. 类语义、硬指标与 delay 规则

| 类 | 层 | 用在哪 | 打标签方式 |
|---|---|---|---|
| `.row`/`.head` | 入场 | 面板/行/标题一次性入场 | 包 `<g class="row" style="animation-delay:Xs">` |
| `.draw` | 入场 | **实线**箭头描边生长（CSS 会覆盖 dasharray，虚线一律用 .fade） | 元素加 `class="draw" pathLength="100"` + delay |
| `.fade` | 入场 | 虚线箭头/标签/次要元素淡入 | 加 class + delay（可内联 duration） |
| `.flowdot` | **稳态·列车** | 主链路光点（粗 3.5） | 复制箭头为 `<path class="flowdot">`（同 d、stroke 用原箭头色或强调色），`pathLength="100"` + delay/duration；同链多枚错相位 = 列车 |
| `.flowtail` | **稳态·列车拖尾** | 与 flowdot 同 d 的宽淡拖尾 | 同 delay 同 duration |
| `.pulse` `.pulse-t` `.pulse-b` | **稳态·脉冲** | 英雄节点缩放+辉光（琥珀/深青/蓝），每图 1~4 个（v4.1 加密） | 包 `<g class="pulse" style="animation-delay:-1.4s">` |
| `.sweepband` | **稳态·语义扫光** | 对比列/新增标注区（禁整图扫，每图 ≤2 区） | 见 §4 配方 |
| `.dashgrow` | **稳态·链路生长** | 关键虚线路径持续生长回卷 | 加 class（可内联 duration 2~3.5s） |
| `.cellwave` | 稳态·行波 | 重复单元格/整行波 | 包 `<g class="cellwave" style="animation-delay:Xs">` |
| `.march` | 稳态·行进 | 虚线行进 | 加 class |
| `.breathe` | 稳态·辅助 | 次要强调，**不得作主要动效**（v1 教训：全图呼吸=看不出动画） | 包 g |
| `.step` | 稳态·步骤循环 | ①②③④ 步骤框 | delay 固定 0/-1.5/-3/-4.5s |

**数据密度硬指标（2026-10-29 用户定调）**：数据矩阵类图，**行 ≥ 20 且列 ≥ 6 视为数据密集——数据区（数值格/数据行/数据列）禁止一切弥漫性动效（逐格呼吸、整行行波、整列扫光）**，原因是行列多时呼吸严重影响读数体验；仅允许 ≤3 个语义强调点（关键行/关键值 pulse）与非数据 chrome（表头/图例/边框）动效。行或列低于阈值的低密度图，呼吸/行波照常（用户体验良好）。

**稳态硬指标（校验器强制）**：每图稳态 ≥2 个族。族 = 列车(flowdot/flowtail) / 脉冲(pulse*) / 扫光(sweepband) / 生长(dashgrow) / 行波(cellwave) / 步骤(step)。march、breathe 不计数。v1 的 `.chg` 低幅呼吸一律废除，由 pulse 变体 + cellwave/sweepband 取代。

**delay 规则**：一次性类（row/head/draw/fade）delay 0~2.2s；无限循环类允许负 delay = 相位偏移（|d| ≤ 周期）；同族必须错相位；**持续层 ≤4 族（含 march/breathe；v4.1 放宽，旧文 ≤3 以此为准——用户 2026-10-28 晚定调"呼吸辉光、慢速列车、行波、虚线生长感觉很棒，再进一步增加"）**。本站长表（49~51 行）入场用 0.03s/行递进；~~行波用 0.2s/行负相位（周期 = 行数×0.2s）~~（v4.2 密集清效废除，长表数据行零行波）；pulse 族 4 枚时相位 0/-0.7/-1.4/-2.1（0.7s 均布，周期 2.8s；密集图 ≤3 枚）；dashgrow 2.6~3.5s 慢档错相位；**列车元素级时长下限 2.4s（v4.2 全站降速）**。

## 4. 扫光带配方（sweepband 唯一合法实现）

1. `<defs>` 加 `<linearGradient id="sweepG-N" gradientUnits="userSpaceOnUse" x1="X0" y1="0" x2="X0+P" y2="0">`，stops：`0 →stop-color 透明`、`0.46 透明`、`0.5 rgba(#b45309,.30)`、`0.54 透明`、`1 透明`（P = 区域宽 + 240；N 用图内唯一序号）。
2. `<defs>` 加 `<clipPath id="sweepC-N">`，内放区域矩形副本。
3. 在区域内容**之下**、白底背景**之上**插入：
   `<g clip-path="url(#sweepC-N)"><rect class="sweepband" x="X0" y="Y" width="P" height="H" fill="url(#sweepG-N)" style="--sweepP:{P}px"/></g>`
4. `X0 = 区域左缘 − int(0.54×P)`：t=0 光带完整藏于区域左外侧，随 translateX(P) 从左到右扫过区域，8s 无缝循环。**注意**：本站扫光置于内容之下（canonical 分层），不透明填充格之上的部分被遮挡、在格间缝隙与空白带可见（POR 列 pill 行距 52px/pill 高 26px ≈ 一半露出；beat 右栏盒间 16px 横缝 + 90px 级纵缝）。

## 5. 入场编排（修 v2/v1 缺陷）

- 顺序铁律：**容器（面板/框）→ 内容（节点/文字）→ 箭头**。
- 箭头 `.draw` 的 delay ≥ max(两端面板 `.row` delay) + **0.55s**（0.35s 不够，0.8s 帧实测出现悬浮箭头）。
- 一次性入场总长 ≤2.5s；`.row` 按阅读顺序递进（面板图 0.1~0.15s 级、长表 0.03s/行）；尾部入场元素可用内联 duration 0.45~0.5s 压收尾。
- flowdot 不穿过任何盒内文字：短边（<60px）只放 1 包；宁缺勿穿。

## 6. 每张图的规格（本站实际实现；锚点行号以各生成器 assert 为准）

### 6.1 checksum_address_map（940×1764）【地址映射表 · 15 行 · v4.2 判定：非密集（15<20），行波照常】
行标签 x=170；0x02/0x0A 为 chip_sel=0/1 双行；图例在末行前。
- 行序：head 标题+位号列头(0) → 15 行 0.15 起 0.08s 递进（至 1.27）→ 图例 head(1.5)；总长 2.05s。
- **行波（主角）**：15 行整行组 cellwave，0.4s/行负相位，周期 6.0s = 地址扫描波。
- **脉冲 ×4**（v4.1 +1）：0x0A cs=1 `PWRC_P[1:0]` 单元格 pulse（琥珀 -0.7，1027v1 checksum 覆盖修复字节）；0x02 行组 pulse-b（蓝 -1.4，唯一 cs 对照行）；0x27 行组 pulse-t（深青 -2.1，frame end 边界）；**0x1F 行组 pulse（琥珀 0s，PWRC 控制字节双行 PWRC_P1..N3/CTRL+NB/NA/PB/PA）**。相位 0/-0.7/-1.4/-2.1 均布。
- 稳态 2 族（行波+脉冲）。

### 6.2 checksum_logic_flow（1240×900）【流程图 · 无 v1 生成器，v4 新建 · v4.2：非矩阵，仅列车降速】
四段式（①拍选择 ②累加锁存 ③比较防护 ④提交门控）+ 底部 1027v1-B 修复面板 + 图例；源 defs 3 个 marker。
- 行序：标题(0) → ①(0.15)+8 拍盒(0.25 起 0.07s) → ②(0.55)+2 盒(0.70/0.78) → ③(0.90)+3 盒(1.00/1.08/1.18) → ④(1.25)+4 盒(1.28/1.34/1.40/1.44) → 修复面板(1.60) → 图例(1.72)。
- **draw（实线）**：A1 xdata_a↓ 1.30 / A2 帧尾锁存 1.35 / A3 ↓ 1.55 / A5 →match_eff 1.75 / A10 1.90(0.5s) / A11 琥珀 2.00(0.45s，收尾 2.45s)；箭头旁标签随箭头同拍 fade。**虚线 A4/A6/A7/A8/A9 用 .fade**（保源 dasharray 5,3，A8/A9 内联 0.45s）。
- **列车（稳态主角；v4.1 每链 +1 包；v4.2 全站降速）**：A2 3 包+拖尾(3.2s)、A5 3 包+拖尾(3.4s)、A1/A3/A10 各 2 包(2.4s)——teal #0e7490 主数据流；A11 2 包琥珀 #b45309（unmatch→unlock 支路，2.4s）；全部在箭头 fade 组内、同链错相位（负相位偏移不变 = 同链间距不变、纯降速）。
- **脉冲 ×3**：5'h04 修复盒+◆ pulse(-0.7)；update_en_a 提交门 pulse-b(-1.4)；match_eff_a 判决盒 pulse-t(-2.1)。
- **行波 ×6**：① 段 6 个实线拍盒（5'h01/02/03/0A/0B/0E）0.55s/盒负相位、4.2s 周期 = 参与字节逐拍扫描；5'h04 用 pulse、gap 虚线盒不参与。
- **虚线生长 ×5**（v4.1 新增）：②③④ 区虚线控制连接 A4(2.8s,-0.4s)/A6(3.0s,-1.2s)/A7(2.6s,-0.8s)/A8(3.2s,-1.9s)/A9(3.2s,-2.7s) 打 `.dashgrow` 持续生长回卷；外层 fade 入场保留。
- 稳态 4 族（v4.1，≤4 上限内）。

### 6.3 chip_sel0_register_map（1100×2842）【寄存器映射表 · 49 行 · v4.2 判定：密集（49≥20 且列≥6）】
行标签 x=158；每行 = 标签 + POR pill（rect+circle+text @x842）+ 位格；波段行（0x09~0x1C 等 3 行）无 pill。
- 行序：head 标题+位号列+POR 表头(0) → 49 行 0.15 起 0.03s（至 1.59）→ 图例 head(1.8)；总长 2.35s。
- **v4.2 删除**：49 行整行 cellwave 行波（原 0.2s/行、周期 9.8s）与 POR 默认值列 sweepband 扫光（含 defs 渐变/clipPath）——数据区零弥漫动效。
- **脉冲 ×2 保留**（≤3）：0x1D `khead_20b_sel[4:0]` 单元格 pulse（琥珀 -0.7，1027v1 变更格）；**0x30 行组 TEST_PRTCT[7:0]（密码/受保护行；cs=0 无 ★ 回拼行）pulse-t（深青 -1.4）**。
- **chrome 呼吸 ×1**（v4.2 第二族补足，唯一许可方式）：图例+脚注组 cellwave（kit 原幅 2.6s）。
- 稳态 2 族（脉冲+chrome 行波）。

### 6.4 chip_sel1_register_map（1100×2946）【寄存器映射表 · 51 行 · v4.2 判定：密集（51≥20 且列≥6）】
同 6.3 布局；0x09/0x0A 为 ★ 回拼行（LC_REG_MAPPING 回拼）。
- 行序：head(0) → 51 行 0.15 起 0.03s（至 1.65）→ 图例 head(1.85)；总长 2.4s。
- **v4.2 删除**：51 行整行 cellwave 行波（原周期 10.2s）与 POR 列 sweepband 扫光（含 defs）。
- **脉冲 ×3**（v4.1 为 ×4，≤3 上限 → 删 0x30 行脉冲，该行语义由 chip_sel0 图承担）：0x1D `khead_20b_sel[4:0]` pulse（琥珀 -0.7）；**0x0A 行组**（PWRC ★ 回拼行）pulse-b（蓝 -1.4，整行组）；**0x09 行组**（SR_NF/NR/PF/PR ★ 回拼行）pulse-t（深青 -2.1）。
- **chrome 呼吸 ×1**（v4.2 第二族补足）：图例+脚注组 cellwave（kit 原幅 2.6s）。
- 稳态 2 族（脉冲+chrome 行波）。

### 6.5 config_data_beat_regroup_0721（1240×848）【拍重组图 · v4.2 判定：非密集（列 4~5<6），行波照常】
双栏（左 0716 2B/拍 13 盒、右 0721 3B/拍 9 盒）× 区域 A~D + 中缝线 + 底部绿/橙两汇总框；源无 defs（扫光 defs 为 v4 新增）。
- 行序：标题+副标题 head(0) → 图例色块 head(0.15) → 列头+中缝 head(0.3) → 26 行（区域标签+拍盒）0.45 起 0.05s（至 1.70）→ 绿框(1.75)/橙框(1.85)；总长 2.4s。
- **行波（主角）**：22 个拍盒 cellwave——左栏 13 盒按拍序 0.35s/盒负相位（4.55s 周期），右栏 9 盒同参数整体相位 +0.175s = **两列波半拍错位**（分组变、节拍推进）。
- **脉冲 ×3**（v4.1 +1）：绿框「XOR 总量不变」pulse-t(-2.1)；橙框「过渡依赖」pulse(-0.7)；**右栏 3'h2 拍行**（43/44/-- 灰格 = CHPI_CONFIG_L0 未升 24bit 的过渡依赖证据行）pulse-b(-1.4)。本图源无虚线元素，不引入 dashgrow（宁缺勿造）。
- **语义扫光 ×1**：右栏（0721 新分组侧）x[648,1224] 区域（P=816，8s）。
- 稳态 3 族。

### 6.6 lsi_unprotected_address_map（1198×2894）【地址映射表 · 50 行 · v4.2 判定：密集（50≥20 且列≥6）】
行标签 x=158；红=受保护、绿=不受保护、紫=密码 0x30、灰虚线=整行 Reserved。
- 行序：head 标题+双副标题+位号列头(0) → 50 行 0.15 起 0.03s（至 1.62）→ 图例 head(1.85)；总长 2.4s。
- **v4.2 删除**：50 行整行 cellwave 行波（原周期 10.0s）——数据区零弥漫动效（本图无扫光列）。
- **脉冲 ×3**（v4.1 为 ×4，≤3 上限 → 删 0x38 行脉冲，reset 图仍强调该行）：0x1D `khead_20b_sel[4:0]` pulse（琥珀 -0.7）；**0x30 密码寄存器行**（TEST_PRTCT，紫行）pulse-t(-2.1)；**0x20 行**（受保护域起点，PWRC_TSEL/TESTO_EN_OPT/R_TESTO_SEL 测试字段入口）pulse（琥珀 0s）。
- **虚线生长 ×1 保留**（非弥漫类单元素强调）：0x09~0x1C 整行 Reserved 带行虚线边框 dashgrow（3.0s，-0.5s）。
- 稳态 2 族（脉冲+生长；已有两族，无需 chrome 呼吸补足）。

### 6.7 reset_domain_address_map（866×2956）【地址映射表 · 51 行 · v4.2 判定：密集（51≥20 且列≥6）】
行标签 x=158（含 0x0B~0x1C、0x31~0x32、0x44~0x8F 波段行）；淡蓝=N_RST_NLOCK、橙=N_RST、绿=RSTN_SCR_EN。
- 行序：head(0) → 51 行 0.15 起 0.03s（至 1.65）→ 图例 head(1.85)；总长 2.4s。
- **v4.2 删除**：51 行整行 cellwave 行波（原周期 10.2s）——数据区零弥漫动效（本图无扫光列）。
- **脉冲 ×3 保留**（≤3 上限内，v4.1 配置原样）：0x1D `khead_20b_sel[4:0]` pulse（琥珀 -0.7）；**0x30 行**（TEST_PRTCT，N_RST 复位域少数橙行）pulse-t(-2.1)；**0x38 行**（0827v1 新增 reg_eol，密码行之外的次关键行）pulse-b(-1.4)。
- **虚线生长 ×1 保留**（非弥漫类单元素强调）：0x0B~0x1C 整行 Reserved 带行虚线边框 dashgrow（3.0s，-1.2s）。
- 稳态 2 族（脉冲+生长；已有两族，无需 chrome 呼吸补足）。

## 7. 生成器要求

- 结构：读源 SVG 全文 → 按行解析 → text 内容+坐标定位锚点（assert 保护）→ 组装输出（**含源 defs（若有）+ 背景 rect**）→ 写文件。
- 输出 `<style>` 行 = §2 kit 逐字（不增删类）；扫光图的 defs 新增项只含渐变+clipPath。
- 幂等：只依赖源 SVG；重跑字节一致（md5 验证）。文件尾：`# ymzhu 2026-10-28 <HH:MM>`。
- 长表锚点通式：行标签 = `<text x=... font-weight="600">0x...`；图例 = text 内容「图例」；单元格三连 = rect+label text+value text。

## 8. 校验（交付门）

```
python images/anim/validate_kit_v4.py <name1> [name2 ...]
```
全 PASS 才算完成。另加人工检查（写进报告）：源 SVG 无改动（mtime/内容未动）；一次性总长 ≤2.5s；持续族 ≤4（v4.1）；同族相位错开；flowdot 不穿文字。

## 9. 报告格式（DONE 消息）

```
DONE — <name1> / <name2> ...
每张图：静态/动画/生成器路径与字节数；校验 PASS 列表；
稳态族清单（行波 N 行/脉冲 N/扫光 N/列车 N 包/生长 N/步骤 N）；
入场时间线（row 顺序与 delay、箭头 delay）；caveats。
```

## 10. Changelog

- **v4.1（2026-10-28 晚，动效加密）**：用户定调"呼吸辉光、慢速列车、行波、虚线生长感觉很棒，再进一步增加"——**持续层族上限 ≤3 放宽为 ≤4（§3/§8 同步）**。checksum_logic_flow：②③④ 区虚线控制连接 A4/A6/A7/A8/A9 升级 `.dashgrow`（2.6~3.2s 错相位，4 族满配）+ 列车每链 +1 包（8→14 包）。脉冲加密：checksum_address_map +0x1F PWRC 双行（×4）、chip_sel0 +0x30 TEST_PRTCT（×2）、chip_sel1 +0x09 ★ 回拼/+0x30（×4）、beat +右栏 3'h2 过渡依赖证据行（×3，源无虚线故不引 dashgrow）、lsi +0x20 受保护域起点行（×4）、reset +0x38 reg_eol 行（×3）；lsi/reset 另各 +1 条 dashgrow（0x09~0x1C / 0x0B~0x1C Reserved 带行虚线边框，升至 3 族）。pulse 4 枚相位 0/-0.7/-1.4/-2.1 均布。所有新元素只给既有几何打标签（新 flowdot 复制既有箭头 d），生成器幂等重跑 md5 一致。
- **v4（2026-10-28，本站升级）**：7 张图全部升级 Motion Kit v4——废除 v1 低幅呼吸（.chg），换行波 cellwave（地址扫描波/拍序波/两列半拍错位波）+ pulse 辉光脉冲（khead 变更格/PWRC_P 修复字节/密码行 0x30/回拼行/汇总框）+ sweepband 语义扫光（POR 默认值列×2、beat 右栏）；流程图（checksum_logic_flow）新建 v4 生成器：draw 入场（虚线保 dasharray 用 fade）+ 主数据流 flowdot 列车 + 三色脉冲 + 拍盒行波；生成器全部重写为零依赖幂等脚本；新增 validate_kit_v4.py（ROOT/SITE 按 images/anim 布局自动推导）。
- v1（2026-10-26/27）：首版动画（rowIn 级联 + .chg 低幅呼吸 233 处；用户判定效果不明显，已全量废除）。
- v4.2（2026-10-29）：用户定调"所有带列车的图，列车速度全部再降"——元素级列车时长下限 2.4s（0.7/0.8s→2.4s、1.4/1.5s→3.2s 档）；列车仍只允许复制既有箭头几何，不扩新图；donut 永不加行进（用户点名）。
- v4.2 补充（2026-10-29）：数据密集图（行≥20 且列≥6）数据区禁弥漫性动效（用户：行列多加呼吸影响体验；低密度加很好）；列车全站再降速（元素级 ≥2.4s）。落地：chip_sel0/chip_sel1/lsi/reset 四图删全部数据行 cellwave 行波（chip 两图另删 POR 列 sweepband 含 defs）；脉冲压至 ≤3（chip_sel1 删 0x30、lsi 删 0x38，语义由邻图承担）；chip 两图以图例+脚注 chrome cellwave 补第二族，lsi/reset 靠 pulse+dashgrow 两族；checksum_logic_flow 列车 1.2s→2.4s、1.5s→3.2s、1.6s→3.4s（相位不变）。checksum_address_map（15 行）/beat（列<6）低于阈值不动。
