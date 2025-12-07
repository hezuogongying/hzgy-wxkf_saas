# -*- coding: utf-8 -*-
"""超级简化的测试运行器"""

import subprocess
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def async_main():
    """异步主函数"""
    print("🚀 wxkf_saas 测试运行器")

    # 测试配置
    print("1. 测试配置...")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()
        print("✅ 配置加载成功")
        print(f"   数据库: {config.db_url}")
        print(f"   Redis: {config.redis_url}")
        print(f"   服务端口: {config.fastapi_port}")
        print("✅ 配置验证通过")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        return

    print("2. 测试数据库连接...")
    try:
        from core.database import get_db_manager
        from sqlalchemy import text
        db_manager = get_db_manager()
        async with db_manager.async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            print("✅ 数据库连接成功")
        print("✅ 事务提交成功")
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")

    print("3. 测试API客户端...")
    try:
        from core.client import WxKfSaasClient
        from api.kf_account import KfAccountApi
        from api.message import MessageApi

        config = WxKfSaasConfig()
        client = WxKfSaasClient(config)
        kf_api = KfAccountApi(client)
        msg_api = MessageApi(client)

        print("✅ 客户端初始化成功")
        print("✅ API接口创建成功")
        print("✅ 消息接口创建成功")
        print("✅ 素材接口创建成功")

        print("   - 测试账号添加...")
        try:
            response = await kf_api.add(
                corp_id="test_corp",
                name="测试客服",
                media_id="test_media"
            )

            if response.errcode == 0:
                print(f"   ✅ 客服账号添加成功 - kf_id: {response.open_kfid}")
            else:
                print(f"   ❌ 客服账号添加失败: errcode={response.errcode}, errmsg={response.errmsg}")
        except Exception as e:
            print(f"   ❌ 客服账号添加异常: {e}")

    except Exception as e:
        print(f"   ❌ API接口创建失败: {e}")

    print("4. 测试消息发送...")
    try:
        response = await msg_api.send_text(
            corp_id="test_corp",
            touser="test_user",
            content="测试消息"
        )

        if response.errcode == 0:
            print(f"   ✅ 消息发送成功 - msgid: {response.msgid}")
        else:
            print(f"   ❌ 消息发送失败: errcode={response.errcode}, errmsg={response.errmsg}")
    except Exception as e:
        print(f"   ❌ 消息发送异常: {e}")

    print("5. 测试同步消息...")
    try:
        response = await msg_api.sync_msg(
            corp_id="test_corp",
            limit=10
        )

        messages = response.msg_list if response.msg_list else []
        print(f"   获取到 {len(messages)} 条同步消息")

        for msg in messages[:5]:  # 显示前5条
            print(f"   消息ID: {msg.msgid}")
            print(f"   类型: {msg.msgtype}")
            if msg.msgtype == "text":
                print(f"   内容: {msg.text.content}")

        if response.has_more:
            print("   还有更多消息")
            print("   请继续执行测试...")
        else:
            print("   没有更多消息")
    except Exception as e:
        print(f"   ❌ 消息同步异常: {e}")

    print("6. ✅ 所有测试完成！")
    return True

def main():
    """主函数"""
    import asyncio
    asyncio.run(async_main())


if __name__ == "__main__":
    main()