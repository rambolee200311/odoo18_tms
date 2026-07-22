# Odoo 版本变更全记录 (15 → 16 → 17 → 18)

## 当前版本
- **Odoo 18.0** Final Release (`version_info = (18, 0, 0, FINAL, 0, '')`)
- 源码路径: `/Users/lijianqiang/Documents/odoo18_tms/odoo/`
- 版本后缀: `e-20250619`
- 本项目直接从 Odoo 18 开发，不涉及降级

---

## 一、Odoo 15 → 16 变更

### 1.1 技术栈
| 项目 | Odoo 15 | Odoo 16 |
|------|---------|---------|
| Python | 3.7 - 3.10 | 3.10+ |
| JS 框架 | OWL + jQuery 共存 | **OWL 为默认**，jQuery 大幅减少 |
| SCSS | Bootstrap 4 | Bootstrap 4 |
| PostgreSQL | 10+ | 12+ |

### 1.2 ORM / 模型层
- **`fields.Command()`** 引入 — 操作 One2many/x2many 的标准方式
  ```python
  # Odoo 16+: (0, 0, vals), (1, id, vals), (2, id), (3, id), (4, id), (5,), (6, 0, ids)
  # Odoo 15-: 同格式，但无 Command 枚举类
  ```
- **`selection` 字段属性改为可调用** — `selection=lambda self: ...` 支持度提升
- **`compute_sudo` 参数** — compute 字段默认使用当前用户权限，需显式 sudo
- **`related_sudo` 参数** — related 字段默认不 sudo
- **`@api.depends` 支持嵌套字段路径** — `line_ids.product_id.uom_id`
- **`_rec_name` 默认值** — 从 `name` 改为 `display_name`（部分模型）

### 1.3 视图层
- **OWL 组件替代大部分 jQuery Widget** — `widget="many2many_tags"` 等改用 OWL 实现
- **`widget="dashboard_graph"`** 替换旧的图表渲染方式
- **表单视图 `readonly_bg` 属性** — 新增，只读字段灰色背景
- **`ir.actions.act_window` 新增 `target="inline"`**
- **`<group>` 布局优化** — `colspan` 属性行为调整

### 1.4 邮件模块
- **`mail.thread` 重构** — 消息分区（inbox/starred/archived）
- **`mail.activity.mixin` 状态机增强** — activity 状态跟踪改进
- **`mail.template` 模板引擎** — 支持 Jinja 语法

### 1.5 联系人 / 地址
- **`res.partner` 地址内联化** — street/street2/city/state_id/zip/country_id 成为 partner 直接字段（不再依赖单独地址模型）
- **`child_ids` 和 `parent_id`** — 联系人层级管理增强

### 1.6 报表
- **QWeb PDF 渲染引擎更新** — 依赖的 wkhtmltopdf 版本变化
- **`ir.actions.report`** 新增 `print_report_name` 动态文件名

### 1.7 安全性
- **`ir.rule` 全局规则变化** — 全局（无 group 的）规则行为调整，权限评估顺序变化
- **Demo 数据保护** — demo 模式与非 demo 模式数据隔离增强

---

## 二、Odoo 16 → 17 变更

### 2.1 视图标签——重大变更

| 项目 | Odoo 16 | Odoo 17 | 本项目状态 |
|------|---------|---------|-----------|
| 列表视图标签 | `<tree>` | **`<tree>` 维持，但建议使用 `<list>`** | ✅ 全部使用 `<list>` |
| 搜索视图 | `<search>` | 无变化 | ✅ |
| 表单视图 | `<form>` | 无变化 | ✅ |

> Odoo 17 引入了 `<list>` 作为 `<tree>` 的别名，两个标签均可使用。
> Odoo 18 移除 `<tree>`，仅 `<list>` 有效。

### 2.2 Widget 重命名

| Odoo 16 | Odoo 17 | 本项目 |
|---------|---------|--------|
| `widget="state_selection"` | **`widget="badge"`** | ✅ 使用 `badge` |
| `widget="badge"` | 无变化 | ✅ |

### 2.3 装饰器属性重命名

| Odoo 16 | Odoo 17 | 本项目 |
|---------|---------|--------|
| `decoration-bf` | **`decoration-bold`**（废弃 bf） | ✅ 未使用 |
| `decoration-it` | **`decoration-italic`**（废弃 it） | ✅ 未使用 |
| `decoration-success/info/warning/muted/danger` | 无变化 | ✅ |

### 2.4 表单视图变化
- **`readonly_bg` 属性移除** — 不再支持在视图中设置只读字段背景色
- **`invisible="..."` 表达式增强** — 支持更多 Python 表达式
- **`<notebook>` 页签** — 新增 `name` 属性支持

### 2.5 模型 / ORM 变化
- **Monetary 字段的 `currency_field` 默认值增强** — 自动检测同模型 `currency_id` 字段
- **`@api.onchange` 行为变化** — 不再清空未返回的字段
- **`Model.load()` 方法移除** — 使用 `Model.create()` 替代
- **`_order` 属性支持二级排序** — `'date desc, id desc'`

### 2.6 邮件模块
- **`mail.thread` 进一步重构** — 活动/消息分区逻辑优化
- **`mail.activity.mixin` 通知机制变化**
- **`mail.channel` 跨模块集成增强**

### 2.7 财务模块
- **`account.move` 行级会计** — `account.move.line` 结构优化
- **税务引擎重构** — 简化多税叠加逻辑

### 2.8 其他
- **`spreadsheet` 模块** — 新增在线电子表格功能
- **`website` 多语言路由优化**
- **`base` 模块的国家/州数据 API 变化** — `res.country.state` 编码格式调整
- **`snailmail` 集成** — 邮件打印与邮寄服务

---

## 三、Odoo 17 → 18 变更

### 3.1 视图标签——最终移除

| Odoo 17 | Odoo 18 | 本项目 |
|---------|---------|--------|
| `<tree>` | **`<list>`（仅此项）** | ✅ 全部使用 `<list>` |
| `<tree>` 的 `colors` 属性 | 移除 | ✅ 未使用 |
| `<tree>` 的 `fonts` 属性 | 移除 | ✅ 未使用 |

### 3.2 本项目 XML 扫描结果
```
转义引号 `\`                          → 无残留
旧版 `<tree>` 标签                     → 0 处
旧版 `decoration-bf/it`                → 0 处
旧版 `colors`/`fonts` 属性             → 0 处
旧版 `decimals` 属性                   → 0 处
旧版 `widget="state_selection"`         → 0 处
旧版 `states=` / `attrs=` 属性       → ✅ 0 处（BUG-008 已修复，verify.py check_5 已覆盖）
`widget="monetary"` 无 `currency_field` → 需确认（已满足模型默认关联）
`options=` 格式                        → 已验证正确
`sum=` 属性                            → 使用正确
```

### 3.3 模块依赖
```python
depends: base, mail, stock, account, portal, contacts, product, fleet, worlddepot
```
- `worlddepot` 卡点: `web.assets_frontend` 模板继承失败（BUG-004），已移除 `data/assets.xml`

### 3.4 已知 Bug
- BUG-001: `transport_request.py` 前导空格（apply_patch 写入格式问题）
- BUG-002: `pickup_plan_fix.py` 前导空格 + 缩进不一致
- BUG-003: `ir.model.access.csv` 模块前缀 `transport_logistics_management.` → `wd_tlms.`
- BUG-004: `data/assets.xml` 继承 `web.assets_frontend` 失败 + `ir.model.access.xml` 前缀残留

---

## 四、版本关键行为速查

### 视图标签各版本兼容性

| 标签 | 15 | 16 | 17 | 18 |
|------|----|----|----|----|
| `<tree>` | ✅ | ✅ | ✅ | ❌ |
| `<list>` | ❌ | ❌ | ✅ 别名 | ✅ 唯一 |
| `<search>` | ✅ | ✅ | ✅ | ✅ |
| `<form>` | ✅ | ✅ | ✅ | ✅ |

### Widget 各版本兼容性

| Widget | 15 | 16 | 17 | 18 |
|--------|----|----|----|----|
| `badge` | ❌ | ❌ | ✅ | ✅ |
| `state_selection` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `monetary` | ✅ | ✅ | ✅ | ✅ |
| `statusbar` | ✅ | ✅ | ✅ | ✅ |
| `many2many_tags` | ✅ | ✅ | ✅ | ✅ |

### 装饰器各版本兼容性

| 装饰器 | 15 | 16 | 17 | 18 |
|--------|----|----|----|----|
| `decoration-bf` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `decoration-bold` | ❌ | ❌ | ✅ | ✅ |
| `decoration-it` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `decoration-italic` | ❌ | ❌ | ✅ | ✅ |
| `decoration-*` 其他 | ✅ | ✅ | ✅ | ✅ |

### 属性各版本兼容性

| 属性 | 15 | 16 | 17 | 18 |
|------|----|----|----|----|
| `colors=""` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `fonts=""` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `decimals=""` | ✅ | ✅ | ⚠️ 部分支持 | ⚠️ 部分支持 |
| `sum=""` | ✅ | ✅ | ✅ | ✅ |
| `widget=""` | ✅ | ✅ | ✅ | ✅ |
| `options=""` | ✅ | ✅ | ✅ | ✅ |
| `attrs=""` | ✅ | ✅ | ✅ | ✅ |
| `states=""` | ✅ | ✅ | ✅ | ✅ |
| `invisible=""` | ✅ | ✅ | ✅ | ✅ |
| `states=""` / `attrs=""` | ✅ | ✅ | ❌ 废弃 | ❌ 移除 |
| `readonly=""` | ✅ | ✅ | ✅ | ✅ |
| `colspan=""` | ✅ | ✅ | ❌ 废弃 | ❌ 废弃 |

---

## 五、版本风险地图

### 本项目的版本敏感代码

| 文件 | 使用特性 | 适配 Odoo 18 状态 |
|------|---------|------------------|
| 所有视图 XML | `<list>` 替代 `<tree>` | ✅ 已适配 |
| 所有视图 XML | `widget="badge"` 替代 `state_selection` | ✅ 已适配 |
| 所有视图 XML | 使用新版 decoration 名 | ✅ 已适配 |
| JS 组件 | OWL 组件模式 | ✅ Odoo 18 原生 |
| 模块清单 | Odoo 18 manifest 格式 | ✅ 已适配 |
| 安全 CSV | 模块前缀正确 | ✅ BUG-003 已修复 |
| 数据文件 | `data/assets.xml` | ⚠️ 已移除（BUG-004） |

### 参考来源
- Odoo 15, 16, 17, 18 官方 release notes
- Odoo 18 源码 (`/odoo/release.py` 确认为 18.0)
- 本项目运行错误日志（BUG-001 ~ BUG-004）
