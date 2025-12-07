# -*- coding: utf-8 -*-
"""消息完整API测试脚本"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 导入基础测试类
from test_complete_api import BaseAPITest


class MessageCompleteAPITest(BaseAPITest):
    """消息完整API测试"""

    def run_all_tests(self):
        """运行所有消息完整相关测试"""
        print("\n" + "="*80)
        print("消息完整 API 测试")
        print("="*80)

        # 基础消息类型测试
        self.test_send_text_complete()
        self.test_send_image_complete()
        self.test_send_voice_complete()
        self.test_send_video_complete()
        self.test_send_file_complete()

        # 特殊消息类型测试
        self.test_send_location_complete()
        self.test_send_miniprogram_complete()
        self.test_send_channels_shop_product()
        self.test_send_channels_shop_order()
        self.test_send_merged_msg()
        self.test_send_channels()
        self.test_send_note()

        # 功能测试
        self.test_sync_complete()
        self.test_send_welcome_complete()
        self.test_recall_complete()

        return self.print_results()

    def test_send_text_complete(self):
        """测试发送文本消息（完整版）"""
        self.log("测试发送文本消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "content": "这是一条完整版测试文本消息"
        }

        success, response = self.make_request("POST", "/message-complete/text", json=data)

        if success:
            self.log("✅ 发送文本消息（完整版）成功")
            self.add_result("发送文本消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送文本消息（完整版）失败: {error}")
            self.add_result("发送文本消息（完整版）", False, error)

    def test_send_image_complete(self):
        """测试发送图片消息（完整版）"""
        self.log("测试发送图片消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_image_media_id_complete_123"
        }

        success, response = self.make_request("POST", "/message-complete/image", json=data)

        if success:
            self.log("✅ 发送图片消息（完整版）成功")
            self.add_result("发送图片消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送图片消息（完整版）失败: {error}")
            self.add_result("发送图片消息（完整版）", False, error)

    def test_send_voice_complete(self):
        """测试发送语音消息（完整版）"""
        self.log("测试发送语音消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_voice_media_id_complete_123",
            "voice_duration": 45
        }

        success, response = self.make_request("POST", "/message-complete/voice", json=data)

        if success:
            self.log("✅ 发送语音消息（完整版）成功")
            self.add_result("发送语音消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送语音消息（完整版）失败: {error}")
            self.add_result("发送语音消息（完整版）", False, error)

    def test_send_video_complete(self):
        """测试发送视频消息（完整版）"""
        self.log("测试发送视频消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_video_media_id_complete_123",
            "thumb_media_id": "test_thumb_media_id_complete_123",
            "title": "完整版测试视频",
            "description": "这是一个完整版测试视频"
        }

        success, response = self.make_request("POST", "/message-complete/video", json=data)

        if success:
            self.log("✅ 发送视频消息（完整版）成功")
            self.add_result("发送视频消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频消息（完整版）失败: {error}")
            self.add_result("发送视频消息（完整版）", False, error)

    def test_send_file_complete(self):
        """测试发送文件消息（完整版）"""
        self.log("测试发送文件消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_file_media_id_complete_123",
            "title": "完整版测试文件.pdf",
            "file_size": 2048000
        }

        success, response = self.make_request("POST", "/message-complete/file", json=data)

        if success:
            self.log("✅ 发送文件消息（完整版）成功")
            self.add_result("发送文件消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送文件消息（完整版）失败: {error}")
            self.add_result("发送文件消息（完整版）", False, error)

    def test_send_location_complete(self):
        """测试发送位置消息"""
        self.log("测试发送位置消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "location": {
                "latitude": 39.908823,
                "longitude": 116.397470,
                "name": "北京市东城区",
                "address": "完整版测试地址"
            }
        }

        success, response = self.make_request("POST", "/message-complete/location", json=data)

        if success:
            self.log("✅ 发送位置消息成功")
            self.add_result("发送位置消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送位置消息失败: {error}")
            self.add_result("发送位置消息", False, error)

    def test_send_miniprogram_complete(self):
        """测试发送小程序消息"""
        self.log("测试发送小程序消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "miniprogram": {
                "title": "完整版测试小程序",
                "appid": "wx1234567890abcdef",
                "pagepath": "/pages/index/index",
                "thumb_media_id": "test_thumb_media_id_complete_123"
            }
        }

        success, response = self.make_request("POST", "/message-complete/miniprogram", json=data)

        if success:
            self.log("✅ 发送小程序消息成功")
            self.add_result("发送小程序消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送小程序消息失败: {error}")
            self.add_result("发送小程序消息", False, error)

    def test_send_channels_shop_product(self):
        """测试发送视频号商品消息"""
        self.log("测试发送视频号商品消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "product": {
                "title": "完整版测试商品",
                "description": "这是一个完整版测试商品描述",
                "image_media_id": "test_image_media_id_complete_123",
                "url": "https://example.com/product/123",
                "price": 19900
            }
        }

        success, response = self.make_request("POST", "/message-complete/channels_shop_product", json=data)

        if success:
            self.log("✅ 发送视频号商品消息成功")
            self.add_result("发送视频号商品消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频号商品消息失败: {error}")
            self.add_result("发送视频号商品消息", False, error)

    def test_send_channels_shop_order(self):
        """测试发送视频号订单消息"""
        self.log("测试发送视频号订单消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "order": {
                "order_number": "COMPLETE_ORDER_123456",
                "order_status": 2,
                "pay_time": 1234567890,
                "product_list": [
                    {
                        "product_img_url": "https://example.com/product.jpg",
                        "product_title": "完整版测试商品",
                        "product_price": 19900
                    }
                ]
            }
        }

        success, response = self.make_request("POST", "/message-complete/channels_shop_order", json=data)

        if success:
            self.log("✅ 发送视频号订单消息成功")
            self.add_result("发送视频号订单消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频号订单消息失败: {error}")
            self.add_result("发送视频号订单消息", False, error)

    def test_send_merged_msg(self):
        """测试发送聊天记录消息"""
        self.log("测试发送聊天记录消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "merged_msg": {
                "title": "完整版聊天记录",
                "digest": "聊天记录摘要",
                "item_list": [
                    {
                        "msgtype": "text",
                        "content": "测试消息内容"
                    }
                ]
            }
        }

        success, response = self.make_request("POST", "/message-complete/merged_msg", json=data)

        if success:
            self.log("✅ 发送聊天记录消息成功")
            self.add_result("发送聊天记录消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送聊天记录消息失败: {error}")
            self.add_result("发送聊天记录消息", False, error)

    def test_send_channels(self):
        """测试发送视频号消息"""
        self.log("测试发送视频号消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "channels": {
                "finder_user_name": "v2_060100231100000000000001",
                "feed_id": "1000000000000000000000"
            }
        }

        success, response = self.make_request("POST", "/message-complete/channels", json=data)

        if success:
            self.log("✅ 发送视频号消息成功")
            self.add_result("发送视频号消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频号消息失败: {error}")
            self.add_result("发送视频号消息", False, error)

    def test_send_note(self):
        """测试发送笔记消息"""
        self.log("测试发送笔记消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "note": {
                "title": "完整版测试笔记",
                "pagepath": "pages/note/detail",
                "finder_user_name": "finder_user_123",
                "feed_id": "feed_id_456"
            }
        }

        success, response = self.make_request("POST", "/message-complete/note", json=data)

        if success:
            self.log("✅ 发送笔记消息成功")
            self.add_result("发送笔记消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送笔记消息失败: {error}")
            self.add_result("发送笔记消息", False, error)

    def test_sync_complete(self):
        """测试同步消息（完整版）"""
        self.log("测试同步消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "cursor": "0",
            "limit": 1000,
            "voice_format": 0
        }

        success, response = self.make_request("POST", "/message-complete/sync", json=data)

        if success:
            self.log("✅ 同步消息（完整版）成功")
            self.add_result("同步消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 同步消息（完整版）失败: {error}")
            self.add_result("同步消息（完整版）", False, error)

    def test_send_welcome_complete(self):
        """测试发送欢迎语（完整版）"""
        self.log("测试发送欢迎语（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "welcome_msg": {
                "text": {
                    "content": "欢迎使用完整版客服服务！"
                },
                "media_id": "test_welcome_media_id_123"
            }
        }

        success, response = self.make_request("POST", "/message-complete/welcome", json=data)

        if success:
            self.log("✅ 发送欢迎语（完整版）成功")
            self.add_result("发送欢迎语（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送欢迎语（完整版）失败: {error}")
            self.add_result("发送欢迎语（完整版）", False, error)

    def test_recall_complete(self):
        """测试撤回消息（完整版）"""
        self.log("测试撤回消息（完整版）...")

        data = {
            "corp_id": self.corp_id,
            "msgid": "test_complete_msg_id_123",
            "usermsgid": "test_complete_user_msg_id_456"
        }

        success, response = self.make_request("POST", "/message-complete/recall", json=data)

        if success:
            self.log("✅ 撤回消息（完整版）成功")
            self.add_result("撤回消息（完整版）", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 撤回消息（完整版）失败: {error}")
            self.add_result("撤回消息（完整版）", False, error)


def main():
    """运行消息完整API测试"""
    print("\n" + "="*80)
    print(" " * 25 + "消息完整 API 测试")
    print(" " * 30 + f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # 创建测试实例
    tester = MessageCompleteAPITest()

    # 运行测试
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()