# -*- coding: utf-8 -*-
"""简化的测试运行器"""

import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent

# 切换到项目根目录
os.chdir(project_root)

# 使用所有语法正确的测试文件
test_files = [
    "test_scripts/test_config_simple.py",
    "test_scripts/test_app_startup.py",
    "tests/test_config.py",
    "tests/test_database.py",
    "tests/test_integration.py",
    "tests/test_message_send_receive.py",
    "tests/test_performance.py"
]

def run_tests():
    """运行所有测试"""
    print("🧪 开始运行wxkf_saas测试套件...")

    success_count = 0
    total_count = len(test_files)

    for i, test_file in enumerate(test_files, 1):
        try:
            print(f"📝 运行测试 {i}/{total_count}: {test_file}")

            # 检查文件是否存在
            if not Path(test_file).exists():
                print(f"⚠️ {test_file} 文件不存在，跳过")
                continue

            result = subprocess.run([
                sys.executable, test_file
            ],
                capture_output=True,
                text=True,
                env=os.environ.copy()
            )

            if result.returncode == 0:
                print(f"✅ {test_file} 通过")
                success_count += 1
            else:
                print(f"❌ {test_file} 失败 (exit code: {result.returncode})")
                if result.stdout:
                    print("标准输出:", result.stdout[-500:])  # 显示最后500字符
                if result.stderr:
                    print("错误输出:", result.stderr[-500:])  # 显示最后500字符
        except Exception as e:
            print(f"❌ {test_file} 运行异常: {e}")

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
    return run_tests()

if __name__ == "__main__":
    sys.exit(0 if main() else 1)