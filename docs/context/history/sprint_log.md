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
