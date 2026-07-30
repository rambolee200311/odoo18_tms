# Architecture Debt Registry

> 记录已知架构债务，后续通过 Sprint Intent Contract 清理。

---

## AD-001: 去除 destination_type，统一由 scene 推导

**发现时间**: 2026-07-30
**发现场景**: Sprint42 手工验证 Scene 1，Go to Schedule 报错时暴露

### 问题描述

`tlmp.transport.scene`（Sprint17 引入）定义了完整的运输场景语义，但 `destination_type` 字段（Sprint1 引入）仍然存在于多个模型中作为并行分流字段。两者之间存在冗余。

### Scene → destination_type 映射

| Scene | code | 对应 destination_type | 确定性 |
|-------|------|---------------------|--------|
| Terminal → Warehouse | terminal_to_warehouse | warehouse | 100% |
| Terminal → Customer | terminal_to_customer | customer | 100% |
| Warehouse → Customer | warehouse_to_customer | customer | 100% |
| Customer A → Customer B | customer_to_customer | customer | 100% |
| Warehouse ↔ Warehouse | warehouse_transfer | warehouse_transfer | 100% |
| Customer → Warehouse (Return) | customer_to_warehouse | customer | 100% |
| Container Swap | container_swap | 不固定 | ❌ 需根据换柜位置 |
| Empty Depo ↔ Warehouse | empty_depot | warehouse | 100% |

**结论**: 7/8 场景可完全推导，仅有 `container_swap` 需额外逻辑。

### 注意事项

1. `container_swap` 不能简单映射 —— 换柜的目标仓库取决于实际业务，可能需要用户手动确认或走独立逻辑
2. 替换过程中，`container_swap` 应保留独立的 `destination_type` 处理路径，或新增字段由用户指定目标仓库
3. `destination_type` 不等于 `customer` 的语义 —— 部分场景（如 `customer_to_warehouse`）虽有 `destination_type=customer`，但实际是回程运输，不应与 `terminal_to_customer` 混用
4. 清理应分步执行，每替换一处就跑一遍测试回归：

| Scene | 隐含 destination_type |
|---|---|
| terminal_to_warehouse | warehouse |
| warehouse_transfer | warehouse_transfer |
| terminal_to_customer | customer |
| warehouse_to_customer | customer |
| customer_to_customer | customer |
| customer_to_warehouse | customer |
| container_swap | 取决于实际换柜位置（不固定） |
| empty_depot | warehouse（空柜回堆场） |

### 影响范围

`destination_type` 在以下位置使用：

**模型字段**:
- `tlmp.transport.request.destination_type` — 1处
- `pickup.plan.destination_type` — 1处（继承自 request 或手动设置）

**校验逻辑**:
- `pickup_plan.py`: `_check_destination()` — warehouse/warehouse_transfer 需 warehouse_id
- `pickup_plan.py`: `_check_partner_when_customer()` — customer/self_pickup 需 partner_id
- `transport_request.py`: `_check_destination_fields()` — 同上
- `pickup_plan.py`: clone 时拷贝 destination_type/warehouse_id

**视图**:
- `transport_request_views.xml`: 表单/列表/搜索视图
- `pickup_plan_views.xml`: 表单/列表/搜索视图
- `transport_order_views.xml`: order 表单中显示

### 建议方案

1. 新增 `tlmp.transport.scene` → `destination_type` 映射方法（在 scene 模型或 service 层）
2. 逐个替换 `if destination_type == 'warehouse'` 为 `if scene.code == 'terminal_to_warehouse'`
3. 移除 `destination_type` 字段（可能需保留计算字段兼容旧视图）
4. 清理 5 处 `@api.constrains` 校验逻辑

### 关联问题

`pickup_plan_fix.py` 中 create 覆盖在无 `transport_request_id` 时自动创建 Transport Request，导致字段冗余问题被放大（一次 create 触发两套校验逻辑）。

### 建议 Sprint

Sprint44+ 架构清理 Sprint

### 决策（2026-07-30 Sprint42 验证确认）

`destination_type` 是 Sprint1 遗产，Sprint17 引入 scene 后未清理。Sprint42 验证中确认：
- destination_type 的功能完全可被 scene.code 推导替代
- 代码中 5+ 处 `@api.constrains` 和流程分流逻辑依赖 destination_type
- **清理策略**: 逐项替换 `if destination_type == 'xxx'` 为 `if scene.code == 'yyy'`，最后删除字段

### 清理步骤

1. 在 `tlmp.transport.scene` 新增 `get_destination_type()` 映射方法
2. 逐个替换模型中的 `destination_type` 引用为 scene 推导
3. 替换 5 处 `@api.constrains` 校验逻辑
4. 更新视图（移除 destination_type、替换为 scene）
5. 数据库迁移：旧记录中的 destination_type 从 scene 回填
6. 删除 `destination_type` 字段定义
7. 全量测试回归

### 影响范围

- 4 个模型字段（transport.request / pickup.plan / transport.order）
- 5 处 `@api.constrains`
- 多个视图（tree/form/search）
- 流程分流逻辑（action_go_schedule / action_create_transport_order）

### 状态

- [ ] Intent 契约已创建
- [ ] 清理完成
- [ ] 旧字段已标记 deprecated
- [ ] 视图已更新
- [ ] 测试已更新

---

## AD-002: Transport Request 与 Pickup Plan 的数据一致性保护

**发现时间**: 2026-07-30
**发现场景**: Sprint42 手工验证 Scene 1，Step 1.2 Go to Schedule 完成后暴露

### 问题描述

当前没有任何约束阻止用户在创建 Pickup Plan 后修改或删除 Transport Request：

1. **删除 Request** — `pickup.plan.transport_request_id` 默认 `ondelete=set null`，删 Request 后 Plan 关联丢失
2. **修改 Request** — 修改 cargo lines/terminal/warehouse 后，已创建的 Plan 数据不同步，两者不一致

### 影响范围

- `tlmp.transport.request` (任何 `scheduled` 状态的 request)
- `pickup.plan` (通过 `transport_request_id` 关联)
- 涉及字段：cargo_line_ids, terminal_id, warehouse_id, destination_type, cargo_type

### 建议方案

**选项 A: 软锁** — Plan 创建后 Request 进入 `scheduled` 状态，禁止 `draft` 状态的变更操作
```python
# transport_request.py
@api.constrains('state')
def _check_scheduled_lock(self):
    for r in self:
        if r.state == 'scheduled' and r.pickup_plan_ids:
            # 禁止删除/修改 cargo lines
```

**选项 B: 硬约束** — `@api.ondelete` 阻止删除，`@api.constrains` 阻止修改关键字段
```python
# pickup_plan.py
transport_request_id = fields.Many2one('tlmp.transport.request', ondelete='restrict')
```

**选项 C: 不做处理** — 当前行为可删可改，留到 Sprint44+ 统一处理

### 建议 Sprint

Sprint44+（架构清理 Sprint）

### 状态

- [ ] Intent 契约已创建
- [ ] 约束已添加
- [ ] 测试已更新
- [ ] 文档已更新

---

## AD-003: 批量排期支持

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 1 验证，用户需要同时对多个 Pickup Plan 进行排期

### 问题描述

当前 OWL 排期组件只支持单个拖拽排期。用户有多个 Request/Plan 时，需要逐一操作，效率低。

### 需求

- 左侧列表支持多选
- 选中多个 Plan 后，点击/拖拽到一个日期 → 批量设置 `scheduled_date`
- 操作后刷新日历和左侧列表

### 状态

- [ ] 功能已实现
- [ ] 测试已更新

---

## AD-004: 排期页面承运商分配

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 1 验证，拖拽排期后无承运商入口

### 问题描述

`pickup.plan` 有 `carrier_id` 字段，但 OWL 排期页面未暴露该字段。用户排期后需要去标准表单页面设置承运商，流程断裂。

### 需求

- OWL 排期组件左侧列表中显示承运商下拉
- 或排期后日历卡片上显示承运商信息
- 或点击日历卡片快速编辑承运商

### 状态

- [ ] 功能已实现
- [ ] 测试已更新

---

## AD-005: Pickup Plan 字段可编辑性控制

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 1 验证，Step 1.4 scene 链验证通过后发现

### 问题描述

Pickup Plan 创建后，起点（terminal_id）、终点（warehouse_id）、柜明细（container_line_ids）等字段仍可编辑。
Plan 本质是 Request 在排期时刻的快照，不应允许随意修改。

当前可编辑的字段：
- `terminal_id`（起点码头/货站）
- `warehouse_id`（终点仓库）
- `source_warehouse_id`（始发仓库）
- `container_line_ids`（柜明细）
- `cargo_type`、`destination_type`（货型、目的地类型）

### 建议方案

**选项 A: 创建后锁字段**
```python
@api.constrains('state')
def _check_snapshot_immutable(self):
    if self.state != 'draft' and any(field in self._fields for field in SNAPSHOT_FIELDS):
        raise ValidationError('Plan 已排期，不可修改')
```

**选项 B: 只读视图**
在 form 视图中根据 `scheduled_date` 字段设置 `readonly`：
```xml
<field name="terminal_id" readonly="scheduled_date != False"/>
```

### 建议 Sprint

Sprint44+（架构清理）

### 状态

- [ ] 决策已确定
- [ ] 约束已添加
- [ ] 视图已更新
- [ ] 测试已更新

---

## AD-006: Transport Request 表单字段显隐应基于 scene 而非 destination_type

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 2 验证，Step 2.1 表单填写

### 问题

Transport Request 表单的字段显隐逻辑使用 `destination_type` 控制：

```xml
<field name="warehouse_id" invisible="destination_type not in ('warehouse', 'warehouse_transfer')"/>
```

当 `scene = terminal_to_customer` 时：
- 应隐藏 `warehouse_id`（送货到客户）
- 应显示详细地址字段（street/zip/city/state/country/remark/timeslot）

但当前模型只有 `delivery_address`（单文本字段），缺少结构化地址字段。

### 建议

1. 将显隐逻辑从 `destination_type` 改为 `scene_id.code`
2. 新增详细地址字段（street/zip/city/state_id/country_id/remark/timeslot）
3. 旧字段 `delivery_address` 标记 deprecate

### 状态

- [ ] 字段显隐已改为 scene 驱动
- [ ] 详细地址字段已添加
- [ ] 视图已更新

---

## AD-007: 地址输入与 Google Maps API 集成

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 2 验证，Step 2.1 填写送货地址

### 需求

用户需要一个地址输入框：
1. 粘贴完整地址文本
2. 自动调用 Google Maps Geocoding API 解析
3. 填充结构化字段：street / zip / city / state / country

### 当前状态

- 参考文件已存放至 `addons/wd_tlms/docs/reference/address.py`（不参与模块加载，仅供 Google Maps API 参考）
- 同目录下 `terminal.py` 为终端模型参考
- 结构化字段完整：street / postcode / city / state / country / latlng / latitude / longitude
- Google Maps API 集成：`button_fetch_google_maps_details()`
- 支持 warehouse/terminal 联动填充
- API key 通过系统参数 `base_geolocalize.google_map_api_key` 配置

### 待办

1. `delivery_address` 单文本字段标记 deprecated
2. 新增 `delivery_remark` / `delivery_timeslot`
3. Transport Request 表单通过 Many2one 关联地址模型
4. 配置视图和 ACL

### 状态

- [x] 模型已部署（address.py）
- [ ] 视图已更新
- [ ] ACL 已配置
- [ ] 前端 widget 已开发
- [ ] API key 已配置

---

## AD-008: 场景模型缺起终点类型，表单无法自动适配地址

**发现时间**: 2026-07-30
**发现场景**: Sprint42 Scene 2 验证，Step 2.1 填写送货地址

### 核心问题

`tlmp.transport.scene` 只定义了 `scene_type`（plan_driven / commercial / mixed），没有定义：
- **起点类型**（origin_type）：terminal / warehouse / customer
- **终点类型**（destination_type）：warehouse / customer

导致表单无法自动适配起终点地址字段。

### 当前状态

| 数据 | 方式 |
|------|------|
| 起点 | 散落在 terminal_id / source_warehouse_id 等字段 |
| 终点 | 散落在 warehouse_id / delivery_address（单文本）等字段 |
| 地址 | 仅有 delivery_address（单文本），无结构化地址 |
| 显隐逻辑 | 已改为 scene_code 驱动，但字段本身仍是零散的 |

### 目标架构

```
Scene
  ├── origin_type (terminal / warehouse / source_partner)
  └── destination_type (customer / warehouse)

Request / Order
  ├── origin_address_id → structured fields (street/zip/city/state/country)
  │     ├── auto-fill from terminal partner (if origin_type=terminal)
  │     ├── auto-fill from source warehouse (if origin_type=warehouse)
  │     └── manual input fallback
  └── destination_address_id
        ├── auto-fill from warehouse (if destination_type=warehouse)
        ├── auto-fill from customer partner (if destination_type=customer)
        └── manual input fallback
```

### 8 场景起终点类型映射（草案）

| Scene | origin_type | destination_type |
|-------|-------------|-----------------|
| terminal_to_warehouse | terminal | warehouse |
| terminal_to_customer | terminal | customer |
| warehouse_to_customer | warehouse | customer |
| customer_to_customer | customer | customer |
| warehouse_transfer | warehouse | warehouse |
| customer_to_warehouse | customer | warehouse |
| container_swap | terminal | warehouse |
| empty_depot | depot | warehouse |

### 依赖

- AD-001: destination_type 清理（本轮先新增 origin_type/destination_type，不清除旧字段）
- AD-006: 表单显隐 scene 驱动（已完成 scene_code 替换）
- AD-007: 地址输入与 Google Maps API（参考 docs/reference/address.py）

### 设计约束

1. 自动填充的地址**用户可编辑** — 即使是码头仓库的地址，自动填充后用户仍可修改
2. 自动填充是将 partner / warehouse 的地址数据一次复制到地址字段，不是关联引用
3. 目的：终端用户可能需要在自动填充的地址上微调（如添加具体门牌号、备注等）

### 建议 Sprint

Sprint44 — 场景驱动起终点地址架构

### 状态

- [ ] Scene 模型：origin_type / destination_type 已添加
- [ ] 8 场景预设数据已更新
- [ ] Request：起终点地址字段已添加
- [ ] Order：地址快照已添加
- [ ] 表单视图已重写（scene 驱动）
- [ ] 自动填充逻辑已实现
- [ ] Google Maps API 集成（可选）
- [ ] 旧 destination_type 已标记 deprecated
