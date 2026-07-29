# Scene 7: Container Swap (Manual Verification)
**Flow**: N/A | **Entry**: Field Extension | **Expected**: needs_swap on container_line

## Steps
1. Open transport.order with container
2. Verify container_line has needs_swap field
3. Set needs_swap=True, fill swap_location

## Expected Results
- [ ] needs_swap field visible on container_line
- [ ] swap_location recorded
