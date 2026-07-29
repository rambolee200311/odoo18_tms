## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: terminal_to_customer | [ ] | Settings -> Scenes |
| Company Partner (customer) | [ ] | Contacts |
| Carrier Partner (is_carrier=True) | [ ] | Contacts |
| Terminal Partner | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene terminal_to_customer exists
- [ ] Customer partner exists
- [ ] Carrier partner exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 2.1: Create Transport Request
1. Transport Requests -> Create -> Request Type = **Commercial**, Destination = **Terminal / Depot to Customer**
2. Fill Customer, Origin Terminal, Delivery Address. Save.

### Step 2.2: Start Inquiry
1. Click **Start Inquiry**
2. Expected: Inquiry created (state=Draft)

### Step 2.3: Accept Carrier Response
1. Add carrier response (e.g. DHL, EUR 850), click Accept
2. Expected: Inquiry state = Accepted

### Step 2.4: Create and Accept Quote
1. From Inquiry -> Create Quote. Set Carrier Cost + Margin. Set state to Accepted.
2. Expected: Order auto-created. order.scene_id = terminal_to_customer

### Step 2.5: Verify Fee Lines
1. Open Order -> Fees tab
2. Expected: carrier_cost fee line exists

---

## Failure Handling

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Field or button missing | View bug / missing permission | Record bug -> Codex fixes |
| Cannot select value | Missing prerequisite | Check Prerequisites section |
| Save fails | Validation error | Follow error message |
| Scene chain broken | scene_id not inherited | Record as blocking bug |

---

## Issues Found
| Bug ID | Scene | Step | Description | Severity | Root Cause | Fix Scope | Commit | Status |
|--------|-------|------|-------------|----------|-----------|-----------|--------|--------|
| | | | | | | | | |

## Fix Record
| Bug ID | Root Cause | Fix Summary | Commit | Regression Test | Status |
|--------|-----------|-------------|--------|-----------------|--------|
| | | | | | |

## Final Result
- **Manual**: pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Executor**:
- **Date**:
- **Environment**:
- **Context Version**:
