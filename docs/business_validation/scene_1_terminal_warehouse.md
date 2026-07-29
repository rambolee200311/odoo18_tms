# Terminal → Warehouse — Operation Guide + Issue Log + Fix Record

**Flow**: plan_driven | **Entry**: Pickup Plan → Order | **Expected Scene**: terminal_to_warehouse

---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 1.1 | Create Transport Request | Transport Requests → Create. Fill: **Request Type**=Plan-Driven, **Cargo Type**=Container, **Destination**=Terminal / Depot to Our Warehouse, **Origin Terminal**=选一个 terminal partner（如 Rotterdam Maasvlakte Terminal），**Destination Warehouse**=选一个仓库（如 Rotterdam Warehouse）。Save | Request state=draft, request_type=plan_driven, terminal_id 和 warehouse_id 已填写 | [ ] |
| 1.2 | Open Schedule Calendar | Click "Go to Schedule" header button | Calendar opens with request in left panel | [ ] |
| 1.3 | Schedule via Drag-and-Drop | Drag request to a date cell | Pickup Plan created automatically | [ ] |
| 1.4 | Verify Scene Chain | Open Pickup Plan → confirm scene_id inherited from request (readonly) | scene_id = terminal_to_warehouse, NOT editable | [ ] |
| 1.5 | Create Transport Order | Click "Create Transport Order" in Pickup Plan | Order created, scene_id = request.scene_id, transport_type = port_to_warehouse | [ ] |
| 1.6 | Verify Order Snapshot | Open Order → check scene_id field definition | scene_id readonly=True, copy=False (immutable snapshot) | [ ] |

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
