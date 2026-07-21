#!/bin/bash
# ==============================================
# AI软件工程标准化 Git 迭代提交脚本
# 适配：TMS四层上下文资产 + 意图契约迭代闭环
# ==============================================

# 1. 读取用户输入迭代说明
echo "请输入本次Sprint迭代描述："
read commit_msg

# 2. 标准提交流程
git add .
git commit -m "Sprint Iteration: $commit_msg

【AI工程资产更新】
1. 同步代码变更
2. 同步context认知资产
3. 同步迭代日志/决策记录
4. 遵循意图契约Scope边界开发"

# 3. 推送到主分支
git push origin main

echo "✅ 迭代提交完成，版本快照已固化！"