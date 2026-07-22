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
