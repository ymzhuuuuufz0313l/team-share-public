# MOTION_KIT v4 — synthesis-integration-flow-guide 站动效规范

> 上位架构 = `blueprint-ui-style` skill「动画/静态双版 SVG 站点架构（v4）」章。
> 本站 v4 落地口径与兄弟站（`hk1v11-longcode-420b-verification` 为 canonical）一致，但**本站只有一套 anim 目录**：
> 静态 SVG 在 `image/`，动画孪生版在 `image/anim/`，同名同尺寸。
> 本文件是本站 14 张动效图 + 14 张静态图的唯一事实源；机器校验 = `image/tools/validate_kit_v4.py`。

## 0. 铁律（不变量，违反即 FAIL）

1. **静态版是事实源**：`image/<name>.svg` 只读口径，几何/文字/颜色以它为准；`image/anim/<name>.svg` 由它派生。
2. **几何与文字零漂移**：`<svg>` 的 `width` / `height` / `viewBox` 与静态版**完全一致**；`<text>` 多重集与静态版相等（当前 14/14 相等）。
3. **纯 CSS in-SVG**：允许 `<style>` 块、`class` 属性、内联 `style`（animation-delay 等）、`@keyframes`；
   **禁止** `<script>`、SMIL `<animate>`、任何外部资源（`href`/`xlink:href` 指向外部文件）。
4. **reduced-motion 安全**：动画版必须含**且仅含一处**：

   ```css
   @media (prefers-reduced-motion: reduce){*, *::before, *::after{animation:none !important;transition:none !important;}}
   ```

   静态版无动画，不要求该块（有也无害）。
5. **单位合规**：根元素 `width`/`height` 必须是无单位数值；**禁止 `pt`/`mm`/`cm`/`in`**
   （历史缺陷：`script-flow-overview` 曾为 `1203pt × 2528pt`，已改 `1203 × 2528`，viewBox 未动）。
6. **CSS 必须良构**：不许留"游离残片"（例如删掉 `@keyframes` 头行后剩下的 ` 50% { opacity: 0.25; } }`）。
   浏览器会整条丢弃这类残片，属生成/手改残留，不是效果。
7. **生成器幂等**：同输入重跑字节一致；生成器文件尾必须带签名 `# ymzhu YYYY-MM-DD HH:MM`。
8. **覆盖前归档**：生成脚本写文件前必须调用 `image/tools/_archive.py` 的 `snapshot(out_path)`，
   保证旧版本在 `image/archive/<YYYYMMDD>/` 有可浏览快照（见 `image/archive/README.md`）。
9. **缓存打击**：HTML 里引用 anim SVG 必须带 `?v=YYYYMMDD`；SVG 内容变更的当天要把引用版本号一起 bump。
   当前全站 13 处引用统一为 `?v=20261117`。

## 1. 文件清单（14 组）

| 静态版 | 动画版 | keyframes | 说明 |
|---|---|---|---|
| `image/30_postpt_setup_2p.svg` | `image/anim/30_postpt_setup_2p.svg` | 1（rowIn） | PT setup 违例总表 2P |
| `image/30_postpt_hold_2p.svg` | `image/anim/30_postpt_hold_2p.svg` | 1 | PT hold 2P |
| `image/30_postpt_trans_2p.svg` | `image/anim/30_postpt_trans_2p.svg` | 1 | PT trans 2P |
| `image/30_postpt_physkew_2p.svg` | `image/anim/30_postpt_physkew_2p.svg` | 1 | PT phy busskew 2P |
| `image/31_postpt_setup_1p.svg` | `image/anim/31_postpt_setup_1p.svg` | 1 | PT setup 1P |
| `image/31_postpt_hold_1p.svg` | `image/anim/31_postpt_hold_1p.svg` | 1 | PT hold 1P |
| `image/31_postpt_trans_1p.svg` | `image/anim/31_postpt_trans_1p.svg` | 1 | PT trans 1P |
| `image/31_postpt_physkew_1p.svg` | `image/anim/31_postpt_physkew_1p.svg` | 1 | PT phy busskew 1P |
| `image/30_postpt_physkew_1p.svg` | `image/anim/30_postpt_physkew_1p.svg` | 1 | 备用 1P phy（页面未引用） |
| `image/30_postpt_trans_1p.svg` | `image/anim/30_postpt_trans_1p.svg` | 1 | 备用 1P trans（页面未引用） |
| `image/33_postpt_sdskew_margin_2p.svg` | `image/anim/33_postpt_sdskew_margin_2p.svg` | 1 | SD skew margin 2P |
| `image/34_postpt_sdskew_margin_1p.svg` | `image/anim/34_postpt_sdskew_margin_1p.svg` | 1 | SD skew margin 1P |
| `image/38_buf_type.svg` | `image/anim/38_buf_type.svg` | 2（revIn/br） | input/output buf type 统计 |
| `image/script-flow-overview.svg` | `image/anim/script-flow-overview.svg` | 24（march/pkt1..22/breath） | 脚本调用关系总图（唯一非表格图） |

## 2. 校验怎么跑

```bash
# Kit 契约（XML 良构 / 无 script / 无外链 / keyframes / reduced-motion 唯一 / 单位 / 与静态版几何+文字一致）
python image/tools/validate_kit_v4.py

# 幂等修正（删游离 CSS 残片、补 reduced-motion、pt→px）
python image/tools/normalize_kit_v4.py --check
python image/tools/normalize_kit_v4.py --apply
```

2026-11-17 基线：`validate_kit_v4.py` → 14 张全 PASS；`normalize_kit_v4.py --check` → 不合规 0 个。

## 3. 本站与 canonical 的差异（有意为之，勿"对齐"掉）

- 本站 anim 目录是 `image/anim/`（不是 `anim/` 或 `images/anim/`），生成器在 `image/tools/`。
- 表格类图动效策略是"逐行入场（rowIn）+ 数值单元格呼吸"的子集，没有 canonical 的扫光/脉冲全家桶；
  2026-11-17 之前部分图的手写呼吸 CSS 被后续手改删掉，残留了孤立 CSS 片段（已清理，见铁律 6）。
- `image/anim/make_static_30_postpt_*.py` 是"从动画版剥离动画生成静态版"的反向脚本：
  剥 CSS 时会连带删掉 `prefers-reduced-motion` 块，因此**动画版必须自带该块**（铁律 4 的由来）。

<!-- ymzhu 2026-11-17 19:43 -->
