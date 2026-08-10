# Sprint52-C Scene 3 Result

> 契约：`INT-TMS-SPRINT52C-001`
> 状态：组合 1-8 全部验证完成

## 组合 1：柜 + 外部车队 + T1 + 普通

| # | Check | Result |
| :--- | :--- | :--- |
| 1 | Commercial Flow 完整 | PASS |
| 2 | State Transition 符合冻结状态机 | PASS |
| 3 | Event Ledger 先写账本再改状态 | PASS（15 条全部命中字典） |
| 4 | Request 双 Snapshot 存在 | PASS |
| 5 | Order Allocation Snapshot 存在 | PASS |
| 6 | Fee Line 金额一致 | PASS（customer_charge 480 + carrier_cost 380） |
| 7 | Business Gap 已登记 | PASS（未发现缺口） |

### 执行数据

| 对象 | ID / Name | 状态 |
| :--- | :--- | :--- |
| Request | 3797 / TLM-REQ-2026-08-4790 | completed |
| Inquiry | 1087 | accepted |
| Quote | 830 / 380 + margin 100 = 480 | accepted |
| Order | 2654 / TLM-ORD-2026-08-5986 | closed |
| Event Ledger | 15 条 | 全部命中字典 |
| Fee Line | customer_charge 480 + carrier_cost 380 | 双向行存在 |

## 组合 2-8：批量验证结果

| 组合 | Request | Inquiry | Quote | Order | Ledger | Request State | Order State | Allocation Snapshot |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2 柜+自有+普通+普通 | 3798 | 1088 | 831 | 2655 | 15 | completed | closed | True |
| 3 托+外部+普通+普通 | 3799 | 1089 | 832 | 2656 | 15 | completed | closed | True |
| 4 托+自有+T1+普通 | 3800 | 1090 | 833 | 2657 | 15 | completed | closed | True |
| 5 件+外部+普通+普通 | 3801 | 1091 | 834 | 2658 | 15 | completed | closed | True |
| 6 件+自有+普通+普通 | 3802 | 1092 | 835 | 2659 | 15 | completed | closed | True |
| 7 柜+外部+普通+危品 | 3803 | 1093 | 836 | 2660 | 15 | completed | closed | True |
| 8 托+自有+T1+危品 | 3804 | 1094 | 837 | 2661 | 15 | completed | closed | True |

8 个组合全部完成 request → inquiry → quote → order → allocate → in_transit → delivered → closed，
`vehicle_allocation_snapshot` 均存在；quote 与 order 均含 customer_charge 480 + carrier_cost 380。

## Final Result

| 项 | 值 |
| :--- | :--- |
| Manual | PASS |
| 数据验证 | PASS（8/8 组合） |
| Executor | Codex |
| Date | 2026-08-10 |
| 阻塞问题 | 无 |
| 开放观察项 | 无 |

## 执行信息

| 项 | 值 |
| :--- | :--- |
| Executor | Codex |
| Date | 2026-08-10 |
| Environment | Odoo 18 dev |
| Module Version | 1.0.125 |
