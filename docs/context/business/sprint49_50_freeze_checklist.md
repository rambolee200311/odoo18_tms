# Sprint49-50 Architecture Freeze Checklist

## 冻结对象与版本

| 对象 | 冻结项 | 版本 |
|------|--------|------|
| Business Rule | Business Matrix Rules / RULE-VEHICLE-000~005 | vehicle_rule 1.0 |
| Workflow | 五模型状态（Request/Inquiry/Quote/Plan/Order） | workflow 1.0 |
| Event | transport_event_code 字典 | event_dictionary 1.0 |
| Snapshot | matrix / vehicle_requirement / vehicle_allocation | snapshot 1.0 |
| Boundary | current commercial boundary | Sprint51 Freeze |

## 禁止项

- 禁止新增状态；
- 禁止新增自由事件编码（只能 deprecated）；
- 禁止修改三类快照字段；
- 禁止新增业务场景 / 规则维度 / Carrier Settlement / OCR；
- 禁止修改 Request / Order 商务边界（Customer Order 缺失仅登记，
  纳入 Sprint52）。

## 回归验证入口

- `test_sprint51_freeze.py`：Rule Engine / Workflow / Event Ledger /
  Snapshot 冻结回归；
- `test_commercial_boundary.py`：商业边界回归。

## 修改要求

冻结基线任何修改需 business_owner_approval + architect_approval。
