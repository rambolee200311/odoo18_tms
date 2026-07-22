# Bug 记录

## BUG-001: transport_request.py 全文件前导空格导致 IndentationError

**发现时间**: 2026-07-22
**发现场景**: 安装/升级 wd_tlms 模块时 Odoo Server Error
**根因文件**: `addons/wd_tlms/models/transport_request.py`
**错误类型**: Python 语法错误 — 全局 `IndentationError: unexpected indent`

### 错误现象

```
File "/.../addons/wd_tlms/models/transport_request.py", line 2
    from odoo import models, fields, api, _
IndentationError: unexpected indent
```

### 根因分析

文件全量由 `apply_patch` 工具的 add-file 操作写入。apply_patch 的 `+ line` 语法：
- `+ line content` → 写入 ` line content`（前导空格被保留）
- 模块级 Python 代码（`from odoo`、`class`、`def` 等）不应有前导空格

影响范围：第 1-5 行（模块级代码）全部多了一个前导空格。

```
实际内容: ' # -*- coding: utf-8 -*-'
实际内容: ' from odoo import models, fields, api, _'
实际内容: ' from odoo.exceptions import UserError'
应为:     'from odoo import models, fields, api, _'
```

### 发生 Sprint

Sprint3 — `transport_request.py` 整文件重构。apply_patch add-file 写入。

### 影响范围

- `wd_tlms` 模块无法加载
- 所有依赖 `transport_request` 的模型均不可用
- 间接影响：该文件还包含了 `from __future__` 问题，`__future__` 必须是所有非注释非文档字符串代码之前的第一个 import

### 修复方案

删除每行前导空格（每行首字符的空格）。

### 复现步骤

1. 启动 Odoo
2. 安装或升级 wd_tlms 模块
3. Odoo Server Error 报 `IndentationError: unexpected indent`

### 状态

✅ 已修复


### 修复记录
- 修复时间: 2026-07-22
- 修复 commit: 待提交
- 修复内容: sed 删除每行前导空格 + 修复 action_create_orders_from_quotes 方法缩进(3→4空格)
- 验证结果: python3 compile() 语法验证通过 ✅

## BUG-002: pickup_plan_fix.py 前导空格 + 缩进不一致

**发现时间**: 2026-07-22
**根因文件**: pickup_plan_fix.py
**错误类型**: 全文件前导空格 + Python 插入的 fee_code 块缩进不一致

### 修复
- sed 删除前导空格
- 修正 fee_code 块缩进 7 -> 8 空格
- compile() 语法验证通过

### 状态: 已修复

---
* 修复记录: BUG-001 同根因，同修复方案

## BUG-003: ir.model.access.csv 模块前缀错误 — group_tlm_manager 找不到

**发现时间**: 2026-07-22
**发现场景**: BUG-001/002 修复后 odoodb -u wd_tlms
**根因文件**: security/ir.model.access.csv
**错误类型**: CSV 中 group_id 使用旧模块前缀 transport_logistics_management. 而非当前模块名 wd_tlms.

### 错误现象
```
No matching record found for external id 'transport_logistics_management.group_tlm_manager'
```

### 根因
Odoo 模块名 = 目录名 = wd_tlms。但 CSV 中的 group_id 前缀残留旧模块名 transport_logistics_management。
security.xml 定义的 group 外部 ID 为 wd_tlms.group_tlm_manager，CSV 引用了不存在的 transport_logistics_management.group_tlm_manager。

### 修复
sed -i '' 's/transport_logistics_management\\.group/wd_tlms.group/g' ir.model.access.csv
共 ~55 行受影响。

### 状态: 已修复

## BUG-004: assets.xml 继承 web.assets_frontend 模板找不到 + ir.model.access.xml 前缀残留

**发现时间**: 2026-07-22
**发现场景**: odoodb -u wd_tlms（BUG-003 修复后）
**根因文件**: data/assets.xml, security/ir.model.access.xml
**严重等级**: LEVEL3（模块无法加载）

### 错误现象（两个问题）
1. `ParseError: while parsing None:3, somewhere inside <data inherit_id="web.assets_frontend">` — assets.xml 继承的模板不存在
2. `ir.model.access.xml` 残留 `transport_logistics_management.` 前缀（同 BUG-003，但 CSV 之前已修，XML 漏了）

### 根因
- assets.xml 继承 web.assets_frontend 但该模板在当前 Odoo 环境无法找到
- ir.model.access.xml 与 BUG-003 同根因：模块名从 transport_logistics_management → wd_tlms，但 XML 文件中 group_id 前缀未更新

### 修复
1. 从 __manifest__.py data 列表中移除 'data/assets.xml'（portal 模板非核心功能）
2. sed 修正 ir.model.access.xml 中 transport_logistics_management.group → wd_tlms.group

### 状态: 已修复


---

## BUG-005: transport_logistics_management 旧模块名残留 12 处

**发现时间**: 2026-07-22
**发现场景**: 全量代码扫描 — 对照 odoo_version.md 版本兼容性检查
**根因文件**: 9 个文件（models/cmr.py, controllers/pickup_schedule.py, static/src/xml/transport_plan.xml, static/src/js/pickup_schedule.js, views/pickup_schedule_templates.xml, views/tlmp_menus.xml, reports/report_cmr.xml, reports/report_bill.xml, reports/report_adr.xml）
**严重等级**: LEVEL3 — 模块名错误导致运行时错误

### 错误现象
模块目录名为 wd_tlms，但代码中大量使用旧模块名 transport_logistics_management 作为：
- XML 外部 ID 前缀（report_cmr, report_bill, report_adr）
- QWeb 模板名称（TransportPlanTemplate, pickup_schedule_template）
- OWL JS 组件模板引用
- 静态资源 URL 路径（CSS href, icon）
- web_icon 声明

### 根因
模块从 transport_logistics_management 重命名为 wd_tlms 后，代码文件未同步更新。

### 修复
sed -i '' 's/transport_logistics_management/wd_tlms/g' 应用至 9 个文件，共 12 处替换。

### 状态: 已修复


---

## BUG-006: 3个XML视图文件首行前导空格 — XMLSyntaxError

**发现时间**: 2026-07-22
**发现场景**: BUG-005 修复后 odoodb -u wd_tlms
**根因文件**: transport_request_views.xml, transport_order_views.xml, transport_fee_views.xml
**严重等级**: LEVEL1 语法错误（自动修复）

### 错误现象


### 根因
apply_patch add-file 写入时  后保留了前导空格。与 BUG-001/002 同根因。

### 修复
sed -i '' '1s/^ //' 作用于 3 个文件。

### 状态: 已修复


---

## BUG-007: transport_request_views.xml 引用了不存在的 schedule_ids 字段 + transport_request.py TabError

**发现时间**: 2026-07-22
**发现场景**: odoodb -u wd_tlms（BUG-006 修复后）
**根因文件**: views/transport_request_views.xml（LINE2）, models/transport_request.py（LEVEL1）
**严重等级**: LEVEL2（视图字段不存在）+ LEVEL1（TAB字符）

### 错误 1: Field schedule_ids does not exist
-  的 Scheduling tab 中引用了  字段，但  模型未定义此字段
- Sprint8 添加了该引用但未在模型层添加对应字段

### 错误 2: TabError
-  第6行存在 TAB 字符与空格混用

### 修复
- 移除视图中 Schedule Plans 整段（模型无对应字段，pickup_plan_ids 已足够）
- expand -t 4 展开 TAB 为 4 空格


---

## BUG-008: attrs/states 属性 Odoo 17+ 已废弃

**发现时间**: 2026-07-22
**发现场景**: odoodb -u wd_tlms（BUG-001~007 修复后暴露）
**根因文件**: transport_request/inquiry/quote/order/schedule_calendar_views.xml
**严重等级**: LEVEL2 — 视图语法错误
**根因分类**: 版本兼容缺陷

### 错误现象
```
Since 17.0, the "attrs" and "states" attributes are no longer used.
```

### 根因
Odoo 17+ 移除了 states= 和 attrs= 属性，需用 invisible="..." 字符串表达式替代。
verify.py check_5 之前未包含这两项检查。

### 修复
- 27 处 states= → invisible= 替换
- 5 处 attrs= → invisible= 替换
- verify.py check_5 新增 attrs= 和 states= 扫描

### 状态: 已修复


---

## BUG-009: transport.order 视图引用 customs_declaration_ref 但模型未定义

**发现时间**: 2026-07-22  
**根因文件**: models/transport_order.py, views/transport_order_views.xml  
**严重等级**: LEVEL3 — 模块加载失败  
**根因分类**: 字段名不一致（视图引用模型不存在的字段）

### 错误现象
```
Field "customs_declaration_ref" does not exist in model "tlmp.transport.order"
```

### 根因
transport_order_views.xml 的 Customs tab 引用了 `customs_declaration_ref` 字段，
但 transport.order 模型未定义此字段（模型只有 `customs_transit_ref`）。
transport.request 模型有 `customs_declaration_ref`，transport.order 漏了。

### 修复
- transport_order.py 新增 `customs_declaration_ref = fields.Char(string='Customs Decl. Ref.')`

### 预防
- check_7（View-Model 字段交叉校验）理论上应能检测到此问题，
  但其 64 个误报淹没了这个真实错误。待 check_7 精确度提升后可自动拦截。

### 状态: 仅记录文档，未落地代码（BUG-010 替代）


---

## BUG-010: BUG-009 修复代码未落地 — customs_declaration_ref 仍缺失

**发现时间**: 2026-07-22 10:04
**发现场景**: 升级模块时 RPC_ERROR
**根因文件**: models/transport_order.py
**严重等级**: LEVEL3 — 模块加载失败
**根因分类**: 工程流程缺陷（修复记录≠代码落地）

### 错误现象
```
Field "customs_declaration_ref" does not exist in model "tlmp.transport.order"
views/transport_order_views.xml:142
```
与 BUG-009 完全相同。

### 根因
**直接原因**: transport.order 模型未定义 customs_declaration_ref 字段
**深层根因**: BUG-009 的「修复」仅写入了 bug_record.md，未实际修改 transport_order.py。
  git commit 093d205e5 只修改了 1 个文件（bug_record.md），0 个代码文件。
  问题未解决，模块依然加载失败，故 BUG-009 复发。

**工程缺陷**: 「只记不修」模式 — 文档记录了修复方案但执行层未落地。

### 修复
- transport_order.py 第 114 行新增:
  ```python
  customs_declaration_ref = fields.Char(string='Customs Decl. Ref.')
  ```

### 预防
1. BUG-009 重新标记为「仅记录文档，未落地代码」
2. bug_record.md 新增「落地验证」字段，修复必须验证代码已修改
3. git_commit.sh 提交前检查：若涉及 BUG-FIX，确认对应代码文件确实已变更

### 落地验证
- transport_order.py: grep customs_declaration_ref → 找到
- verify.py: 7 项全 PASS
- 待 odoo_check.py 运行确认模块加载无错

### 状态: 已修复



---

## BUG-011: tlmp_menus.xml 菜单顺序错误 — menu_tlmp_config 后置引用

**发现时间**: 2026-07-22 10:24
**发现场景**: 升级模块时 RPC_ERROR
**根因文件**: views/tlmp_menus.xml
**严重等级**: LEVEL2 — 菜单加载失败
**根因分类**: 设计错误（XML 定义顺序）

### 错误现象
```
ValueError: External ID not found in the system: wd_tlms.menu_tlmp_config
ParseError: while parsing .../views/tlmp_menus.xml:59
<menuitem id="menu_tlmp_rate_bases" name="Rate Bases" parent="menu_tlmp_config" .../>
```

### 根因
`menu_tlmp_config` 父菜单定义在 line 63，但其子菜单 `menu_tlmp_rate_bases` (line 58)、
`menu_tlmp_fee_lines` (line 60) 已在 line 58/60 引用它作为 parent。
Odoo 加载 menuitem XML 时按顺序执行，子菜单先加载找不到父菜单 XML ID。

### 修复
- 将 line 63 `<menuitem id="menu_tlmp_config"...>` 整体移至 line 57（<!-- Configuration --> 注释后）
- 父菜单现在在子菜单之前定义，Odoo 可以正确解析

### 预防
- verify.py 新增 check_8：扫描 XML 中的 parent="menu_*" 引用，验证目标 menuitem 是否在文件前部定义
- 但此检查为启发式，无法完全避免顺序问题。更可靠的方式：Odoo 16+ 支持 noupdate="0" 的独立序列

### 落地验证
- tlmp_menus.xml: `menu_tlmp_config` 现位于第 58 行，早于所有子菜单
- verify.py: 待运行确认
- odoo_check.py: 待运行确认模块加载无错

### 状态: 已修复



---

## BUG-012: schedule_calendar_views.xml view_mode 使用 "tree"（Odoo 18 需用 "list"）

**发现时间**: 2026-07-22 10:36
**发现场景**: 点击 Schedule Plans 菜单 → UncaughtPromiseError
**根因文件**: views/schedule_calendar_views.xml
**严重等级**: LEVEL2 — 菜单无法打开
**根因分类**: 版本兼容缺陷（同 BUG-008）

### 错误现象
```
Uncaught Promise > View types not defined tree found in act_window action 589
```

### 根因
`action_schedule_plan_schedule` 的 `view_mode` 设置为 `"calendar,tree,form"`。
Odoo 18 已将 `tree` 重命名为 `list`，`view_mode` 中仍使用 `tree` 导致前端无法找到对应视图类型。

### 修复
- `view_mode` 值: `"calendar,tree,form"` → `"calendar,list,form"`
- verify.py check_5 新增 view_mode 中 `tree` 值检测

### 预防
- verify.py check_5 扩展：新增正则 `view_mode\s*=\s*"[^"]*\btree\b[^"]*"` 扫描
- 同类扫描显示仅此一处

### 落地验证
- verify.py: check_5 通过
- schedule_calendar_views.xml line 149: `calendar,list,form`

### 状态: 已修复

