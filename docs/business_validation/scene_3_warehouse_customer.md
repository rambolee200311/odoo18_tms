# Warehouse → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: warehouse_to_customer

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **warehouse_to_customer** | Scenes 列表 | 升级模块或手动创建 |
| 0.2 | Partner: 客户 | Contacts | 手动创建 |
| 0.3 | Partner: 承运商（is_carrier=True） | Contacts | 手动创建 |
| 0.4 | Warehouse: 至少一个仓库 | Inventory → Warehouses | 手动创建 |





## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 3.1 | Create Request (commercial, warehouse) | Create request: commercial, destination=warehouse, partner=customer | Saved | [ ] |
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
