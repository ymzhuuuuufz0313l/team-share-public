// render_diagram —— Phase 2 预留桩（§6.5）。
// MVP：参数 schema 冻结（structure 开放对象，MVP 不做深度校验）；execute 直接返回
// {ok:false, code:"NOT_IMPLEMENTED", implemented:false, planned}，绝不产出占位图。
// T7 合稿：description 与 planned 恢复 architecture.md §6.5 逐字契约文本。
// 系统提示（§12）已写明本工具未实现、禁止编造。
import { loadConfig } from '../config.js'
import { err } from '../report/resolve-target.js'

const PLANNED = 'Phase 2: fireworks-tech-graph style SVG -> validate-svg.sh -> CairoSVG -> PNG (T6 prefers gen_rtl_structure fixed layout)'

function validateArgs(args) {
  if (!['site', 'daily', 'report'].includes(args.target_kind)) throw err('INVALID_ARGS', `target_kind 必须是 site/daily/report：${JSON.stringify(args.target_kind)}`)
  if (typeof args.target_name !== 'string' || args.target_name.trim() === '') throw err('INVALID_ARGS', 'target_name 必填（非空字符串）')
}

export function register(ctx, config) {
  ctx.tools.register({
    name: 'render_diagram',
    description: 'Render a structure/flow diagram (blocks + arrows + badges) as blueprint-styled SVG/PNG. NOT IMPLEMENTED in MVP (Phase 2: fireworks-tech-graph SVG -> validate -> CairoSVG -> PNG); returns a stub result describing the planned flow.',
    parameters: {
      type: 'object',
      properties: {
        structure: { type: 'object', description: '图结构：{blocks[], arrows[], badges[]}（开放对象，MVP 不做深度校验）' },
        theme: { type: 'string', enum: ['paper', 'teal'], description: '缺省 paper' },
        target_kind: { type: 'string', enum: ['site', 'daily', 'report'], description: '落盘目标域' },
        target_name: { type: 'string', description: '站目录名 / 日报项目名 / 报告目录名' },
        slug: { type: 'string', description: '文件名主题段' },
        alt: { type: 'string', description: '引用里的 alt 文本' },
      },
      required: ['target_kind', 'target_name'],
    },
    output: {
      schema: {
        type: 'object',
        additionalProperties: false,
        properties: {
          ok: { type: 'boolean'},
          code: { type: 'string'},
          implemented: { type: 'boolean'},
          planned: { type: 'string'},
        },
        required: ['ok', 'code', 'implemented', 'planned'],
      },
      render: (_args, value) => [{ type: 'text', text: `render_diagram: NOT_IMPLEMENTED（${value.planned}）` }],
    },
    timeoutMs: 5000,
    async execute(args, _exec) {
      loadConfig(config)
      validateArgs(args)
      return { ok: false, code: 'NOT_IMPLEMENTED', implemented: false, planned: PLANNED }
    },
  })
}
