# -*- coding: utf-8 -*-
"""API 端点测试脚本"""

import sys
import os
import requests
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class APITester:
    """API 测试类"""

    def __init__(self):
        # 从配置加载
        from core.config import WxKfSaasConfig
        self.config = WxKfSaasConfig()

        # API 基础 URL
        self.base_url = f"http://localhost:{self.config.fastapi_port}"
        self.corp_id = self.config.corp_id

        # 测试结果
        self.results = []

    def log(self, message, level="INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def test_health_check(self):
        """测试健康检查"""
        self.log("测试健康检查接口...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 健康检查成功: {data.get('status')}")
                self.results.append(("健康检查", True, None))
                return True
            else:
                error = f"状态码: {response.status_code}"
                self.log(f"❌ 健康检查失败: {error}")
                self.results.append(("健康检查", False, error))
                return False
        except Exception as e:
            self.log(f"❌ 健康检查异常: {e}")
            self.results.append(("健康检查", False, str(e)))
            return False

    def test_tenant_info(self):
        """测试租户信息接口"""
        self.log("测试租户信息接口...")
        try:
            response = requests.get(
                f"{self.base_url}/api/tenants/{self.corp_id}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 租户信息获取成功")
                self.log(f"   企业ID: {data.get('corp_id')}")
                self.log(f"   企业名称: {data.get('corp_name', '未设置')}")
                self.results.append(("租户信息", True, None))
                return True
            else:
                error = response.json().get('detail', f"状态码: {response.status_code}")
                self.log(f"❌ 租户信息获取失败: {error}")
                self.results.append(("租户信息", False, error))
                return False
        except Exception as e:
            self.log(f"❌ 租户信息异常: {e}")
            self.results.append(("租户信息", False, str(e)))
            return False

    def test_kf_accounts(self):
        """测试客服账号列表"""
        self.log("测试客服账号列表接口...")
        try:
            response = requests.get(
                f"{self.base_url}/api/kf_accounts",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                accounts = data.get('accounts', [])
                self.log(f"✅ 客服账号列表获取成功: 共{len(accounts)}个")
                for acc in accounts[:3]:  # 只显示前3个
                    self.log(f"   - {acc.get('name', '')} ({acc.get('status', '')})")
                self.results.append(("客服账号列表", True, None))
                return True
            else:
                error = response.json().get('detail', f"状态码: {response.status_code}")
                self.log(f"❌ 客服账号列表失败: {error}")
                self.results.append(("客服账号列表", False, error))
                return False
        except Exception as e:
            self.log(f"❌ 客服账号列表异常: {e}")
            self.results.append(("客服账号列表", False, str(e)))
            return False

    def test_service_status(self):
        """测试服务状态（需要 access_token）"""
        self.log("测试服务状态接口...")
        try:
            response = requests.get(
                f"{self.base_url}/api/service/status",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 服务状态获取成功")
                self.log(f"   服务状态: {data.get('status', 'unknown')}")
                self.results.append(("服务状态", True, None))
                return True
            else:
                error = response.json().get('detail', f"状态码: {response.status_code}")
                self.log(f"❌ 服务状态失败: {error}")
                self.results.append(("服务状态", False, error))
                return False
        except Exception as e:
            self.log(f"❌ 服务状态异常: {e}")
            self.results.append(("服务状态", False, str(e)))
            return False

    def test_docs_available(self):
        """测试 API 文档是否可访问"""
        self.log("测试 API 文档接口...")
        try:
            # 测试 Swagger UI
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                self.log("✅ Swagger 文档可访问")
                self.results.append(("API文档", True, None))

                # 测试 ReDoc
                response = requests.get(f"{self.base_url}/redoc", timeout=5)
                if response.status_code == 200:
                    self.log("✅ ReDoc 文档可访问")
                else:
                    self.log("⚠️ ReDoc 文档不可访问")

                return True
            else:
                error = f"状态码: {response.status_code}"
                self.log(f"❌ API 文档不可访问: {error}")
                self.results.append(("API文档", False, error))
                return False
        except Exception as e:
            self.log(f"❌ API 文档异常: {e}")
            self.results.append(("API文档", False, str(e)))
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print(" " * 20 + "微信客服 API 端点测试")
        print(" " * 25 + f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(" " * 30 + f"目标: {self.base_url}")
        print("="*80 + "\n")

        # 检查服务是否运行
        self.log("检查服务是否运行...")
        try:
            requests.get(f"{self.base_url}/", timeout=2)
            self.log("✅ 服务正在运行")
        except:
            self.log("❌ 服务未运行或无法访问")
            self.log("请确保已启动 main.py 或 gunicorn 服务")
            return False

        # 运行各项测试
        tests = [
            ("健康检查", self.test_health_check),
            ("API文档", self.test_docs_available),
            ("租户信息", self.test_tenant_info),
            ("客服账号列表", self.test_kf_accounts),
            ("服务状态", self.test_service_status),
        ]

        for name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log(f"❌ {name}测试异常: {e}")
                self.results.append((name, False, str(e)))
            print()  # 空行分隔

        # 打印测试结果汇总
        self.print_summary()

    def print_summary(self):
        """打印测试结果汇总"""
        print("="*80)
        print("测试结果汇总")
        print("="*80)

        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)

        for name, success, error in self.results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"  {name:<20} {status}")
            if error:
                print(f"    错误: {error}")

        print(f"\n总计: {passed}/{total} 通过")

        if passed == total:
            print("\n🎉 所有 API 测试通过！")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败")
            print("\n💡 提示：")
            print("  - 确保服务已启动（python main.py 或 gunicorn）")
            print("  - 检查 .env 中的配置是否正确")
            print("  - 部分接口需要有效的 access_token")

        print("="*80)


def main():
    """主函数"""
    # 从环境变量读取配置（如果指定）
    api_url = os.getenv("API_TEST_URL", "")
    corp_id = os.getenv("API_TEST_CORP_ID", "")

    if api_url or corp_id:
        print("使用环境变量中的配置...")

    # 创建测试实例
    tester = APITester()

    # 如果环境变量指定了 URL，覆盖配置
    if api_url:
        tester.base_url = api_url
    if corp_id:
        tester.corp_id = corp_id

    # 运行测试
    tester.run_all_tests()


if __name__ == "__main__":
    main()