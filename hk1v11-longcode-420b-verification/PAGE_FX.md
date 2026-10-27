# PAGE_FX 规范 — 站点页面级特效（v1，2026-10-27）

> 背景：10 张 SVG 已是 v2 动效；导航已有「动效/静态」切换按钮（每页内联 IIFE 控制 img src 交换）。
> 本次：给**页面本身**加大规模特效（hero、滚动显现、数字滚动、表格级联等），并让现有按钮**同时关掉所有页面特效**。
> 大胆做，但静态模式必须 100% 完整可见（同一套"隐藏基态只在 fx-on 下生效 + kill 块"纪律，与 SVG kit 同源）。

## 0. 架构（共享文件 + 最小页面改动）

新增 2 个共享文件（站点根目录）：
- `fx.css` — 全部页面特效样式 + 静态 kill 块 + `@media (prefers-reduced-motion:reduce)` kill 块
- `fx.js` — 特效引擎：接管原 IIFE 的全部职责（模式解析/按钮/img src 交换/滚动重播）+ 页面特效（显现观察器/数字滚动/进度条/hero 字级 reveal/表格级联/nav 阴影/返回顶部）

6 个页面（index + architecture/comparison/decoder/encoding/frame）各自改动（**很小**）：
1. `<head>` 里 marked 的 `<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>`（6 页都在 L13）**下一行**插入：`  <link rel="stylesheet" href="./fx.css">`
2. 内联 `<script>`（index L608 / 模板页 L649 起）里**整段删除**「动画/静态一键切换 + 滚动重播（2026-10-27 ymzhu v2）」IIFE（从注释行到 `    })();` 止；模板页保留 `marked.parse` 那行，index 保留 lightbox 全部代码，只删 IIFE 段）。职责移交 fx.js。
3. 该内联 `</script>` 之后（body 末尾、`</body>` 之前）插入：`  <script src="./fx.js"></script>`
4. 文件尾签名替换为 `<!-- ymzhu 2026-10-27 <HH:MM> -->`。
**不加其它任何 markup**——hero 字级 split、数字滚动、reveal 标记、进度条、返回顶部按钮全部由 fx.js 运行时自动完成。

## 1. 核心状态机（fx.js）

- `html.fx-on`：JS 成功初始化后加。**所有"隐藏基态"CSS 必须以 `html.fx-on` 为前缀**（无 JS → 无 fx-on → 全部直接可见，天然兜底）。
- `html.page-static`：静态模式（按钮切换 / URL `?motion=static` / 系统 prefers-reduced-motion）时加。kill 块见 §3。
- 模式优先级（与原 IIFE 一致）：URL `?motion=static|anim` > `localStorage('motion-mode')` > `prefers-reduced-motion` > `anim`。
- 按钮 `#motionToggle`（已存在，导航最右）：点击翻转模式 → 存 localStorage → 全量重放（SVG src 换新时间戳重播 + 页面特效重新入场）。label/aria-pressed 与原逻辑一致（🎬 动效 / 🖼 静态）。
- 原 IIFE 的 svgImgs/baseAnim/nameOf/apply/observe 逻辑**原样搬进 fx.js**（滚动重播修复保留：匹配 `img[src*=".svg"]` 含 query 的写法，不要退回 `src$=`）。
- 初始化时机：脚本在 body 末尾（marked.parse 已同步跑完，article 内容已就位）；仍用 `readyState` 检查 + DOMContentLoaded 兜底。

## 2. 特效目录（大胆，但每图/每区 ≤3 族持续效果；一次性 ≤1.2s/元素；只用 transform/opacity）

**全局**
1. 滚动进度条：`#fx-progress`（fx.js 创建；fixed top:0 left:0 height:3px background:var(--accent) z-index:200；用 `transform:scaleX(0→1)` transform-origin:left 随滚动更新，rAF 节流）。静态模式 display:none。
2. 滚动显现：`html.fx-on .fx-r{opacity:0;transform:translateY(14px);transition:opacity .55s ease,transform .55s cubic-bezier(.22,.7,.3,1)}` / `.fx-r.fx-in{opacity:1;transform:none}`。fx.js 自动标记：`#article h2`、`#article h3`、`#article table`、`#article figure`、`.article > p:first-of-type`、`.stat`、`.hero-hint`、`.page-nav a`（index 与模板通用；不存在的选择器自然跳过）。IntersectionObserver rootMargin '120px 0px'，一次性；加载时已在视口的直接 fx-in。
3. 正文蓝图底纹：body 固定背景——2 条 linear-gradient 32px 网格，rgba(28,37,52,0.03) 线（静态纹理，不动画；只在 body 原背景之上叠加，不改原背景色）。
4. 导航滚动阴影：`.navbar.scrolled{box-shadow:0 2px 14px rgba(28,37,52,.12)}`，scroll>10px 切换（transition .25s）。
5. 返回顶部：`#fx-top`（fx.js 创建；fixed right:24px bottom:28px；60px 圆钮，var(--surface) 底 + var(--line) 边 + ↑；滚过 600px 淡入；点击 scrollTo 顶 smooth；z-index 90；静态模式隐藏）。

**hero（index.html 的 `<header class="hero">`；模板页无 hero，以下自动跳过）**
6. hero 蓝图网格漂移：`.hero::before`（绝对定位铺满；2 条 linear-gradient 40px 网格 rgba(255,255,255,.05)；`animation:fxGridPan 46s linear infinite` 平移 40px 循环；z-index:0）。
7. hero 光晕漂移：`.hero::after`（radial-gradient 橙色 18% 透明，380px 圆，top:-80px right:8%；`animation:fxGlow 26s ease-in-out infinite alternate` 缓慢移动+呼吸 opacity .5↔.85；z-index:0）。
8. 标题字级升起：fx.js 把 hero 大标题（选 `.hero h1`，若没有则 `.hero-inner` 里最大的 text 元素）的**直接文本节点**拆成 span：CJK 单字一个 span、连续拉丁/数字一个 span、空白保留原样；每个 span `class="fx-w"` + 内联 `animation-delay:0.06s×i`；CSS：`html.fx-on .fx-w{display:inline-block;opacity:0;transform:translateY(18px);animation:fxWordUp .5s cubic-bezier(.22,.7,.3,1) forwards}`。
   约束：只拆文本节点、不碰子元素（<br>、em、code 原样）；可见文本必须与原文完全一致（拼接后逐字相等，写 assert）。
9. meta 行（`.meta` 内各 chip）与 badge：`.meta > *`、`.hero .badge` 加 fx-r（0.1s 递增 delay，JS 设内联 transition-delay）。
10. 数字滚动：`.stat .v`——文本里每个**纯数字 run** 从 0 滚到原值（0.9s ease-out，卡片间 0.12s 错拍）；`0720v1` 这种"数字+字母后缀"的跳过（只 reveal 不滚动）；`5<em>/</em>5`、`6<em>/</em>10` 的两个 run 各自滚动。静态模式不滚动（保持原值）。用 textContent 分段实现，保留 em 结构（对 em 包裹的 run 直接改 em 内文本）。

**内容区（article，模板页为主）**
11. 表格行级联：`#article table.fx-t`（=被 fx-r 标记的 table）；`html.fx-on .fx-t tr{opacity:0;transform:translateX(-8px)}`，fx-in 后 `tr{opacity:1;transform:none;transition:opacity .4s,transform .4s}`，JS 给每行内联 `transition-delay:0.03s×i`（上限 0.9s，超出的行不再递增）。表头行（th 所在）delay 0。
12. 章节标题 accent 画线：`#article h2.fx-hdr`（=h2 加 fx-r 的同时加 fx-hdr）；`::before`（现有 h2 若已有 accent 伪元素则跳过加 fx-hdr，避免双重装饰——fx.js 用 getComputedStyle 检查 content/border）：`html.fx-on .fx-hdr::before{content:"";display:inline-block;width:26px;height:3px;background:var(--accent);vertical-align:middle;margin-right:10px;transform:scaleX(0);transform-origin:0 50%;transition:transform .6s .15s}` `.fx-in::before{transform:scaleX(1)}`（固定宽度 scaleX 画线，标题文字零位移；2026-10-27 由 width 动画改来，审计发现 width 动画会推挤标题 36px）。若 h2 已有 ::before 装饰则整体跳过此效果（保持原样）。
13. 卡片/图块 hover 抬升：`.stat`、`.article figure`、`.page-nav a`：`transition:transform .25s,box-shadow .25s`；hover `transform:translateY(-3px)` + `box-shadow:var(--shadow)`。

**持续效果族总数**：网格漂移、光晕、（进度条/阴影/返回顶部属滚动驱动不算族）→ 2 族 + 一次性群。达标。

## 3. 静态 kill 块（fx.css 末尾，逐字）

```css
/* ===== PAGE FX 静态 kill（page-static 类 与 系统减少动态效果，双通道） ===== */
html.page-static *, html.page-static *::before, html.page-static *::after {
  animation: none !important;
  transition: none !important;
}
html.page-static .fx-r, html.page-static .fx-w, html.page-static .fx-t tr {
  opacity: 1 !important;
  transform: none !important;
}
html.page-static .fx-hdr::before { width: 26px !important; }
html.page-static #fx-progress, html.page-static #fx-top { display: none !important; }
html.page-static .navbar { box-shadow: none !important; }
@media (prefers-reduced-motion: reduce) {
  html.page-static *, html.page-static *::before, html.page-static *::after {
    animation: none !important;
    transition: none !important;
  }
}
```

注意：`prefers-reduced-motion` 的纯 CSS 兜底**只覆盖无 JS 场景**（有 JS 时 fx.js 已按该 media 把模式设为 static → page-static 类生效）。若担心重复，media 块可只留一条注释说明——但保留上面这段更稳（无 JS + 减动效双保险）。

## 4. 铁律

1. 不改任何数据/文案：hero 拆 span 后拼接文本必须逐字等于原文（JS assert）；数字滚动结束值 = 原值；不增删可见内容。
2. 不新增外部资源；不引新 JS 库（纯原生，无依赖）。
3. 静态模式 = 完整静态页面（kill 块覆盖所有隐藏基态；逐条核对 §2 里每个设置 opacity:0/transform 的选择器都在 kill 块里）。
4. 布局零位移：reveal 用 transform 不用 display/height/margin 变化；hero ::before/::after 用绝对定位 + pointer-events:none。
5. 性能：只动画 transform/opacity；rAF 节流滚动；观察器一次性（unobserve）。
6. 现有功能不许动：lightbox、marked 渲染、滚动重播（保留修复后的行为）、按钮原有 img src 交换语义。
7. 6 页一致性：模板页 5 份改动必须逐字节同构（除 active 链接与页内文本）；index 单独处理 hero 部分。
8. fx.css/fx.js 文件尾签名：`/* ymzhu 2026-10-27 <HH:MM> */`。
9. 不碰 SVG（anim/ 下 10 图与生成器）、不碰源图、不碰其它站点目录。

## 5. 自校验（必须全过再报 DONE）

1. `node --check fx.js`（站点根目录有 node；把 fx.js 直接 check）。
2. 每页 grep：`fx.css` link 存在 ×1、`fx.js` script 存在 ×1、旧 IIFE 注释行（`动画/静态一键切换`）已删、`src$=` 选择器不再出现、签名已更新。
3. 渲染对比（Edge headless，**绝对路径** screenshot，mktemp user-data-dir，virtual-time-budget=9000）：
   - `index.html`（默认动画）：hero 网格/光晕/进度条/字级/数字/卡片 全部在场
   - `index.html?motion=static`：按钮「🖼 静态」、进度条/返回顶部隐藏、所有内容完整可见、无半透明残留
   - `encoding.html?motion=static`：article 标题/表格/图块全部完整可见（无 opacity 残留）
   - `index.html` 截图里 hero 标题文字与原文逐字一致（视觉核对）
4. kill 块完整性：grep fx.css 里 `.fx-r`、`.fx-w`、`.fx-t tr`、`.fx-hdr::before`、`#fx-progress`、`#fx-top` 均出现在 `page-static` 选择器中。

## 6. 报告格式

```
DONE — PAGE FX v1
- fx.css / fx.js：行数 + 签名
- 6 页改动核对表（每页：link/script/删IIFE/签名 ✓）
- node --check 结果
- 4 张渲染截图路径 + 每张一句话结论
- caveats（哪些效果因结构原因跳过、为什么）
```
