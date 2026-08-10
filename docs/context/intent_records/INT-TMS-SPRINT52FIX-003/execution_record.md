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
