# Decision Note — 决策笔记

## Sprint1: pickup.plan 提货需求基础底座

**契约**: INT-TMS-SPRINT1-001
**时间**: 2026-07-21

---

### 决策1：destination_type 字段可见性修正

**背景**: 现有视图 `destination_type` 被设置为 `invisible="1"`，用户无法手动选择目的地类型。

**决策**: 将 `destination_type` 改为可见必选字段，放置在Base Info区域的 `cargo_type` 之后。

**依据**: 
- 需求文档明确四种目的地场景由用户选择（仓库/调拨/客户/自提）
- 下游按钮(action_create_transport_request vs action_open_schedule)依赖此字段
- IFFM导入自动填充，manual创建需手动选择

**影响**: 表单布局更直观，用户操作路径清晰，无双关性。

---

### 决策2：destination_type 控制 terminal_id 显隐范围

**决策**: `terminal_id`（起点码头/货站）仅在 `warehouse` 和 `customer` 场景显示。

**依据**:
- 调拨场景(warehouse_transfer)起点是source_warehouse，不需要terminal
- 自提场景(self_pickup)客户自行处理起点端，不涉及terminal
- 场景1(Terminal→仓库)和场景2(Terminal→客户)需要terminal作为运输起点

---

### 决策3：新增3个约束校验

| 约束 | 触发条件 | 说明 |
|------|---------|------|
| `_check_partner_required` | customer / self_pickup | 客户地址类目的地必须关联客户 |
| `_check_warehouse_required` | warehouse / warehouse_transfer | 入仓目的地必须指定仓库 |
| `_check_source_warehouse_required` | warehouse_transfer | 调拨必须指定发货仓 |

**依据**: 确保数据完整性，防止下游流程因缺少必填字段报错。

---

### 决策4：表单布局重组

将 `partner_id` 从 `Flow` 标签页移至主表单 `Destination` 组，确保客户选择和地址信息始终可见。

**理由**: partner_id 是业务核心字段（客户是谁决定报价流程），不应埋在二级标签页。

---

### 决策5：cargo_type 加入列表/搜索视图

在列表视图和搜索过滤器中增加 cargo_type 维度，方便运营按货物类型筛选。

---

### 前置决策（继承已有）

| 决策 | 来源 | 说明 |
|------|------|------|
| 流程严格二分 | 需求分析.md | 计划驱动型 vs 商务报价型 |
| 柜/托不混合 | 详细设计.md | 同一需求不混装，数据差异大 |
| IFFM来源只读 | 详细设计.md | `container_number/type/weight/bl_number/seal_number` 只读 |
| 保税调拨强制勾选 | 详细设计.md | 出/入仓任一方为保税仓时强制勾选 |
