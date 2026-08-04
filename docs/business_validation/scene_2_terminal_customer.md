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

### Step 2.1: Create Transport Request（场景驱动）

1. Transport Requests → Create
2. **Transport Scene** = Terminal → Customer
   （场景第一驱动，自动匹配 origin_type=terminal, destination_type=customer）
3. 表单自动显示 **Origin Address** / **Destination Address** 两个组
4. **Origin Terminal** = select a terminal partner
   → origin_street / origin_zip / origin_city 自动填充
5. 目的地二选一：
   - 有客户主档：**Customer** = select a customer partner
     → destination_street / destination_zip / destination_city 自动填充
   - 无客户主档：直接在 **Destination Address** 手工填写 street / zip / city
     （3PL 受货主委托送货，目的地是地址，不强制建立 Partner 档案）
6. Save
7. Expected: state=Draft, scene_id=terminal_to_customer,
   origin/destination 地址已自动填充（用户可编辑）

### Step 2.2: Start Carrier Inquiry

1. Click **Start Inquiry** button
2. Expected: Inquiry created, state=Draft，Carrier 为空（由 3PL 后续选择）
3. Inquiry 显示 Request 的场景/起终点/Cargo（related 投影）
4. Click **Send to Carrier** → state=Sent（向承运商询价）

### Step 2.3: Carrier Response & Select Carrier

1. 承运商回复：在 Inquiry 设置 **Carrier**（partner_id）和承运商报价（Cargo Lines 单价，合计即 Carrier Quote）
2. Click **Record Response** → state=Responded
3. 3PL 内部选定承运商：Click **Select Carrier** → state=Accepted
4. 注意：这里是「承运商选定」，不是客户接受

### Step 2.4: Create Customer Quote

1. From Inquiry → Click **Create Customer Quote**
2. Expected: Quote 自动创建，request_id/inquiry_id 已带出，Carrier Cost=承运商报价，Customer Price=Carrier Cost + Margin
3. Set **Margin**，Customer Price 自动计算
4. Quote state=Draft，partner_id=货主/客户

### Step 2.5: Customer Accept Quote → Order

1. Click **Send to Customer** → Quote state=Sent
2. 客户接受：Click **Accept Quote** → state=Accepted，自动创建 Transport Order
3. Verify: `order.scene_id` = terminal_to_customer
4. Verify: `order.carrier_id` = Inquiry 选定的承运商，`order.partner_id` = Quote 客户

### Step 2.6: Verify Fee Lines

1. Open Order → **Fees** tab
2. Expected: carrier_cost fee line（应付承运商）与 customer_charge fee line（应收客户）存在
3. Verify: fee line amounts match Inquiry Carrier Quote / Quote Customer Price

---

## Sprint47 验证进度

| Step | Description | Result | Notes |
|------|-------------|--------|-------|
| 2.1-S47 | Create Transport Request（request 2074） | ✅ PASS | scene=terminal_to_customer，origin 地址自动填充，无 Partner 手工填目的地地址（city 缺失与 legacy destination_type 不一致按用户决定忽略） |
| 2.2-S47 | Start Inquiry（inquiry 690） | ⏳ PARTIAL | Inquiry 已创建；carrier 默认成 ljq、cargo 信息缺失、表单排版乱（SD47-S2-002/003/004），已修复并升级 1.0.96，待 UI 复验 |
| 2.3-S47 | Carrier Response & Select Carrier（inquiry 690） | ✅ PASS（数据核验） | Carrier=Gemini Furniture，inquiry line 单价 380，total=380，state=accepted |
| 2.4-S47 | Create Customer Quote（quote 535） | ✅ PASS（数据核验） | margin_rate=0.208333（UI 显示 20.83%），Customer Price=480（carrier 380 + margin 100）；cargo line 描述 `ewew - eewdd232323 - dfadfd432223`；Fee Line 可新增保存（默认 source_type=commercial），6 条 Charge Item 下拉齐全 |

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
| SD47-S2-001 | 2.1 | 无客户主档的目的地无法保存，customer 场景强制 partner_id | blocking | 校验要求 customer/self_pickup 必须有 partner_id，与 3PL 按货主指令送临时地址的业务不符 | 校验放宽为 partner_id 或 destination_street 二选一；无 Partner 时手工填目的地地址；Quote→Order 的 carrier 不再取 customer | fixed |
| SD47-S2-002 | 2.2 | Start Inquiry 后 Carrier 自动填成当前用户 ljq | blocking | `action_start_inquiry` 用 `self.carrier_id or env.user.partner_id` 兜底，Request 无承运商时把当前用户当承运商 | 去掉 env.user 兜底，仅取 request.carrier_id；Carrier 字段改为非必填，由用户在 Inquiry 中选择 | fixed |
| SD47-S2-003 | 2.2 | Inquiry 无 cargo 信息（summary 空、无行明细） | blocking | 只复制 request.cargo_description，Request 只有 Cargo Lines 时 Inquiry 为空 | 从 Cargo Lines 生成 summary 和 inquiry line，重量/体积缺省从行汇总 | fixed |
| SD47-S2-004 | 2.2 | Inquiry 表单排版混乱 | minor | 地址组嵌套在 Route & Cargo 内，deprecated 文本字段仍显示 | 重排表单：Inquiry Info / Schedule / Origin+Destination Address / Cargo / Cargo Lines / Notes | fixed |
| SD47-S2-005 | 2.1 | request 2074 destination_city 为空、legacy destination_type=warehouse 与场景不一致 | minor | 手工录入未填 city；记录创建于场景 onchange 生效前 | 用户决定忽略，不阻塞验证 | accepted |
| SD47-S2-006 | 2.3-2.5 | 3PL 流程错误：Inquiry “Accept” 被当作客户接受，缺少“Create Customer Quote”按钮，Quote 客户价未按 Carrier Cost + Margin 计算 | blocking | 领域模型把承运商报价与客户报价混为同一动作 | Inquiry 按钮改为 Select Carrier；新增 Create Customer Quote；Quote total=Carrier Cost+Margin；客户接受 Quote 才建 Order | fixed |
| SD47-S2-007 | 2.4 | Quote 535 Margin Rate 显示 2631.58%，且无 cargo line | blocking | margin_rate 存为百分比数值又被 percentage widget 乘 100；`action_create_quote` 未复制 Request 柜明细 | margin_rate 改为销售利润率小数（margin/customer price）；Create Customer Quote 复制 cargo lines；535 已回填 | fixed |
| SD47-S2-008 | 2.4 | Quote cargo line 描述未含柜号/BL，Fee Lines 只读不可编辑 | minor | 创建 Quote 时描述只取 cargo.description；fee_line_ids 视图 readonly | cargo line 描述补 Container No. + BL；Fee Lines 放开可编辑（editable bottom）；535 描述已回填 | fixed |
| SD47-S2-009 | 2.6 | Fee Line 的 Fee Type 下拉无记录 | blocking | `world.depot.charge.item` 主档为空 | 预置 6 条运输费用档案：Transportation Fee / Fuel Surcharge / Terminal Handling / Container Pickup / Customs Clearance / Documentation；版本 1.0.100 | fixed |
| SD47-S2-010 | 2.6 | Quote 535 新增 Fee Line 报错：Source Type 必填未设置 | blocking | `transport.fee.line.source_type` required 无默认值，Quote 表单新增行时未自动带值 | source_type 默认值改为 commercial；版本 1.0.101 | fixed |
| SD47-S2-011 | 2.4 | Quote 535 表头 Customer Price（480）与 Fee Lines 合计（550）不一致 | blocking | `tlmp.transport.quote.total_amount` 只按 carrier_cost+margin 计算，忽略 fee_line_ids | total_amount 改为按 customer_charge 费用行合计（无费用行时回退 carrier+margin）；Fee Lines 列表显示 quantity；存量数据已重算回填；版本 1.0.102 | fixed |
| SD47-S2-012 | 2.4-2.6 | 已接受 Quote 的费用行仍可编辑/删除，535 定价被改乱（margin 100 / rate 500% / price 20）；Order 无费用行 | blocking | fee_line_ids 无状态锁；margin_amount 仍为手填，未随费用行推导；_auto_create_order 在 accept 后向 quote 建费用行但未写入 order | fee_line_ids 非 draft 只读 + ORM 删除/写入拦截；margin_amount 改为按 customer fee 合计自动推导；accept 后 quote 费用行复制到 Order（source_order_id）；535/1579 已修复并回填；版本 1.0.103 | fixed |
| SD47-S2-013 | 2.5 | request 2074 已有 accepted quote/order 仍可 Start Inquiry；Create Order 按钮藏在 Inquiry & Quote 页且 quote 无 transport_order_id 无法打开 | blocking | action_start_inquiry 无状态拦截；quote 缺 transport_order_id 关联；建单按钮在 notebook 内不易发现 | 新增 has_accepted_quote；Start Inquiry 非 draft 隐藏 + ORM 拦截；quote 新增 transport_order_id（accept 自动回写，535 已回填 1579）；Create Order 移至表单 header 并直达已有 Order；版本 1.0.104 | fixed |

---

## Fix Record

| Bug ID | Root Cause | Fix Summary | Re-verified | Status |
|--------|-----------|-------------|-------------|--------|
| C-001~C-003, C-011 | 全局修复（参见 common_pre_check.md） | 全局修复 | ✅ | fixed |
| SD47-S2-001 | 目的地被当作客户主档强制必填 | 校验放宽：有 Partner 自动带地址，无 Partner 手工填 Destination Address；同步修复 Quote→Order carrier 复用 customer 的问题 | 待 UI 复验 | fixed |
| SD47-S2-002 | Inquiry carrier 用 env.user 兜底 | 仅取 request.carrier_id，Carrier 字段非必填，由用户在 Inquiry 选择 | 待 UI 复验 | fixed |
| SD47-S2-003 | Inquiry 只复制 cargo_description | 从 Request Cargo Lines 生成 cargo_summary + inquiry line + 重量/体积 | 待 UI 复验 | fixed |
| SD47-S2-004 | 表单地址组嵌套、旧字段未隐藏 | 重排 Inquiry 表单为清晰分组 | 待 UI 复验 | fixed |
| SD47-S2-005 | 2074 目的地 city 缺失、legacy destination_type 未同步 | 用户决定忽略 | 已确认 | accepted |
| SD47-S2-006 | 承运商报价与客户报价混为同一动作 | Select Carrier → Create Customer Quote → 客户 Accept Quote 才建 Order；Customer Price=Carrier Cost+Margin | 数据复验通过（2.4） | fixed |
| SD47-S2-007 | margin_rate 双重百分比 + Quote 无 cargo line | margin_rate=100/480=20.83%（小数存储）；Create Quote 复制 cargo lines；535 已回填 | 数据复验通过（2.4） | fixed |
| SD47-S2-008 | Quote cargo 描述缺柜号/BL；Fee Lines 只读 | cargo line 描述补 Container No.+BL；Fee Lines 可编辑；535 描述已回填 | 数据复验通过（2.4） | fixed |
| SD47-S2-009 | Charge Item 主档为空 | 预置 6 条运输费用档案（data/transport_charge_item_data.xml），noupdate 防重复 | 数据复验通过（2.4） | fixed |
| SD47-S2-010 | Fee Line source_type 无默认值 | 默认 commercial；XML-RPC 升级 1.0.101 通过 | 数据复验通过（2.4） | fixed |
| SD47-S2-011 | total_amount 忽略 fee_line_ids | total_amount = customer_charge 费用行合计；无费用行回退 carrier+margin；view 显示 quantity；1.0.102 XML-RPC 升级通过并重算回填 | 数据复验通过（2.4） | fixed |
| SD47-S2-012 | 费用行无状态锁 + margin 未推导 | 非 draft 费用行只读并拦截删除/写入；margin_amount=total-carrier；accept 复制费用行到 Order；1.0.103 升级通过；535/1579 回填复核通过 | 数据复验通过（2.4-2.6） | fixed |
| SD47-S2-013 | 商务流状态缺失拦截 + 建单入口难找 | has_accepted_quote 隐藏/拦截 Start Inquiry；quote.transport_order_id 回填；Create Order 移到 header 直达 Order；1.0.104 升级通过；2074/535/1579 复核通过 | 数据复验通过（2.5） | fixed |

---

## Final Result
- **Manual**: ⏳ PENDING
- **Executor**: lijianqiang
- **Date**: 2026-08-03
- **Environment**: Odoo 18 dev
- **Context Version**: 1.0.96

---

*在 common_pre_check.md 中标记的全局共性问题不再重复记录，仅记录 Scene 2 特有的发现。*


---

## 地址架构验证（Sprint44/45）

**场景**: S2 Terminal → Customer | **code**: terminal_to_customer

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **terminal_to_customer** | Origin Address / Destination Address 两个组显示 | [x] |
| A.2 | 起点：terminal (选 terminal_id 自动填充 origin 地址) | 地址字段自动填充 | [x] |
| A.3 | 终点：有 partner 选 partner 自动填充；无 partner 手工填写 Destination Address | 两种方式都能保存 | [x] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Commercial → Inquiry → Quote → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| SD47-S2-001 | 2.1 | 无客户主档的目的地无法保存 | blocking | fixed（待 UI 复验） |
| SD47-S2-002 | 2.2 | Inquiry Carrier 默认成 ljq | blocking | fixed（待 UI 复验） |
| SD47-S2-003 | 2.2 | Inquiry 无 cargo 信息 | blocking | fixed（待 UI 复验） |
| SD47-S2-004 | 2.2 | Inquiry 表单排版混乱 | minor | fixed（待 UI 复验） |
| SD47-S2-005 | 2.1 | 2074 city 缺失 / legacy destination_type 不一致 | minor | accepted |
| SD47-S2-006 | 2.3-2.5 | 3PL 流程缺失客户接受环节 | blocking | fixed（待 UI 复验） |
| SD47-S2-007 | 2.4 | Margin Rate 显示错误 + Quote 无 cargo line | blocking | fixed（待 UI 复验） |
| SD47-S2-008 | 2.4 | Quote cargo 描述缺柜号/BL；Fee Lines 只读 | minor | fixed（待 UI 复验） |
| SD47-S2-009 | 2.6 | Fee Type 下拉无记录 | blocking | fixed（待 UI 复验） |
| SD47-S2-010 | 2.6 | 保存 Fee Line 报 Source Type 必填 | blocking | fixed（待 UI 复验） |
