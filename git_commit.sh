#!/bin/bash
# ==============================================
# AI软件工程标准化 Git 迭代提交脚本
# v2 — 集成产出语法门禁
# ==============================================

cd "$(dirname "$0")"

# Step 1: 运行产出语法门禁
echo ">>> 运行产出语法门禁..."
python3 verify.py
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 门禁未通过，拒绝提交。修复后重试。"
    echo "   如需强制提交: git_commit.sh --force"
    exit 1
fi

# Step 2: 读取用户输入迭代说明
echo ""
echo "请输入本次Sprint迭代描述："
read commit_msg

# Step 3: 标准提交流程
git add .
git commit -m "Sprint Iteration: $commit_msg

【AI工程资产更新】
1. 同步代码变更
2. 同步context认知资产
3. 同步迭代日志/决策记录
4. 遵循意图契约Scope边界开发"

# Step 4: 推送到主分支
git push origin main

echo "✅ 迭代提交完成，版本快照已固化！"
