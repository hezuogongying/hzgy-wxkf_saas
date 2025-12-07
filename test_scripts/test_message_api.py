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
    """测试 Token 管理器"""
    print("\n[1/4] 测试 Token 管理...")
    try:
        from core.token_manager import MultiTenantTokenManager
        from core.config import WxKfSaasConfig

        config = WxKfSaasConfig()
        token_manager = MultiTenantTokenManager(config)

        # 测试获取企业 access_token
        print(f"   获取企业 Token: {config.corp_id}")
        token = token_manager.get_access_token(config.corp_id)
        print(f"   ✅ Token 获取成功: {token[:20]}...")
        return True, token
    except Exception as e:
        print(f"   ❌ Token 获取失败: {e}")
        return False, None


def test_wx_client(token):
    """测试微信客服客户端"""
    print("\n[2/4] 测试微信客服客户端...")
    try:
        from core.client import WxKfSaasClient
        from core.config import WxKfSaasConfig

        config = WxKfSaasConfig()
        client = WxKfSaasClient(config)

        print(f"   客户端初始化成功")
        return True, client
    except Exception as e:
        print(f"   ❌ 客户端初始化失败: {e}")
        return False, None


def test_get_service_status(client):
    """测试获取客服服务状态"""
    print("\n[3/4] 测试获取客服服务状态...")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()

        response = client.get_service_status(corp_id=config.corp_id)
        print(f"   ✅ 服务状态获取成功")
        print(f"   服务状态: {response.status}")
        if response.status.value == 1:
            print("   - 服务状态: 启用")
        else:
            print("   - 服务状态: 未启用")
        return True
    except Exception as e:
        print(f"   ❌ 服务状态获取失败: {e}")
        return False


def test_send_text_message(client):
    """测试发送文本消息（仅测试请求格式）"""
    print("\n[4/4] 测试文本消息格式...")
    try:
        from core.config import WxKfSaasConfig
        from core.models.message import TextMessageRequest

        config = WxKfSaasConfig()

        # 构造测试消息（仅测试格式，不实际发送）
        test_message = TextMessageRequest(
            touser="test_user",  # 测试用户ID
            agentid=1000001,     # 测试应用ID
            msgtype="text",
            text={
                "content": "这是一条测试消息，仅验证格式。"
            }
        )

        print(f"   ✅ 消息格式构造成功")
        print(f"   消息类型: {test_message.msgtype}")
        print(f"   消息内容: {test_message.text['content'][:20]}...")

        # 注意：这里不实际发送，只验证格式
        print("   ⚠️ 跳过实际发送（避免测试消息干扰）")
        return True
    except Exception as e:
        print(f"   ❌ 消息格式测试失败: {e}")
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

    # 测试获取服务状态
    service_result = test_get_service_status(client)

    # 测试消息格式
    message_result = test_send_text_message(client)

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("-"*60)
    print(f"Token 管理:    {'✅ 通过' if token_result else '❌ 失败'}")
    print(f"客户端初始化:  {'✅ 通过' if client_result else '❌ 失败'}")
    print(f"服务状态获取:  {'✅ 通过' if service_result else '❌ 失败'}")
    print(f"消息格式测试:  {'✅ 通过' if message_result else '❌ 失败'}")

    total = sum([token_result, client_result, service_result, message_result])
    print(f"\n总计: {total}/4 通过")

    if total == 4:
        print("\n🎉 所有消息 API 测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查配置")

    print("="*60)


if __name__ == "__main__":
    main()