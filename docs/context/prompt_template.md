# AI Agent Sprint 启动提示词模板

## 标准模板

```
## 任务基准
启动 {Sprint名称}。

## 前置加载
首先执行 `python3 execution/scripts/context_loader.py` 加载上下文认知快照，
读取当前基线版本、资产状态、历史教训。
（loader 输出仅保留控制台日志作为启动凭证，不将全文加载入对话）

## 契约绑定
绑定意图契约：docs/context/intent/{intent_yaml}
基线上下文版本：context_version = {版本号}

## 迭代类型
{类型描述}

## 画像说明
本次迭代类型为「{profile_label}」，
context_loader.py 将按此画像决定深度扫描的资产范围：
- {深度扫描资产1}
- {深度扫描资产2}
- 其余资产仅做行数统计（轻量扫描）
```

## Profile 画像速查

| Sprint 类型 | profile | 深度扫描资产 | 适合场景 |
|---|---|---|---|
| 新功能开发 | development | architecture, business, constraints | 添加业务模型、视图、逻辑 |
| 测试覆盖 | testing | history, validation, test_lessons | 写单元测试、修复测试 |
| Bug修复 | bugfix | bug_record, constraints, test_lessons | 排查和修复缺陷 |
| 基础设施重构 | infrastructure | governance, architecture/dependency | 重构工程工具、门禁脚本 |
| 全量审计 | full | 全部资产 | 跨迭代资产整理、全量审查 |

## 配套规则

1. **loader只出快照**：以 loader 输出的摘要、风险为准，资产原文仅在开发中按需 `cat` 读取
2. **token控制**：单次 loader 输出约 300-400 tokens，不预载资产全文
3. **迭代结束**：更新 decision_note.md，如有新教训同步更新 test_lessons.yaml
