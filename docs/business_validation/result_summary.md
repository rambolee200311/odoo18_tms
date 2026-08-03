# Sprint42-47 Business Scenario Validation — Results
> Status: Sprint47 in_progress | Last Updated: 2026-07-31
> Status Enums: pass / fail-fixed / fail-deferred / fail-accepted-risk / pending

| Scene | Name | Scene Code | origin_type | destination_type | Manual | Issues | Notes |
|-------|------|-----------|-------------|-----------------|--------|--------|-------|
| S1 | Terminal → Warehouse | terminal_to_warehouse | terminal | warehouse | ⏳ | 3 | 1.1/1.2/1.4 PASS；1.3/1.5 已修复待 UI 复验（SD47-S1-002/003/004） |
| S2 | Terminal → Customer | terminal_to_customer | terminal | customer | ⏳ | 3 | 2.1 PASS；2.2 已修复待 UI 复验（SD47-S2-002/003/004） |
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
| SD47-S1-001 | S1 | Step 1.1 未创建 Cargo Line（container_no / bl_number 为空） | fixed |
| SD47-S1-002 | S1 | Step 1.3 拖拽后日历不显示（时区日期偏移） | fixed（待 UI 复验） |
| SD47-S1-003 | S1 | Step 1.5 Customer=Carrier 且 scene_id 缺失 | fixed（待 UI 复验） |
| SD47-S1-004 | S1 | Step 1.5 订单无起始地点展示 | fixed（待 UI 复验） |
| SD47-S2-001 | S2 | 无客户主档的目的地无法保存 | fixed |
| SD47-S2-002 | S2 | Inquiry Carrier 默认成 ljq | fixed（待 UI 复验） |
| SD47-S2-003 | S2 | Inquiry 无 cargo 信息 | fixed（待 UI 复验） |
| SD47-S2-004 | S2 | Inquiry 表单排版混乱 | fixed（待 UI 复验） |
| SD47-S2-005 | S2 | 2074 city 缺失 / legacy destination_type 不一致 | accepted |
| SD47-S2-006 | S2 | 3PL 流程缺失客户接受环节 | fixed（待 UI 复验） |
| SD47-S2-007 | S2 | Quote Margin Rate 显示错误 + 无 cargo line | fixed（待 UI 复验） |
| SD47-S2-008 | S2 | Quote cargo 描述缺柜号/BL；Fee Lines 只读 | fixed（待 UI 复验） |

---

*执行说明：每个场景在 docs/business_validation/scene_N_*.md 的"地址架构验证"章节逐项勾选，缺陷记录到该场景 Issues Found，汇总到上表。*
