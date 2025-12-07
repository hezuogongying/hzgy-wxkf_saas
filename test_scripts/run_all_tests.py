# -*- coding: utf-8 -*-
"""运行所有测试脚本"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def print_banner():
    """打印横幅"""
    print("\n" + "="*80)
    print(" "*20 + "微信客服 SaaS API 测试套件")
    print(" "*25 + f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")


def run_test_file(filepath):
    """运行单个测试文件"""
    print(f"\n{'#'*80}")
    print(f"# 运行: {filepath.name}")
    print(f"{'#'*80}\n")

    try:
        # 使用 subprocess 运行测试文件
        result = subprocess.run(
            [sys.executable, str(filepath)],
            cwd=str(filepath.parent),
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行失败: {e}")
        return False


def main():
    """主函数"""
    print_banner()

    # 获取所有测试脚本（排除自己和特殊文件）
    test_dir = Path(__file__).parent
    test_files = sorted([
        f for f in test_dir.glob("test_*.py")
        if f.name != "run_all_tests.py"
    ])

    # 添加 quick_test 作为快速检查（插在最前面）
    quick_test = test_dir / "quick_test.py"
    if quick_test.exists():
        test_files.insert(0, quick_test)

    # API 测试需要服务运行，放在最后
    api_test = test_dir / "test_api_endpoints.py"
    message_test = test_dir / "test_message_api.py"

    # 移动 API 测试到最后
    if api_test in test_files:
        test_files.remove(api_test)
        test_files.append(api_test)
    if message_test in test_files:
        test_files.remove(message_test)
        test_files.append(message_test)

    if not test_files:
        print("❌ 没有找到测试脚本")
        sys.exit(1)

    print(f"找到 {len(test_files)} 个测试脚本\n")

    # 运行所有测试
    results = []
    for test_file in test_files:
        success = run_test_file(test_file)
        results.append((test_file.name, success))

    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)

    total = len(results)
    passed = sum(1 for _, success in results if success)

    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name:<30} {status}")

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("\n🎉 所有测试通过！")
        exit_code = 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        exit_code = 1

    print("="*80)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()