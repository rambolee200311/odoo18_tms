# Scene 1: Terminal → Warehouse — 详细操作指导

## Prerequisites
- [ ] Golden dataset base_data.xml imported
- [ ] Scene `terminal_to_warehouse` exists in transport.scene
- [ ] Transport type `port_to_warehouse` exists
- [ ] User has plan_driven request creation permission

## Step-by-Step

### Step 1: Create Transport Request
1. Open Transport Requests menu
2. Click "Create"
3. Fill in:
   - Request Type: **Plan-Driven**
   - Cargo Type: **Container**
   - Destination: **Terminal / Depot to Our Warehouse**
4. Save
5. **Expected**: Request state = draft, request_type = plan_driven

### Step 2: Open Schedule Calendar
1. Click "Go to Schedule" header button
2. **Expected**: Calendar view opens with request in left panel
3. Verify request's cargo appears in unscheduled list

### Step 3: Schedule via Drag-and-Drop
1. Drag the request/item to a date cell
2. **Expected**: Pickup Plan created automatically
3. Verify: Pickup Plan appears in the Scheduling tab of the request

### Step 4: Verify Scene Chain
1. Open the created Pickup Plan
2. **Expected**: Pickup Plan.scene_id is inherited from request (readonly)
3. **Expected**: Pickup Plan.scene_id is NOT editable (related field)

### Step 5: Create Transport Order
1. In Pickup Plan, click "Create Transport Order"
2. **Expected**: Transport Order created
3. Verify Order:
   - [ ] order.scene_id = request.scene_id (terminal_to_warehouse)
   - [ ] order.request_id = original request
   - [ ] order.transport_type = port_to_warehouse (or scene.default)
   - [ ] order.scene_id is readonly (immutable snapshot)

### Step 6: Verify Flow Validation
1. Try to change request.scene_id to a different scene
2. **Expected**: If the new scene has different allowed_flows, validation error

## Checklist
- [ ] Request.scene_id = terminal_to_warehouse
- [ ] Pickup Plan.scene_id = terminal_to_warehouse (inherited, readonly)
- [ ] Order.scene_id = terminal_to_warehouse (immutable)
- [ ] Flow type = plan_driven matches scene.allowed_flows
- [ ] Transport type = port_to_warehouse (from scene.default or mapping)
- [ ] Settlement: allocation can be created from order
