# -*- coding: utf-8 -*-
"""简化的API测试"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_api_import():
    """测试API模块导入"""
    print("1. 测试API模块导入...")

    try:
        # 测试相对导入
        from core.client import WxKfSaasClient
        from api.kf_account import KfAccountApi
        from api.message import MessageApi
        print("✅ API模块导入成功")
        return True
    except Exception as e:
        print(f"❌ API模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_instantiation():
    """测试API实例化"""
    print("2. 测试API实例化...")

    try:
        from core.client import WxKfSaasClient
        from core.config import WxKfSaasConfig
        from api.kf_account import KfAccountApi
        from api.message import MessageApi

        # 创建配置（使用环境变量或默认值）
        config = WxKfSaasConfig()
        client = WxKfSaasClient(config)
        kf_api = KfAccountApi(client)
        msg_api = MessageApi(client)

        print("✅ API实例化成功")
        print(f"   - 客户端: {type(client).__name__}")
        print(f"   - 客服API: {type(kf_api).__name__}")
        print(f"   - 消息API: {type(msg_api).__name__}")
        return True
    except Exception as e:
        print(f"❌ API实例化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_methods():
    """测试API方法"""
    print("3. 测试API方法...")

    try:
        from core.client import WxKfSaasClient
        from api.kf_account import KfAccountApi
        from core.config import WxKfSaasConfig

        config = WxKfSaasConfig()
        client = WxKfSaasClient(config)
        kf_api = KfAccountApi(client)

        # 检查方法是否存在
        methods = ['add', 'update', 'delete', 'get_list', 'get_account_link', 'get_customer_info']
        for method in methods:
            if hasattr(kf_api, method):
                print(f"   ✅ {method} 方法存在")
            else:
                print(f"   ❌ {method} 方法缺失")
                return False

        print("✅ API方法检查完成")
        return True
    except Exception as e:
        print(f"❌ API方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🧪 简化API测试运行器")

    tests = [
        test_api_import,
        test_api_instantiation,
        test_api_methods
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if test_func():
            passed += 1

    print(f"\n📊 测试结果:")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}")

    if passed == total:
        print("🎉 所有测试通过！")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)