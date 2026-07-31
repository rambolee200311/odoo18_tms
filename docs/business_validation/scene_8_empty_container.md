## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: empty_depot | [ ] | Transport → Configuration → Transport Scenes |
| Container Master record | [ ] | Container -> Masters |
| Depot Partner | [ ] | Contacts |
| Warehouse | [ ] | Inventory -> Warehouses |
| Carrier Partner | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene empty_depot exists
- [ ] Container Master exists (e.g. MSCU1234567)
- [ ] Depot and warehouse exist
- [ ] Carrier partner exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 8.1: Create Transport Request（场景驱动）
1. Transport Requests -> Create
2. **Transport Scene** = Empty Depot ↔ Warehouse（自动匹配 origin=depot, dest=warehouse）
3. **Origin Depot** = select depot/terminal partner → origin 地址自动填充
4. **Destination Warehouse** = select warehouse → destination 地址自动填充
5. Save.
6. Expected: scene_id=empty_depot, origin/destination 地址已填充
2. Fill Container, Depot, Warehouse, Carrier, Planned Date. Save.

### Step 8.2: Confirm -> Create Transport Order
1. Click Confirm, then Create Dispatch Order
2. Expected: Transport Order created

### Step 8.3: Verify Scene
1. Open created Order -> check scene_id
2. Expected: order.scene_id = empty_depot (from container service, NOT transport.request)

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

**场景**: S8 Empty Depot | **code**: empty_depot

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **empty_depot** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：depot (选 terminal/depot partner 自动填充) | 地址字段自动填充 | [ ] |
| A.3 | 终点：warehouse (选 warehouse_id 自动填充) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Plan → Go to Schedule → Plan → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
