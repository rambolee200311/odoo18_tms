# INT-TMS-SPRINT52FIX-003 Execution Record

## 问题

- Inquiry 的 `accepted` 状态实际表达“选定获胜承运商”，事件仍使用
  `INQUIRY_ACCEPTED`，与领域语义不符；
- Customer Quote 状态机包含 issued/approved/confirmed 等驱动状态，
  communication 与 workflow 耦合；
- Supplier Order 缺少强制追溯链约束与 `ORDER_CREATED` 事件；
- 存量 inquiry 27 条 / quote 25 条需按新状态机迁移并回填元数据。

## 修复

- `transport_inquiry.py`：状态收敛为
  draft / sent / responded / selected / rejected / closed；
  `action_select()` 使用新增 `INQUIRY_SELECTED`，回填
  `selected_carrier_id`；`action_respond()` 记录 `response_date`；
  过期询价改为 `close(reason=expired)`，不再使用 expired 状态。
- `transport_quote.py`：状态收敛为 draft / accepted / rejected / closed；
  新增 `communication_status / accepted_by / accepted_date`；
  `QUOTE_SENT / QUOTE_ISSUED / QUOTE_APPROVED` 仅审计不驱动 state；
  `action_accept()` 校验 selected inquiry 并回填接受元数据；
  `action_close()` 使用 `QUOTE_CLOSED`；
  `_auto_create_order()` 强制 accepted quote + selected inquiry + carrier，
  禁止同一 quote 重复建单，回填 `total_carrier_cost / source_amount_carrier`，
  并写入 `ORDER_CREATED` 事件。
- `transport_order.py / pickup_plan.py`：inquiry 引用状态
  `accepted` → `selected`。
- 新增 transient wizard：
  `tlmp.create.carrier.inquiry.wizard`（选承运商 + 成本 + 响应日期，
  创建后留在 request 页面）；
  `tlmp.create.customer.quote.wizard`（margin 复用
  `tlmp.service_margin_rate`，允许 service_fee 与人工覆盖）。
- 事件码：新增 `INQUIRY_SELECTED / QUOTE_CLOSED / ORDER_CREATED`；
  `INQUIRY_ACCEPTED` 标记 deprecated；历史 ledger 不重写。
- 迁移 `1.0.126`：
  - inquiry accepted → selected（24 条）；
  - quote sent/issued → draft + communication_status=sent；
  - quote approved/confirmed → accepted；
  - accepted quote 按 ledger `QUOTE_ACCEPTED / QUOTE_CONFIRMED` 时间回填
    `accepted_by / accepted_date`，无 ledger 时回填 create 元数据；
  - order 追溯回填 `carrier_id / inquiry_id`，quote 回填
    `transport_order_id`，inquiry 回填 `selected_quote_id`。
- `__manifest__.py`：1.0.125 → 1.0.126。

## 存量边界

历史 quote 646（原 confirmed）已迁移为 accepted；其 inquiry 844 原为
draft，迁移不重算历史结论、不篡改 ledger。若后续尝试为该 quote 建单，
会被“accepted quote 必须引用 selected inquiry”约束拦截。

## 验证

| Check | Result |
| :--- | :--- |
| py_compile / XML parse | PASS |
| XML-RPC button_immediate_upgrade | PASS（18.0.1.0.125 → 18.0.1.0.126） |
| 升级日志 ERROR / CRITICAL / TRACEBACK | 0（仅 worlddepot 既有 DeprecationWarning） |
| inquiry 状态分布 | draft 2 / sent 1 / selected 24 = 27 |
| quote 状态分布 | accepted 25 |
| quote 646 元数据 | accepted + accepted_by/accepted_date 已回填 |
| order 追溯链 | 25/25，无 carrier/inquiry/quote link 缺失 |
| 事件码 | INQUIRY_SELECTED / QUOTE_CLOSED / ORDER_CREATED 存在；INQUIRY_ACCEPTED deprecated |
| S2/S3 新链回归 | PASS（wizard inquiry → selected → wizard quote → accepted → order → closed） |
| Quote/Order fee line | 480 / 380 双向行一致 |
| ORDER_CREATED ledger | 存在 |
| 新会话二次核验 | PASS |
| 8089 端口 | 已释放 |

## 数据（回归链）

| 对象 | ID |
| :--- | :--- |
| Request | 3807 |
| Inquiry | 1097 |
| Quote | 840 |
| Order | 2663 |

## 遗留

- BUSINESS-DEBT-001 v2 / BUSINESS-DEBT-002 已登记；
- quote 646 为历史边界记录，后续建单需按新流程重新询价/选商；
- 下一子意图：Sprint52-G。

## 补充修复（wd_tlms 1.0.127，2026-08-10）

- request 表单 Inquiry & Quote 页新增 Actions 按钮栏：
  `Start Inquiry`（action_create_carrier_inquiry）与
  `Start Quote`（action_create_customer_quote）；
- 页面按钮不再因 `has_accepted_quote / has_selected_inquiry` 隐藏，
  业务校验仍由 wizard 与模型方法强制；
- 表单 header 文案同步为 Start Inquiry / Start Quote；
- 升级 1.0.126 → 1.0.127 PASS，已加载视图确认按钮栏存在。

## INT-TMS-SPRINT52FIX-003 Contract Compliance Evidence

1. **Request → N Inquiry**
   - 数据库核对：request 3780 关联 2 条 carrier inquiry
     （1069 sent / 1070 draft），`request_id` 关联正确；
   - 新链回归 request 3807 关联 inquiry 1097（selected），
     wizard 创建后仍停留在 request 页面且关联保持。
2. **Inquiry 成本/响应字段**
   - inquiry 1097：`carrier_id=24627`、`total_amount=380.0`、
     `response_date=2026-08-10 02:58:40`、
     `vehicle_qualification_result=pass`；
   - 状态流：wizard 创建后 responded → `action_select()` 后 selected。
3. **Selected Inquiry → Quote source 强绑定**
   - quote 840 的 `inquiry_id=1097` 且 `inquiry.state=selected`；
   - 对 draft inquiry 调用 `action_create_quote()` 被拦截：
     `UserError('Select a winning carrier first (Inquiry state = Selected).')`。
4. **Quote → Order 唯一建单**
   - quote 840 关联 order 数量为 1；
   - 重复调用 `quote._auto_create_order()` 返回同一 order 2663，
     未产生第二条 supplier order。
5. **Historical ledger 保留**
   - 迁移脚本未写入/修改 `tlmp_transport_event_ledger`；
   - 历史 quote 646 ledger 记录数为 0（原无 QUOTE_ACCEPTED/CONFIRMED
     ledger，迁移不补造事件，仅回填 metadata）；
   - 新链 ledger 顺序为 ORDER_CREATED → ORDER_CONFIRMED →
     ORDER_ALLOCATED → ORDER_IN_TRANSIT → POD_RECEIVED →
     ORDER_DELIVERED → ORDER_POD_CONFIRMED → DELIVERY_COMPLETED →
     ORDER_SETTLEMENT_PENDING → ORDER_CLOSED，共 10 条。
6. **Freeze exception 合规**
   - `INT-TMS-SPRINT52FIX-003` v1.3 已记录 freeze_exception 范围：
     inquiry/quote 状态枚举、quote metadata 字段、新事件码；
   - `business_owner_approval / architect_approval` 已按用户
     2026-08-10 指令标记 approved；
   - 冻结清单其余对象（matrix / vehicle / allocation snapshot、
     Request/Order 状态机）未修改。
