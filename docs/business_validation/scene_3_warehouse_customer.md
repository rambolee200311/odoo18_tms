# Warehouse → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: warehouse_to_customer

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
| 3.2 | Inquiry → Quote → Order | Same flow as S2 | Order created, scene_id=warehouse_to_customer | [ ] |


## Issues Found
| Step | Issue Description | Severity | Reported | Fix Status |
|------|------------------|----------|----------|------------|
| | _(user fills this)_ | blocking / minor | date | pending / fixed / deferred |


## Fix Record
| Bug ID | Scene | Root Cause | Fix Scope | Commit | Regression Test | Status |
|--------|-------|-----------|-----------|--------|-----------------|--------|
| | | | | | | |


## Final Result
- **BAT**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Manual**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk


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
