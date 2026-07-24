# ADR-024: Transport Type Master Data — Selection to Many2one Migration

## 决策
将 `transport_type` 从 4 个模型中重复定义的 Selection 枚举统一重构为
`tlmp.transport.type` 档案模型（Many2one）。

## 动机
- 原有 Selection 散落在 transport_order / request / rate_base / pricing_rule 四模型中，
  新增一个值需要改 4 处代码，极易遗漏
- LTL/Parcel/Groupage 新场景需要新增运输类型，Selection 模式无法扩展
- 未来 Carrier Adapter、定价引擎、报表分析均依赖统一运输分类语言

## 影响范围
| 模型 | 变更 |
|------|------|
| 4 个业务模型 | legacy_transport_type(deprecated) + transport_type_id(M2O) |
| pickup_plan / container_service | type_map 从 dict 改为 database lookup + 缓存 |
| 6 个视图文件 | 字段替换 |
| 2 个 new model | transport.type + carrier.service |

## 降级方案
保留 `legacy_transport_type` 字段至 Sprint30+，确保旧代码 domain 筛选兼容。

## 未来扩展
- Sprint30: pricing_rule 费用引擎重构后可移除 legacy_transport_type
- Sprint25: Carrier Service 档案 → Shipment Label
- Sprint25+: Carrier Adapter Framework
