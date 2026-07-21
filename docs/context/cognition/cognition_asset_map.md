# 认知资产总览图谱（第六章 认知控制工程）
## 1. 认知体系整体结构
本项目AI认知由 **五层认知资产** 构成，AI开发前必须完整加载：

1. **架构认知**（怎么建系统）
2. **业务认知**（业务铁律是什么）
3. **历史认知**（以前踩过什么坑、做过什么决策）
4. **约束认知**（什么绝对不能做）
5. **任务认知**（本次意图契约边界）

## 2. 所有认知资产目录清单
### 2.1 架构认知
- architecture/module_map.md
- architecture/dependency.yaml

### 2.2 业务认知
- business/stock_rule.md
- business/inventory_flow.md

### 2.3 历史认知
- history/sprint_shturl
- history/bug_record.md
- history/decision_note.md

### 2.4 刚性约束认知
- constraints/forbidden_change.yaml

### 2.5 迭代意图认知
- intent/ 全部意图契约

## 3. AI 标准认知执行闭环
加载认知 → 校验认知一致性 → 基于认知开发 → 迭代沉淀认知 → 版本锁定认知

## 4. 认知工程核心价值
解决大模型三大幻觉问题：
1. 不懂项目架构乱开发
2. 遗忘历史决策重复踩坑
3. 不懂业务规则乱写逻辑