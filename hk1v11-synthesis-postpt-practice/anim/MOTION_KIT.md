# Motion Kit v4（本站 v4.1 二轮加密）— 电影感纯 CSS in-SVG 动效规范（hk1v11-synthesis-postpt-practice 站，2026-10-28）

> 本文件由 canonical 站 `hk1v11-longcode-420b-verification/anim/MOTION_KIT.md`（v4）复制而来；
> §1 路径与 §6 分图规格已替换为本站实际（6 张图，双 anim 目录），§0/§2/§3/§4/§5 与 canonical 逐字一致。
> 上位架构 = `blueprint-ui-style` skill「动画/静态双版 SVG 站点架构（v4）」章。
> v4 方向：**稳态肉眼可辨（列车/脉冲/扫光/行波）+ 入场先容器后内容再箭头 + 不要怕炫技**（用户 2026-10-28 定调，取代 v2"温和呼吸"）。
> 本文件是本站 6 张图动效的唯一事实源。

## 0. 铁律（不变量，违反即 FAIL）

1. **源 SVG 一律只读**。输出只写 `anim/<name>.svg` 或 `images/anim/<name>.svg`；生成器只写对应 anim 目录内 `make_anim_<name>.py`。
2. **数据/几何/颜色零改动**：`<text>` 多重集与源图完全一致；`<svg>` 开标签（width/height/viewBox）与源图完全一致；所有 rect/text/line/path 的坐标、尺寸、fill、stroke、stroke-width、stroke-dasharray 原样保留。
3. **纯 CSS in-SVG**：不允许 `<script`、不允许 SMIL `<animate>`、不允许外部资源。新增允许项：`class` 属性、`pathLength` 属性、`style` 内联（animation-delay/duration/opacity 初值/CSS 变量）、`<style>` 块（kit CSS）、复制既有线段得到的装饰路径（`.flowdot`/`.flowtail`）、`<defs>` 内渐变 + `<clipPath>`（仅扫光带用）。
4. **生成器必须保留源图 `<defs>`（marker/clip/filter 依赖）与背景 rect**。组装段用 assert 保护。
5. **保留源图既有字体 `<style>`**；v4 kit `<style>` 是独立的下一行。**例外（仅一处）**：源样式内残留的 `animation:` 声明若与 kit keyframes 同名（本站实测：power_module_compare 的 `.hdr{...animation:sweepMove 6s...}`），必须在输出中删除该声明——不删则网格/图例整体平移 160px。同类惰性残留（breathe/tl/rg*/pl/cellB/diag/wash/glowPulse/tickBreathe/rowBreathe/numGlow 等无同名 keyframes 者）原样保留即可。
6. **reduced-motion 安全**：kit CSS 自带媒体块，原样保留（源图自带媒体块也保留，双保险）。
7. 生成器**确定性、幂等**：只读源 SVG，重跑输出字节一致；零第三方依赖；`python`（3.13）运行。
8. 生成器文件尾签名：`# ymzhu 2026-10-28 <HH:MM>`。
9. 不动其他图的文件、**不动任何 HTML**（引用 bump 由主代理统一做）、不建临时目录、不删任何现有文件。

## 1. 路径（本站双 anim 目录）

- 功耗类 3 张：源 = `<site>\<name>.svg`（只读）→ 输出/生成器 = `<site>\anim\<name>.svg`、`<site>\anim\make_anim_<name>.py`
  - `power_compare_hk11` / `power_composition_donut_1v11_1v22` / `power_module_compare_1v11_1v22`
- 表格类 3 张：源 = `<site>\images\<name>.svg`（只读）→ 输出/生成器 = `<site>\images\anim\<name>.svg`、`<site>\images\anim\make_anim_<name>.py`
  - `dc_area_evolution_table` / `dc_gen_summary_table` / `delay_skew_14vs12`
- 校验：`python anim/validate_kit_v4.py <name...>`（双目录自动解析，见 §8）。
- 本站静态版是"剥离动画"产物：样式块留有大量空规则与 opacity=0 辅助元素（tl/rg1-3/pulseU/nGlow/tL 等），一律**原样保留、不激活**；唯一例外见 §6.6 rowB。

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

**fade/row 禁忌（本站实测新增）**：`.fade`/`.row`/`.head` 终值强制 `opacity:1`——凡自身 opacity ≠1 的元素（属性或源 CSS 类，如 donut 的 `.sweep{opacity:.08}` 白环）**禁止直接加这三个类**，必须包外壳 `<g class="fade">`（父 1 × 子原值 = 原值）。

## 3. 类语义、硬指标与 delay 规则

| 类 | 层 | 用在哪 | 打标签方式 |
|---|---|---|---|
| `.row`/`.head` | 入场 | 面板/行/标题一次性入场 | 包 `<g class="row" style="animation-delay:Xs">`（或在既有 g 的 class 上并入） |
| `.draw` | 入场 | 实线箭头描边生长 | 元素加 `class="draw" pathLength="100"` + delay；**delay>0 时必须外包同 delay 的 `.fade`**（否则延迟期全程可见） |
| `.fade` | 入场 | 虚线/次要元素淡入 | 加 class + delay |
| `.flowdot` | **稳态·列车** | 主链路光点（粗 3.5） | 装饰 path（沿线复制），`pathLength="100"` + delay/duration；同链多枚错相位 = 列车 |
| `.flowtail` | **稳态·列车拖尾** | 与 flowdot 同 d 的宽淡拖尾 | 同 delay 同 duration |
| `.pulse` `.pulse-t` `.pulse-b` | **稳态·脉冲** | 英雄节点缩放+辉光（琥珀/深青/蓝），每图 1~3 个 | 包 `<g class="pulse" style="animation-delay:-1.4s">` |
| `.sweepband` | **稳态·语义扫光** | 对比列/关键行/量程区（禁整图扫，每图 ≤2 区） | 见 §4 配方 |
| `.dashgrow` | **稳态·链路生长** | 关键虚线路径持续生长回卷 | 加 class（可内联 duration 2~3.5s） |
| `.cellwave` | 稳态·行波 | 重复行/单元格波 | 包 `<g class="cellwave" style="animation-delay:Xs">` |
| `.march` | 稳态·行进 | 虚线行进（**仅 dash 周期整除 16 的虚线**，否则循环跳变） | 加 class |
| `.breathe` | 稳态·辅助 | 次要强调，**不得作主要动效** | 包 g |
| `.step` | 稳态·步骤循环 | ①②③④ 步骤框 | delay 固定 0/-1.5/-3/-4.5s |

**数据密度硬指标（2026-10-29 用户定调）**：数据矩阵类图，**行 ≥ 20 且列 ≥ 6 视为数据密集——数据区（数值格/数据行/数据列）禁止一切弥漫性动效（逐格呼吸、整行行波、整列扫光）**，原因是行列多时呼吸严重影响读数体验；仅允许 ≤3 个语义强调点（关键行/关键值 pulse）与非数据 chrome（表头/图例/边框）动效。行或列低于阈值的低密度图，呼吸/行波照常（用户体验良好）。

**稳态硬指标（校验器强制）**：每图稳态 ≥2 个族。族 = 列车(flowdot/flowtail) / 脉冲(pulse*) / 扫光(sweepband) / 生长(dashgrow) / 行波(cellwave) / 步骤(step)。march、breathe 不计数。

**delay 规则**：一次性类（row/head/draw/fade）delay 0~2.2s；无限循环类允许负 delay = 相位偏移（|d| ≤ 周期）；同族必须错相位；**持续层 ≤4 族（含 march/breathe；2026-10-28 晚二轮加密由 ≤3 放宽）**。

**入场 vs 稳态同类冲突（本站实测新增）**：同一元素不得同时挂入场类与稳态类（两条 `animation:` 声明级联只留后者）——需要两者时用嵌套：外层 `.row/.fade`、内层 `.pulse/.cellwave`。

## 4. 扫光带配方（sweepband 唯一合法实现）

1. `<defs>` 加 `<linearGradient id="sweepG-N" gradientUnits="userSpaceOnUse" x1="X0" y1="0" x2="X0+P" y2="0">`，stops：`0 透明`、`0.46 透明`、`0.5 #b45309 透明度 .3`、`0.54 透明`、`1 透明`（P = 区域宽 + 240；N 用图内唯一序号）。
2. `<defs>` 加 `<clipPath id="sweepC-N">`，内放区域矩形副本。
3. 在区域内容**之下**、面板底色**之上**插入：
   `<g clip-path="url(#sweepC-N)"><rect class="sweepband" x="X0" y="Y" width="P" height="H" fill="url(#sweepG-N)" style="--sweepP:{P}px"/></g>`
4. 效果：琥珀光带每 8s 从左到右扫过区域一次。注意：区域若含**实心底色 rect**（表格行底色），扫光带必须插在该 rect 之后、行文字之前（行组内部），否则被盖住。

## 5. 入场编排

- 顺序铁律：**容器（面板/框）→ 内容（节点/文字/条）→ 箭头**。
- 箭头 `.draw` 的 delay ≥ max(两端面板 `.row` delay) + **0.55s**。
- 一次性入场总长 ≤2.5s；`.row` 按阅读顺序 0.1~0.4s 递进。
- flowdot 不穿过任何文字；贴文字的边宁缺勿穿。

## 6. 每张图的规格（本站事实源）

### 6.1 power_compare_hk11（605×444，功耗柱状对比表）→ anim/
- 入场：表头组 head(0)；数据行 r0~r16 row，0.15s 起 0.09s 递进（末 1.59）；每行数值条簇（bar+峰值三角+dot；r12 为 徽章+条组+dot）再包内层 row(+0.12，末 1.71+0.55=2.26s)；网格 fade(0.05)。
- 稳态（v4.1）：cellwave——组头标签 5 处（1015 组 0s / 1027 组 1.2s）+ 数值条簇 17 行（4s，delay -0.1n/行自上而下递增，pulse 簇嵌波内）；pulse ×3——r12 峰值 37.9 簇 pulse(-0.5s)、r10 pulse-b(-1.9s)、r16 pulse-b(-2.6s)。sweepband 已按用户验收整体移除；底部色带无箭头线，不设 dashgrow。
- 源遗留（静态外观保留、不激活）：breath/breath2/cmpband/zeband/peakglow/dot 类。

### 6.2 power_composition_donut_1v11_1v22（1200×578，双环形图）→ anim/
- 入场：标题 head(0)、副标题 head(0.1)、图例行 ×2 row(0.2/0.35)、环面板 row(0.5/0.75)；扇区 circle 依次 fade（左 9 个 0.65+0.07k、右 7 个 0.9+0.07k；扇区 stroke-dasharray 是弧线几何，**禁 .draw**）；标签组 fade（1.3+0.05k / 1.45+0.05k）；中心 fade(1.7/1.75)。末 2.35s。
- 稳态（v4.1；**donut 永不加行进列车**——用户点名移除过，加密只用呼吸系）：cellwave——图例 top-3 行 ×2 侧（左 0/0.6/1.2s，右 1.3/1.9/2.5s）+ 扇区环向慢波 14 个（左 8 delay -0.3k、右 6 delay -(1.9+0.3k) 半周期跨侧错拍；3.8s 周期 ≠ 图例 2.6s 永不锁相，相位即环向顺序 0.3s/扇区递增）；pulse ×2——左 top1（短编码解码 41.8%）pulse-t(-0.7s)、右 top1（LC_CSPIF_L0 35.4%）pulse(-2.1s)。
- 白色扫光环（源 .sweep opacity .08）fade 走外壳包装（§2 禁忌）。

### 6.3 power_module_compare_1v11_1v22（1200×688，双条横向柱状图）→ anim/
- 源样式中和：`.hdr` 的 `animation:sweepMove 6s linear infinite` 删除（kit 同名 keyframes 致网格/图例平移，§0.5 例外）。
- 入场：标题 head(0)、网格 fade(0.05)、模块名 fade(0.1)、11 组双条块 row 0.3+0.1i（末 1.3+0.55=1.85s）、glow 矩形 fade(1.5/1.55)、图例 head(1.65)、基线条 fade(1.7)。
- 稳态（v4.1）：cellwave——模块名故事行 3 处（g0 0s / g9 0.6s / g10 1.2s）+ 柱对行波 11 组（bar rect 组逐组包，4s，delay -0.15i/组递增；数值文本不入波；0 值系列源图单条也入波）；pulse ×2——g0 峰值对（10294/8590）pulse-t(-0.9s)、g9 rx_phy 1V22 独有条（4196）pulse(-2.3s)，pulse 壳在 cellwave 外。sweepband 已按用户验收整体移除；基线轴为实线（无数值虚线），不设 dashgrow。

### 6.4 dc_area_evolution_table（2743×1009，DC 三代面积演进表）→ images/anim/
- 入场：表头 head(0)、网格 fade(0.05)、r1/r2/r3 row(0.2/0.5/0.8)、脚注块 fade(1.1)。末 1.7s。
- 稳态（v4.1）：cellwave 按格 ×15——三代行各 5 单元格逐格包（行间基相 0/-1.2/-2.4，行内 0.25s/格递增，3.6s）＝行内自左向右 + 跨行自上而下二维慢波；行底色/rg/br/diag 不入波；sweepband ×1——r3 当代行（y488..618，P=2983），插在行底色后/行文字前；pulse ×3——r2 "+4.0%"(-0.7s)、r3 "+6.7%"(-2.1s)（pl1/pl2 组类并入）、r3 面积峰值 "314707" 琥珀(-1.4s)。

### 6.5 dc_gen_summary_table（3928×489，DC 三代总览表）→ images/anim/
- 入场：表头 head(0)、网格 fade(0.05)、r1/r2/r3 row(0.25/0.55/0.85)。末 1.4s。
- 稳态（v4.1）：cellwave 按格 ×15（同 6.4：行间基相 0/-1.2/-2.4，行内 0.25s/格，3.6s）；sweepband ×1——r3 结果行（y396..489，P=4168）；pulse ×3——r2 最差代 "452 条/-1.45ns" pulse(-1.4s)、r3 收敛 "11 条/-0.01ns" pulse-t(-0.7s)、r2 最差代面积 "294907" 琥珀(-2.1s)。

### 6.6 delay_skew_14vs12（1440×950，STA skew 三面板）→ images/anim/
- 入场：页眉 kicker head(0)/标题 head(0.05)/图例 row(0.15)；面板① row(0.2)：注解框 fade(0.25~0.6)、六支量测箭头 draw（0.8/0.95/1.0/1.1/1.25/1.45，全部 ≥0.2+0.55）、端帽/标签 fade(1.45~1.75)；面板② row(0.5)：轴/表头 fade(0.85~0.95)、阈值线对 fade(1.0)、三行场景 row(1.1/1.25/1.4)、结论 fade(1.55)；面板③ row(0.8)：包络带 fade(1.15/1.2)、阈值对 fade(1.3)、两支标记箭头 draw(1.45/1.55)、徽章框 head(1.7)；页脚 fade(1.75)、铭牌 head(1.8)。末 2.35s。
- 稳态（v4.1，4 族=新上限）：列车——①时钟 arrival 边（#1c2530，phase 0/-0.75）+数据 arrival 边（#0e7490，phase -0.4/-1.15）各 2 包+拖尾 1.5s/趟（维持不动）；pulse ×3——①slack 绿线组 pulse-t(-0.7s)、②12/14 阈值线对 pulse-b(-2.1s)、③STATUS 行 pulse(-1.4s)；sweepband ×1——②场景表三行区（x60..680/y660..788，P=860）；dashgrow ×6——6 条 12/14 阈值虚线并入 `.march .dashgrow` 双类 + 行内 `animation-name:dashgrow` 钉死（kit CSS 中 .march 声明晚于 .dashgrow，不钉死会级联回 march -16 跳变），3.0s、文档序 0/-0.4/-0.8/-1.2/-1.6/-2.0s 错相位，虚线生长表达阈值推进。
- 源样式处理 ×2（assert 保护）：上述 6 条阈值虚线（v4 曾行内 `animation:none` 中和，v4.1 起改为 dashgrow 生长）；rowB 行洗矩形静态剥离版漏带 opacity（渲染为实心琥珀盖表）→ 动画版恢复 `style="opacity:.08"`（静态版不动，待上游修）。

## 7. 生成器要求

- 结构：读源 SVG 全文 → 按行解析 → 内容+坐标定位锚点（assert 保护）→ 组装输出（含源 defs/背景 rect）→ 写文件。
- 输出 `<style>` 行 = §2 kit 逐字（不增删类）。
- 幂等：只依赖源 SVG；重跑字节一致。文件尾：`# ymzhu 2026-10-28 <HH:MM>`。
- 源含尾注释（`</svg>` 后 `<!-- ... -->`）或行尾无换行等差异由生成器自适应（eol 探测 + 尾保留）。

## 8. 校验（交付门）

```
python anim/validate_kit_v4.py power_compare_hk11 power_composition_donut_1v11_1v22 power_module_compare_1v11_1v22 dc_area_evolution_table dc_gen_summary_table delay_skew_14vs12
```

全 PASS 才算完成（本站版自动解析 anim/ 与 images/anim/ 双目录及其静态对照）。人工检查项：源 SVG 零改动；一次性总长 ≤2.5s；持续族 ≤4；同族错相位；flowdot 不穿文字；同元素无入场/稳态类冲突；opacity≠1 元素不直接挂 fade/row/head。

## 9. 报告格式（DONE 消息）

```
DONE — <name1> / <name2> ...
每张图：输出+生成器路径与字节数；校验 PASS 列表；
稳态族清单（列车 N 包/脉冲 N/扫光 N/生长 N/行波 N 格/步骤 N）；
入场时间线（row 顺序与 delay、箭头 delay）；caveats。
```

## 10. Changelog

- **v4.1（2026-10-28 晚，本站二轮"动效加密"）**：用户定调"呼吸辉光、慢速列车、行波、虚线生长感觉很棒，再进一步增加"——持续层族上限 ≤3 → **≤4**（§3/§8 同步）；六图加密：donut 扇区环向呼吸波（14 扇区 cellwave，3.8s，0.3s/扇区环向递增，永不加列车）；hk11 数值条簇行波（17 行 cellwave，4s，-0.1s/行）；module_compare 柱对行波（11 组 bar rect cellwave，4s，-0.15s/组）；dc_area/dc_gen 行波细化到单元格（每行 5 格 cellwave，行内 0.25s/格 + 行间 0/-1.2/-2.4 基相）各 +1 最差代琥珀 pulse（"314707"/"294907"）；delay_skew 6 条阈值虚线由 animation:none 中和改为 dashgrow 生长（3.0s，0.4s 递进，行内钉死 animation-name 防 .march 级联回退）。同族全部错相位；慢档 wave 3.6–4s；静态源零改动。
- **v4（2026-10-28，本站升级）**：6 张图旧动效（低幅呼吸/单元格错峰/扫光带不明显）整体升级为 Motion Kit v4——稳态 ≥2 族硬指标（列车/脉冲/扫光/行波）、入场先容器后内容再箭头（箭头 delay ≥ 面板+0.55s）、扫光带按 §4 语义配方重做；全部改为确定性生成器产出（`make_anim_*.py`）；新增本站版 `validate_kit_v4.py`（双 anim 目录解析）。本文件 §0/§2/§3/§4/§5 自 canonical 站 v4 逐字继承，§1/§6 为本站实际（v4.1 起 §3 上限为本站放宽值）。
- v4 canonical（2026-10-28，longcode 站）：稳态升级（pulse 缩放辉光/扫光带/列车加粗+拖尾/dashgrow）；入场箭头 delay +0.35→+0.55；稳态 ≥2 族硬指标；kit CSS 全量替换；校验 validate_kit_v4.py。
- 旧版（2026-10-27 前，本站 v1-v3 动效）：fadeIn/grow/breathe 词汇表 + 面板 panelIn + 行扫光，已由 v4 全量取代（旧 anim svg 被生成器输出覆盖，无历史文件保留义务）。

<!-- ymzhu 2026-10-28 21:22 -->
- v4.2（2026-10-29）：用户定调"所有带列车的图，列车速度全部再降"——元素级列车时长下限 2.4s（0.7/0.8s→2.4s、1.4/1.5s→3.2s 档）；列车仍只允许复制既有箭头几何，不扩新图；donut 永不加行进（用户点名）。
- v4.2 补充（2026-10-29）：数据密集图（行≥20 且列≥6）数据区禁弥漫性动效（用户：行列多加呼吸影响体验；低密度加很好）；列车全站再降速（元素级 ≥2.4s）。
