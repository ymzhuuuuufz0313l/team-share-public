// render_chart —— 固定模板重绘（Phase 1：参数化壳 + table 族样例，§6.4）。
// 把结构化数据 + themes.json 色板喂给 back_ppt 同族模板渲染器，出 blueprint 风格 PNG。
// 模型只判断（作图/保图/裁哪）与供数；数据必须来自 extract_table 输出，工具绝不虚构。
import fs from 'node:fs/promises'
import path from 'node:path'
import { loadConfig } from '../config.js'
import { err, sha256Hex, resolveTarget, makeGallery, runPython } from '../report/resolve-target.js'

// 长度校验（§6.4）：len(headers[i]) === len(rows[j]) === 数据列数+1；数据列数 = len(headers[0]) - 1。
// 空数组行 [] = 半高分隔缝（合法，跳过长度断言）。
function validateData(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw err('INVALID_ARGS', 'data 必填（对象）')
  const { headers, rows, mode, title, subtitle } = data
  if (typeof title !== 'string' || title.trim() === '') throw err('DATA_INVALID', 'data.title 必填（非空字符串）')
  if (subtitle !== undefined && typeof subtitle !== 'string') throw err('DATA_INVALID', 'data.subtitle 必须是字符串')
  if (!Array.isArray(headers) || headers.length < 1 || headers.length > 2) throw err('DATA_INVALID', `headers 必须是 1 或 2 层（收到 ${headers && headers.length} 层）`)
  for (let i = 0; i < headers.length; i++) if (!Array.isArray(headers[i])) throw err('DATA_INVALID', `headers[${i}] 必须是数组`)
  const dataColsPlus1 = headers[0].length
  if (dataColsPlus1 < 2) throw err('DATA_INVALID', `数据列数必须 ≥1（headers[0].length=${dataColsPlus1}，含行标签列）`)
  for (let i = 1; i < headers.length; i++)
    if (headers[i].length !== dataColsPlus1) throw err('DATA_INVALID', `headers 各层长度必须一致（=${dataColsPlus1}）：layer ${i} = ${headers[i].length}`)
  if (!Array.isArray(rows) || rows.length === 0) throw err('DATA_INVALID', 'rows 必填且非空数组')
  for (let j = 0; j < rows.length; j++) {
    if (!Array.isArray(rows[j])) throw err('DATA_INVALID', `rows[${j}] 必须是数组`)
    if (rows[j].length === 0) continue // 半高分隔缝
    if (rows[j].length !== dataColsPlus1) throw err('DATA_INVALID', `rows[${j}] 长度必须 = ${dataColsPlus1}（数据列数+1）：收到 ${rows[j].length}`)
  }
  if (!['violation', 'window', 'plain'].includes(mode)) throw err('DATA_INVALID', `mode 必须是 violation/window/plain：${JSON.stringify(mode)}`)
}

function validateArgs(args) {
  if (args.template !== 'table') throw err('INVALID_ARGS', `template MVP 仅支持 'table'：${JSON.stringify(args.template)}`)
  validateData(args.data)
  if (args.theme !== undefined && !['paper', 'teal'].includes(args.theme)) throw err('INVALID_ARGS', `theme 必须是 paper/teal：${JSON.stringify(args.theme)}`)
  if (!['site', 'daily', 'report'].includes(args.target_kind)) throw err('INVALID_ARGS', `target_kind 必须是 site/daily/report：${JSON.stringify(args.target_kind)}`)
  if (typeof args.target_name !== 'string' || args.target_name.trim() === '') throw err('INVALID_ARGS', 'target_name 必填（非空字符串）')
}

function renderChart(v) {
  if (v.ok === false) return `render_chart failed: ${v.code}${v.self_check ? ` (self_check=${v.self_check})` : ''}`
  return `render_chart: ${v.name} -> ${v.path} (${v.width}x${v.height}, ${v.bytes}B, theme=${v.theme}, self_check=${v.self_check}) | md: ${v.reference.markdown ?? v.reference.html ?? ''}`
}

export function register(ctx, config) {
  ctx.tools.register({
    name: 'render_chart',
    description: 'Render structured data into a blueprint-styled chart PNG via the fixed back_ppt template family. MVP family: "table" (1-2 layer headers, violation/window/plain cell coloring, supersampled, self-checked). Theme defaults to paper.',
    parameters: {
      type: 'object',
      properties: {
        template: { type: 'string', enum: ['table'], description: 'MVP 仅 table（code/bar/donut 留 Phase 2）' },
        data: { type: 'object', description: 'table 族数据契约：{title, subtitle, headers: string[][](1-2 层), rows: string[][], mode: violation|window|plain}' },
        theme: { type: 'string', enum: ['paper', 'teal'], description: '缺省 paper（teal 仅 2M23 指南站例外）' },
        target_kind: { type: 'string', enum: ['site', 'daily', 'report'], description: '落盘目标域' },
        target_name: { type: 'string', description: '站目录名 / 日报项目名 / 报告目录名' },
        slug: { type: 'string', description: '文件名主题段，净化为 [a-z0-9-]{1,24}，缺省 shot' },
        alt: { type: 'string', description: '引用里的 alt 文本，缺省 = slug' },
      },
      required: ['template', 'data', 'target_kind', 'target_name'],
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          ok: { type: 'boolean'},
          name: { type: 'string'},
          path: { type: 'string'},
          copies: { type: 'array', items: { type: 'string' }},
          bytes: { type: 'integer'},
          width: { type: 'integer'},
          height: { type: 'integer'},
          mediaType: { type: 'string'},
          template: { type: 'string'},
          theme: { type: 'string'},
          self_check: { type: 'string'},
          source_data_digest: { type: 'string'},
          reference: {
            type: 'object', additionalProperties: false,
            properties: { html: { type: 'string' }, markdown: { type: 'string' }, markdown_absolute: { type: 'string' } },
            required: ['html', 'markdown', 'markdown_absolute'],
          },
          gallery: {
            type: 'object', additionalProperties: false,
            properties: { sha256: { type: 'string' }, canonical: { type: 'string' }, implemented: { type: 'boolean' } },
            required: ['sha256', 'canonical', 'implemented'],
          },
          code: { type: 'string' },
        },
        required: ['ok', 'name', 'path', 'copies', 'bytes', 'width', 'height', 'mediaType', 'template', 'theme', 'self_check', 'source_data_digest', 'reference', 'gallery'],
      },
      render: (_args, value) => [{ type: 'text', text: renderChart(value) }],
    },
    timeoutMs: 120000,
    async execute(args, exec) {
      const cfg = loadConfig(config)
      validateArgs(args)
      const theme = (args.theme && ['paper', 'teal'].includes(args.theme)) ? args.theme : cfg.defaultTheme
      const { dirs, name, reference } = await resolveTarget(cfg, { kind: args.target_kind, name: args.target_name, slug: args.slug, alt: args.alt, ext: 'png' })
      const primary = path.join(dirs[0], name)
      const sourceDigest = sha256Hex(Buffer.from(JSON.stringify(args.data), 'utf8'))
      const m = await runPython(ctx, cfg, 'render_chart.py', {
        data: args.data,
        out: primary,
      }, [cfg.themesFile, theme, cfg.backpptScriptDir], exec, { cwd: cfg.backpptScriptDir })
      if (!m || m.ok !== true) {
        if (m && m.code === 'SELF_CHECK_FAILED') {
          // 自检失败：产物未写盘 → copies 为空（T7 合稿修正，勿列出不存在的文件）。
          return {
            ok: false, name, path: primary, copies: [], bytes: 0, width: null, height: null,
            mediaType: 'image/png', template: 'table', theme, self_check: 'failed',
            source_data_digest: sourceDigest, reference,
            gallery: makeGallery(sourceDigest, 'png'),
            code: 'SELF_CHECK_FAILED',
          }
        }
        throw err('RENDER_FAILED', (m && m.detail) || '渲染失败')
      }
      // 双写
      const copies = [primary]
      for (let i = 1; i < dirs.length; i++) {
        const p = path.join(dirs[i], name)
        await fs.copyFile(primary, p)
        copies.push(p)
      }
      // gallery.sha256 = 产物文件的 sha256（§7.4：canonical 收的是产物，不是源图）
      const prodBytes = await fs.readFile(primary)
      const prodSha = sha256Hex(prodBytes)
      return {
        ok: true,
        name,
        path: primary,
        copies,
        bytes: (typeof m.bytes === 'number') ? m.bytes : prodBytes.length,
        width: m.width,
        height: m.height,
        mediaType: 'image/png',
        template: 'table',
        theme,
        self_check: (m.self_check === 'passed') ? 'passed' : null,
        source_data_digest: sourceDigest,
        reference,
        gallery: makeGallery(prodSha, 'png'),
      }
    },
  })
}
