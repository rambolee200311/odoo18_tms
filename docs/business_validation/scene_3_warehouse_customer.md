# Scene: Warehouse → Customer — 详细操作指导

**Flow**: commercial | **Entry**: Inquiry → Quote | **Expected Scene**: warehouse_to_customer

## Prerequisites
- Golden dataset base_data.xml imported
- Scene `warehouse_to_customer` exists in transport.scene

## Steps for commercial

### Step 1: Create Transport Request
1. Open Transport Requests menu → Create
2. Fill request_type = **commercial**, destination_type = **warehouse**
3. Save

### Step 2: Start Inquiry → Accept Quote → Order auto-created
1. Click "Start Inquiry", add carrier response, create Quote, accept
2. Verify scene chain

### Step 3: Verify
- Request.scene_id = warehouse_to_customer
- Order.scene_id = warehouse_to_customer (immutable snapshot)
- Flow validation: allowed_flows matches request_type

## Checklist
- [ ] Entry doc created successfully
- [ ] Scene source correct: warehouse_to_customer
- [ ] Scene_id not lost in chain
- [ ] Order snapshot immutable (readonly)
- [ ] Related object state matches expectations
