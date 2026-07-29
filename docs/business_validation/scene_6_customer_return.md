# Scene 6: Customer Return (Manual Verification)
**Flow**: Commercial | **Entry**: Inquiry → Quote | **Expected Scene**: customer_return

## Steps
1. Create transport.request (commercial, destination_type=warehouse)
2. Inquiry → Quote with carrier_cost + margin
3. Accept Quote → verify order + fee.line creation

## Expected Results
- [ ] Scene ID: customer_return
- [ ] Inquiry → Quote → Order scene chain
- [ ] fee.line carrier_cost + customer_charge both exist
