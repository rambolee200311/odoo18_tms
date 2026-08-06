# state_migration_plan.md
## 文档定位
Sprint50 Workflow Engine 存量状态值迁移映射。迁移只做 value 映射与快照回填，
不重算业务结论；历史快照保持不变。

## transport.request
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| confirmed | submitted | confirmed 视为已提交；若已有 matrix_snapshot_status=frozen 保持冻结 |
| cancelled | cancelled | 不变 |
| draft | draft | 不变 |

补充字段回填：
- `validation_state`：confirmed 存量置 passed，draft 置 pending
- `fulfillment_status`：confirmed 且无下游订单置 pending
- `vehicle_requirement_mode_snapshot / vehicle_requirement_snapshot`：
  已冻结保持不变，未冻结的 confirmed 单据按 49-B 回填

## transport.inquiry
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| accepted | closed | accepted 视为已关闭询价，回填 selected_carrier_id |
| responded | sent | 已回价但未选定的保持 sent，response_count 保留 |
| rejected/expired | cancelled | 作废场景统一 cancelled，close_reason 回填 |

## transport.quote
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| sent | issued | sent 视为已出具报价 |
| accepted | confirmed | accepted 视为客户确认，confirmation_source 回填 customer |
| rejected | rejected | 不变 |
| cancelled/expired | cancelled/expired | 不变 |

## transport.plan（pickup.plan / container.transport.plan）
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| confirmed（container.transport.plan） | reserved | confirmed 视为资源预留完成，reservation_type 默认 vehicle |
| completed | finished | completed 视为正常完结 |
| pending/scheduled（bl.container） | scheduled | pending/scheduled 统一 scheduled |

## transport.order
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| assigned | allocated | assigned 视为资源绑定完成 |
| signed | delivered | signed 视为签收完成（POD 已确认） |
| billed | settlement_pending | billed 视为进入结算缓冲期 |
| closed | settled | closed 视为结算办结终态 |
| settled | settled | 不变 |
| confirmed/in_transit/delivered/cancelled | 同名保留 | 不变 |

## 回填约束
1. 迁移先升级模块 schema，再执行 value 映射，最后回填快照。
2. 49-B 已冻结的 vehicle_requirement_snapshot 不得被覆盖。
3. order 双快照（matrix + vehicle requirement）迁移时 exists/valid 校验放行
   存量 draft 订单，仅对确认后订单强制有效。
