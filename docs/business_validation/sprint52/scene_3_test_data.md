# Sprint52-C Scene 3 Test Data

> 契约：`INT-TMS-SPRINT52C-001`
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
| transport.inquiry | 0 | 等待验证指令后从 request 派生 |
| transport.quote | 0 | 等待验证指令后从 inquiry 派生 |
| transport.order | 0 | quote accepted 后自动创建 |
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
| Request | 8 条已写入（见下表） | completed |
| Inquiry | 1087-1094 | accepted |
| Quote | 830-837 | accepted |
| Order | 2654-2661 | closed |

### 已写入 Request

| # | 组合 | Request ID | Matrix Code | Matrix / Vehicle Result | 状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 柜+外部+T1+普通 | 3797 | S3-B2-C1-D2-E1-F2 | pass / pass | completed |
| 2 | 柜+自有+普通+普通 | 3798 | S3-B2-C1-D1-E2-F2 | pass / pass | completed |
| 3 | 托+外部+普通+普通 | 3799 | S3-B2-C2-D2-E2-F2 | pass / pass | completed |
| 4 | 托+自有+T1+普通 | 3800 | S3-B2-C2-D1-E1-F2 | pass / pass | completed |
| 5 | 件+外部+普通+普通 | 3801 | S3-B2-C3-D2-E2-F2 | pass / pass | completed |
| 6 | 件+自有+普通+普通 | 3802 | S3-B2-C3-D1-E2-F2 | pass / pass | completed |
| 7 | 柜+外部+普通+危品 | 3803 | S3-B2-C1-D2-E2-F1 | pass / pass | completed |
| 8 | 托+自有+T1+危品 | 3804 | S3-B2-C2-D1-E1-F1 | pass / pass | completed |
