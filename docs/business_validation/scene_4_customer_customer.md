# Customer → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: customer_to_customer

---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 4.1 | Create Request (commercial, customer) | Create request: commercial, destination=customer, no warehouse_id | Saved, partner_id required validated | [ ] |
| 4.2 | Inquiry → Quote → Order | Same flow as S2 | Order created, scene_id=customer_to_customer | [ ] |

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
