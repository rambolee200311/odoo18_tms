#!/usr/bin/env python3
import os, sys, subprocess

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
VERIFY = os.path.join(BASE, 'execution/scripts/verify.py')

def main():
    r = subprocess.run([sys.executable, VERIFY])
    if r.returncode != 0:
        print()
        print('Gate not passed. Fix errors and retry.')
        sys.exit(1)
    print()
    print('Enter sprint description:')
    msg = sys.stdin.readline().strip()
    if not msg:
        print('Empty description rejected')
        sys.exit(1)
    full = 'Sprint Iteration: ' + msg + '\n\n[AI Asset Update]\n1. Code\n2. Context\n3. Logs\n4. Scope compliance'
    os.chdir(BASE)
    for cmd in [['git','add','.'],['git','commit','-m',full],['git','push','origin','main']]:
        r = subprocess.run(cmd)
        if r.returncode != 0:
            print('Git failed:', cmd[0], cmd[1])
            sys.exit(1)
    print('Commit done.')

if __name__ == '__main__':
    main()
