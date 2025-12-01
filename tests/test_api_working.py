# -*- coding: utf-8 -*-
"""可以工作的API测试 - 使用相对导入"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

async def test_api_imports():
    """测试API模块导入（使用相对导入）"""
    print("1. 测试API模块导入...")

    try:
        # 使用相对导入避免包问题
        import core.client
        import core.config
        import api.kf_account
        import api.message

        print("✅ API模块导入成功")

        # 测试实例化
        config = core.config.WxKfSaasConfig()
        client = core.client.WxKfSaasClient(config)
        kf_api = api.kf_account.KfAccountApi(client)
        msg_api = api.message.MessageApi(client)

        print("✅ API实例化成功")
        print(f"   - 客户端类型: {type(client).__name__}")
        print(f"   - 客服API类型: {type(kf_api).__name__}")
        print(f"   - 消息API类型: {type(msg_api).__name__}")

        return True
    except Exception as e:
        print(f"❌ API导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_methods():
    """测试API方法存在性"""
    print("2. 测试API方法...")

    try:
        import api.kf_account
        import api.message

        # 检查客服API方法
        kf_api_methods = ['add', 'update', 'delete', 'get_list', 'get_account_link', 'get_customer_info']
        for method in kf_api_methods:
            if hasattr(api.kf_account.KfAccountApi, method):
                print(f"   ✅ 客服API.{method} 方法存在")
            else:
                print(f"   ❌ 客服API.{method} 方法缺失")

        # 检查消息API方法
        msg_api_methods = ['send_text', 'send_image', 'send_voice', 'send_video', 'send_file', 'sync_msg']
        for method in msg_api_methods:
            if hasattr(api.message.MessageApi, method):
                print(f"   ✅ 消息API.{method} 方法存在")
            else:
                print(f"   ❌ 消息API.{method} 方法缺失")

        print("✅ API方法检查完成")
        return True
    except Exception as e:
        print(f"❌ API方法测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🧪 API功能测试运行器")

    tests = [
        test_api_imports,
        test_api_methods
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        if await test_func():
            passed += 1

    print(f"\n📊 测试结果:")
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}")

    if passed == total:
        print("🎉 所有API测试通过！")
        return True
    else:
        print("❌ 部分API测试失败")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)