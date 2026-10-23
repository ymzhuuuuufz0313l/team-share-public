# 真机验收记录（2026-10-22 · 三张真实截图）

> 性质：队长验收记录（事实档），供 architecture.md §16 与后续维护引用。所有数值为实跑输出。

## 截图 1：PT hold 报告上半段（gvim，深色主题）

- 源：`objects/72/72c624eebb5ea9077db9425be32a88bebdf2e861fb8f8c5ad8c8e67a48828495`
- 原始尺寸：**1211×839** PNG RGB
- image_metrics：laplacian_var=2473.5155、short_edge=839、aspect=1.443385、too_small=false、flags=[]
- auto_trim：**零裁剪**（1211×839 → 1211×839）——深色主题无白边可去（正确行为）
- 判定：**keep**（PT 时序报告为文本报告，非模板族；信息在完整上下文）
- 落盘：`advanced-design/image/1022_hold-rpt_1.png`（引用 `<img src="/image/1022_hold-rpt_1.png">`）
- 引用口径注：根相对 `/image/…` 是 advanced-design 站的实际惯例（t32 站点盘点实测）；§7.3 的文件相对式为通用默认，本站按 per-site 惯例取根相对，两者静态服务下均可达。

## 截图 2：PT hold 报告下半段（同窗口，241-274 行，含 slack VIOLATED -0.017941）

- 源：`objects/d0/d0273491e60ce31238a826a6ce0af23bf318efd655ac4ff93b9ed51d5678e559`
- 原始尺寸：**1220×846** PNG RGB
- image_metrics：laplacian_var=2889.0663、short_edge=846、aspect=1.44208、too_small=false、flags=[]
- auto_trim：零裁剪（同上）
- 判定：**keep**（同上；两段之间隔 200+ 行路径详情，单张不完整，redraw 有丢信息风险）
- 落盘：`advanced-design/image/1022_hold-rpt_2.png`（`<img src="/image/1022_hold-rpt_2.png">`）

## 截图 3：PT 违例汇总 CSV 表格（浏览器，hold.rpt 汇总页）

- 源：`objects/48/48d4d6b569457ec336cd097bc841c080d421f85981a2973ca4eec582bef0e717`
- 原始尺寸：**1989×1154** PNG RGB
- image_metrics：laplacian_var=1583.428、short_edge=1154、aspect=1.72357、too_small=false、flags=[]
- extract_table（RapidOCR 1.2.3 实跑）：n_rows=40、n_cols_max=15、**cell_confidence_mean=0.7966**（>0.70 门）、frac_low_confidence=0.0521（<0.30 门）、warnings=[ragged_rows, low_confidence_cells:10]、**unreliable=false**
- 抽取质量：RX_CLK 行全命中（20/-0.031806/…/52/-0.146213/32/-0.217263）、hold.rpt 汇总行、OSC_CLK 12/12 违例——核心数据正确；但 ragged（浏览器标签栏混入、行号列混入、`12C_CLK`/`I2C_CLK` 误读、`0,010942` 逗号误读）→ **喂 render_chart 前需模型整形**（§12 既有规则）
- 判定候选：**redraw（table 族）**——整形后可出 to-signoff 同款表格图（本张留作 Phase 2 首个真机用例）

## 结论与增量

- 落盘/体检/防撞/引用链路全部真机可用；深色主题 auto_trim 局限已固化进 §12（"深色/非白底截图 auto_trim 常无效，勿依赖"）
- 三图未 push（teamshare `??` 未跟踪），进站页面引用待用户编辑
- 记录口径：本档为真机事实档；与 final-verdict §5 遗留清单并行维护

<!-- 队长验收记录 2026-10-22 -->
