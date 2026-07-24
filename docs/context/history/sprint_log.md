# Sprint Log — 迭代日志

## Sprint1: pickup.plan 提货需求基础底座

**时间**: 2026-07-21
**契约**: INT-TMS-SPRINT1-001
**状态**: 已完成

---

### 迭代目标

完整实现 pickup.plan 提货需求核心模型、字段体系、货物类型双分支（集装箱/托件）、
目的地类型分支，搭建TMS所有运输场景的底层需求基座，支撑计划驱动、商务报价双流程。

### 完成成果

#### 模型层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `models/pickup_plan.py` | 优化 | 新增3个约束校验：partner_id必填、warehouse_id必填、source_warehouse_id必填 |
| `pickup.plan` 主模型 | 已有 | 完整字段体系：cargo_type(双分支)、destination_type(4场景)、IFFM只读、保税调拨 |
| `pickup.plan.container.line` | 已有 | 集装箱明细子模型，含IFFM来源只保护 |

#### 视图层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `views/pickup_plan_views.xml` | 重写 | destination_type从隐藏改为可见、表单按场景动态布局优化、列表/搜索改进 |

**表单视图关键改进**：
1. `destination_type` 改为可见选择字段（4种目的地类型）
2. 表头按钮根据destination_type自动切换（计划驱动 vs 商务报价）
3. Destination组按场景动态显隐：terminal_id(仓库/客户)、双仓库(调拨)、partner_id+地址(客户/自提)
4. 列表视图新增cargo_type列
5. 搜索视图新增cargo_type筛选和warehouse_transfer筛选

#### 安全层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `security/ir.model.access.csv` | 已有 | pickup.plan + container_line 已配置 Manager(CRUD)/Operator(CRU)/all(只读) |

### 验收状态

| 规则 | 状态 | 说明 |
|------|------|------|
| 集装箱/托件双形态切换 | ✅ | cargo_type控制Containers与Cargo Details标签页互斥显隐 |
| 四种目的地场景字段展示 | ✅ | warehouse/warehouse_transfer/customer/self_pickup各场景正确 |
| IFFM导入来源只读 | ✅ | container_line明细字段 readonly when source_type='iff' |
| 调拨场景双仓库展示 | ✅ | warehouse_transfer时显示source+destination双仓库+保税标记 |
| 无违规代码、越界功能 | ✅ | 未触碰forbidden范围，未修改Odoo底层、未添加财务字段 |
| 迭代日志同步 | ✅ | 本文件 + decision_note.md 已更新 |

### 问题与决策

- destination_type 原视图设置为 `invisible="1"`，用户无法手动选择目的地类型。已修正为可见选择字段。
- 新增3个Python约束校验：partner_id(客户/自提必填)、warehouse_id(仓库/调拨必填)、source_warehouse_id(调拨必填)
- 调拨场景 dual-warehouse 展示逻辑正确：source_warehouse_id + warehouse_id + is_bonded_transfer
- `terminal_id` 仅在 warehouse/customer 场景显示（调拨和自提不涉及起点码头）


---

## Sprint2: schedule.plan.schedule 日历拖拽排期系统

**时间**: 2026-07-21
**契约**: INT-TMS-SPRINT2-001
**状态**: 已完成

### 迭代目标
完整实现 TMS 运输可视化日历拖拽排期系统，支持提货计划拖拽排班、时间段占用、排期状态管理。

### 完成成果

#### 模型层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `models/schedule_plan.py` | **新建** | `schedule.plan.schedule` 排期核心模型 |
| `models/pickup_plan.py` | **增量** | 仅新增 `schedule_ids` One2many 字段 |

**schedule.plan.schedule 模型字段体系**：
- 核心关联：`plan_id` → pickup.plan, `container_line_id` → container.line
- 排期字段：`scheduled_date`, `state`(draft/scheduled/completed/cancelled)
- Related 显示字段：cargo_type, destination_type, warehouse_id, container_number, pallet_count 等
- SQL 约束：`UNIQUE(container_line_id, scheduled_date)` 防重叠
- API 方法：`api_create_schedule`, `api_delete_schedule`, `api_get_schedules`, `api_get_unplanned`

#### 视图层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `views/schedule_calendar_views.xml` | **新建** | 日历视图 + 列表视图 + 表单视图 + 搜索视图 |

#### 控制器层

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `controllers/pickup_schedule.py` | **增量** | 新增 4 个 v2 API 端点 |

#### 认知资产补齐

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `architecture/module_map.md` | **新建** | 模块架构地图 |
| `architecture/dependency.yaml` | **新建** | 依赖与调用关系图 |
| `business/stock_rule.md` | **新建** | 运输业务铁律 |
| `business/inventory_flow.md` | **新建** | 单据流转规则 |

### 验收状态

| 规则 | 状态 | 说明 |
|------|------|------|
| 日历拖拽功能正常 | ✅ | schedule.plan.schedule 模型支撑 + v2 API |
| 时间段防重叠校验 | ✅ | SQL UNIQUE 约束 + 业务逻辑 |
| 所有货型可正常排期 | ✅ | 适配 container + pallet |
| 不破坏 Sprint1 存量代码 | ✅ | 仅增量添加，未改旧逻辑 |
| 架构分层、业务铁律合规 | ✅ | 视图仅UI控制，模型层做约束 |
| 认知资产同步更新 | ✅ | v1.0.3 + 4项架构/业务新增 |


## 架构修正 v1.0.4（业务流程重校正）

**时间**: 2026-07-21
**修正内容**: 流程入口从 `pickup.plan` 改为 `transport.request`

### 发现问题
原文档及代码中，`pickup.plan` 被设计为全流程顶层入口单据，
`transport.request` 仅作为商务报价流程的子步骤。
这与实际业务流程相反。

### 正确架构
```
计划驱动型（场景1/5/8）:
  transport.request → Schedule → pickup.plan → transport.order

商务报价型（场景2/3/4/6）:
  transport.request → inquiry → quote → transport.order
```

### 修正范围
- `transport.request` 为**全流程统一入口**，pickup.plan 降级为排期阶段创建的子单据
- 所有认知资产（business/stock_rule, inventory_flow, architecture/module_map, dependency, design/详细设计, requirement/需求分析, 一期完成）已同步修正


---

## Sprint4: transport.order 运输订单统一收敛闭环

**时间**: 2026-07-22
**契约**: INT-TMS-SPRINT4-001
**状态**: 已完成

### 迭代目标
搭建 transport.order 全局统一运输订单闭环，实现双链路统一落单收敛。

### 完成成果

#### 模型层
| 文件 | 变更 | 说明 |
|------|------|------|
| models/transport_order.py | 增强 | 新增 pickup_plan_id / source_type / _compute_source_type / _sync_upstream_status / create_from_pickup_plan |
| models/pickup_plan_fix.py | 修正 | action_create_transport_order 设置 pickup_plan_id |

#### 视图层
| 文件 | 变更 | 说明 |
|------|------|------|
| views/transport_order_views.xml | 重写 | 10 状态流转 + source_type badge + 上游溯源跳转 + 5 标签页 |

### 验收状态
- transport.order 双来源落单: ✅ source_type computed
- 计划链路: request → schedule → plan → order: ✅ pickup_plan_id 绑定
- 商务链路: request → inquiry → quote → order: ✅ quote._auto_create_order
- 上游溯源精准可跳转: ✅ 表单 Source Documents 组
- 状态流转正常 + 联动回写: ✅ 10 状态 + _sync_upstream_status
- 不破坏 S1/S2/S3 存量: ✅ 仅增量扩展


---

## Sprint5: 全局费用费率底层底座

**时间**: 2026-07-22
**契约**: INT-TMS-SPRINT5-001
**状态**: 已完成

### 迭代目标
搭建 TMS 全局统一费用/费率底层模型体系，为双链路提供计费底座。

### 完成成果
| 文件 | 变更 | 说明 |
|------|------|------|
| models/transport_fee_type.py | 新建 | FeeType 费用类型字典（5类 + code唯一） |
| models/transport_rate_base.py | 新建 | RateBase 费率底座（6种rate_type + valid_period） |
| models/transport_fee_line.py | 新建 | FeeLine 费用明细行（source_type 双链路 + qty x amount compute） |
| models/fee_base_inherit.py | 新建 | quote + order 增量挂载 fee_line_ids |
| views/transport_fee_views.xml | 新建 | FeeType/RateBase/FeeLine 全套视图 + window action |

### 验收状态
- 三层费用底座完整: ✅ FeeType + RateBase + FeeLine
- quote 挂载费用: ✅ fee_line_ids(source_quote_id)
- order 挂载费用: ✅ fee_line_ids(source_order_id)
- 双链路费用隔离: ✅ source_type = commercial / plan_driven
- 纯增量不破坏存量: ✅ 零侵入 S1-S4


---

## Sprint6: 费用模型重构 — fee_type 指向全局 charge.item + 双向计费

**时间**: 2026-07-22
**契约**: INT-TMS-SPRINT6-001
**状态**: 已完成

### 迭代目标
修正 Sprint5 费用底座架构：fee_type_id 从 TMS 自建 transport.fee.type 改为指向全局费用主数据 world.depot.charge.item，新增 party_type（customer_charge / carrier_cost）实现双向计费隔离。

### 完成成果
| 文件 | 变更 | 说明 |
|------|------|------|
| models/transport_fee_type.py | 移除 | 被 world.depot.charge.item 替代 |
| models/transport_fee_line.py | 重写 | fee_type_id → world.depot.charge.item; 新增 party_type / partner_id |
| models/transport_rate_base.py | 修正 | fee_type_id → world.depot.charge.item |
| views/transport_fee_views.xml | 重写 | 移除 fee.type 视图; fee.line 新增 party_type + partner_id 字段 |
| __manifest__.py | 修正 | depends 追加 worlddepot |
| forbidden_change.yaml | 追加 | soft_reference_allow 例外: 允许引用 charge.item |

### 验收状态
- fee_type_id 指向全局 charge.item: ✅ world.depot.charge.item
- party_type 双向区分: ✅ customer_charge / carrier_cost
- partner_id 对手方: ✅
- rate_base 同步修正: ✅
- worlddepot 基础依赖: ✅
- 不破坏 S1-S5: ✅ 纯重构 Sprint5 增量


---

## Sprint7: 商业报价流程完善 — inquiry→quote→order 全链路 + fee.line 集成

**时间**: 2026-07-22
**契约**: INT-TMS-SPRINT7-001
**状态**: 已完成

### 迭代目标
完善 commercial flow 全链路视图与业务逻辑：inquiry 完整表单、quote margin/cost 字段、accepted 后自动创建 fee.line。

### 完成成果
| 文件 | 变更 | 说明 |
|------|------|------|
| models/transport_quote.py | 增强 | +carrier_cost, margin_amount, margin_rate, fee_line_ids; +action_accept; _auto_create_order 创建2条 fee.line |
| views/transport_inquiry_views.xml | 重写 | 完整表单：request/partner/cargo/lines/total/state |
| views/transport_quote_views.xml | 重写 | 完整表单：request/inquiry/carrier_cost/margin/total + Fee Lines tab |

### 验收
- inquiry 表单完整可用: ✅ 所有字段 + 状态流转
- quote 表单完整可用: ✅ margin/cost + 状态流转
- quote accepted → fee.line: ✅ customer_charge + carrier_cost
- 不破坏 S1-S6: ✅ 纯增量


---

## Sprint8: 计划驱动链路端到端闭环 — Schedule→pickup.plan→order+fee

**时间**: 2026-07-22
**契约**: INT-TMS-SPRINT8-001
**状态**: 已完成

### 迭代目标
对标Sprint7商业报价链路，完善计划驱动链路闭环：transport.request → schedule.plan.schedule → pickup.plan → transport.order + fee.line。

### 完成成果
| 文件 | 变更 | 说明 |
|------|------|------|
| models/schedule_plan.py | 增量 | +pickup_plan_id（排期记录 → pickup.plan 关联） |
| models/pickup_plan_fix.py | 增量 | action_create_transport_order 创建后自动生成 fee.line (carrier_cost) |
| views/transport_request_views.xml | 增量 | Scheduling tab 新增 schedule.plan.schedule 子列表 |

### 技术约束新增
- forbidden_change.yaml 追加 controller_bypass 规则：禁止新增 Controller JSON 路由，前端统一走 orm.call
- Sprint8 零新增 Controller，所有交互通过模型方法 + JS orm.call 完成

### 验收
- schedule.plan.schedule 可关联 pickup.plan: ✅
- pickup.plan → order 自动创建 fee.line: ✅
- transport.request 可见 schedule 列表: ✅
- 不破坏 S1-S7: ✅

## Sprint16: 运输订单跟踪核心基座 — Transport Event + 异常 + 费用

**时间**: 2026-07-24
**契约**: INT-TMS-SPRINT16-001
**状态**: 已完成

### 迭代目标
搭建运输订单全生命周期跟踪系统核心基座：Transport Event 动态运输事件、运输异常闭环管理、途中额外费用台账、transport_order 增量扩展。

### 完成成果
- transport_order 增量扩展：transport_scene 8 场景枚举、tracking_state 6 态跟踪状态机、容器/地址字段
- Transport Event 动态运输事件：8 类型 + 3 层时间（planned/estimated/actual）+ 5 态事件状态 + 时序约束 + POD 附件强制
- Transport Exception 异常闭环：4 态生命周期（OPEN→PROCESSING→RESOLVED→CLOSED）+ 12 类型 + 归档前 CLOSED 强制
- Extra Charge 额外费用台账：9 费用类型 + 承担方 + 自动汇总
- 归档附件：DELIVERY_COMPLETED 强制 POD 附件上传
- context_loader.py v4：Profile 文件驱动、include/exclude/load_strategy、--profile/--skip-baseline CLI

### 关键决策
1. 运输事件禁止物理删除 → 逻辑作废（state=skipped/cancelled + reason 必填）
2. 异常强制闭环后归档 → action_close 校验所有 exception.state=CLOSED
3. 与原有 transport_type/state 共存，不破坏存量逻辑

### 验收
- verify.py 8/8: ✅ PASS
- odoo_check: ✅ PASS
- test_runner: 93 tests, 23 tracking tests PASS, 1 pre-existing pickup_plan ERROR

## Sprint17: 运输场景/事件类型/场景路径可配置化管理

**时间**: 2026-07-24
**契约**: INT-TMS-SPRINT17-001
**状态**: 已完成

### 迭代目标
将运输场景和事件类型从硬编码 Selection 改造为独立档案模型，新增场景-事件路径映射，后台可配置管理且无需改代码。

### 完成成果
- 3 个新档案模型：tlmp.transport.scene（8 场景预设）、tlmp.transport.event.type（8 事件预设）、tlmp.transport.scene.event（路径映射）
- transport_order.transport_scene Selection → scene_id Many2one
- transport_event.event_type Selection → event_type_id Many2one
- TransportEvent.BASE_EVENT_ORDER 硬编码 → 基于 scene.event 路径配置驱动时序约束
- transport_request 新增 scene_id，plan→order 和 quote→order 全链路自动拷贝
- Configuration 菜单下 3 个子菜单管理档案

### 关键决策
1. 场景/事件配置化：新增档案只需在 model 中添加记录，无需改 Python 代码
2. 时序约束配置驱动：_check_sequential_order 改读 tlmp.transport.scene.event 路径记录
3. scene_id 全链路贯穿：request → plan/quote → order，确保 Event 在正确场景路径下约束
4. 存量兼容：新增 Many2one 字段，旧值通过预设 data xml 的 code 匹配映射

### 验收
- verify.py 8/8: ✅ PASS
- odoo_check: ✅ PASS

## Sprint18: MRN/T1 单据号记录 + 产品 ADR 属性扩展（松耦合）

**时间**: 2026-07-24
**契约**: INT-TMS-SPRINT18-001
**状态**: 已完成

### 迭代目标
运输跟踪 P0 合规模块松耦合实现：MRN/T1 仅记录单据号，ADR 扩展产品属性。

### 完成成果
- transport_order 新增 5 个简单字段：mrn_code / t1_ref / dg_file_ref / adr_quantity / adr_weight
- product_adr.py: product.product ADR 属性扩展（un_number / class / packing_group / is_dangerous_good）
- product_adr_views.xml: 产品表单 ADR 标签页（仅 manager 组可见）

### 关键决策
1. MRN/T1 不建档不绑定，松耦合记录单据号
2. ADR 不建独立模型，扩展产品属性
3. 存量字段全部保留不动

### 验收
- verify.py 8/8: ✅ PASS
- odoo_check: ✅ PASS

## Sprint20: transport_request/order Cargo Line + scene cargo rule + CMR 联动

**时间**: 2026-07-24
**契约**: INT-TMS-SPRINT20-001
**状态**: 已完成

### 迭代目标
为 transport_request/order 新增运输货物明细子表（Cargo Line），通过 tlmp.transport.scene.cargo.rule 配置模型决定场景货物来源策略，CMR 生成时自动读取运输货物快照。

### 完成成果
- Cargo Line 模型完整（description/commodity/qty/packages/weight/volume/container/source_type）
- Scene Cargo Rule 配置模型（8 场景预设）
- request → order → CMR 全链路贯穿
- CMR 防重复 + source_cargo_line_id 追溯

### 验收
- verify.py 8/8: ✅ PASS
- odoo_check: ✅ PASS
