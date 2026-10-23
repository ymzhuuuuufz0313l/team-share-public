# screenshot-report 插件（T7 终审合稿版 + v1.5 被动模式）

本地「截图→报告」DSH 函数插件：用户**明确要求**时，把会话里贴入的截图落盘并按体检判据**保图**（自动裁剪引用）或**作图**（本地 OCR 提数 + 固定模板重绘成 blueprint 表格图，后台执行）。**判断与执行分离**：模型只判断，工具只执行；表格数据只信本地 OCR，绝不虚构。

> **v1.5 被动模式（2026-10-22）**：①**默认零动作**——用户贴图只分析/提问时，插件完全沉默（不存图/不判图/不调工具/不进作图阶段/不花时间）；②**明示同意才动作**——存图先确认去向（默认建议收件箱 screenshot-inbox）、作图必须明示提出；③**同意后全部后台**——经 subagent 执行，主对话只回"已提交后台，完成后通知"，质量问题在完成通知标 [待确认] 不回主对话追问。v1.3 收件箱与 v1.4 判定判据保留为后台执行规范。详见 architecture.md §12 + §16 v1.5。

> **v1.3 贴图即存（已废除）**：自动落盘/自动评价/自动执行模式经实机验证与用户意图不符（贴图分析被卡 14 分钟），已由 **v1.5 被动模式**取代。见 §16 v1.3（历史记录）与 §16 v1.5。

> **v1.2 交互三原则（2026-10-22）**：**后台执行**（工作流交后台有视觉 subagent，不阻塞主对话）+ **安静回复**（可见输出最多一句"已存图（判定：…）"，产物走 present 卡片）。详见 architecture.md §12 + §16 v1.2。

> **v1.1 视觉降级（2026-10-22）**：调用模型无视觉能力（图片不可见）时，系统提示指示改派有视觉的 subagent 代做判图（首选 `zai-coding-cn/glm-5.3-flash`，备选 `xxw/Qwen`），返回富描述符 JSON 后主模型继续调工具执行——**工具层零 LLM 红线不变**。详见 architecture.md §12 工作流第 6 步 + §16 v1.1。

> 合稿说明：本目录是四路独立实现（impl-a/b/c/d）经三路对账 + T7 终审的**正式合稿**——基座 impl-d（契约语义四路最对：async fs/required 齐全/附件三重回退/领域结果正确 return），移植 impl-b 的向量化 self_check（四路最严），修 P1（sp.section 真实签名 `{name, order, text}`，DSH 源码 system-prompt/src/index.ts:52-76）/P3（§12 系统提示逐字全文）/M5（CROP_EMPTY 改 return）等。详见 `../docs/final-verdict.md`。

## 形态
纯 ESM、零 npm 依赖（profile 无 dsh-tools，走裸 `ctx.tools.register` + 完整 JSON Schema parameters + execute 内 args 自校验）。入口 `index.js` 导出 `name / inject / apply(ctx, config)`；`apply` 依次注册 5 个工具 + 可选系统提示段（`sp.section({name, order:900, text})`，DSH 真实签名）。**挂载由队长执行**（见下），不 pnpm publish。

## 五工具（一句话）
- `save_screenshot`：把最近一张截图按 `<MMDD>_<slug>_<n>.<ext>` 落盘到 **inbox（默认收件箱，v1.5）/ site / daily / report**（日报域双写），返回路径+体检+引用+中央图库接口字段。
- `crop_image`：分数框裁剪 / `auto_trim` 自动裁白边，重编码 PNG + 完整体检；0 面积裁剪返回 `ok:false, code:'CROP_EMPTY'`（领域结果）。
- `extract_table`：本地 RapidOCR（**1.2.3 已装，勿 pip install**）表格抽取，输出结构化 JSON + 置信度（不进 LLM）。
- `render_chart`：固定模板族（MVP=table，1-2 层表头 + [] 分隔缝 + violation/window/plain 判色，S=4 超采样，向量化自检），blueprint 画风。
- `render_diagram`：Phase 2 桩，固定返回 `NOT_IMPLEMENTED`（不画占位图）。

## SSRP_* 配置（§5，env > row config > 默认）
`SSRP_TEAM_SHARE_ROOT` / `SSRP_DAILY_ROOT` / `SSRP_DAILY_GITHUB_IMAGES_ROOT` / `SSRP_REPORT_ROOT` / `SSRP_INBOX`（收件箱，v1.5）／4+1 个根；`SSRP_VENV_PYTHON` / `SSRP_BACKPPT_SCRIPT_DIR`（Python 桥）；`SSRP_DAILY_WRITE_GITHUB`（日报双写开关）；`SSRP_CENTRAL_GALLERY_ROOT` / `SSRP_THEMES`；`DSH_HOME`（源图宿主目录兜底）。默认值即真实生产路径；per-site 图片目录映射 `siteImageDirs`（advanced-design→image 等 6 站，默认 assets，无尾斜杠）。

## 安装 / 卸载（队长操作）
把本目录 `cordis.patch.yml` 片段追加进 `~/.dsh/profiles/desktop/cordis.patch.yml`（`insert:` 同形先例 mcp-github），**重启 DSH Desktop** 生效（以重启为验收口径）；id 用独立名 `screenshot-report`（防跨 bundle 同名静默丢弃）。卸载=删除该条目再重启。兜底：Loader 不认 `file://` 时把 `"screenshot-report": "file:E:/screenshot-report-plugin/plugin"` 加进 profile package.json dependencies。

## 测试（§14.4）
```bash
node test/smoke.mjs            # S0–S6 全部通过，退出码 0（离线 mock，4 根指到 test/tmp-sandbox/）
node test/smoke.mjs save       # S1+S2：落盘/防撞/双写/引用/无图报错
node test/smoke.mjs render     # S5：模板渲染/自检/色板像素探针/[] 分隔缝
```
含 T7 增补断言：S0e sp.section 签名形状（P1 回归锁）、S3f CROP_EMPTY 领域返回、S5f 分隔缝渲染。
