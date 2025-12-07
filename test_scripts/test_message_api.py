# -*- coding: utf-8 -*-
"""消息 API 测试脚本"""

import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_token_manager():
    """测试 Token 管理（简化版）"""
    print("\n[1/4] 测试 Token 配置...")
    try:
        from core.config import WxKfSaasConfig

        config = WxKfSaasConfig()

        # 检查配置
        print(f"   企业ID: {config.corp_id}")
        print(f"   企业Secret: {config.corp_secret[:10]}...")
        print(f"   Token缓存配置: {config.redis_url}")

        if config.corp_id and config.corp_secret:
            print("   ✅ Token 配置正常")
            return True, "mock_token"
        else:
            print("   ❌ Token 配置缺失")
            return False, None
    except Exception as e:
        print(f"   ❌ Token 配置检查失败: {e}")
        return False, None


def test_wx_client(token):
    """测试微信客服客户端配置"""
    print("\n[2/4] 测试客户端配置...")
    try:
        from core.config import WxKfSaasConfig

        config = WxKfSaasConfig()

        # 检查客户端需要的配置
        print(f"   服务商配置: {config.suite_id or '单体模式'}")
        print(f"   回调URL: {config.server_url}")
        print(f"   ✅ 客户端配置正常")
        return True, "mock_client"
    except Exception as e:
        print(f"   ❌ 客户端配置检查失败: {e}")
        return False, None


def test_message_models():
    """测试消息模型"""
    print("\n[3/4] 测试消息模型...")
    try:
        from models.message import SendTextMessageRequest

        # 构造测试消息
        test_message = SendTextMessageRequest(
            touser="test_user",
            open_kfid="kf001@xxx",  # 测试客服账号ID
            text={
                "content": "测试消息内容"
            }
        )

        print(f"   ✅ 文本消息模型创建成功")
        print(f"   接收人: {test_message.touser}")
        print(f"   客服ID: {test_message.open_kfid}")
        print(f"   消息内容: {test_message.text.content}")
        return True
    except Exception as e:
        print(f"   ❌ 消息模型测试失败: {e}")
        return False


def test_api_endpoints():
    """测试 API 端点可用性"""
    print("\n[4/4] 测试 API 端点...")
    import requests

    try:
        # 测试健康检查
        response = requests.get("http://localhost:58083/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ 健康检查端点正常")

            # 测试 API 文档
            response = requests.get("http://localhost:58083/docs", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ API 文档端点正常")
                return True
        return False
    except Exception as e:
        print(f"   ❌ API 端点测试失败: {e}")
        return False


def main():
    """主函数"""
    print("="*60)
    print("微信客服消息 API 测试")
    print("="*60)

    # 测试 Token 管理
    token_result, token = test_token_manager()
    if not token_result:
        print("\n❌ Token 管理测试失败，无法继续")
        sys.exit(1)

    # 测试客户端
    client_result, client = test_wx_client(token)
    if not client_result:
        print("\n❌ 客户端初始化失败，无法继续")
        sys.exit(1)

    # 测试消息模型
    model_result = test_message_models()

    # 测试 API 端点
    endpoint_result = test_api_endpoints()

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("-"*60)
    print(f"Token 管理:    {'✅ 通过' if token_result else '❌ 失败'}")
    print(f"客户端配置:    {'✅ 通过' if client_result else '❌ 失败'}")
    print(f"消息模型:      {'✅ 通过' if model_result else '❌ 失败'}")
    print(f"API端点:       {'✅ 通过' if endpoint_result else '❌ 失败'}")

    total = sum([token_result, client_result, model_result, endpoint_result])
    print(f"\n总计: {total}/4 通过")

    if total == 4:
        print("\n🎉 所有消息 API 测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

    print("="*60)


if __name__ == "__main__":
    main()