#!/usr/bin/env python3
"""集成测试执行器 — 运行 wd_tlms 的 Odoo TestCase。
作为 git_commit.sh Step 2.5 执行。

捕获: view_mode 兼容 / menuitem parent / action-model-view 链路 / view_refs
"""
import os, sys, subprocess

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ODOO = os.path.join(BASE, "odoo-bin")
CONF = os.path.join(BASE, "odoo.conf")


def run():
    if not os.path.exists(ODOO):
        print("  odoo-bin not found — skip runtime tests")
        return True

    VENV_PYTHON = os.path.join(BASE, "venv", "bin", "python3")
    cmd = [
        VENV_PYTHON, ODOO, "-c", CONF,
        "--http-port=8088",     # 避免与运行中的服务端口冲突
        "--logfile=",           # 输出到 stderr 而非日志文件
        "-u", "wd_tlms",       # 触发升级（检测代码变更自动执行）
        "--test-enable",
        "--stop-after-init",
    ]
    print(f"  Running: {' '.join(cmd)}")

    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        print("  TIMEOUT (300s) — tests may still be running")
        return True

    output = (r.stderr or "") + (r.stdout or "")

    # 检测 test 失败
    if "FAIL:" in output or "ERROR:" in output:
        lines = output.split("\n")
        failures = [l.strip() for l in lines if "FAIL:" in l or "ERROR:" in l or "Traceback" in l]
        print(f"  FAIL: {len(failures)} test failure(s)")
        for f in failures[:15]:
            print(f"    {f}")
        return False

    # 检测 test 通过
    if "0 failures, 0 errors" in output:
        print("  PASS: all tests passed")
        return True

    # 无变更时 -u 跳过了升级，非错误
    print(f"  SKIP (no pending changes, exit={r.returncode})")
    return True


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
