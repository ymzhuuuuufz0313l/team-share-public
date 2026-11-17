# vendor/ — 本地第三方运行时依赖

## marked.min.js

| 项 | 值 |
|---|---|
| 库 | [marked](https://github.com/markedjs/marked)（Markdown 渲染器） |
| 版本 | **v15.0.12** |
| 原始地址 | `https://cdn.jsdelivr.net/npm/marked/marked.min.js` |
| 下载日期 | 2026-11-17 |
| 许可 | MIT（见文件头 license 声明） |
| 字节数 | 39903 |
| md5 | `e04ae0bf88da292e65e1e677394f6058` |
| sha256 | 见同目录 `marked.min.js.sha256` |

### 为什么放进仓库（审查项 F01）

原来 11 个页面都从 `cdn.jsdelivr.net` 拉 marked：

```html
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
```

**断网 / CDN 被墙 / 离线打开**（例如把站点拷到内网机器或直接 `file://` 打开）时，
`marked` 不存在 → `marked.parse()` 抛错 → `#article` 一直空白，整页正文不可读。
把同一版本 vendor 进仓库后，站点核心渲染不再依赖外网。

### 兜底不是靠"文件在"，而是靠显式判断

11 个页面共用同一段入口（`index.html` 没有 markdown，已删掉它那行无用依赖）：

```js
if (typeof marked !== 'undefined' && marked && typeof marked.parse === 'function') {
  artEl.innerHTML = marked.parse(src);      // 正常路径
  return;
}
// 兜底：<pre> 纯文本视图 + 顶部提示条（.md-offline-tip / .md-offline-fallback）
```

即使 `vendor/marked.min.js` 也被删掉/被拦，页面仍会退化成**可读的纯文本**，
而不是白屏。实测截图见修复报告（把 vendor 文件临时移走后的渲染结果）。

### 升级方式

```bash
curl -o vendor/marked.min.js https://cdn.jsdelivr.net/npm/marked/marked.min.js
sha256sum vendor/marked.min.js   # 更新本文件与 .sha256
```
升级后需回归：任一页面正文正常渲染 + 临时移走 vendor 文件仍可读。

<!-- ymzhu 2026-11-17 19:55 -->
