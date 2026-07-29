# Empty Container Move — Operation Guide + Issue Log + Fix Record

**Flow**: plan_driven | **Entry**: Container Service → Order | **Expected Scene**: empty_depot

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **empty_depot** | Scenes 列表 | 升级模块或手动创建 |
| 0.2 | Container Master：至少一个柜档案 | Container → Masters | 手动创建（如 "MSCU1234567", 40HQ） |
| 0.3 | Partner: 承运商（is_carrier=True） | Contacts | 手动创建 |
| 0.4 | Warehouse | Inventory → Warehouses | 手动创建 |
| 0.5 | Depot Partner | Contacts | 手动创建（如 "ECT Delta Terminal"） |

---



---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 8.1 | Create Container Service Request | Open Container Service → Create, fill depot+warehouse+cargo, save | Saved | [ ] |
| 8.2 | Confirm + Create Dispatch Order | Click Confirm → Create Dispatch Order | Transport Order created | [ ] |
| 8.3 | Verify Scene | Open created Order → check scene_id | scene_id = empty_depot (from container service context, NOT transport.request) | [ ] |

---

## Issues Found
| Step | Issue Description | Severity | Reported | Fix Status |
|------|------------------|----------|----------|------------|
| | _(user fills this)_ | blocking / minor | date | pending / fixed / deferred |

---

## Fix Record
| Bug ID | Scene | Root Cause | Fix Scope | Commit | Regression Test | Status |
|--------|-------|-----------|-----------|--------|-----------------|--------|
| | | | | | | |

---

## Final Result
- **BAT**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Manual**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
