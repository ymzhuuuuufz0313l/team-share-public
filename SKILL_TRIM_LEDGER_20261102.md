# team-share skill 精简迁移台账（2026-11-02）

> 目的：证明这次精简**没有丢任何内容**，每一段原文都有明确去向，且去向可机检。
> 旧版：`~/.config/opencode/skills/team-share/SKILL.md.bak-20261102`（563 行）；kimi 副本同名 `.bak-20261102`（556 行）。
> 新版：同路径 `SKILL.md`（约 150 行）。`~/.zcode/skills/team-share` 是指向 opencode 的 junction，两处为同一文件；kimi 副本已同步（CRLF）。
> 回滚：`cp SKILL.md.bak-20261102 SKILL.md`（opencode 与 kimi 各一次）。

## 1. 逐段去向

| 原段落（旧版行号） | 行数 | 去向 | 怎么核实 |
|---|---|---|---|
| Trigger（L8–15） | 8 | **留在原地**（压缩） | 新版「Trigger」节 |
| Workflow A（L16–27） | 12 | **留在原地**（压缩） | 新版「Workflow A」节 |
| Workflow B 步骤 1–4（L28–44） | 17 | **留在原地**；新增第 3 步「复制 site-template」 | 新版 Workflow B 1–4 |
| 视觉风格 + 字体 + 核心令牌（L45–47） | 3 | 禁止项**留在原地**；令牌/字体 → `site-template/css/style.css`（实际生效值）；说明 → `blueprint-ui-style`「设计系统（Design Tokens）」章 | `check_skill_pointers.py` 章节/文件检查 |
| fx 双 tag 条款（L48–53，11-02 新增） | 6 | **留在原地**，缩成一句（骨架已带，禁删） | 模板 `index.html`/`page.html` 已含双 tag；`check_article.py [F]` |
| Markdown 嵌入方式（L54–55） | 2 | **留在原地** | Workflow B 第 5 步 |
| 配图决策（L57–63） | 7 | **留在原地**（别的 skill 没有等价内容，不能指出去） | 新版「配图决策」 |
| Graphviz 使用方式（L64–74） | 11 | **留在原地**，压缩为一条（同上：无等价内容） | 新版「配图决策」第 3 条 |
| fireworks-tech-graph 使用方式（L75–97） | 23 | **指向** `fireworks-tech-graph`「Workflow (Always Follow This Order)」章（完全覆盖） | `check_skill_pointers.py` |
| 防缓存 meta（L85–91） | 7 | **留在原地**一行（骨架已带） | Important Rules |
| SVG 寄存器/地址图约定（L98–116） | 19 | **留在原地**，压缩（无等价内容），示例 XML 原样保留 | 新版「配图决策」第 5 条 |
| 动画 SVG（L117–119） | 3（长段） | 硬约束 4 条**留在原地**；细节**指向** `fireworks-tech-graph`「Animated SVG」章 + `blueprint-ui-style`「动画/静态双版 SVG 站点架构」章（冲突以 v4 为准） | `check_skill_pointers.py` |
| 单页结构 TOC 要求（L121–135） | 15 | 规则**留在原地**（Important Rules「TOC」）；实现 → 模板 `js/site.js` | `check_article.py [T]` |
| 多页结构 landing/chapter/导航/TOC/page-nav（L136–162） | 27 | 规则**留在原地**（Workflow B 第 4–5 步、Important Rules）；导航度量 → 模板 `style.css`；导航上限 → `check_article.py [N]` | 同左 |
| 根占位页 / README / commit / Pages / 报告（L163–175） | 13 | **留在原地** | Workflow B 第 7–12 步 |
| Important Rules（L177–197） | 21 | **全部留在原地**（标题编号、级别一致、多页标题体系、TOC 缩进、配图、lightbox 强制） | 新版 Important Rules |
| 组件 1–5：badge / statbar / flow / timeline / pcard 的 CSS+HTML（L199–306） | 108 | → 模板 `css/style.css`（已有：`.statbar` `.fbox` `.farrow` `.timeline` `.titem` `.tdate` `.pcard` `.prow`；**补入**：`.badge-rtl` `.badge-tx` `.badge-dv`）；旧类名映射见下 | 速查表类名由 `check_skill_pointers.py` 逐个在 style.css 里 grep |
| 组件 6：status-tracker（L307–343） | 37 | CSS → 模板 `style.css`（**补入** `.st-details` 全套，改用站点令牌）；使用规则**留在原地**（速查表下「状态跟踪总账规则」） | 同上 |
| 图片 Lightbox 代码（L344–449） | 106 | 实现 → 模板 `js/lightbox.js`；强制规则 + 自查清单**留在原地** | `check_article.py [L]` |
| TOC 折叠代码（L463–530） | 68 | 实现 → 模板 `js/site.js`；规则 + 自查清单**留在原地** | `check_article.py [T]` |
| PIL 表格图规范（L533–562） | 30 | → 新 skill `pil-table-render`，**原文逐字搬迁**（opencode + zcode junction + kimi） | 新 skill 正文与 bak 对应段落 diff 为 0 |

### 旧类名 → 模板类名映射

| 旧（skill 内嵌代码） | 新（模板） | 说明 |
|---|---|---|
| `badge-fixed` | `badge-ok` | 已解决 |
| `badge-pending` | `badge-warn` | 待跟进 |
| `badge-rtl` / `badge-tx` / `badge-dv` | 同名（2026-11-02 补入模板） | 侧别 |
| `.stat .num.ok` / `.num.warn` | 无对应 | 模板 `.stat .num` 统一用 accent 色；需要绿/黄数字时用 `.badge-ok/.badge-warn` 标注（不再按数字着色） |
| `pcard.pending` | `pcard.warn` | 待跟进卡片 |

## 2. 本次附带修改

| 文件 | 改动 |
|---|---|
| `site-template/css/style.css` | 末尾追加侧别徽章 3 个 + `.st-details` 全套（只追加，不改已有规则） |
| `site-template/README.md` | 切换按钮位置「右下角」→「顶部导航」（对齐 10-28 晚定稿） |
| `fireworks-tech-graph/SKILL.md`（opencode + kimi） | description 补中文触发词（降低"指向了但匹配不到"的风险） |
| `pil-table-render/SKILL.md`（新建，opencode + kimi + zcode junction） | 见上表 |
| `scripts/check_skill_pointers.py`（新建） | 指向校验 |
| `scripts/check_article.py`（新建） | 发布前门禁（skill Workflow B 第 9 步强制） |

## 3. 校验结果

- `check_skill_pointers.py`：skill 引用 7、章节引用 6、文件引用 23、类名 28 —— **0 断链**；2 条告警 = 主知识库 `E:\project\team-share\` **本机未 clone**（旧版 skill 就指向这里，属既有事实，非本次引入）。
  - 首次运行抓到 1 处真实断链：我写的「动画/静态双版 SVG 站点架构（v4）」不是 blueprint 实际标题的子串 → 已改正。这正是该脚本要防的问题。
- `check_article.py` 现有站点基线（只报告，不修）：

| 站点 | 页数 | 结果 | 失败项（均为既有问题，经人工复核非误报） |
|---|---|---|---|
| advanced-design | 9 | ✅ PASS | — |
| fusion-compiler-migration | 8 | ✗ | [H] 1 页标题未编号（`### ①` 类） |
| hv2m23-agent-vm-workflow | 9 | ✗ | [H] 1 页 4 个标题未编号 |
| synthesis-integration-flow-guide | 14 | ✗ | [H] 2 页 h4 未编号 |
| hk1v11-synthesis-postpt-practice | 24 | ✗ | [H] 19 页各 1 个 `## 交叉引用` 未编号 |
| hk1v11-lc-cpuwr-history | 9 | ✗ | [T] 8 页**无 TOC 折叠**；[H] 1 页 |
| hk1v11-longcode-420b-verification | 11 | ✗ | [T] 10 页**无 TOC 折叠**；[N] 导航 11 项 > 10；[H] 1 页 |
| site-template | 2 | ✗ | [S] 骨架无签名（预期：复制建站后新页面必须补签名，门禁据此强制） |

## 4. 演练（新旧版同题对比，2026-11-02）

题目：用 skill 发布单页测试文章「HK1V11 时钟域速览」（含架构图 + 统计条 + 待跟进问题卡），各由一个无本对话背景的子代理执行；只允许写各自的 `_rehearsal_*` 目录，不碰 git。

| 维度 | 旧版 skill（bak，563 行） | 新版 skill（精简版） |
|---|---|---|
| 骨架来源 | **没有复制模板**，参考 3 个旧站，打算照 skill 内嵌代码手写页面 | 第一步 `cp -r site-template`，只改 README 列出的内容槽 |
| 调用的 skill | blueprint-ui-style → fireworks-tech-graph | team-share → fireworks-tech-graph → blueprint-ui-style |
| 架构图 | 静态 SVG 已画；动画版生成器未写 | 静态版 + 动画版（确定性生成器，`validate_kit_v4` ALL PASS） |
| 页面产出 | **0 页**（写到一半中断） | 1 页 |
| `check_article.py` | **FAIL**（[P] 无页面、[N] 无导航） | **PASS，exit 0** |

结论：「指向别的 skill」在新版里**实际被执行了**（fireworks、blueprint 都按指向加载）；旧版的失败模式正是精简要解决的"照贴的代码手写骨架"。演练产物目录已删除（未入库）。

### 演练暴露的问题与处置

| 问题 | 来源 | 处置 |
|---|---|---|
| 门禁 [L] 只认 HTML `<img`，markdown `![]()` 图片漏检 | 新版演练 | ✅ 已修（同时识别 markdown 图片），抽测 3 站无误伤 |
| 门禁在 0 页面时只报"无导航"，未明确报"无页面" | 旧版演练 | ✅ 已修，新增 [P] 项 |
| 流光点速度两套口径（fireworks 150pt/s vs blueprint ≥2.4s/程）、缩放动画、扫光周期、动画目录四处冲突 | 旧版演练 + 子代理核查 | ✅ 单一来源化：blueprint v4 为唯一数值来源，fireworks 改为通用技法 + 指向 |
| fireworks 引用不存在的脚本（generate-diagram.sh 等） | 两次演练都踩到 | ✅ 已删除引用，改为正文已有的 ElementTree / cairosvg 做法 |
| 模板 `site.js` 仍用 `?v=Date.now()` 重播图片（v4 已禁止） | 新版演练 | ⏳ 待办：改模板固定文件需全仓库统一处理，记入 PAGE_FX §7 推广前置 |
| 模板 NAV 写 `'./index.html'` 导致当前页不高亮 | 新版演练 | ⏳ 待办（同上） |
| 模板缺 `anim/validate_kit_v4.py`，MOTION_KIT §8 却要求跑 | 新版演练 | ⏳ 待办（同上） |
| 全仓库 `fx.js?v=` 实际 v4/v6/v7 三值并存 | 两次演练 | ⏳ v2 推广时统一（PAGE_FX §7） |
| 旧版 lightbox 用 `transform:scale` 与 blueprint v4.3 冲突 | 旧版演练 | ✅ 新版已不内嵌 lightbox 代码，以模板 `lightbox.js` 为准 |

<!-- ymzhu 2026-11-02 19:35 -->

## 5. 全仓整改与终验（2026-11-02 22:10 收官）

按新版 skill 对全部存量站整改完毕，四包并行（420b 收尾 / lc-cpuwr / postpt / 三小站），每包独立门禁验收：

| 站 | 整改内容 | 门禁 |
|---|---|---|
| site-template | 补缓存 meta 三条 / 补 lightbox.js 引用 / site.js 删 ?v=Date.now 重播（归口 fx.js v4.1）/ NAV 高亮归一化 / 补 anim/validate_kit_v4.py / 引擎 v2 | PASS |
| 420b | 10 页 TOC 折叠（逐字节同构）/ 导航 11→10 / h4 补号 / dummy 图短箭头列车删 / 改过的 SVG 引用 ?v 升 20261102 | PASS |
| lc-cpuwr | 8 页 TOC 折叠 / regmap h4 补号 / beat 图扫光带→文字光带（像素亮度分桶验证：光带列 +27~+69、带外 ±0） | PASS |
| postpt | 19 页 175 个标题补号（ch10 全量重编 + 11 处交叉引用同步）/ 7 页补 lightbox / 4 张 SVG→文字光带（同刻含/删光带差分隔离验证：白化像素仅在字形内） | PASS |
| fusion / hv2m23 / synth-guide | 3 页标题补号（①②③ 保留）/ 2 个孤儿动画图补静态版（幂等生成器 + text/几何多重集自检）→ check_anim_pairs 全仓 44/44 OK | 三站 PASS |

终验（2026-11-02 22:05）：8/8 站 `check_article.py` PASS；引擎 9 副本 md5 唯一（tj 除外）；`check_skill_pointers.py` 0 断链；fx 引用全仓统一 `?v=5/?v=8`。遗留项见 `PAGE_FX.md` §8（均不阻塞）。
