# Scene: Container Swap — 详细操作指导

**Flow**: N/A | **Entry**: Field Extension | **Expected Scene**: N/A

## Prerequisites
- Golden dataset base_data.xml imported
- Scene `N/A` exists in transport.scene

## Steps for N/A

### Step 1: Create Transport Request
1. Open Transport Requests menu → Create
2. Fill request_type = **N/A**, destination_type = **warehouse**
3. Save

### Step 2: Schedule → Pickup Plan → Create Transport Order
1. Go to Schedule Calendar, drag to date, open Pickup Plan, click Create Transport Order
2. Verify scene chain

### Step 3: Verify
- Request.scene_id = N/A
- Order.scene_id = N/A (immutable snapshot)
- Flow validation: allowed_flows matches request_type

## Checklist
- [ ] Entry doc created successfully
- [ ] Scene source correct: N/A
- [ ] Scene_id not lost in chain
- [ ] Order snapshot immutable (readonly)
- [ ] Related object state matches expectations
