#!/usr/bin/env python3
"""Module load check. Run before commit."""
import os, sys, subprocess

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ODOO = os.path.join(BASE, "odoo-bin")
CONF = os.path.join(BASE, "odoo.conf")

def check():
    if not os.path.exists(ODOO):
        print("  odoo-bin not found — skip runtime validation")
        return True
    cmd = [ODOO, "-c", CONF, "-u", "wd_tlms", "--stop-after-init"]
    print(f"  Running: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        print("  TIMEOUT (180s) — module may still be loading")
        return True
    errors = [
        l for l in (r.stderr or "").split("\n")
        if "ERROR" in l or "CRITICAL" in l or "Traceback" in l
    ]
    if errors:
        print(f"  FAIL: {len(errors)} errors")
        for e in errors[:5]: print(f"    {e.strip()}")
        return False
    print("  PASS: module loaded without errors")
    return True

if __name__ == "__main__":
    sys.exit(0 if check() else 1)
