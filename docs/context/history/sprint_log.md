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
