#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库迁移管理脚本
使用Alembic进行数据库版本控制
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description=""):
    """运行命令"""
    print(f"\n{'='*60}")
    if description:
        print(f"操作: {description}")
    print(f"命令: {cmd}")
    print('='*60)

    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8')

    if result.returncode == 0:
        print("✅ 执行成功")
        if result.stdout.strip():
            print("\n输出:")
            print(result.stdout)
    else:
        print("❌ 执行失败")
        if result.stderr.strip():
            print("\n错误:")
            print(result.stderr)
        if result.stdout.strip():
            print("\n输出:")
            print(result.stdout)
        sys.exit(1)

def init_migrations():
    """初始化迁移环境"""
    print("\n🚀 初始化Alembic迁移环境...")
    run_command("alembic init alembic", "创建迁移目录和配置文件")

def create_migration(message="Auto migration"):
    """创建新的迁移文件"""
    print(f"\n📝 创建迁移文件: {message}")
    run_command(f'alembic revision --autogenerate -m "{message}"', "自动生成迁移")

def upgrade_database(revision="head"):
    """升级数据库到指定版本"""
    print(f"\n⬆️ 升级数据库到版本: {revision}")
    run_command(f"alembic upgrade {revision}", "应用迁移")

def downgrade_database(revision="-1"):
    """降级数据库到指定版本"""
    print(f"\n⬇️ 降级数据库到版本: {revision}")
    run_command(f"alembic downgrade {revision}", "回滚迁移")

def show_history():
    """显示迁移历史"""
    print("\n📜 迁移历史:")
    run_command("alembic history", "查看所有迁移版本")

def show_current():
    """显示当前版本"""
    print("\n📍 当前数据库版本:")
    run_command("alembic current", "查看当前版本")

def show_heads():
    """显示最新版本"""
    print("\n🔝 最新迁移版本:")
    run_command("alembic heads", "查看最新版本")

def reset_database():
    """重置数据库（删除所有表并重新创建）"""
    print("\n⚠️ 警告: 这将删除所有数据!")
    confirm = input("确定要继续吗? (yes/no): ")
    if confirm.lower() != 'yes':
        print("操作已取消")
        return

    # 先降级到基版本
    run_command("alembic downgrade base", "删除所有表")
    # 再升级到最新版本
    run_command("alembic upgrade head", "重新创建所有表")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='数据库迁移管理工具')

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 初始化命令
    subparsers.add_parser('init', help='初始化迁移环境')

    # 创建迁移
    create_parser = subparsers.add_parser('create', help='创建新迁移')
    create_parser.add_argument('-m', '--message', default='Auto migration', help='迁移说明')

    # 升级数据库
    upgrade_parser = subparsers.add_parser('upgrade', help='升级数据库')
    upgrade_parser.add_argument('revision', nargs='?', default='head', help='目标版本（默认为最新）')

    # 降级数据库
    downgrade_parser = subparsers.add_parser('downgrade', help='降级数据库')
    downgrade_parser.add_argument('revision', nargs='?', default='-1', help='目标版本（默认为上一个）')

    # 查看命令
    subparsers.add_parser('history', help='查看迁移历史')
    subparsers.add_parser('current', help='查看当前版本')
    subparsers.add_parser('heads', help='查看最新版本')

    # 重置数据库
    subparsers.add_parser('reset', help='重置数据库（危险操作）')

    # 解析参数
    args = parser.parse_args()

    # 显示帮助
    if not args.command:
        parser.print_help()
        return

    # 执行对应命令
    if args.command == 'init':
        init_migrations()
    elif args.command == 'create':
        create_migration(args.message)
    elif args.command == 'upgrade':
        upgrade_database(args.revision)
    elif args.command == 'downgrade':
        downgrade_database(args.revision)
    elif args.command == 'history':
        show_history()
    elif args.command == 'current':
        show_current()
    elif args.command == 'heads':
        show_heads()
    elif args.command == 'reset':
        reset_database()

if __name__ == '__main__':
    main()