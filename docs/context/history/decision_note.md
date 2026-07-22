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


---

## Sprint2: schedule.plan.schedule 日历拖拽排期系统

**契约**: INT-TMS-SPRINT2-001
**时间**: 2026-07-21

---

### 决策1：新建 schedule.plan.schedule 独立排期模型

**决策**: 创建全新的 `schedule.plan.schedule` 模型，而非复用现有的 `container.transport.plan`。

**依据**:
- 现有 `container.transport.plan` 仅支持集装箱（耦合 `bl.container`），不支持托/件货型
- 新模型直接链接 `pickup.plan`，原生支持 cargo_type 双货型
- 新模型含完整的 state 状态机（draft/scheduled/completed/cancelled）
- 实现与 `pickup.plan.scheduled_date` 的双向同步，保持向后兼容

**影响**: 现有 `container.transport.plan` 保持不变，两种排期模型可共存。

---

### 决策2：防重叠使用 SQL UNIQUE 约束 + 业务逻辑双层保护

**决策**: `UNIQUE(container_line_id, scheduled_date)` SQL约束 + `api_create_schedule` 中前置查询双重保护。

**依据**:
- SQL 约束保证数据库层绝对不重复
- API 层前置查询可给出更友好的错误提示
- 对 pallet 类型不设约束（一个计划多个柜/托件可排不同日期）

---

### 决策3：状态回写 pickup.plan.scheduled_date

**决策**: 创建/更新/删除 `schedule.plan.schedule` 时自动同步 `pickup.plan.scheduled_date`。

**依据**:
- 保持与现有 Controller v1 API 的向后兼容
- 当所有排期被取消或删除时，自动清空 scheduled_date
- 由 `create()` / `write()` / `unlink()` 覆盖处理

---

### 决策4：v2 API 使用 JSON 类型路由以适配前端拖拽

**决策**: 新增 v2 API 端点使用 `type='json'`，与现有 v1 的 `type='http'` 区分。

**依据**:
- JSON API 更适配前端 OWL 组件的 ORM 调用模式
- v1 保持不变以保证旧有前端兼容
- v2 内部调用 `schedule.plan.schedule` 模型的方法

---

### 决策5：认知资产补齐

**决策**: 补齐 architecture/ 和 business/ 缺失的 4 个认知资产文件。

**依据**:
- 认知控制工程要求 8 步加载全部到位
- 之前 Sprint1 的缺失已在 Sprint2 补齐
- 8 步认知加载已全部可执行


---

### 决策6（流程架构重校正）：transport.request 为全流程统一入口

**背景**: 原设计文档将 `pickup.plan` 作为全流程顶层入口，导致 Sprint1+Sprint2 代码基于错误前提开发。

**决策**: 将 `tlmp.transport.request` 修正为全流程统一入口。

**正确流程**:
| 流程类型 | 链路 |
|---------|------|
| 计划驱动型 | transport.request → Schedule → pickup.plan → transport.order |
| 商务报价型 | transport.request → inquiry → quote → transport.order |

**影响**:
- `pickup.plan` 从顶层入口降级为计划驱动型排期子单据
- `transport.request` 需要增加 request_type 字段区分计划驱动/商务报价
- 所有菜单、按钮、API 需要反向调整
- `pickup.plan.action_create_transport_request()` 方法逻辑反转
- Sprint3 将基于修正后的架构进行开发
