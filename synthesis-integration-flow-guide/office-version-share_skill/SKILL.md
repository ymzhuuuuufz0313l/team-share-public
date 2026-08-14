---
name: office-version-share
description: Agent 创建/修改 Office 文件（PPT / Word / Excel）时的版本号与 share 副本管理规则。Trigger on: 创建或修改 .pptx / .docx / .xlsx、"PPT"、"演示文稿"、"版本号"、"share 版本"、"分享版本"、"pptx 加密"、"DLP 加密读不了"。
---

# Office 文件：版本号 + share 副本规则

## 背景（为什么需要这个规则）

本机有 DLP 透明加密：**Office 应用（PowerPoint / Word / Excel）保存过的文件会被加密**，python（python-pptx / python-docx / openpyxl）和标准工具读不了；而 agent 用 python 写出的文件是明文、可继续读写的。

因此约定：**编号版本是 agent 的工作底稿（永远明文），share 副本给用户打开/分享（被加密也无所谓，是消耗品）**。这样 agent 每次都能读到最新编号版本并递增，用户只传播 share 副本，原始版本永远不会被加密锁死。

## 命名规则（强制）

- Agent 创建的 Office 文件**必须带版本号**：`<名称>_v<N>.<ext>`，N 从 1 开始、每次修改递增。
  例：`BE_Review_HV2M23_20260813_v21.pptx`
- 同时维护一个 **share 副本**：`share_<名称>.<ext>`（share 前缀放最前，目录里排最前、一眼可见），内容 = 最新编号版本的完整拷贝。
  例：`share_BE_Review_HV2M23_20260813.pptx`
- 用户只分享 / 打开 share 副本；编号版本不对外。

## Agent 工作流

1. **新建**：写 `_v1`，再复制出 `_share`。
2. **修改**：
   1. 找最新编号版本 `_vN`——按文件名版本号排序，**不要按修改时间**（share 副本时间更新但可能已加密不可读）。
   2. 检查 `_share` 是否被用户手改过（见下节）；有改动先合并进新版本。
   3. 以 `_vN` 为底写 `_v(N+1)`（**不覆盖旧编号版本**）。
   4. 用 `_v(N+1)` 复制覆盖 `_share`。若 share 正被 Office 占用（存在 `~$<名称>` 锁文件 / 写入 PermissionError），提示用户关闭后重试，不要硬写。
3. **修改用户给的未编号文件**时：先复制为 `_v1` 再改，原文件保持不动。
4. 每次出新版在项目的变更记录（如 `CHANGES.md`）里写清该版本改了什么。

## 用户改动检测（share 已被加密时）

share 副本被 Office 打开另存后 python 读不了，但 **Office COM 可读**。判断用户是否手改过：

1. 用 COM 分别导出 share 副本和最新编号版本的全部文本，做 diff：
   - PowerPoint：`Presentations.Open(path, True, False, False)`（ReadOnly, Untitled, WithWindow=False），遍历 `Slides → Shapes`，文本取 `TextFrame.TextRange.Text`，表格遍历 `Table.Cell(r,c)`；几何取 shape 的 `Left/Top/Width/Height` 和 `TextRange.BoundTop/BoundHeight`。
   - Word / Excel 同理（`Documents.Open` / `Workbooks.Open`，只读 + 不可见）。
   - 脚本 stdout 重定向由 shell 落盘；VBS 输出是系统 ANSI 编码，中文呈乱码但**不影响 diff**（两份导出编码一致）。
2. diff 为空 → 用户无手改（或仅查看），直接递增版本。
3. 有差异 → 先把差异合并进新版本，再递增、刷新 share。
4. 参考实现（HV2M23 项目）：`_dump_ppt_text.vbs`（全文导出）、`_measure_ppt.vbs`（渲染边界测量），曾用此法把用户在 PowerPoint 里的居中手改复现回 agent 版本。

## 注意

- 不要试图用 python 读 Office 保存过的文件：先 `head -c 4` 看是不是 `PK` 头，不是即已加密，走 COM。
- 不要编辑编号旧版本；一切增量都出新版本号。
- share 副本可以随时用最新编号版本重建，丢了/坏了不重要。
