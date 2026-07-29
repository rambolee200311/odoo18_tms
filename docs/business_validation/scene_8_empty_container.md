# Scene: Empty Container Move — 详细操作指导

**Flow**: plan_driven | **Entry**: Container Service Request | **Expected Scene**: empty_depot

## Prerequisites
- Golden dataset base_data.xml imported
- Scene `empty_depot` exists in transport.scene

## Steps for plan_driven

### Step 1: Create Transport Request
1. Open Transport Requests menu → Create
2. Fill request_type = **plan_driven**, destination_type = **empty**
3. Save

### Step 2: Schedule → Pickup Plan → Create Transport Order
1. Go to Schedule Calendar, drag to date, open Pickup Plan, click Create Transport Order
2. Verify scene chain

### Step 3: Verify
- Request.scene_id = empty_depot
- Order.scene_id = empty_depot (immutable snapshot)
- Flow validation: allowed_flows matches request_type

## Checklist
- [ ] Entry doc created successfully
- [ ] Scene source correct: empty_depot
- [ ] Scene_id not lost in chain
- [ ] Order snapshot immutable (readonly)
- [ ] Related object state matches expectations
