# Container Swap — Operation Guide + Issue Log + Fix Record

**Flow**: N/A | **Entry**: Field Extension | **Expected Scene**: N/A

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **container_swap** | Transport → Configuration → Transport Scenes | 升级模块或手动创建 |
| 0.2 | Transport Order：已有容器明细（container_line_ids） | 打开一个已有 Order | 创建一个 FTL 类型的 Order |
| 0.2 | container_line 表单可见 needs_swap / swap_location | 确认视图中有这两个字段 | 升级模块 |





## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 7.1 | Open Transport Order with container | Find order with container_line, open form | Container line visible | [ ] |
| 7.2 | Verify needs_swap field | Check container_line form for needs_swap checkbox, swap_location field | needs_swap exists, swap_location exists | [ ] |


## Issues Found
| Step | Issue Description | Severity | Reported | Fix Status |
|------|------------------|----------|----------|------------|
| | _(user fills this)_ | blocking / minor | date | pending / fixed / deferred |


## Fix Record
| Bug ID | Scene | Root Cause | Fix Scope | Commit | Regression Test | Status |
|--------|-------|-----------|-----------|--------|-----------------|--------|
| | | | | | | |


## Final Result
- **BAT**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Manual**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk


---

## 地址架构验证（Sprint44/45）

**场景**: S7 Container Swap | **code**: container_swap

| # | Action | Expected | Pass? |
|---|--------|----------|-------|
| A.1 | 新建 Request，选择场景 **container_swap** | Origin Address / Destination Address 两个组显示 | [ ] |
| A.2 | 起点：terminal (选 terminal_id 自动填充) | 地址字段自动填充 | [ ] |
| A.3 | 终点：warehouse (选 warehouse_id 自动填充) | 地址字段自动填充 | [ ] |
| A.4 | 手动修改一个地址字段（如 street） | 可编辑，不被后续 onchange 覆盖 | [ ] |
| A.5 | 按流程创建 Order（Plan → Go to Schedule → Plan → Order） | Order 地址与 Request/Plan 一致 | [ ] |
| A.6 | Order 确认后尝试修改地址 | 被阻止（只读） | [ ] |

**验证记录**:

| Bug ID | Step | Issue | Severity | Status |
|--------|------|-------|----------|--------|
| | | | | |
