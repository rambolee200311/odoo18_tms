# Sprint52-C Scene 3: Warehouse → Customer

> 契约：`INT-TMS-SPRINT52C-001`
> 场景码：`warehouse_to_customer`
> 链路：request → carrier inquiry（wizard）→ customer quote（wizard）
> → transport.order → delivery
> 2026-08-10：按 `INT-TMS-SPRINT52FIX-003` 重新 mock。

## 前置条件

- `common_pre_check.md` 已执行。
- Master Data：SPN Warehouse（起点）、Customer（终点，可复用现有客户或自由地址）、Carrier 可用。
- wd_tlms >= 1.0.126（Sprint52-Fix3 商务链流程修正已生效）。

## 验证步骤

| 步骤 | 操作 | 预期 |
| :--- | :--- | :--- |
| 1 | 创建 request，场景 = warehouse_to_customer，选择 source warehouse | state=draft，scene/起终点/地址正确，origin 地址自动填充 |
| 2 | Create Carrier Inquiry wizard（选承运商 + 成本 + 响应日期） | inquiry 创建并记录响应，留在 request 页面 |
| 3 | 承运商响应 / Select Carrier | inquiry → draft → sent → responded → selected |
| 4 | Create Customer Quote wizard（selected inquiry + margin + service fee） | quote 自动带出 Carrier Cost，Customer Price 可人工覆盖 |
| 5 | Send to Customer / Accept Quote | quote communication_status=sent → accepted，自动创建 order |
| 6 | 检查 order | scene/carrier/partner/地址快照正确，carrier_id/quote_id/inquiry_id 追溯完整 |
| 7 | 检查 fee.line | customer_charge 应收 + carrier_cost 应付与 quote 一致 |
| 8 | order 状态流转 | confirm → allocated → in_transit → delivered → closed |
| 9 | 检查 Event Ledger 与 Snapshot | INQUIRY_SELECTED/QUOTE_ACCEPTED/ORDER_CREATED 命中字典，Request/Order 快照存在 |
| 10 | 检查业务缺口 | 记录到 issue register，不直接修复 |

## 验收清单

| # | Check | Result |
| :--- | :--- | :--- |
| 1 | Commercial Flow 完整 | [ ] |
| 2 | State Transition 符合 Sprint52-Fix3 收敛状态机 | [ ] |
| 3 | Event Ledger 先写账本再改状态 | [ ] |
| 4 | Request 双 Snapshot 存在 | [ ] |
| 5 | Order Allocation Snapshot 存在 | [ ] |
| 6 | Fee Line 金额一致 | [ ] |
| 7 | Business Gap 已登记 | [ ] |
