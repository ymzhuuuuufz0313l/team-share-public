// save_screenshot —— 落盘桥（Phase 0 核心，§6.1）。
// 从会话取最近一张（或指定序号）截图的原始全分辨率对象，按命名规则写到目标目录（日报域双写），
// 返回路径 + 体检 + 引用 + 中央图库接口字段。不做任何清理/重绘。
import fs from 'node:fs/promises'
import path from 'node:path'
import { loadConfig } from '../config.js'
import { err, resolveTarget, makeGallery, runPython } from '../report/resolve-target.js'

const MEDIA_EXT = { 'image/png': 'png', 'image/jpeg': 'jpg', 'image/webp': 'webp', 'image/gif': 'gif' }

function sniffMediaType(bytes) {
  const b = bytes
  if (b.length >= 4 && b[0] === 0x89 && b[1] === 0x50 && b[2] === 0x4e && b[3] === 0x47) return 'image/png'
  if (b.length >= 3 && b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return 'image/jpeg'
  if (b.length >= 3 && b[0] === 0x47 && b[1] === 0x49 && b[2] === 0x46) return 'image/gif'
  if (b.length >= 12 && b[0] === 0x52 && b[1] === 0x49 && b[2] === 0x46 && b[3] === 0x46 && b[8] === 0x57 && b[9] === 0x45 && b[10] === 0x42 && b[11] === 0x50) return 'image/webp'
  return null
}

// 会话图引用：优先 attachment_id；否则从尾向头收集 user 消息 image 块，按 attachment_index 取。
function resolveSessionImageRef(exec, args) {
  if (args.attachment_id) {
    if (!/^sha256:([a-f0-9]{64})$/.test(args.attachment_id))
      throw err('INVALID_ARGS', `attachment_id 必须形如 sha256:<64hex>：${JSON.stringify(args.attachment_id)}`)
    return { attachmentId: args.attachment_id, mediaType: undefined, width: undefined, height: undefined }
  }
  const derive = exec && exec.agent && exec.agent.session && exec.agent.session.deriveMessages
  const msgs = typeof derive === 'function' ? derive.call(exec.agent.session) : undefined
  if (!Array.isArray(msgs)) throw err('NO_IMAGE_IN_SESSION', '会话不可用或无消息（无法定位图片）')
  const index = (typeof args.attachment_index === 'number') ? Math.max(0, args.attachment_index) : 0
  const images = []
  for (let i = msgs.length - 1; i >= 0; i--) {
    const m = msgs[i]
    if (m && m.role === 'user' && Array.isArray(m.content)) {
      for (const block of m.content) {
        if (block && block.type === 'image') {
          const att = (block.attachment && typeof block.attachment === 'object') ? block.attachment : {}
          const id = att.attachmentId ?? att.id ?? block.attachmentId
          if (id) images.push({ attachmentId: id, mediaType: att.mediaType ?? block.mediaType, width: att.width ?? block.width, height: att.height ?? block.height })
        }
      }
    }
  }
  if (images.length === 0) throw err('NO_IMAGE_IN_SESSION', '会话中没有任何图片')
  if (index >= images.length) throw err('NO_IMAGE_IN_SESSION', `attachment_index=${index} 越界（会话共 ${images.length} 张图）`)
  return images[index]
}

function validateArgs(args) {
  // v1.5 被动模式：inbox（收件箱）——用户同意存图但未给去向时的默认目标，target_name 可省略
  if (!['site', 'daily', 'report', 'inbox'].includes(args.target_kind)) throw err('INVALID_ARGS', `target_kind 必须是 site/daily/report/inbox：${JSON.stringify(args.target_kind)}`)
  if (args.target_kind !== 'inbox' && (typeof args.target_name !== 'string' || args.target_name.trim() === '')) throw err('INVALID_ARGS', 'target_name 必填（非空字符串；target_kind=inbox 时可省略）')
  if (args.attachment_index !== undefined && !(Number.isInteger(args.attachment_index) && args.attachment_index >= 0)) throw err('INVALID_ARGS', 'attachment_index 必须是非负整数')
}

async function runMetrics(ctx, cfg, imgPath, exec, ref) {
  try {
    const m = await runPython(ctx, cfg, 'image_metrics.py', {
      path: imgPath,
      thresholds: { short_edge_min: cfg.shortEdgeMin, aspect_max: cfg.aspectMax, laplacian_min: cfg.laplacianMin },
    }, [], exec)
    if (m && m.ok === true) {
      return {
        width: m.width, height: m.height, short_edge_px: m.short_edge_px,
        aspect_ratio: m.aspect_ratio, laplacian_var: (m.laplacian_var === undefined ? null : m.laplacian_var),
        too_small: (m.too_small === undefined ? null : m.too_small), flags: m.flags || [],
      }
    }
    throw new Error('metrics not ok')
  } catch {
    // python 不可用 → 兜底 quality，照常成功
    return {
      width: (ref.width ?? null), height: (ref.height ?? null),
      short_edge_px: null, aspect_ratio: null, laplacian_var: null, too_small: null,
      flags: ['metrics_unavailable'],
    }
  }
}

function renderSave(v) {
  const w = v.width ?? '?', h = v.height ?? '?'
  const md = v.reference.markdown ?? v.reference.html ?? ''
  return `saved ${v.name} -> ${v.path} (${w}x${h}, ${v.bytes}B) | md: ${md} | too_small=${v.quality.too_small}`
}

export function register(ctx, config) {
  ctx.tools.register({
    name: 'save_screenshot',
    description: 'Save the most recent pasted screenshot from this conversation to a named image file in a target site/daily-report/report directory. Returns the file path, image metrics, and ready-to-paste HTML/Markdown references.',
    parameters: {
      type: 'object',
      properties: {
        target_kind: { type: 'string', enum: ['inbox', 'site', 'daily', 'report'], description: '目标域：inbox=收件箱（用户同意存图但未给去向时的默认去向）/ site=team-share 站 / daily=日报项目 / report=独立报告' },
        target_name: { type: 'string', description: '站目录名（如 advanced-design）/ 日报项目名（如 HK1V11）/ 报告目录名；target_kind=inbox 时可省略' },
        slug: { type: 'string', description: '文件名主题段，净化为 [a-z0-9-]{1,24}，缺省 shot' },
        alt: { type: 'string', description: '引用里的 alt 文本，缺省 = slug' },
        attachment_index: { type: 'integer', description: '取会话中第几张图，0=最近一张（默认），1=上一张，依此向前' },
        attachment_id: { type: 'string', description: '显式指定 attachmentId（形如 sha256:<64hex>；给了则忽略 attachment_index）' },
      },
      required: ['target_kind'],
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
          sha256: { type: 'string'},
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
            type: 'object',
            additionalProperties: false,
            properties: {
              html: { type: 'string' },
              markdown: { type: 'string' },
              markdown_absolute: { type: 'string' },
            },
            required: ['html', 'markdown', 'markdown_absolute'],
          },
          gallery: {
            type: 'object',
            additionalProperties: false,
            properties: {
              sha256: { type: 'string' },
              canonical: { type: 'string' },
              implemented: { type: 'boolean' },
            },
            required: ['sha256', 'canonical', 'implemented'],
          },
          code: { type: 'string' },
        },
        required: ['ok', 'name', 'path', 'copies', 'bytes', 'width', 'height', 'mediaType', 'sha256', 'quality', 'reference', 'gallery'],
      },
      render: (_args, value) => [{ type: 'text', text: renderSave(value) }],
    },
    timeoutMs: 30000,
    async execute(args, exec) {
      const cfg = loadConfig(config)
      validateArgs(args)
      const ref = resolveSessionImageRef(exec, args)
      const digest = ref.attachmentId.slice(7)
      // 宿主绝对路径：优先 imageHostPath（传 ImageAttachmentRef 形状对象，非裸字符串——T7/P9 修正，
      // DSH 源码 attachment/src/index.ts:174 imageHostPath(ref: ImageAttachmentRef)），兜底 objects/ 直读
      const att = (ctx.get && ctx.get('attachments')) || ctx.attachments
      let hostPath = null
      if (att && typeof att.imageHostPath === 'function') {
        const refObj = { attachmentId: ref.attachmentId, mediaType: ref.mediaType, width: ref.width, height: ref.height }
        try { const r = att.imageHostPath(refObj); if (typeof r === 'string' && r) hostPath = r } catch { hostPath = null }
      }
      const srcPath = hostPath || path.join(cfg.dshHome, 'attachments', 'v1', 'objects', digest.slice(0, 2), digest)
      const bytes = await fs.readFile(srcPath) // 读字节（语义复制；写时不用硬链接）
      // 扩展名：mediaType 映射，无 mediaType 时 sniff 前 16 字节
      const mediaType = (ref.mediaType && MEDIA_EXT[ref.mediaType]) ? ref.mediaType : sniffMediaType(bytes)
      if (!mediaType || !MEDIA_EXT[mediaType]) throw err('SOURCE_NOT_IMAGE', `无法识别图片类型（mediaType=${ref.mediaType ?? '未知'}）`)
      const ext = MEDIA_EXT[mediaType]
      // 目标目录 + 文件名（命名防撞 + 日报双写）
      const { dirs, name, reference } = await resolveTarget(cfg, { kind: args.target_kind, name: args.target_name, slug: args.slug, alt: args.alt, ext })
      // 写入每个目录（语义复制）
      const copies = []
      for (const dir of dirs) {
        const p = path.join(dir, name)
        await fs.writeFile(p, bytes)
        copies.push(p)
      }
      // 体检（PIL 实测为准）
      const quality = await runMetrics(ctx, cfg, copies[0], exec, ref)
      return {
        ok: true,
        name,
        path: copies[0],
        copies,
        bytes: bytes.length,
        width: quality.width ?? null,
        height: quality.height ?? null,
        mediaType,
        sha256: digest,
        quality,
        reference,
        gallery: makeGallery(digest, ext),
      }
    },
  })
}
