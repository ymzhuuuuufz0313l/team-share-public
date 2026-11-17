# power_module_compare_1v11_1v22.svg —— 参数化之前的手写产物（历史快照）

## 这是什么

本目录下的 `power_module_compare_1v11_1v22.svg` 是 **2026-11-17 参数化重构之前手工编写的** 4.46G（4g5）模块功耗对比条形图，
与今天 `script/_chapter_viz/gen_power_module_compare_svg.py` 的生成结果**语义完全一致、数字格式不同**：

| 项 | 在网/归档手写版 | 生成器输出 | 视觉差异 |
|---|---|---|---|
| 条宽 / 文本 x 等坐标 | `389`（整数） | `389.0`（`%.1f`） | 无（SVG 数值等价） |
| 条数 / 标签 / 模块名 / 图例 / viewBox / width / height | 21 / 21 / 11 / 6 | 同 | 无 |

即：`--check` 对 4g5 档只做**语义对账**（条 21 / 数值标签 21 / 模块名 11 / 图例 6 + viewBox/根尺寸/`preserveAspectRatio` 全部一致，
差异仅在"数字格式"白名单 `(\d+)\.0` ↔ `\1` 内），不要求逐字节一致。

## 为什么归档

1. 该文件是**参数化前的手写基线**，不是生成器产物；将来若有人（或某个 `--write`）把它重新生成为 `389.0` 形式，
   手写原字节就会永久消失。归档保证历史可追溯。
2. 它同时是 4g5 档语义对账的**参照物**（`REF_4G5` 只读参照）。

## 归档信息

- 原路径：`hk1v11-synthesis-postpt-practice/images/power_module_compare_1v11_1v22.svg`
- 归档路径：`hk1v11-synthesis-postpt-practice/images/archive/20261117/power_module_compare_1v11_1v22_handwritten/power_module_compare_1v11_1v22.svg`
- 字节数：9559
- md5：`a8bca20b724087dbeb24ebd34ec8efea`（归档件与在网件逐字节一致，`cp -p` 保留原字节，未做 EOL 转换）
- 归档时的在网 EOL：LF

## 待裁决事项（N-7）

4g5 档"逐字节复现"需要把生成器的整数格式化口径（`%.1f` → 去尾 `.0`）改掉，属 **N-6 同族（`y` 坐标整数格式）**，
会改动生成器输出的 120 行纯数字格式文本、零视觉差异，故本轮（t29）**不修改**，交用户裁决。
在裁决前，4g5 档 `--write` 在 DRIFT 态会被代码拒绝（打印 `DRIFT 态禁止 --write，先裁决`）。

<!-- ymzhu 2026-11-17 21:40 -->
