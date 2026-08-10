# business_debt_register.md
## 文档定位
业务债务登记台账。发现的问题只登记、不擅自开发；
排期信息仅用于项目管理台账，不植入交付客户的业务文档正文。

## BUSINESS-DEBT-001: Customer Order entity missing

| 字段 | 内容 |
|------|------|
| Debt ID | BUSINESS-DEBT-001 |
| Problem | Customer Order entity missing |
| Current behavior | Customer Request 被用作商务参考（demand input），
  transport.order 仅承载供应商执行订单 |
| Risk | 无法区分 customer commitment 与 supplier execution order |
| Severity | HIGH |
| Impact | commercial_traceability / customer_commitment_management /
  billing_boundary |
| Decision | Deferred |
| Target | Sprint52 Business Validation |

### BUSINESS-DEBT-001 v2（Sprint52FIX-003 更新）

| 字段 | 内容 |
|------|------|
| Debt ID | BUSINESS-DEBT-001 v2 |
| Problem | Customer Contract Order Layer Missing |
| Current behavior | customer request → customer quote accepted → supplier order |
| Target | customer request → customer quote → customer order → supplier order |
| Impact | customer contract fulfillment missing / revenue recognition boundary
  unclear / customer settlement cannot attach / customer SLA tracking impossible |
| Plan | Sprint52 仅登记；未来 Customer Order Domain / Customer Settlement Domain |

## BUSINESS-DEBT-002: Inquiry Communication Lifecycle Separation

| 字段 | 内容 |
|------|------|
| Debt ID | BUSINESS-DEBT-002 |
| Problem | Inquiry Communication Lifecycle Separation |
| Current behavior | inquiry state 使用 responded 表示承运商回复 |
| Target | inquiry lifecycle（draft/sent/selected/rejected/closed）
  + communication（not_sent/sent/responded）分离，支持改价后再次 responded |
| Plan | Sprint52FIX-003 暂不实施；未来登记后另行处理 |

### 边界约定（Sprint51 冻结）
- `transport.request`：客户需求入口，不定义为 Customer Order；
- `transport.order`：供应商执行订单；
- `customer.order`：暂不实现，Sprint51 不修改 Request/Order 关系。
