# TLMS Transport Business Matrix
## 3PL运输业务组合矩阵与约束规则规范 V1.0

---

# 0. 文档定位
## 0.1 Purpose
本文档定义 TLMS（Transport Logistics Management System）运输领域的业务组合模型与强制约束规则。

本文件用于：
- Transport Request 业务建模
- Cargo Line 三视图设计
- Inquiry / Quote / Order 数据同步规则
- Carrier 能力匹配
- 前后端业务校验
- 自动化测试依据
- 后续运输规则引擎（Rule Engine）基础

## 0.2 核心原则
TLMS 不通过创建大量固定流程覆盖复杂运输业务。

系统采用：
```
运输场景 Scene
        +
业务维度 Business Dimension
        +
规则校验 Business Rule
        +
事件模型 Event
```
组合实现。

理论组合数量不代表流程数量。
系统禁止将576种组合实现为576套代码流程。

## 0.3 校验强制执行范围
下述所有规则**多层级强制校验，缺一不可**：
1. 前端页面下拉选项过滤、字段显隐、提交前提示；
2. Odoo ORM 层`create/write`拦截，非法数据禁止入库；
3. XML‑RPC、接口调用、Excel批量导入、定时自动建单全部复用同一套校验逻辑；
4. 第三方对接回传数据同样触发矩阵校验；
5. 拦截后返回标准化报错码+中文说明，便于运维定位。

---

# 1. 六大业务维度定义
## 1.1 Dimension Overview
|维度代号|维度名称|枚举值|数量|作用|
|-|-|-|-|-|
|A|运输场景 Scene|S1~S8|8|决定业务流程、状态机、事件|
|B|业务驱动 Business Driver|B1/B2|2|决定订单来源模式|
|C|包装形态 Cargo Type|C1/C2/C3|3|决定货物模型|
|D|承运商类型 Carrier Type|D1/D2/D3|3|决定执行模式|
|E|T1报关属性 Customs Type|E1/E2|2|决定监管要求|
|F|危险品属性 DG Type|F1/F2|2|决定安全合规要求|

---

# 2. 理论组合空间
六维理论组合：
```
8 × 2 × 3 × 3 × 2 × 2
= 576
```

## 2.1 组合编码规范
格式：
```
A{x}-B{x}-C{x}-D{x}-E{x}-F{x}
```
示例：
```
S1-B1-C2-D1-E2-F2
```
含义：
```
运输场景 S1
+
计划驱动 B1
+
托盘运输 C2
+
自有车队 D1
+
普通运输 E2
+
普货 F2
```

## 2.2 组合分层拆分（对应 Cargo Line 三个视图）
按包装形态C拆分为三组独立子集，每组理论组合192个：
- C1整柜子集：$8\times2\times1\times3\times2\times2=192$
- C2托盘子集：$8\times2\times1\times3\times2\times2=192$
- C3散件子集：$8\times2\times1\times3\times2\times2=192$

## 2.3 有效组合说明
576为笛卡尔积全域理论值；依托第4章节刚性互斥规则做系统硬拦截后，**常态化有效运营组合约280组**，无效组合在前端过滤、后端拦截，禁止入库保存。

---

# 3. 维度详细定义
## A. Transport Scene 运输场景
### 定义
运输场景决定：
- 业务流程
- 状态流转
- 必填字段
- 事件类型

当前系统配置：
```
S1 ~ S8
```
说明：
- 场景枚举由业务配置维护；
- 新增运输模式优先新增规则，不直接复制流程；
- 每个场景可单独配置允许开放的Cargo Type范围（例如港到仓场景仅开放C1/C2，屏蔽C3）。

## B. Business Driver 业务驱动
### 枚举
|代码|名称|说明|
|-|-|-|
|B1|计划驱动|长期计划、固定线路、周期运输|
|B2|商务驱动|客户询价、报价确认后运输|

### B1 计划驱动
特点：
- 可提前预测
- 批量生成运输任务
- 强调执行效率
配套能力：排期日历、运力预约、波次调度、协议批量运价、`PLAN_RESERVE`专属事件。

### B2 商务驱动
特点：
- 客户提出需求
- 需要报价流程
- 支持多承运商竞争报价
配套能力：绑定`quote_id`报价单、客户阶梯单价、`QUOTE_CONFIRM`专属事件、报价+运单归档包。

## C. Cargo Type 包装形态
Cargo Type 是 Cargo Line 核心分类。
系统只允许：
```
C1 Container
C2 Pallet
C3 Piece
```
三种模式。

### C1 Container 整柜
#### 使用场景
适用于：
- 海运整柜
- 港口提柜
- 柜级运输

#### 必备字段
```
container_type
container_no
seal_number
pallets_in_container
container_gross_weight
container_volume
```
#### 允许承运商
允许：
```
D1 自有车队
D2 第三方卡车公司
```
禁止：
```
C1 + D3
整柜 + 快递
```
#### 计费方式
默认：
```
按柜计费
```
配套单证：整柜清关单证组、T1专用CMR报关版；专属事件`CONTAINER_LOAD`。

### C2 Pallet 托盘
#### 使用场景
适用于：
- 海外仓配送
- 仓间调拨
- 客户交付
- 托盘级运输

#### 关联模型
必须支持：
```
Package Lifecycle
Physical Package
Lot
Quantity
```
#### 托盘锁定粒度
运输执行必须锁定：
```
Lifecycle
+
Physical Package
+
Lot
+
Quantity
```
#### 支持事件
允许：
```
SPLIT
MERGE
REPACK
REPLACE
```
#### 允许承运商
允许：
```
D1 自有车队
D2 第三方卡车
D3 快递
```
限制：
D3：
```
仅允许普通货物末端配送
禁止D3承接E1(T1)、F1(危险品)托盘业务
```
#### 计费方式
对接Billing Segment分段计费模型：托天计费+干线运费+特种合规溢价。

### C3 Piece 散件
#### 使用场景
适用于：
- 零担
- 小件配送
- 快递

#### 必备字段
```
piece_qty
length_cm
width_cm
height_cm
unit_weight
packing_type
total_weight
```
#### 计费方式
默认：
```
按件数/重量阶梯计费
```
配套事件`PIECE_SORT`、输出快递面单+零担运单；刚性约束：禁止C3搭配E1(T1)跨境运输。

## D. Carrier Type 承运商类型
### 枚举
|代码|名称|
|-|-|
|D1|自有车队|
|D2|第三方卡车公司|
|D3|快递公司|

### Carrier Capability 承运能力
承运商主数据必须维护两个布尔资质字段，作为下拉过滤与后端校验依据：
```yaml
support_t1: true/false
support_dg: true/false
```
业务规则：
- `support_t1=false` 的承运商，E1场景直接隐藏不可选；
- `support_dg=false` 的承运商，F1场景直接隐藏不可选。

## E. T1 Customs Attribute
### 枚举
|代码|说明|配套专属字段|专属事件|
|-|-|-|-|
|E1|T1运输|T1备案编号、口岸编码|`T1_FILING`、`T1_CLEAR`|
|E2|普通运输|无额外报关字段|常规收发运事件|

## F. Dangerous Goods Attribute
### 枚举
|代码|说明|配套专属字段|专属事件|
|-|-|-|-|
|F1|危险品|UN编号、危险等级、DGD附件|`DG_DECLARE`、`DG_TRANSFER`|
|F2|普货|无危化专属字段|常规收发运事件|

---

# 4. 全局业务约束规则
所有规则必须：
- 前端提前过滤
- 后端强制校验
- API调用、批量导入、自动任务同样生效

## RULE‑CARGO‑001 整柜禁止快递
条件：
```
C1 + D3
```
结果：
```
Reject
```
说明：
整柜运输不允许快递公司承运；前端D3选项在C1视图直接隐藏，后端命中组合直接拦截。

## RULE‑CARGO‑002 散件禁止T1运输
条件：
```
C3 + E1
```
结果：
```
Reject
```
说明：散件不承接T1跨境监管运输，勾选E1后C3视图入口禁用。

## RULE‑CARGO‑003 快递禁止T1
条件：
```
D3 + E1
```
结果：
```
Reject
```
说明：快递公司无跨境T1报关配套能力，E1场景下拉不展示D3。

## RULE‑CARGO‑004 快递禁止危险品
条件：
```
D3 + F1
```
结果：
```
Reject
```
说明：普通快递无危化运输资质，F1场景下拉屏蔽D3。

## RULE‑CARRIER‑001 T1承运商资质校验
条件：
```
E1
```
必须满足：
```
carrier.support_t1 = true
```
否则：
```
Reject
```

## RULE‑CARRIER‑002 危险品承运商资质校验
条件：
```
F1
```
必须满足：
```
carrier.support_dg = true
```
否则：
```
Reject
```

## RULE‑CARGO‑005 单Transport Request禁止混合包装形态
禁止：
```
Container + Pallet
或
Pallet + Piece
或
Container + Piece
```
规则：
一个 Transport Request：
```
只能选择一种 Cargo Type
```
实现方式：切换Tab时清空其他Tab明细行、后端校验多条明细`cargo_type`必须完全一致。

## RULE‑SUMMARY‑001 表头汇总口径约束
页面顶部`Pallets/Packages/Weight/Volume`汇总字段，**仅统计当前激活Tab内明细数据**，杜绝表头数值与明细脱节（例如表头Pallets=0、明细录入10托盘的异常）。

---

# 5. Cargo Line 三视图约束
Sprint48必须遵循架构：
```
Cargo Line
    |
-----------------
Container View
Pallet View
Piece View
```
底层共用数据表：`transport.cargo.line`，通过枚举字段`cargo_category`区分C1/C2/C3，**不新建多张明细表**。

## 5.1 Request
Request 是货物源数据：
```
transport_request.cargo_line_ids
```
负责：
- 明细录入
- 分视图自动汇总计算
- 全矩阵业务校验

## 5.2 Inquiry / Quote
只允许摘要投影：
字段：
```
description
qty
weight
volume
amount
```
禁止重新定义货物结构、禁止新增货物维度字段；报价阶段仅读取Request已校验完成的数据。

## 5.3 Order
Order创建时必须快照复制：
```
Cargo Type
Cargo Lines
Weight
Volume
Quantity
Business Rules Result
```
订单快照永久固化，后续上游Transport Request修改不回写已生成Order，保障结算历史稳定可追溯。

---

# 6. 测试要求
## 6.1 正向测试（必须全覆盖）
### Container
```
C1+D2+E1+F2
```
T1整柜运输

### Pallet
```
C2+D2+E2+F2
```
托盘普通干线配送

### Piece
```
C3+D3+E2+F2
```
普通快递末端配送

补充正向用例清单：
1. C1+D1+E2+F2：自有车队普通整柜运输
2. C2+D1+E1+F1：自有危化资质车队承接T1危险品托盘运输
3. C3+D2+E2+F2：第三方卡车零担普货散件

## 6.2 负向测试（必须全部拦截）
```
C1+D3
C3+E1
D3+E1
D3+F1
E1 + support_t1=false
F1 + support_dg=false
同一运单同时录入C1+C2明细
```
每个反向用例分别执行：前端提交、API调用、Excel导入三种入口，确认全部拦截。

---

# 7. 与TLMS领域模型关系
业务矩阵驱动完整链路：
```
Business Matrix（规则基线）
        ↓
Transport Request
        ↓
Cargo Line（三视图结构化数据）
        ↓
Inquiry
        ↓
Quote
        ↓
Transport Order（固化快照）
        ↓
Transport Event（事件留痕）
        ↓
Transport Charge（维度差异化计费）
        ↓
Carrier Settlement（承运商结算）
```

---

# 8. 设计原则总结
TLMS不是：
```
576个固定运输流程
```
而是：
```
8个运输场景
+
6个业务维度
+
刚性规则校验
+
事件驱动
+
统一Cargo模型 + 三视图隔离交互
```
通过组合化方式覆盖欧洲3PL复杂运输业务；把复杂度封装在后台规则层，前端操作人员界面简洁、选项可控。

# 9. 版本管控说明
1. 本文档为开发冻结基线，Codex所有运输模块开发必须优先读取本文约束；
2. 维度枚举、刚性互斥规则修改必须**业务负责人+架构师双审批**；
3. 迭代新增场景、承运商仅在主数据配置层维护，不改动底层代码；
4. 配套自动化测试用例随本文档同步更新，测试通过率100%方可上线。

---

# Document Version
Version:
```
V1.0
```
Status:
```
Development Baseline
```
Effective Sprint:
```
Sprint48
```