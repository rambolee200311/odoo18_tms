## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: customer_return | [ ] | Transport → Configuration → Transport Scenes |
| Company Partner (customer) | [ ] | Contacts |
| Carrier Partner | [ ] | Contacts |
| Warehouse (return destination) | [ ] | Inventory -> Warehouses |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene customer_return exists
- [ ] Transport type reverse_logistics exists
- [ ] Customer and carrier partners exist
- [ ] Warehouse exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 6.1: Create Transport Request（场景驱动）
1. Transport Requests -> Create
2. **Transport Scene** = Customer → Warehouse (Return)（自动匹配 origin=customer, dest=warehouse）
3. **Customer** = select customer partner → origin 地址自动填充
4. **Destination Warehouse** = select warehouse → destination 地址自动填充
5. Save.
6. Expected: scene_id=customer_to_warehouse, origin/destination 地址已填充
2. Customer = select partner, Source Warehouse = select WH. Save.

### Step 6.2: Inquiry -> Quote
1. Start Inquiry -> accept carrier -> Create Quote with Carrier Cost + Margin
2. Expected: Quote created

### Step 6.3: Accept Quote -> Verify Fee Lines
1. Set Quote to Accepted. Open created Order -> Fees tab.
2. Expected: Order auto-created. Fee lines: carrier_cost + customer_charge

---

## Failure Handling

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Field or button missing | View bug / missing permission | Record bug -> Codex fixes |
| Cannot select value | Missing prerequisite | Check Prerequisites section |
| Save fails | Validation error | Follow error message |
| Scene chain broken | scene_id not inherited | Record as blocking bug |

---

## Issues Found
| Bug ID | Scene | Step | Description | Severity | Root Cause | Fix Scope | Commit | Status |
|--------|-------|------|-------------|----------|-----------|-----------|--------|--------|
| | | | | | | | | |

## Fix Record
| Bug ID | Root Cause | Fix Summary | Commit | Regression Test | Status |
|--------|-----------|-------------|--------|-----------------|--------|
| | | | | | |

## Final Result
- **Manual**: pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Executor**:
- **Date**:
- **Environment**:
- **Context Version**:


---

## 地址架构验证（Sprint44/45）

**场景**: S6 Customer Return | **code**: customer_to_warehouse

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **customer_to_warehouse** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：customer (选 partner_id 自动填充 origin 地址) | 地址字段自动填充 | [ ] |
| A.3 | 终点：warehouse (选 warehouse_id 自动填充) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Commercial → Inquiry → Quote → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
