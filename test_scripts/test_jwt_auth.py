# -*- coding: utf-8 -*-
"""JWT认证功能测试"""

import sys
import os
import requests
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class JWTAuthTester:
    """JWT认证测试类"""

    def __init__(self):
        from core.config import WxKfSaasConfig
        self.config = WxKkSaasConfig()

        # API基础URL
        self.base_url = f"http://localhost:{self.config.fastapi_port}"

        # 测试结果
        self.results = []

        # 认证Token
        self.access_token = None
        self.refresh_token = None
        self.user_info = None

    def log(self, message, level="INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")

    def add_result(self, test_name, success, error=None):
        """添加测试结果"""
        self.results.append((test_name, success, error))

    def make_request(self, method, endpoint, **kwargs):
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"

        # 添加认证头
        if self.access_token:
            headers = kwargs.get('headers', {})
            headers['Authorization'] = f'Bearer {self.access_token}'
            kwargs['headers'] = headers

        try:
            response = requests.request(method, url, timeout=10, **kwargs)
            return response
        except Exception as e:
            self.log(f"请求失败: {e}", "ERROR")
            return None

    def test_login(self):
        """测试登录"""
        self.log("测试用户登录...")

        # 测试表单登录
        data = {
            "username": "username",
            "password": "password"
        }

        response = self.make_request("POST", "/api/v1/auth/login", data=data)

        if response and response.status_code == 200:
            result = response.json()
            self.access_token = result.get("access_token")
            self.refresh_token = result.get("refresh_token")
            self.user_info = result.get("user")

            self.log(f"✅ 登录成功，用户: {self.user_info.get('username')}")
            self.add_result("用户登录", True)
        else:
            error = "登录失败" if response else "无响应"
            self.log(f"❌ 登录失败: {error}")
            self.add_result("用户登录", False, error)

    def test_verify_token(self):
        """测试Token验证"""
        if not self.access_token:
            self.log("❌ 无有效Token，跳过Token验证测试")
            self.add_result("Token验证", False, "无有效Token")
            return

        self.log("测试Token验证...")

        response = self.make_request("GET", "/api/v1/auth/verify-token")

        if response and response.status_code == 200:
            result = response.json()
            self.log(f"✅ Token验证成功，有效")
            self.add_result("Token验证", True)
        else:
            error = response.text if response else "无响应"
            self.log(f"❌ Token验证失败: {error}")
            self.add_result("Token验证", False, error)

    def test_get_user_info(self):
        """测试获取用户信息"""
        if not self.access_token:
            self.log("❌ 无有效Token，跳过用户信息测试")
            self.add_result("获取用户信息", False, "无有效Token")
            return

        self.log("测试获取用户信息...")

        response = self.make_request("GET", "/api/v1/auth/me")

        if response and response.status_code == 200:
            result = response.json()
            self.log(f"✅ 获取用户信息成功，用户: {result.get('username')}")
            self.add_result("获取用户信息", True)
        else:
            error = response.text if response else "无响应"
            self.log(f"❌ 获取用户信息失败: {error}")
            self.add_result("获取用户信息", False, error)

    def test_refresh_token(self):
        """测试刷新Token"""
        if not self.refresh_token:
            self.log("❌ 无刷新Token，跳过Token刷新测试")
            self.add_result("刷新Token", False, "无刷新Token")
            return

        self.log("测试刷新Token...")

        data = {
            "refresh_token": self.refresh_token
        }

        response = self.make_request("POST", "/api/v1/auth/refresh", json=data)

        if response and response.status_code == 200:
            result = response.json()
            new_access_token = result.get("access_token")

            if new_access_token:
                self.access_token = new_access_token
                self.log("✅ Token刷新成功")
                self.add_result("刷新Token", True)
            else:
                self.log("❌ Token刷新失败：无新Token")
                self.add_result("刷新Token", False, "无新Token")
        else:
            error = response.text if response else "无响应"
            self.log(f"❌ Token刷新失败: {error}")
            self.add_result("刷新Token", False, error)

    def test_logout(self):
        """测试登出"""
        if not self.access_token:
            self.log("❌ 无有效Token，跳过登出测试")
            self.add_result("用户登出", False, "无有效Token")
            return

        self.log("测试用户登出...")

        response = self.make_request("POST", "/api/v1/auth/logout")

        if response and response.status_code == 200:
            result = response.json()
            self.log(f"✅ 登出成功")
            self.add_result("用户登出", True)

            # 清除Token
            self.access_token = None
            self.refresh_token = None
            self.user_info = None
        else:
            error = response.text if response else "无响应"
            self.log(f"❌ 登出失败: {error}")
            self.add_result("用户登出", False, error)

    def test_protected_api_without_token(self):
        """测试未授权访问受保护的API"""
        self.log("测试未授权访问受保护的API...")

        # 临时保存Token
        saved_token = self.access_token
        self.access_token = None

        # 访问需要认证的API
        response = self.make_request("GET", "/api/tenants/")

        # 恢复Token
        self.access_token = saved_token

        if response and response.status_code == 401:
            self.log("✅ 未授权访问被正确拒绝")
            self.add_result("未授权访问保护", True)
        else:
            status = response.status_code if response else "无响应"
            self.log(f"❌ 未授权访问未被拒绝，状态码: {status}")
            self.add_result("未授权访问保护", False, f"期望401，实际{status}")

    def test_protected_api_with_token(self):
        """测试授权访问受保护的API"""
        if not self.access_token:
            self.log("❌ 无有效Token，跳过授权访问测试")
            self.add_result("授权访问保护", False, "无有效Token")
            return

        self.log("测试授权访问受保护的API...")

        response = self.make_request("GET", "/api/tenants/")

        if response:
            # 200表示成功（可能是空列表），404表示未找到（但API可访问）
            if response.status_code in [200, 404]:
                self.log("✅ 授权访问成功（API可访问）")
                self.add_result("授权访问保护", True)
            else:
                status = response.status_code
                error = response.text if response.text else "未知错误"
                self.log(f"⚠️ API访问异常，状态码: {status}")
                self.add_result("授权访问保护", False, f"状态码: {status}, 错误: {error}")
        else:
            self.log("❌ 无响应")
            self.add_result("授权访问保护", False, "无响应")

    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "="*80)
        print(" " * 25 + "JWT认证功能测试")
        print(" " * 30 + f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        # 测试登录
        self.test_login()

        # 只有登录成功才进行后续测试
        if self.access_token:
            # 测试Token相关功能
            self.test_verify_token()
            self.test_get_user_info()

            # 测试Token刷新
            self.test_refresh_token()

            # 测试API保护
            self.test_protected_api_without_token()
            self.test_protected_api_with_token()

            # 测试登出
            self.test_logout()
        else:
            self.log("⚠️ 登录失败，跳过后续测试")

        # 打印测试结果
        self.print_results()

    def print_results(self):
        """打印测试结果"""
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed

        print("\n" + "="*80)
        print("JWT认证测试结果")
        print("="*80)

        print("\n✅ 通过的测试:")
        for name, success, _ in self.results:
            if success:
                print(f"  - {name}")

        if failed > 0:
            print("\n❌ 失败的测试:")
            for name, success, error in self.results:
                if not success:
                    error_msg = f": {error}" if error else ""
                    print(f"  - {name}{error_msg}")

        print(f"\n总计: {passed}/{total} 通过")
        return passed == total


def main():
    """运行JWT认证测试"""
    tester = JWTAuthTester()
    tester.run_all_tests()

    return 0 if all(success for _, success, _ in tester.results) else 1


if __name__ == "__main__":
    sys.exit(main())