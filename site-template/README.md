# site-template — 新站唯一骨架（核心框架定死，2026-10-28）

> 用户口径：**"架构要把核心框架定死，不然模型会放飞自我，大体结构要定死。"**
> 建新站 = 复制本目录 → 改槽位 → 过验证门。**不是创作，是组装。**
> 上位规范：skill `blueprint-ui-style` 的「新站搭建强制流程」章与「动画/静态双版 SVG 站点架构（v4）」章。

## 固定文件（禁改，逐字使用）

| 文件 | 说明 |
|---|---|
| `css/style.css` | 组件唯一事实源（token/组件禁改；只许追加站点专属内容类，须最小化） |
| `js/site.js` | 导航/TOC/表格增强/代码块增强。**唯一内容槽 = 顶部 `NAV` 数组** |
| `js/lightbox.js` · `js/marked.min.js` | 图片查看器 / markdown 渲染，逐字使用 |
| `fx.js` · `fx.css` | 动效引擎 v4（零重载切换 + 右下角统一浮动按钮 + 默认动画模式）。与全仓库 9 处副本字节一致，禁改；升级全仓库统一做 |
| `index.html` · `page.html` | 页面骨架（head 引用顺序、两行导航、hero、container/with-toc/content、page-nav、footer、脚本顺序全部定死） |
| `anim/MOTION_KIT.md` | 双版图动效规范模板（kit CSS 与铁律禁改；只改 §1 路径与 §6 分图规格） |

## 内容槽（只改这些）

1. `js/site.js` 顶部 `NAV` 数组——本站导航；
2. 页面 `<title>` / `navbar-brand` / hero 各槽 / `footer` 文案；
3. `page.html` 的 `<script type="text/template" id="md">` 内的 markdown 正文；
4. 双版图：`<name>.svg`（静态，事实源）+ `anim/<name>.svg`（生成器产出）+ `anim/make_anim_<name>.py`，页面只引用 `./anim/<name>.svg`；
5. 根目录 `../index.html` 站点列表登记新站入口。

## 禁止清单（模型放飞自我的常见路径，一律禁止）

- ❌ 新框架/新依赖/构建步骤/包管理（零依赖：原生 HTML/CSS/JS）
- ❌ 改 design tokens（色板/字体/圆角/阴影/动效时序）
- ❌ 改 fx.js/fx.css、发明第二套切换按钮或页面级硬编码 `#motionToggle`
- ❌ 发明组件库里不存在的新组件（要新组件 → 先向用户提案，批后写回 skill）
- ❌ 新目录层级/新 CSS 文件/新 JS 文件（除 `anim/make_anim_*.py` 生成器）
- ❌ 图不经双版管线直接塞 PNG/手写动画 SVG

## 建站步骤

1. `cp -r site-template <新站名>` → 改 5 个内容槽；
2. 双版图管线走 MOTION_KIT v4（生成器确定性幂等 + validate 校验全 PASS）；
3. 验证门：`md5` 校验 fx.js/fx.css 与仓库一致 · `scripts/check_anim_pairs.py` 无孤儿 · 切换零位移 · 稳态可辨 · file:// 与线上均正常；
4. 根导航登记 → 本地预览问用户"要不要截图验收" → git 提交（信息含改什么/为什么/验证结果）。
