# 单据流转规则（Inventory Flow Rules）

## 1. 运输单据全生命周期

### 1.1 计划驱动型（场景 1/5）
```
transport.request 创建（计划驱动型）
  │  request_type = plan_driven
  │  指定目的地、货物信息
  ▼
排期日历拖拽调度
  │  左侧待排 → 拖拽到日期格 → 创建 pickup.plan 排期子单据
  │  每个柜/托件创建一条 pickup.plan 记录
  ▼
action_create_transport_order()（基于 pickup.plan）
  │  校验: cargo_type=container 必须有 container_line_ids
  │  校验: carrier_id 必须选择
  ▼
tlmp.transport.order 创建
  │  transport_type = port_to_warehouse / warehouse_transfer
  │  container 明细从 pickup.plan.container_line 复制
  ▼
运输执行 → 追踪 → POD 签收 → CMR → 结算
```

### 1.2 商务报价型（场景 2/3/4/6）
```
transport.request 创建（商务报价型）
  │  request_type = commercial
  │  指定客户、货物信息
  ▼
承运商询价（按路线报价，市场价，非公式计算）
  │  tlmp.transport.inquiry: draft → sent → responded → accepted/rejected
  ▼
客户报价（在承运商报价上加价）
  │  tlmp.transport.quote: draft → sent → accepted → (auto create order)
  │  rejected → 退回 inquiry.sent → 重新询价
  │         → 客户或暂停需求
  │  cancelled → 归档
  ▼
tlmp.transport.order 创建（报价接受时自动触发）
  ▼
运输执行 → 追踪 → POD → CMR → 结算
```

### 1.3 空柜调拨（场景 8）
```
container.service.request 创建
  │  request_type = depot_to_warehouse / warehouse_to_depot
  │  container_master_id 引用全局柜档案
  ▼
action_confirm() → state = confirmed
  ▼
action_create_transport_order()
  ▼
tlmp.transport.order 创建
  │  transport_type 由 request_type 映射
  ▼
运输执行
```

## 2. 跨模块单据流

### 2.1 TMS → WMS 信号联动
```
pickup.plan.is_bonded_transfer = True
  │  仅发送信号，不携带库存数据
  ▼
wd_bonded_wms 接收信号：
  │  入仓 → 保税账册核增
  │  出仓 → 保税账册核减
  │  调拨 → 跨仓账册流转
```
- TMS 绝不持有保税库存数据
- TMS 不做任何库存增减操作

 
 ### 2.2 双 Transport Request 体系
 
 TMS 系统存在两类对等的 transport.request，分别来自两个业务部门：
 
 ```
      IFFM 部门（进口货代）                 TMS 部门（运输物流）
   import.pickup.requirement           tlmp.transport.request
   （进口到港触发）                      （客户委托/运营手动创建）
           │                                      │
           │  pickup_scene:                       │  request_type:
           │    to_our_warehouse                  │    plan_driven → 排期调度
           │    to_customer_address               │    commercial  → 询价报价
           │    customer_self_pickup              │
           │                                      │  destination_type:
           │  容器: container_lines               │    warehouse
           │  （from waybill）                     │    warehouse_transfer
           │                                      │    customer
           │  状态: draft→submitted→planned→      │    self_pickup
           │        completed / cancelled          │
           │                                      │  货物: cargo_type + 明细
           │                                      │  （手动/request录入）
           │                                      │
           │                                      │  状态: draft→confirmed→cancelled
           │                                      │
           └─────────→  pickup.plan  ←────────────┘
                     （统一排期调度子单据）
                         │
                         ↓
                   transport.order
 ```
 
 两个 transport.request 的结构对等关系：
 
 | 维度 | import.pickup.requirement | tlmp.transport.request |
 |------|--------------------------|------------------------|
 | 触发方式 | waybill（进口提单）触发 | 客户委托 / 运营手动创建 |
 | 场景字段 | pickup_scene（3选1） | request_type + destination_type |
 | 仓库场景 | warehouse_id + warehouse_contact_id | warehouse_id（stock.warehouse） |
 | 客户地址 | delivery_city/street/contact/phone | partner_id（res.partner 地址） |
 | 自提 | self_pickup_contact_id/phone | 无（Sprint3补充） |
 | 集装箱 | container_lines（pickup.container.line） | 无（Sprint3补充→pickup.plan） |
 | 托件货物 | 无 | pallet_count/package_count/weight/volume |
 | 状态机 | 5状态（draft→submitted→planned→completed→cancelled） | 3状态（draft→confirmed→cancelled） |
 | 模块归属 | wd_iffm | wd_tlms |
 | 下游 | pickup.plan（source_type=iff） | pickup.plan（transport_request_id） |
 
 ### 2.3 IFFM ↔ TMS 引用流
 
 ```
 import.pickup.requirement  ──只读引用──→  pickup.plan
 （wd_iffm）                 Reference字段       （wd_tlms）
      │                                              │
      │ pickup_scene → destination_type               │ transport_request_id
      │ container_lines → container_line_ids          │ （Sprint3 强化）
      │ terminal/warehouse/address→目标字段            │
      │ source_type='iff', 所有明细 readonly            │
      │                                                │
      禁止反向修改 IFFM                                  │
 ```
 
 **跨模块引用约束**:
 - `pickup.plan.iff_requirement_ref` = Reference 字段指向 `import.pickup.requirement`（无硬 depends）
 - `pickup.plan.transport_request_id` = Many2one 指向 `tlmp.transport.request`（同模块）
 - IFFM 来源的 pickup.plan 所有明细字段 readonly
 - TMS 绝不反向修改 IFFM 任何数据
 

## 3. 禁止的操作路径

### 3.1 绝对禁止
- 不通过 pickup.plan 直接创建 transport.order
- 不通过单据直接修改库存/运输状态
- 不修改 IFFM、wd_bonded_wms 的数据
- 不在视图层/JS/Controller 中写业务逻辑
- 不在 pickup.plan 上添加财务/费用字段

### 3.2 允许的操作路径
- 通过 action button 触发模型层方法
- 通过 Odoo 标准 ORM CRUD
- 通过 @api.constrains 做数据完整性校验
- 通过 write() 拦截做写保护

## 4. 八场景 → 流程映射速查表

| 场景 | 流程类型 | 排期日历 | 询价报价 | 运输订单 |
|------|---------|---------|---------|---------|
| 1. Terminal → 我方仓库 | 计划驱动 | ✅ 本迭代 | ❌ | action_create |
| 2. Terminal → 客户地址 | 商务报价 | ❌ | ✅ | auto (报价确认) |
| 3. 仓库 → 客户地址 | 商务报价 | ❌ | ✅ | auto |
| 4. 客户A → 客户B | 商务报价 | ❌ | ✅ | auto |
| 5. 仓库A → B (调拨) | 计划驱动 | ✅ 本迭代 | ❌ | action_create |
| 6. 客户 → 仓库 (退货) | 商务报价 | ❌ | ✅ | auto |
| 7. 柜到仓换柜 | 柜级标记 | — | — | 字段扩展 |
| 8. Depot ↔ 仓库 (空柜) | 计划驱动 | ❌ | ❌ | action_create |
