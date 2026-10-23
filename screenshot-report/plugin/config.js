// screenshot-report 插件配置（§5）。
// 三级来源：SSRP_* 环境变量 > row config（cordis.patch.yml 该条目 config:，经 apply(ctx, config) 传入）> 内置默认。
// loadConfig() 每次调用现读环境（工具执行时取），不缓存跨调用状态。
import os from 'node:os'
import { fileURLToPath } from 'node:url'

// 内置默认值即真实生产路径；smoke 测试用 SSRP_* 环境变量把 4 个根指到 test/tmp-sandbox/（§14），从而绝不碰生产目录。
const defaults = {
  teamShareRoot: 'E:/project/team-share-public',
  dailyRoot: 'E:/每日记录',
  dailyGithubImagesRoot: 'E:/每日记录/daily-record-site-github/images',
  dailyWriteGithubCopy: true,
  reportRoot: 'E:/report',
  venvPython: 'E:/project/team-share-public/synthesis-integration-flow-guide/script/.venv/Scripts/python.exe',
  backpptScriptDir: 'E:/project/team-share-public/synthesis-integration-flow-guide/script',
  centralGalleryRoot: 'E:/project/team-share-public/assets',
  // v1.5 被动模式：用户同意存图但未给去向时的默认收件箱（待整理区；判定后可再整理到 site/daily/report）
  inboxRoot: 'E:/每日记录/screenshot-inbox',
  // per-site 图片目录映射（T4 定稿，2026-10-21 实测）：dir = siteImageDirs[name] ?? "assets"，dir 一律无尾斜杠（"" = 站点根）。
  siteImageDirs: {
    'advanced-design': 'image',
    'synthesis-integration-flow-guide': 'image',
    'hk1v11-lc-cpuwr-history': 'images',
    'hk1v11-synthesis-postpt-practice': 'images',
    'hv2m23-agent-vm-workflow': 'img',
    'hk1v11-longcode-420b-verification': '',
  },
  themesFile: fileURLToPath(new URL('./templates/themes.json', import.meta.url)),
  shortEdgeMin: 480,      // 小图阈值：短边 px（恰等于 480 不触发）
  aspectMax: 8,           // 小图阈值：长宽比
  laplacianMin: 50.0,     // 小图阈值：Laplacian 方差
  ocrConfidenceMin: 0.70, // OCR 可靠阈值（均值；绑定 rapidocr 1.2.3 实机校准，§11.3）
  ocrLowConfFracMax: 0.30,// OCR 低置信格（score<0.60）占比上限
  defaultTheme: 'paper',
}

function envOverrides() {
  const e = process.env
  const o = {}
  if (e.SSRP_TEAM_SHARE_ROOT) o.teamShareRoot = e.SSRP_TEAM_SHARE_ROOT
  if (e.SSRP_DAILY_ROOT) o.dailyRoot = e.SSRP_DAILY_ROOT
  if (e.SSRP_DAILY_GITHUB_IMAGES_ROOT) o.dailyGithubImagesRoot = e.SSRP_DAILY_GITHUB_IMAGES_ROOT
  if (e.SSRP_DAILY_WRITE_GITHUB !== undefined) o.dailyWriteGithubCopy = e.SSRP_DAILY_WRITE_GITHUB !== '0'
  if (e.SSRP_REPORT_ROOT) o.reportRoot = e.SSRP_REPORT_ROOT
  if (e.SSRP_VENV_PYTHON) o.venvPython = e.SSRP_VENV_PYTHON
  if (e.SSRP_BACKPPT_SCRIPT_DIR) o.backpptScriptDir = e.SSRP_BACKPPT_SCRIPT_DIR
  if (e.SSRP_CENTRAL_GALLERY_ROOT) o.centralGalleryRoot = e.SSRP_CENTRAL_GALLERY_ROOT
  if (e.SSRP_INBOX) o.inboxRoot = e.SSRP_INBOX
  if (e.SSRP_THEMES) o.themesFile = e.SSRP_THEMES
  return o
}

// dshHome 优先级：SSRP_DSH_HOME > DSH_HOME > homedir/.dsh。
function resolveDshHome(envOverride) {
  return envOverride || process.env.DSH_HOME || (os.homedir() + '/.dsh')
}

export function loadConfig(rowConfig = {}) {
  const rc = rowConfig || {}
  const cfg = { ...defaults, ...rc, ...envOverrides() }
  cfg.dshHome = resolveDshHome(rc.dshHome)
  return cfg
}
