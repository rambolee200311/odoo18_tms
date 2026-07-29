# Scene 1: Terminal → Warehouse (Manual Verification)
**Flow**: Plan-Driven | **Entry**: Pickup Plan | **Expected Scene**: terminal_to_warehouse

## Prerequisites
- Golden dataset base_data.xml + scenario_s1.xml imported
- Scene terminal_to_warehouse exists in transport.scene with allowed_flow=plan_driven

## Steps
1. Create transport.request (request_type=plan_driven, destination_type=warehouse)
2. Open Schedule Calendar, verify request appears in left panel
3. Drag to a date, verify pickup.plan created
4. Open pickup.plan, verify scene_id inherited from request
5. Click "Create Transport Order", verify order created with scene_id
6. Verify order.scene_id is readonly after creation

## Expected Results
- [ ] Request.scene_id = terminal_to_warehouse
- [ ] Pickup plan.scene_id = terminal_to_warehouse
- [ ] Order.scene_id = terminal_to_warehouse (immutable snapshot)
- [ ] Flow validation: allowed_flow=plan_driven matches request_type
