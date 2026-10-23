// 共享管道（5 个工具共用，禁止各写一份）：
//  1) 路径解析 / 命名防撞 / 引用片段生成（§7）
//  2) 源图解析（attachment_id | path 二选一，§6 通用约定）
//  3) 统一 Python 桥（§11 桥规范：优先 ctx.get('subprocess')，兜底 node:child_process.spawn）
import fs from 'node:fs/promises'
import { spawn as nodeSpawn } from 'node:child_process'
import path from 'node:path'
import os from 'node:os'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'

const PLUGIN_DIR = path.dirname(fileURLToPath(new URL('.', import.meta.url))) // impl-d/plugin/（本文件在 report/ 下）
const PY_DIR = path.join(PLUGIN_DIR, 'py')
const TMP_DIR = () => path.join(os.tmpdir(), 'screenshot-report')
const SOURCE_MAX_BYTES = 32 * 1024 * 1024 // 源图字节上限 32MB（§6 通用约定 A15）
const OUT_MAX = 1024 * 1024 // stdout ≤ 1MB
const ERR_MAX = 64 * 1024   // stderr ≤ 64KB

// --------------------------------------------------------------------------- 错误
// 基础设施失败 → throw 'CODE: message'（DSH 转 isError）。
export function err(code, message) {
  return new Error(`${code}: ${message}`)
}

// --------------------------------------------------------------------------- 哈希
export function sha256Hex(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex')
}

// --------------------------------------------------------------------------- slug 净化（§7.2）
// 小写、非 [a-z0-9-] → '-'、压缩连续 '-'、去首尾 '-'、截断 24；空 → shot。
export function slugify(slug) {
  if (typeof slug !== 'string' || slug.trim() === '') return 'shot'
  let s = slug.toLowerCase().replace(/[^a-z0-9-]/g, '-').replace(/-+/g, '-').replace(/^-+|-+$/g, '')
  s = s.slice(0, 24).replace(/-+$/g, '')
  return s === '' ? 'shot' : s
}

async function exists(p) {
  try { await fs.access(p); return true } catch { return false }
}

// --------------------------------------------------------------------------- 目标解析 + 命名 + 引用（§7）
// spec = { kind, name, slug, alt, ext }。返回 { dirs, name, reference, refDir }。
// dirs：按序全部写入目录（site=1，daily=1 或 2（双写），report=1）。
export async function resolveTarget(cfg, spec) {
  const { kind, name, slug, alt, ext } = spec
  if (!['site', 'daily', 'report', 'inbox'].includes(kind))
    throw err('INVALID_TARGET_NAME', `target_kind 必须是 site/daily/report/inbox，收到 ${JSON.stringify(kind)}`)
  if (kind !== 'inbox') {
    // v1.3：inbox（收件箱）不需要 target_name；其余目标必填且只允许安全字符
    if (typeof name !== 'string' || name.includes('..') || name.includes('/') || name.includes('\\') || !/^[A-Za-z0-9._-]+$/.test(name))
      throw err('INVALID_TARGET_NAME', `target_name 只允许 [A-Za-z0-9._-]，禁 .. / 路径分隔符：${JSON.stringify(name)}`)
  }

  let dirs = []
  let refDir = null // site 引用用 dir 令牌（无尾斜杠；"" = 站点根）

  if (kind === 'site') {
    const siteRoot = path.join(cfg.teamShareRoot, name)
    if (!await exists(path.join(siteRoot, 'index.html'))) {
      const list = await listIndexSites(cfg.teamShareRoot)
      throw err('SITE_NOT_FOUND', `site 不存在（无 index.html）：${siteRoot}；teamShareRoot 下含 index.html 的目录：${list.join(', ') || '(无)'}`)
    }
    refDir = (cfg.siteImageDirs && cfg.siteImageDirs[name] !== undefined) ? cfg.siteImageDirs[name] : 'assets' // 无尾斜杠
    const outDir = refDir === '' ? siteRoot : path.join(siteRoot, refDir)
    await fs.mkdir(outDir, { recursive: true })
    dirs = [outDir]
  } else if (kind === 'daily') {
    const projRoot = path.join(cfg.dailyRoot, name)
    if (!await exists(projRoot)) {
      const list = await listDirs(cfg.dailyRoot)
      throw err('PROJECT_NOT_FOUND', `日报项目不存在：${projRoot}；现有项目目录：${list.join(', ') || '(无)'}`)
    }
    const imgDir = path.join(projRoot, 'image')
    await fs.mkdir(imgDir, { recursive: true })
    dirs = [imgDir]
    if (cfg.dailyWriteGithubCopy) {
      const ghDir = path.join(cfg.dailyGithubImagesRoot, name)
      await fs.mkdir(ghDir, { recursive: true })
      dirs.push(ghDir)
    }
  } else if (kind === 'inbox') {
    // v1.5 被动模式：用户同意存图但未给去向时的默认收件箱（待整理区），不产生引用（整理到最终目标时再生成）
    const inboxDir = cfg.inboxRoot
    await fs.mkdir(inboxDir, { recursive: true })
    dirs = [inboxDir]
    refDir = null
  } else { // report
    const repRoot = path.join(cfg.reportRoot, name)
    if (!await exists(repRoot)) throw err('REPORT_NOT_FOUND', `报告目录不存在：${repRoot}`)
    const assetsDir = path.join(repRoot, 'assets')
    await fs.mkdir(assetsDir, { recursive: true })
    dirs = [assetsDir]
  }

  // 命名防撞（§7.2）：MMDD 用系统当前日期（本机时区），n 取首个使所有写入目录都不存在的值（上限 999）。
  const slugClean = slugify(slug)
  const d = new Date()
  const mmdd = `${String(d.getMonth() + 1).padStart(2, '0')}${String(d.getDate()).padStart(2, '0')}`
  let n = 0
  let fname
  for (;;) {
    n++
    if (n > 999) throw err('NAME_EXHAUSTED', `命名耗尽（>999）：${mmdd}_${slugClean}`)
    fname = `${mmdd}_${slugClean}_${n}.${ext}`
    let conflict = false
    for (const dir of dirs) if (await exists(path.join(dir, fname))) { conflict = true; break }
    if (!conflict) break
  }

  // 引用片段（§7.3）
  const altText = (typeof alt === 'string' && alt !== '') ? alt : slugClean
  const reference = {}
  if (kind === 'site') {
    const prefix = refDir === '' ? '' : `${refDir}/` // 恰一个 /；站点根无目录段
    reference.html = `<img src="${prefix}${fname}" alt="${altText}">`
    reference.markdown = `![${altText}](${prefix}${fname})`
    reference.markdown_absolute = null
  } else if (kind === 'daily') {
    reference.html = null
    reference.markdown = `![${altText}](image/${fname})`
    reference.markdown_absolute = `![${altText}](https://ymzhuuuuufz0313l.github.io/daily-record/images/${name}/${fname})`
  } else if (kind === 'inbox') {
    // 收件箱为待整理区，不产出引用片段（整理到最终目标时再生成）
    reference.html = null
    reference.markdown = null
    reference.markdown_absolute = null
  } else { // report
    reference.html = null
    reference.markdown = `![${altText}](assets/${fname})`
    reference.markdown_absolute = null
  }

  return { dirs, name: fname, reference, refDir }
}

// 中央图库接口字段（§7.4 / §10）。MVP implemented:false，绝不写中央图库。
export function makeGallery(sha256, ext) {
  return {
    sha256,
    canonical: `objects/${sha256.slice(0, 2)}/${sha256}.${ext}`,
    implemented: false,
  }
}

async function listIndexSites(root) {
  try {
    const entries = await fs.readdir(root, { withFileTypes: true })
    const out = []
    for (const e of entries) if (e.isDirectory() && await exists(path.join(root, e.name, 'index.html'))) out.push(e.name)
    return out
  } catch { return [] }
}
async function listDirs(root) {
  try {
    const entries = await fs.readdir(root, { withFileTypes: true })
    return entries.filter((e) => e.isDirectory()).map((e) => e.name)
  } catch { return [] }
}

// --------------------------------------------------------------------------- 源图解析（§6 通用约定）
// { attachment_id, path } 二选一。返回 { absPath, sourceKind, sourceId, sha256 }。
export async function resolveSource(cfg, { attachment_id, path }, ctx, exec) {
  const hasA = attachment_id !== undefined && attachment_id !== null && attachment_id !== ''
  const hasP = path !== undefined && path !== null && path !== ''
  if (hasA && hasP) throw err('SOURCE_AMBIGUOUS', 'attachment_id 与 path 二选一（两者都给了）')
  if (!hasA && !hasP) throw err('SOURCE_REQUIRED', 'attachment_id 与 path 至少给一个')

  if (hasA) {
    if (typeof attachment_id !== 'string' || !/^sha256:([a-f0-9]{64})$/.test(attachment_id))
      throw err('INVALID_ARGS', `attachment_id 必须形如 sha256:<64hex>：${JSON.stringify(attachment_id)}`) // T7/P9：并入 INVALID_ARGS（§6 错误码清单外无私有码）
    const digest = attachment_id.slice(7)
    let abs = null
    const att = (ctx && ctx.get && typeof ctx.get === 'function') ? ctx.get('attachments') : (ctx && ctx.attachments)
    if (att && typeof att.imageHostPath === 'function') {
      // 传 ImageAttachmentRef 形状对象（T7/P9：attachment/src/index.ts:174 imageHostPath(ref)），非裸字符串
      try { const r = att.imageHostPath({ attachmentId: attachment_id }); if (typeof r === 'string' && r) abs = r } catch { abs = null }
    }
    if (!abs) abs = path.join(cfg.dshHome, 'attachments', 'v1', 'objects', digest.slice(0, 2), digest) // 兜底直读
    if (!await exists(abs)) throw err('SOURCE_NOT_FOUND', `源图不存在：${abs}`)
    const st = await fs.stat(abs)
    if (st.size > SOURCE_MAX_BYTES) throw err('SOURCE_TOO_LARGE', `源图超过 32MB：${st.size} bytes`)
    return { absPath: abs, sourceKind: 'attachment_id', sourceId: attachment_id, sha256: digest }
  }
  // path：先 realpath 归一（解 .. 与符号链接），必须存在且可读
  const rp = await fs.realpath(path).catch(() => null)
  if (!rp) throw err('SOURCE_NOT_FOUND', `源图不存在：${path}`)
  const st = await fs.stat(rp)
  if (!st.isFile()) throw err('SOURCE_NOT_FOUND', `源图不是普通文件：${path}`)
  if (st.size > SOURCE_MAX_BYTES) throw err('SOURCE_TOO_LARGE', `源图超过 32MB：${st.size} bytes`)
  return { absPath: rp, sourceKind: 'path', sourceId: path, sha256: null }
}

// --------------------------------------------------------------------------- Python 桥（§11 桥规范）
// 优先 ctx.get('subprocess')（进程树级 kill + 凭证 scrub + 收尾 grace）；拿不到/失败兜底 node:child_process.spawn。
// 入参 inputObj 写入临时 JSON 文件作为 argv[1]；extraArgs 为附加路径参数（render_chart 用）。
// 出参：stdout 恰好一行完整 JSON → 解析返回；非 0 退出 → throw PY_CRASH:<script>。
export async function runPython(ctx, cfg, scriptName, inputObj, extraArgs, exec, opts = {}) {
  const script = path.join(PY_DIR, scriptName)
  const tmpDir = TMP_DIR()
  await fs.mkdir(tmpDir, { recursive: true })
  const inPath = path.join(tmpDir, `sr_in_${Date.now()}_${Math.random().toString(36).slice(2, 8)}.json`)
  await fs.writeFile(inPath, JSON.stringify(inputObj ?? {}), 'utf8')
  const argv = [script, inPath, ...(extraArgs || [])]
  const signal = exec && exec.signal ? exec.signal : undefined
  const cwd = opts.cwd
  let res
  const svc = (ctx && ctx.get && typeof ctx.get === 'function') ? ctx.get('subprocess') : undefined
  if (svc && typeof svc.spawn === 'function') {
    try { res = await spawnViaSubprocess(svc, cfg.venvPython, argv, { cwd, signal }) }
    catch { res = await spawnViaNode(cfg.venvPython, argv, { cwd, signal }) }
  } else {
    res = await spawnViaNode(cfg.venvPython, argv, { cwd, signal })
  }
  await fs.rm(inPath, { force: true }).catch(() => {})
  if (signal && signal.aborted) throw err('PY_ABORTED', '子进程已取消（AbortSignal 触发）')
  if (res.code !== 0) throw err('PY_CRASH', `${scriptName}: 退出码 ${res.code}\n${(res.stderr || '').slice(-4096)}`)
  const line = (res.stdout || '').trim().split('\n').filter((l) => l.trim() !== '').pop()
  if (!line) throw err('PY_CRASH', `${scriptName}: stdout 为空`)
  try { return JSON.parse(line) } catch { throw err('PY_CRASH', `${scriptName}: stdout 非合法 JSON：${line.slice(0, 300)}`) }
}

async function spawnViaSubprocess(svc, venvPython, argv, { cwd, signal }) {
  const handle = svc.spawn({
    argv: [venvPython, ...argv],
    cwd: cwd || os.tmpdir(),
    stdio: { stdin: 'ignore', stdout: 'pipe', stderr: 'pipe' },
    graceMs: 2000,
    ...(signal ? { signal } : {}),
  })
  let out = '', errb = ''
  if (handle.stdout) for await (const chunk of handle.stdout) { if (out.length < OUT_MAX) out += chunk }
  if (handle.stderr) for await (const chunk of handle.stderr) { if (errb.length < ERR_MAX) errb += chunk }
  const outcome = await handle.done
  return { code: outcome.exitCode, stdout: out, stderr: errb }
}

function spawnViaNode(venvPython, argv, { cwd, signal }) {
  return new Promise((resolve, reject) => {
    let child
    try { child = nodeSpawn(venvPython, argv, { cwd: cwd || undefined, ...(signal ? { signal } : {}) }) }
    catch (e) { reject(new Error(`PY_SPAWN_ERROR: ${e.message}`)); return }
    let out = '', errb = ''
    child.stdout.on('data', (d) => { if (out.length < OUT_MAX) out += d })
    child.stderr.on('data', (d) => { if (errb.length < ERR_MAX) errb += d })
    child.on('error', (e) => reject(new Error(`PY_SPAWN_ERROR: ${e.message}`)))
    child.on('close', (code) => resolve({ code, stdout: out, stderr: errb }))
  })
}
