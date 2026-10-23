# final-verdict · T7 终审合稿结论（plugin/ 正式版）

> 终审人：final（GLM5.3 MAX·思考强度 MAX）｜ 2026-10-21 ｜ 对象：四路实现（impl-a/b/c/docs 外的根级 impl-d）→ **合稿 `E:/screenshot-report-plugin/plugin/`**
> 性质：终审记录（过程产物）。**实现依据与合稿结果以 `plugin/` 代码 + `docs/architecture.md` v1.0.1 为准**。
> 方法：**两遍法**——第一遍不读任何 QWEN 审查产物，独立抽样读四路源码 + DSH 源码核验关键 API；第二遍读 7 份审查（review-impl-1/2/3 + review-impla/b/c/d-1/2）对账，矛盾以源码裁决、未盲信任何一方稿件。

---

## 0. 一句话结论

**四路交叉验证的硬锚点全部兑现，合稿完成并通过 55/55 全量验收 + 真实校准图端到端演练。** 合稿 = **impl-d 基座** + **impl-b 向量化 self_check 移植** + **7 项终审修正**（含四路共性 HIGH P1 sp.section 签名、四路共性 MEDIUM CROP_EMPTY 返回语义）。plugin/ 即队长挂载对象（cordis.patch.yml 片段随附）。

## 1. 第一遍独立结论（未读审查产物时形成，后经第二遍交叉印证）

1. **impl-d 为基座**（本人逐文件读源码判定）：契约语义四路最对——领域结果三处正确 return（render_chart 自检失败/render_diagram 桩/extract_table ENGINE_MISSING）、output 带 template+source_data_digest、required 列表齐全、async fs/promises 全程、附件字段三重回退（attachmentId??id??block.attachmentId）、Python 桥两级（ctx.subprocess 优先+spawn 兜底）带 IO 预算、config 三级来源 + siteImageDirs 无尾斜杠、模块结构最贴 §4 目录树（无额外 py-bridge/toolkit 模块——§4 树本就没有这些文件）。
2. **P1 我亲自从 DSH 源码钉死**：`PromptSection = {name(唯一), order(必填·有限数), text, complete?}`（`packages/core/system-prompt/src/index.ts:52-76`），`section()` 对非有限 order **抛 TypeError**（:448-451）；先例 `plugins/dsh-stock-watch-zhu/index.js:691-694` 用 `{name, order:200, text}`。四路写法（{title,body}/裸串/{when,content,priority}/{name,title,content}）真机上不是"注入错文本"而是**直接抛错**——比审查稿描述的还严重。
3. impl-a 两处真伤（JS+py 双拒 `[]` 分隔缝；self_check 无右内缘竖带）、impl-c 五处真伤（inject=['tools']、render/diagram 两处超时 60000/30000、SELF_CHECK_FAILED/NOT_IMPLEMENTED 两处 throw、render output 缺 template+source_data_digest、全同步 fs）——均本人读源码证实。
4. impl-b 亮点：self_check 向量化（ink 距离 <30 判文字 + 数据区四边 3px 环带 + 右内缘竖带）四路最严、最贴 §11.5 字面。
5. impl-d 两伤：位置越规（根 impl-d/ 非 docs/impl-d/，P2）+ 系统提示自拟精简版（P3）；外加 P9（INVALID_ATTACHMENT_ID 私有码 + imageHostPath 传裸字符串——`attachment/src/index.ts:174` 签名是 `imageHostPath(ref: ImageAttachmentRef)`，本人核验）。

## 2. 第二遍对账（7 份审查 × 我的源码裁决）

- **review-impl-1（QWEN①）/ review-impl-2（QWEN②）**：结论"impl-d≈impl-b 最贴 v1.0.1"与我的第一遍一致，其发现清单经我抽源码复核**全部成立**（含 rev-2 补漏的 impl-a 2 MEDIUM、impl-c 3 MEDIUM、四路共性 CROP_EMPTY）。
- **review-impl-3（架构师）**：P1-P12 大多成立（P1 我已源码级独立证实）；但其"source_data_digest 四路全过"为事实错误（impl-c 缺，Ge1/Ge2 与我均证实）、"基座取 a 或 b"建议**不采纳**——impl-a 有 2 MEDIUM（[] 缝双拒、self_check 缺右带）需修，而 impl-d 的两伤（位置、提示文本）在合稿场景下自动消解（合稿就是搬到 plugin/ 且 index.js 必然重写），d 的契约/质量优势（rev-1/rev-2 双审与我三方一致）压倒性。
- **review-impld-1/2、implb/c/a-1/2**：各路 MINOR 清单与我的读码一致；采纳项见 §3。
- **review-archcheck-1/2（Ge 轮）**：对架构师报告的补漏（A1-A5）与我第一遍独立发现完全撞合——方法学交叉验证成功。

**裁决原则**：所有"返回 vs 抛错"以 architecture.md §3.2/§6.3/§6.4/§6.5/§11.2 为准（领域结果 return）；所有签名/形状以 DSH 源码为准；所有数值锚点（阈值/色板/像素探针/引用串）零改动。

## 3. 合稿说明（plugin/ 从哪路继承 / 合并了什么 / 改了什么）

| 部分 | 来源 | 说明 |
|---|---|---|
| 整体基座（index/tools/report/py/templates/config/package） | **impl-d** | 逐文件复制后做下列修正；模块结构维持 d 形态（单 resolve-target.js 含 目标解析/命名/引用/源图/桥——最贴 §4 树） |
| self_check（py/render_chart.py） | **impl-b 移植** | 向量化 ink 距离（<30 判文字）+ 数据区四边 3px 环带 + 右内缘竖带（pad+2px 容差）；替换 d 的角点+环带白名单版（四路最严 → 合稿采最严） |
| 系统提示 SYSTEM_PROMPT | **architecture.md §12 逐字** | 修 P3：富描述符 JSON/summary/Laplacian 门/present/注入护栏全量恢复 |
| **修 P1** sp.section 签名 | 终审修正 | `ctx.effect(() => sp.section({name:'screenshot-report', order:900, text}), 'screenshot-report-prompt')`——真实签名（源码:52-76/448-451 + stock-watch 先例），四路原稿真机必抛 TypeError |
| **修 M5/P9-adjacent** CROP_EMPTY | 终审修正 | crop-image.js 改 return `{ok:false, code:'CROP_EMPTY', …全字段}`（§11.2:609 领域结果）；schema 的 bytes/width/height 放宽 nullable 以容纳失败形态（对齐 render_chart 先例） |
| **修 P9** | 终审修正 | INVALID_ATTACHMENT_ID 并入 INVALID_ARGS（无私有码）；imageHostPath 改传 `ImageAttachmentRef` 形状对象（save 传全 ref、resolveSource 传 {attachmentId}） |
| **修 §6.5 逐字** | 终审修正 | render_diagram 的 description 与 planned 文本恢复 architecture.md 逐字契约 |
| SELF_CHECK_FAILED 返回形态 | 终审修正 | copies 由 [primary] 改 []（自检失败产物未写盘，勿列不存在文件） |
| smoke.mjs 增强 | 终审增补 | d 的 47 断言全保留 + S0e（sp.section 形状 5 断言，P1 回归锁）+ S3f（CROP_EMPTY 领域返回）+ S5f（[] 分隔缝渲染，锁死 impl-a 偏离不复现）= **55 断言** |
| e2e-demo.mjs | 终审新增 | tests/fixtures 校准图端到端演练（非契约）：贴图→save→判断→redraw（OCR→render）/keep（auto_trim）→引用 |
| README.md / cordis.patch.yml | 重写 | 合稿版部署说明（装/卸/env/工具/测试）+ §3.3 挂载片段（id 独立命名注记）；.gitignore（tmp-sandbox/__pycache__） |
| themes.json / make_fixtures.py / _py_probe.py / image_metrics.py / crop_image.py / ocr_table.py | impl-d 原样 | 四路字节级一致（themes）或 d 版正确（py 契约逐项对 v1.0.1 核过） |

**不采纳项**：架构师"基座 a/b"建议（理由见 §2）；rev-1"CROP_EMPTY 保留 throw 同步改 arch"选项（arch §11.2 白纸黑字 return，四路 py 侧也全 return，JS 侧统一到 return）；impl-c 的 inject/超时/throw 形态（全按 v1.0.1）；impl-a 的 [] 拒绝与弱 self_check（§6.4/§11.5 明文相反）。

## 4. 验收记录（在案）

| # | 命令 | 结果 |
|---|---|---|
| A1 | `cd E:/screenshot-report-plugin/plugin && node test/smoke.mjs` | **55 passed, 0 failed, exit 0**（S0 注册+P1 签名 / S1 落盘+reference 精确串 / S2 防撞+双写+绝对 URL / S3 裁剪 450×315·200×100·边界 flags·CROP_EMPTY 返回 / S4 OCR 实跑 mean=0.7703 与 T4 基线逐位一致 / S5 三像素探针 (28,37,52)/(239,224,218)/(14,124,107)±8 + [] 缝 / S6 桩 return） |
| A2 | `node test/e2e-demo.mjs`（tests/fixtures 校准图） | **exit 0**：table_like 贴图→save 1200×800→extract n_rows=33 **mean=0.7268 与 t42 校准值逐位一致**→判断 redraw（laplacian=3758≥50）→render 2172×3041 self_check=passed→`<img src="assets/…">`/`![…](…)` 引用；padding 800×600→auto_trim **401×189 与 t29 记录的 getbbox(200,175,601,364) 精确吻合** |
| A3 | 红线复查 | plugin/ 零 npm 依赖（package.json 无 dependencies）、未挂载（真 cordis.patch.yml 未动）、样式库只 import（G.S=4 运行期）、rapidocr 1.2.3 未动、只写 plugin/ 与 docs/ |

## 5. 遗留问题与下一步

**队长真机验收清单（挂载后，§14.5）**：
1. 追加 `plugin/cordis.patch.yml` 片段 → 重启 DSH Desktop → 日志出现 screenshot-report；
2. 新对话贴真实截图 → "存到 advanced-design 站，slug demo" → 断言 `E:/project/team-share-public/advanced-design/image/1021_demo_1.png`（per-site 映射 image/）出现且可直开；
3. **确认提示段已注入**（对话里问模型是否知道 save_screenshot 工作流——P1 修复的真机验证点）；
4. subprocess 30 秒可达性实验（t41 §5，顺手确认两级桥首选路径）。

**遗留（不阻塞）**：
- team goal 文本"中央图库 E:\assets"仍未更正（D6，实机为空目录；正确 = `E:/project/team-share-public/assets/`）；
- OCR 阈值绑定 rapidocr 1.2.3：换引擎/版本须重跑 `tests/probe_ocr_calib.py` 重校（§11.3）；
- ragged_rows（OCR 列对齐尽力而为）→ 喂 render_chart 前需模型整形为等宽（e2e-demo 已示范；富描述符 structure 字段引导已进系统提示）；
- impl-d 仍在根目录越规位置（P2）——合稿已取材完毕，是否搬移/清理 impl-* 四路原件由队长定夺；
- Phase 2 backlog：render_diagram 执行体、T3/T4/T5 模板族、中央图库写入、交互式 hotspot、超分。

## 6. 独立性声明

第一遍未读 review-impl-1/2/3、review-impla/b/c/d-1/2、review-archcheck-1/2，仅读四路源码 + architecture.md v1.0.1 + DSH 源码 + 实机；第二遍逐份对账，关键结论（P1 签名、imageHostPath 形状、impl-a/c 偏差、b self_check 优势）均以本人源码核验为准。本任务只写 `plugin/` 与 `docs/final-verdict.md`。

<!-- final（T7·GLM5.3 MAX）2026-10-21 · 两遍法终审合稿 · 基座 impl-d + b self_check + 7 项修正 · 验收 55/55 + E2E 校准图闭环 -->
