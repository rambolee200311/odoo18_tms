# Scene 8: Empty Container Move (Manual Verification)
**Flow**: Plan-Driven (via Container Service) | **Entry**: Container Service Request

## Steps
1. Create container.service.request (depot → warehouse)
2. Confirm → Create Dispatch Order
3. Verify order.scene_id = scene_empty_depot

## Expected Results
- [ ] Container service request → Order created
- [ ] Order.scene_id = scene_empty_depot
- [ ] Scene is from container service, not transport.request
