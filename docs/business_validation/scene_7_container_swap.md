# Container Swap — Operation Guide + Issue Log + Fix Record

**Flow**: N/A | **Entry**: Field Extension | **Expected Scene**: N/A

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Transport Order：已有容器明细（container_line_ids） | 打开一个已有 Order | 创建一个 FTL 类型的 Order |
| 0.2 | container_line 表单可见 needs_swap / swap_location | 确认视图中有这两个字段 | 升级模块 |

---



---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 7.1 | Open Transport Order with container | Find order with container_line, open form | Container line visible | [ ] |
| 7.2 | Verify needs_swap field | Check container_line form for needs_swap checkbox, swap_location field | needs_swap exists, swap_location exists | [ ] |

---

## Issues Found
| Step | Issue Description | Severity | Reported | Fix Status |
|------|------------------|----------|----------|------------|
| | _(user fills this)_ | blocking / minor | date | pending / fixed / deferred |

---

## Fix Record
| Bug ID | Scene | Root Cause | Fix Scope | Commit | Regression Test | Status |
|--------|-------|-----------|-----------|--------|-----------------|--------|
| | | | | | | |

---

## Final Result
- **BAT**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
- **Manual**: ⏳ pass / fail-fixed / fail-deferred / fail-accepted-risk
