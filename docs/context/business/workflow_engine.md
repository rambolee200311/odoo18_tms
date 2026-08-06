五模型状态机汇总

前置统一规则
1. Scene 唯一业务语义入口：彻底下线 destination_type 冗余字段。Scene 承载：业务含义、执行范式、合规约束（非简单地点路线），所有单据不再冗余存储场景属性。
2. 事件驱动单向联动：上下游联动仅靠事件通知，下游禁止直接改写上游状态。
3. 状态是计算结果，Event 是唯一事实：所有状态变更必先写入 Transport Event Ledger，再更新单据状态。
4. 异常字段化、不状态膨胀：运输异常通过异常类型字段区分，不新增独立异常状态。

状态守卫规则：
Request:submitted → processing
必须:validation_state=passed

Quote:approved → confirmed
必须:approval_user存在

Order:in_transit → delivered
必须:POD_RECEIVED事件存在

Order:delivered → settlement_pending
必须:Delivery Event完成

---
1. transport.request 运输需求单（已修正：删除冗余validated状态、支持部分履约）
业务生命周期 state
draft → submitted → processing → completed / cancelled
状态
释义
draft
草稿，可完整编辑单据内容
submitted
已提交，进入校验队列等待核验
processing
校验通过，已生成Plan/Inquiry，下游履约流程运行中
completed
需求履约完结（支持完全完结/部分完结）
cancelled
整单需求作废终止
独立技术校验状态 validation_state
pending / passed / failed
流转守卫：submitted + validation_state=passed → processing，彻底消除状态语义重复。
独立履约结果字段 fulfillment_status（解决3PL部分履约场景）
pending / partial / completed / cancelled
用途：主状态统一为completed时，通过该字段区分「整单完成 / 部分交付 / 部分取消」业务场景。
配套聚合字段
planned_qty、ordered_qty、delivered_qty、settled_order_count、total_order_count、requested_qty

---
2. transport.inquiry 询价单
主状态 state
draft → sent → closed / cancelled
状态
释义
draft
草稿，维护询价承运商清单
sent
已批量下发至对应承运商等待回价
closed
满足业务决策条件即关闭（支持部分回价择优报价、无需全部承运商回价，完成Quote生成）
cancelled
客户终止询价，流程作废
进度字段：expected_carrier_count、response_count（仅展示，不控制状态流转）

---
3. transport.quote 报价单
主状态 state
draft → issued → approved → confirmed / rejected / expired
状态
释义（权责严格区分）
draft
草稿，核算运价及各类附加费
issued
正式对外出具报价
approved
企业内部风控审批通过（商务/运营/危化合规审批，允许对外成交）
confirmed
客户正式接受报价，费率固化，同步写入Order作为结算基准
rejected
报价驳回失效
expired
报价超出有效期自动失效
议价记录字段：negotiation_count、last_negotiation_time、negotiation_log（过程字段化，无negotiating状态）

---
4. transport.plan 运输执行计划
主状态 state（allocated 统一更名 reserved）
draft → scheduled → reserved → executing → finished / failed / cancelled
状态
释义（层级隔离）
draft
待排班
scheduled
线路、时间窗排班规划完成
reserved
计划层资源预留：锁定卡车、司机、路线、时段（调度预占用，未绑定正式订单）
executing
班次履约进行中，持续上报节点事件
finished
班次正常完结
failed
履约异常：车辆故障、口岸拥堵、客户拒收等
cancelled
发车前作废班次，不计费

---
5. transport.order 运输订单
主状态 state（完全保留评审认可链路）
draft → confirmed → allocated → in_transit → exception → delivered → settlement_pending → settled / cancelled
状态
释义
draft
初始待确认
confirmed
订单信息核验锁定
allocated
订单级资源绑定，通过allocation_source溯源对应Plan预留资源
in_transit
货物在途运输
exception
运输异常总态（具体异常由字段区分，不膨胀状态）
delivered
现场签收完成
settlement_pending
结算缓冲期：核验POD、CMR、滞留费、燃油附加费、承运商发票
settled
财务对账办结，终态固化结算快照
cancelled
仅confirmed/allocated阶段允许取消，在途及签收后禁止作废
异常类型字段 exception_type（枚举）
delay、damage、customer_refuse、document_issue、customs_hold、vehicle_failure
规则：统一exception主状态，通过字段细分异常场景，彻底杜绝状态爆炸。

---
核心模型权责边界
1. Request：业务准入校验、全单需求生命周期、整体履约结果管控
2. Inquiry+Quote：商务询价、议价、内部风控、客户确认全流程
3. Plan：调度层运力规划、资源预留、班次执行管控
4. Order：订单级资源绑定、在途履约、异常处置、财务结算闭环
5. Scene：承载全部业务语义、执行模式、合规规则，作为系统唯一模板入口
