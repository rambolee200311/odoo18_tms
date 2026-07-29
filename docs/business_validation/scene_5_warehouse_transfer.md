# Scene 5: Warehouse Transfer (Manual Verification)
**Flow**: Plan-Driven | **Entry**: Pickup Plan | **Expected Scene**: warehouse_transfer

## Steps
1. Create transport.request (plan_driven, warehouse_transfer)
2. Set source_warehouse + destination warehouse
3. Verify bonded_transfer constraint
4. Schedule → Pickup Plan → Create Order
5. Verify container handling and cost allocation

## Expected Results
- [ ] Scene ID: warehouse_transfer
- [ ] Bonded transfer constraint works
- [ ] Allocation exists after settlement
