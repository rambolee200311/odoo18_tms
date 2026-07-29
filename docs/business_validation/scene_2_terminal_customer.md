# Terminal → Customer — Operation Guide + Issue Log + Fix Record

**Flow**: commercial | **Entry**: Inquiry → Quote → Order | **Expected Scene**: terminal_to_customer

## Prerequisites
| # | 档案 | 检查方式 | 如果缺失 |
|---|------|---------|---------|
| 0.1 | Scene: **terminal_to_customer** | Scenes 列表 | 升级模块或手动创建 |
| 0.2 | Partner: 至少一个客户公司（is_company=True） | Contacts | 手动创建（如 "ACME B.V."） |
| 0.3 | Partner: 至少一个承运商（is_carrier=True） | Contacts → 筛选 carrier | 手动创建（如 "DHL Freight"） |
| 0.4 | Terminal Partner | Contacts | 手动创建（如 "Rotterdam Maasvlakte Terminal"） |
| 0.5 | 费用类型：至少一个 charge type | Settlement → Charge Types | 升级模块 |

---



---

## Step-by-Step Operation

| # | Action | Instructions | Expected Result | Pass? |
|---|--------|-------------|-----------------|-------|
| 2.1 | Create Transport Request | Transport Requests → Create, request_type=commercial, destination_type=customer, save | Request state=draft | [ ] |
| 2.2 | Start Inquiry | Click "Start Inquiry" | Inquiry created, state=draft, request_id=the request | [ ] |
| 2.3 | Accept Carrier Response | Add carrier response (DHL, 850 EUR), accept | Inquiry state=accepted | [ ] |
| 2.4 | Create & Accept Quote | Create Quote from inquiry, set cost+margin, accept | Order auto-created, scene_id=request.scene_id | [ ] |
| 2.5 | Verify Fee Lines | Open Order → Fees tab | carrier_cost line exists, customer_charge line exists (if applicable) | [ ] |

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
