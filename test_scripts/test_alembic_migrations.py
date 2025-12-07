#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Alembic迁移测试
"""

import sys
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """运行命令并返回结果"""
    print(f"\n{'='*60}")
    print(f"操作: {description}")
    print(f"命令: {cmd}")
    print('='*60)

    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

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

    return result.returncode == 0


def test_alembic_history():
    """测试查看迁移历史"""
    print("测试查看迁移历史...")
    success = run_command("alembic history", "查看迁移历史")
    return success


def test_alembic_current():
    """测试查看当前版本"""
    print("\n测试查看当前版本...")
    success = run_command("alembic current", "查看当前版本")
    return success


def test_alembic_heads():
    """测试查看最新版本"""
    print("\n测试查看最新版本...")
    success = run_command("alembic heads", "查看最新版本")
    return success


def test_migration_sql():
    """测试生成迁移SQL（不执行）"""
    print("\n测试生成迁移SQL...")
    success = run_command(
        "alembic upgrade head --sql",
        "生成升级SQL（不执行）"
    )
    return success


def test_migration_check():
    """测试迁移检查"""
    print("\n测试迁移检查...")
    success = run_command(
        "python -c \"from alembic.runtime.migration import MigrationContext; "
        "from sqlalchemy import create_engine; "
        "from core.config import WxKfSaasConfig; "
        "config = WxKfSaasConfig(); "
        "engine = create_engine(config.database_url); "
        "with engine.connect() as connection: "
        "    context = MigrationContext.configure(connection); "
        "    print(f'当前版本: {context.get_current_revision()}'); "
        "    print(f'最新版本: {context.get_head_revision()}')\"",
        "检查数据库迁移状态"
    )
    return success


def test_manage_migrations_script():
    """测试迁移管理脚本"""
    print("\n测试迁移管理脚本...")

    # 测试帮助命令
    success = run_command(
        "python manage_migrations.py --help",
        "查看管理脚本帮助"
    )

    if not success:
        return False

    # 测试查看历史
    success = run_command(
        "python manage_migrations.py history",
        "使用管理脚本查看历史"
    )

    return success


def main():
    """主函数"""
    print("="*80)
    print("Alembic迁移功能测试")
    print("="*80)

    results = []

    # 切换到项目目录
    project_root = Path(__file__).parent.parent
    import os
    os.chdir(project_root)

    # 运行测试
    results.append(("迁移历史", test_alembic_history()))
    results.append(("当前版本", test_alembic_current()))
    results.append(("最新版本", test_alembic_heads()))
    results.append(("迁移SQL生成", test_migration_sql()))
    results.append(("迁移状态检查", test_migration_check()))
    results.append(("管理脚本", test_manage_migrations_script()))

    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)

    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed

    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name}: {status}")

    print(f"\n总计: {passed}/{total} 个测试通过")

    if passed == total:
        print("\n🎉 所有Alembic迁移测试通过！")
        return True
    else:
        print(f"\n⚠️ {failed} 个测试失败")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)