# -*- coding: utf-8 -*-
"""修复的测试脚本 - 支持Windows路径"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径（Windows兼容方式）
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 测试的文件列表
test_files = [
    "test_config.py",
    "test_url_building.py",
    "test_async_db.py",
    "test_database.py",
    "test_client.py",
    "test_kf_account.py",
    "test_message.py",
    "test_media.py",
    "test_api.py",
    "test_integration.py",
    "test_performance.py",
    "test_error_handling.py",
    "__init__.py"
]

# 获取当前目录
current_dir = Path.cwd()
print(f"当前目录: {current_dir}")
print(f"脚本目录: {current_dir / 'tests'}")

# 检查测试文件是否存在
missing_files = []
for test_file in test_files:
    test_path = current_dir / 'tests' / test_file
    if not test_path.exists():
        missing_files.append(test_file)
        print(f"⚠️ 缺失文件: {test_path}")

if missing_files:
    print(f"\n❌ 缺失 {len(missing_files)} 个测试文件，请检查脚本目录结构")
else:
    print("\n✅ 所有测试文件存在")

# 构建正确的pytest命令
if sys.platform == "win32":
    python_exe = "Scripts\\python.exe"
else:
    python_exe = "python3"

# 构建参数
pytest_base = [
    python_exe, "-m", "pytest", "tests/",
    "-m", "unit", "-v", "--tb=short",
    "--cov=wxkf_saas", "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=90",
    "--junitxml=junit.xml",
    "--htmlcov=htmlcov/index.html"
]

# 运行测试
def run_test(test_type, description):
    """运行指定类型的测试"""
    print(f"\n🚀 运行{description}测试...")
    cmd = pytest_base + ["-m", test_type, "-v"]

    try:
        # 切换到测试目录
        original_cwd = os.getcwd()
        os.chdir(current_dir / "tests")

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        # 切换回原目录
        os.chdir(original_cwd)

        # 输出结果
        output_lines = result.stdout.strip().split('\n') if result.stdout else []
        success = result.returncode == 0

        if success:
            print(f"✅ {description}测试通过")
            for line in output_lines[-20:]:  # 显示最后20行
                print(f"   {line}")
        else:
            print(f"❌ {description}测试失败")
            print("错误输出:")
            for line in output_lines[-10:]:  # 显示最后10行
                print(f"   {line}")
            if len(output_lines) > 20:
                print("   ... (更多)")

        # 返回码
        return result.returncode

def main():
    """运行所有测试"""
    print("🧪 wxkf_saas 测试套件运行器")

    # 测试配置
    run_test("config", "配置模块测试")

    # 测试URL构建
    run_test("url", "URL构建测试")

    # 测试数据库
    run_test("database", "数据库操作测试")

    # 测试API客户端
    run_test("client", "客户端功能测试")

    # 测试客服账号
    run_test("kf_account", "客服账号API测试")

    # 测试消息
    run_test("message", "消息API测试")

    # 测试素材
    run_test("media", "素材API测试")

    # 测试API响应
    run_test("api", "API响应模型测试")

    # 测试错误处理
    run_test("error", "错误处理测试")

    # 运行所有测试
    run_test("all", "完整集成测试")


if __name__ == "__main__":
    main()