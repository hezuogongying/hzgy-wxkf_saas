#!/bin/bash
# ============================================
# wxkf_saas 代码同步脚本
# 功能：从 origin/bwx_dev 拉取最新代码（增量更新+同步删除）
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
echo -e "\n${YELLOW}[1/7] 检查当前 Git 状态...${NC}"
git status --short

# 2. 获取最新代码
echo -e "\n${YELLOW}[2/7] 从远程获取最新代码...${NC}"
git fetch origin "$BRANCH"

# 3. 检查是否有更新
echo -e "\n${YELLOW}[3/8] 检查代码更新...${NC}"
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/"$BRANCH")

if [ "$LOCAL" = "$REMOTE" ]; then
    echo -e "${GREEN}代码已是最新，无需更新${NC}"
    exit 0
fi

echo -e "${YELLOW}发现更新，正在同步...${NC}"

# 4. 备份重要文件（如果有）
echo -e "\n${YELLOW}[4/8] 备份重要文件...${NC}"
BACKUP_DIR="/tmp/wxkf_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 备份可能存在的重要文件
[ -f .env ] && cp .env "$BACKUP_DIR/" 2>/dev/null || true
[ -d logs/ ] && cp -r logs/ "$BACKUP_DIR/" 2>/dev/null || true
[ -d uploads/ ] && cp -r uploads/ "$BACKUP_DIR/" 2>/dev/null || true

# 5. 检查并处理本地修改
echo -e "\n${YELLOW}[5/8] 检查本地修改...${NC}"
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}警告：发现本地修改！${NC}"
    echo -e "${YELLOW}本地修改将被暂存...${NC}"
    git stash push -m "自动暂存 $(date)"
fi

# 6. 同步代码（包括删除远程已删除的文件）
echo -e "\n${YELLOW}[6/8] 同步代码（包括删除）...${NC}"
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

# 7. 恢复重要文件
echo -e "\n${YELLOW}[7/8] 恢复重要文件...${NC}"
[ -f "$BACKUP_DIR/.env" ] && cp "$BACKUP_DIR/.env" . 2>/dev/null || true
[ -d "$BACKUP_DIR/logs" ] && cp -r "$BACKUP_DIR/logs" . 2>/dev/null || true
[ -d "$BACKUP_DIR/uploads" ] && cp -r "$BACKUP_DIR/uploads" . 2>/dev/null || true

# 清理备份目录
rm -rf "$BACKUP_DIR"

# 8. 清理 Python 缓存（可选）
echo -e "\n${YELLOW}[8/8] 清理 Python 缓存...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# 9. 显示更新结果
echo -e "\n${YELLOW}更新完成，当前状态：${NC}"
echo -e "${GREEN}最新提交：${NC}"
git log -2 --oneline
echo ""

# 检查是否需要重启服务
echo -e "${YELLOW}检查是否需要重启服务...${NC}"
# 检查关键文件是否有更新
NEED_RESTART=false
KEY_FILES=("main.py" "core/" "api/" "models/")

for file in "${KEY_FILES[@]}"; do
    if git diff --name-only HEAD~1 HEAD | grep -q "^$file"; then
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

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}代码增量同步完成！${NC}"
echo -e "${GREEN}========================================${NC}"