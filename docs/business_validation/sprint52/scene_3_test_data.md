# Sprint52-C Scene 3 Test Data

> 契约：`INT-TMS-SPRINT52C-001`
> 2026-08-10：按 `INT-TMS-SPRINT52FIX-003` 重新 mock，
> 商务链使用 Create Carrier Inquiry / Create Customer Quote wizard。
> 原则：复用 Master Data，只创建 1 套 Transaction Data。

## Master Data（复用/待确认）

| 对象 | 名称 | 说明 |
| :--- | :--- | :--- |
| Warehouse | SPN | 起点仓库，复用现有 warehouse，source_warehouse_id 自动填充 origin 地址 |
| Customer | 待选定 | 终点客户，可复用现有 partner 或使用自由地址 |
| Carrier | 待选定 | 外部/自有车队，T1/危品资质按组合确认 |

## Transaction Data（计划创建）

| 对象 | 数量 | 说明 |
| :--- | :--- | :--- |
| transport.request | 8 | scene=warehouse_to_customer, request_type=commercial |
| transport.inquiry | 8 | Create Carrier Inquiry wizard 创建并记录响应 |
| transport.quote | 8 | Create Customer Quote wizard 从 selected inquiry 创建 |
| transport.order | 8 | quote accepted 后自动创建，回填 carrier/inquiry/quote |
| event.ledger | N | 状态流转对应事件编码 |

## 组合矩阵

与 Sprint52-A/B 保持一致，8 个代表组合：

| # | 货型 | 车队 | T1 | 危品 |
| :--- | :--- | :--- | :--- | :--- |
| 1 | 柜 | 外部 | T1 | 普通 |
| 2 | 柜 | 自有 | 普通 | 普通 |
| 3 | 托 | 外部 | 普通 | 普通 |
| 4 | 托 | 自有 | T1 | 普通 |
| 5 | 件 | 外部 | 普通 | 普通 |
| 6 | 件 | 自有 | 普通 | 普通 |
| 7 | 柜 | 外部 | 普通 | 危品 |
| 8 | 托 | 自有 | T1 | 危品 |

覆盖口径：3 货型 × 2 车队 × 2 T1 × 2 危品，全量 24 组合中选取代表 8 组合。

## 执行后填写

| 对象 | ID / Name | 状态 |
| :--- | :--- | :--- |
| Request | 8 条已写入（见下表，Fix3 重跑 3808-3815） | completed |
| Inquiry | 1098-1105 | selected |
| Quote | 841-848 | accepted |
| Order | 2664-2671 | closed |

### 执行链路（FIX-003）

request → `Create Carrier Inquiry` wizard（carrier + cost + response_date）
→ inquiry responded → `action_select`（INQUIRY_SELECTED）
→ `Create Customer Quote` wizard（margin + service_fee）
→ quote `action_send`（communication_status=sent）
→ quote `action_accept`（accepted_by/accepted_date，ORDER_CREATED）
→ order 状态流转至 closed。

### 已写入 Request

| # | 组合 | Request ID | Matrix Code | Matrix / Vehicle Result | 状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 柜+外部+T1+普通 | 3808 | S3-B2-C1-D2-E1-F2 | pass / pass | completed |
| 2 | 柜+自有+普通+普通 | 3809 | S3-B2-C1-D1-E2-F2 | pass / pass | completed |
| 3 | 托+外部+普通+普通 | 3810 | S3-B2-C2-D2-E2-F2 | pass / pass | completed |
| 4 | 托+自有+T1+普通 | 3811 | S3-B2-C2-D1-E1-F2 | pass / pass | completed |
| 5 | 件+外部+普通+普通 | 3812 | S3-B2-C3-D2-E2-F2 | pass / pass | completed |
| 6 | 件+自有+普通+普通 | 3813 | S3-B2-C3-D1-E2-F2 | pass / pass | completed |
| 7 | 柜+外部+普通+危品 | 3814 | S3-B2-C1-D2-E2-F1 | pass / pass | completed |
| 8 | 托+自有+T1+危品 | 3815 | S3-B2-C2-D1-E1-F1 | pass / pass | completed |
