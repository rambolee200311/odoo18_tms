# Sprint52-C Scene 3: Warehouse → Customer

> 契约：`INT-TMS-SPRINT52C-001`
> 场景码：`warehouse_to_customer`
> 链路：request → inquiry → quote → transport.order → delivery

## 前置条件

- `common_pre_check.md` 已执行。
- Master Data：SPN Warehouse（起点）、Customer（终点，可复用现有客户或自由地址）、Carrier 可用。
- wd_tlms >= 1.0.125（商务链双向费用修复已生效）。

## 验证步骤

| 步骤 | 操作 | 预期 |
| :--- | :--- | :--- |
| 1 | 创建 request，场景 = warehouse_to_customer，选择 source warehouse | state=draft，scene/起终点/地址正确，origin 地址自动填充 |
| 2 | Start Inquiry | inquiry 创建，Carrier 为空，cargo 投影正确 |
| 3 | Send to Carrier / 承运商响应 / Select Carrier | inquiry → sent → responded → accepted |
| 4 | Create Customer Quote | quote 自动带出 Carrier Cost，可设 Margin |
| 5 | Send to Customer / Accept Quote | quote → sent → accepted，自动创建 order |
| 6 | 检查 order | scene/carrier/partner/地址快照正确 |
| 7 | 检查 fee.line | customer_charge 应收 + carrier_cost 应付与 quote 一致 |
| 8 | order 状态流转 | confirm → allocated → in_transit → delivered → closed |
| 9 | 检查 Event Ledger 与 Snapshot | 事件全部命中字典，Request/Order 快照存在 |
| 10 | 检查业务缺口 | 记录到 issue register，不直接修复 |

## 验收清单

| # | Check | Result |
| :--- | :--- | :--- |
| 1 | Commercial Flow 完整 | [ ] |
| 2 | State Transition 符合冻结状态机 | [ ] |
| 3 | Event Ledger 先写账本再改状态 | [ ] |
| 4 | Request 双 Snapshot 存在 | [ ] |
| 5 | Order Allocation Snapshot 存在 | [ ] |
| 6 | Fee Line 金额一致 | [ ] |
| 7 | Business Gap 已登记 | [ ] |
