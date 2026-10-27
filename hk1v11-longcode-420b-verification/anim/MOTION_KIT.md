# Motion Kit v2 — 大胆但有序的纯 CSS in-SVG 动效规范

> 任务：把 v1（只有少量 flowdot + breathe）升级为 v2：入场编排 + 箭头自绘 + 数据列车 + 单元格行波 + 英雄辉光 + 步骤循环 + 虚线行进。
> 本文件是 10 张图动画升级的**唯一事实源**。每个子代理只负责分配给自己的 2~3 张图。

## 0. 铁律（不变量，违反即 FAIL）

1. **源 SVG 一律只读**。输出只写 `anim/<name>.svg`；生成器只写 `anim/make_anim_<name>.py`。
2. **数据/几何/颜色零改动**：`<text>` 多重集与源图完全一致；`<svg>` 开标签（width/height/viewBox）与源图完全一致；所有 rect/text/line/path 的坐标、尺寸、fill、stroke、stroke-width、stroke-dasharray 原样保留。
3. **纯 CSS in-SVG**：不允许 `<script`、不允许外部资源、不允许 JS。新增的只有：`class` 属性、`pathLength` 属性、`style` 内联（仅 animation-delay / animation-duration / opacity 初始值）、`<style>` 块（motion kit）、复制出来的 `<path class="flowdot">` 装饰路径。
4. **保留源图第 2 行的既有字体 `<style>`**（行号 2），新增的 motion `<style>` 是独立一行（行号 3）。
5. **reduced-motion 安全**：媒体块必须原样使用 kit 里给定的那段（含 `.row,.head,.fade,.fademarch{opacity:1!important}` 与 `.flowdot{display:none!important}`）。
6. 生成器必须**确定性、幂等**：只读源 SVG，重跑输出字节一致；无第三方依赖；用 `python`（3.14）运行。
7. 生成器文件尾签名：`# ymzhu 2026-10-27 <HH:MM>`（用你实际完成时刻）。
8. 不要动 `anim/` 里其他图的文件、不要动任何 HTML、不要建 .preview/.pagecheck 等临时目录（渲染由主代理统一做）。

## 1. 路径

- 源 SVG：`E:\project\team-share-public\hk1v11-longcode-420b-verification\<name>.svg`
- 输出：`E:\project\team-share-public\hk1v11-longcode-420b-verification\anim\<name>.svg`
- 生成器：`E:\project\team-share-public\hk1v11-longcode-420b-verification\anim\make_anim_<name>.py`
- v1 生成器已存在（同名文件）：**先读它**理解结构锚点（哪些行是面板/盒子/箭头），然后**整体重写**为 v2（v1 的逐边 keyframes 逻辑被统一 `flow` keyframe 取代，不要照抄）。

## 2. Motion Kit CSS（逐字嵌入生成器，作为新增 `<style>` 行的内容）

```
<style>
.row{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
.head{opacity:0;animation:rowIn .5s cubic-bezier(.22,.7,.3,1) forwards}
@keyframes rowIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
.draw{stroke-dasharray:100;animation:drawIn .55s ease-out forwards}
@keyframes drawIn{from{stroke-dashoffset:100}to{stroke-dashoffset:0}}
.fade{opacity:0;animation:fadeIn .6s ease forwards}
@keyframes fadeIn{to{opacity:1}}
.fademarch{opacity:0;animation:fadeIn .6s ease forwards,march 1.8s linear infinite}
.breathe{animation:br 3.2s ease-in-out infinite}
@keyframes br{0%,100%{opacity:1}50%{opacity:.55}}
.cellwave{animation:wave 3s ease-in-out infinite}
@keyframes wave{0%,100%{opacity:1}50%{opacity:.68}}
.march{animation:march 1.8s linear infinite}
@keyframes march{to{stroke-dashoffset:-16}}
.flowdot{fill:none;stroke-linecap:round;stroke-dasharray:12 88;animation:flow 2s linear infinite}
@keyframes flow{to{stroke-dashoffset:-100}}
.glow-b{animation:glowB 2.8s ease-in-out infinite}
@keyframes glowB{0%,100%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}50%{filter:drop-shadow(0 0 6px rgba(37,99,235,.85))}}
.glow-g{animation:glowG 2.8s ease-in-out infinite}
@keyframes glowG{0%,100%{filter:drop-shadow(0 0 0 rgba(22,163,74,0))}50%{filter:drop-shadow(0 0 6px rgba(22,163,74,.85))}}
.glow-o{animation:glowO 2.8s ease-in-out infinite}
@keyframes glowO{0%,100%{filter:drop-shadow(0 0 0 rgba(217,119,6,0))}50%{filter:drop-shadow(0 0 6px rgba(217,119,6,.85))}}
.step{animation:stepLit 6s ease-in-out infinite}
@keyframes stepLit{0%,16%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}24%,92%{filter:drop-shadow(0 0 0 rgba(37,99,235,0))}100%{filter:drop-shadow(0 0 7px rgba(37,99,235,.9))}}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.row,.head,.fade,.fademarch{opacity:1!important}.flowdot{display:none!important}}
</style>
```

## 3. 用法（类语义 + 打标签方法）

| 类 | 用在哪 | 打标签方式 |
|---|---|---|
| `.row` / `.head` | 一次性的"行/面板"入场组 | 把该行所有元素包进 `<g class="row" style="animation-delay:0.4s">…</g>`；标题/副标题/底部注释用 `.head` |
| `.draw` | **实线**箭头（`<line>`/`<path>`/`<polyline>`，有 stroke、通常带 marker-end） | 元素上加 `class="draw" pathLength="100"` + `style="animation-delay:Xs"`（X = 源面板 delay + 0.35s） |
| `.fade` / `.fademarch` | **虚线**连接器 / 虚线边框盒（虚线不能用 draw，dash 图案会被 dasharray:100 覆盖） | 加 `class="fade"`（或 `.fademarch` 要持续行进）+ `style="animation-delay:Xs"` |
| `.flowdot` | 流动数据包 | **复制**箭头元素为 `<path class="flowdot">`（保留 d/坐标、stroke 用原箭头颜色或提亮、stroke-width 2.5），加 `pathLength="100"` + `style="animation-duration:0.7s;animation-delay:0.2s"`。周期=走完全边时间；同链多边形错 delay 形成"列车" |
| `.cellwave` | 重复单元格的行进波 | 每个单元格（rect+text 组）包 `<g class="cellwave" style="animation-delay:Xs">`；X 按波传播方向递增（0.08~0.3s/格）；周期 3s（可内联改 animation-duration） |
| `.breathe` | 单个英雄节点呼吸 | 包 `<g class="breathe">`（±可选 delay） |
| `.glow-b/g/o` | 英雄辉光（每图 ≤3 个） | 包 `<g class="glow-b" style="animation-delay:1.4s">` |
| `.step` | ①②③④ 步骤循环（6s 周期） | 每个步骤框组加 `class="step"`，delay 分别 0 / -1.5 / -3 / -4.5s（负值=相位） |

**pathLength 技巧**：`pathLength="100"` 归一化路径长度，`.draw` 与 `.flowdot` 因此共用一个 keyframe，与边的实际长度无关。对多段折线路径同样有效（整条链一次画出/一次走完）。

**相位编排原则**（不混乱的关键）：
- 一次性效果总时长 ≤2.5s，之后才进入"持续层"；
- 每张图持续层 ≤3 个"族"（列车/行波/辉光/步骤/行进）；
- 同族元素必须**相位错开**（行进波、列车），禁止全体同相闪烁；
- 行波幅度 kit 已定（0.68），不要加大；辉光 drop-shadow ≤7px。

**delay 规则**（v2.1 澄清）：
- 一次性类（.row/.head/.draw/.fade）delay 必须 0~3s；
- 无限循环类（.breathe/.cellwave/.march/.flowdot/.glow-*/.step）允许**负 delay = 相位偏移**（|d| ≤ 该动画周期），如两个同族辉光错相位用 `-1.4s`；.step 固定 0/-1.5/-3/-4.5s。

## 4. 每张图的规格（只读自己负责的）

### 4.1 longcode_verification_architecture（1200×980）
六面板：Test/Config（顶）、发送端 TX（中左）、接收端 RX（中右）、Transaction/Driver（下左）、接收端离线验证路径（底，绿虚线框）、版本管理（底条）。
- 行序（重排 v1 的 delay，分组不变）：标题(0) → Test/Config(0.15) → TX(0.4) → Transaction(0.8) → RX(0.6) → 离线 band(1.15) → 版本条(1.5)。
- draw：所有实线箭头（Test/Config→TX/RX 的↓、TX 内部链条箭头、driver→RX、K 码对齐蓝色边、RX 内部 4 个↓、离线链路 3~4 个箭头）。delay=源面板 delay+0.35。
- fademarch：紫色虚线"期望值/比对"连接器；绿色虚线离线边框盒；其余虚线连接器（fade）。
- flow 列车：(a) 蓝链 TX→RX：build_bit_stream→pad_bit_stream→long_encoding→CHPI_KCODE_ALIGN 各边 + RX 内部 long_decoding_top.v→decoder_7b.v→desramble_7b.v→dout 各边，每边 2 包、周期 0.7s、按边序错 phase（0.15s 递增）；(b) 绿链离线：long_rt_tap_debug.sv→long_rt_dap_lane0.md→decode_dap.py→long_pydec_lane0.md→report 每边 2 包。
- glow（2）：TAP 徽章（glow-b）；✅ verdict 盒（glow-g）。
- cellwave（可选）：TX 面板里的 K2/K3/K4 小 chip（0.4s 递增）；不好剥离就跳过。

### 4.2 pydec_tx_rx_structure（1200×680）
TX 面板（左，3 模块+dump 盒）、RX 面板（右，TAP 盒+虚线 RTL 盒+3 绿脚本盒）、离线比对 band（底）。
- 行序：标题(0) → TX(0.2) → RX(0.45) → 离线 band(0.85)。
- draw：TX 内部 2 个↓、K 码对齐蓝色边（CHPI 帧对齐那条）、RX→脚本 3 个箭头、离线链 2 个箭头（rawbyte→report、lane0→report）。
- fademarch：虚线"RTL 解码链（不看·不依赖）"盒；fademarch：紫色虚线期望值连接器、虚线实测值连接器。
- flow：绿脚本链 3 边（2 包列车，0.7s）；蓝 K 码对齐边 2 包。
- glow（2）：TAP 徽章（glow-b）；✅ verdict 盒（glow-g）。
- breathe（1）："dout_24b + 2-bit valid" 盒。

### 4.3 8b10b_vs_420b_architecture（1400×1210）
双列：左 8B/10B、右 420B，每列堆叠模块盒 + 5 段 spine 箭头；底部对比/verdict 区。
- 行序：标题(0) → 左列盒自上而下(0.15 起，0.12s 递增) → 右列盒(0.3 起，0.12s 递增) → 底部对比/verdict(1.4)。
- draw：两列所有 spine 箭头（逐段，0.1s 递增）、横向对比箭头。
- flow：左列 spine 链（5 边，2 包列车，0.7s）；右列 spine 链同参数但整体 phase 偏移 0.35s → 双列"赛跑"。
- cellwave：两列的 bit 单元格（左列 8b/10b 单元格、右列 420b bit 单元格）——每列自上而下行波（0.1s/格，3.2s 周期）。单元格是 rect+text 组，逐个包 `<g class="cellwave">`。
- march：若有虚线边框盒 → `.march`。
- glow（≤3）：语义上的"结果"盒（如编码效率/编码率盒、verdict 盒），自选 2~3 个，glow-b/g。
- 不要加 breathe（行波已覆盖）。

### 4.4 spec_tag_replacement（1200×460）
输入 413b 行、↓替换箭头（全0/全1 红格）、输出 420b 行（黄 tag 格）、A→B"发送顺序"箭头、图例（右，3 项）、①②③④ 步骤框（底）。
- 行序：标题(0) → 输入行(0.2) → 输出行(0.55) → A→B 箭头(0.85) → 图例(0.9) → ①(1.1) ②(1.25) ③(1.4) ④(1.55)。
- draw：输入→输出蓝色↓箭头；A→B 箭头。
- step：4 个步骤框（delay 0 / -1.5 / -3 / -4.5s）。
- flow：A→B 箭头 2 包（1.6s 周期）。
- cellwave：输出行全部单元格从左到右行进波（0.1s/格，3.4s 周期）。
- glow（2）：两个红色全0/全1 格（glow-o，phase 差 1.4s）。

### 4.5 spec_scramble_rolling（1200×520）
编码前 行、↓编码后 箭头、编码后 行（含 K5~K8 黄格）、3 条横条（绿 SCR_KEY / 橙 SCR_XOR / 蓝 413/420 ENC）+ 绿色虚线 LFSR 反馈环、n+1 行、图例（3 项）。
- 行序：标题(0) → 编码前(0.2) → 编码后(0.5) → 三条横条(0.85/0.95/1.05) → n+1 行(1.25) → 图例(1.4)。
- draw：编码前→编码后 ↓箭头；三条横条用 `.draw`+`pathLength="100"` 依次绘出（0.55s，错 0.1s）。
- march：绿色虚线 LFSR 反馈环（`.march`，持续）。
- flow：绿条 1 包、蓝条 1 包（左→右，错 phase）。
- cellwave：编码后 行 K5~K8 黄格 + 末尾 K5（0.3s 递增，2.4s 周期）。
- glow（1）："n 行截止状态 → n+1 行起始状态（LFSR 继承）"注释（glow-g）。

### 4.6 spec_bit_order（1200×560）
三列 bit 网格（R0[7..0]/G0[7..0]/B0[7..0]）、左侧竖直蓝色"发送顺序"↑箭头（Bit0→Bit7）、byte0>>byte1>>byte2 标签、↓串行化 箭头、Case1 条带（24 格 R0[0..7] B0[0..7] G0[0..7]）、底部时间轴箭头。
- 行序：标题(0) → 网格(0.3) → 发送顺序箭头(0.6) → byte 标签(0.7) → 串行化箭头(0.9) → Case1 条带(1.05) → 时间轴(1.5)。
- draw：竖直发送顺序箭头、串行化 ↓箭头、时间轴箭头。
- flow：竖直发送顺序箭头 2 包（**向上**走 = Bit0→Bit7）；时间轴箭头 2 包（向右）。
- cellwave：Case1 条带 24 格从左到右（0.08s/格，2.9s 周期）→ 演示 LSB-first 逐 bit 发送；三列网格按列波（R 列 0 / G 列 1s / B 列 2s phase，3.6s 周期，幅度用 kit 默认）。
- glow（1）：R0[0] 格（glow-b，"Bit0 最先发出"英雄）。

### 4.7 spec_dummy_70b（1200×600）
顶部 ①②③④ 步骤框（3 个蓝箭头串联）、3 行（LSP/Active Line/Config Line：左标签 + Before ENC 橙框盒 + 箭头(413b/420b) + After ENC 盒）、底部注释。
- 行序：标题(0) → ①(0.15) ②(0.3) ③(0.45) ④(0.6) → LSP 行(0.9) → Active 行(1.05) → Config 行(1.2) → 注释(1.4)。
- draw：3 个 pipeline 箭头、3 个 Before→After 行箭头。
- step：4 个步骤框（6s 循环，delay 0 / -1.5 / -3 / -4.5s）。
- flow：3 个 pipeline 箭头（2 包列车，错 phase）；3 个行箭头（各 2 包，错 phase）。
- cellwave：After ENC 盒里的 D 格（"D · 70b×N"、"D · 140b"、"Dmy"）+ K5~K8 格（0.3s 递增，2.8s 周期）。
- glow（1）：Active 行 "D · 70b×N" 盒（glow-o）。

### 4.8 spec_frame_flow（1200×700）
Clock training 条、LSP 条（绿）、Config Line（Frame c 配置）行、Video Active 4 行（带左括号）、Config Line · Frame c+1 行（绿高亮框）、V blanking 2 行（VBK dummy line，带左括号）、……省略。
- 行序：标题(0) → Clock 条(0.15) → LSP 条(0.35) → Frame c 行(0.55) → Active 4 行(0.7/0.85/1.0/1.15) → c+1 行(1.3) → VBK 2 行(1.45/1.6) → 括号+省略(1.75)。
- cellwave（本图主角）：**帧滚动波**——所有"行"（Frame c、4 个 Active、c+1、2 个 VBK）整行组包 `<g class="cellwave">`，自上而下 delay 0.18s 递增，周期 4.5s（内联 animation-duration）。
- glow（2）："Config Line · Frame c+1 配置"行盒（glow-g，0717 修复点）；LSP 条（glow-b）。
- 不加 flow/breathe（行波已是主角）。

### 4.9 spec_lsp_kcode（1200×620）
编码前 行（K2 + 0xEA~0xED 橙格 + … + K3）、"0xEA/EA/EB/EC/ED × 8 = 32 Byte" 括号下划线、编码后 行（含 dmy 格）、"编码后末尾补 dmy — 280b (70×4)" 注释、K 码表（K1~K4 4 行 bit 串）、底部 先发/后发 箭头 + "串行发送方向：右 → 左" 注释。
- 行序：标题(0) → 编码前 行(0.2) → 括号(0.5) → 编码后 行(0.65) → dmy 注释(0.8) → K 表 4 行(1.0/1.15/1.3/1.45) → 先发/后发(1.7)。
- draw：先发/后发 2 个箭头；括号下划线若是 `<line>` 用 draw。
- cellwave：编码前/编码后 两行的 0xEA~0xED 橙格——左右行进波（0.1s/格，3s 周期，两行同相）；K 表 4 行 bit 串——按行 phase（0.5s 递增，3.6s 周期）。
- march：括号下划线若为虚线 → `.march`。
- glow（2）：编码前 行 K3 格（glow-b）；K 表 K3 行（glow-b，phase 差 1.4s）。
- flow：先发/后发 箭头各 2 包（按标注方向走）。

### 4.10 spec_blanking_idle（1200×660）
IDLE pattern · 10-bit 面板（K5~K8 4 行：格 + bit 串）、lane 间轮换 (EMI 优化) 面板（Lane1~4，每行 4 个 K 格 + 小箭头）、V blanking 行结构 行、Config Line 单独成行 行、VBP 首行 行、底部注释。
- 行序：标题(0) → IDLE 面板(0.2) → lane 面板(0.5) → V blanking 行(0.85) → Config 行(1.05) → VBP 行(1.25) → 注释(1.45)。
- cellwave（本图主角）：**lane 轮换点亮**——每 lane 的 4 个 K 格按轮换顺序点亮：Lane1 K5→K6→K7→K8；Lane2 K6→K7→K8→K5；Lane3 K7→K8→K5→K6；Lane4 K8→K5→K6→K7。实现：每个格 `class="cellwave"` + 内联 `animation-duration:2.4s`，delay = 该格在**轮换序**中的位置 × 0.6s（4 条 lane 共用同一时间线 → 不同 lane 呈现不同相位 = 轮换偏移可视化）。
- cellwave2：IDLE 面板 bit 串格（K5~K8 4 行，0.4s 递增，3.2s 周期）。
- flow：每 lane 格间小箭头（8 条）各 1 包，lane 间错 0.3s。
- glow（1）：VBP 首行 行盒（glow-b）。

## 5. 生成器要求（每张图一个 make_anim_<name>.py）

- 结构建议：读源 SVG 全文 → 按行解析 → 定位锚点（用 text 内容 + 坐标，assert 保护）→ 组装输出 → 写文件。
- 输出的 `<style>` 行 = 本文件第 2 节 kit **逐字**（不要增删类）。
- 每个打标签的元素：class + 必要的 `pathLength`/内联 style；flowdot 是**新增**的 `<path>`（复制 d 属性）。
- 幂等：只依赖源 SVG 内容；重跑 → 字节一致。
- 文件尾：`# ymzhu 2026-10-27 <HH:MM>`。

## 6. 自校验（你的 3 张图必须全绿才许报 DONE）

对每张图运行（python，cwd 在站点目录）：

```python
import xml.etree.ElementTree as ET
from collections import Counter
import re, os, sys
NS="{http://www.w3.org/2000/svg}"
def check(t):
    s=f"{t}.svg"; a=f"anim/{t}.svg"
    data=open(a,encoding="utf-8").read()
    r={}
    try: ET.parse(a); r["xml"]="OK"
    except Exception as e: r["xml"]=f"NG {e}"
    def texts(p): return Counter(el.text or "" for el in ET.parse(p).getroot().iter(f"{NS}text"))
    try: r["text"]="OK" if texts(s)==texts(a) else "NG"
    except Exception as e: r["text"]=f"NG {e}"
    r["noscript"]="OK" if "<script" not in data else "NG"
    r["keyframes"]="OK" if data.count("@keyframes")>=4 else "NG"
    m1=re.search(r"<svg[^>]*>",open(s,encoding="utf-8").read()); m2=re.search(r"<svg[^>]*>",data)
    r["svgtag"]="OK" if m1 and m2 and m1.group(0)==m2.group(0) else "NG"
    r["size"]="OK" if os.path.getsize(a)>1024 else "NG"
    r["rmfix"]="OK" if re.search(r"prefers-reduced-motion.*?flowdot\{display:none!important\}",data,re.S) and re.search(r"prefers-reduced-motion.*?opacity:1!important",data,re.S) else "NG"
    ok=all(str(v)=="OK" for v in r.values())
    print(("PASS" if ok else "FAIL"),t, [f"{k}={v}" for k,v in r.items() if v!="OK"])
    return ok
allok=all([check(t) for t in sys.argv[1:]])
sys.exit(0 if allok else 1)
```

另加人工检查（写进报告）：
- 源 SVG 未被修改（git status 里源图无 M）。
- 一次性效果总时长 ≤2.5s；持续族 ≤3；行波/列车相位错开。
- flowdot 不穿过任何盒内文字（若某边太短/贴盒，改用更细 stroke-width 2 或放弃该边，宁缺勿穿）。

## 7. 报告格式（DONE 消息）

```
DONE — <name1> / <name2> ...
每个文件：
- 输出/生成器路径 + 字节数
- 校验：7 点 PASS/FAIL 列表
- 效果清单：draw N 条 / flowdot N 包 / cellwave N 格 / glow N / step N / march N / row 行序
- caveats（哪些边/格放弃了、为什么）
```

## 8. Changelog

- v2.1（2026-10-27）：① 修 longcode/pydec 生成器漏带源 `<defs>`（5 箭头 marker）与全页白底 rect 的回归（Qwen 交叉验证发现，marker-end 引用悬空 → 箭头端丢失）；生成器组装段补 `out.extend(lines[2:bg_end+1])` + assert 保护。② 澄清 delay 规则：无限循环类允许负 delay 作相位偏移（|d| ≤ 周期）。
