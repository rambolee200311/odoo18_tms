# Transport Scenario Catalog
> Sprint41 Business Scenario Validation — Contract Document
> Version: 1.0 | Last Updated: 2026-07-29

## 8-Scenario Mapping Matrix

| Scene | Business Name | Trigger | Flow Type | Entry Doc | Expected Behavior | Model Chain | BAT | Manual |
|-------|--------------|---------|-----------|-----------|------------------|-------------|-----|--------|
| S1 | Terminal → Warehouse | Container arrival at port | plan_driven | Pickup Plan | Container picked up from terminal, delivered to warehouse | Request → Schedule → Pickup Plan → Order → Event → Billing | ✅ | ✅ |
| S2 | Terminal → Customer | Container arrival at port | commercial | Inquiry → Quote | Container delivered from terminal to customer address | Request → Inquiry → Quote → Order → Billing | ❌ | ✅ |
| S3 | Warehouse → Customer | Customer order fulfillment | commercial | Inquiry → Quote | Goods from warehouse to customer | Request → Inquiry → Quote → Order → Billing | ❌ | ✅ |
| S4 | Customer → Customer | Cross-dock / direct ship | commercial | Inquiry → Quote | Goods from customer A to customer B | Request → Inquiry → Quote → Order → Billing | ❌ | ✅ |
| S5 | Warehouse Transfer | Inventory relocation | plan_driven | Pickup Plan | Goods moved between warehouses (bonded transfer) | Request → Schedule → Pickup Plan → Order → Event → Billing | ✅ | ✅ |
| S6 | Customer Return | Return logistics | commercial | Inquiry → Quote | Goods picked up from customer, returned to warehouse | Request → Inquiry → Quote → Order → Billing | ✅ | ✅ |
| S7 | Container Swap | Container exchange after discharge | N/A | Field Extension | Swap container at depot after discharge | Order container_line.needs_swap = True | ❌ | ✅ |
| S8 | Empty Container Move | Depot ↔ Warehouse empty move | plan_driven | Container Service Request | Empty container picked from depot to warehouse or vice versa | Container Service Req → Order → Event | ✅ | ✅ |

## Scene Details

### S1: Terminal → Warehouse
- **Flow**: Plan-Driven
- **Entry**: Pickup Plan (from Schedule Calendar)
- **Request**: request_type=plan_driven, destination_type=warehouse
- **Scene expected**: terminal_to_warehouse
- **Key Verification**: Pickup Plan → Order scene_id chain, allocation exists

### S2: Terminal → Customer
- **Flow**: Commercial
- **Entry**: Inquiry → Quote
- **Request**: request_type=commercial, destination_type=customer
- **Scene expected**: terminal_to_customer
- **Key Verification**: Quote → Order auto-create, scene sync, fee.line exists

### S3: Warehouse → Customer
- **Flow**: Commercial
- **Entry**: Inquiry → Quote
- **Request**: request_type=commercial, destination_type=customer
- **Scene expected**: warehouse_to_customer

### S4: Customer → Customer
- **Flow**: Commercial
- **Entry**: Inquiry → Quote
- **Request**: request_type=commercial, destination_type=customer
- **Scene expected**: customer_to_customer

### S5: Warehouse Transfer
- **Flow**: Plan-Driven
- **Entry**: Pickup Plan
- **Request**: request_type=plan_driven, destination_type=warehouse_transfer
- **Scene expected**: warehouse_transfer
- **Key Verification**: bonded_transfer flag, container handling, cost allocation

### S6: Customer Return
- **Flow**: Commercial
- **Entry**: Inquiry → Quote
- **Request**: request_type=commercial, destination_type=warehouse
- **Scene expected**: customer_return
- **Key Verification**: Quote → Order auto-create, fee.line carrier_cost + customer_charge

### S7: Container Swap
- **Flow**: N/A (field extension)
- **Entry**: N/A — order-level field
- **Key Verification**: needs_swap flag on container_line, swap_location recorded

### S8: Empty Container Move
- **Flow**: Plan-Driven (via Container Service Request)
- **Entry**: Container Service Request
- **Key Verification**: container.service.request → Order, scene_id preserved, no Request chain

## Change Policy
- Sprint42+ functional changes must update this catalog
- New scenarios require new intent + catalog update
