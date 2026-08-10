# transport_event_dictionary.md
## 文档定位
TLMS Workflow Engine 事件编码字典。所有状态变更事件必须使用本字典编码，
禁止自由文本；Event 是唯一事实，状态变更先写 Transport Event Ledger 再更新单据。

## 事件分类 event_category
- `state`：单据状态流转事件
- `business`：业务行为事件（报价、调度、车辆预留、异常处置）
- `integration`：外部系统/API/Excel 导入事件

## transport.request
| code | category | from_state | to_state | 说明 |
|------|----------|------------|----------|------|
| REQUEST_DRAFT_CREATED | state | - | draft | 新建草稿 |
| REQUEST_SUBMITTED | state | draft | submitted | 提交并冻结 matrix + vehicle 快照 |
| REQUEST_VALIDATION_PASSED | business | pending | passed | 矩阵/车辆校验通过 |
| REQUEST_VALIDATION_FAILED | business | pending | failed | 校验 BLOCK |
| REQUEST_PROCESSING | state | submitted | processing | 校验通过进入履约 |
| REQUEST_COMPLETED | state | processing | completed | 全量/部分履约完结 |
| REQUEST_CANCELLED | state | draft/submitted | cancelled | 整单作废 |

## transport.inquiry
| code | category | from_state | to_state | 说明 |
|------|----------|------------|----------|------|
| INQUIRY_SENT | state | draft | sent | 下发承运商 |
| INQUIRY_RESPONDED | business | sent | responded | 承运商响应（成本/日期/资质） |
| INQUIRY_SELECTED | state | responded | selected | 选定获胜承运商 |
| INQUIRY_REJECTED | state | responded | rejected | 未选中承运商 |
| INQUIRY_CLOSED | state | sent/responded/selected | closed | 关闭询价（含过期 close_reason=expired） |
| INQUIRY_ACCEPTED | business | responded | accepted | deprecated（1.0.126 起；历史 ledger 不重写） |

## transport.quote
| code | category | from_state | to_state | 说明 |
|------|----------|------------|----------|------|
| QUOTE_SENT | business | draft | draft | 发送客户（communication_status=sent，不驱动 state） |
| QUOTE_ISSUED | business | draft | draft | 出具记录（仅审计，不驱动 state） |
| QUOTE_APPROVED | business | draft | draft | 内部审批记录（仅审计，不驱动 state） |
| QUOTE_ACCEPTED | business | draft | accepted | 客户接受，回填 accepted_by/accepted_date |
| QUOTE_REJECTED | state | draft | rejected | 报价驳回 |
| QUOTE_CLOSED | state | draft/accepted | closed | 报价关闭（含过期） |
| QUOTE_CONFIRMED | state | approved | confirmed | 历史事件，1.0.126 后不再产生 |
| QUOTE_CANCELLED / QUOTE_EXPIRED | state | - | cancelled/expired | 历史事件，1.0.126 后不再产生 |

> Sprint52FIX-003：quote 状态收敛为 draft / accepted / rejected / closed；
> communication_status（not_sent/sent/viewed/responded）只记录客户沟通，
> 不驱动 workflow。

## transport.plan（pickup.plan / container.transport.plan）
| code | category | from_state | to_state | 说明 |
|------|----------|------------|----------|------|
| PLAN_SCHEDULED | state | draft | scheduled | 排班规划完成 |
| PLAN_RESERVED | state | scheduled | reserved | 资源预留（车辆/司机/运力） |
| PLAN_EXECUTING | state | reserved | executing | 班次履约 |
| PLAN_FINISHED | state | executing | finished | 正常完结 |
| PLAN_FAILED | state | executing | failed | 履约异常 |
| PLAN_CANCELLED | state | draft/scheduled/reserved | cancelled | 发车前作废 |
| VEHICLE_RESERVED | business | scheduled | reserved | 车辆资源预留（含 ADR 校验） |
| ADR_DRIVER_CHECK | business | reserved | executing | RULE-VEHICLE-004 司机 ADR 校验 |

## transport.order
| code | category | from_state | to_state | 说明 |
|------|----------|------------|----------|------|
| ORDER_CREATED | state | - | draft | 供应商执行订单创建（商务链） |
| ORDER_CONFIRMED | state | draft | confirmed | 订单锁定 |
| ORDER_ALLOCATED | state | confirmed | allocated | 绑定 Plan 预留资源 |
| ORDER_IN_TRANSIT | state | allocated | in_transit | 在途 |
| ORDER_EXCEPTION | state | in_transit/allocated | exception | 异常总态（exception_type 区分） |
| ORDER_EXCEPTION_RECOVERED | business | exception | in_transit/delivered/cancelled | 异常恢复 |
| ORDER_DELIVERED | state | in_transit | delivered | 签收完成（需 POD_RECEIVED） |
| ORDER_SETTLEMENT_PENDING | state | delivered | settlement_pending | 结算缓冲期 |
| ORDER_SETTLED | state | settlement_pending | settled | 财务办结 |
| ORDER_CANCELLED | state | confirmed/allocated | cancelled | 允许取消窗口 |
| POD_RECEIVED | business | in_transit | delivered | POD 签收事件（守卫条件） |
| VEHICLE_ALLOCATED | business | confirmed | allocated | 车辆分配快照固化 |

## 守卫规则引用
- `REQUEST_SUBMITTED → REQUEST_PROCESSING`：validation_state=passed
- `QUOTE_ACCEPTED → ORDER_CREATED`：quote.inquiry_id.state=selected 且 carrier 存在
- `ORDER_IN_TRANSIT → ORDER_DELIVERED`：存在 POD_RECEIVED
- `ORDER_DELIVERED → ORDER_SETTLEMENT_PENDING`：Delivery Event 完成
