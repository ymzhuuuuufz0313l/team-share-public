# Motion Kit v4.1 — 电影感纯 CSS in-SVG 动效规范（2026-10-28 定稿；当晚动效加密轮升 v4.1）

> v4 取代 v2（v2 全文见 git 历史）。上位架构 = `blueprint-ui-style` skill「动画/静态双版 SVG 站点架构（v4）」章。
> 用户对 v2 的两条判定：①稳态动效不明显（低幅 opacity 呼吸看不出动画）；②入场 0.8s 帧"箭头悬浮在空白面板上"。
> v4 方向：**稳态肉眼可辨（列车/脉冲/扫光/生长）+ 入场先容器后内容再箭头 + 不要怕炫技**。
> 本文件是 10 张图 v4 升级的唯一事实源；每个子代理只负责分给自己的图。

## 0. 铁律（不变量，违反即 FAIL）

1. **源 SVG 一律只读**。输出只写 `images/anim/<name>.svg`；生成器只写 `images/tools/make_anim_<name>.py`。
2. **数据/几何/颜色零改动**：`<text>` 多重集与源图完全一致；`<svg>` 开标签（width/height/viewBox）与源图完全一致；所有 rect/text/line/path 的坐标、尺寸、fill、stroke、stroke-width、stroke-dasharray 原样保留。
3. **纯 CSS in-SVG**：不允许 `<script`、不允许 SMIL `<animate>`、不允许外部资源。新增允许项：`class` 属性、`pathLength` 属性、`style` 内联（animation-delay/duration/opacity 初值/CSS 变量）、`<style>` 块（kit CSS）、复制箭头得到的装饰路径（`.flowdot`/`.flowtail`）、**v4 新增：`<defs>` 内渐变 + `<clipPath>`（仅扫光带用）**。
4. **生成器必须保留源图 `<defs>`（marker-end 箭头依赖）与背景 rect**（v2.1 回归教训：漏带 defs → 箭头端丢失）。组装段用 assert 保护。
5. **保留源图第 2 行既有字体 `<style>`**；v4 kit `<style>` 是独立的下一行。
6. **reduced-motion 安全**：kit CSS 自带媒体块，原样保留。
7. 生成器**确定性、幂等**：只读源 SVG，重跑输出字节一致；零第三方依赖；`python`（3.13）运行。
8. 生成器文件尾签名：`# ymzhu 2026-10-28 <HH:MM>`。
9. 不动其他图的文件、**不动任何 HTML**（引用 bump 由主代理统一做）、不建临时目录。

## 1. 路径

- 源 SVG（只读）：`E:\project\team-share-public\hk1v11-longcode-420b-verification\images\<name>.svg`
- 输出：`...\hk1v11-longcode-420b-verification\images\anim\<name>.svg`
- 生成器：`...\images\tools\make_anim_<name>.py`
- v2 生成器已存在：**先读它**理解结构锚点（哪些行是面板/盒子/箭头），然后整体重写为 v4（v2 的类名/delay 逻辑不要照抄，稳态选型按 §6 的新规格）。

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
| `.draw` | 入场 | 实线箭头描边生长 | 元素加 `class="draw" pathLength="100"` + delay |
| `.fade` | 入场 | 虚线/次要元素淡入 | 加 class + delay |
| `.flowdot` | **稳态·列车** | 主链路光点（粗 3.5） | 复制箭头为 `<path class="flowdot">`（同 d、stroke 用原箭头色或强调色），`pathLength="100"` + delay/duration；同链多枚错相位 = 列车 |
| `.flowtail` | **稳态·列车拖尾** | 与 flowdot 同 d 的宽淡拖尾 | 同 delay 同 duration |
| `.pulse` `.pulse-t` `.pulse-b` | **稳态·脉冲** | 英雄节点缩放+辉光（琥珀/深青/蓝），每图 1~3 个 | 包 `<g class="pulse" style="animation-delay:-1.4s">` |
| `.sweepband` | **稳态·文字光带**（v4.3 起；原"语义扫光"琥珀色带已废除） | 关键文字（标题/标注区/结论文字），每图 ≤2 区 | 见 §4 配方 |
| `.dashgrow` | **稳态·链路生长** | 关键虚线路径持续生长回卷 | 加 class（可内联 duration 2~3.5s） |
| `.cellwave` | 稳态·行波 | 重复单元格波 | 包 `<g class="cellwave" style="animation-delay:Xs">` |
| `.march` | 稳态·行进 | 虚线行进 | 加 class |
| `.breathe` | 稳态·辅助 | 次要强调，**不得作主要动效** | 包 g |
| `.step` | 稳态·步骤循环 / 接力点亮 | ①②③④ 步骤框；**短箭头链路的方框接力**（v4.3） | 步骤框 delay 固定 0/-1.5/-3/-4.5s；接力点亮按流向逐盒 +1s |

**短箭头规则（v4.3，2026-11-02 用户定调）**：可见长度 < 80px 的箭头**不挂** flowdot / flowtail / march / dashgrow——短线上的流点只剩一团闪烁（8b10b 对比图 16px spine 实测"很丑"）。改用 `.step` **方框接力点亮**表达流向：沿链路的方框按顺序逐个点亮（stepLit 6s 周期、亮约 1s，相邻盒 delay +1s；双列对照图另一列整体 +0.5s）。

**数据密度硬指标（2026-10-29 用户定调）**：数据矩阵类图，**行 ≥ 20 且列 ≥ 6 视为数据密集——数据区（数值格/数据行/数据列）禁止一切弥漫性动效（逐格呼吸、整行行波、整列扫光）**，原因是行列多时呼吸严重影响读数体验；仅允许 ≤3 个语义强调点（关键行/关键值 pulse）与非数据 chrome（表头/图例/边框）动效。行或列低于阈值的低密度图，呼吸/行波照常（用户体验良好）。

**稳态硬指标（校验器强制）**：每图稳态 ≥2 个族。族 = 列车(flowdot/flowtail) / 脉冲(pulse*) / 扫光(sweepband) / 生长(dashgrow) / 行波(cellwave) / 步骤(step)。march、breathe 不计数。v2 里 glow-* 一律由 pulse 变体取代（glow-b→pulse-b、glow-g→pulse-t、glow-o→pulse）。

**delay 规则**：一次性类（row/head/draw/fade）delay 0~2.2s；无限循环类允许负 delay = 相位偏移（|d| ≤ 周期）；同族必须错相位；持续层 ≤4 族（含 march/breathe；v4.1 起，v4 曾为 ≤3——2026-10-28 晚"动效加密"轮放宽，用户定调：呼吸辉光/慢速列车/行波/虚线生长很棒，再进一步增加）。

## 4. 文字光带配方（sweepband 唯一合法实现；v4.3 起取代琥珀扫光带）

> 2026-11-02 用户定调："琥珀色扫光带很丑，不如标题那种光带——SVG 里面用光带，而不是扫光。"
> 光带 = 首页 hero 标题同款技法：**光只出现在文字字形内**，白色亮峰滑过，文字被短暂提亮；不再是一整块色带擦过面板。

1. **给目标文字加 id**：区域内要发光的每个 `<text>` 加 `id="shT{k}"`（**只加属性，文字内容零改动** → text 多重集校验不变）。注意：生成器里给 `<text ` 插 id 用普通字符串替换，**不要用含 `\1`/`\b` 的正则替换串**——工具链会吞反斜杠，`\b` 变退格符导致静默不匹配（2026-11-02 实测）。
2. `<defs>` 加 `<linearGradient id="sweepG-N" gradientUnits="userSpaceOnUse" x1="X0" y1="0" x2="X0+P" y2="0">`，stops **全部白色** `#ffffff`：`0 → 0`、`0.40 → 0`、`0.46 → .3`、`0.5 → .65`、`0.54 → .3`、`0.60 → 0`、`1 → 0`（stop-opacity）。P = 区域宽 + 240；**X0 = 区域左 − 0.60P**（t=0 光带右缘恰在区域左缘）。峰值 .65 是上限：再高会把浅底上的深色字"洗白"到不可读。
3. `<defs>` 加 `<clipPath id="sweepC-N">`，内容 = 对目标文字的引用 `<use href="#shT0"/><use href="#shT1"/>…`（**不复制文字**；Edge/Chrome 实测 `<use>` 引用 `<text>` 作裁剪有效）。
4. 在**全部内容之上**（不是之下）插入，并包 `.fade`（delay = 目标区入场 delay）：
   `<g class="fade" style="animation-delay:Ds"><g clip-path="url(#sweepC-N)"><rect class="sweepband" x="X0" y="Y" width="P" height="H" fill="url(#sweepG-N)" style="--sweepP:{P}px"/></g></g>`
5. 效果：白色光带每 8s 从左到右滑过目标文字一次。rect 覆盖完整扫掠轨迹（x=X0 起、宽 P）；可见范围由文字字形裁剪决定。一个 clipPath 可同时引用多处文字（如标题 + 底部注释），光带同步滑过。
6. **颜色铁律**：亮峰只能白 / 冷白；**禁止红棕 / 琥珀色亮带**（琥珀只做基底色，不做光）。
7. **验证方法（重要）**：无头截图（`--virtual-time-budget`）对合成层 `transform` 动画取帧**不可靠**，光带常截不到——验证时在诊断副本末尾注入
   `<script>addEventListener("load",function(){document.getAnimations().forEach(function(a){a.pause();a.currentTime=T;});});</script>`
   定格到指定毫秒再截图（诊断副本不入库）。光带中心位置 x(t) = X0 + 0.5P + P·t/8。

## 5. 入场编排（修 v2 缺陷）

- 顺序铁律：**容器（面板/框）→ 内容（节点/文字）→ 箭头**。
- 箭头 `.draw` 的 delay ≥ max(两端面板 `.row` delay) + **0.55s**（v2 用 +0.35s 不够，0.8s 帧实测出现悬浮箭头）。
- 一次性入场总长 ≤2.5s；`.row` 按阅读顺序 0.15~0.4s 递进。
- flowdot 不穿过任何盒内文字：某边太短/贴盒 → 改 stroke-width 2.5 或放弃该边，宁缺勿穿（v2 人工规则保留）。

## 6. 每张图的规格（只读自己负责的；锚点沿 v2 实测，稳态选型为 v4 新定；【v4.1】标记 = 2026-10-28 晚动效加密增量）

### 6.1 longcode_verification_architecture（1200×980）【A】
六面板：Test/Config（顶）、TX（中左）、RX（中右）、Transaction/Driver（下左）、接收端离线验证路径（底，绿虚线）、版本管理（底条）。
- 行序：标题(0) → Test/Config(0.15) → TX(0.4) → RX(0.6) → Transaction(0.8) → 离线 band(1.15) → 版本条(1.5)。
- draw：Test/Config→TX/RX ↓、TX 内部链箭头、driver→RX、RX 内部 4 ↓、离线链路箭头。delay = max(两端面板 delay)+0.55。
- **列车（稳态主角）**：蓝链 TX→RX（build_bit_stream→pad→long_encoding→CHPI_KCODE_ALIGN + RX 内部链）每边 2 包 + flowtail，0.7s/边，按边序错 phase；绿链离线（long_rt_tap_debug→…→report）每边 3 包【v4.1，2→3 更明显"列车"】、duration ×2（慢速支路对比）。
- **脉冲**：TAP 徽章 pulse-b；✅ verdict 盒 pulse-t。
- dashgrow：紫色虚线"期望值/比对"连接器。
- cellwave（可选）：TX 面板 K2/K3/K4 chip；不好剥离就跳过。

### 6.2 pydec_tx_rx_structure（1200×680）【A】
TX 面板（左 3 模块+dump 盒）、RX 面板（右 TAP 盒+虚线 RTL 盒+3 绿脚本盒）、离线比对 band（底）。
- 行序：标题(0) → TX(0.2) → RX(0.45) → 离线 band(0.85)。
- draw：TX 内部 2 ↓、K 码对齐蓝边、RX→脚本 3 箭头、离线链 2 箭头（delay 遵 §5）。
- **列车**：绿脚本链 3 边（2 包 + flowtail，0.7s）；蓝 K 码对齐边 2 包。
- **脉冲**：TAP 徽章 pulse-b；✅ verdict pulse-t。
- **光带**（v4.3）：离线比对区全部文字（标题 + 3 盒文字 + 期望值/实际值标签，共 10 个 `<text>`）文字光带 1 处。
- **布局修正**（v4.3，改静态源）：离线比对区三盒原间距不对称（左 105px / 右仅 15px，"实际值"箭头与标签压在中盒上）→ 三盒等距重排：左 84–344、中 441–781、右 878–1128（两侧连线落点 x=214 / 1003 不变），两条箭头各约 97px。
- breathe（1 辅助）："dout_24b + 2-bit valid" 盒。
- 【v4.1】生长 dashgrow（第 4 族）：紫"期望值"链 2 条虚线（dump↓ 3.2s/-1.6s、rawbyte→report 期望值 2.8s/-0.5s）+ RTL 虚线盒边（3.0s/-1.0s）由 march 升级为 dashgrow；"实际值"连线为实线（draw），dashgrow 会把实线伪造成虚线 → 不动。march 辅助缩减为灰"传统路径"、绿 lane0↓。

### 6.3 8b10b_vs_420b_architecture（1400×1210）【A】
双列（左 8B/10B、右 420B）堆叠模块盒 + spine 箭头；底部对比/verdict 区。
- 行序：标题(0) → 左列盒自上而下(0.15 起 0.12s 递增) → 右列盒(0.3 起) → 底部对比/verdict(1.4)。
- draw：两列 spine 箭头逐段、横向对比箭头（delay ≥ 列盒+0.55）。
- **接力点亮**（v4.3，取代列车）：spine 箭头每段仅 16px（< 80px 短箭头规则）→ 删除双列流点列车；两列方框按流向逐盒 `.step` 点亮（左列阶段 k：delay 1.6+k s；右列整体 +0.5s；右列 ref model 与 transaction 同阶段）。
- ~~列车（双列赛跑）~~：v4.3 删除。
- cellwave：两列 bit 单元格自上而下行波（0.07s/格【v4.1，0.1→0.07 加密；源图两列各恰 5 chip、已是全部 bit 格】）。
- **脉冲**：编码效率/编码率盒、verdict 盒选 2~3 个（pulse / pulse-t 错相位）。
- 不加 breathe。

### 6.4 spec_frame_flow（1200×700）【A】
Clock training 条、LSP 条、Config Line(Frame c)、Video Active 4 行、Frame c+1 行、V blanking 2 行、省略号。
- 行序：标题(0) → Clock(0.15) → LSP(0.35) → Frame c(0.55) → Active 4 行(0.7/0.85/1.0/1.15) → c+1(1.3) → VBK(1.45/1.6) → 括号(1.75)。
- **行波（主角）**：所有"行"整行组包 cellwave，自上而下 0.18s 递增，周期 4.5s（内联 duration）= 帧滚动波。
- **脉冲**："Config Line · Frame c+1"行盒 pulse-t（0717 修复点）；LSP 条 pulse-b；【v4.1】Clock training 条 pulse-b(-2.1s，与 LSP 错 0.7s)、V blanking 两行组 pulse-t(-1.4s，两行同 delay 同步，与既有 pulse-t 错 0.7s)。
- 不加列车/breathe/sweep（行波+脉冲已 2 族、画面已密）。

### 6.5 spec_tag_replacement（1200×460）【B】
输入 413b 行、↓替换箭头（全0/全1 红格）、输出 420b 行（黄 tag 格）、A→B 发送顺序箭头、图例、①②③④ 步骤框。
- 行序：标题(0) → 输入行(0.2) → 输出行(0.55) → A→B(0.85) → 图例(0.9) → ①~④(1.1/1.25/1.4/1.55)。
- draw：输入→输出蓝 ↓；A→B 箭头（≥0.55 规则）。
- step：4 框（0/-1.5/-3/-4.5s）。
- **列车**：A→B 箭头 3 包+每包 flowtail【v4.1，2→3，1.6s 整周期均布】（1.6s）。
- **行波**：输出行全部单元格左→右（0.1s/格，3.4s）。
- **脉冲**：全0/全1 两个红格 pulse（琥珀，phase 差 1.4s）。
- march：header 位虚线（若有）。

### 6.6 spec_scramble_rolling（1200×520）【B】
编码前行、↓箭头、编码后行（K5~K8 黄格）、3 条横条（绿 SCR_KEY/橙 SCR_XOR/蓝 ENC）+ 绿虚线 LFSR 反馈环、n+1 行、图例。
- 行序：标题(0) → 编码前(0.2) → 编码后(0.5) → 三横条(0.85/0.95/1.05) → n+1(1.25) → 图例(1.4)。
- draw：↓箭头；三横条 `.draw`+`pathLength="100"` 依次绘出（0.55s，0.1s 错开）。
- **生长（主角）**：LFSR 绿色虚线反馈环 `.dashgrow`（2.6s）—— key 逐轮演化的语义。
- **列车**：绿条 2 包、蓝条 2 包+拖尾（【v4.1】各 1→2；左→右错 phase，白点骑实心条上为已验收样式，tail 用链色）。
- 行波：编码后行 K5~K8 黄格+末尾 K5（0.3s 递增，2.4s）。
- **脉冲**："n → n+1（LFSR 继承）"注释 pulse-t。

### 6.7 spec_dummy_70b（1200×600）【B】
顶部 ①②③④ 步骤框（3 蓝箭头串联）、3 行（LSP/Active/Config：Before ENC 盒 → 箭头 → After ENC 盒）、底部注释。
- 行序：标题(0) → ①(0.15) ②(0.3) ③(0.45) ④(0.6) → LSP(0.9) → Active(1.05) → Config(1.2) → 注释(1.4)。
- draw：3 pipeline 箭头 + 3 行 Before→After 箭头。
- step：4 框循环。
- **列车：已废除**（2026-11-02 拍板，PAGE_FX §3-2 短箭头规则：< 80px 不挂列车）——原 3 pipeline 箭头 3 包+flowtail 与 3 行箭头各 2 包全删，箭头保留 draw 入场后静止；流向由 ①②③④ `.step` 方框接力表达。kit CSS 仍逐字嵌入（类定义保留、无实例）。
- 行波：After ENC 盒 D 格（D·70b×N / D·140b / Dmy）+ K5~K8（0.3s 递增，2.8s）。
- **脉冲**：Active 行 "D·70b×N" 盒 pulse。
- **光带**（v4.3）：大标题「非 413b 整数倍数据处理」+ 底部 70-bit 对齐注释两行文字光带（同一 clipPath，光带同步滑过）。原底部注释区琥珀扫光已废除。
- 稳态族现状：cellwave / pulse / sweepband / step = 4 族（列车族删除后回到 ≤4 上限内）。

### 6.8 spec_bit_order（1200×560）【C】
三列 bit 网格（R0/G0/B0[7..0]）、左侧竖直蓝↑"发送顺序"（Bit0→Bit7）、byte 标签、↓串行化、Case1 条带（24 格）、时间轴箭头。
- 行序：标题(0) → 网格(0.3) → 发送顺序箭头(0.6) → byte 标签(0.7) → 串行化(0.9) → Case1(1.05) → 时间轴(1.5)。
- draw：竖直↑、串行化↓、时间轴→。
- **列车**：竖直↑箭头 3 包+每包 flowtail【v4.1，2→3；源图无虚线 → dashgrow 跳过】（向上走=Bit0→Bit7）；时间轴→ 2 包。
- **行波（LSB 演出主角）**：Case1 条带 24 格左→右 0.08s/格（2.9s）= 逐 bit 发送；三列网格按列波（R/G/B phase 0/1/2s，3.6s）。
- **脉冲**：R0[0] 格 pulse-b（"Bit0 最先发出"英雄）。

### 6.9 spec_lsp_kcode（1200×620）【C】
编码前行（K2+0xEA~0xED 橙格+K3）、括号下划线、编码后行（含 dmy）、dmy 注释、K 码表 4 行、先发/后发箭头+"右→左"注释。
- 行序：标题(0) → 编码前(0.2) → 括号(0.5) → 编码后(0.65) → dmy 注释(0.8) → K 表(1.0/1.15/1.3/1.45) → 先发/后发(1.7)。
- draw：先发/后发 2 箭头；实线下划线。
- **行波**：编码前后两行 0xEA~0xED 橙格左右行进（0.1s/格，两行同相）；K 表 4 行按行 phase（0.5s 递增，3.6s）。
- **列车**：先发/后发箭头各 3 包（【v4.1】2→3，按标注方向走）+flowtail。
- **脉冲**：编码前行 K3 格 pulse-b；K 表 K3 行 pulse-b（phase 差 1.4s）。
- march：虚线括号下划线。

### 6.10 spec_blanking_idle（1200×660）【C】
IDLE pattern 面板（K5~K8 4 行）、lane 间轮换面板（Lane1~4）、V blanking 行、Config Line 行、VBP 首行、注释。
- 行序：标题(0) → IDLE 面板(0.2) → lane 面板(0.5) → V blanking(0.85) → Config(1.05) → VBP(1.25) → 注释(1.45)。
- **行波（轮换演出主角）**：每 lane 的 4 个 K 格按轮换序点亮（Lane1 K5→K6→K7→K8；Lane2 K6→…；Lane3 K7→…；Lane4 K8→…）：每格 `class="cellwave"` + 内联 `animation-duration:2.4s`，delay = 轮换序位置 × 0.6s，4 lane 共用时间线 = 轮换偏移可视化。IDLE 面板 bit 串格 0.4s 递增（3.2s）。
- ~~列车~~：~~每 lane 格间小箭头各 1 包~~ **2026-11-02 更正：实际生成物中无任何 flowdot/flowtail（CSS 类定义存在但未实例化，图只有行波 + 脉冲两族，稳定多年）；且格间小箭头 < 80px，按 v4.3 短箭头规则本就不应挂列车——维持无列车现状，此行留作不回归说明**。
- **脉冲**：VBP 首行行盒 pulse-b；【v4.1】IDLE pattern 面板标题组 pulse-b(-2.1s，与 VBP 错 0.7s)。

## 7. 生成器要求

- 结构：读源 SVG 全文 → 按行解析 → text 内容+坐标定位锚点（assert 保护）→ 组装输出（**含源 defs/背景 rect**）→ 写文件。
- 输出 `<style>` 行 = §2 kit 逐字（不增删类）。
- 幂等：只依赖源 SVG；重跑字节一致。文件尾：`# ymzhu 2026-10-28 <HH:MM>`。

## 8. 校验（交付门）

```
python images/tools/validate_kit_v4.py <name1> [name2 ...]
```
全 PASS 才算完成。另加人工检查（写进报告）：源 SVG 无改动（git status 源图无 M）；一次性总长 ≤2.5s；持续族 ≤4（spec_dummy_70b 列车族已按 §3-2 短箭头规则删除，现存 cellwave/pulse/sweepband/step = 4 族，不许再加新族）；相位错开；flowdot 不穿文字。

## 9. 报告格式（DONE 消息）

```
DONE — <name1> / <name2> ...
每张图：输出+生成器路径与字节数；校验 PASS 列表；
稳态族清单（列车 N 包/脉冲 N/扫光 N/生长 N/行波 N 格/步骤 N）；
入场时间线（row 顺序与 delay、箭头 delay）；caveats。
```

## 10. Changelog

- **v4.3（2026-11-02）**：①**琥珀扫光带 → 文字光带**（§4 重写：光只在文字字形内、白色亮峰 .65、叠在内容之上；`<use>` 引用原文字作裁剪，零复制）。**本条覆盖 v4.1 的"禁白色亮色 / 禁新 sweep"**——白色只允许用于文字光带亮峰。②**短箭头规则**（< 80px 不挂列车/行进/生长，改方框接力点亮）。③pydec 离线比对区三盒等距重排（改静态源）。④8b10b 删除 spine 列车改接力点亮；dummy_70b 光带改作用于标题+注释。⑤验证方法：transform 动画须用 `getAnimations()` 定格截图（无头 virtual-time 截图不可靠）。
- v4.1（2026-10-28 晚）：**动效加密轮**（用户定调："呼吸辉光、慢速列车、行波、虚线生长很棒，再进一步增加"）。持续层族上限 ≤3 → **≤4**（§3/§8 同步）；只用四族（pulse*/cellwave/flowdot+flowtail/dashgrow），禁新几何/禁 scale/禁白色亮色/禁新 sweep；各图增量——longcode 绿链 3 包、pydec 紫期望值链+RTL 盒边 dashgrow（第 4 族）、8b10b 行波 0.07s/格+spine 3 包、frame_flow +Clock pulse-b/VBK 两行组 pulse-t、blanking +IDLE 标题组 pulse-b、tag A→B 3 包、scramble 绿/蓝条各 2 包、dummy_70b pipeline 3 包（存量 5 族只加密不加族）、bit_order 竖直列车 3 包（无虚线跳 dashgrow）、lsp_kcode 先发/后发各 3 包。
- v4（2026-10-28）：稳态升级（pulse 缩放辉光/扫光带/列车加粗+拖尾/dashgrow），glow-* 废除由 pulse* 取代；入场箭头 delay 规则 +0.35→+0.55 修悬浮箭头；稳态 ≥2 族硬指标；kit CSS 全量替换；校验升级 validate_kit_v4.py。
- v2.1（2026-10-27）：生成器漏带源 defs/背景 rect 回归修复；无限循环类负 delay 澄清。
- v2（2026-10-27）：首版 kit（rowIn/drawIn/flowdot/cellwave/glow/step）。
- v4.2（2026-10-29）：用户定调"所有带列车的图，列车速度全部再降"——元素级列车时长下限 2.4s（0.7/0.8s→2.4s、1.4/1.5s→3.2s 档）；列车仍只允许复制既有箭头几何，不扩新图；donut 永不加行进（用户点名）。
- v4.2 补充（2026-10-29）：数据密集图（行≥20 且列≥6）数据区禁弥漫性动效（用户：行列多加呼吸影响体验；低密度加很好）；列车全站再降速（元素级 ≥2.4s）。

<!-- ymzhu 2026-11-04 17:20 -->
