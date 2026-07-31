# Common Pre-Check & Known Issues

> 适用于所有 8 个运输场景的公共预检项和已发现的共性问题。
> 执行任一场景的手工验证前，应先确认本清单全部通过。

---

## 1. 模块安装与升级

| # | Check | Expected | Status |
|---|-------|----------|--------|
| 1.1 | wd_tlms 模块已安装 | Apps → wd_tlms → Installed | [ ] |
| 1.2 | 预置数据已加载 | Configuration → Transport Scenes 应有 8 条记录 | [ ] |
| 1.3 | 模块版本 >= 1.0.60 | __manifest__.py version 字段 | [ ] |

> **如果场景下拉为空**: 在 UI 中升级 wd_tlms 模块（Apps → wd_tlms → Upgrade）。
> `data/transport_scene_data.xml` 包含 8 大场景 + 8 事件类型 + 8 货物规则预置数据。

---

## 2. 菜单可见性

| # | 菜单路径 | 预期动作 | Status |
|---|---------|---------|--------|
| 2.1 | Configuration → Transport Scenes | 列出 8 条场景记录 | [ ] |
| 2.2 | Configuration → Event Types | 列出 8 条事件类型 | [ ] |
| 2.3 | Configuration → Scene Events | 场景-事件映射管理 | [ ] |

> **如果菜单缺失**: 升级模块后刷新。

---

## 3. 权限与 ACL

以下模型在新装/升级模块后自动获得 ACL。如果出现 `Access Denied` 或字段不可见，
检查用户组是否分配正确。

| # | Model | Min Required Group | Status |
|---|-------|-------------------|--------|
| 3.1 | `tlmp.transport.scene` | base.group_user（读） | [ ] |
| 3.2 | `tlmp.transport.event.type` | base.group_user（读） | [ ] |
| 3.3 | `tlmp.transport.scene.event` | base.group_user（读） | [ ] |
| 3.4 | `tlmp.transport.flow.type` | base.group_user（读） | [ ] |
| 3.5 | `tlmp.transport.destination.type` | base.group_user（读） | [ ] |
| 3.6 | `tlmp.transport.scene.cargo.rule` | base.group_user（读） | [ ] |
| 3.7 | `tlmp.transport.cargo.line` | base.group_user（读） | [ ] |

> Manager 组有全部 CRUD 权限，Operator 组有读写权限，base.group_user 有只读权限。

---

## 4. 已知共性问题（已修复）

以下问题在 Sprint42 调试中被发现并修复，影响全部 8 个场景。

| ID | 问题 | 根因 | 修复范围 | 状态 |
|----|------|------|---------|------|
| C-001 | Transport Scene 下拉无数据 | `data/transport_scene_data.xml` 未在 manifest 注册 | `__manifest__.py` 添加 data 引用 | fixed |
| C-002 | Configuration 下无 Transport Scenes 菜单 | 菜单条目不存在 | `tlmp_menus.xml` 新增 3 个菜单 | fixed |
| C-003 | 三个场景模型无 ACL | Sprint17 创建后遗漏 | `ir.model.access.csv` 新增 21 行 ACL | fixed |
| C-004 | `tlmp_menus.xml` RelaxNG 验证失败 | `<menuitem>` 缺少 `<data>` 包裹 | 添加 `<data>` wrapper | fixed |
| C-005 | 三个 portal JS 文件 Odoo 18 不兼容 | 使用已移除的 `web.rpc`/`web.core` | 重写为 `@odoo-module` ES module | fixed |
| C-006 | `transport_request.py` 缺少 `scene_id` 字段 | Sprint40 视图引用但模型未定义 | 添加 `scene_id` Many2one 字段 | fixed |
| C-007 | Sprint38 Rule Engine 残留引用 | 删除模型后 views/menus/ACL/tests 未清理 | 11 处文件清理 | fixed |
| C-008 | `security_settlement_groups.xml` XML 结构损坏 | sed 编辑产生孤儿行 | 删除孤儿行 | fixed |
| C-009 | 无效 category XML ID | `module_category_transport_management` 不存在 | 改为 `base.module_category_transport` | fixed |
| C-010 | `sequence` 必须是 int 类型 | `tlmp_menus.xml` 中 `48.5` 等小数被 RNG `<rng:data type="int"/>` 拒绝 | 改为整数 `48/49/50` | fixed |
| C-011 | `transport_scene_views.xml` 未注册到 manifest | Sprint17 创建视图文件后忘记加入 `__manifest__.py` | 添加到 manifest 并确保 views 在 menus 之前加载 | fixed |
| C-012 | Manifest Python 语法因 sed 编辑损坏 | 多次 `sed -i` 累积导致缺 `}` 和重复行 | 用 Python 重写 manifest 编辑逻辑 | fixed |

---

## 5. 待清理项（需要手动执行）

| # | 操作 | 命令 | 状态 |
|---|------|------|------|
| 5.1 | 清理数据库残留的 Sprint38 视图/菜单/动作 | `psql -h 127.0.0.1 -p 5555 -U odoo -d odoo18e_tms -f /tmp/cleanup_sprint38.sql` | pending |

---

## 6. 场景文档索引

| Scene | 文档 | 特有 Issue 数 |
|-------|------|-------------|
| S1: Terminal → Warehouse | [scene_1_terminal_warehouse.md](scene_1_terminal_warehouse.md) | 3 |
| S2: Terminal → Customer | [scene_2_terminal_customer.md](scene_2_terminal_customer.md) | - |
| S3: Warehouse → Customer | [scene_3_warehouse_customer.md](scene_3_warehouse_customer.md) | - |
| S4: Customer A → B | [scene_4_customer_customer.md](scene_4_customer_customer.md) | - |
| S5: Warehouse ↔ Warehouse | [scene_5_warehouse_transfer.md](scene_5_warehouse_transfer.md) | - |
| S6: Customer → Warehouse (Return) | [scene_6_customer_return.md](scene_6_customer_return.md) | - |
| S7: Container Swap | [scene_7_container_swap.md](scene_7_container_swap.md) | - |
| S8: Empty Depo ↔ Warehouse | [scene_8_empty_depot.md](scene_8_empty_depot.md) | - |

---

*Last updated: 2026-07-30 | Context Version: 1.0.60*

| C-013 | Odoo shell 写操作必须 `env.cr.commit()` | shell 事务默认不回滚，`unlink` 等操作在会话结束时回滚 | 明确调用 `env.cr.commit()` 持久化 | fixed |
| C-014 | `@odoo-module` JS 文件需用精确路径加载 | glob 模式 `*.js` 可能导致 bundler 处理异常 | manifest 改用精确文件路径 | fixed |
| C-015 | XML 模版中 `&larr;`/`&rarr;` 不是合法 XML 实体 | lxml 解析器不识别 HTML 实体，导致 `Entity 'larr' not defined` | 使用 Unicode 字符（←→）或十进制实体 | fixed |
| C-016 | JS 模版方法和组件方法必须对齐 | `t-on-click="methodName"` 引用的方法在 JS 中不存在时静默失败 | 使用 inline arrow function `(ev) => method(ev, arg)` 或明确添加桥接方法 | fixed |

## 7. 参考实现

OWL 日历拖拽排期组件请参考 `addons/transport/static/src/js/transport_plan/transport_plan.js`：
- `@odoo-module` 后必须空行
- 必须 `export class ComponentName extends Component`
- 必须 `export { ComponentName }`
- 模版事件用 inline arrow function：`t-on-click="(ev) => methodName(ev, arg)"`
- manifest 用精确路径而非 glob

## 8. 地址架构预检（Sprint44/45）

> 验证前确认以下地址架构能力已部署（版本 ≥ 1.0.90）。

| # | Check | Expected | Status |
|---|-------|----------|--------|
| 8.1 | Scene 有 origin_type / destination_type | Configuration → Transport Scenes 每行可见 | [ ] |
| 8.2 | 8 场景起终点类型正确 | 见下方映射表 | [ ] |
| 8.3 | Request 表单有 Origin/Destination Address 组 | 选场景后显示 | [ ] |
| 8.4 | terminal_id 自动填充 origin 地址 | 选 terminal 后 street/zip/city 自动填 | [ ] |
| 8.5 | warehouse_id 自动填充 destination 地址 | 选 warehouse 后自动填 | [ ] |
| 8.6 | Order 创建时地址快照正确 | 创建后检查 Order 地址 | [ ] |
| 8.7 | Order 确认后地址只读 | confirm 后无法改地址 | [ ] |

### 8 场景起终点类型映射（Sprint44）

| Scene | code | origin_type | destination_type |
|-------|------|-------------|-----------------|
| S1 Terminal → Warehouse | terminal_to_warehouse | terminal | warehouse |
| S2 Terminal → Customer | terminal_to_customer | terminal | customer |
| S3 Warehouse → Customer | warehouse_to_customer | warehouse | customer |
| S4 Customer A → B | customer_to_customer | customer | customer |
| S5 Warehouse ↔ Warehouse | warehouse_transfer | warehouse | warehouse |
| S6 Customer Return | customer_to_warehouse | customer | warehouse |
| S7 Container Swap | container_swap | terminal | warehouse |
| S8 Empty Depot | empty_depot | depot | warehouse |

## 9. Transport Type 自动推导说明

Transport Type（port_to_warehouse / warehouse_transfer 等）由场景自动推导，
不需要用户单独设置。Prerequisites 中不再列出 Transport Type。
