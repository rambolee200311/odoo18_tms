# Sprint42-47 Business Scenario Validation — Results
> Status: Sprint47 in_progress | Last Updated: 2026-08-04
> Status Enums: pass / fail-fixed / fail-deferred / fail-accepted-risk / pending

| Scene | Name | Scene Code | origin_type | destination_type | Manual | Issues | Notes |
|-------|------|-----------|-------------|-----------------|--------|--------|-------|
| S1 | Terminal → Warehouse | terminal_to_warehouse | terminal | warehouse | ⏳ | 3 | 1.1/1.2/1.4 PASS；1.3/1.5 已修复待 UI 复验（SD47-S1-002/003/004） |
| S2 | Terminal → Customer | terminal_to_customer | terminal | customer | ✅ | 3 | 2.1-2.6 全部 PASS（1.0.104）；Order 1579 费用行 480 应收 + 380 应付 |
| S3 | Warehouse → Customer | warehouse_to_customer | warehouse | customer | ⏳ | 3 | Sprint47 人工验证进行中（2026-08-05）；SD47-S3-001/002/003 已修复（1.0.110）待 UI 复验 |
| S4 | Customer A → B | customer_to_customer | customer | customer | ⏳ | 0 | |
| S5 | Warehouse Transfer | warehouse_transfer | warehouse | warehouse | ⏳ | 0 | |
| S6 | Customer Return | customer_to_warehouse | customer | warehouse | ⏳ | 0 | |
| S7 | Container Swap | container_swap | terminal | warehouse | ⏳ | 0 | |
| S8 | Empty Depot | empty_depot | depot | warehouse | ⏳ | 0 | |

## 地址架构公共验证项（Sprint44/45）

| # | Check | Result |
|---|-------|--------|
| 1 | 8 场景 origin_type/destination_type 正确 | ⏳ |
| 2 | Request 表单选场景后显示地址组 | ⏳ |
| 3 | terminal/warehouse/partner 自动填充地址 | ⏳ |
| 4 | 用户可编辑自动填充地址 | ⏳ |
| 5 | Plan 创建时地址快照复制 | ⏳ |
| 6 | Order 创建时地址一致 | ⏳ |
| 7 | Order 确认后地址只读 | ⏳ |

## 缺陷汇总

| Bug ID | Scene | Description | Status |
|--------|-------|-------------|--------|
| SD47-S1-001 | S1 | Step 1.1 未创建 Cargo Line（container_no / bl_number 为空） | fixed |
| SD47-S1-002 | S1 | Step 1.3 拖拽后日历不显示（时区日期偏移） | fixed（待 UI 复验） |
| SD47-S1-003 | S1 | Step 1.5 Customer=Carrier 且 scene_id 缺失 | fixed（待 UI 复验） |
| SD47-S1-004 | S1 | Step 1.5 订单无起始地点展示 | fixed（待 UI 复验） |
| SD47-S2-001 | S2 | 无客户主档的目的地无法保存 | fixed |
| SD47-S2-002 | S2 | Inquiry Carrier 默认成 ljq | fixed（待 UI 复验） |
| SD47-S2-003 | S2 | Inquiry 无 cargo 信息 | fixed（待 UI 复验） |
| SD47-S2-004 | S2 | Inquiry 表单排版混乱 | fixed（待 UI 复验） |
| SD47-S2-005 | S2 | 2074 city 缺失 / legacy destination_type 不一致 | accepted |
| SD47-S2-006 | S2 | 3PL 流程缺失客户接受环节 | fixed（2.4 数据复验通过） |
| SD47-S2-007 | S2 | Quote Margin Rate 显示错误 + 无 cargo line | fixed（2.4 数据复验通过） |
| SD47-S2-008 | S2 | Quote cargo 描述缺柜号/BL；Fee Lines 只读 | fixed（2.4 数据复验通过） |
| SD47-S2-009 | S2 | Fee Type 下拉无记录（Charge Item 主档为空） | fixed（2.4 数据复验通过） |
| SD47-S2-010 | S2 | 保存 Fee Line 报 Source Type 必填未设置 | fixed（2.4 数据复验通过） |
| SD47-S2-011 | S2 | Quote 表头 Customer Price 与 Fee Lines 合计不一致 | fixed（1.0.102 数据复验通过） |
| SD47-S2-012 | S2 | 已接受 Quote 费用行可改删 + 定价不一致 + Order 无费用行 | fixed（1.0.103 数据复验通过） |
| SD47-S2-013 | S2 | 已有 accepted quote 仍可 Start Inquiry；Create Order 按钮难找/不可用 | fixed（1.0.104 数据复验通过） |
| SD47-S3-001 | S3 | pallet cargo line 无托件明细，Inquiry/Quote 无托件行 | fixed（1.0.110 三视图数据复验通过） |
| SD47-S3-002 | S3 | Origin 无仓库选择/自动填充 | fixed（1.0.106 数据复验通过） |
| SD47-S3-003 | S3 | cargo line 与 Request 表头汇总无关联、UOM 语义不清 | fixed（1.0.109 数据复验通过） |

## Sprint49-B 车辆需求规则修复（2026-08-06）

### 缺陷汇总

| Bug ID | Description | Status |
|--------|-------------|--------|
| SD49B-001 | VEHICLE-POLICY / RULE-VEHICLE 配置导致所有 request 全量 BLOCK | fixed（1.0.119） |
| SD49B-002 | BLOCK 结果未拦截 confirm / order 履约 | fixed（1.0.119） |
| SD49B-003 | is_dangerous_goods 未从货物危险品推导，ADR 详情缺失 | fixed（1.0.119） |
| SD49B-004 | carrier_type_vehicle_policy 硬编码，courier 配置不生效 | fixed（1.0.119） |
| SD49B-005 | RULE-VEHICLE 编号与 intent 冲突 | fixed（1.0.119 契约对齐） |
| SD49B-006 | request 快照可改、inquiry/quote/plan 展示策略缺失 | fixed（1.0.119） |

### 验证

| Check | Result |
|-------|--------|
| TestVehicleRequirement（23 项） | PASS |
| TestBusinessMatrix（11 项） | PASS |
| 全量 372 项测试中历史脏数据错误 | 149 errors / 8 failures（与本修复无关，均为重复唯一键/旧字段名） |
| XML-RPC button_immediate_upgrade | 18.0.1.0.118 → 18.0.1.0.119 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| 存量 request 回填 | confirmed snapshot 100% 回填 |
| 8089 端口 | 已释放 |

## Sprint50 Workflow Engine 基础件（2026-08-06）

### 验证

| Check | Result |
|-------|--------|
| TestWorkflowEngine（11 项） | PASS |
| TestVehicleRequirement（23 项）回归 | PASS |
| TestPickupPlan.test_07 状态机更新 | PASS |
| 全量 383 项测试中历史脏数据错误 | 148 errors / 8 failures（与本改动无关） |
| XML-RPC button_immediate_upgrade | 18.0.1.0.119 → 18.0.1.0.120 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| 新模型 tlmp.transport.event.ledger / tlmp.workflow.engine | 已建表 |
| 8089 端口 | 已释放 |

## Sprint50-A Workflow Convergence（2026-08-06）

### 验证

| Check | Result |
|-------|--------|
| TestWorkflowEngine（17 项） | PASS |
| tlmp.workflow.guard 种子守卫 | 13 条（6 wildcard + 7 关键） |
| 五模型状态动作接入 Event Ledger | PASS（ledger.source 已建） |
| 存量 request confirmed→submitted 迁移 | PASS（遗留 confirmed 0） |
| tlmp.transport.plan 抽象层 + transport_plan_id | PASS（不物理合并） |
| RULE-VEHICLE-004 正负用例 | PASS |
| transition_to_allocated 快照固化 | PASS |
| 全量 389 项测试中历史脏数据错误 | 148 errors / 8 failures（与本次无关） |
| XML-RPC button_immediate_upgrade | 18.0.1.0.120 → 18.0.1.0.121 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| 8089 端口 | 已释放 |

## Sprint50-B Operational Workflow Completion（2026-08-06）

### 验证

| Check | Result |
|-------|--------|
| TestWorkflowEngine（20 项） | PASS |
| transport_event_code 种子 | 41 条 |
| Ledger event_code_id / event_code_status | 已建字段并强绑定 |
| TransportPlan 唯一状态归属 | PASS（detail 为 related 投影） |
| allocation_candidate JSON draft | PASS（不建独立模型） |
| plan.reserve Validation / order.allocated Verification | PASS |
| 快递豁免无 allocation | PASS（snapshot NULL） |
| 全量 392 项测试中历史脏数据错误 | 148 errors / 8 failures（与本次无关） |
| XML-RPC button_immediate_upgrade | 18.0.1.0.121 → 18.0.1.0.122 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| 8089 端口 | 已释放 |

## Sprint51 Workflow Freeze & Regression Validation（2026-08-06）

### 验证

| Check | Result |
|-------|--------|
| test_sprint51_freeze（16 项） | PASS |
| test_commercial_boundary（3 项） | PASS |
| Rule Engine 四组（普通/ADR车辆/ADR司机/Express 隔离） | PASS |
| Workflow 五模型回归 | PASS |
| Event Ledger ledger-first + 事件字典 | PASS |
| Snapshot version + immutability | PASS |
| 全量 411 项测试中历史脏数据错误 | 148 errors / 8 failures（与本次无关） |
| XML-RPC button_immediate_upgrade | 18.0.1.0.122 → 18.0.1.0.123 PASS |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| 8089 端口 | 已释放 |

---

*执行说明：每个场景在 docs/business_validation/scene_N_*.md 的"地址架构验证"章节逐项勾选，缺陷记录到该场景 Issues Found，汇总到上表。*

## Sprint52 Business Scenario Validation（2026-08-07）

> Sprint52 为业务真实性验证阶段，不做功能开发；执行顺序按
> common_pre_check → A → C → B → G → H → E → F → D。

### 子意图进度

| 子意图 | 场景 | 状态 |
| :--- | :--- | :--- |
| Sprint52-A | S1 Terminal → Warehouse | ✅ PASS（人工验证通过） |
| Sprint52-C | S3 Warehouse → Customer | ✅ PASS（组合 1-8 全链路通过） |
| Sprint52-B | S2 Terminal → Customer | ✅ PASS（组合 1-8 全链路 + SD52-B-001/002 fixed） |
| Sprint52-G | S7 Container Swap | ⏳ pending |
| Sprint52-H | S8 Empty Depot | ⏳ pending |
| Sprint52-E | S5 Warehouse Transfer | ⏳ pending |
| Sprint52-F | S6 Customer Return | ⏳ pending |
| Sprint52-D | S4 Customer A → B | ⏳ pending |

### Sprint52-A 验证记录

| Check | Result |
| :--- | :--- |
| 8 个代表组合 | ✅ PASS（柜/托/件 × 自有/外部 × T1/普通 × 危品/普通） |
| Request 状态 | completed（8/8） |
| Order 状态 | closed（8/8） |
| Event Ledger | 每条 12 条，全部命中事件字典 |
| Request 双 Snapshot | frozen（8/8） |
| Order vehicle_allocation_snapshot | 存在（8/8） |
| 阻塞问题 | 0 |
| 开放观察项 | SD52-A-001（Plan 名称双连字符）、SD52-A-002（计划驱动 carrier_cost 0.00 占位） |

### Sprint52-B 验证记录

| Check | Result |
| :--- | :--- |
| 8 个代表组合 | ✅ PASS（柜/托/件 × 自有/外部 × T1/普通 × 危品/普通） |
| Commercial Flow | ✅ PASS（request → inquiry → quote → order → allocate → in_transit → delivered → closed） |
| Request 状态 | completed（8/8） |
| Order 状态 | closed（8/8） |
| Event Ledger | 15 条/组合，全部命中事件字典 |
| Request 双 Snapshot | frozen（8/8） |
| Order vehicle_allocation_snapshot | 存在（8/8） |
| Quote 双向 fee line | PASS（customer_charge + carrier_cost） |
| Order 双向 fee line | PASS（customer_charge 480 + carrier_cost 380，8/8） |
| 阻塞问题 | 0 |
| 修复记录 | SD52-B-001（1.0.124）、SD52-B-002（1.0.125）均验证通过 |
| 8089 端口 | 已释放 |

### Sprint52-C 验证记录

| Check | Result |
| :--- | :--- |
| 8 个代表组合 | ✅ PASS（柜/托/件 × 自有/外部 × T1/普通 × 危品/普通） |
| Commercial Flow | ✅ PASS（request → inquiry → quote → order → allocate → in_transit → delivered → closed） |
| Request 状态 | completed（8/8） |
| Order 状态 | closed（8/8） |
| Event Ledger | 15 条/组合，全部命中事件字典 |
| Request 双 Snapshot | frozen（8/8） |
| Order vehicle_allocation_snapshot | 存在（8/8） |
| Quote 双向 fee line | PASS（customer_charge + carrier_cost） |
| Order 双向 fee line | PASS（customer_charge 480 + carrier_cost 380，8/8） |
| Fix3 重跑（1.0.126） | PASS（8/8，request 3808-3815，ledger 18/组合） |
| 阻塞问题 | 0 |
| 开放观察项 | 无 |
| 8089 端口 | 已释放 |

### Sprint52-Fix3 验证记录（wd_tlms 1.0.126，2026-08-10）

| Check | Result |
| :--- | :--- |
| XML-RPC button_immediate_upgrade | PASS（18.0.1.0.125 → 18.0.1.0.126） |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0 |
| inquiry 状态分布 | draft 2 / sent 1 / selected 33 |
| quote 状态分布 | accepted 34 |
| order 追溯链回填 | 33/33 无缺失 |
| S2/S3 新链回归 | PASS（wizard → selected inquiry → accepted quote → order → closed） |
| Sprint52-C Fix3 重跑 | PASS（8/8，request 3808-3815，ledger 18/组合） |
| Quote/Order fee line | 480 / 380（8/8 既有链 + 新链一致） |
| 8089 端口 | 已释放 |

下一子意图：Sprint52-G。
