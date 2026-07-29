# Warehouse Transfer — Operation Guide + Issue Log + Fix Record

**Flow**: plan_driven | **Entry**: Pickup Plan → Order | **Expected Scene**: warehouse_transfer

---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 5.1 | Create Request (plan_driven, transfer) | Create request: plan_driven, destination=warehouse_transfer, source_WH + dest_WH | Saved | [ ] |
| 5.2 | Verify Bonded Transfer | If source/dest WH is bonded → is_bonded_transfer=True required | Constraint enforced | [ ] |
| 5.3 | Schedule → Pickup Plan → Order | Drag to calendar, open Pickup Plan, Create Transport Order | Order created, scene_id=warehouse_transfer | [ ] |

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
