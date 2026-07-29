# Terminal → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: terminal_to_customer

---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 2.1 | Create Transport Request | Transport Requests → Create, request_type=commercial, destination_type=customer, save | Request state=draft | [ ] |
| 2.2 | Start Inquiry | Click "Start Inquiry" | Inquiry created, state=draft, request_id=the request | [ ] |
| 2.3 | Accept Carrier Response | Add carrier response (DHL, 850 EUR), accept | Inquiry state=accepted | [ ] |
| 2.4 | Create & Accept Quote | Create Quote from inquiry, set cost+margin, accept | Order auto-created, scene_id=request.scene_id | [ ] |
| 2.5 | Verify Fee Lines | Open Order → Fees tab | carrier_cost line exists, customer_charge line exists (if applicable) | [ ] |

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
