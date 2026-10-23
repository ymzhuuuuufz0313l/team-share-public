// smoke.mjs — 四路一致的硬口径验收（§14.3）。
// 离线 mock 运行：不挂载、不真机、不 LLM、不碰生产目录（4 个根指到 test/tmp-sandbox/）。
// 用法：node test/smoke.mjs [register|save|crop|extract|render|diagram]  （无子命令 = S0–S6 全跑）
import crypto from 'node:crypto'
import fs from 'node:fs'
import path from 'node:path'
import { spawnSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const TEST_DIR = fileURLToPath(new URL('.', import.meta.url))
const FIX_DIR = path.join(TEST_DIR, 'fixtures')
const TMP = path.join(TEST_DIR, 'tmp-sandbox')
const VENV_PY = process.env.VENV_PYTHON || 'E:/project/team-share-public/synthesis-integration-flow-guide/script/.venv/Scripts/python.exe'
const BACKPPT = process.env.BACKPPT_SCRIPT_DIR || 'E:/project/team-share-public/synthesis-integration-flow-guide/script'

// 把 4 个根 + 沙箱指到 tmp-sandbox（§14：绝不碰生产目录）
process.env.SSRP_TEAM_SHARE_ROOT = path.join(TMP, 'team-share')
process.env.SSRP_DAILY_ROOT = path.join(TMP, 'daily')
process.env.SSRP_DAILY_GITHUB_IMAGES_ROOT = path.join(TMP, 'daily-github', 'images')
process.env.SSRP_REPORT_ROOT = path.join(TMP, 'report')
process.env.DSH_HOME = path.join(TMP, 'dsh-home')
process.env.SSRP_DAILY_WRITE_GITHUB = '1'
process.env.SSRP_VENV_PYTHON = VENV_PY
process.env.SSRP_BACKPPT_SCRIPT_DIR = BACKPPT

// --------------------------------------------------------------------------- helpers
let passed = 0
let failed = 0
function assert(cond, label) {
  if (cond) { passed++; console.log('  \u2713 ' + label) }
  else { failed++; console.error('  \u2717 ' + label) }
}
async function assertThrowsAsync(fn, code, label) {
  try {
    await fn()
    failed++
    console.error('  \u2717 ' + label + ' (did not throw)')
  } catch (e) {
    if (code && !String(e.message).includes(code)) {
      failed++
      console.error('  \u2717 ' + label + ` (threw without ${code}: ${e.message})`)
    } else { passed++; console.log('  \u2713 ' + label) }
  }
}
function shaFile(p) { return crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex') }
function pyProbe(mode, p, ...args) {
  const r = spawnSync(VENV_PY, [path.join(TEST_DIR, '_py_probe.py'), mode, p, ...args], { encoding: 'utf8' })
  if (r.status !== 0) throw new Error('py_probe failed: ' + (r.stderr || ''))
  return r.stdout.trim()
}
function pyGetPixel(p, x, y) { return JSON.parse(pyProbe('pixel', p, x, y)) }
function pyFindColor(p, rgb, tol) { return pyProbe('find', p, JSON.stringify(rgb), tol) === '1' }

// --------------------------------------------------------------------------- mock ctx
let hostPaths = {}
let spSectionCalls = [] // T7/P12：捕获 sp.section 调用参数（mock effect 立即执行 fn，验签名形状）
function makeMockCtx(registered) {
  return {
    tools: { register(def) { registered.push(def); return () => {} } },
    effect(fn, _id) { try { fn() } catch { /* 捕获期错误留给 S0e 断言 */ } },
    get(n) {
      if (n === 'systemPrompt') return { section(args) { spSectionCalls.push(args) } }
      if (n === 'attachments') return { imageHostPath: (ref) => hostPaths[typeof ref === 'string' ? ref : ref.attachmentId] || null }
      return undefined // subprocess → 走 node:child_process.spawn 兜底
    },
    attachments: { imageHostPath: (ref) => hostPaths[typeof ref === 'string' ? ref : ref.attachmentId] || null },
  }
}
function makeExec(msgs) {
  return { agent: { session: { deriveMessages: () => msgs } }, signal: new AbortController().signal }
}

// --------------------------------------------------------------------------- setup
let shaWhite, shaTable
async function setup() {
  fs.rmSync(TMP, { recursive: true, force: true })
  fs.mkdirSync(path.join(TMP, 'team-share', 'demo-site'), { recursive: true })
  fs.writeFileSync(path.join(TMP, 'team-share', 'demo-site', 'index.html'), '<html></html>')
  fs.mkdirSync(path.join(TMP, 'daily', 'HK1V11'), { recursive: true })
  fs.mkdirSync(path.join(TMP, 'dsh-home'), { recursive: true })
  const fix = spawnSync(VENV_PY, [path.join(TEST_DIR, 'make_fixtures.py')], { encoding: 'utf8' })
  if (fix.status !== 0) throw new Error('make_fixtures.py failed: ' + ((fix.stderr || '') + (fix.stdout || '')))
  shaWhite = shaFile(path.join(FIX_DIR, 'f_white_rect.png'))
  shaTable = shaFile(path.join(FIX_DIR, 'f_table.png'))
  hostPaths = {
    ['sha256:' + shaWhite]: path.join(FIX_DIR, 'f_white_rect.png'),
    ['sha256:' + shaTable]: path.join(FIX_DIR, 'f_table.png'),
  }
}
function imageMsg() {
  return [{ role: 'user', content: [{ type: 'image', attachment: { attachmentId: 'sha256:' + shaWhite, mediaType: 'image/png', width: 1000, height: 700 } }] }]
}

// --------------------------------------------------------------------------- S0
async function s0() {
  console.log('\nS0 register')
  const registered = []
  const mod = await import('../index.js')
  assert(mod.default === undefined, 'S0a: no default export')
  assert(mod.name === 'screenshot-report', 'S0b: name === screenshot-report')
  mod.apply(makeMockCtx(registered), {})
  assert(registered.length === 5, `S0c: exactly 5 tools (got ${registered.length})`)
  const names = registered.map((t) => t.name).sort()
  const expect = ['crop_image', 'extract_table', 'render_chart', 'render_diagram', 'save_screenshot'].sort()
  assert(JSON.stringify(names) === JSON.stringify(expect), 'S0c2: 5 tool names match')
  for (const t of registered) {
    assert(t.output && t.output.schema && t.output.schema.type === 'object', `S0d: ${t.name} output.schema object`)
    assert(typeof t.output.render === 'function', `S0d: ${t.name} output.render function`)
    assert(typeof t.timeoutMs === 'number', `S0d: ${t.name} timeoutMs number`)
  }
  // T7/P12 新增：sp.section 调用形状断言（真实签名 {name, order, text}，四路原稿全错、mock 曾吞掉）
  assert(spSectionCalls.length === 1, `S0e: sp.section 恰好调用 1 次 (got ${spSectionCalls.length})`)
  const sp = spSectionCalls[0] || {}
  assert(sp.name === 'screenshot-report', `S0e: section.name === screenshot-report (got ${JSON.stringify(sp.name)})`)
  assert(typeof sp.order === 'number' && Number.isFinite(sp.order), `S0e: section.order 有限数 (got ${JSON.stringify(sp.order)})`)
  assert(typeof sp.text === 'string' && sp.text.includes('save_screenshot') && sp.text.includes('summary') && sp.text.includes('laplacian_var'), 'S0e: section.text 为 §12 全文（含 save_screenshot/summary/laplacian_var）')
  assert(sp.title === undefined && sp.body === undefined && sp.content === undefined, 'S0e: 无 title/body/content 伪键（P1 修正验证）')
}

// --------------------------------------------------------------------------- S1
async function s1() {
  console.log('\nS1 save·site')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const save = registered.find((t) => t.name === 'save_screenshot')
  const out = await save.execute({ target_kind: 'site', target_name: 'demo-site', slug: 'Demo Shot!' }, makeExec(imageMsg()))
  const assetsDir = path.join(TMP, 'team-share', 'demo-site', 'assets')
  assert(fs.existsSync(path.join(assetsDir, out.name)), `S1a: file in demo-site/assets/ (${out.name})`)
  assert(/^\d{4}_demo-shot_1\.png$/.test(out.name), `S1b: name format (got ${out.name})`)
  assert(out.reference.html === `<img src="assets/${out.name}" alt="demo-shot">`, `S1c: reference.html (got ${out.reference.html})`)
  assert(out.quality.width === 1000 && out.quality.height === 700, `S1d: quality 1000x700 (got ${out.quality.width}x${out.quality.height})`)
  assert(out.gallery.sha256 === shaWhite && out.gallery.implemented === false, 'S1e: gallery.sha256 + implemented=false')
}

// --------------------------------------------------------------------------- S2
async function s2() {
  console.log('\nS2 save·防撞+daily双写')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const save = registered.find((t) => t.name === 'save_screenshot')
  // S1 已落 _1；同名再调 → _2
  const out2 = await save.execute({ target_kind: 'site', target_name: 'demo-site', slug: 'Demo Shot!' }, makeExec(imageMsg()))
  assert(/_2\.png$/.test(out2.name), `S2a: 第二次同名以 _2.png 结尾 (got ${out2.name})`)
  // daily 双写
  const outD = await save.execute({ target_kind: 'daily', target_name: 'HK1V11', slug: 'shot' }, makeExec(imageMsg()))
  const imgDir = path.join(TMP, 'daily', 'HK1V11', 'image')
  const ghDir = path.join(TMP, 'daily-github', 'images', 'HK1V11')
  assert(fs.existsSync(path.join(imgDir, outD.name)) && fs.existsSync(path.join(ghDir, outD.name)), 'S2b: daily 双写两个目录同名文件')
  assert(outD.reference.markdown === `![shot](image/${outD.name})`, `S2c1: markdown (got ${outD.reference.markdown})`)
  assert(outD.reference.markdown_absolute && outD.reference.markdown_absolute.includes('https://ymzhuuuuufz0313l.github.io/daily-record/images/HK1V11/'), 'S2c2: markdown_absolute 含 GitHub 绝对 URL')
  await assertThrowsAsync(() => save.execute({ target_kind: 'site', target_name: 'demo-site', slug: 'x' }, makeExec([])), 'NO_IMAGE_IN_SESSION', 'S2d: 无图 → NO_IMAGE_IN_SESSION')
}

// --------------------------------------------------------------------------- S3
async function s3() {
  console.log('\nS3 crop')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const crop = registered.find((t) => t.name === 'crop_image')
  const exec = makeExec([])
  const white = path.join(FIX_DIR, 'f_white_rect.png')
  const outBox = await crop.execute({ path: white, target_kind: 'site', target_name: 'demo-site', slug: 'crop', box: { left: 0.05, top: 0.05, right: 0.5, bottom: 0.5 } }, exec)
  assert(outBox.width === 450 && outBox.height === 315, `S3: box crop 450x315 (got ${outBox.width}x${outBox.height})`)
  const outTrim = await crop.execute({ path: white, target_kind: 'site', target_name: 'demo-site', slug: 'trim', auto_trim: true }, exec)
  assert(outTrim.width === 200 && outTrim.height === 100, `S3: auto_trim 200x100 (got ${outTrim.width}x${outTrim.height})`)
  const assetsDir = path.join(TMP, 'team-share', 'demo-site', 'assets')
  assert(fs.existsSync(path.join(assetsDir, outBox.name)) && fs.existsSync(path.join(assetsDir, outTrim.name)), 'S3a: 两输出 PNG 落 demo-site/assets/')
  assert(Math.abs(outBox.quality.aspect_ratio - (450 / 315)) < 0.01, `S3b: aspect_ratio = w/h (got ${outBox.quality.aspect_ratio})`)
  const outSmall = await crop.execute({ path: path.join(FIX_DIR, 'f_small.png'), target_kind: 'site', target_name: 'demo-site', slug: 'small', box: { left: 0, top: 0, right: 1, bottom: 1 } }, exec)
  assert(outSmall.quality.too_small === true && outSmall.quality.flags.includes('short_edge_lt_480'), 'S3c: f_small too_small + short_edge_lt_480')
  await assertThrowsAsync(() => crop.execute({ path: white, target_kind: 'site', target_name: 'demo-site', slug: 'x' }, exec), 'CROP_SPEC_REQUIRED', 'S3d: box 与 auto_trim 都缺 → CROP_SPEC_REQUIRED')
  const outThin = await crop.execute({ path: path.join(FIX_DIR, 'f_thin.png'), target_kind: 'site', target_name: 'demo-site', slug: 'thin', box: { left: 0, top: 0, right: 1, bottom: 1 } }, exec)
  assert(outThin.quality.too_small === true && outThin.quality.flags.includes('aspect_gt_8') && !outThin.quality.flags.includes('short_edge_lt_480'), 'S3e: f_thin aspect_gt_8 且不含 short_edge_lt_480')
  // T7 新增（四路共性 M5）：空裁剪是领域结果 → return ok:false + code CROP_EMPTY（不 throw，§11.2:609）
  const outEmpty = await crop.execute({ path: white, target_kind: 'site', target_name: 'demo-site', slug: 'empty', box: { left: 0.5, top: 0, right: 0.5, bottom: 1 } }, exec)
  assert(outEmpty && outEmpty.ok === false && outEmpty.code === 'CROP_EMPTY', `S3f: 0 面积裁剪 → return {ok:false, code:'CROP_EMPTY'} (got ok=${outEmpty && outEmpty.ok} code=${outEmpty && outEmpty.code})`)
}

// --------------------------------------------------------------------------- S4
async function s4() {
  console.log('\nS4 extract')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const extract = registered.find((t) => t.name === 'extract_table')
  const out = await extract.execute({ path: path.join(FIX_DIR, 'f_table.png') }, makeExec([]))
  assert(out.ok === true && out.engine === 'rapidocr-onnxruntime', `S4a: ok + engine (got ok=${out.ok} engine=${out.engine})`)
  assert(out.rows.length >= 3, `S4b: rows.length >= 3 (got ${out.rows.length})`)
  const hasSetup = out.rows.some((r) => r.join(' ').toLowerCase().includes('setup'))
  assert(hasSetup, 'S4c①(硬): 某行 join 含 setup')
  assert((out.unreliable === false || out.warnings.length > 0) && out.n_rows >= 2, `S4c②(硬): unreliable 门禁 (unreliable=${out.unreliable} n_rows=${out.n_rows} warnings=${out.warnings.join(',')})`)
  assert(typeof out.unreliable === 'boolean', `S4d: unreliable 是 boolean (got ${typeof out.unreliable})`)
  console.log(`     参考: n_rows=${out.n_rows} n_cols_max=${out.n_cols_max} mean=${out.cell_confidence_mean} frac_low=${out.frac_low_confidence} rows=${JSON.stringify(out.rows)}`)
}

// --------------------------------------------------------------------------- S5
async function s5() {
  console.log('\nS5 render')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const render = registered.find((t) => t.name === 'render_chart')
  const data = {
    title: 'report_setup.csv', subtitle: 'demo',
    headers: [['Corner', 'slack', 'value', 'count'], ['', '(ns)', '#', '#']],
    rows: [['setup', '-0.012', '5', '3'], ['hold', '0.045', '0', '0'], ['trans', '-0.301', '24', '12']],
    mode: 'violation',
  }
  const out = await render.execute({ template: 'table', theme: 'paper', target_kind: 'site', target_name: 'demo-site', slug: 'rpt', data }, makeExec([]))
  assert(out.ok === true && out.self_check === 'passed', `S5a: ok + self_check passed (got ok=${out.ok} self_check=${out.self_check} code=${out.code})`)
  const assetsDir = path.join(TMP, 'team-share', 'demo-site', 'assets')
  assert(fs.existsSync(path.join(assetsDir, out.name)) && /^\d{4}_rpt_1\.png$/.test(out.name), `S5b: PNG + name format (got ${out.name})`)
  const p55 = pyGetPixel(path.join(assetsDir, out.name), 5, 5)
  assert(Math.abs(p55[0] - 28) <= 8 && Math.abs(p55[1] - 37) <= 8 && Math.abs(p55[2] - 52) <= 8, `S5c: (5,5)≈(28,37,52)±8 (got ${JSON.stringify(p55)})`)
  assert(pyFindColor(path.join(assetsDir, out.name), [239, 224, 218], 8), 'S5d: 负值整格出现 bad_bg (239,224,218)±8')
  const outTeal = await render.execute({ template: 'table', theme: 'teal', target_kind: 'site', target_name: 'demo-site', slug: 'rpt-teal', data }, makeExec([]))
  const pTeal = pyGetPixel(path.join(assetsDir, outTeal.name), 5, 5)
  assert(Math.abs(pTeal[0] - 14) <= 8 && Math.abs(pTeal[1] - 124) <= 8 && Math.abs(pTeal[2] - 107) <= 8, `S5e: teal (5,5)≈(14,124,107)±8 (got ${JSON.stringify(pTeal)})`)
  // T7 新增（锁 impl-a 曾偏离的 §6.4 契约）：[] 分隔缝行合法（半高分隔缝），渲染 + 自检须通过
  const dataGap = { ...data, rows: [['setup', '-0.012', '5', '3'], [], ['trans', '-0.301', '24', '12']] }
  const outGap = await render.execute({ template: 'table', theme: 'paper', target_kind: 'site', target_name: 'demo-site', slug: 'rpt-gap', data: dataGap }, makeExec([]))
  assert(outGap.ok === true && outGap.self_check === 'passed', `S5f: 含 [] 分隔缝渲染通过 (got ok=${outGap.ok} self_check=${outGap.self_check} code=${outGap.code})`)
  assert(fs.existsSync(path.join(assetsDir, outGap.name)), 'S5f: 分隔缝产物落盘')
}

// --------------------------------------------------------------------------- S6
async function s6() {
  console.log('\nS6 diagram 桩')
  const registered = []
  const mod = await import('../index.js')
  const ctx = makeMockCtx(registered)
  mod.apply(ctx, {})
  const diagram = registered.find((t) => t.name === 'render_diagram')
  const out = await diagram.execute({ target_kind: 'site', target_name: 'demo-site' }, makeExec([]))
  assert(out.ok === false && out.code === 'NOT_IMPLEMENTED' && out.implemented === false, `S6: 桩 NOT_IMPLEMENTED (got ok=${out.ok} code=${out.code} implemented=${out.implemented})`)
}

// --------------------------------------------------------------------------- main
const sub = process.argv[2]
try {
  if (sub === 'register') { await s0() }
  else if (sub === 'save') { await setup(); await s1(); await s2() }
  else if (sub === 'crop') { await setup(); await s3() }
  else if (sub === 'extract') { await setup(); await s4() }
  else if (sub === 'render') { await setup(); await s5() }
  else if (sub === 'diagram') { await setup(); await s6() }
  else {
    await setup()
    await s0(); await s1(); await s2(); await s3(); await s4(); await s5(); await s6()
  }
} catch (e) {
  failed++
  console.error('\nFATAL: ' + (e && e.stack || e))
}
console.log(`\n${passed} passed, ${failed} failed`)
process.exit(failed > 0 ? 1 : 0)
