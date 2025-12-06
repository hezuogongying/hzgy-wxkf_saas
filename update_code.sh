#!/bin/bash
# ============================================
# wxkf_saas 代码同步脚本
# 功能：从 origin/bwx_dev 拉取最新代码并保持完全一致
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
echo -e "${GREEN}开始同步代码...${NC}"
echo -e "${GREEN}========================================${NC}"

cd "$PROJECT_DIR"

# 1. 检查当前状态
echo -e "\n${YELLOW}[1/5] 检查当前 Git 状态...${NC}"
git status --short

# 2. 获取最新代码
echo -e "\n${YELLOW}[2/5] 从远程获取最新代码...${NC}"
git fetch origin "$BRANCH"

# 3. 强制重置到远程分支
echo -e "\n${YELLOW}[3/5] 重置到 origin/${BRANCH}...${NC}"
git reset --hard "origin/$BRANCH"

# 4. 清理未跟踪文件（排除重要的本地文件）
echo -e "\n${YELLOW}[4/5] 清理未跟踪文件...${NC}"
# -f: 强制删除文件
# -d: 删除目录
# -e: 排除指定文件/目录
git clean -fd \
    -e .env \
    -e logs/ \
    -e uploads/ \
    -e __pycache__/ \
    -e '*.pyc' \
    -e '*.log'

# 5. 显示同步结果
echo -e "\n${YELLOW}[5/5] 同步完成，当前状态：${NC}"
git log -1 --oneline
echo ""
git status

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}代码同步完成！${NC}"
echo -e "${GREEN}========================================${NC}"

# 可选：重启服务（根据需要取消注释）
# echo -e "\n${YELLOW}正在重启服务...${NC}"
# supervisorctl restart wxkf_saas
# 或者
# systemctl restart wxkf_saas

echo -e "\n${YELLOW}提示：如需重启服务，请手动执行相关命令${NC}"