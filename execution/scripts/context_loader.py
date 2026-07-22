#!/usr/bin/env python3
"""Load all context assets before development."""
import os, sys

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CTX = os.path.join(BASE, 'docs/context')

order = [
    ('Version', 'context_version.yaml'),
    ('Architecture', 'architecture/module_map.md'),
    ('Dependency', 'architecture/dependency.yaml'),
    ('Odoo Version', 'architecture/odoo_version.md'),
    ('Stock Rules', 'business/stock_rule.md'),
    ('Inventory Flow', 'business/inventory_flow.md'),
    ('Decisions', 'history/decision_note.md'),
    ('Bug Records', 'history/bug_record.md'),
    ('Forbidden Changes', 'constraints/forbidden_change.yaml'),
    ('Cognition Rules', 'cognition/cognition_rule.yaml'),
    ('Consistency Check', 'cognition/cognition_consistency_check.yaml'),
    ('Cognition Refresh', 'cognition/cognition_refresh.yaml'),
    ('Asset Map', 'cognition/cognition_asset_map.md'),
    ('Rules', 'governance/rules.yaml'),
    ('Risk Levels', 'governance/risk_level.yaml'),
    ('Human Loop', 'governance/human_loop.yaml'),
    ('Workflow Risk', 'governance/workflow_risk.yaml'),
    ('Pipeline Check', 'governance/pipeline_check.yaml'),
    ('Audit', 'governance/audit_spec.yaml'),
    ('Tool Governance', 'governance/tool_governance.yaml'),
    ('Bug Fix Workflow', 'governance/bug_fix_workflow.yaml'),
]

print()
print('===== Context Loader =====')
found = 0
for name, path in order:
    fp = os.path.join(CTX, path)
    if os.path.exists(fp):
        print(f'  [OK] {path}')
        found += 1
    else:
        print(f'  [MISS] {path}')

vp = os.path.join(CTX, 'context_version.yaml')
if os.path.exists(vp):
    for line in open(vp):
        if 'context_version:' in line:
            print(f'  Baseline: {line.strip()}')
            break

print(f'  Loaded: {found}/{len(order)}')
print('===== Load Complete =====')
sys.exit(0 if found > 0 else 1)
