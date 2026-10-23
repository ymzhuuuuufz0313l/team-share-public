// crop_image —— 裁剪 + 体检（Phase 1，§6.2）。
// 按分数坐标框裁剪（或自动裁白边），重编码 PNG 落盘，返回新图 + 完整体检。
import fs from 'node:fs/promises'
import path from 'node:path'
import { loadConfig } from '../config.js'
import { err, sha256Hex, resolveTarget, makeGallery, resolveSource, runPython } from '../report/resolve-target.js'

function validateArgs(args) {
  if (!['site', 'daily', 'report'].includes(args.target_kind)) throw err('INVALID_ARGS', `target_kind 必须是 site/daily/report：${JSON.stringify(args.target_kind)}`)
  if (typeof args.target_name !== 'string' || args.target_name.trim() === '') throw err('INVALID_ARGS', 'target_name 必填（非空字符串）')
  const hasA = args.attachment_id !== undefined && args.attachment_id !== null && args.attachment_id !== ''
  const hasP = args.path !== undefined && args.path !== null && args.path !== ''
  if (hasA && hasP) throw err('INVALID_ARGS', 'attachment_id 与 path 二选一（都给了）')
  if (!hasA && !hasP) throw err('INVALID_ARGS', 'attachment_id 与 path 至少给一个')
  const hasBox = args.box !== undefined && args.box !== null
  const hasTrim = args.auto_trim === true
  if (!hasBox && !hasTrim) throw err('CROP_SPEC_REQUIRED', 'box 与 auto_trim 至少给一个')
  if (hasBox) {
    const b = args.box
    if (typeof b !== 'object' || typeof b.left !== 'number' || typeof b.top !== 'number' || typeof b.right !== 'number' || typeof b.bottom !== 'number')
      throw err('INVALID_ARGS', 'box 必须是 {left,top,right,bottom}（各为 0..1 分数）')
    for (const k of ['left', 'top', 'right', 'bottom']) {
      if (b[k] < 0 || b[k] > 1) throw err('INVALID_ARGS', `box.${k} 必须在 0..1：${b[k]}`)
    }
  }
  if (args.margin !== undefined && !(Number.isInteger(args.margin) && args.margin >= 0)) throw err('INVALID_ARGS', 'margin 必须是非负整数')
}

function sourceField(src) {
  return src.sourceKind === 'attachment_id'
    ? { path: null, attachment_id: src.sourceId }
    : { path: src.sourceId, attachment_id: null }
}

function renderCrop(v) {
  return `cropped ${v.name} -> ${v.path} (${v.width}x${v.height}, ${v.bytes}B) | md: ${v.reference.markdown ?? v.reference.html ?? ''}`
}

export function register(ctx, config) {
  ctx.tools.register({
    name: 'crop_image',
    description: 'Crop an image by fractional bounding box (resolution-independent) or auto-trim uniform margins, save as PNG to a target directory, and return size/aspect/blur quality metrics.',
    parameters: {
      type: 'object',
      properties: {
        attachment_id: { type: 'string', description: '源图 attachmentId（形如 sha256:<64hex>）；与 path 二选一' },
        path: { type: 'string', description: '源图绝对路径（通常是上游工具输出的 path 字段）；与 attachment_id 二选一' },
        target_kind: { type: 'string', enum: ['site', 'daily', 'report'], description: '裁剪结果落盘目标域' },
        target_name: { type: 'string', description: '站目录名 / 日报项目名 / 报告目录名' },
        slug: { type: 'string', description: '文件名主题段，净化为 [a-z0-9-]{1,24}，缺省 shot' },
        alt: { type: 'string', description: '引用里的 alt 文本，缺省 = slug' },
        box: {
          type: 'object',
          additionalProperties: false,
          properties: {
            left: { type: 'number' }, top: { type: 'number' }, right: { type: 'number' }, bottom: { type: 'number' },
          },
          required: ['left', 'top', 'right', 'bottom'],
          description: '分数框 {left,top,right,bottom}，各为 0..1 相对原始图，含端点；与 auto_trim 至少给一个',
        },
        auto_trim: { type: 'boolean', description: 'true=PIL 灰度阈值≥245 视为背景，getbbox() 自动紧致裁剪' },
        margin: { type: 'integer', description: '裁剪后四周保留像素，默认 0' },
      },
      required: ['target_kind', 'target_name'],
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
          source: {
            type: 'object', additionalProperties: false,
            properties: { path: { type: 'string' }, attachment_id: { type: 'string' } },
            required: ['path', 'attachment_id'],
          },
          quality: {
            type: 'object',
            additionalProperties: false,
            properties: {
              width: { type: 'integer' },
              height: { type: 'integer' },
              short_edge_px: { type: 'integer' },
              aspect_ratio: { type: 'number' },
              laplacian_var: { type: 'number' },
              too_small: { type: 'boolean' },
              flags: { type: 'array', items: { type: 'string' } },
            },
            required: ['width', 'height', 'short_edge_px', 'aspect_ratio', 'laplacian_var', 'too_small', 'flags'],
          },
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
        required: ['ok', 'name', 'path', 'copies', 'bytes', 'width', 'height', 'mediaType', 'source', 'quality', 'reference', 'gallery'],
      },
      render: (_args, value) => [{ type: 'text', text: renderCrop(value) }],
    },
    timeoutMs: 60000,
    async execute(args, exec) {
      const cfg = loadConfig(config)
      validateArgs(args)
      const src = await resolveSource(cfg, { attachment_id: args.attachment_id, path: args.path }, ctx, exec)
      const { dirs, name, reference } = await resolveTarget(cfg, { kind: args.target_kind, name: args.target_name, slug: args.slug, alt: args.alt, ext: 'png' })
      const primary = path.join(dirs[0], name)
      const margin = (typeof args.margin === 'number') ? args.margin : 0
      const m = await runPython(ctx, cfg, 'crop_image.py', {
        source: src.absPath,
        out: primary,
        box: (args.box !== undefined && args.box !== null) ? args.box : null,
        auto_trim: args.auto_trim === true,
        margin,
        thresholds: { short_edge_min: cfg.shortEdgeMin, aspect_max: cfg.aspectMax, laplacian_min: cfg.laplacianMin },
      }, [], exec)
      if (!m || m.ok !== true) {
        // T7 修正（四路共性 M5，§11.2:609）：空裁剪是领域结果 → return ok:false（与 render_chart
        // SELF_CHECK_FAILED / render_diagram NOT_IMPLEMENTED / extract_table ENGINE_MISSING 一致），不 throw。
        if (m && m.code === 'CROP_EMPTY') {
          return {
            ok: false, name, path: primary, copies: [], bytes: 0, width: null, height: null,
            mediaType: 'image/png', source: sourceField(src),
            quality: { width: null, height: null, short_edge_px: null, aspect_ratio: null, laplacian_var: null, too_small: null, flags: [] },
            reference, gallery: makeGallery(sha256Hex(Buffer.alloc(0)), 'png'),
            code: 'CROP_EMPTY',
          }
        }
        throw err('CROP_FAILED', (m && m.message) || '裁剪失败')
      }
      // 日报双写等：主写后再复制到其余目录
      const copies = [primary]
      for (let i = 1; i < dirs.length; i++) {
        const p = path.join(dirs[i], name)
        await fs.copyFile(primary, p)
        copies.push(p)
      }
      const prodBytes = await fs.readFile(primary)
      const prodSha = sha256Hex(prodBytes)
      const quality = {
        width: (m.width ?? null), height: (m.height ?? null),
        short_edge_px: (m.short_edge_px ?? null), aspect_ratio: (m.aspect_ratio ?? null),
        laplacian_var: (m.laplacian_var === undefined ? null : m.laplacian_var),
        too_small: (m.too_small === undefined ? null : m.too_small), flags: m.flags || [],
      }
      return {
        ok: true,
        name,
        path: primary,
        copies,
        bytes: (typeof m.bytes === 'number') ? m.bytes : prodBytes.length,
        width: m.width,
        height: m.height,
        mediaType: 'image/png',
        source: sourceField(src),
        quality,
        reference,
        gallery: makeGallery(prodSha, 'png'),
      }
    },
  })
}
