## Prerequisites

### Required Data
| Item | Status | How to Verify |
|------|--------|--------------|
| Scene: terminal_to_warehouse | [ ] | Transport → Configuration → Transport Scenes |
| Company Partner (customer/carrier) | [ ] | Contacts |
| Warehouse (destination) | [ ] | Inventory -> Warehouses |
| Terminal Partner (origin) | [ ] | Contacts |

### If Missing
| Item | How to Create |
|------|--------------|
| Scene | Upgrade module (-u wd_tlms) or create manually |
| Partners | Create in Contacts |
| Warehouses | Create in Inventory configuration |

### Verification Checklist
- [ ] Scene terminal_to_warehouse exists
- [ ] Transport type port_to_warehouse exists
- [ ] Warehouse exists (e.g. Rotterdam Warehouse)
- [ ] Terminal partner exists
- [ ] User has required permissions

---

## Step-by-Step Operation

### Step 1.1: Create Transport Request（场景驱动）
1. Transport Requests -> Create
2. **Transport Scene** = Terminal → Warehouse
   （场景第一驱动，自动匹配 origin_type=terminal, destination_type=warehouse）
3. 表单自动显示 **Origin Address** / **Destination Address** 两个组
4. **Origin Terminal** = select a terminal partner
   → origin_street / origin_zip / origin_city 自动填充
5. **Destination Warehouse** = select a warehouse
   → destination_street / destination_zip / destination_city 自动填充
6. **Cargo Lines** 页签新增至少 1 行，填写：
   - Description（必填）
   - Container No.
   - Container Type（默认 20GP）
   - BL Number
   （港到提柜场景要求 Request 必须先有提单号和柜号，才能单独/批量排期）
7. Save
8. Expected: state=Draft, scene_id=terminal_to_warehouse,
   origin/destination 地址已自动填充（用户可编辑），
   cargo_line_ids ≥ 1 且含 container_no + bl_number

### Step 1.2: Open Schedule Calendar
1. Click **Go to Schedule** header button
2. Expected: Calendar opens, request in left panel

### Step 1.3: Schedule via Drag-and-Drop
1. Drag request to a date cell
2. Expected: Pickup Plan created, appears in Scheduling tab

### Step 1.4: Verify Scene Chain
1. Open Pickup Plan: scene_id = terminal_to_warehouse (readonly, inherited)
2. Open Request: request.scene_id = terminal_to_warehouse

### Step 1.5: Create Transport Order
1. In Pickup Plan click **Create Transport Order**
2. Check Order: scene_id = terminal_to_warehouse, transport_type auto-filled, carrier auto-filled (if set)

### Step 1.6: Verify Order Snapshot
1. Order.scene_id is readonly (not editable), copy=False (not copied on duplicate)

---

## Failure Handling

| Symptom | Likely Cause | Action |
|---------|-------------|--------|
| Field or button missing | View bug / missing permission | Record bug -> Codex fixes |
| Cannot select value | Missing prerequisite | Check Prerequisites section |
| Save fails | Validation error | Follow error message |
| Scene chain broken | scene_id not inherited | Record as blocking bug |

---

## Issues Found (during manual verification)

| Bug ID | Scene | Step | Description | Severity | Root Cause | Fix Scope | Status |
|--------|-------|------|-------------|----------|-----------|-----------|--------|
| SD42-S1-001 | S1 | 1.1 | Transport Scene 下拉为空，无记录可选 | blocking | `data/transport_scene_data.xml` 未在 `__manifest__.py` 注册，数据从未加载 | manifest 添加 data 引用 | fixed |
| SD42-S1-002 | S1 | 1.1 | Configuration 菜单无 Transport Scenes 入口 | minor | 菜单未添加 | tlmp_menus.xml 新增 3 个配置菜单 | fixed |
| SD42-S1-003 | S1 | global | 三个场景模型无 ACL 权限定义 | blocking | Sprint17 创建后遗漏 | ir.model.access.csv 新增 21 行 ACL | fixed |
| SD42-S1-004 | S1 | 1.2 | Go to Schedule 500 — `pickup_schedule_templates.xml` 未在 manifest 注册 | blocking | 视图文件遗漏 | 加入 manifest 并修复加载顺序 | fixed |
| SD42-S1-005 | S1 | 1.2 | OWL 日历组件注册失败：`@odoo-module` 缺少 `export class`、blank line、精确路径 | blocking | JS 模块结构不完整；manifest 用 glob 模式代替精确路径 | 按 `addons/transport` 参考实现重写 JS；manifest 用精确路径 | fixed |
| SD42-S1-006 | S1 | 1.2 | Go to Schedule 每次点击重复创建 Pickup Plan | blocking | 未检查幂等性 | 已添加复用逻辑：按 `transport_request_id` 或名称查找 | fixed |
| SD42-S1-007 | S1 | 1.1 | Pickup Plan 创建失败 — warehouse 约束被触发 | blocking | `pickup_plan_fix.py` 无 `transport_request_id` 时自动创建 Transport Request，未传 warehouse_id | action_go_schedule 创建 Plan 时传入 `transport_request_id` 阻止自动创建 | fixed |
| SD42-S1-008 | S1 | 1.2 | Shell 删数据无效 — 事务未 commit | blocking | 未调用 `env.cr.commit()`，会话结束时回滚 | 写操作后必须 commit；新会话 `search_count` 验证 | fixed |
| SD42-S1-009 | S1 | 1.4 | Pickup Plan 上游字段可编辑/可删除 | blocking | 无快照保护，来源 Request 的数据（起点/终点/柜明细）可随意修改 | 已记录 AD-005；Sprint44+ 实施只读约束 + 禁止删除 | deferred |
| SD42-S1-010 | S1 | 1.5 | carrier_id domain `is_carrier=True` 导致无可选项 | blocker | 无 partner 设置 is_carrier 标记 | 移除 domain，允许所有 partner 可选 | fixed |
| SD42-S1-011 | S1 | 1.5 | world.depot.charge.item 无 ACL | blocker | worlddepot 模块未正确加载 ACL，导致 Create Transport Order 时报权限错误 | 添加 ACL（所有用户读权限） | fixed |
| SD47-S1-001 | S1 | 1.1 | request 2069 未创建 Cargo Line，container_no / bl_number 为空，无法进入柜排期 | blocking | 文档 Step 1.1 未包含柜明细步骤，人工验证时漏填 | Step 1.1 补充 Cargo Lines 步骤；2069 补 Cargo Line 后复验 | fixed |
| SD47-S1-002 | S1 | 1.3 | 拖拽后 scheduled_date 已写入（2069 → plan 719 = 2026-07-30），但日历不显示该计划 | blocking | JS 用 `toISOString()` 生成日期键，UTC+8 时区使 7/30 落在查询区间外；月末 `< end` 又排除最后一天 | JS 改为本地日期 `formatLocalDate()`，月份区间改为 `[当月1日, 下月1日)`；升级 1.0.91 | fixed |
| SD47-S1-003 | S1 | 1.5 | Order 1578 Customer 被写成 Carrier（Azure Interior），且 scene_id=None | blocking | `action_create_transport_order()` 把 `partner_id` 写成 `carrier_id` 兜底；港到仓 Request 无客户时订单客户变成承运商；plan 链路也未复制 scene_id | Customer 改为 Request/Plan 客户，无客户时用公司伙伴兜底；订单创建补齐 scene_id；1578 已回填 scene + customer；升级 1.0.93 | fixed |
| SD47-S1-004 | S1 | 1.5 | Order 1578 表单看不到起始地点 | blocking | 订单表单地址组 `invisible="not scene_id"`，而该订单 scene_id 为空；`pickup_location_id/delivery_location_id/place_of_departure/place_of_destination` 未在表单显示 | 表单显示 scene_id、起终点地址、pickup/delivery location、place 文本；生成订单时自动填充 place_of_departure/destination；1578 已回填；升级 1.0.93 | fixed |

## Fix Record

| Bug ID | Root Cause | Fix Summary | Status |
|--------|-----------|-------------|--------|
| SD42-S1-001 | data/transport_scene_data.xml 未在 manifest 引用 | 已加入 manifest data 列表 | fixed |
| SD42-S1-002 | Configuration 下无 Transport Scenes 菜单 | 已添加 menu_tlmp_transport_scene + event_type + scene_event | fixed |
| SD42-S1-003 | tlmp.transport.scene / event.type / scene.event 无 ACL | 已添加 21 行 ACL（含 cargo.line / flow.type / destination.type / cargo.rule） | fixed |
| SD42-S1-004 | pickup_schedule_templates.xml 未注册 manifest | 加入 manifest + 修复加载顺序 | fixed |
| SD42-S1-005 | JS 模块结构不完整 | 按 addons/transport 参考实现重写：export class + blank line + 精确路径 | fixed |
| SD42-S1-006 | action_go_schedule 无幂等检查 | 新增 existing_plan 搜索，按 transport_request_id 或名称复用 | fixed |
| SD42-S1-007 | pickup_plan_fix.py 自动创建 Request 无 warehouse_id | action_go_schedule 传入 transport_request_id 阻止自动创建 | fixed |
| SD42-S1-008 | Shell 事务未 commit | 写操作后 env.cr.commit()；新会话 search_count 验证 | fixed |
| SD42-S1-009 | 无快照保护（AD-005） | 所有上游字段只读 + 已排期禁止删除 — Sprint44+ 实施 | deferred |
| SD42-S1-010 | carrier_id 设 domain `is_carrier=True` | 移除 domain，所有 partner 可选 | fixed |
| SD42-S1-011 | world.depot.charge.item 无 ACL | 添加所有用户读权限 | fixed |
| SD47-S1-001 | 文档未写 Cargo Lines 前置步骤，验证时未填柜号/BL | Step 1.1 补充 Description / Container No. / Container Type / BL Number；2069 补 Cargo Line（abc123 / def456） | fixed |
| SD47-S1-002 | 日历日期用 UTC ISO 字符串，时区偏移导致计划不在查询区间 | `pickup_schedule.js` 改用本地日期；XML-RPC 升级 1.0.91 通过，区间查询可返回 plan 719 | fixed（待 UI 复验） |
| SD47-S1-003 | plan 链路将 carrier 写进 Customer 且漏 scene_id | Customer 改从 Request/Plan 客户取，缺省用公司伙伴；补 scene_id；1578 数据回填 | fixed（待 UI 复验） |
| SD47-S1-004 | 订单表单 scene 缺失时隐藏地址组，起终点字段未展示 | 表单改为 scene 或地址存在即显示，并新增 pickup/delivery location 与 place 文本；生成订单时自动填充 | fixed（待 UI 复验） |

## Verification Progress

| Step | Description | Result | Notes |
|------|-------------|--------|-------|
| 1.1-S47 | Create Transport Request（复验 request 2069） | ✅ PASS | scene_id / 起终点 / 地址自动填充通过；Cargo Line 已补（container_no=abc123, bl_number=def456） |
| 1.2-S47 | Open Schedule Calendar | ✅ PASS | 日历正常打开，左侧待排期计划显示 |
| 1.3-S47 | Schedule via Drag-and-Drop | ⏳ PARTIAL | 拖拽写入 scheduled_date 成功；日历不显示（SD47-S1-002），已修复并升级 1.0.91，待 UI 复验 |
| 1.4-S47 | Verify Scene Chain | ✅ PASS | request.scene_id / plan.scene_id = terminal_to_warehouse |
| 1.5-S47 | Create Transport Order | ⏳ PARTIAL | Order 1578 可创建；customer=carrier、scene=None、起始地点不可见（SD47-S1-003/004），已修复并回填 1578，升级 1.0.93，待 UI 复验 |
| 1.1 | Create Transport Request | ✅ PASS | scene=terminal_to_warehouse, state=draft |
| 1.2 | Open Schedule Calendar | ✅ PASS | 日历显示正确，Plan 可拖拽到日期上排期 |
| 1.3 | Schedule via Drag-and-Drop | ✅ PASS | Plan 可拖拽到日历日期，scheduled_date 写入成功 |
| 1.4 | Verify Scene Chain | ✅ PASS | scene_id terminal_to_warehouse 贯穿 request → plan; 但 plan 可编辑字段过多 |
| 1.5 | Create Transport Order | ✅ PASS | carrier_id 选择后正常创建 Transport Order |
| 1.6 | Verify Order Snapshot | ✅ PASS | order snapshot 已创建，scene_id 保持 terminal_to_warehouse |

## Final Result
- **Manual**: ⏳ pending（Sprint47 复验中；1.1 / 1.2 / 1.4 PASS；1.3 / 1.5 已修复待 UI 复验）
- **Executor**: lijianqiang
- **Date**: 2026-07-31
- **Environment**: Odoo 18 dev
- **Context Version**: 1.0.93

### 验证说明
- 本轮发现的 11 个问题中，10 个已修复并复验通过
- 1 个延期（SD42-S1-009: Pickup Plan 快照保护 → Sprint44+）
- 全部步骤从创建 Request → 排期 → 创建 Order 链路完整
- Sprint47 复验：SD47-S1-001 已修复（2069 补 Cargo Line）；SD47-S1-002 已修复（日历日期时区问题），待 UI 复验 1.3


---

## 地址架构验证（Sprint44/45）

**场景**: S1 Terminal → Warehouse | **code**: terminal_to_warehouse

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **terminal_to_warehouse** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：terminal (选 terminal_id 自动填充 origin 地址) | street/zip/city 已自动填充（2069） | [x] |
| A.3 | 终点：warehouse (选 warehouse_id 自动填充 destination 地址) | street/zip/city 已自动填充（2069） | [x] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Plan → Go to Schedule → Plan → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

> 注：2069 的 origin_state_id / destination_state_id / country_id 为空，原因是 Terminal1 / SPN 主数据未配置省州和国家，不属于代码缺陷；补齐主数据后地址组可完整自动填充。

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| SD47-S1-001 | 1.1 | request 2069 无 Cargo Line（container_no / bl_number 为空） | blocking | fixed |
| SD47-S1-002 | 1.3 | 拖拽写 scheduled_date 成功但日历不显示（时区日期偏移） | blocking | fixed（待 UI 复验） |
