# docs/ 目录规约（队长定 · 防先行产物干扰后续任务）

> 背景：暂停期 QWEN 成员先行产出大量 prep-* 脏活素材。本规约保证这些先行产物不会污染或偏置后续 GLM 判定任务与四路实现。

## 权威层级（冲突时的唯一裁决序）

1. **docs/architecture.md（T4 定稿 v1.0 及之后）** —— 实现的唯一依据
2. 研究定稿 `E:/screenshot-report-research/00_汇总_截图报告插件.md`（v3）—— 架构的输入基线
3. 其余一切 docs/ 文件均为**过程产物**（review-* 审查报告 / prep-* 预习素材 / final-* 终审记录），**不是依据**

## 硬规则

- **prep-\* 一律非权威**：每份 prep-* 首行必须自标"非权威素材……冲突以 architecture.md 定稿为准"；其中的数值/路径/API，写码前必须自行回源核实。
- **GLM 判定任务两遍法（T4 定稿 / T7 终审 / T6c 对账）**：第一遍**不读任何 QWEN 产物**（review-\* / prep-\*），独立读 architecture.md / 源码 / 研究定稿形成自己的结论；第二遍才读 QWEN 产物对账（我独有 / 稿独有 / 共有 / 矛盾，矛盾以源证据裁决）。**禁止引 QWEN 稿当论据。**
- **四路实现只认 architecture.md**：impl-\*/ 里的代码必须可溯源到定稿条款；prep-\* 只能当导航，不得当规范。
- **审查员独立性**：rev-1 与 rev-2 的审查轮互相禁读对方报告；prep-review-checklist 只是覆盖面底线，不替代各自独立判断。
- 过程产物不删不改他人文件；每个成员只写自己任务声明的文件。

## 队长环境核验记录（机器可验证事实；T4 定稿时须折叠进 architecture.md）

- venv：`E:/project/team-share-public/synthesis-integration-flow-guide/script/.venv` · Python 3.13.13
- 已装并 import 验证（2026-10-21 队长安装）：matplotlib 3.11.2、opencv-contrib-python 5.0.0.93、**rapidocr-onnxruntime 1.2.3**
- ⚠️ **修正 pin**：architecture.md 草稿所写 `rapidocr-onnxruntime==1.4.4` 在本机**不可解析**（默认源与官方 PyPI `-i https://pypi.org/simple` 均报 No matching distribution；本机该包可见上限 1.2.3；新统一包 `rapidocr` 另行存在、现到 3.10.0、API 不同）。**定稿应改为 `rapidocr-onnxruntime==1.2.3`（已 import 验证）**。
- pip 无自定义索引配置（默认通道）；`pip install … | tail` 会吃掉退出码，验收时须看输出文本而非 exit code。

<!-- captain 规约 2026-10-21 -->
