## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: warehouse_transfer | [ ] | Settings -> Scenes |
| Transport Type: warehouse_transfer | [ ] | Settings -> Transport Types |
| Warehouse A (source) | [ ] | Inventory -> Warehouses |
| Warehouse B (dest, diff from A) | [ ] | Inventory -> Warehouses |
| Carrier Partner | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene warehouse_transfer exists
- [ ] Transport type warehouse_transfer exists
- [ ] Two different warehouses exist
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 5.1: Create Transport Request
1. Transport Requests -> Create -> Request Type = **Plan-Driven**, Destination = **Our Warehouse Transfer**
2. Source Warehouse = select WH A, Destination Warehouse = select WH B (must differ from A). Save.

### Step 5.2: Check Bonded Transfer
1. If source/dest WH is bonded -> is_bonded_transfer must be True
2. Expected: Constraint enforced if bonded

### Step 5.3: Schedule -> Pickup Plan -> Order
1. Go to Schedule -> drag to date -> Pickup Plan created -> Create Transport Order
2. Expected: Order created. order.scene_id = warehouse_transfer

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
