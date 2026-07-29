## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: empty_depot | [ ] | Settings -> Scenes |
| Container Master record | [ ] | Container -> Masters |
| Depot Partner | [ ] | Contacts |
| Warehouse | [ ] | Inventory -> Warehouses |
| Carrier Partner | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene empty_depot exists
- [ ] Container Master exists (e.g. MSCU1234567)
- [ ] Depot and warehouse exist
- [ ] Carrier partner exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 8.1: Create Container Service Request
1. Container Service -> Create. Direction = Depot -> Warehouse (or reverse)
2. Fill Container, Depot, Warehouse, Carrier, Planned Date. Save.

### Step 8.2: Confirm -> Create Transport Order
1. Click Confirm, then Create Dispatch Order
2. Expected: Transport Order created

### Step 8.3: Verify Scene
1. Open created Order -> check scene_id
2. Expected: order.scene_id = empty_depot (from container service, NOT transport.request)

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
