# -*- coding: utf-8 -*-
"""wxkf_saas 测试运行器"""

import subprocess
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_pytest(test_target=None, extra_args=None, verbose=False, log_level="INFO", log_to_file=False, clear_logs=False):
    """运行pytest测试"""
    cmd = [sys.executable, "-m", "pytest"]

    # 根据日志级别调整详细程度
    if log_level.upper() == "DEBUG":
        cmd.extend(["-v", "-s", "--tb=long"])
        verbose = True
    elif log_level.upper() == "DETAILED":
        cmd.extend(["-vv", "-s", "--tb=long"])
        verbose = True
    else:
        cmd.extend(["-v"])

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

    # 添加覆盖率报告（如果安装了pytest-cov）
    try:
        import pytest_cov
        cmd.extend([
            "--cov=wxkf_saas",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing"
        ])
    except ImportError:
        if verbose:
            print("⚠️  未安装pytest-cov，跳过覆盖率报告")

    # 基础跟踪设置
    if log_level.upper() in ["DEBUG", "DETAILED"]:
        cmd.extend(["--tb=long", "--capture=no"])
    else:
        cmd.extend(["--tb=short"])

    if extra_args:
        cmd.extend(extra_args)

    # 添加日志环境变量
    env = os.environ.copy()
    env["WXKF_TEST_LOG_LEVEL"] = log_level.upper()
    if log_to_file:
        env["WXKF_TEST_LOG_TO_FILE"] = "true"
        if clear_logs:
            env["WXKF_TEST_CLEAR_LOGS"] = "true"

    print(f"🚀 运行命令: {' '.join(cmd)}")
    print(f"📝 日志级别: {log_level}")

    if log_to_file:
        if clear_logs:
            print(f"🗑️ 将清空logs目录并创建新日志文件")
        else:
            print(f"📁 日志将保存到文件: logs/test_*.log")

    # 显示最新日志文件
    log_dir = Path("logs")
    if log_dir.exists():
        log_files = list(log_dir.glob("test_*.log"))
        if log_files:
            latest_log = max(log_files, key=os.path.getmtime)
            print(f"📄 最新日志文件: {latest_log}")

            # 如果需要清理，显示清理信息
            if clear_logs:
                print(f"🗑️ 清理前发现 {len(log_files)} 个日志文件")

    if verbose:
        print(f"🔧 工作目录: {os.getcwd()}")
        print(f"🐍 Python路径: {sys.executable}")

    return subprocess.run(cmd, env=env)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("🎯 wxkf_saas 测试运行器")
        print("\n📋 使用方法:")
        print("  python test_runner.py <测试类型> [选项]")
        print("")
        print("🧪 测试类型:")
        print("  all              # 运行所有测试")
        print("  unit             # 运行单元测试")
        print("  integration      # 运行集成测试")
        print("  performance      # 运行性能测试")
        print("  config           # 运行配置测试")
        print("  database         # 运行数据库测试")
        print("  api              # 运行API测试")
        print("  client           # 运行客户端测试")
        print("  models           # 运行模型测试")
        print("  tests/test_x.py   # 运行特定文件")
        print("")
        print("🔧 日志选项:")
        print("  --log-level=INFO      # 标准日志输出")
        print("  --log-level=DEBUG     # 详细调试信息")
        print("  --log-level=DETAILED  # 最详细的输出")
        print("  --log-to-file         # 保存日志到文件")
        print("  --clear-logs         # 清空历史日志文件")
        print("  --verbose             # 显示运行环境信息")
        print("")
        print("📊 示例:")
        print("  python test_runner.py unit")
        print("  python test_runner.py unit --log-level=DEBUG")
        print("  python test_runner.py unit --log-to-file")
        print("  python test_runner.py all --verbose --log-level=DETAILED")
        print("  python test_runner.py tests/test_config.py --log-level=DEBUG --log-to-file --verbose")
        print("  python test_runner.py unit --log-to-file --clear-logs")
        print("")
        print("📁 日志文件位置:")
        print("  测试日志将保存到 logs/test_YYYYMMDD_HHMMSS.log")
        print("  文件包含详细的时间戳、函数名和行号")
        return 1

    # 解析命令行参数
    test_type = None
    log_level = "INFO"
    log_to_file = False
    clear_logs = False
    verbose = False
    extra_args = []

    # 处理参数
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg.startswith("--log-level="):
            log_level = arg.split("=", 1)[1]
        elif arg == "--log-to-file":
            log_to_file = True
        elif arg == "--clear-logs":
            clear_logs = True
        elif arg == "--verbose":
            verbose = True
        elif test_type is None:
            test_type = arg
        else:
            extra_args.append(arg)

        i += 1

    # 运行测试
    result = run_pytest(test_type, extra_args, verbose, log_level, log_to_file)

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