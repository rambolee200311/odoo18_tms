# INT-TMS-SPRINT52FIX-001 Execution Record

## 问题

- SD52-B-001：商务链 quote 创建的 order 无 transport.plan，`order.action_allocate()`
  报 `Allocation candidate is missing; plan.reserve must be completed first.`

## 修复

- `addons/wd_tlms/models/transport_order.py`：`action_allocate()` 在无 abstract plan 时，
  直接校验 request 快照并生成 `vehicle_allocation_snapshot`；plan-driven 仍要求
  plan.reserve 的 allocation_candidate。
- `addons/wd_tlms/__manifest__.py`：版本 1.0.123 → 1.0.124。

## 验证

| Check | Result |
| :--- | :--- |
| py_compile | PASS |
| 模块升级（button_immediate_upgrade） | PASS（18.0.1.0.123 → 18.0.1.0.124） |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0（仅有先前 XML-RPC 测试的 marshal 错误日志，非升级错误） |
| Order 2638 action_allocate | PASS，生成 vehicle_allocation_snapshot |
| Order 2638 全链路 | closed |
| Request 3781 | completed |
| Event Ledger | 12 条全部命中字典 |
| 8089 端口 | 已释放 |

## 遗留

- SD52-B-002：商务链 order 缺少 carrier_cost fee line，当时为 open；
  已由 INT-TMS-SPRINT52FIX-002 修复并在 wd_tlms 1.0.125 复测通过。
