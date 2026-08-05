# INT-TMS-SPRINT48C-001 Execution Record

- intent_id: INT-TMS-SPRINT48C-001
- parent_intent_id: INT-TMS-SPRINT48-001
- title: Cargo Model Reset & Regression（测试库清空 + 回归）
- status: COMPLETED
- started_at: 2026-08-05
- completed_at: 2026-08-05
- executor: AI-Engineering-Team（Codex）
- module_version: wd_tlms 18.0.1.0.112

## Scope

测试数据库历史数据全部清空（order / plan / inquiry / quote / request 及附属行），
不做历史迁移；按 Sprint48-A/B 新模型（Cargo Node）重建业务场景并回归。

## Execution Steps

1. 清空前统计各模型数量，按依赖顺序删除：
   schedule.plan.schedule / tlmp.transport.container / transport.fee.line /
   tlmp.transport.cargo.line / pickup.plan.container.line / tlmp.transport.order /
   pickup.plan / tlmp.transport.quote / tlmp.transport.inquiry / tlmp.transport.request
   （删除前将 quote 状态临时置回 draft 以通过费用行锁定）。
2. `env.cr.commit()` 提交，并在新 shell 会话 `search_count` 复核全部为 0。
3. 新增业务场景回归测试 `test_sprint48_business_scenarios`：
   - 一柜20托：container + 20 handling_unit → 表头 20 托 / 200 件 / 600 kg / 30 m³
   - 托盘拆件双订单：同一 request/cargo node 生成两个独立 order 快照
   - 报价快照冻结隔离：order confirm 后 cargo 快照不可变
4. 运行回归：`-u wd_tlms --test-enable --test-tags=wd_tlms:TestBusinessScenarios`
   → 0 failed, 0 errors of 3 tests。

## Results

- 清空复核：order=0 / plan=0 / quote=0 / inquiry=0 / request=0 /
  cargo.line=0 / fee.line=0 / container.line=0 / transport.container=0 / schedule=0
- 回归测试：3/3 通过
- Sprint48-A/B/C 定向回归累计：12/12 通过

## Artifacts

- tests: addons/wd_tlms/tests/test_sprint48_business_scenarios.py
- docs: docs/context/history/decision_note.md
- context_version: 1.0.62
- commits: 7e4f02266（Sprint48-C 回归与文档）

## Notes

全量 332 项测试在开发库仍有主数据唯一键等环境冲突（与本次改动无关）；
全量绿需在干净测试库运行。
