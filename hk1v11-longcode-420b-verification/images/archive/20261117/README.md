# images/archive/20261117/ — 补齐「被替换图版」快照（2026-11-17）

本目录是审查项 **F05** 的修复产物：`2997411`（2026-11-05 全量图版更新）改了 8 张已有静态图，
当时只归档了 3 张（`archive/20260720/`），其余 5 张以「原地更新，未归档」处理；
另有 `kcode_bitrev_compare.svg` 被 `053c875` 与 `b063c7f` 连续两次修改，两版都没留快照。
合计 **7 个被替换过的版本**没有快照，本次全部补齐。

**取证方式**：全部用 `git show <rev>:<path>` 从历史提交取出，不是把当前版复制一份冒充旧版；
下表最后一列给出与现行版 md5 的比对结果，全部不同（DIFF）。

## 清单

| 归档文件 | 来源提交 | 对应现行文件 | 字节 | md5 | vs 现行 |
|---------|---------|-------------|-----:|---|---|
| `pydec_tx_rx_structure_pre1105.svg` | `2997411^` | `images/pydec_tx_rx_structure.svg` | 10724 | `419ae0ac610d81bb1b7515765de6a533` | DIFF |
| `anim/pydec_tx_rx_structure_pre1105.svg` | `2997411^` | `images/anim/pydec_tx_rx_structure.svg` | 18751 | `bbc735531a37f163509bc28d21818075` | DIFF |
| `spec_blanking_idle_pre1105.svg` | `2997411^` | `images/spec_blanking_idle.svg` | 14190 | `911d51c9db504bce0bb9319aee9e049d` | DIFF |
| `anim/spec_blanking_idle_pre1105.svg` | `2997411^` | `images/anim/spec_blanking_idle.svg` | 18865 | `9e996f6b30cde223bbd1c349b295dc14` | DIFF |
| `spec_dummy_70b_pre1105.svg` | `2997411^` | `images/spec_dummy_70b.svg` | 11358 | `15be64c1460ed936e33dc2892b889bf3` | DIFF |
| `anim/spec_dummy_70b_pre1105.svg` | `2997411^` | `images/anim/spec_dummy_70b.svg` | 16471 | `3ea60aa4643036de882127583990a20e` | DIFF |
| `spec_lsp_kcode_pre1105.svg` | `2997411^` | `images/spec_lsp_kcode.svg` | 10850 | `192748d44059d674e6cee1560d10e7b1` | DIFF |
| `anim/spec_lsp_kcode_pre1105.svg` | `2997411^` | `images/anim/spec_lsp_kcode.svg` | 17748 | `603bfddf09f0e12de646e82266ee60a7` | DIFF |
| `8b10b_vs_420b_architecture_pre1105.svg` | `2997411^` | `images/8b10b_vs_420b_architecture.svg` | 19546 | `c3907c91989e9488de9ef7ea8f464fe9` | DIFF |
| `anim/8b10b_vs_420b_architecture_pre1105.svg` | `2997411^` | `images/anim/8b10b_vs_420b_architecture.svg` | 25306 | `0e70bb4cc009940d63893a0d806bb5f0` | DIFF |
| `kcode_bitrev_compare_before_053c875.svg` | `053c875^` | `images/kcode_bitrev_compare.svg` | 8004 | `64dba86bc0978a36ddb2404c07d5337d` | DIFF |
| `kcode_bitrev_compare_before_b063c7f.svg` | `b063c7f^` | `images/kcode_bitrev_compare.svg` | 8024 | `f66c7838e451b94a8b5fe82f64aff299` | DIFF |

> **换行说明**：站点的硬性卫生要求是「文本资源无 CRLF」，因此归档快照在落盘时统一做了
> **仅换行**归一化（CRLF/CR → LF）。`anim/spec_dummy_70b_pre1105.svg` 取自的
> `2997411^` 版本当年本身是 CRLF，故其原始字节 md5 与上表所列（归一化后）md5 不同：
> 归一化只消除 EOL 差异：**字符内容完全一致，但不是逐字节相同**（V5 措辞更正）。
> 其余 11 个快照本来即 LF，未受影响。

## 第二批：`10b469e`（repair#1）替换的图版快照

审查复核轮（t15）发现：`10b469e` 这次修复改了 6 张图，但**一张快照都没留**，于是
「被替换必归档」的规矩又被绕过了一次。本批补齐，同时把规矩从「README 里的散文」
升级成**机器强制**（见下一节）。

**取证方式**：`git show 818ca97:<path>`（`818ca97` == `10b469e^`）取原件，落盘时做 EOL 归一化。

| 归档文件 | 来源提交 | 对应现行文件 | 字节 | md5（归一化后） | 分类 |
|---------|---------|-------------|-----:|---|---|
| `delta_case_matrix_before_10b469e.svg` | `818ca97` | `images/delta_case_matrix.svg` | 23282 | `d50bf66609be8f74d746341c2e868108` | 内容变更 |
| `anim/delta_case_matrix_before_10b469e.svg` | `818ca97` | `images/anim/delta_case_matrix.svg` | 29392 | `12fdec1598bb52171041b49195e9c9dd` | 内容变更 |
| `spec_tag_replacement_anim_before_10b469e.svg` | `818ca97` | `images/anim/spec_tag_replacement.svg` | 13589 | `5f36d972af77ad15b2e36211cafe71dc` | **仅换行**（内容等价） |
| `longcode_verification_architecture_anim_before_10b469e.svg` | `818ca97` | `images/anim/longcode_verification_architecture.svg` | 29949 | `f0f582f4411576ed2b4af408d9431f71` | **仅换行**（内容等价） |
| `spec_dummy_70b_anim_before_10b469e.svg` | `818ca97` | `images/anim/spec_dummy_70b.svg` | 16590 | `87ae85bfd8cbb4673e18df1182be5640` | **仅换行**（内容等价） |
| `spec_scramble_rolling_anim_before_10b469e.svg` | `818ca97` | `images/anim/spec_scramble_rolling.svg` | 15385 | `2f8b4f7ccb0d833345e9577dc611bbad` | **仅换行**（内容等价） |

**为什么这 4 张不放在 `anim/` 子目录**：仓库级闸门 `scripts/check_anim_pairs.py` 对**任何**
路径里含 `anim/` 目录段的 SVG 都要求同名静态版存在（fx.js 切静态模式时去 `/anim/` 段，
缺则 404）。归档快照不被任何页面引用，静态版当年也没变，硬凑一份静态副本会变成
「与现行同 md5 的重复文件」（正是本目录下面批评的 fx_phases 重复落盘问题），
因此改为 `<name>_anim_before_10b469e.svg` 平铺命名：既表明是动画版原件，
又不触发 live 引用的配对规则。内容与 `818ca97` 的 `images/anim/<name>.svg` 完全一致
（`check_archive.py` 按 md5 索引，与落点目录无关）。

**两点必须说清（不要误读）**：

1. 后 4 张是**整文件 CRLF→LF 重写**造成的「变更」，归一化后与现行文件**字符内容完全相同**
   ——它们不是内容替换，归档价值在于证明「旧版是 CRLF」。原始 blob md5 见下表，与归一化后 md5 不同是预期的。
2. `spec_tag_replacement` 的 diff 有 137 行，全部来自行分隔符，**没有任何一个字符/数值变化**。

| 归档文件（CRLF 原件） | 原始 blob 字节 | 原始 md5 |
|---|---:|---|
| `spec_tag_replacement_anim_before_10b469e.svg` | 13756 | `dc2b672b075a669d985582f839721121`（167 处 CRLF + 137 处单独 CR） |
| `longcode_verification_architecture_anim_before_10b469e.svg` | 30227 | `0ab6df5001179799827544765581e569` |
| `spec_dummy_70b_anim_before_10b469e.svg` | 16783 | `09efc89b95af2cb50b82cf96bd6ae836` |
| `spec_scramble_rolling_anim_before_10b469e.svg` | 15557 | `1fb2d66bc6d927d0b9b8a30120c2f8cf` |

（`delta_case_matrix` 两张取自 `818ca97` 时本身即 LF，归一化后 md5 与原始 blob md5 相同，
故未列入本表。）

## 归档规范（新，已机器强制）

原规范只有上面这段散文，**没有任何机制执行**，所以两轮修复各绕过一次
（`10b469e` 6 张全漏；`spec_tag_replacement` 是生成器之外的整文件重写，也漏）。
V1 根因修复做了两件事，把「规矩」变成「闸门」：

1. **写入口自动归档**：`images/tools/site_paths.py` 的 `write_svg()` 在覆盖前比较旧/新内容
   （LF 归一化后），不同则自动把旧版落到 `images/archive/<YYYYMMDD>/<相对路径>_before_<rev>.svg`。
   预览模式（`--out` / `SITE_ROOT`）不触发；内容相同不触发；已存在不重复。所有生成器都走这个入口，
   不需要每个生成器各自记得归档。
2. **闸门兜底**：`images/tools/check_archive.py --base <rev>` 对 `images/` 下（排除 `archive/`）
   每个相对基线被改动的图，检查归档目录里存在与该基线版本 LF 归一化 md5 相等的快照；
   缺一个即 FAIL 退出 1。它连**手工改图**（绕过生成器）也能抓到。

## 同名去重（fx_phases 视口截图）

`images/tools/overlap_evidence_20261105_after_fix/` 下曾同时存在 5 个 `fx_phases_vt*.png`
（vt400 / vt900 / vt1600 / vt3200 / vt9000），**五个文件字节完全相同**（各 462665 B，md5 `dc58279899a3030cb547bedd4925faa7`）。
它们是同一张视口截图的重复落盘，与视口高度无关（不是 5 张不同证据）。

- **保留 1 份在位**：`images/tools/overlap_evidence_20261105_after_fix/fx_phases_vt1600.png`（canonical）
- **其余 4 份移动**到 `evidence_dedupe/`，文件名不变、内容不变（md5 同上），无一张图片被删除
- 站点内（含 `.md` / `.html`）原本没有任何地方引用这 5 个名字，移动不产生死链（已全库 grep 验证）

| 去重后位置 | md5 | 与 canonical 关系 |
|---|---|---|
| `../../tools/overlap_evidence_20261105_after_fix/fx_phases_vt1600.png` | `dc58279899a3030cb547bedd4925faa7` | canonical（保留在位） |
| `evidence_dedupe/fx_phases_vt400.png` | `dc58279899a3030cb547bedd4925faa7` | 与 canonical **完全同一字节**（重复落盘） |
| `evidence_dedupe/fx_phases_vt900.png` | `dc58279899a3030cb547bedd4925faa7` | 与 canonical **完全同一字节**（重复落盘） |
| `evidence_dedupe/fx_phases_vt3200.png` | `dc58279899a3030cb547bedd4925faa7` | 与 canonical **完全同一字节**（重复落盘） |
| `evidence_dedupe/fx_phases_vt9000.png` | `dc58279899a3030cb547bedd4925faa7` | 与 canonical **完全同一字节**（重复落盘） |

> 说明：`fx_debug-log_vt*.png`（5 个）md5 各不相同，是 5 张不同的视口证据，**不做去重**、原样保留。

## 与 `archive/20260720/` 的分工

- `20260720/`：0720 代际（老版本被 1105 图版更新替换）——由 `2997411` 建立，本轮未改动内容，仅换行统一。
- `20261117/`：**1105 更新中被「原地替换」而没有留快照的那一批**，以及 kcode 两版手改，以及本次去重产物。

## 归档规范（新）

图版更新时**不允许**再写「原地更新，未归档」。任何被替换的版本必须在同一提交内
`git show <上一版 rev>:<path>` 取出并落到 `images/archive/<更新日期YYYYMMDD>/`，
同时在 `images/tools/README.md` 的引用替换清单里登记归档路径与 md5。
<!-- ymzhu 2026-11-17 20:35 -->
