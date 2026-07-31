# Sprint42-47 Business Scenario Validation — Results
> Status: Sprint47 in_progress | Last Updated: 2026-07-31
> Status Enums: pass / fail-fixed / fail-deferred / fail-accepted-risk / pending

| Scene | Name | Scene Code | origin_type | destination_type | Manual | Issues | Notes |
|-------|------|-----------|-------------|-----------------|--------|--------|-------|
| S1 | Terminal → Warehouse | terminal_to_warehouse | terminal | warehouse | ⏳ | 0 | Scene1 旧流程已 PASS，地址架构需重验 |
| S2 | Terminal → Customer | terminal_to_customer | terminal | customer | ⏳ | 0 | 地址架构需重验 |
| S3 | Warehouse → Customer | warehouse_to_customer | warehouse | customer | ⏳ | 0 | |
| S4 | Customer A → B | customer_to_customer | customer | customer | ⏳ | 0 | |
| S5 | Warehouse Transfer | warehouse_transfer | warehouse | warehouse | ⏳ | 0 | |
| S6 | Customer Return | customer_to_warehouse | customer | warehouse | ⏳ | 0 | |
| S7 | Container Swap | container_swap | terminal | warehouse | ⏳ | 0 | |
| S8 | Empty Depot | empty_depot | depot | warehouse | ⏳ | 0 | |

## 地址架构公共验证项（Sprint44/45）

| # | Check | Result |
|---|-------|--------|
| 1 | 8 场景 origin_type/destination_type 正确 | ⏳ |
| 2 | Request 表单选场景后显示地址组 | ⏳ |
| 3 | terminal/warehouse/partner 自动填充地址 | ⏳ |
| 4 | 用户可编辑自动填充地址 | ⏳ |
| 5 | Plan 创建时地址快照复制 | ⏳ |
| 6 | Order 创建时地址一致 | ⏳ |
| 7 | Order 确认后地址只读 | ⏳ |

## 缺陷汇总

| Bug ID | Scene | Description | Status |
|--------|-------|-------------|--------|
| （待人工验证填写） | | | |

---

*执行说明：每个场景在 docs/business_validation/scene_N_*.md 的"地址架构验证"章节逐项勾选，缺陷记录到该场景 Issues Found，汇总到上表。*
