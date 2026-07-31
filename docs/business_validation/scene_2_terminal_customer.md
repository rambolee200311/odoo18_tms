# Scene 2: Terminal → Customer（商务报价链路）

> 前置条件请先完成 [common_pre_check.md](common_pre_check.md) 全部检查项。

---

## Prerequisites

| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: terminal_to_customer | [ ] | Transport → Configuration → Transport Scenes |
| Customer partner | [ ] | Contacts |
| Carrier partner | [ ] | Contacts |
| Terminal partner | [ ] | Contacts |

---

## Step-by-Step Operation

### Step 2.1: Create Transport Request

1. Transport Requests → Create
2. Fill fields:
   - **Request Type** = Commercial
   - **Transport Scene** = Terminal → Customer
   - **Destination** = Terminal / Depot to Customer（由 scene 推导，但当前仍需手动选）
   - **Cargo Type** = Container
3. **Customer** = select a customer partner
4. **Origin Terminal** = select a terminal partner
5. **Delivery Address** = fill delivery address
6. Save
7. Expected: state=Draft, request_type=commercial, scene_id is NOT set yet (set by Inquiry)

### Step 2.2: Start Inquiry

1. Click **Start Inquiry** button
2. Expected: Inquiry created, state=Draft, inquiry.scene_id = terminal_to_customer
3. Verify: `request.scene_id` now equals `terminal_to_customer`

### Step 2.3: Accept Carrier Response

1. In Inquiry, add carrier response fields (Carrier, Total Amount)
2. Click **Accept**
3. Expected: Inquiry state = Accepted

### Step 2.4: Create and Accept Quote

1. From the Inquiry → Click **Create Quote**
2. Set **Carrier Cost**, **Margin**
3. Set Quote state to **Accepted**
4. Expected: Transport Order auto-created
5. Verify: `order.scene_id` = terminal_to_customer

### Step 2.5: Verify Fee Lines

1. Open Order → **Fees** tab
2. Expected: carrier_cost fee line exists
3. Verify: fee line amounts match Inquiry/Quote

---

## Failure Handling

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Scene field not visible | Missing ACL / view bug | Check common_pre_check.md |
| Inquiry/Quote buttons missing | request_type=commercial required | Verify request_type setting |
| Scene chain broken | scene_id not inherited | Record as blocking bug |

---

## Issues Found

### 本轮修复项（从 Scene 1 继承的全局修复，Scene 2 直接受益）

| Bug ID | Description | Severity | Root Cause | Fix Scope | Status |
|--------|-------------|----------|-----------|-----------|--------|
| C-001 | 8 大场景数据未预置 | blocking | `transport_scene_data.xml` 未注册 manifest | 已加入 manifest | fixed |
| C-002 | Configuration 菜单无 Transport Scenes | minor | 菜单条目缺失 | 新增 3 个菜单 | fixed |
| C-003 | 场景模型无 ACL | blocking | Sprint17 遗漏 | 新增 21 行 ACL | fixed |
| C-011 | `transport_scene_views.xml` 未注册 manifest | blocking | Sprint17 遗漏 | 已加入 manifest | fixed |

### 本轮发现

| Bug ID | Step | Description | Severity | Root Cause | Fix Scope | Status |
|--------|------|-------------|----------|-----------|-----------|--------|
| | | | | | | |

---

## Fix Record

| Bug ID | Root Cause | Fix Summary | Re-verified | Status |
|--------|-----------|-------------|-------------|--------|
| C-001~C-003, C-011 | 全局修复（参见 common_pre_check.md） | 全局修复 | ✅ | fixed |

---

## Final Result
- **Manual**: ⏳ PENDING
- **Executor**:
- **Date**:
- **Environment**:
- **Context Version**: 1.0.78

---

*在 common_pre_check.md 中标记的全局共性问题不再重复记录，仅记录 Scene 2 特有的发现。*


---

## 地址架构验证（Sprint44/45）

**场景**: S2 Terminal → Customer | **code**: terminal_to_customer

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **terminal_to_customer** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：terminal (选 terminal_id 自动填充 origin 地址) | 地址字段自动填充 | [ ] |
| A.3 | 终点：customer (选 partner_id 自动填充 destination 地址) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Commercial → Inquiry → Quote → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
