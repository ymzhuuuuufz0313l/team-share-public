# -*- coding: utf-8 -*-
# qa_site.py — 站点级只读自检（一条命令跑完 2026-11-17 修复项的验收）
#
# 用法（站点根目录）：
#   python image/tools/qa_site.py            # 全跑
#   python image/tools/qa_site.py --leak     # 只跑泄露扫描
# 退出码 0 = 全 PASS。
import io
import os
import re
import subprocess
import sys

# 统一按 UTF-8 写 stdout/stderr：Windows 控制台默认 cp936 遇到「↔」之类会 UnicodeEncodeError，
# 让自检自己抛异常（t20 · R6 顺带修）。
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
GUIDE = os.path.dirname(os.path.dirname(BASE))
PREFIX = subprocess.check_output(["git", "rev-parse", "--show-prefix"],
                                 cwd=GUIDE).decode().strip()
PY = sys.executable or "python"

# 本检查器自身的 git 相对路径：它必然包含下方 LEAK/ALLOW 的正则字面量，
# 扫自己会永久报红（闸门自伤）。显式排除自身，而不是把判据放宽。
SELF = os.path.relpath(os.path.abspath(__file__), GUIDE).replace("\\", "/")

# 泄露判据：真实内部标识（用户/公司账号/服务器挂载点/主机名/工程绝对路径）
LEAK = re.compile(r"ymzhu@|\byzhao\b|/sim_dd|/project/[A-Z]|node053")
# 允许保留的 ymzhu 出现形态：AGENTS.md 强制要求的文件尾签名 + 公开 GitHub 句柄
ALLOW = re.compile(r"ymzhu 20\d\d-\d\d-\d\d|20\d\d-\d\d-\d\d ymzhu|ymzhuuuu")
# 显式「文档提及」白名单：逐 (文件, 该行必须包含的原文片段) 列出，不放水成整类。
# 仅用于规范文档里讲解签名格式本身（不是真实签名、也不是泄露）。
MENTION_ALLOW = [
    ("image/anim/MOTION_KIT.md", "`# ymzhu YYYY-MM-DD HH:MM`"),
]


def mention_allowed(f, line):
    return any(f == af and frag in line for af, frag in MENTION_ALLOW)


def run(cmd):
    p = subprocess.run(cmd, cwd=GUIDE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def tracked():
    out = subprocess.check_output(["git", "ls-files", "."], cwd=GUIDE).decode("utf-8").splitlines()
    return out


def qa_leak():
    files = tracked()
    leak_files = []
    ymzhu_files = []
    ymzhu_bad = []
    for f in files:
        if f == SELF or not os.path.exists(f):
            continue
        try:
            s = io.open(f, encoding="utf-8").read()
        except Exception:
            continue
        if LEAK.search(s):
            leak_files.append(f)
        if "ymzhu" in s:
            ymzhu_files.append(f)
            for ln, line in enumerate(s.splitlines(), 1):
                if "ymzhu" in line and not ALLOW.search(line) and not mention_allowed(f, line):
                    ymzhu_bad.append("%s:%d:%s" % (f, ln, line.strip()[:100]))
    ok = not leak_files and not ymzhu_bad
    print("PASS" if ok else "FAIL", "泄露扫描：内部标识命中 %d 文件；含 ymzhu 的文件 %d 个（其中非签名/非公开句柄形态 %d 行）"
          % (len(leak_files), len(ymzhu_files), len(ymzhu_bad)))
    for f in leak_files:
        print("    X 内部标识:", f)
    for b in ymzhu_bad[:10]:
        print("    X 疑似泄露:", b)
    return ok


def qa_power():
    rc, out = run([PY, os.path.join("image", "tools", "gen_descramble_power_table.py"), "--check"])
    ok = rc == 0
    print("PASS" if ok else "FAIL", "功耗数值单一事实源 ↔ 页面块一致")
    for line in out.strip().splitlines():
        print("    ", line)
    return ok


def qa_params():
    """R1/R2/R4/R5：业务参数单一事实源闸门（JSON ↔ 源报告 ↔ 页面块 三方一致）。
    JSON 一改 / 页面被手改 / 源 rpt 变动，任一漂移立即报 FAIL。"""
    ok = True
    for script in ("gen_svt_summary.py", "gen_power_0812.py", "gen_param_blocks.py"):
        rc, out = run([PY, os.path.join("image", "tools", script), "--check"])
        lines = [l for l in out.strip().splitlines() if l.strip()]
        tail = lines[-1] if lines else "no output"
        good = rc == 0
        ok = ok and good
        print("PASS" if good else "FAIL", "参数单一事实源 %s：%s" % (script, tail[:160]))
    return ok


def qa_archive():
    rc, out = run([PY, os.path.join("image", "tools", "archive_history.py"), "--check"])
    txt = out.strip()
    m = re.search(r"缺失快照 (\d+) 个", txt)
    ok = rc == 0 and m and int(m.group(1)) == 0
    print("PASS" if ok else "FAIL", "归档快照完整：" + (txt.splitlines()[0] if txt else ""))
    return bool(ok)


def qa_kit():
    rc, out = run([PY, os.path.join("image", "tools", "validate_kit_v4.py")])
    ok = rc == 0
    tail = [l for l in out.strip().splitlines() if l.startswith("----")]
    print("PASS" if ok else "FAIL", "Kit v4 校验：" + (tail[0] if tail else "no output"))
    return ok


def qa_cache_bust():
    bad = []
    n = 0
    for f in tracked():
        if not f.endswith(".html"):
            continue
        s = io.open(f, encoding="utf-8").read()
        for m in re.finditer(r"(?:src=\"|!\[[^\]]*\]\()([^\")]*image/anim/[^\")]+\.svg)([^\")\s]*)", s):
            n += 1
            if "?v=" not in (m.group(2) or ""):
                bad.append("%s: %s" % (f, m.group(1)))
    ok = not bad
    print("PASS" if ok else "FAIL", "anim 图引用缓存打击：%d 处引用，缺 ?v= %d 处" % (n, len(bad)))
    for b in bad:
        print("    X", b)
    return ok


def main():
    only = [a for a in sys.argv[1:] if a.startswith("--")]
    checks = [("leak", qa_leak), ("power", qa_power), ("params", qa_params),
              ("archive", qa_archive), ("kit", qa_kit), ("cache", qa_cache_bust)]
    results = []
    for name, fn in checks:
        if only and ("--" + name) not in only and "--all" not in only:
            continue
        results.append((name, fn()))
    print("---- 合计 %d 项，FAIL %d 项" % (len(results), sum(1 for _, ok in results if not ok)))
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())

# ymzhu 2026-11-17 20:50
