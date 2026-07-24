# ADR-024: Transport Type Master Data — Selection to Many2one Migration

## 决策
将 `transport_type` 从 4 个模型中重复定义的 Selection 枚举直接替换为
`transport_type_id` Many2one → `tlmp.transport.type` 档案模型。

## 动机
- 原有 Selection 散落在 transport_order / request / rate_base / pricing_rule 四模型中，
  新增一个值需要改 4 处代码
- LTL/Parcel/Groupage 新场景需要新增运输类型，Selection 模式无法扩展
- 开发阶段无生产数据，无需向后兼容

## 影响范围
| 模型 | 变更 |
|------|------|
| 4 个业务模型 | transport_type(Selection) → transport_type_id(M2O, required) |
| pickup_plan / container_service | type_map 从 dict 改为 database lookup |
| 6 个视图文件 | 字段替换 |
| 2 个新模型 | transport.type + carrier.service |


## 三层决策

### Decision 1: Selection 不适合 TMS 主分类
transport_type 使用 Selection 无法支持：
- 元数据扩展（category/mode）
- 多语言
- 权限控制
- 业务分类（报表/定价/SLA）

### Decision 2: Transport Type 是 Master Data，不是业务状态
与 state（状态）不同，type 是业务实体的固有分类属性。
独立档案模型（tlmp.transport.type）实现单点维护。

### Decision 3: Carrier Service 与 Carrier（公司）解耦
carrier.service 不预设具体承运商名（DHL/UPS/DPD），
使用通用服务代码（parcel_standard/parcel_express/...）。
具体承运商通过 carrier_id Many2one → res.partner 关联，
实现公司↔服务分层架构。

## 备注
- 开发阶段（无生产数据），不保留旧字段
- Sprint25: Shipment Label
- Sprint25+: Carrier Adapter Framework
