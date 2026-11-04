# images/tools/ — 图生成与校验脚本

本目录存放站点图的生成脚本与校验工具。每个脚本头部标注其生成的图组。

## 生成脚本（anim/ 动画版 SVG）

| 脚本 | 生成目标 |
|------|---------|
| `make_anim_8b10b_vs_420b.py` | `images/anim/8b10b_vs_420b_architecture.svg` |
| `make_anim_longcode_verification_architecture.py` | `images/anim/longcode_verification_architecture.svg` |
| `make_anim_pydec_tx_rx_structure.py` | `images/anim/pydec_tx_rx_structure.svg` |
| `make_anim_spec_bit_order.py` | `images/anim/spec_bit_order.svg` |
| `make_anim_spec_blanking_idle.py` | `images/anim/spec_blanking_idle.svg` |
| `make_anim_spec_dummy_70b.py` | `images/anim/spec_dummy_70b.svg` |
| `make_anim_spec_frame_flow.py` | `images/anim/spec_frame_flow.svg` |
| `make_anim_spec_lsp_kcode.py` | `images/anim/spec_lsp_kcode.svg` |
| `make_anim_spec_scramble_rolling.py` | `images/anim/spec_scramble_rolling.svg` |
| `make_anim_spec_tag_replacement.py` | `images/anim/spec_tag_replacement.svg` |

> 静态版（事实源）为同站点 `images/` 下同名 SVG；动画版在 `images/anim/`。
> 生成器确定性幂等：只读静态版，零第三方依赖，重跑输出字节一致。

## 校验脚本

| 脚本 | 用途 |
|------|------|
| `validate_kit_v2.py` | MOTION_KIT v2 规范校验（历史） |
| `validate_kit_v4.py` | MOTION_KIT v4 规范校验（当前） |

<!-- ymzhu 2026-11-04 17:20 -->
