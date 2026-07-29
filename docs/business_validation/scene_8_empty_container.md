# Empty Container Move — Operation Guide + Issue Log + Fix Record

**Flow**: plan_driven | **Entry**: Container Service → Order | **Expected Scene**: empty_depot

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
