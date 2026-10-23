// e2e-demo.mjs — T7 终审验收演练（非 smoke 契约，真实团队校准图端到端）。
// 用工作区根 tests/fixtures/ 校准图走完整流水线：
//   贴图（mock 附件 sha256）→ save_screenshot 落盘+体检 → 判断（小图/糊度门禁演示）
//   → keep 路径：crop_image auto_trim（padding.png 清理无效边）
//   → redraw 路径：extract_table 真跑 OCR（table_like.png）→ render_chart 重绘 → <img>/Markdown 引用
// 运行：node test/e2e-demo.mjs   （沙箱根 = test/tmp-sandbox/e2e/，绝不碰生产目录）
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'

const TEST_DIR = new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')
const TMP = path.join(TEST_DIR, 'tmp-sandbox', 'e2e')
const VENV_PY = process.env.VENV_PYTHON || 'E:/project/team-share-public/synthesis-integration-flow-guide/script/.venv/Scripts/python.exe'
const BACKPPT = process.env.BACKPPT_SCRIPT_DIR || 'E:/project/team-share-public/synthesis-integration-flow-guide/script'
const FIXTURES_ROOT = path.resolve(TEST_DIR, '..', '..', 'tests', 'fixtures')

process.env.SSRP_TEAM_SHARE_ROOT = path.join(TMP, 'team-share')
process.env.SSRP_DAILY_ROOT = path.join(TMP, 'daily')
process.env.SSRP_DAILY_GITHUB_IMAGES_ROOT = path.join(TMP, 'daily-github', 'images')
process.env.SSRP_REPORT_ROOT = path.join(TMP, 'report')
process.env.DSH_HOME = path.join(TMP, 'dsh-home')
process.env.SSRP_VENV_PYTHON = VENV_PY
process.env.SSRP_BACKPPT_SCRIPT_DIR = BACKPPT

const shaFile = (p) => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex')

// ---- 沙箱站点
fs.rmSync(TMP, { recursive: true, force: true })
fs.mkdirSync(path.join(TMP, 'team-share', 'demo-e2e'), { recursive: true })
fs.writeFileSync(path.join(TMP, 'team-share', 'demo-e2e', 'index.html'), '<html></html>')

// ---- mock ctx/exec（模拟"贴图"）
const tableLike = path.join(FIXTURES_ROOT, 'table_like.png')
const padding = path.join(FIXTURES_ROOT, 'padding.png')
const hostPaths = { ['sha256:' + shaFile(tableLike)]: tableLike, ['sha256:' + shaFile(padding)]: padding }
const ctx = {
  tools: { register() { return () => {} } },
  effect(fn) { fn() },
  get(n) {
    if (n === 'systemPrompt') return { section() {} }
    if (n === 'attachments') return { imageHostPath: (ref) => hostPaths[typeof ref === 'string' ? ref : ref.attachmentId] || null }
    return undefined
  },
  attachments: { imageHostPath: (ref) => hostPaths[typeof ref === 'string' ? ref : ref.attachmentId] || null },
}
const exec = (msgs) => ({ agent: { session: { deriveMessages: () => msgs } }, signal: new AbortController().signal })

const mod = await import('../index.js')
const reg = []
const captureCtx = { ...ctx, tools: { register(def) { reg.push(def); return () => {} } }, effect(fn) { fn() }, get: ctx.get, attachments: ctx.attachments }
mod.apply(captureCtx, {})
const tool = (n) => reg.find((t) => t.name === n).execute
const imgMsg = (p) => [{ role: 'user', content: [{ type: 'image', attachment: { attachmentId: 'sha256:' + shaFile(p), mediaType: 'image/png' } }] }]

console.log('== E2E 演练（tests/fixtures 校准图）==\n')

// 1) 贴图 → save_screenshot（redraw 路径留底）
const saved = await tool('save_screenshot')({ target_kind: 'site', target_name: 'demo-e2e', slug: 'table-e2e' }, exec(imgMsg(tableLike)))
console.log(`[1] save_screenshot: ${saved.name} ${saved.width}x${saved.height} too_small=${saved.quality.too_small} flags=[${saved.quality.flags.join(',')}]`)

// 2) 判断：富描述符结论（演示；门禁字段全部取工具输出）
const ext = await tool('extract_table')({ path: saved.path }, exec([]))
console.log(`[2] extract_table: n_rows=${ext.n_rows} n_cols_max=${ext.n_cols_max} mean=${ext.cell_confidence_mean} frac_low=${ext.frac_low_confidence} unreliable=${ext.unreliable}`)
const decision = (ext.unreliable === false && saved.quality.laplacian_var >= 50) ? 'redraw' : 'keep'
console.log(`    → 判断：decision=${decision}（unreliable=${ext.unreliable}，laplacian_var=${saved.quality.laplacian_var} ≥50 才 redraw）`)

// 3a) redraw：OCR 行 → 规整为等宽（ragged_rows 是 OCR 已知行为，喂模板前需整形）→ render_chart（plain 演示）
if (decision === 'redraw') {
  const W_ = ext.n_cols_max
  const pad = (r) => Array.from({ length: W_ }, (_, i) => r[i] ?? '')
  const headers = [pad(ext.rows[0])]
  const rows = ext.rows.slice(1).filter((r) => r.length > 0).map(pad)
  const ren = await tool('render_chart')({ template: 'table', theme: 'paper', target_kind: 'site', target_name: 'demo-e2e', slug: 'table-redraw', data: { title: 'e2e table_like.png', subtitle: 'redraw from OCR', headers, rows, mode: 'plain' } }, exec([]))
  console.log(`[3a] render_chart: ok=${ren.ok} self_check=${ren.self_check} ${ren.name} ${ren.width}x${ren.height}`)
  console.log(`     ${ren.reference.html}`)
  console.log(`     ${ren.reference.markdown}`)
}

// 3b) keep：padding.png auto_trim 清理无效边
const savedP = await tool('save_screenshot')({ target_kind: 'site', target_name: 'demo-e2e', slug: 'pad-e2e' }, exec(imgMsg(padding)))
const crop = await tool('crop_image')({ path: savedP.path, target_kind: 'site', target_name: 'demo-e2e', slug: 'pad-trim', auto_trim: true }, exec([]))
console.log(`[3b] crop auto_trim: ${savedP.width}x${savedP.height} → ${crop.width}x${crop.height} ${crop.name}`)
console.log(`     ${crop.reference.html}`)

console.log('\nE2E OK')
