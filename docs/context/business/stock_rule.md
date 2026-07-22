# 运输业务铁律（Stock & Transport Rules）

## 1. 流程铁律
### 1.1 双流程严格分离
```
计划驱动型（内部调度）:    场景1(Terminal→仓库), 场景5(仓库调拨), 场景8(空柜调拨)
  链路: transport.request → Schedule → pickup.plan → transport.order

商务报价型（对外接单）:    场景2(T→客户), 场景3(仓库→客户), 场景4(客户A→B), 场景6(退货)
  链路: transport.request → inquiry → quote → transport.order
```
- 两种流程不可混用，由 `pickup.plan.destination_type` 决定
- 计划驱动型不进询价报价流程；商务报价型不进排期日历

### 1.2 柜/托不混合
- 同一 `pickup.plan` 不可同时包含集装箱和托盘/件货
- 由 `cargo_type` 字段严格区分：container / pallet
- 集装箱需求在 `container_line_ids` 维护，托/件需求在 `pallet_count`/`package_count`/`cargo_weight` 等字段维护

### 1.3 单据驱动原则
- 所有运输/库存变更必须基于单据发起
- `pickup.plan` 是运输场景的底层需求单据
- 禁止不通过单据直接修改收货/发货/库存数据

## 2. 排期铁律
### 2.1 排期范围
- 排期日历（Schedule Calendar）仅用于计划驱动型场景：
  - 场景1: Terminal → 我方仓库
  - 场景5: 我方仓库 A → 我方仓库 B（调拨）
- 商务报价型场景不进日历排期

### 2.2 排期粒度
- 集装箱需求：每个柜作为独立调度单元
- 托/件需求：整个需求作为调度单元
- 同一日期的同一仓库不能排入同一柜两次

### 2.3 防重叠
- 同一集装箱不可在相同日期内被排期两次
- 排期日期不允许为空（正值日期）

## 3. 保税铁律
### 3.1 保税调拨强制勾选
- 调拨场景（warehouse_transfer）且出/入仓任一方为保税仓时，`is_bonded_transfer` 必须为 True
- 由 `_check_bonded_transfer()` 约束校验强制执行

### 3.2 TMS 不持有保税库存数据
- 库存增减、账册额度、B3/T1 申报全部由 WMS 模块执行
- TMS 只做运输轨迹留痕
- `is_bonded_transfer = True` 仅作为信号触发

## 4. IFFM 引用铁律
### 4.1 只读引用
- TMS 对 IFFM 模块仅做只读引用（Reference 字段）
- 绝不反向修改 IFFM 任何数据

### 4.2 明细保护
- IFFM 来源的 `pickup.plan` 中 5 个集装箱明细字段（container_number, container_type, weight, bl_number, seal_number）设为只读
- 由 `_onchange_iff_requirement_ref()` 自动加载数据
- 由 `write()` 拦截保护
## 5. 运输请求双来源体系

### 5.1 两类对等 Transport Request

TMS 系统存在两个对等的 transport.request 模型：

| 模型 | 模块 | 触发方式 | 适用场景 |
|------|------|---------|---------|
| `import.pickup.requirement` | wd_iffm | 进口提单到港触发 | 进口货代部门的运输需求 |
| `tlmp.transport.request` | wd_tlms | 客户委托/运营手动创建 | 运输部门的运输需求 |

### 5.2 统一调度入口

无论哪种 transport.request 来源，排期与执行阶段使用统一模型：
任何 transport.request → pickup.plan（排期调度子单据）→ transport.order（运输执行）

### 5.3 字段对等映射

| import.pickup.requirement | tlmp.transport.request | 说明 |
|--------------------------|------------------------|------|
| pickup_scene | destination_type | 目的地场景 |
| warehouse_id | warehouse_id | 目标仓库 |
| terminal_a | terminal_id | 起点码头/货站 |
| container_lines | container_line_ids（Sprint3） | 集装箱明细 |
| delivery_city/street/zip/contact/phone | partner_id 地址 | 客户交付信息 |
| self_pickup_contact_id/phone | 无（Sprint3补充） | 自提信息 |

### 5.4 跨模块只读引用

- import.pickup.requirement 是 wd_iffm 模块的模型，TMS 通过 Reference 字段只读引用
- 当 pickup.plan.source_type='iff' 时，所有同步字段设为 readonly
- TMS 绝不反向修改 wd_iffm 的数据

### 5.5 状态机差异

| import.pickup.requirement | tlmp.transport.request | 说明 |
|--------------------------|------------------------|------|
| draft → submitted | draft → ... | 草案阶段 |
| submitted → planned | draft → confirmed | 确认/计划阶段 |
| planned → completed | confirmed → (order) | 执行完成 |
| draft/submitted → cancelled | draft/confirmed → cancelled | 取消 |


## 5. 客户/合作伙伴铁律
### 5.1 必填条件
- `customer/self_pickup` 场景 → `partner_id` 必填
- `warehouse/warehouse_transfer` 场景 → `warehouse_id` 必填
- `warehouse_transfer` 场景 → `source_warehouse_id` + `warehouse_id` 均必填且不可相同

### 5.2 承运商标记
- 卡车公司通过 `res.partner.is_carrier = True` 标记
- 卡车公司选择默认值来自系统参数 `tlmp.default_pickup_carrier_id`



## 7. 费用记录铁律

### 7.1 费用不由系统自动计算
- 运费由承运商根据路线和货物情况独立报价，无标准费率公式
- rate.base 仅作为历史价格参考线，不用于自动报价决策
- 询价阶段的费用以承运商回复为准，系统不做任何计价

### 7.2 fee.line 是记录层，不是计算层
- fee.line 在 transport.order 确认后手动录入或从 inquiry/quote 同步
- 同一笔运输有两笔费用行：一笔 customer_charge（向客户收），一笔 carrier_cost（向承运商付）
- 两笔费用数据独立录入，金额无自动关联关系

### 7.3 报价流程
- inquiry（承运商报价）→ quote（TMS 加价后报客户）
- 客户接受 → transport.order 创建 → fee.line 记录实际费用
- 客户不接受 → 重新 inquiry 或 暂停需求

## 6. 状态约束
- `pickup.plan` 无独立状态机，生命周期由下游单据派生：
  - `scheduled_date` 有值 = 已排期
  - `transport_request_id` 有值 = 已进入询价链路
  - `transport_order_id` 有值 = 已生成运输订单
- `schedule.plan.schedule` 有完整状态机（draft → scheduled → completed → cancelled）
