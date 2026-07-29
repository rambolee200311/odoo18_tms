# Warehouse Transfer — Operation Guide + Issue Log + Fix Record

**Flow**: plan_driven | **Entry**: Pickup Plan → Order | **Expected Scene**: warehouse_transfer

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **warehouse_transfer** | Scenes 列表 | 升级模块或手动创建 |
| 0.2 | Transport Type: **warehouse_transfer** | Transport Types | 升级模块或手动创建 |
| 0.3 | Warehouse A（source） | Inventory → Warehouses | 手动创建（如 "Rotterdam WH"） |
| 0.4 | Warehouse B（destination，不可与 A 相同） | Inventory → Warehouses | 手动创建（如 "Den Haag WH"） |
| 0.5 | Partner: 承运商（is_carrier=True） | Contacts | 手动创建 |





## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 5.1 | Create Request (plan_driven, transfer) | Create request: plan_driven, destination=warehouse_transfer, source_WH + dest_WH | Saved | [ ] |
| 5.2 | Verify Bonded Transfer | If source/dest WH is bonded → is_bonded_transfer=True required | Constraint enforced | [ ] |
| 5.3 | Schedule → Pickup Plan → Order | Drag to calendar, open Pickup Plan, Create Transport Order | Order created, scene_id=warehouse_transfer | [ ] |


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
