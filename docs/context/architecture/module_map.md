# 模块架构地图（Module Architecture Map）

## 1. 模块组织
TMS 系统部署在 `addons/wd_tlms/` 模块中，遵循标准 Odoo 模块结构。

### 1.1 目录结构
```
wd_tlms/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── pickup_schedule.py            # 排期日历 API + 页面路由
├── data/
│   ├── assets.xml                    # 前端资源注册
│   ├── sequences.xml                 # 所有序列号
│   └── surcharge_data.xml            # 附加费基础数据
├── models/
│   ├── __init__.py                   # 导入所有模型
│   ├── carrier_settlement.py         # 承运商结算
│   ├── cmr.py                        # CMR 运单
│   ├── container_master.py           # 全局柜档案
│   ├── container_service.py          # 空柜调拨申请
│   ├── customer_bill.py              # 客户账单
│   ├── pickup_plan.py                # 提货需求 + 集装箱明细
│   ├── pod.py                        # 签收凭证
│   ├── pricing_rule.py               # 定价规则
│   ├── res_partner.py                # 伙伴扩展（承运商标记）
│   ├── surcharge.py                  # 附加费
│   ├── transport_container.py        # 运输订单集装箱明细
│   ├── transport_inquiry.py          # 承运商询价
│   ├── transport_order.py            # 运输订单（全系统统一收敛出口，Sprint4）
│   ├── transport_plan.py             # 运输排期计划
│   ├── transport_quote.py            # 客户报价
│   ├── transport_request.py          # 运输请求（商务报价入口）
│   └── transport_tracking.py         # 运输追踪
├── reports/
│   ├── report_bill.xml
│   ├── report_cmr.xml
│   └── report_adr.xml
├── security/
│   ├── ir.model.access.csv           # 模型级权限
│   ├── ir.model.access.xml           # 模型级权限（XML 格式）
│   └── security.xml                  # 安全组定义
├── static/
│   ├── description/icon.png
│   └── src/
│       ├── css/pickup_schedule.css   # 排期日历样式
│       ├── js/                       # JS 前端组件
│       │   ├── pickup_schedule.js
│       │   ├── tlmp_portal_carrier.js
│       │   ├── tlmp_portal_customer.js
│       │   └── tlmp_portal_helper.js
│       ├── scss/tlmp_portal.scss
│       └── xml/transport_plan.xml    # OWL 排期日历模板
└── views/
    ├── carrier_settlement_views.xml
    ├── cmr_views.xml
    ├── container_master_views.xml
    ├── container_service_views.xml
    ├── customer_bill_views.xml
    ├── pickup_plan_views.xml         # 提货需求表单视图
    ├── pickup_schedule_templates.xml # 排期日历 QWeb 模板
    ├── pod_views.xml
    ├── portal_carrier_templates.xml
    ├── portal_customer_templates.xml
    ├── pricing_rule_views.xml
    ├── surcharge_views.xml
    ├── tlmp_menus.xml                # 菜单导航结构
    ├── transport_container_views.xml
    ├── transport_inquiry_views.xml
    ├── transport_order_views.xml
    ├── transport_plan_views.xml      # 排期计划视图
    ├── transport_quote_views.xml
    ├── transport_request_views.xml
    └── transport_tracking_views.xml
```

## 2. 模型分层

### 2.1 单据层次（按生命周期）
```
上游单据（需求层）:
  tlmp.transport.request        —— 运输请求（全流程统一入口，Sprint3 核心）
  container.service.request     —— 空柜调拨申请

中游单据（计划/报价层）:
  transport.request → pickup.plan  —— 排期子单据（计划驱动型，Sprint1）
  transport.request → schedule.plan.schedule —— 排期计划（Sprint2）
  transport.request → tlmp.transport.inquiry —— 承运商询价（商务报价型）
  tlmp.transport.inquiry        —— 承运商询价
  tlmp.transport.quote          —— 客户报价

下游单据（执行层）:
  tlmp.transport.order          —— 运输订单
  tlmp.transport.container      —— 运输订单集装箱明细
  tlmp.transport.tracking       —— 运输追踪

签收/结算层:
  tlmp.pod                      —— 签收凭证
  tlmp.cmr                      —— CMR 运单
  tlmp.customer.bill            —— 客户账单
  tlmp.carrier.settlement       —— 承运商结算
```

### 2.2 主数据层
```
res.partner                     —— 伙伴（客户/承运商/码头）
res.company                     —— 公司
stock.warehouse                 —— 仓库
container.master                —— 全局柜档案
tlmp.pricing.rule               —— 定价规则
tlmp.surcharge.type             —— 附加费类型
```

## 3. 分层架构约束
- **模型层**: 数据定义 + 约束校验（@api.constrains）+ 业务流程方法
- **视图层**: UI 显隐控制（invisible/attrs），禁止业务逻辑
- **控制器层**: 前端 API 入口，JSON 收发
- **JS 层**: 前端交互（OWL 组件），调用 ORM API
- **禁止**: 视图层写 SQL、JS 层 bypass ORM、Controller 直写数据库

## 4. 模块外部依赖
```
wd_tlms 依赖: base, mail, stock, account, portal, contacts, product, fleet
可选引用（无硬 depends）: wd_iffm（import.pickup.requirement）
禁止依赖: wd_bonded_wms（仅信号联动，无模块依赖）
```
