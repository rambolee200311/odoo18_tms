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
| accepted | selected | 语义修正为“选定获胜承运商”，回填 selected_carrier_id=partner_id |
| draft / sent / responded / rejected / closed | 同名保留 | 不迁移 |
| expired | closed（close_reason=expired） | 过期不再作为状态，按关闭询价处理 |

## transport.quote
| 旧值 | 新值 | 迁移规则 |
|------|------|----------|
| sent / issued | draft + communication_status=sent | 发送/出具仅审计沟通，不驱动 state |
| approved / confirmed | accepted | 内部审批/客户确认统一收敛为 accepted |
| draft / accepted / rejected / closed | 同名保留 | 不迁移 |
| cancelled / expired | 保留旧值 | 历史终态保留；当前库无存量，仅作兼容说明 |

补充：1.0.126 迁移对 accepted quote 按 ledger
`QUOTE_ACCEPTED` / `QUOTE_CONFIRMED` 时间回填 `accepted_by / accepted_date`，
并回填 order 的 `carrier_id / inquiry_id` 与 quote 的 `transport_order_id` 追溯链。

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
