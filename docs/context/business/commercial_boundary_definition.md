# commercial_boundary_definition.md
## 文档定位
定义 Sprint49-50 Freeze Baseline 的商务边界，防止 Request 被误认为 Customer Order。

## 当前商务边界（冻结）

| 对象 | 角色 |
|------|------|
| transport.request | demand_input（客户需求入口） |
| transport.order | supplier_execution_order（供应商执行订单） |
| customer.order | missing（缺失），planned_sprint=Sprint52 |

## 未来演进方向（关系）

```
customer_request
    ↓ creates
customer.order（未来）
    ↓ creates
transport_order（supplier execution order）
    ↓ executes
transport_plan
```

| 源对象 | 关系 | 目标对象 |
|--------|------|----------|
| customer_request | creates | customer_order（future） |
| customer_order | creates | transport_order |
| transport_order | executes | transport_plan |

## 目标模型（Sprint52 后再评估）

```
transport.request
    ↓
customer.order
    ↓
carrier.order
```

## Sprint51 约束
- 不修复 Customer Order 缺失问题；
- 仅登记业务债务（BUSINESS-DEBT-001）；
- 不改变 Request / Order 模型关系。
