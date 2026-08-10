# INT-TMS-SPRINT52C-001 Execution Record

## 验证范围

- 场景：S3 Warehouse → Customer（warehouse_to_customer）
- 链路：request → inquiry → quote → transport.order → delivery
- 数据：8 个代表组合（柜/托/件 × 自有/外部 × T1/普通 × 危品/普通）

## 执行

- 创建 8 条 request（scene=warehouse_to_customer，source_warehouse_id=SPN，
  destination=Customer），提交后冻结 matrix / vehicle_requirement snapshot。
- 每条 request 走 inquiry → quote → order → allocate → in_transit →
  delivered → closed 完整商务链；客户价 380 + margin 100 = 480，
  carrier_cost 保持 380。
- 数据写入后在新会话二次核验。

## 验证

| Check | Result |
| :--- | :--- |
| 组合 1-8 全链路 | PASS（order closed，request completed） |
| Quote 双向 fee line | PASS（创建 380/380；加 margin 后 480/380） |
| Order 双向 fee line | PASS（customer_charge 480 + carrier_cost 380） |
| Event Ledger | 15 条/组合，全部命中事件字典 |
| Request 双 Snapshot | frozen（8/8） |
| vehicle_allocation_snapshot | 存在（8/8） |
| 新会话二次核验 | PASS（8/8） |
| 业务缺口 | 0 |

## 数据

| 组合 | Request | Inquiry | Quote | Order |
| :--- | :--- | :--- | :--- | :--- |
| 1 柜+外部+T1+普通 | 3797 | 1087 | 830 | 2654 |
| 2 柜+自有+普通+普通 | 3798 | 1088 | 831 | 2655 |
| 3 托+外部+普通+普通 | 3799 | 1089 | 832 | 2656 |
| 4 托+自有+T1+普通 | 3800 | 1090 | 833 | 2657 |
| 5 件+外部+普通+普通 | 3801 | 1091 | 834 | 2658 |
| 6 件+自有+普通+普通 | 3802 | 1092 | 835 | 2659 |
| 7 柜+外部+普通+危品 | 3803 | 1093 | 836 | 2660 |
| 8 托+自有+T1+危品 | 3804 | 1094 | 837 | 2661 |

## Sprint52-Fix3 重跑（wd_tlms 1.0.126，2026-08-10）

按 `INT-TMS-SPRINT52FIX-003` 新商务链重新执行 8 组合：
request → Create Carrier Inquiry wizard → selected inquiry →
Create Customer Quote wizard → accepted quote → order → closed。

| 组合 | Request | Inquiry | Quote | Order |
| :--- | :--- | :--- | :--- | :--- |
| 1 柜+外部+T1+普通 | 3808 | 1098 | 841 | 2664 |
| 2 柜+自有+普通+普通 | 3809 | 1099 | 842 | 2665 |
| 3 托+外部+普通+普通 | 3810 | 1100 | 843 | 2666 |
| 4 托+自有+T1+普通 | 3811 | 1101 | 844 | 2667 |
| 5 件+外部+普通+普通 | 3812 | 1102 | 845 | 2668 |
| 6 件+自有+普通+普通 | 3813 | 1103 | 846 | 2669 |
| 7 柜+外部+普通+危品 | 3814 | 1104 | 847 | 2670 |
| 8 托+自有+T1+危品 | 3815 | 1105 | 848 | 2671 |

| Check | Result |
| :--- | :--- |
| 8/8 组合全链路 | PASS（order closed，request completed） |
| Inquiry 状态 | selected（8/8，INQUIRY_SELECTED） |
| Quote 状态 / communication | accepted / responded（8/8） |
| Quote/Order fee line | customer_charge 480 + carrier_cost 380（8/8） |
| Order 追溯链 | carrier_id/quote_id/inquiry_id 回填（8/8） |
| Event Ledger | 18 条/组合，全部命中字典 |
| vehicle_allocation_snapshot | 存在（8/8） |
| 新会话二次核验 | PASS（8/8） |
| 业务缺口 | 0 |

## 遗留

- Sprint52-C 阻塞问题为 0，未登记业务缺口。
- Sprint52-C Fix3 重跑 8/8 PASS（wd_tlms 1.0.126）。
- 下一子意图：Sprint52-G。
