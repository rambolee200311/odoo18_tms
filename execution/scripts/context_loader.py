#!/usr/bin/env python3
"""Context Loader v2 — 目录扫描模式，新增文件自动识别"""
import os, sys, glob

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CTX = os.path.join(BASE, 'docs/context')


def read_version():
    fp = os.path.join(CTX, 'context_version.yaml')
    if not os.path.exists(fp):
        return 'UNKNOWN'
    for line in open(fp):
        if 'context_version:' in line:
            return line.split(':', 1)[1].strip()
    return 'UNKNOWN'


def read_intent():
    files = sorted(glob.glob(os.path.join(CTX, 'intent', 'sprint*.yaml')))
    if not files:
        return 'NONE'
    last = files[-1]
    name = os.path.basename(last)
    for line in open(last):
        if 'sprint_version:' in line:
            ver = line.split(':', 1)[1].strip()
            return f'{name}: {ver}'
    return name


def scan_dir(subdir):
    """扫描目录返回非隐藏条目列表，新增文件自动识别"""
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
    print(f'  {name:15s} [{status}]  {ok} file(s)')
    return ok > 0


def load_lessons():
    fp = os.path.join(CTX, 'governance', 'test_lessons.yaml')
    if not os.path.exists(fp):
        print('  Test Lessons:  NOT FOUND')
        return
    with open(fp) as f:
        text = f.read()
    blocks = text.split('\n  - id:')
    rules = []
    for block in blocks[1:]:
        rid = block.split('"')[1] if block.count('"') >= 2 else '?'
        problem = ''
        severity = ''
        for line in block.split('\n'):
            if 'problem: "' in line:
                problem = line.split('"')[1]
            if 'severity: "' in line:
                severity = line.split('"')[1]
        if severity in ('LEVEL2', 'LEVEL3'):
            rules.append((rid, problem, severity))
    if rules:
        print(f'  \u26a0  Test Lessons: {len(rules)} rules to review')
        for rid, problem, severity in rules:
            print(f'     [{severity}] {rid}: {problem[:80]}')
    else:
        print('  Test Lessons:  0 rules')


def main():
    version = read_version()
    intent = read_intent()

    print()
    print('=' * 50)
    print('  Context Loader - Cognitive Snapshot')
    print('=' * 50)
    print(f'  Project:    Odoo18 TMS')
    print(f'  Version:    {version}')
    print(f'  Intent:     {intent}')
    print()

    domain_dirs = [
        ('Architecture', 'architecture'),
        ('Business', 'business'),
        ('History', 'history'),
        ('Constraints', 'constraints'),
        ('Cognition', 'cognition'),
        ('Governance', 'governance'),
        ('Validation', 'validation'),
    ]

    all_pass = True
    for name, subdir in domain_dirs:
        if not check(name, subdir):
            all_pass = False

    print()
    load_lessons()
    print()
    print(f'  Engine:     4 scripts in execution/scripts/')
    print(f'  Validation: odoo_check.py + test_runner.py')
    print()
    if all_pass:
        print('  Ready for Development: YES')
    else:
        print('  Ready for Development: NO (some domains empty)')
    print('=' * 50)
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
