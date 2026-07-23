#!/usr/bin/env python3
"""
Context Runtime v3 — AI Agent 开发前置认知加载 + 基线验证 + 风险注入

职责:
  1. 加载上下文资产（目录扫描 + 内容摘要）
  2. 基线校验（intent binding vs context_version）
  3. 风险阻断（test_lessons LEVEL3 规则告警）
  4. 结构化输出（human / --json）

退出码:
  0 = READY         一切正常，可以开发
  1 = ASSET_MISSING 关键资产缺失
  2 = RISK_BLOCKED  存在未确认的 LEVEL3 风险
  3 = BASELINE_MISMATCH 上下文版本与契约要求的基线不匹配
"""
import os, sys, glob, json, re
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CTX = os.path.join(BASE, 'docs/context')
PATH_TEST_LESSONS = os.path.join(CTX, 'governance', 'test_lessons.yaml')
PATH_DECISION_NOTE = os.path.join(CTX, 'history', 'decision_note.md')

EXIT_READY = 0
EXIT_ASSET_MISSING = 1
EXIT_RISK_BLOCKED = 2
EXIT_BASELINE_MISMATCH = 3

# -----------------------------------------------------------
# 加载画像 — 按 Sprint 类型决定哪些资产做深度扫描
# -----------------------------------------------------------
PROFILE_ASSETS = {
    'development': {
        'deep': ['architecture', 'business', 'constraints/forbidden_change.yaml'],
        'label': 'New Feature Development',
    },
    'testing': {
        'deep': ['history/bug_record.md', 'governance/test_lessons.yaml', 'validation'],
        'label': 'Testing',
    },
    'bugfix': {
        'deep': ['history/bug_record.md', 'constraints/forbidden_change.yaml',
                 'governance/test_lessons.yaml'],
        'label': 'Bug Fix',
    },
    'infrastructure': {
        'deep': ['governance', 'architecture/dependency.yaml'],
        'label': 'Infrastructure',
    },
    'full': {
        'deep': None,
        'label': 'Full Audit',
    },
}


# -----------------------------------------------------------
# 通用工具
# -----------------------------------------------------------
def _read(path):
    """安全读取文件，补全 encoding + 异常捕获"""
    if not os.path.exists(path):
        return ''
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except (UnicodeDecodeError, PermissionError, OSError) as err:
        return f'[READ_ERROR]: {repr(err)}'


def _yaml_val(text, key, default=''):
    """从 YAML 文本中提取指定 key 的值，支持多行（纯文本解析）"""
    import re as _re
    pat = _re.compile(rf'^{_re.escape(key)}\s*:\s*(["\']?)(.*?)\1?$', _re.MULTILINE | _re.DOTALL)
    m = pat.search(text)
    if m:
        return m.group(2).strip().strip('"').strip("'")
    return default


# -----------------------------------------------------------
# 版本与意图
# -----------------------------------------------------------
def read_version():
    raw = _read(os.path.join(CTX, 'context_version.yaml'))
    return _yaml_val(raw, 'context_version', 'UNKNOWN')


def read_intent():
    """返回 (filename, sprint_version, bind_context_version)"""
    files = glob.glob(os.path.join(CTX, 'intent', '*[Ss]print*.yaml'))
    files = [f for f in files if 'template' not in f]
    if not files:
        return ('NONE', '', '')
    def sprint_num(fp):
        m = re.search(r'sprint(\d+)', os.path.basename(fp))
        return int(m.group(1)) if m else 0
    best = max(files, key=sprint_num)
    name = os.path.basename(best)
    raw = _read(best)
    sv = _yaml_val(raw, 'sprint_version', '')
    bv = _yaml_val(raw, 'bind_context_version', '')
    pf = _yaml_val(raw, 'context_load_profile', 'full')
    return (name, sv, bv, pf)


# -----------------------------------------------------------
# 资产扫描
# -----------------------------------------------------------
def scan_dir(subdir):
    path = os.path.join(CTX, subdir)
    if not os.path.isdir(path):
        return []
    items = []
    for f in sorted(os.listdir(path)):
        if f.startswith('.') or f == '__pycache__':
            continue
        items.append(f)
    return items


def check(name, subdir):
    items = scan_dir(subdir)
    ok = len(items)
    status = 'PASS' if ok > 0 else 'FAIL'
    return {'name': name, 'subdir': subdir, 'count': ok, 'status': status, 'items': items}


# -----------------------------------------------------------
# 内容摘要
# -----------------------------------------------------------
def summarize_file(fullpath, filename):
    """读取单个文件，返回一行摘要"""
    raw = _read(fullpath)
    if not raw:
        return f'{filename}: EMPTY'
    lines = raw.split('\n')
    if filename.endswith(('.yaml', '.yml')):
        entries = sum(1 for l in lines if ':' in l and not l.strip().startswith('#') and l[0] != ' ')
        return f'{filename}: {entries} entries'
    elif filename.endswith('.md'):
        headers = sum(1 for l in lines if l.startswith('#'))
        bullets = sum(1 for l in lines if l.strip().startswith('-'))
        return f'{filename}: {headers} headings, {bullets} items'
    else:
        return f'{filename}: {len(lines)} lines'


def _is_deep(subdir, fname, deep_list):
    if deep_list is None:
        return True
    rel = os.path.join(subdir, fname)
    for pattern in deep_list:
        if rel == pattern or rel.startswith(pattern):
            return True
    return False


def summarize_domain(name, subdir, items, deep_list):
    summary = {'name': name, 'subdir': subdir, 'count': len(items), 'files': []}
    for fname in items:
        fpath = os.path.join(CTX, subdir, fname)
        if _is_deep(subdir, fname, deep_list):
            line = summarize_file(fpath, fname) + ' [Deep]'
        else:
            raw = _read(fpath)
            lc = raw.count('\n') + 1 if raw else 0
            line = f'{fname}: {lc} lines [Light]'
        summary['files'].append(line)
    return summary


# -----------------------------------------------------------
# 风险加载
# -----------------------------------------------------------
def load_risks():
    """从 test_lessons.yaml 加载风险规则"""
    fp = PATH_TEST_LESSONS
    if not os.path.exists(fp):
        return []
    raw = _read(fp)
    blocks = raw.split('\n  - id:')
    rules = []
    for block in blocks[1:]:
        rid = block.split('"')[1] if block.count('"') >= 2 else '?'
        severity = ''
        problem = ''
        for line in block.split('\n'):
            if 'severity: "' in line:
                severity = line.split('"')[1]
            if 'problem: "' in line:
                problem = line.split('"')[1]
        rules.append({'id': rid, 'severity': severity, 'problem': problem})
    return rules


# -----------------------------------------------------------
# 报告构建
# -----------------------------------------------------------
def build_report(version, intent_info, domains, risks, summaries, all_pass):
    iv_name, iv_sprint, iv_bind, iv_profile = intent_info
    baseline_match = version == iv_bind if iv_bind else True
    high_risks = [r for r in risks if r['severity'] == 'LEVEL3']
    medium_risks = [r for r in risks if r['severity'] == 'LEVEL2']

    return {
        'version': version,
        'intent': {
            'file': iv_name,
            'sprint': iv_sprint,
            'bind_version': iv_bind,
        },
        'baseline_check': {
            'context_version': version,
            'intent_bind': iv_bind,
            'match': baseline_match,
        },
        'domains': domains,
        'all_pass': all_pass,
        'risks': {
            'total': len(risks),
            'level3': high_risks,
            'level2': medium_risks,
        },
        'summaries': summaries,
        'ready': all_pass and baseline_match and len(high_risks) == 0,
    }


# -----------------------------------------------------------
# 显示
# -----------------------------------------------------------
def display_human(report):
    print()
    print('=' * 50)
    print('  Context Runtime v3 - Pre-Development Gate')
    print('=' * 50)
    print(f'  Run Timestamp:    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'  Context Version:  {report["version"]}')

    iv = report['intent']
    if iv['file'] != 'NONE':
        pf = report.get('profile', 'full')
        print(f'  Load Profile:     {PROFILE_ASSETS.get(pf, PROFILE_ASSETS["full"])["label"]}')
        if iv['sprint']:
            print(f'  Sprint:           {iv["sprint"]}')
        print(f'  Decision Note:    {PATH_DECISION_NOTE}')

    # Baseline
    bc = report['baseline_check']
    if bc['intent_bind']:
        ok = 'PASS' if bc['match'] else 'FAIL'
        icon = '✅' if bc['match'] else '❌'
        print(f'  Baseline Check:   [{ok}]  {icon}')
        if not bc['match']:
            print(f'    context_version={bc["context_version"]} vs intent bind={bc["intent_bind"]}')
    else:
        print(f'  Baseline Check:   [SKIP]  (intent has no baseline)')

    print()

    # Domains
    all_pass = True
    for d in report['domains']:
        ok = 'PASS' if d['status'] == 'PASS' else 'FAIL'
        print(f'  {d["name"]:15s} [{ok}]  {d["count"]} file(s)')
        for fl in d.get('files', []):
            print(f'    {fl}')
        if d['status'] != 'PASS':
            print(f'    ⚠ WARNING: Directory [{d["subdir"]}] has zero asset files')
            all_pass = False
    report['all_pass'] = all_pass

    print()

    # Risks
    risks = report['risks']
    if risks['level3']:
        print(f'  🔴 HIGH RISK: {len(risks["level3"])} unresolved LEVEL3 rule(s)')
        for r in risks['level3']:
            print(f'     [{r["severity"]}] {r.get("id","?")}: {r.get("problem","")[:80]}')
        print('  ⚠  Review required before development')
    elif risks['level2']:
        print(f'  🟡 MEDIUM RISK: {len(risks["level2"])} LEVEL2 rule(s) to review')
        for r in risks['level2'][:3]:
            print(f'     [{r["severity"]}] {r.get("id","?")}: {r.get("problem","")[:60]}')
        if len(risks['level2']) > 3:
            print(f'     ... and {len(risks["level2"]) - 3} more')
    else:
        print('  Risk Review:      No unresolved risks')

    print()



    # Status
    ready = report['ready'] and all_pass
    if ready:
        print('  Status: READY ✅  Development can proceed')
    else:
        blockers = []
        if not all_pass:
            blockers.append('asset missing')
        if not report['baseline_check'].get('match', True):
            blockers.append('baseline mismatch')
        if risks['level3']:
            blockers.append('LEVEL3 risks unresolved')
        print(f'  Status: BLOCKED ❌  ({", ".join(blockers)})')
    print('=' * 50)


def display_json(report):
    print(json.dumps(report, ensure_ascii=False, indent=2))


# -----------------------------------------------------------
# 主流程
# -----------------------------------------------------------
def main():
    json_mode = '--json' in sys.argv

    version = read_version()
    intent_info = read_intent()
    iv_name, iv_sprint, iv_bind, iv_profile = intent_info

    # ── 1. 基线校验 ──
    if iv_bind and version != iv_bind:
        mismatch = {
            'version': version,
            'intent': {'file': iv_name, 'sprint': iv_sprint, 'bind_version': iv_bind},
            'baseline_check': {'context_version': version, 'intent_bind': iv_bind, 'match': False},
            'status': 'BLOCKED', 'reason': 'baseline_mismatch', 'ready': False,
        }
        if json_mode:
            print(json.dumps(mismatch, ensure_ascii=False, indent=2))
        else:
            print()
            print('=' * 50)
            print('  ❌ BASELINE MISMATCH - Development BLOCKED')
            print('=' * 50)
            print(f'  context_version.yaml:  {version}')
            print(f'  intent requires:       {iv_bind}')
            print(f'  Intent file:           {iv_name}')
            print()
            print('  Run: context_loader.py --json for machine-readable output')
            print('=' * 50)
        sys.exit(EXIT_BASELINE_MISMATCH)

    # ── 2. 资产扫描 ──
    domain_configs = [
        ('Architecture', 'architecture'),
        ('Business', 'business'),
        ('History', 'history'),
        ('Constraints', 'constraints'),
        ('Cognition', 'cognition'),
        ('Governance', 'governance'),
        ('Validation', 'validation'),
    ]

    domains = []
    all_pass = True
    for name, subdir in domain_configs:
        result = check(name, subdir)
        domains.append(result)
        if result['status'] != 'PASS':
            all_pass = False

    if not all_pass:
        # Print report anyway, let user see what's missing
        pass  # Continue to show report, don't exit yet

    # ── 3. 风险加载 ──
    risks = load_risks()

    # ── 4. 内容摘要 ──
    summaries = []
    for name, subdir in domain_configs:
        items = scan_dir(subdir)
        profile_dict = PROFILE_ASSETS.get(iv_profile, PROFILE_ASSETS['full'])
        deep_list = profile_dict['deep']
        summary = summarize_domain(name, subdir, items, deep_list)
        summaries.append(summary)

    # ── 5. 构建 + 显示 ──
    report = build_report(version, intent_info, domains, risks, summaries, all_pass)

    if json_mode:
        # Report already has domains in it via build_report, but needs all_pass
        report['all_pass'] = all_pass
        display_json(report)
    else:
        display_human(report)

    # ── 6. 退出码 ──
    final_code = EXIT_READY
    if not report['ready']:
        if not report['all_pass']:
            final_code = EXIT_ASSET_MISSING
        elif len(report['risks']['level3']) > 0:
            final_code = EXIT_RISK_BLOCKED
    sys.exit(final_code)


if __name__ == '__main__':
    main()
