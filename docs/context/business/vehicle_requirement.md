# vehicle_requirement.md
## 文档定位
本文档定义运输车辆需求的业务约束规则，归属**业务规则引擎**范畴，独立于工作流流转逻辑；所有校验结论输出给上层业务流程消费，不直接定义流程状态。

## 一、前置分流规则（优先级最高）
### 1.1 运输服务类型分流判定
字段正式命名：`transport_service_type`（原`carrier_type`更名，明确为**业务运输模式分类**，不等于承运商主体类型；同一家承运商可同时承接多种服务类型）
枚举取值：
- `road_haulage`：陆运整车/零担运输服务，必须完整填写车辆需求相关字段，执行全部车辆约束校验；
- `express_courier`：快递运输服务，豁免车辆需求字段填写、豁免本文件内所有车辆维度校验，前端隐藏车辆相关录入区域。

### 1.2 两个核心概念严格隔离
#### Vehicle Requirement（车辆需求约束）
挂载对象：`transport.request`
含义：下单阶段业务侧对执行车辆装卸形式、载重下限、专项资质的前置约束，为下单快照，可覆盖场景默认配置，用于运力匹配前置校验。

#### Vehicle Allocation（实际车辆分配）
挂载对象：`transport.plan`、`transport.order`
含义：调度最终敲定的真实车辆、司机、资质、额定载重等履约信息；快递场景不生成车辆分配数据；该快照仅用于履约、结算与审计，**不可反向修改下单时的需求约束**。

## 二、字段规范定义
### 2.1 状态分层设计（移除`confirmed(exempted)`复合状态）
1. `vehicle_requirement_state`（生命周期状态，仅三类）
    - `pending`：车辆约束信息待补充完善
    - `confirmed`：信息完整，可进入规则校验
    - `failed`：约束信息非法或缺失，拦截下游履约
2. `vehicle_requirement_mode`（规则执行模式，独立字段）
    - `required`：强制执行全套车辆校验（陆运场景默认）
    - `exempted`：豁免全套车辆校验（快递场景默认）

### 2.2 vehicle_body_type 车辆装卸类型
仅`transport_service_type=road_haulage`、`mode=required`时生效；`express_courier+exempted`场景豁免；该字段代表车辆能力分类，不指代车辆品牌。
枚举分组：
1. 无要求
    - `no_requirement`：无装卸形式约束
2. 装卸方式维度
    - `rear_only`：仅车尾装卸
    - `side_loading`：侧面装卸
    - `side_rear_both`：侧尾双向装卸
    - `top_loading`：顶部吊装作业
    - `tail_lift`：车尾配备液压尾板
3. 特种车体维度
    - `open_flatbed`：开放式平板车
    - `reefer_refrigerated`：温控冷藏车
    - `tanker`：罐式特种运输车

### 2.3 vehicle_capacity_requirement 车辆载重下限要求
释义：约束**分配车辆的额定载重最低门槛**，不等同货物重量限制；单位：吨；区间边界严格闭合：
- `no_limit`：无载重下限约束
- `below_40t`：车辆额定载重 ＜ 40
- `40t_44t`：车辆额定载重 ≥40 且 ≤44
- `over_44t`：车辆额定载重 ＞44

### 2.4 dangerous_goods_vehicle_requirement 危险品车辆专项需求
#### 数据归属边界
- 货物危险品原生属性：存放于`transport.cargo.line`，字段为`is_dangerous_goods`、`adr_class`、`un_code`；
- 车辆侧配套要求：存放于`transport.request`本结构体，仅一个布尔字段：
  `require_adr_vehicle`：`true`=必须分配持有有效ADR认证的车辆；`false`=无ADR车辆强制要求。

### 2.5 Order双快照字段约定
`transport.order`固化两组独立JSON快照，不混用：
1. `vehicle_requirement_snapshot`：下单时的车辆需求完整快照
2. `vehicle_allocation_snapshot`：调度分配的实际车辆履约快照

## 三、单据链路透传原则
1. `transport.request`：
    - 陆运：存储完整`Vehicle Requirement`快照，`mode=required`；
    - 快递：仅记录`transport_service_type`、`mode=exempted`，不存储车辆字段；
2. `transport.inquiry`：陆运展示运力约束摘要；快递不展示任何车辆相关信息；
3. `transport.quote`：陆运承运商对照车辆约束完成运力匹配后报价；快递报价不读取车辆维度；
4. `transport.plan`：陆运生成`Vehicle Allocation`数据并执行规则校验；快递不产生车辆分配记录；
5. `transport.order`：陆运持久化`vehicle_requirement_snapshot + vehicle_allocation_snapshot`；快递仅留存运输服务类型与豁免标识用于审计。

## 四、业务校验规则清单
- **RULE‑VEHICLE‑000 运输服务类型分流规则（最高优先级）**：依据`transport_service_type`绑定`mode`，决定是否启用车辆校验体系；
- **RULE‑VEHICLE‑001 车型装卸能力匹配规则**：实际分配车辆装卸形式必须匹配下单约束；`no_requirement`放行全部车型；
- **RULE‑VEHICLE‑002 车辆载重下限匹配规则**：实际分配车辆额定载重必须满足Request设置的车辆能力下限区间；
- **RULE‑VEHICLE‑003 ADR车辆资质匹配规则**：当`require_adr_vehicle=true`时，仅允许分配有效ADR认证车辆；
- **RULE‑VEHICLE‑004 ADR司机资质匹配规则**：ADR危险品订单上岗司机必须持有有效ADR从业证书；
- **RULE‑VEHICLE‑005 危化/普通运力互斥规则**：普通运力禁止承运ADR危险品；危化运力是否兼容普通货物按业务参数配置执行。

## 五、校验优先级顺序
运输服务类型分流判定 ＞ ADR全维度合规校验 ＞ 车辆载重下限校验 ＞ 装卸车型匹配校验

ADR合规内部核验顺序：承运商ADR资质核验 → 车辆ADR认证核验 → 司机ADR从业资质核验
任一环节校验不通过，单据`vehicle_requirement_state=failed`，禁止流转履约阶段。

## 六、默认初始化规则
新建`transport.request`自动赋值：
1. 选择`road_haulage`
```yaml
vehicle_body_type = no_requirement
vehicle_capacity_requirement = no_limit
dangerous_goods_vehicle_requirement.require_adr_vehicle = false
vehicle_requirement_state = pending
vehicle_requirement_mode = required
```
2. 选择`express_courier`
车辆相关字段前端隐藏、不录入
```yaml
vehicle_requirement_state = confirmed
vehicle_requirement_mode = exempted
# 自动跳过全部车辆类校验
```

## 七、文档依赖链路
目录存放路径：`docs/context/business/vehicle_requirement.md`

依赖顺序：
`business_matrix.md → cargo_requirement.md → vehicle_requirement.md → carrier_capability.md → workflow_engine.md`

说明：危险品属性优先取自`cargo_requirement`，车辆仅承接“是否需要ADR专用车辆”这一层需求。

## 八、架构兼容说明
1. 所有规则在业务规则层落地，**不新增Workflow主状态**；
2. 历史单据固化下单时刻快照，不会随后续场景配置、规则迭代被动变更；
3. 快递、陆运两套场景完全隔离，杜绝无效字段填写与误校验；
4. 字段边界清晰：货物危险品信息归属Cargo，车辆配套资质要求归属Request，后续扩展不会产生数据冗余与复制混乱。

## 冻结说明
本版为`vehicle_requirement.md V1.0 Development Baseline`，不再新增车辆维度字段，后续仅做规则参数微调，避免侵入工作流层。