# image/archive — 图片历史版本归档说明

本目录保存站点图片的**历史版本快照**。本站点图片是"原地覆盖"式更新的（同一路径反复重写），
只靠 git 历史无法直接浏览旧图，因此把每个历史版本按提交导出成可打开的独立文件。

## 1. 命名与目录规则

```
image/archive/<YYYYMMDD>/<原文件名主干>_<commit7>.<ext>
```

- `<YYYYMMDD>`：该版本**首次出现的提交日期**（不是导出日期）。
- `<commit7>`：该版本所在提交的短哈希前 7 位，可 `git show <commit7> -- <原路径>` 复核。
- 只导出**与当前工作区版本不同**的历史版本；当前版在原位（`image/` 或 `image/anim/`），不重复归档。
- 同一份内容（md5 相同）在目录内**只存一份**；重复历史（如纯改名 C100 提交）复用已有文件。
- 不删除任何文件；归档只做新增。单文件 >5MB 不导出（仓库体积约束），只在清单里记来源。

## 2. 清单

`MANIFEST.md` 由脚本生成，**不要手改**（下次运行会被覆盖）：

```bash
python image/tools/archive_history.py --check    # 报告还缺哪些快照
python image/tools/archive_history.py --apply    # 实际导出 + 重写 MANIFEST.md
```

## 3. 生成脚本的"覆盖前自动归档"

新增/重跑生成脚本时，**写文件之前**先调用归档动作，避免再出现"旧版本只能靠 git 挖"的情况：

```python
from _archive import snapshot      # image/tools/_archive.py
snapshot(out_path)                 # 覆盖前把磁盘上的旧版本存进 image/archive/<今天>/<stem>_<HEAD7>.ext
```

命令行等价用法：

```bash
python image/tools/_archive.py image/30_postpt_hold_2p.png image/anim/30_postpt_hold_2p.svg
```

已接入的生成脚本：`gen_postpt_tables_anim.py`、`gen_postpt_skew_tables_anim.py`、
`gen_buf_type_anim.py`、`gen_power_compare_descramble.py`、`make_flow_anim.py`、
`_gen_be_review_images.py`（出图前对目标路径调用 `snapshot()`）。

## 4. 覆盖率（2026-11-17 核对）

| 口径 | 数量 | 说明 |
|---|---|---|
| `image/` 下入库图片总数（不含 `archive/`） | 58 | png + svg |
| 有历史版本且历史版本**已全部归档** | 37 | 逐版本 md5 与 archive 内文件一一对应 |
| 无历史版本（多次提交但内容未变，无可归档版本） | 21 | 属"无版本差异"，不是"缺归档" |
| 归档文件总数 | 165（png/svg 142 + 历史 jpg 素材 21 + 说明/清单 2） | 14 MB，无单文件 >5MB |

> 口径提示：审计报告里 A9 项"归档覆盖率"此前写作 **6/86**，统计的是"有独立归档目录的图片数 / 站内图片引用数"，
> 与本表口径（入库图片文件数）不同。按文件口径现在是 **37/58 全归档 + 21 单版本**，两个口径不要混用。

## 5. 已知修正与版本标签映射（必读）

### 5.1 `20260826/script-flow-overview.svg` 已修正

- 修正前：该文件内容与**当前**的 `image/script-flow-overview.svg` 完全相同（md5 `a38d92b2…`），
  即"归档的是当前版"，没有任何历史价值。
- 修正后：内容替换为 **2026-08-26 提交 `99d7fbf`** 的真实版本（md5 `ece13cf5…`，47456 字节）。
- 同内容的规范命名快照另存于 `20261027/script-flow-overview_775da64.svg`
  （`775da64` 是纯改名 C100 提交，内容与 `99d7fbf` 一致，按去重规则落到了先出现的那份）。
- 另注：`20260826/` 这份**文件名不带版本号/提交号**，是既有手工快照的遗留命名，
  与 `MANIFEST.md` 中的自动命名规则不同；请以 md5 与本节记录为准，不要靠文件名推断版本。

### 5.2 `power_compare_vertical` 版本标签与提交正文口径不一致

两个手工快照的文件名用的是 `_1106v0/_1106v1`，而提交正文用的是"v1/v2"，两者**不是同一套编号**：

| 归档文件 | md5 | 实际内容 | 来源提交 | 提交正文里的叫法 |
|---|---|---|---|---|
| `20261106/power_compare_vertical_1106v0.png` | `edfaa275…` | 4 块版，**与当前 `image/power_compare_vertical.png` 完全相同** | `af38d0d`（2026-11-06，revert 提交） | 正文写"revert 回 v1"，即正文的 **v1** |
| `20261106/power_compare_vertical_1106v1.png` | `dde304e9…` | 含 1106 descramble 新块的 5 块版 | `d59441c`（2026-11-06） | 正文写"v2 snapshotted"，即正文的 **v2** |

即：**文件名 v0 ↔ 提交正文 v1（revert 目标，当前版）；文件名 v1 ↔ 提交正文 v2（被 revert 掉的那版）**。
`1106v0` 与当前主文件同 md5 属**预期**——它记的正是"revert 后恢复的那一版"，不是"归档=当前"的缺陷；
其历史价值在 provenance（哪次提交把它恢复回来），不在图片内容差异。

### 5.3 descramble 1106 三张快照

`20261106/power_compare_descramble_1106_1106v{0,1,2}.png` 分别是同一天三次迭代的产物；
当前值以 `image/tools/data/descramble_power.json` 为准（13.3 / 15.2 / 14.7 mW），
其中 24b 首跑误测的 8.57 mW 已在数据源的 `provenance.voided` 里显式标记作废。

<!-- ymzhu 2026-11-17 19:43 -->
