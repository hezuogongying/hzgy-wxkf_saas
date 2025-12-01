# -*- coding: utf-8 -*-
"""wxkf_saas 测试运行器"""

import subprocess
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_pytest(test_target=None, extra_args=None):
    """运行pytest测试"""
    cmd = [sys.executable, "-m", "pytest", "-v"]

    if test_target:
        if test_target == "unit":
            cmd.extend(["-m", "unit", "tests/"])
        elif test_target == "integration":
            cmd.extend(["-m", "integration", "tests/"])
        elif test_target == "performance":
            cmd.extend(["-m", "performance", "tests/"])
        elif test_target.startswith("tests/"):
            cmd.append(test_target)
        else:
            cmd.append(f"tests/test_{test_target}.py")
    else:
        cmd.append("tests/")

    # 添加覆盖率报告
    cmd.extend([
        "--cov=wxkf_saas",
        "--cov-report=html:htmlcov",
        "--cov-report=term-missing",
        "--tb=short"
    ])

    if extra_args:
        cmd.extend(extra_args)

    print(f"🚀 运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🎯 wxkf_saas 测试运行器")
        print("\n使用方法:")
        print("  python test_runner.py all              # 运行所有测试")
        print("  python test_runner.py unit             # 运行单元测试")
        print("  python test_runner.py integration      # 运行集成测试")
        print("  python test_runner.py performance      # 运行性能测试")
        print("  python test_runner.py config           # 运行配置测试")
        print("  python test_runner.py database         # 运行数据库测试")
        print("  python test_runner.py api              # 运行API测试")
        print("  python test_runner.py tests/test_x.py   # 运行特定文件")
        print("\n示例:")
        print("  python test_runner.py all --cov-fail-under=80")
        return 1

    test_type = sys.argv[1]
    extra_args = sys.argv[2:] if len(sys.argv) > 2 else []

    # 运行测试
    result = run_pytest(test_type, extra_args)

    if result.returncode == 0:
        print("\n✅ 测试完成！")
        if Path("htmlcov").exists():
            print("📊 覆盖率报告: htmlcov/index.html")
        return 0
    else:
        print(f"\n❌ 测试失败，返回码: {result.returncode}")
        return result.returncode


if __name__ == "__main__":
    sys.exit(main())