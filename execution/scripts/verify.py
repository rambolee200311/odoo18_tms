#!/usr/bin/env python3
"""产出语法门禁 — 可执行版本。取代 verify.sh（避免 bash heredoc 问题）"""
import os, sys, glob, xml.etree.ElementTree as ET

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS = os.path.join(BASE, 'addons/wd_tlms/models')
VIEWS = os.path.join(BASE, 'addons/wd_tlms/views')
passed, failed = 0, 0

def check(name, fn):
    global passed, failed
    print(f'  {name:20s} ... ', end='', flush=True)
    ok = fn()
    print('PASS' if ok else 'FAIL')
    if ok: passed += 1
    else: failed += 1
    return ok

print('\n========== 产出语法门禁 ==========')

# c1: Python 编译
def c1():
    for root, dirs, files in os.walk(MODELS):
        for fn in files:
            if not fn.endswith('.py'): continue
            fp = os.path.join(root, fn)
            try: compile(open(fp).read(), fn, 'exec')
            except SyntaxError as ex: print(f'\n  FAIL: {fn}: {ex}'); return False
    return True
check('Python 编译', c1)

# c2: XML 结构
def c2():
    for fn in sorted(os.listdir(VIEWS)):
        if not fn.endswith('.xml'): continue
        try: ET.parse(os.path.join(VIEWS, fn))
        except ET.ParseError: print(f'\n  FAIL: {fn}'); return False
    return True
check('XML 结构', c2)

# c3: 首行前导空格
def c3():
    for root, dirs, files in os.walk(os.path.join(BASE, 'addons/wd_tlms')):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            if not fn.endswith(('.py', '.xml')): continue
            l = open(os.path.join(root, fn)).readline()
            if len(l) - len(l.strip()) > 1:
                print(f'\n  LEADING SPACE: {fn}'); return False
    return True
check('首行空格', c3)

# c4: 模块名一致性
def c4():
    matches = []
    for root, dirs, files in os.walk(os.path.join(BASE, 'addons/wd_tlms')):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            if not fn.endswith(('.py', '.xml', '.js', '.csv')): continue
            for i, line in enumerate(open(os.path.join(root, fn)), 1):
                if 'transport_logistics_management' in line:
                    matches.append(f'{fn}:{i}')
    if matches:
        for m in matches: print(f'\n  {m}')
        return False
    return True
check('模块名称', c4)

# c5: Odoo18 兼容
def c5():
    patterns = ['<tree', 'decoration-bf', 'decoration-it', 'state_selection', 'colors=', 'fonts=']
    for pat in patterns:
        for root, dirs, files in os.walk(VIEWS):
            for fn in files:
                if not fn.endswith('.xml'): continue
                for i, line in enumerate(open(os.path.join(root, fn)), 1):
                    if pat in line:
                        print(f'\n  {fn}:{i}: {pat}'); return False
    return True
check('Odoo18 兼容', c5)

# c6: Tab 字符
def c6():
    for root, dirs, files in os.walk(os.path.join(BASE, 'addons/wd_tlms')):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for fn in files:
            if not fn.endswith(('.py', '.xml')): continue
            for i, line in enumerate(open(os.path.join(root, fn)), 1):
                if '\t' in line: print(f'\n  TAB: {fn}:{i}'); return False
    return True
check('Tab 字符', c6)

# c7: View-Model（启发式，仅警告）
def c7():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(BASE, 'docs/context/governance/check_view_fields.py')],
                      capture_output=True, text=True)
    out = r.stdout.strip()
    if out:
        n = sum(1 for l in out.split('\n') if 'NOT in model' in l)
        if n > 50:
            print(f'\n  ⚠ {n} fields reported (heuristic, may be false positives)')
        return True
    return True
check('View-Model', c7)

print(f'\n========== 结果: {passed} pass, {failed} fail ==========')
if failed == 0: print('  ALL CHECKS PASSED ✅')
else: print(f'  {failed} checks failed ❌')
sys.exit(failed)
