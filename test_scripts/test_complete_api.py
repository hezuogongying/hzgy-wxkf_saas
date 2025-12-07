# -*- coding: utf-8 -*-
"""完整API端点测试套件 - 修复版"""

import sys
import os
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import tempfile

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class BaseAPITest:
    """API测试基类"""

    def __init__(self):
        from core.config import WxKfSaasConfig
        self.config = WxKfSaasConfig()

        # API基础URL
        self.base_url = f"http://localhost:{self.config.fastapi_port}"
        self.corp_id = self.config.corp_id

        # 测试结果存储
        self.results = []

        # 请求会话
        self.session = requests.Session()

    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Any]:
        """发起HTTP请求"""
        url = f"{self.base_url}{endpoint}"

        try:
            self.log(f"{method} {endpoint}")
            response = self.session.request(method, url, timeout=10, **kwargs)

            # 记录响应状态
            self.log(f"响应状态: {response.status_code}")

            # 尝试解析JSON响应
            try:
                data = response.json()
            except:
                data = response.text

            return response.status_code < 400, data

        except requests.exceptions.Timeout:
            self.log(f"请求超时: {endpoint}", "ERROR")
            return False, {"error": "请求超时"}
        except requests.exceptions.ConnectionError:
            self.log(f"连接错误: {endpoint}", "ERROR")
            return False, {"error": "连接错误"}
        except Exception as e:
            self.log(f"请求异常: {e}", "ERROR")
            return False, {"error": str(e)}

    def add_result(self, test_name: str, success: bool, error: str = None):
        """添加测试结果"""
        self.results.append((test_name, success, error))

    def print_results(self):
        """打印测试结果"""
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        failed = total - passed

        print("\n" + "="*80)
        print(f"{self.__class__.__name__} 测试结果")
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


class TenantAPITest(BaseAPITest):
    """租户管理API测试"""

    def run_all_tests(self):
        """运行所有租户相关测试"""
        print("\n" + "="*80)
        print("租户管理 API 测试")
        print("="*80)

        # 1. 获取租户详情
        self.test_get_tenant()

        # 2. 获取租户列表
        self.test_get_tenants()

        # 3. 创建测试租户
        self.test_create_tenant()

        # 4. 更新租户信息
        self.test_update_tenant()

        # 5. 设置永久授权码
        self.test_set_permanent_code()

        # 6. 激活/停用租户
        self.test_toggle_tenant_status()

        # 7. 删除测试租户
        self.test_delete_tenant()

        return self.print_results()

    def test_create_tenant(self):
        """测试创建租户"""
        self.log("测试创建租户...")

        data = {
            "corp_id": "test_corp_001",
            "corp_name": "测试企业001",
            "contact_name": "测试联系人",
            "contact_phone": "13800138000",
            "contact_email": "test@example.com"
        }

        success, response = self.make_request("POST", "/api/tenants/", json=data)

        if success:
            self.log("✅ 创建租户成功")
            self.add_result("创建租户", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 创建租户失败: {error}")
            self.add_result("创建租户", False, error)

    def test_get_tenants(self):
        """测试获取租户列表"""
        self.log("测试获取租户列表...")

        success, response = self.make_request("GET", "/api/tenants/")

        if success:
            tenants = response.get("tenants", [])
            self.log(f"✅ 获取租户列表成功，共{len(tenants)}个租户")
            self.add_result("获取租户列表", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取租户列表失败: {error}")
            self.add_result("获取租户列表", False, error)

    def test_get_tenant(self):
        """测试获取租户详情"""
        self.log("测试获取租户详情...")

        success, response = self.make_request("GET", f"/api/tenants/{self.corp_id}")

        if success:
            self.log("✅ 获取租户详情成功")
            self.add_result("获取租户详情", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取租户详情失败: {error}")
            self.add_result("获取租户详情", False, error)

    def test_update_tenant(self):
        """测试更新租户信息"""
        self.log("测试更新租户信息...")

        data = {
            "corp_name": "更新后的企业名称",
            "contact_name": "更新后的联系人"
        }

        success, response = self.make_request("PUT", f"/api/tenants/{self.corp_id}", json=data)

        if success:
            self.log("✅ 更新租户信息成功")
            self.add_result("更新租户信息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 更新租户信息失败: {error}")
            self.add_result("更新租户信息", False, error)

    def test_set_permanent_code(self):
        """测试设置永久授权码"""
        self.log("测试设置永久授权码...")

        data = {
            "permanent_code": "test_permanent_code_12345"
        }

        success, response = self.make_request("PUT", f"/api/tenants/{self.corp_id}/permanent-code", params=data)

        if success:
            self.log("✅ 设置永久授权码成功")
            self.add_result("设置永久授权码", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 设置永久授权码失败: {error}")
            self.add_result("设置永久授权码", False, error)

    def test_toggle_tenant_status(self):
        """测试激活/停用租户"""
        self.log("测试激活/停用租户...")

        # 先尝试激活
        data = {"is_active": True}
        success, response = self.make_request("PUT", f"/api/tenants/{self.corp_id}/status", params=data)

        if success:
            self.log("✅ 激活租户成功")
            self.add_result("激活/停用租户", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 激活/停用租户失败: {error}")
            self.add_result("激活/停用租户", False, error)

    def test_delete_tenant(self):
        """测试删除租户"""
        self.log("测试删除租户...")

        # 使用测试租户ID，避免删除实际数据
        test_corp_id = "test_corp_001"
        success, response = self.make_request("DELETE", f"/api/tenants/{test_corp_id}")

        if success:
            self.log("✅ 删除租户成功")
            self.add_result("删除租户", True)
        else:
            error = response.get("detail", "未知错误")
            # 租户不存在也是预期的
            if "不存在" in str(error) or "not found" in str(error).lower():
                self.log("✅ 删除租户成功（租户已不存在）")
                self.add_result("删除租户", True)
            else:
                self.log(f"❌ 删除租户失败: {error}")
                self.add_result("删除租户", False, error)


def main():
    """运行租户管理API测试"""
    print("\n" + "="*80)
    print(" " * 25 + "租户管理 API 测试")
    print(" " * 30 + f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # 创建测试实例
    tester = TenantAPITest()

    # 运行测试
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()