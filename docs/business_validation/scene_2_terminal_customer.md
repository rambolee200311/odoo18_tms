# Scene 2: Terminal → Customer (Manual Verification)
**Flow**: Commercial | **Entry**: Inquiry → Quote | **Expected Scene**: terminal_to_customer

## Steps
1. Create transport.request (request_type=commercial, destination_type=customer)
2. Click "Start Inquiry", verify inquiry created
3. Add carrier response, accept
4. Create Quote, verify scene_id synced from request
5. Accept Quote, verify order auto-created with scene_id

## Expected Results
- [ ] Request → Quote → Order scene chain consistent
- [ ] Order.scene_id = terminal_to_customer
- [ ] fee.line exists with carrier_cost + customer_charge
