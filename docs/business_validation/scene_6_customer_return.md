## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: customer_return | [ ] | Settings -> Scenes |
| Transport Type: reverse_logistics | [ ] | Settings -> Transport Types |
| Company Partner (customer) | [ ] | Contacts |
| Carrier Partner | [ ] | Contacts |
| Warehouse (return destination) | [ ] | Inventory -> Warehouses |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene customer_return exists
- [ ] Transport type reverse_logistics exists
- [ ] Customer and carrier partners exist
- [ ] Warehouse exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 6.1: Create Transport Request
1. Transport Requests -> Create -> Request Type = **Commercial**, Destination = **Customer Address to Our Warehouse**
2. Customer = select partner, Source Warehouse = select WH. Save.

### Step 6.2: Inquiry -> Quote
1. Start Inquiry -> accept carrier -> Create Quote with Carrier Cost + Margin
2. Expected: Quote created

### Step 6.3: Accept Quote -> Verify Fee Lines
1. Set Quote to Accepted. Open created Order -> Fees tab.
2. Expected: Order auto-created. Fee lines: carrier_cost + customer_charge

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
