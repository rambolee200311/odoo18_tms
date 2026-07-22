#!/usr/bin/env python3
"""Check odoo module loading."""
import os, sys, subprocess

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ODOO = os.path.join(BASE, 'odoo-bin')
CONF = os.path.join(BASE, 'odoo.conf')

def check():
    if not os.path.exists(ODOO):
        print(f'odoo-bin not found')
        return False
    cmd = [ODOO, '-c', CONF, '-u', 'wd_tlms', '--stop-after-init']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    errors = [l for l in r.stderr.split('\n') if 'ERROR' in l or 'CRITICAL' in l or 'Traceback' in l]
    if errors:
        print(f'{len(errors)} errors:')
        for e in errors[:5]: print(f'  {e}')
        return False
    print('Module OK')
    return True

if __name__ == '__main__':
    sys.exit(0 if check() else 1)
