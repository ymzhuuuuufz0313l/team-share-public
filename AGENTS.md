# team-share-public 工作区 Agent 指南

本仓库是蓝图风静态站点群（每目录一站 + 根导航 + fx 引擎）。改任何站点/图之前，先查下面的路由表并加载对应 skill（skill 库在 `C:\Users\zhuyanming\.dsh\skills\`，全表见其 `README.md`「任务路由表」）。

## 任务 → Skill 路由（强制先查）

| 任务长相 | 必加载 |
|---|---|
| 建站 / 新站 / 改站点 / 改图 / 重生成图 / 动效 / 静动双版 | `blueprint-ui-style` |
| 审计站点 / 全站核对 / 图体检 / 环形图加起来不对 | `blueprint-ui-style`（读 `references/site-audit.md`，A0–A9） |
| 表格图 / 条形图 / 环形图 / PowerPro 图 | `pil-table-render` |
| team-share 加文章 / 发布文章 | `team-share` |
| 改完要提交推送 | `hk1v11-delivery-gate`（站点改动交付条款） |

## 本仓库硬规则（细节以 skill 为准）

- 图只归档、永不删除；换版先快照 `images/archive/<内容日>/`（只追加不覆盖）。
- 改图第一动作 = 跑生成器 `--out` 与线上 `cmp`，禁手改线上 SVG。
- 改图/页必须同提交 bump `?v=`；`search-index.json/.js` 由同一脚本重产出。
- 所有写文件 LF、UTF-8 无 BOM；文件尾签名 `ymzhu YYYY-MM-DD HH:MM` 唯一（规则本体见 `workflow-maintainer`）。
- 提交用显式路径 `git add -- <路径>`；push 用一次性代理参数，不写 config。

<!-- ymzhu 2026-11-18 14:35 -->
