# -*- coding: utf-8 -*-
"""运行所有测试"""

import subprocess
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test_suite(test_type, description):
    """运行指定类型的测试套件"""
    print(f"🧪 运行{description}测试...")
    print("-" * 50)

    try:
        # 根据测试类型选择不同的运行方式
        if test_type == "config":
            # 配置测试：直接运行Python文件
            cmd = [sys.executable, "tests/test_config.py"]
        elif test_type == "database":
            # 数据库测试：直接运行Python文件
            cmd = [sys.executable, "tests/test_database.py"]
        elif test_type == "unit":
            # 单元测试：运行已知的可工作测试
            cmd = [sys.executable, "tests/run_tests.py"]
        else:
            # 其他测试：跳过
            print(f"⚠️ {description}测试类型暂不支持，跳过")
            return False

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description}测试成功完成")
            return True
        else:
            print(f"❌ {description}测试失败")
            print(f"错误输出: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 运行{description}测试时出错: {e}")
        return False


def main():
    """运行所有测试"""
    print("🚀 开始运行wxkf_saas测试套件...")

    print(f"当前工作目录: {Path.cwd()}")

    success = True

    # 运行单元测试
    success &= run_test_suite("unit", "单元测试")

    # 运行配置测试
    success &= run_test_suite("config", "配置测试")

    # 运行数据库测试
    success &= run_test_suite("database", "数据库测试")

    if success:
        print("\n🎉 所有测试成功完成！")
        print("\n📊 测试报告已生成:")
        print("  - HTML报告: htmlcov/index.html")
        print("  - XML报告: junit.xml")
        print("  - 覆盖率报告: 查看 htmlcov/index.html")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())