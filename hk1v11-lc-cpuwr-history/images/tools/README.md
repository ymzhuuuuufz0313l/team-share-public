# images/tools/ — 图生成脚本

> 依「图版生命周期与归档标准」（blueprint-ui-style，2026-11-04）：静态图生成脚本统一归本目录；
> 主名位 = 当前采纳版；换版必快照进 `images/archive/<采纳日期>/`（永不删除）；PNG/位图素材只进日期夹。
> 动画版生成器 `make_anim_*.py` 属 v4 双版契约，留在 `images/anim/`（生成 `anim/<name>.svg`），不在本目录。

| 脚本 | 生成目标（主名位） | 复跑法 |
|------|-------------------|--------|
| `gen_reg_1104v1.py` | `1104v1_reg_changes.svg`（静态事实源）+ `anim/` 动画版——1104v1 迭代变更表（**r1，含第 7 行输出口归属修正 b49e5741**）；被替换 r0 快照在 `../archive/20261104/` | `python images/tools/gen_reg_1104v1.py`（内置自检：XML 合法 / 静态无动画 / 动画有 / `<text>` 零漂移，`ALL PASS` 即成功） |
| `gen_reg_sync_1104.py` | `1104_reg_sync_changes.svg`（静态）+ `anim/` 动画版——1104 服务器同步五处差异表（内容稳定，重跑输出字节一致） | `python images/tools/gen_reg_sync_1104.py`（同款自检） |
| `gen_beat_regroup_svg.py` | `config_data_beat_regroup_0721.svg`——0721v1 配置拍重组对照（历史图，绝对路径输出） | `python images/tools/gen_beat_regroup_svg.py`（尾部 `XML valid` 即成功；动画版由 `anim/make_anim_beat.py` 维护） |
| `regen_lsi_map.py` | `lsi_unprotected_address_map.svg`——LSI 保护地址图（0827v1；字段源 = `chip_sel0_register_address_map.md`，保护真值 = LC_CPUWR.v RTL） | `python images/tools/regen_lsi_map.py`（绝对路径，位置无关） |
| `make_sync1104_html.py` | ⚠ **历史脚手架，勿重跑**——首次生成 `sync-1104.html`（仅 §1-5）；现行页面已手工扩展 §6（1104v1），重跑会整页覆盖丢 §6 | 仅留档复现首次建页 |

<!-- ymzhu 2026-11-04 16:12 -->
