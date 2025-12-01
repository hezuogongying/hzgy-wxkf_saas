# -*- coding: utf-8 -*-
"""简化的测试运行器"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent

# 切换到项目根目录
os.chdir(project_root)

# 测试文件
test_files = [
    "tests/test_config.py",
    "tests/test_async_db.py",
    "tests/test_base.py"
    "tests/test_config_validation.py"
    "tests/test_database_config.py"
    "tests/test_client_initialization.py",
    "tests/test_kf_account.py",
    "tests/test_message.py",
    "tests/test_media.py",
    "tests/test_integration.py",
    "tests/test_error_scenarios.py",
    "tests/test_performance.py"
    "tests/test_async_database.py",
    "tests/test_unit.py",
    "tests/test_all.py",
]

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行wxkf_saas测试套件...")

    success_count = 0
    total_count = len(test_files)

    for i, test_file in enumerate(test_files, 1):
        try:
            print(f"📝 运行测试 {i}/{total_count}: {test_file}")
            result = subprocess.run([
                sys.executable, "python", "-m", "pytest",
                "tests", test_file
            ],
                capture_output=True,
                text=True,
                env=os.environ.copy()
            ],
                check=True
            )

            if result.returncode == 0:
                print(f"✅ {test_file} 通过")
                success_count += 1
            else:
                print(f"❌ {test_file} 失败 (exit code: {result.returncode})")

        print(f"\n📊 测试结果:")
        print(f"✅ 通过: {success_count}/{total_count}")
        print(f"❌ 失败: {total_count - success_count}")

        if success_count == total_count:
            print("🎉 所有测试通过！")
            return True
        else:
            print(f"❌ 有 {total_count - success_count} 个测试失败")
            return False

def main():
    """主函数"""
    print("🚀 wxkf_saas 测试套件运行器")
    print("=" * 50)

    # 测试基本配置
    print("📝 运行基础配置测试...")
    if run_tests():
        print("✅ 基本配置测试通过")

    # 运行所有测试
    print("🧪 运行完整测试...")
    if run_tests():
        print("✅ 完整测试通过！")
        print("🎯 wxkf_saas项目测试完成！")
        print("\n💡 下一步:")
        print("1. 运行: python tests/run_tests.py [test_name]")
        print("2. 覆盖率测试: python -m pytest --cov=wxkf_saas")
        print("3. 性能测试: python -m pytest tests/test_performance.py")
        print("4. 完整套件测试: python -m pytest tests/test_integration.py")

if __name__ == "__main__":
    main()