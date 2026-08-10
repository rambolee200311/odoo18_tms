# INT-TMS-SPRINT52FIX-002 Execution Record

## 问题

- SD52-B-002：商务链 quote 创建的 order 只有 customer_charge 应收行，
  缺少 carrier_cost 应付行（380），应付费用无法从 order 费用行直接核对。

## 修复

- `addons/wd_tlms/models/transport_inquiry.py`：`action_create_quote()`
  创建 quote 时同时生成 `customer_charge` 与 `carrier_cost` 两条 fee line；
  客户价加 margin 后仅更新 customer_charge，carrier_cost 保持承运商报价。
- `addons/wd_tlms/__manifest__.py`：版本 1.0.124 → 1.0.125。
- order 复制 quote fee line 的既有逻辑保持不变，应收/应付双行随 order 生成。

## 验证

| Check | Result |
| :--- | :--- |
| py_compile | PASS |
| 模块升级（button_immediate_upgrade） | PASS（18.0.1.0.124 → 18.0.1.0.125） |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0（仅 worlddepot 既有 DeprecationWarning） |
| Quote 双向 fee line（组合 1-8） | PASS（创建 380/380；加 margin 后 480/380） |
| Order 双向 fee line（组合 1-8） | PASS（customer_charge 480 + carrier_cost 380） |
| 组合 1-8 全链路 | PASS（order closed，request completed） |
| Event Ledger | 15 条/组合，全部命中事件字典 |
| vehicle_allocation_snapshot | 存在（8/8） |
| 新会话二次核验 | PASS（8/8） |
| 8089 端口 | 已释放 |

## 数据

| 组合 | Request | Inquiry | Quote | Order |
| :--- | :--- | :--- | :--- | :--- |
| 1 柜+外部+T1+普通 | 3789 | 1079 | 822 | 2646 |
| 2 柜+自有+普通+普通 | 3790 | 1080 | 823 | 2647 |
| 3 托+外部+普通+普通 | 3791 | 1081 | 824 | 2648 |
| 4 托+自有+T1+普通 | 3792 | 1082 | 825 | 2649 |
| 5 件+外部+普通+普通 | 3793 | 1083 | 826 | 2650 |
| 6 件+自有+普通+普通 | 3794 | 1084 | 827 | 2651 |
| 7 柜+外部+普通+危品 | 3795 | 1085 | 828 | 2652 |
| 8 托+自有+T1+危品 | 3796 | 1086 | 829 | 2653 |

## 遗留

- Sprint52-B 阻塞问题为 0；SD52-B-001、SD52-B-002 均已 fixed。
- 下一子意图：Sprint52-C。
