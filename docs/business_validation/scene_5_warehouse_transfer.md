## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: warehouse_transfer | [ ] | Transport → Configuration → Transport Scenes |
| Warehouse A (source) | [ ] | Inventory -> Warehouses |
| Warehouse B (dest, diff from A) | [ ] | Inventory -> Warehouses |
| Carrier Partner | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene warehouse_transfer exists
- [ ] Transport type warehouse_transfer exists
- [ ] Two different warehouses exist
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 5.1: Create Transport Request（场景驱动）
1. Transport Requests -> Create
2. **Transport Scene** = Warehouse ↔ Warehouse（自动匹配 origin=warehouse, dest=warehouse）
3. **Source Warehouse** = select WH A → origin 地址自动填充
4. **Destination Warehouse** = select WH B（must differ from A）→ destination 地址自动填充
5. Save.
6. Expected: scene_id=warehouse_transfer, origin/destination 地址已填充

### Step 5.2: Check Bonded Transfer
1. If source/dest WH is bonded -> is_bonded_transfer must be True
2. Expected: Constraint enforced if bonded

### Step 5.3: Schedule -> Pickup Plan -> Order
1. Go to Schedule -> drag to date -> Pickup Plan created -> Create Transport Order
2. Expected: Order created. order.scene_id = warehouse_transfer

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

**场景**: S5 Warehouse ↔ Warehouse | **code**: warehouse_transfer

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **warehouse_transfer** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：warehouse (选 source_warehouse_id 自动填充) | 地址字段自动填充 | [ ] |
| A.3 | 终点：warehouse (选 warehouse_id 自动填充) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Plan → Go to Schedule → Plan → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
