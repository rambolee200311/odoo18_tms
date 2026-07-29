# Scene: Warehouse Transfer — 详细操作指导

**Flow**: plan_driven | **Entry**: Pickup Plan | **Expected Scene**: warehouse_transfer

## Prerequisites
- Golden dataset base_data.xml imported
- Scene `warehouse_transfer` exists in transport.scene

## Steps for plan_driven

### Step 1: Create Transport Request
1. Open Transport Requests menu → Create
2. Fill request_type = **plan_driven**, destination_type = **warehouse**
3. Save

### Step 2: Schedule → Pickup Plan → Create Transport Order
1. Go to Schedule Calendar, drag to date, open Pickup Plan, click Create Transport Order
2. Verify scene chain

### Step 3: Verify
- Request.scene_id = warehouse_transfer
- Order.scene_id = warehouse_transfer (immutable snapshot)
- Flow validation: allowed_flows matches request_type

## Checklist
- [ ] Entry doc created successfully
- [ ] Scene source correct: warehouse_transfer
- [ ] Scene_id not lost in chain
- [ ] Order snapshot immutable (readonly)
- [ ] Related object state matches expectations
