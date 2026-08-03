---
name: odo-validate-loop
description: >
  Use when changing or fixing custom Odoo modules (e.g. wd_tlms) in this
  workspace. Enforces the Odoo-specific verification loop: syntax/XML checks,
  running-server XML-RPC upgrade, log inspection, targeted DB checks, port
  cleanup, and a closure report.
---

# Odoo 验证闭环

## When to use

Trigger automatically when the task involves modifying Odoo custom module code, views, or data, or when the user asks "模块升级验证", "验证完了吗", "升级了吗", or "输出工作报告".

## Hard rules

- Never modify official `odoo/` code.
- Never debug through caches / .pyc files; inspect custom module code first.
- Never rely only on `-u wd_tlms --stop-after-init`; use XML-RPC `button_immediate_upgrade` on a running server (UI-equivalent).
- Odoo shell writes must call `env.cr.commit()` and be re-verified in a new session.
- Do not hardcode credentials in the skill; use the workspace's configured dev credentials or environment-managed secrets.

## Workflow

1. Fix the custom module code; keep the change scoped.
2. Validate syntax and XML:
   - `venv/bin/python -m py_compile <changed .py files>`
   - parse changed XML with lxml
3. If the change touches module metadata, bump `__manifest__.py` version.
4. Start or reuse a persistent server on the workspace's standard dev port; clear the prior module log before the run.
5. Upgrade via XML-RPC on the running server (UI-equivalent): authenticate with the workspace's configured dev credentials, locate the module, and call `button_immediate_upgrade`.
6. Read the whole log top to bottom; fail on ERROR / CRITICAL / TRACEBACK / ParseError / AssertionError.
7. Verify data/behavior with odoo shell or targeted test data; commit any shell writes.
8. Free the dev port if this session started the server, and confirm no listener remains.
9. Update business validation docs and `result_summary.md` only if this change owns those artifacts.
10. If repo workflow requires publication, commit the changes; push only when explicitly requested or when the session policy requires it.
11. Output a work report: changes, version, verification result, docs updated, git hash if any, port status, remaining pending items.

## Common traps

- After writing "我现在执行", the next message must be a tool call.
- XML-RPC upgrade returns an act_url success; always re-read module version afterwards.
- Data backfill blocked by a NOT NULL constraint: upgrade the module first to apply the schema change, then backfill.
- This skill complements `task-completion-discipline`; use both for Odoo change turns.

## Learnings

- `button_immediate_upgrade` on a running server is the authoritative verification path for Odoo UI behavior; `-u --stop-after-init` is not sufficient because it can miss UI-equivalent upgrade failures.
- When using Odoo shell to modify data, `env.cr.commit()` is required before re-verifying in a fresh session; otherwise the work can roll back silently.
- Keep verification instructions free of hardcoded credentials so the skill stays safe and reusable across sessions.
