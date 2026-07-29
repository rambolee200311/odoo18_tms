## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: terminal_to_warehouse | [ ] | Settings -> Scenes |
| Transport Type: port_to_warehouse | [ ] | Settings -> Transport Types |
| Company Partner (customer/carrier) | [ ] | Contacts |
| Warehouse (destination) | [ ] | Inventory -> Warehouses |
| Terminal Partner (origin) | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene terminal_to_warehouse exists
- [ ] Transport type port_to_warehouse exists
- [ ] Warehouse exists (e.g. Rotterdam Warehouse)
- [ ] Terminal partner exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 1.1: Create Transport Request
1. Transport Requests -> Create
2. Request Type = **Plan-Driven**, Cargo Type = **Container**, Destination = **Terminal / Depot to Our Warehouse**
3. Origin Terminal = select a terminal partner, Destination Warehouse = select a warehouse
4. Save
5. Expected: state=Draft, terminal_id and warehouse_id filled

### Step 1.2: Open Schedule Calendar
1. Click **Go to Schedule** header button
2. Expected: Calendar opens, request in left panel

### Step 1.3: Schedule via Drag-and-Drop
1. Drag request to a date cell
2. Expected: Pickup Plan created, appears in Scheduling tab

### Step 1.4: Verify Scene Chain
1. Open Pickup Plan: scene_id = terminal_to_warehouse (readonly, inherited)
2. Open Request: request.scene_id = terminal_to_warehouse

### Step 1.5: Create Transport Order
1. In Pickup Plan click **Create Transport Order**
2. Check Order: scene_id = terminal_to_warehouse, transport_type auto-filled, carrier auto-filled (if set)

### Step 1.6: Verify Order Snapshot
1. Order.scene_id is readonly (not editable), copy=False (not copied on duplicate)

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
