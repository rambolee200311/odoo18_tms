# Sprint52 Business Scenario Validation Phase

> 定位：在 Sprint49-50 Freeze Baseline 上做业务真实性验证，发现业务模型缺口，
> 不开发新功能，不修改冻结基线。

## 执行顺序

common_pre_check → A → C → B → G → H → E → F → D

| 子意图 | 场景 | 场景码 | 验证文档 |
| :--- | :--- | :--- | :--- |
| Sprint52-A | Terminal → Warehouse | terminal_to_warehouse | `scene_1_terminal_warehouse.md` |
| Sprint52-C | Warehouse → Customer | warehouse_to_customer | `scene_3_warehouse_customer.md` |
| Sprint52-B | Terminal → Customer | terminal_to_customer | `scene_2_terminal_customer.md` |
| Sprint52-G | Container Swap | container_swap | `scene_7_container_swap.md` |
| Sprint52-H | Empty Depot | empty_depot | `scene_8_empty_depot.md` |
| Sprint52-E | Warehouse Transfer | warehouse_transfer | `scene_5_warehouse_transfer.md` |
| Sprint52-F | Customer Return | customer_to_warehouse | `scene_6_customer_return.md` |
| Sprint52-D | Customer A → B | customer_to_customer | `scene_4_customer_customer.md` |

## 每个子意图固定结构

| 文件 | 用途 |
| :--- | :--- |
| `docs/context/intent/intent_sprint52x_*.yaml` | 子意图契约 |
| `scene_N_*.md` | 验证步骤与验收清单 |
| `scene_N_test_data.md` | 模拟数据清单 |
| `scene_N_result.md` | 验证结果 |
| `scene_N_issue_register.md` | 业务缺口与债务登记 |
| `docs/context/intent_records/INT-TMS-SPRINT52X-001/execution_record.md` | 执行记录 |

## 数据限制

- Master Data：复用现有 carrier / warehouse / customer / terminal / vehicle / driver。
- Transaction Data：每场景只允许 1 Request、1 Inquiry（商务链）、1 Quote（商务链）、1 Plan、1 Order、N Event Ledger。
- 不创建随机数据，不污染冻结基线。

## 阶段约束

1. Sprint52 是业务验证，不是 Development Sprint。
2. 不修改 Workflow 状态机、不新增 Event Code、不修改 Snapshot 结构、不扩展规则维度。
3. 发现的业务缺口统一登记为 business debt，修复必须另起新 intent。
