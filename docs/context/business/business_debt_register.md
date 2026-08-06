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

### 边界约定（Sprint51 冻结）
- `transport.request`：客户需求入口，不定义为 Customer Order；
- `transport.order`：供应商执行订单；
- `customer.order`：暂不实现，Sprint51 不修改 Request/Order 关系。
