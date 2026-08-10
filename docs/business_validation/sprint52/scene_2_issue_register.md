# Sprint52-B Scene 2 Issue Register

> 契约：`INT-TMS-SPRINT52B-001`
> 规则：发现业务缺口只登记，不直接修复；修复需新 intent。

| 编号 | 场景 | 问题 | 影响 | 建议 | 状态 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| SD52-B-001 | S2 | 商务链 quote 创建 order 后，order 无法 allocate：`Allocation candidate is missing; plan.reserve must be completed first.` | 商务链 order 无法进入 allocated/in_transit/delivered，状态卡在 confirmed | 已按 INT-TMS-SPRINT52FIX-001 修复：无 plan 时直接校验 request 快照并生成 allocation snapshot；wd_tlms 1.0.124 验证通过 | fixed |
| SD52-B-002 | S2 | 商务链 order 只有 customer_charge fee line（480），缺少 carrier_cost 应付行（380） | 应付费用无法从 order 费用行直接核对 | 已按 INT-TMS-SPRINT52FIX-002 修复：quote 创建时同时生成 customer_charge + carrier_cost，order 复制双向 fee line；wd_tlms 1.0.125 组合 1-8 复测通过 | fixed |
