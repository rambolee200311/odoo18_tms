#!/usr/bin/env python3
"""Context Loader — 认知加载 + 结构化快照输出"""
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

def check(name, paths):
    ok = 0
    for p in paths:
        if os.path.exists(os.path.join(CTX, p)):
            ok += 1
    status = 'PASS' if ok == len(paths) else 'FAIL'
    print(f'  {name:15s} [{status}]  {ok}/{len(paths)}')
    return ok == len(paths)

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

    domains = [
        ('Architecture', [
            'architecture/module_map.md',
            'architecture/dependency.yaml',
            'architecture/odoo_version.md',
        ]),
        ('Business', [
            'business/stock_rule.md',
            'business/inventory_flow.md',
        ]),
        ('History', [
            'history/decision_note.md',
            'history/bug_record.md',
            'history/sprint_log.md',
            'history/sprint_shturl',
        ]),
        ('Constraints', [
            'constraints/forbidden_change.yaml',
        ]),
        ('Cognition', [
            'cognition/cognition_rule.yaml',
            'cognition/cognition_consistency_check.yaml',
            'cognition/cognition_refresh.yaml',
            'cognition/cognition_asset_map.md',
        ]),
        ('Governance', [
            'governance/rules.yaml',
            'governance/risk_level.yaml',
            'governance/human_loop.yaml',
            'governance/workflow_risk.yaml',
            'governance/pipeline_check.yaml',
            'governance/audit_spec.yaml',
            'governance/tool_governance.yaml',
            'governance/bug_fix_workflow.yaml',
        ]),
    ]

    all_pass = True
    for name, paths in domains:
        if not check(name, paths):
            all_pass = False

    print()
    print(f'  Engine:     4 scripts in execution/scripts/')
    print(f'  Gate:       7 checks (verify.py)')
    print(f'  Validation: odoo_check.py')
    print()
    if all_pass:
        print('  Ready for Development: YES')
    else:
        print('  Ready for Development: NO (missing assets)')
    print('=' * 50)
    sys.exit(0 if all_pass else 1)

if __name__ == '__main__':
    main()
