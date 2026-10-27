# ROLLOUT_FX 规范 — 把「动效/静态」引擎推广到 team-share 全部站点（2026-10-27）

> 参考实现（已完成）：`hk1v11-longcode-420b-verification/`（fx.js / fx.css / PAGE_FX.md；引擎已在 commit 6fc9b1e 多站点兼容化）。
> 本任务：其余 7 个站点接入同一引擎。**引擎是通用的，页面只需 2 个 tag**——按钮自动注入、特效自动标记，全部由 fx.js 运行时完成。

## 0. 引擎能力（已内置，不需要站点侧任何 markup）

- 模式：URL `?motion=static|anim` > `localStorage('motion-mode')` > `prefers-reduced-motion` > 动画；切换=全量重放，按钮记住选择
- 按钮：页面无 `#motionToggle` 时自动创建——有 `.navbar-links` → 注入导航栏（navbar-motion 样式）；无 → 右上角浮动胶囊（float-motion 样式）
- 特效：滚动进度条 / 章节表格图块滚动显现（选择器已覆盖 `#article`、`main`、`.container`）/ 表格行级联 / h2 画线（scaleX 零位移）/ 导航滚动阴影（仅 `.navbar`）/ 返回顶部（站点已有 `#toTop` 自动跳过）/ hover 抬升 / 正文蓝图底纹；有 `.hero` 的页面额外获得网格漂移+光晕+标题字级升起，有 `.stat .v` 的获得数字滚动
- 动画 SVG 交换：`img[src*="/anim/"]` ↔ 去掉 `/anim/` 段的静态原版（根目录或 images/ 等任意深度）
- 静态三道防线：无 JS（隐藏态 CSS 带 `html.fx-on` 前缀）/ `html.page-static` kill 块 / `prefers-reduced-motion` 纯 CSS 兜底——静态模式 = 完整静态页面

## 1. 每个站点的标准动作

1. `cp hk1v11-longcode-420b-verification/fx.css <site>/fx.css`；`cp .../fx.js <site>/fx.js`（引擎原样复制，不改动——如确需站点级调整，改完必须 `node --check` 并在报告里说明）
2. **每个页面** 2 处插入（Python 读写，`newline=""` 保留原 EOL）：
   - `</head>` 之前：`  <link rel="stylesheet" href="./fx.css">`
   - `</body>` 之前：`  <script src="./fx.js"></script>`
   - **断言**：每页 `</head>`、`</body>` 各恰出现 1 次；插入后 `grep -c 'fx.css'` == 1、`fx.js` == 1
3. 每个被改页面文件尾签名 `<!-- ymzhu 2026-10-27 <HH:MM> -->`（已有则替换，没有则追加；页面尾不是 `</html>` 时加在最后一行后）
4. 自校验（必须全过）：
   - `node --check <site>/fx.js`
   - 全页 grep 核对（上条断言）
   - Edge headless 渲染 **2–3 个代表性页面 × 两种模式**（默认 + `?motion=static`）：
     `msedge --headless --disable-gpu --user-data-dir=$(mktemp -d) --window-size=1400,1750 --virtual-time-budget=30000 --screenshot=<绝对路径> "file:///<绝对路径>.html[?motion=static]"`
     **必须用 30000 虚拟时间**（9000 会抓到 lazy 图/rAF 计数器中途态，属已知截图伪影，不是 bug）
   - 截图核对：按钮在场（导航栏内或右上角浮动胶囊）；静态模式 = 内容完整无半透明残留；版式无破坏
   - EOL 抽查（`file` 或 `grep -c $'\r'` 前后一致）
5. **不 commit**（lead 统一提交）；渲染临时文件用完即删
6. 报告格式：
   ```
   DONE — <site> fx 推广
   - 引擎复制 + node --check ✓
   - 页面核对表：N 页 × (link/script/签名) ✓（异常页单列原因）
   - 渲染截图路径 ×4~6 + 每张一句话结论
   - caveats（跳过的页/原因/站点级调整）
   ```

## 2. 站点分派（每人只碰自己目录）

| 站 | 页数 | 结构 | 特别注意事项 |
|---|---|---|---|
| advanced-design | 9 | marked/#article 模板族，assets/style.css | 导航链接栏由 JS 运行时生成（markup 为空）→ 按钮由引擎自动注入，**不要手改 nav** |
| fusion-compiler-migration | 8 | 同上 | 同上 |
| hk1v11-lc-cpuwr-history | 9 | 静态 .container 页 + diagrams.html 是 marked 模板 | 动画 SVG 在 `images/anim/`（静态原版在 `images/` 同名，已确认存在）→ 引擎 staticSrc 泛化已兼容；diagrams.html 的 nav 在文件中部（~L362），正常插入即可 |
| hk1v11-synthesis-postpt-practice | 23 | marked 模板族，css/style.css | 23 页用批量 Python 一次处理，断言逐页 |
| hv2m23-agent-vm-workflow | 9 | marked 模板族，assets/style.css | 注意该站若用 teal 主题，fx 的 accent 走 `var(--accent, #b45309)` 自动适配，勿硬编码改色 |
| synthesis-integration-flow-guide | 14 | 静态 .container 页 | 有 1 个动画 SVG 引用 `./image/anim/script-flow-overview.svg`（index.html ~L560 + script-dict.html markdown ~L797），但 `image/script-flow-overview.svg` 静态版**缺失**。站根 `script-flow-overview.svg` 疑似静态原版（0 @keyframes，md5 与 anim 版不同）——**先验证**：其 `<text>` 多重集与 anim 版一致、无 flowdot/kit 类 → 通过则 `cp` 到 `image/script-flow-overview.svg`；不通过则从 anim 版生成（删含 @keyframes 的 `<style>` 块 + 删 `<path class="flowdot">` 元素 + 去 kit 类属性），再验证 XML 良构 + text 多重集一致 |
| tj | 182 | 深色主题股票页，`<main><article>`，PWA（sw.js） | **批量 Python 脚本一次处理 182 页**（每页断言 head/body 各 1）；无 `.navbar`（tabbar 仅移动端）→ 引擎自动用**浮动按钮**；已有 `#toTop` → 引擎自动跳过自家返回顶部；sw.js 是运行时缓存（CORE 仅 3 项）→ **不改 sw.js**；渲染验证选 index.html + 持仓快照.html + 任一股票页 |

## 3. 铁律

1. 只加 2 个 tag + 签名 +（站点级）引擎文件/静态 SVG 补件；**不改**页面既有 CSS/JS/内容/功能
2. 不新增外部资源（fx.css/fx.js 是站内的）；不动其它站点目录；不动 anim/ 下已验证的 SVG
3. 静态模式必须 100% 完整可见（引擎已保证；若发现你站点某元素静态下消失，报告之，不要自己改引擎逻辑——先报 lead）
4. EOL 逐文件保留（CRLF 站不得变 LF）
5. 签名时间统一 `2026-10-27 <你实际执行时刻>`
6. 渲染截图放各站 `.fxcheck/`（用完删），不进 git

## 4. 环境

- Windows；`python` / `node`(v24) 在 PATH；Edge = `C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe`
- 仓库根：`E:\project\team-share-public`；各站目录见 §2
- 截图必须绝对路径；`--user-data-dir=$(mktemp -d)`；轮询 ≤60s

<!-- ymzhu 2026-10-27 13:55 -->
