# Warehouse → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: warehouse_to_customer

> Sprint47 人工验证进行中 | 开始日期：2026-08-05 | wd_tlms 1.0.104

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **warehouse_to_customer** | Transport → Configuration → Transport Scenes | 升级模块或手动创建 |
| 0.2 | Partner: 客户 | Contacts | 手动创建 |
| 0.3 | Partner: 承运商（is_carrier=True） | Contacts | 手动创建 |
| 0.4 | Warehouse: 至少一个仓库 | Inventory → Warehouses | 手动创建 |





## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 3.1 | Create Request（场景驱动） | Transport Scene=warehouse_to_customer → 自动匹配 origin=warehouse, dest=customer；选 source warehouse 自动填充 origin 地址、选 customer 自动填充 destination 地址 | Saved, 地址已填充 | [ ] |
| 3.2 | Start Inquiry | Click Start Inquiry；Inquiry 投影 Request 场景/地址/Cargo | Inquiry draft，Carrier 为空 | [ ] |
| 3.3 | Carrier Response & Select Carrier | 承运商在 Inquiry 录入报价 → Record Response → Select Carrier | Inquiry responded → accepted，total=承运商报价 | [ ] |
| 3.4 | Create Customer Quote | From Inquiry → Create Customer Quote；自动生成 Transportation Fee（=询价合计）；编辑费用行定客户价 | Quote draft；Customer Price=应收费用行合计；margin 自动推导 | [ ] |
| 3.5 | Customer Accept Quote → Order | Send to Customer → Accept Quote | Order 自动创建；scene_id=warehouse_to_customer；carrier=Inquiry 承运商 | [ ] |
| 3.6 | Verify Fee Lines | Open Order → Fees 页 | customer_charge 应收 + carrier_cost 应付 与 Quote/Inquiry 一致 | [ ] |

## Sprint47 验证进度

| Step | Description | Result | Notes |
|------|-------------|--------|-------|
| 3.1-S47 | Create Transport Request（warehouse_to_customer） | ⏳ PENDING | 发现 SD47-S3-001：pallet cargo line 无托件明细，1.0.105 已修复待 UI 复验 |
| 3.2-S47 | Start Inquiry | ⏳ PENDING | |
| 3.3-S47 | Carrier Response & Select Carrier | ⏳ PENDING | |
| 3.4-S47 | Create Customer Quote | ⏳ PENDING | |
| 3.5-S47 | Customer Accept Quote → Order | ⏳ PENDING | |
| 3.6-S47 | Verify Fee Lines | ⏳ PENDING | |


## Issues Found
| Step | Issue Description | Severity | Reported | Fix Status |
|------|------------------|----------|----------|------------|
| 3.1 | cargo_type=pallet 时 Cargo Lines 仍匹配集装箱字段（container_no/BL），无托件明细；Inquiry/Quote 无托件行 | blocking | 2026-08-05 | fixed（1.0.105 待 UI 复验） |


## Fix Record
| Bug ID | Scene | Root Cause | Fix Scope | Commit | Regression Test | Status |
|--------|-------|-----------|-----------|--------|-----------------|--------|
| SD47-S3-001 | S3 | cargo line 视图/Inquiry/Quote 只处理集装箱明细，pallet 无对应行 | Request Cargo Lines 按 cargo_type 显隐列（pallet 显示 commodity/qty/uom/packages）；action_start_inquiry / action_create_quote 无 cargo line 且 cargo_type=pallet 时生成 Pallet x / Package y 行 | 1.0.105 | shell 临时 pallet request→inquiry→quote 验证通过 | fixed |


## Final Result
- **BAT**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Manual**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Executor**: lijianqiang
- **Date**: 2026-08-05
- **Environment**: Odoo 18 dev
- **Context Version**: 1.0.104


---

## 地址架构验证（Sprint44/45）

**场景**: S3 Warehouse → Customer | **code**: warehouse_to_customer

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **warehouse_to_customer** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：warehouse (选 source warehouse 自动填充 origin 地址) | 地址字段自动填充 | [ ] |
| A.3 | 终点：customer (选 partner_id 自动填充 destination 地址) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Commercial → Inquiry → Quote → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
