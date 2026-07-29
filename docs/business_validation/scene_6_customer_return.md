# Customer Return — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: customer_return

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **customer_return** | Scenes 列表 | 升级模块或手动创建 |
| 0.2 | Transport Type: **reverse_logistics** | Transport Types | 升级模块或手动创建 |
| 0.3 | Partner: 客户 | Contacts | 手动创建 |
| 0.4 | Partner: 承运商（is_carrier=True） | Contacts | 手动创建 |
| 0.5 | Warehouse | Inventory → Warehouses | 手动创建 |





## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 6.1 | Create Request (commercial, return) | Create request: commercial, destination=warehouse, partner=customer | Saved | [ ] |
| 6.2 | Inquiry → Quote | Same as S2 flow | Quote with carrier_cost + margin | [ ] |
| 6.3 | Accept Quote → Order | Accept quote | Order created, fee.line carrier_cost + customer_charge both exist | [ ] |


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
