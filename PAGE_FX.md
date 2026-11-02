# PAGE_FX 规范 — team-share 全仓库页面级特效引擎（v2，2026-11-02）

> **位置说明（2026-11-02 起）**：本文件是全仓库 fx 引擎（`fx.css` / `fx.js`）的唯一规范，位于仓库根级，与 `ROLLOUT_FX.md`（推广流程）并列。
> v1 原文曾放在 `hk1v11-longcode-420b-verification/PAGE_FX.md`（与 anim 图混放，位置错误），已迁移合并到此处；v1 原文见该路径的 git 历史。
> 相关规范：SVG 动画/静态双版架构 → `blueprint-ui-style` skill「v4 架构章」；站内动效 kit → 各站 `anim/MOTION_KIT.md`；新文章接入 → `team-share` skill Workflow B。

## 版本状态

| 版本 | 日期 | 状态 | 引擎所在 |
|---|---|---|---|
| v1 | 2026-10-27/28 | 已被 v2 取代 | — |
| v2 | 2026-11-02 | **全仓库已上线**：9 处副本字节一致（仓库根 + `site-template/` + 7 个文章站点；tj 临时目录除外，待删）；页面引用统一 `fx.css?v=5` / `fx.js?v=8`；扫光基底色由 fx.js 运行时取自页面 computed color（透明/渐变字自动回退拆字，居中标题自动补 margin）；全部文章站 `check_article.py` PASS | 各站目录 + 根级 |

## 0. 架构（共享文件 + 页面 2 个 tag）

- 每个站点目录各放一份 `fx.css` + `fx.js`（全仓库字节一致）。
- 每个页面只需 2 处：`</head>` 前 `<link rel="stylesheet" href="./fx.css?v=N">`；`</body>` 前 `<script src="./fx.js?v=M"></script>`。
- **其余全部由 fx.js 运行时完成，页面不写任何特效 markup**：动效/静态按钮注入、滚动显现标记、hero 扫光/拆字、数字滚动、进度条、返回顶部、SVG 动/静交换。
- 新文章接入规则见 §6（与 `team-share` skill 同步）。

## 1. 状态机（fx.js）

- `html.fx-on`：JS 初始化成功且为动画模式时加。**所有"隐藏基态"与"视觉改写"CSS 必须以 `html.fx-on` 为前缀**（无 JS → 无 fx-on → 页面原样，天然兜底）。
- `html.page-static`：静态模式时加，同时**移除 `fx-on`**——基态全灭，静态模式即完整静态页面。（v1 文档中 fx.css 末尾的 page-static kill 块已随 v4 引擎演进删除，现以"移除 fx-on"为唯一机制。）
- 模式优先级：URL `?motion=static|anim` > `sessionStorage('motion-mode')` > `prefers-reduced-motion` > 默认 `anim`（2026-10-28 定稿：选择只在会话内记忆）。
- 切换按钮 `#motionToggle` 由 fx.js 注入顶部导航（挂载规则见 blueprint-ui-style v4 §2.7），页面不得硬编码。

## 2. 特效目录

### 2.1 v1 已上线（13 项）

| # | 效果 | 作用域 | 实现要点 |
|---|---|---|---|
| 1 | 滚动进度条 `#fx-progress` | 全局 | fixed 顶部 3px，`scaleX` 随滚动，rAF 节流 |
| 2 | 滚动显现 `.fx-r` → `.fx-in` | 正文 h2/h3/table/figure、`.stat`、`.hero-hint`、`.page-nav a` | IO 一次性，rootMargin 120px；首屏内 rAF 后直接入场 |
| 3 | 正文蓝图底纹 | body | 32px 网格（v2 加噪点层，见 2.2-B） |
| 4 | 导航滚动阴影 | `.navbar` | scroll>10px 切 `.scrolled` |
| 5 | 返回顶部 `#fx-top` | 全局 | 滚过 600px 淡入；站点自带 `#toTop` 时跳过 |
| 6 | hero 网格漂移 | `.hero::before` | 40px 网格 46s 平移循环 |
| 7 | hero 光晕 | `.hero::after` | 琥珀 radial 26s alternate |
| 8 | 标题字级升起 `.fx-w` | `.hero h1` | 拆字 + 逐字 assert；**v2：与扫光互斥，挂 fx-shine 时不拆字** |
| 9 | meta chips 错拍入场 | `.hero .meta > *`、`.hero .badge` | 0.1s 递增 delay（v2 叠加微弹，见 2.2-D） |
| 10 | 数字滚动 | `.stat .v` | 纯数字 run 0→原值 0.9s；`0720v1` 类跳过 |
| 11 | 表格行级联 `.fx-t` | 正文 table | 行 delay 0.03s×i，上限 0.9s |
| 12 | 章节标题画线 `.fx-hdr` | 无 ::before 装饰的 h2 | 固定宽 `scaleX` 画线，零位移 |
| 13 | hover 抬升 | `.stat`、`.article figure`、`.page-nav a` | translateY(-3px) + shadow |


**v2.1 新增（2026-11-02 晚，用户定稿铺全仓）**：**E. 流程组件入场（fx.css §18 + fx.js markReveals）**——`.flow` 容器进视口时一次性演出：每个 `.fbox` 标题 `<b>` 依次过一道白光（与 hero 扫光同技法，基色 `--fx-flow-base` 运行时取自各页 computed color，取不到/透明则整组跳过），标题光带走完后 `.farrow` → 逐个点亮（0.25→1，0.3s 步进）。全部 forwards 不循环；静态/无 JS 原样。生效范围 = 所有引用引擎的页面（tj 除外），当前 5 站 9 页含 `.flow`。
### 2.2 v2 新增（4 项，参考 dshtui.com 逆向技法）

**A. 缓动令牌**（fx.css §15）
- `--fx-ease-out: cubic-bezier(.16,1,.3,1)`（通用快出慢收）
- `--fx-ease-spring`：默认 `cubic-bezier(.34,1.56,.64,1)` 过冲近似；`@supports (transition-timing-function: linear(0,1))` 时升级为 `linear(0, .324 8.1%, .794 19.9%, 1.028 30.1%, 1.008 43.1%, 1)` 真弹簧。新特效一律用令牌，不再手写 cubic-bezier。

**B. 噪点纹理**（fx.css §3）
- body 第三层背景：`feTurbulence` 分形噪点 data-uri（180px 平铺，`baseFrequency .8`），浅色模式黑粒 α=0.04、暗色模式（`prefers-color-scheme: dark`）白粒 α=0.035。网格两层保持 v1 原值不变。
- 作用：消除大面积纯色的"塑料感"，给蓝图纸面加纸张颗粒。静态纹理，不动画。

**C. hero 标题扫光 `fx-shine`**（fx.css §16 + fx.js init）
- fx.js 给 `.hero h1` 加 `fx-shine`；CSS 双层背景（上层扫光带两端透明 + 下层纯色基底）+ `background-clip:text` + `color:transparent`，**只动上层 `background-position`**——基底层恒定，任何时刻文字都完整着色。
- 配色：主文案基底 `--fx-shine-base`（默认 `#f7f3e8` 奶白）+ 白峰；`.thin` 基底 `--fx-shine-thin-base`（默认 `#f0a137` 琥珀）+ 白峰。
- 几何：h1 是块元素（宽≈容器，字只占一小段），亮带按元素宽度百分比计 → 挂 fx-shine 时 h1 设 `width:fit-content`（左对齐 hero 文字位置不变，零位移），否则亮带比整行字还宽，变成整体发亮。行程 `120% → -20%`（图宽 220%，两端恰在画外），亮带可见约占扫程 91%，`linear` 匀速。
- 节奏（两拍，相位锁定）：主标题与 `.thin` 同周期 5s——主标题 1.2s 起、扫程 1.5s（可见约 1.52–2.88s）；`.thin` 2.6s 起、扫程 0.85s（约等于主标题像素速度，可见约 2.89–3.66s）；随后静息约 2.9s。两条可见窗口按构造不重叠 → 任何时刻字上最多一条光带，与布局无关（`.thin` 自带不透明基底层，主标题光带经过"验证体系"时被盖住）。
- 渐进增强：全部规则包在 `@supports ((-webkit-background-clip:text) or (background-clip:text))` 内，不支持的浏览器保持纯色标题。
- 互斥：挂 fx-shine 的 h1 不再拆 `.fx-w`（clip-to-text 的父级背景无法稳定穿透 transform 中的 inline-block 子 span）。`splitHero()` 检测到 fx-shine 直接返回。

**D. chip 微弹 `fx-pop`**（fx.css §17 + fx.js markReveals）
- 对象：hero `.meta > *` / `.hero .badge`（沿用 0.1s 递增 delay）、`.stat` 卡片（0.08s 错拍）。
- 入场 = 上浮 12px + 缩放 0.94→1，`var(--fx-ease-spring)` 轻微过冲；animation 只用 `backwards` 填充——播完回落到 `.fx-r.fx-in` 自然态，不锁 transform，hover 抬升照常。
- `.stat` 的 hover 合并规则（§13，特异性 0,3,0）由 `.fx-pop.stat`（0,4,0）覆盖，transition 保留 transform/box-shadow。

## 3. 审美定稿条款（设计约束，优先于"能做"）

1. **扫光禁红棕/琥珀色亮带；SVG 里一律用"文字光带"**（2026-11-02 ymzhu："这个红色扫光真的很丑，不如别人的""SVG 里面用光带，而不是扫光"）——亮带一律白/冷白，且**只在文字字形内可见**（与 hero 标题同技法），禁止整块色带擦过面板；琥珀只能做**基底**，不能做**光**。SVG 配方见 `anim/MOTION_KIT.md` §4（v4.3）。
2. **短箭头不加走线/流动特效**（2026-11-02 ymzhu：验证架构对比图箭头连线很短，做走线效果会很丑，不如不加）——判据：可见长度 < 80px 的箭头不挂 flowdot / flowtail / march / dashgrow，箭头保持 draw 入场后静止；需要表达流向时改用**方框接力点亮**（`.step` 沿链路逐盒点亮）。已同步 MOTION_KIT v4.3 §3。
3. **持续效果族 ≤3 / 区**：hero = 网格漂移 + 光晕 + 扫光 = 3，已顶格，hero 不得再加任何 infinite 效果。

## 4. 铁律（v1 九条 + v2 修订/新增）

1. 不改任何数据/文案：拆字后逐字 assert；数字滚动终值 = 原值；不增删可见内容。
2. 不新增外部资源、不引 JS 库（纯原生；噪点用 data-uri，无外部请求）。
3. 静态模式 = 100% 完整静态页面（移除 fx-on 后所有基态失效；新增效果必须逐条核对）。
4. 布局零位移：reveal 用 transform；伪元素装饰绝对定位 + `pointer-events:none`。
5. 性能：只动画 transform / opacity；rAF 节流；观察器一次性。**v2 唯一白名单例外**：`fx-shine` 的 `background-clip:text` 扫光允许动画 `background-position`（重绘区域限于字形，dshtui 实测开销极低）；其它任何元素不得动画 background / width / height / top / left。
6. 现有功能不许动：lightbox、marked 渲染、SVG 滚动重播（same-src 重赋值）、img 动/静交换语义。
7. 页面同构：同站模板页改动逐字节一致（除 active 链接与页内文本）。
8. 签名：fx.css / fx.js 尾 `/* ymzhu YYYY-MM-DD HH:MM */`；页面尾 `<!-- ymzhu YYYY-MM-DD HH:MM -->`（替换不累积）。
9. 不碰 SVG：anim/ 下动画图与生成器归 MOTION_KIT + blueprint v4 管辖。
10. **（v2 新增）门控 + 渐进增强**：新视觉改写必须同时满足 `html.fx-on` 前缀；依赖新 CSS 特性（`background-clip:text`、`linear()` 等）时必须 `@supports` 包裹或给兜底值。
11. **（v2 新增）新页面必带双 tag**：任何新生成页面必须带 fx 双 tag（见 §6，与 team-share skill 同步）；缺失视为页面未完成。

## 5. 自校验（改引擎后必须全过）

1. `node --check fx.js`。
2. 每页 grep：`fx.css?v=N` ×1、`fx.js?v=M` ×1、尾签名已更新。
3. fx.css 中所有含新类名的选择器均以 `html.fx-on` 开头（keyframes 除外）。
4. DOM 检查（Edge `--dump-dom`）：动画模式 `<html>` 含 `fx-on`、hero h1 含 `fx-shine` 且无 `.fx-w`；`?motion=static` 时无 `fx-on`、有 `page-static`。
5. 渲染截图（Edge headless，绝对路径，独立 `--user-data-dir`，`--virtual-time-budget=30000`；扫光另截 2200（主标题亮带途中）/ 3300（「验证体系」亮带途中）中途帧）：标题任何时刻完整可读、亮带为白色（**不得出现红/红棕扫光**）、静态模式纯色无半透明残留、正文纹理不过重。

## 6. 新文章 / 新站点接入（与 team-share skill Workflow B 同步）

1. 从**仓库根级** `fx.css` / `fx.js`（= 最新已验收版本）复制到文章目录，不得改动。
2. 每个页面插入双 tag（带当前全仓库统一的 `?v=`），`</head>`、`</body>` 各恰 1 次。
3. 页面无需任何特效 markup；hero 用 `<header class="hero"><div class="hero-inner">…<h1>` 结构即自动获得网格/光晕/扫光。
4. 按 §5 自校验。

## 7. v2 全仓库推广流程（用户验收后执行，一次性）

1. 420b 站 v2 引擎 → 覆盖根级 `fx.css`/`fx.js` + 其余 7 站 + `site-template/`，**9 处副本字节一致**（md5 核对）。
2. 全部站点页面引用统一 bump：`fx.css?v=` 与 `fx.js?v=` 各 +1（取全仓库现值最大者 +1，避免回退）。
3. 推广前补齐引擎通用性（**推广前置条件**）：①扫光基底色改为 fx.js 运行时读取 h1 / `.thin` 的 computed color 写入 `--fx-shine-base` / `--fx-shine-thin-base`；若 computed color 为透明（站点已用渐变字），该站跳过扫光、回退拆字。否则非奶白标题的站点会被强制染成奶白。②`width:fit-content` 只对左对齐 hero 零位移；居中 hero 的站点需同时补 `margin-inline:auto`（由 fx.js 读 computed text-align 决定）。
4. 按 `ROLLOUT_FX.md` §1 第 4 步做每站渲染验证（tj 深色站 182 页重点看噪点在深底的观感）。
5. 本文件版本状态表把 v2 改为"全仓库已上线"。

## 8. 待办 / 已完成（2026-11-02 22:00 全量整改后更新）

**已全部完成（2026-11-02，用户定调"SVG 里面用光带，而不是扫光"）**：
- ✅ 全仓 7 张琥珀扫光带 → 文字光带：420b `pydec_tx_rx_structure` / `spec_dummy_70b`；lc-cpuwr `config_data_beat_regroup_0721`（标题 + XOR 结论行）；postpt `skew_probe_audit_1028` / `dc_area_evolution_table` / `dc_gen_summary_table` / `delay_skew_14vs12`（均落结论文字、不落数值区）。配方 = §4 / MOTION_KIT v4.3。
- ✅ 短箭头列车全清：420b `8b10b_vs_420b`（16px spine → 方框接力点亮）、`spec_dummy_70b`（35/60px → 删列车，draw 静止）。
- ✅ `pydec_tx_rx_structure` 离线比对区三盒等距重排（静态源）。
- ✅ MOTION_KIT v4.3 三站同步（420b / postpt / lc-cpuwr 各自站内文件）。
- ✅ 引擎 v2 全仓库上线：9 处副本字节一致（根 + site-template + 7 文章站；tj 临时目录除外），页面引用统一 `fx.css?v=5` / `fx.js?v=8`（87 处）。
- ✅ 模板修复：缓存 meta / lightbox.js 引用 / site.js `?v=Date.now()` 重播废除（归口 fx.js v4.1）/ NAV 高亮归一化 / 补 `anim/validate_kit_v4.py`。
- ✅ 全部 8 个文章站门禁 PASS（`check_article.py` 各站 exit 0；含 TOC 折叠补齐、导航 ≤ 首页+9、标题编号补齐共 190+ 个标题、7 页补 lightbox、2 个孤儿动画图补静态版——`check_anim_pairs.py` 全仓 44/44 OK）。
- 更正记录：此前怀疑 kit 的 `translateX(var(--sweepP))` 在 SVG 关键帧中失效——定格截图证实有效，误判源于无头截图对 transform 动画取帧不可靠；kit CSS 未改。

**遗留（不阻塞）**：
1. `postpt` 站 `51_signoff_setup_hk11` 系列 5 张图为无动画静态副本（存量形态，非本次引入）；如需动画化按 MOTION_KIT 另开任务。
2. `MOTION_KIT.md §6.10` 文档漂移：声称 `spec_blanking_idle` 有格间箭头列车，实际 flowdot 为 0。
3. lc-cpuwr `diagrams.html` 的 TOC 为「分节按钮」特殊形态，折叠 CSS 已就位、JS 不适用（已注记）。
4. postpt ch10 尾部 5 个案例「节号 vs 案例号」错位（原文档物理顺序使然，编号连续优先；对齐需重排内容）。
5. ✅ `.fbox` 一次性文字光带入场 + `→` 逐个点亮：2026-11-02 用户拍板「对仓库下所有页面修改（tj 除外）」→ 引擎 v2.1 实现（见 §2.2-E），全仓生效。框角小灰点来源仍未复现（不影响任何功能）。

<!-- ymzhu 2026-11-02 22:45 -->
