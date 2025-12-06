#!/bin/bash
# ============================================
# wxkf_saas 代码增量同步脚本
# 功能：从 origin/bwx_dev 拉取最新代码（真正的增量更新）
# ============================================

set -e  # 遇到错误立即退出

# 项目目录
PROJECT_DIR="/www/wwwroot/python_project/wxkf_saas"
BRANCH="bwx_dev"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}开始增量同步代码...${NC}"
echo -e "${GREEN}========================================${NC}"

cd "$PROJECT_DIR"

# 1. 检查当前状态
echo -e "\n${YELLOW}[1/6] 检查当前 Git 状态...${NC}"
git status --short

# 2. 获取最新代码
echo -e "\n${YELLOW}[2/6] 从远程获取最新代码...${NC}"
git fetch origin "$BRANCH"

# 3. 检查是否有更新
echo -e "\n${YELLOW}[3/6] 检查代码更新...${NC}"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/"$BRANCH")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}代码已是最新，无需更新${NC}"
    exit 0
fi

echo -e "${YELLOW}发现更新，正在同步...${NC}"

# 4. 备份本地修改（如果有）
echo -e "\n${YELLOW}[4/6] 处理本地修改...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}警告：发现本地修改！${NC}"
    echo -e "${YELLOW}本地修改将被暂存...${NC}"
    git stash push -m "自动暂存 $(date)"
fi

# 5. 增量更新代码
echo -e "\n${YELLOW}[5/6] 增量更新代码...${NC}"

# 方案：使用 git merge 替代 git pull，然后清理已删除的文件
git merge origin/"$BRANCH" --no-edit --ff-only

# 5.1 同步删除远程已删除的文件（排除重要文件）
echo -e "\n${YELLOW}[5.1/6] 同步删除远程已删除的文件...${NC}"

# 获取本次 merge 中删除的文件列表
DELETED_FILES=$(git diff --name-only --diff-filter=D HEAD~1 HEAD 2>/dev/null || true)

if [ -n "$DELETED_FILES" ]; then
    echo -e "${YELLOW}发现以下文件在远程已被删除：${NC}"
    echo "$DELETED_FILES"

    # 删除这些文件，但排除重要文件
    for file in $DELETED_FILES; do
        # 检查文件是否仍然存在（可能已经被删除）
        [ ! -f "$file" ] && continue

        # 检查是否是重要文件
        if [[ "$file" == .env ]] || [[ "$file" == logs/* ]] || [[ "$file" == uploads/* ]] || [[ "$file" == *.log ]]; then
            echo -e "${YELLOW}跳过重要文件：${file}${NC}"
            continue
        fi

        # 确认删除（为了安全，添加确认提示）
        echo -e "${YELLOW}删除远程已移除的文件：${file}${NC}"
        rm -f "$file"
    done
else
    echo -e "${GREEN}没有需要删除的文件${NC}"
fi

# 6. 显示更新结果
echo -e "\n${YELLOW}[6/6] 更新完成，当前状态：${NC}"
echo -e "${GREEN}最新提交：${NC}"
git log -2 --oneline
echo ""

# 检查是否需要重启服务
echo -e "${YELLOW}检查是否需要重启服务...${NC}"
# 获取本次更新的文件列表
UPDATED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || true)

# 检查关键文件是否有更新
NEED_RESTART=false
KEY_FILES=("main.py" "core/" "api/" "models/")

for file in "${KEY_FILES[@]}"; do
    if echo "$UPDATED_FILES" | grep -q "^$file"; then
        NEED_RESTART=true
        break
    fi
done

if [ "$NEED_RESTART" = true ]; then
    echo -e "${RED}检测到核心文件更新，建议重启服务${NC}"
    echo -e "${YELLOW}重启命令示例：${NC}"
    echo "  supervisorctl restart wxkf_saas"
    echo "  # 或者"
    echo "  systemctl restart wxkf_saas"
else
    echo -e "${GREEN}仅配置文件或文档更新，无需重启服务${NC}"
fi

# 清理 Python 缓存
echo -e "\n${YELLOW}清理 Python 缓存...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}代码增量同步完成！${NC}"
echo -e "${GREEN}========================================${NC}"