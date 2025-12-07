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
    # 按优先级排序：基础测试 -> 原有API测试 -> 完整API测试
    api_test = test_dir / "test_api_endpoints.py"
    message_test = test_dir / "test_message_api.py"
    complete_api_test = test_dir / "test_complete_api.py"

    # 移动 API 测试到最后
    for test in [api_test, message_test]:
        if test in test_files:
            test_files.remove(test)
            test_files.append(test)

    # 完整API测试放在最最后
    if complete_api_test in test_files:
        test_files.remove(complete_api_test)
        test_files.append(complete_api_test)

    if not test_files:
        print("❌ 没有找到测试脚本")
        sys.exit(1)

    print(f"找到 {len(test_files)} 个测试脚本\n")

    # 运行所有测试
    results = []
    for test_file in test_files:
        success = run_test_file(test_file)
        results.append((test_file.name, success, None))  # None 作为占位符

    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)

    total = len(results)
    passed = sum(1 for result in results if len(result) >= 2 and result[1])
    failed = total - passed

    # 详细显示每个测试结果
    print("\n✅ 通过的测试:")
    for result in results:
        if len(result) >= 2 and result[1]:  # result[1] 是 success
            print(f"  - {result[0]} API 端点测试通过")

    if failed > 0:
        print("\n❌ 失败的测试:")
        for result in results:
            if len(result) >= 2 and not result[1]:
                error_msg = f": {result[2]}" if len(result) > 2 else ""
                print(f"  - {result[0]} API 端点测试失败{error_msg}")

    print(f"\n" + "="*80)
    print(f"总计: {passed} 个 API 端点测试通过，{failed} 个 API 端点测试失败")
    print("="*80)

    if passed == total:
        print("\n🎉 所有 API 端点测试通过！")
        exit_code = 0
    else:
        print(f"\n⚠️ {failed} 个 API 端点测试失败，请检查相关功能")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()