# -*- coding: utf-8 -*-
"""微信消息收发功能测试"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import wxkf_saas.core.config as config_module
from wxkf_saas.core.client import WxKfSaasClient
from wxkf_saas.api.message import MessageApi
from wxkf_saas.api.media import MediaApi


async def test_message_apis():
    """测试消息API功能"""
    print("🧪 测试微信消息收发API")
    print("=" * 50)

    try:
        # 初始化配置和客户端
        print("1. 初始化配置和客户端...")
        config = config_module.Config()
        client = WxKfSaasClient(config)
        msg_api = MessageApi(client)
        media_api = MediaApi(client)

        print("✅ 配置和客户端初始化成功")

        # 测试参数
        test_corp_id = "test_corp_001"
        test_user = "test_user_001"

        print(f"\n2. 测试文本消息发送 (corp_id: {test_corp_id}, user: {test_user})...")

        # 发送文本消息
        try:
            response = await msg_api.send_text(
                corp_id=test_corp_id,
                touser=test_user,
                content="这是一条测试消息，用于验证消息发送功能。"
            )

            if response.errcode == 0:
                print(f"✅ 文本消息发送成功")
                print(f"   消息ID: {response.msgid}")
                print(f"   用户: {test_user}")
                print(f"   内容: 这是一条测试消息，用于验证消息发送功能。")
            else:
                print(f"❌ 文本消息发送失败")
                print(f"   错误码: {response.errcode}")
                print(f"   错误信息: {response.errmsg}")

        except Exception as e:
            print(f"❌ 文本消息发送异常: {e}")

        print("\n3. 测试图片消息发送...")

        # 发送图片消息（需要先上传图片素材）
        try:
            # 这里使用一个示例media_id，实际使用时需要先上传图片
            test_media_id = "test_image_media_001"

            response = await msg_api.send_image(
                corp_id=test_corp_id,
                touser=test_user,
                media_id=test_media_id
            )

            if response.errcode == 0:
                print(f"✅ 图片消息发送成功")
                print(f"   消息ID: {response.msgid}")
                print(f"   素材ID: {test_media_id}")
            else:
                print(f"❌ 图片消息发送失败")
                print(f"   错误码: {response.errcode}")
                print(f"   错误信息: {response.errmsg}")

        except Exception as e:
            print(f"❌ 图片消息发送异常: {e}")

        print("\n4. 测试消息同步...")

        try:
            # 同步最近的消息
            sync_response = await msg_api.sync_msg(
                corp_id=test_corp_id,
                limit=10,  # 获取最近10条消息
                cursor=None  # 从最新消息开始
            )

            print(f"✅ 消息同步请求成功")
            print(f"   获取到消息数: {len(sync_response.msg_list) if sync_response.msg_list else 0}")
            print(f"   是否还有更多消息: {sync_response.has_more}")

            if sync_response.msg_list:
                print("\n   最近的消息列表:")
                for i, msg in enumerate(sync_response.msg_list[:5], 1):
                    print(f"   {i}. 消息ID: {msg.msgid}")
                    print(f"      类型: {msg.msgtype}")
                    print(f"      时间: {msg.create_time}")

                    # 根据消息类型显示不同内容
                    if msg.msgtype == "text":
                        print(f"      文本内容: {msg.text.content}")
                    elif msg.msgtype == "image":
                        print(f"      图片素材ID: {msg.image.media_id}")
                        print(f"      图片URL: {msg.image.pic_url}")
                    elif msg.msgtype == "voice":
                        print(f"      语音素材ID: {msg.voice.media_id}")
                        print(f"      语音时长: {msg.voice.voice_duration}秒")
                    elif msg.msgtype == "video":
                        print(f"      视频素材ID: {msg.video.media_id}")
                        print(f"      视频时长: {msg.video.play_length}秒")
                        print(f"      视频封面ID: {msg.video.thumb_media_id}")
                    elif msg.msgtype == "file":
                        print(f"      文件素材ID: {msg.file.media_id}")
                        print(f"      文件名: {msg.file.title}")
                        print(f"      文件大小: {msg.file.file_size}字节")

                    print(f"      方向: {'客服发送' if msg.direction == 'send' else '用户接收'}")
                    print(f"      服务状态: {msg.service_status}")
                    print()

        except Exception as e:
            print(f"❌ 消息同步异常: {e}")

        print("\n5. 测试事务性消息发送...")

        try:
            # 测试事务性消息（需要接收方的确认）
            response = await msg_api.send_msg_on_event(
                corp_id=test_corp_id,
                touser=test_user,
                msgtype="text",
                content="这是一条事务性消息，需要用户确认。"
            )

            if response.errcode == 0:
                print(f"✅ 事务性消息发送成功")
                print(f"   消息ID: {response.msgid}")
            else:
                print(f"❌ 事务性消息发送失败")
                print(f"   错误码: {response.errcode}")
                print(f"   错误信息: {response.errmsg}")

        except Exception as e:
            print(f"❌ 事务性消息发送异常: {e}")

        print("\n" + "=" * 50)
        print("🎉 消息API测试完成！")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        return False


async def test_media_apis():
    """测试素材API功能"""
    print("\n🧪 测试素材管理API")
    print("=" * 50)

    try:
        # 初始化配置和客户端
        config = config_module.Config()
        client = WxKfSaasClient(config)
        media_api = MediaApi(client)

        test_corp_id = "test_corp_001"

        print("1. 测试临时素材上传...")

        # 创建一个测试图片文件
        test_image_path = "test_image.jpg"
        test_image_content = b"fake_image_content_for_testing"

        try:
            # 写入测试图片文件
            with open(test_image_path, "wb") as f:
                f.write(test_image_content)

            # 上传临时图片素材
            upload_response = await media_api.upload(
                corp_id=test_corp_id,
                media_type="image",
                file_path=test_image_path
            )

            if upload_response.errcode == 0:
                print(f"✅ 临时图片素材上传成功")
                print(f"   素材ID: {upload_response.media_id}")
                print(f"   文件类型: {upload_response.type}")
                print(f"   创建时间: {upload_response.created_at}")

                # 测试获取素材
                print("\n2. 测试获取临时素材...")
                try:
                    get_response = await media_api.get(
                        corp_id=test_corp_id,
                        media_id=upload_response.media_id
                    )

                    if hasattr(get_response, 'status_code') and get_response.status_code == 200:
                        print(f"✅ 临时素材获取成功")
                        print(f"   内容类型: {get_response.headers.get('content-type')}")
                        print(f"   内容长度: {len(get_response.content)}字节")
                    else:
                        print(f"❌ 临时素材获取失败")
                except Exception as e:
                    print(f"❌ 临时素材获取异常: {e}")

            else:
                print(f"❌ 临时图片素材上传失败")
                print(f"   错误码: {upload_response.errcode}")
                print(f"   错误信息: {upload_response.errmsg}")

        except Exception as e:
            print(f"❌ 临时素材上传异常: {e}")

        finally:
            # 清理测试文件
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

        print("\n" + "=" * 50)
        print("🎉 素材API测试完成！")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"❌ 素材API测试过程中发生错误: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 微信客服消息收发功能测试")
    print("=" * 60)

    # 测试消息API
    message_success = await test_message_apis()

    # 测试素材API
    media_success = await test_media_apis()

    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"   消息API测试: {'✅ 通过' if message_success else '❌ 失败'}")
    print(f"   素材API测试: {'✅ 通过' if media_success else '❌ 失败'}")

    if message_success and media_success:
        print("\n🎉 所有测试通过！消息收发功能正常。")
    else:
        print("\n⚠️  部分测试失败，请检查配置和网络连接。")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())