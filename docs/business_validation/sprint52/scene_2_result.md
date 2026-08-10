# Sprint52-B Scene 2 Result

> 契约：`INT-TMS-SPRINT52B-001`
> 状态：组合 1-8 已执行并通过；SD52-B-001 fixed（1.0.124），SD52-B-002 fixed（1.0.125）

## 组合 1：柜 + 外部车队 + T1 + 普通

| # | Check | Result |
| :--- | :--- | :--- |
| 1 | Commercial Flow 完整 | PASS（SD52-B-001 修复后） |
| 2 | State Transition 符合冻结状态机 | PASS |
| 3 | Event Ledger 先写账本再改状态 | PASS（12 条全部命中字典） |
| 4 | Request 双 Snapshot 存在 | PASS |
| 5 | Order Allocation Snapshot 存在 | PASS（1.0.124 后生成） |
| 6 | Fee Line 金额一致 | PASS（fix2 复测 order 2646：customer_charge 480 + carrier_cost 380） |
| 7 | Business Gap 已登记 | PASS（SD52-B-001 fixed，SD52-B-002 fixed） |

### 执行数据

| 对象 | ID / Name | 状态 |
| :--- | :--- | :--- |
| Request | 3781 / TLM-REQ-2026-08-4774 | completed（partial fulfillment） |
| Inquiry | 1071 | accepted |
| Quote | 814 / 380 + margin 100 = 480 | accepted |
| Order | 2638 / TLM-ORD-2026-08-5978 | closed |
| Event Ledger | 12 条 | 全部命中字典 |
| Fee Line | 首轮 244 / customer_charge / 480 | fix2 复测 order 2646 含双向行 |

### 缺口摘要

- `SD52-B-001`：已按 INT-TMS-SPRINT52FIX-001 修复，wd_tlms 1.0.124
  无 plan 时直接校验 request 快照并生成 allocation snapshot，验证通过。
- `SD52-B-002`：已按 INT-TMS-SPRINT52FIX-002 修复，wd_tlms 1.0.125；
  quote 创建时同时生成 customer_charge + carrier_cost，order 复制双向 fee line。

## 组合 2-8：批量验证结果

| 组合 | Request | Inquiry | Quote | Order | Ledger | Request State | Order State | Allocation Snapshot |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2 柜+自有+普通+普通 | 3782 | 1072 | 815 | 2639 | 15 | completed | closed | True |
| 3 托+外部+普通+普通 | 3783 | 1073 | 816 | 2640 | 15 | completed | closed | True |
| 4 托+自有+T1+普通 | 3784 | 1074 | 817 | 2641 | 15 | completed | closed | True |
| 5 件+外部+普通+普通 | 3785 | 1075 | 818 | 2642 | 15 | completed | closed | True |
| 6 件+自有+普通+普通 | 3786 | 1076 | 819 | 2643 | 15 | completed | closed | True |
| 7 柜+外部+普通+危品 | 3787 | 1077 | 820 | 2644 | 15 | completed | closed | True |
| 8 托+自有+T1+危品 | 3788 | 1078 | 821 | 2645 | 15 | completed | closed | True |

组合 2-8 均完成 request → inquiry → quote → order → allocate → in_transit → delivered → closed，
`vehicle_allocation_snapshot` 均存在；SD52-B-001 修复对商务链全部组合生效。

## SD52-B-002 修复复测（组合 1-8，wd_tlms 1.0.125）

修复后重新创建 8 条 request 并跑完整商务链，数据已提交数据库。

| 组合 | Request | Inquiry | Quote | Order | Ledger | Request State | Order State | Quote Fee（应收/应付） | Order Fee（应收/应付） | Allocation Snapshot |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 柜+外部+T1+普通 | 3789 | 1079 | 822 | 2646 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 2 柜+自有+普通+普通 | 3790 | 1080 | 823 | 2647 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 3 托+外部+普通+普通 | 3791 | 1081 | 824 | 2648 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 4 托+自有+T1+普通 | 3792 | 1082 | 825 | 2649 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 5 件+外部+普通+普通 | 3793 | 1083 | 826 | 2650 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 6 件+自有+普通+普通 | 3794 | 1084 | 827 | 2651 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 7 柜+外部+普通+危品 | 3795 | 1085 | 828 | 2652 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |
| 8 托+自有+T1+危品 | 3796 | 1086 | 829 | 2653 | 15 | completed | closed | 480 / 380 | 480 / 380 | True |

费用行为：
- quote 创建时 `customer_charge 380 + carrier_cost 380` 双行生成；
- 客户价加 margin 到 480 后，quote `customer_charge 480`、`carrier_cost 380`；
- order 从 quote 复制后 `customer_charge 480 + carrier_cost 380`。

| Check | Result |
| :--- | :--- |
| py_compile | PASS |
| XML-RPC button_immediate_upgrade | 18.0.1.0.124 → 18.0.1.0.125 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0（仅 worlddepot 既有 DeprecationWarning） |
| Quote 双向 fee line（8/8） | PASS |
| Order 双向 fee line（8/8） | PASS |
| Order closed / Request completed（8/8） | PASS |
| Event Ledger 15 条全部命中字典 | PASS |
| vehicle_allocation_snapshot（8/8） | PASS |
| 新会话二次核验 | PASS（8/8） |

## 执行信息

| 项 | 值 |
| :--- | :--- |
| Executor | Codex |
| Date（首轮） | 2026-08-07 |
| Date（fix2 复测） | 2026-08-10 |
| Environment | Odoo 18 dev |
| Module Version | 1.0.124 → 1.0.125 |
