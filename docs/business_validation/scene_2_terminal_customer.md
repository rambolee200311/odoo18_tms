# Scene 2: Terminal → Customer — 详细操作指导

## Prerequisites
- [ ] Golden dataset base_data.xml imported
- [ ] Customer partner exists
- [ ] Scene `terminal_to_customer` exists

## Step-by-Step

### Step 1: Create Transport Request
1. Open Transport Requests → Create
2. Fill: Request Type = **Commercial**, Destination = **Terminal / Depot to Customer**
3. Fill: Customer = a company partner, Origin Terminal = a terminal
4. Fill: Cargo Type = **Container**, add container details
5. Save

### Step 2: Start Inquiry
1. Click "Start Inquiry" header button
2. **Expected**: Inquiry created with state = draft
3. **Expected**: Inquiry.request_id = the request

### Step 3: Accept Carrier Quote
1. Add a carrier response (e.g., DHL Freight, €850)
2. Click Accept
3. **Expected**: Inquiry state = accepted

### Step 4: Create & Accept Quote
1. From the inquiry, create Quote
2. **Expected**: Quote.request_id = original request
3. **Expected**: Quote.scene_id inherited from request
4. Set Carrier Cost, add Margin
5. Set Quote state to "accepted"
6. **Expected**: Transport Order auto-created
7. Verify Order:
   - [ ] order.scene_id = request.scene_id
   - [ ] order.quote_id = the quote
   - [ ] order.request_id = the request

### Step 5: Verify Fee Lines
1. Open the created Transport Order
2. Go to Fees tab
3. **Expected**: At least 1 fee line exists (carrier_cost)
4. **Expected**: If applicable, customer_charge fee line exists

## Checklist
- [ ] Request.scene_id = terminal_to_customer
- [ ] Inquiry → Quote → Order scene chain consistent
- [ ] Order.scene_id = terminal_to_customer (immutable)
- [ ] Fee line(s) exist
- [ ] Flow type = commercial matches scene
