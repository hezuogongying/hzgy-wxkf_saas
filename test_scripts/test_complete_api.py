# -*- coding: utf-8 -*-
"""完整API端点测试套件"""

import sys
import os
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any
import tempfile
import time

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

        # 1. 创建租户
        self.test_create_tenant()

        # 2. 获取租户列表
        self.test_get_tenants()

        # 3. 获取租户详情
        self.test_get_tenant()

        # 4. 更新租户信息
        self.test_update_tenant()

        # 5. 设置永久授权码
        self.test_set_permanent_code()

        # 6. 激活/停用租户
        self.test_toggle_tenant_status()

        # 7. 删除租户
        self.test_delete_tenant()

        return self.print_results()


class KfAccountAPITest(BaseAPITest):
    """客服账号管理API测试"""

    def run_all_tests(self):
        """运行所有客服账号相关测试"""
        print("\n" + "="*80)
        print("客服账号管理 API 测试")
        print("="*80)

        # 1. 获取客服账号列表
        self.test_get_kf_accounts()

        # 2. 添加客服账号
        self.test_add_kf_account()

        # 3. 获取客服账号链接
        self.test_get_kf_account_link()

        # 4. 获取客户信息
        self.test_get_customer_info()

        # 5. 修改客服账号
        self.test_update_kf_account()

        # 6. 删除客服账号
        self.test_delete_kf_account()

        return self.print_results()


class MessageAPITest(BaseAPITest):
    """消息API测试"""

    def run_all_tests(self):
        """运行所有消息相关测试"""
        print("\n" + "="*80)
        print("消息 API 测试")
        print("="*80)

        # 1. 发送文本消息
        self.test_send_text_message()

        # 2. 发送图片消息
        self.test_send_image_message()

        # 3. 发送语音消息
        self.test_send_voice_message()

        # 4. 发送视频消息
        self.test_send_video_message()

        # 5. 发送文件消息
        self.test_send_file_message()

        # 6. 同步消息
        self.test_sync_message()

        # 7. 发送欢迎语
        self.test_send_welcome_message()

        # 8. 撤回消息
        self.test_recall_message()

        # 9. 发送视频号订单号消息
        self.test_send_video_order_number()

        # 10. 发送视频订单消息
        self.test_send_video_order_message()

        return self.print_results()


class MediaAPITest(BaseAPITest):
    """素材管理API测试"""

    def run_all_tests(self):
        """运行所有素材相关测试"""
        print("\n" + "="*80)
        print("素材管理 API 测试")
        print("="*80)

        # 1. 上传临时素材
        self.test_upload_temp_media()

        # 2. 获取临时素材
        self.test_get_temp_media()

        # 3. 下载临时素材
        self.test_download_temp_media()

        return self.print_results()


class ContactAPITest(BaseAPITest):
    """联系人管理API测试"""

    def run_all_tests(self):
        """运行所有联系人相关测试"""
        print("\n" + "="*80)
        print("联系人管理 API 测试")
        print("="*80)

        # 1. 设置客户联系Profile
        self.test_set_profile()

        # 2. 获取客户联系Profile
        self.test_get_profile()

        # 3. 批量获取客户联系Profile
        self.test_batch_get_profile()

        return self.print_results()

    def test_set_profile(self):
        """测试设置客户联系Profile"""
        self.log("测试设置客户联系Profile...")

        data = {
            "corp_id": self.corp_id,
            "profile": {
                "chat_id": "test_chat_id_123",
                "service_state": 1,
                "service_state_expires": 1234567890
            }
        }

        success, response = self.make_request("POST", f"/contact/set-profile/{self.corp_id}", json=data)

        if success:
            self.log("✅ 设置客户联系Profile成功")
            self.add_result("设置客户联系Profile", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 设置客户联系Profile失败: {error}")
            self.add_result("设置客户联系Profile", False, error)

    def test_get_profile(self):
        """测试获取客户联系Profile"""
        self.log("测试获取客户联系Profile...")

        params = {
            "chat_id": "test_chat_id_123"
        }

        success, response = self.make_request("GET", f"/contact/get-profile/{self.corp_id}", params=params)

        if success:
            self.log("✅ 获取客户联系Profile成功")
            self.add_result("获取客户联系Profile", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取客户联系Profile失败: {error}")
            self.add_result("获取客户联系Profile", False, error)

    def test_batch_get_profile(self):
        """测试批量获取客户联系Profile"""
        self.log("测试批量获取客户联系Profile...")

        data = {
            "chat_id_list": ["test_chat_id_123", "test_chat_id_456"],
            "need_enter_session_context": 0
        }

        success, response = self.make_request("POST", f"/contact/batch-get-profile/{self.corp_id}", json=data)

        if success:
            self.log("✅ 批量获取客户联系Profile成功")
            self.add_result("批量获取客户联系Profile", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 批量获取客户联系Profile失败: {error}")
            self.add_result("批量获取客户联系Profile", False, error)


class CallbackAPITest(BaseAPITest):
    """回调API测试"""

    def run_all_tests(self):
        """运行所有回调相关测试"""
        print("\n" + "="*80)
        print("回调 API 测试")
        print("="*80)

        # 1. 处理客服会话回调
        self.test_customer_service_callback()

        # 2. 处理企业授权事件回调
        self.test_suite_callback()

        # 3. 处理服务商授权事件回调
        self.test_provider_callback()

        # 4. 验证回调URL
        self.test_verify_callback()

        # 5. 验证服务商回调URL
        self.test_verify_provider_callback()

        # 6. 验证企业回调URL
        self.test_verify_suite_callback()

        # 7. 验证客服回调URL
        self.test_verify_customer_service_callback()

        return self.print_results()

    def test_customer_service_callback(self):
        """测试处理客服会话回调"""
        self.log("测试处理客服会话回调...")

        data = {
            "ToUserName": self.corp_id,
            "FromUserName": "test_open_kfid",
            "CreateTime": "1234567890",
            "MsgType": "event",
            "Event": "kf_service_session_info",
            "SessionStatus": 3
        }

        success, response = self.make_request("POST", "/callback/customer-service", json=data)

        if success:
            self.log("✅ 处理客服会话回调成功")
            self.add_result("处理客服会话回调", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 处理客服会话回调失败: {error}")
            self.add_result("处理客服会话回调", False, error)

    def test_suite_callback(self):
        """测试处理企业授权事件回调"""
        self.log("测试处理企业授权事件回调...")

        data = {
            "ToUserName": self.corp_id,
            "FromUserName": "test_suite_id",
            "CreateTime": "1234567890",
            "MsgType": "event",
            "Event": "create_auth",
            "AuthCorpId": "test_auth_corp_id"
        }

        success, response = self.make_request("POST", "/callback/suite", json=data)

        if success:
            self.log("✅ 处理企业授权事件回调成功")
            self.add_result("处理企业授权事件回调", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 处理企业授权事件回调失败: {error}")
            self.add_result("处理企业授权事件回调", False, error)

    def test_provider_callback(self):
        """测试处理服务商授权事件回调"""
        self.log("测试处理服务商授权事件回调...")

        data = {
            "ToUserName": self.corp_id,
            "FromUserName": "test_provider_id",
            "CreateTime": "1234567890",
            "MsgType": "event",
            "Event": "register_third_party_fast",
            "AuthCode": "test_auth_code_123"
        }

        success, response = self.make_request("POST", "/callback/provider", json=data)

        if success:
            self.log("✅ 处理服务商授权事件回调成功")
            self.add_result("处理服务商授权事件回调", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 处理服务商授权事件回调失败: {error}")
            self.add_result("处理服务商授权事件回调", False, error)

    def test_verify_callback(self):
        """测试验证回调URL"""
        self.log("测试验证回调URL...")

        params = {
            "msg_signature": "test_signature",
            "timestamp": "1234567890",
            "nonce": "test_nonce",
            "echostr": "test_echostr"
        }

        success, response = self.make_request("GET", "/callback/verify", params=params)

        if success:
            self.log("✅ 验证回调URL成功")
            self.add_result("验证回调URL", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 验证回调URL失败: {error}")
            self.add_result("验证回调URL", False, error)

    def test_verify_provider_callback(self):
        """测试验证服务商回调URL"""
        self.log("测试验证服务商回调URL...")

        params = {
            "msg_signature": "test_signature",
            "timestamp": "1234567890",
            "nonce": "test_nonce",
            "echostr": "test_echostr"
        }

        success, response = self.make_request("GET", "/callback/provider", params=params)

        if success:
            self.log("✅ 验证服务商回调URL成功")
            self.add_result("验证服务商回调URL", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 验证服务商回调URL失败: {error}")
            self.add_result("验证服务商回调URL", False, error)

    def test_verify_suite_callback(self):
        """测试验证企业回调URL"""
        self.log("测试验证企业回调URL...")

        params = {
            "msg_signature": "test_signature",
            "timestamp": "1234567890",
            "nonce": "test_nonce",
            "echostr": "test_echostr"
        }

        success, response = self.make_request("GET", "/callback/suite", params=params)

        if success:
            self.log("✅ 验证企业回调URL成功")
            self.add_result("验证企业回调URL", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 验证企业回调URL失败: {error}")
            self.add_result("验证企业回调URL", False, error)

    def test_verify_customer_service_callback(self):
        """测试验证客服回调URL"""
        self.log("测试验证客服回调URL...")

        params = {
            "msg_signature": "test_signature",
            "timestamp": "1234567890",
            "nonce": "test_nonce",
            "echostr": "test_echostr"
        }

        success, response = self.make_request("GET", "/callback/customer-service", params=params)

        if success:
            self.log("✅ 验证客服回调URL成功")
            self.add_result("验证客服回调URL", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 验证客服回调URL失败: {error}")
            self.add_result("验证客服回调URL", False, error)

    def test_upload_temp_media(self):
        """测试上传临时素材"""
        self.log("测试上传临时素材...")

        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"这是一个测试文件内容")
            tmp_path = tmp.name

        try:
            files = {
                "media": ("test_file.txt", open(tmp_path, "rb"), "text/plain")
            }
            data = {
                "corp_id": self.corp_id,
                "type": "file"
            }

            success, response = self.make_request("POST", "/media/upload", files=files, data=data)

            if success:
                media_id = response.get("media_id", "")
                self.log(f"✅ 上传临时素材成功，media_id: {media_id}")
                self.add_result("上传临时素材", True)
            else:
                error = response.get("detail", "未知错误")
                self.log(f"❌ 上传临时素材失败: {error}")
                self.add_result("上传临时素材", False, error)

        finally:
            # 清理临时文件
            if "files" in locals():
                files["media"][1].close()
            os.unlink(tmp_path)

    def test_get_temp_media(self):
        """测试获取临时素材"""
        self.log("测试获取临时素材...")

        params = {
            "corp_id": self.corp_id,
            "media_id": "test_media_id_123"
        }

        success, response = self.make_request("GET", f"/media/test_media_id_123", params=params)

        if success:
            self.log("✅ 获取临时素材成功")
            self.add_result("获取临时素材", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取临时素材失败: {error}")
            self.add_result("获取临时素材", False, error)

    def test_download_temp_media(self):
        """测试下载临时素材"""
        self.log("测试下载临时素材...")

        params = {
            "corp_id": self.corp_id,
            "media_id": "test_media_id_123"
        }

        success, response = self.make_request("GET", f"/media/download/test_media_id_123", params=params)

        if success:
            self.log("✅ 下载临时素材成功")
            self.add_result("下载临时素材", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 下载临时素材失败: {error}")
            self.add_result("下载临时素材", False, error)

    def test_send_text_message(self):
        """测试发送文本消息"""
        self.log("测试发送文本消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "content": "这是一条测试文本消息"
        }

        success, response = self.make_request("POST", "/message/text", json=data)

        if success:
            self.log("✅ 发送文本消息成功")
            self.add_result("发送文本消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送文本消息失败: {error}")
            self.add_result("发送文本消息", False, error)

    def test_send_image_message(self):
        """测试发送图片消息"""
        self.log("测试发送图片消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_image_media_id_123"
        }

        success, response = self.make_request("POST", "/message/image", json=data)

        if success:
            self.log("✅ 发送图片消息成功")
            self.add_result("发送图片消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送图片消息失败: {error}")
            self.add_result("发送图片消息", False, error)

    def test_send_voice_message(self):
        """测试发送语音消息"""
        self.log("测试发送语音消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_voice_media_id_123",
            "voice_duration": 30
        }

        success, response = self.make_request("POST", "/message/voice", json=data)

        if success:
            self.log("✅ 发送语音消息成功")
            self.add_result("发送语音消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送语音消息失败: {error}")
            self.add_result("发送语音消息", False, error)

    def test_send_video_message(self):
        """测试发送视频消息"""
        self.log("测试发送视频消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_video_media_id_123",
            "thumb_media_id": "test_thumb_media_id_123",
            "title": "测试视频",
            "description": "这是一个测试视频"
        }

        success, response = self.make_request("POST", "/message/video", json=data)

        if success:
            self.log("✅ 发送视频消息成功")
            self.add_result("发送视频消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频消息失败: {error}")
            self.add_result("发送视频消息", False, error)

    def test_send_file_message(self):
        """测试发送文件消息"""
        self.log("测试发送文件消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "media_id": "test_file_media_id_123",
            "title": "测试文件.pdf",
            "file_size": 1024000
        }

        success, response = self.make_request("POST", "/message/file", json=data)

        if success:
            self.log("✅ 发送文件消息成功")
            self.add_result("发送文件消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送文件消息失败: {error}")
            self.add_result("发送文件消息", False, error)

    def test_sync_message(self):
        """测试同步消息"""
        self.log("测试同步消息...")

        params = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "cursor": "0",
            "limit": 1000
        }

        success, response = self.make_request("GET", "/message/sync", params=params)

        if success:
            self.log("✅ 同步消息成功")
            self.add_result("同步消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 同步消息失败: {error}")
            self.add_result("同步消息", False, error)

    def test_send_welcome_message(self):
        """测试发送欢迎语"""
        self.log("测试发送欢迎语...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "welcome_msg": {
                "text": {
                    "content": "欢迎使用我们的客服服务！"
                }
            }
        }

        success, response = self.make_request("POST", "/message/welcome", json=data)

        if success:
            self.log("✅ 发送欢迎语成功")
            self.add_result("发送欢迎语", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送欢迎语失败: {error}")
            self.add_result("发送欢迎语", False, error)

    def test_recall_message(self):
        """测试撤回消息"""
        self.log("测试撤回消息...")

        data = {
            "corp_id": self.corp_id,
            "msgid": "test_msg_id_123",
            "usermsgid": "test_user_msg_id_456"
        }

        success, response = self.make_request("POST", "/message/recall", json=data)

        if success:
            self.log("✅ 撤回消息成功")
            self.add_result("撤回消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 撤回消息失败: {error}")
            self.add_result("撤回消息", False, error)

    def test_send_video_order_number(self):
        """测试发送视频号订单号消息"""
        self.log("测试发送视频号订单号消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "order_number": "TEST_ORDER_123456"
        }

        success, response = self.make_request("POST", "/message/send_video_order_number", json=data)

        if success:
            self.log("✅ 发送视频号订单号消息成功")
            self.add_result("发送视频号订单号消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频号订单号消息失败: {error}")
            self.add_result("发送视频号订单号消息", False, error)

    def test_send_video_order_message(self):
        """测试发送视频订单消息"""
        self.log("测试发送视频订单消息...")

        data = {
            "corp_id": self.corp_id,
            "open_kfid": "kf001@abc",
            "userid": "test_user_001",
            "order": {
                "order_number": "TEST_ORDER_123456",
                "order_status": 1,
                "pay_time": 1234567890,
                "open_order_id": "test_open_order_id",
                "product_list": [
                    {
                        "product_img_url": "https://example.com/product.jpg",
                        "product_title": "测试商品",
                        "product_price": 9900
                    }
                ]
            }
        }

        success, response = self.make_request("POST", "/message/send_video_order_message", json=data)

        if success:
            self.log("✅ 发送视频订单消息成功")
            self.add_result("发送视频订单消息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 发送视频订单消息失败: {error}")
            self.add_result("发送视频订单消息", False, error)

    def test_get_kf_accounts(self):
        """测试获取客服账号列表"""
        self.log("测试获取客服账号列表...")

        params = {"corp_id": self.corp_id}
        success, response = self.make_request("GET", "/kf-account/", params=params)

        if success:
            accounts = response.get("accounts", [])
            self.log(f"✅ 获取客服账号列表成功，共{len(accounts)}个账号")
            self.add_result("获取客服账号列表", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取客服账号列表失败: {error}")
            self.add_result("获取客服账号列表", False, error)

    def test_add_kf_account(self):
        """测试添加客服账号"""
        self.log("测试添加客服账号...")

        data = {
            "name": "测试客服",
            "media_id": "test_media_id_123",  # 需要有效的头像media_id
            "corp_id": self.corp_id
        }

        success, response = self.make_request("POST", "/kf-account/", json=data)

        if success:
            self.log("✅ 添加客服账号成功")
            self.add_result("添加客服账号", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 添加客服账号失败: {error}")
            self.add_result("添加客服账号", False, error)

    def test_get_kf_account_link(self):
        """测试获取客服账号链接"""
        self.log("测试获取客服账号链接...")

        # 使用测试的客服ID
        open_kfid = "kf001@abc"
        success, response = self.make_request("GET", f"/kf-account/{open_kfid}/link")

        if success:
            self.log("✅ 获取客服账号链接成功")
            self.add_result("获取客服账号链接", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取客服账号链接失败: {error}")
            self.add_result("获取客服账号链接", False, error)

    def test_get_customer_info(self):
        """测试获取客户信息"""
        self.log("测试获取客户信息...")

        # 使用测试的外部用户ID
        external_userid = "wo_external_userid_123"
        success, response = self.make_request("GET", f"/kf-account/customer/{external_userid}")

        if success:
            self.log("✅ 获取客户信息成功")
            self.add_result("获取客户信息", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 获取客户信息失败: {error}")
            self.add_result("获取客户信息", False, error)

    def test_update_kf_account(self):
        """测试修改客服账号"""
        self.log("测试修改客服账号...")

        # 使用测试的客服ID
        open_kfid = "kf001@abc"
        data = {
            "name": "更新后的客服名称",
            "corp_id": self.corp_id
        }

        success, response = self.make_request("PUT", f"/kf-account/{open_kfid}", json=data)

        if success:
            self.log("✅ 修改客服账号成功")
            self.add_result("修改客服账号", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 修改客服账号失败: {error}")
            self.add_result("修改客服账号", False, error)

    def test_delete_kf_account(self):
        """测试删除客服账号"""
        self.log("测试删除客服账号...")

        # 使用测试的客服ID
        open_kfid = "kf001@abc"
        success, response = self.make_request("DELETE", f"/kf-account/{open_kfid}")

        if success:
            self.log("✅ 删除客服账号成功")
            self.add_result("删除客服账号", True)
        else:
            error = response.get("detail", "未知错误")
            self.log(f"❌ 删除客服账号失败: {error}")
            self.add_result("删除客服账号", False, error)

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

        success, response = self.make_request("POST", "/tenant/", json=data)

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

        success, response = self.make_request("GET", "/tenant/")

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

        success, response = self.make_request("GET", f"/tenant/{self.corp_id}")

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

        success, response = self.make_request("PUT", f"/tenant/{self.corp_id}", json=data)

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

        success, response = self.make_request("PUT", f"/tenant/{self.corp_id}/permanent-code", json=data)

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
        success, response = self.make_request("PUT", f"/tenant/{self.corp_id}/status", json=data)

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
        success, response = self.make_request("DELETE", f"/tenant/{test_corp_id}")

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
    """运行所有测试"""
    print("\n" + "="*80)
    print(" " * 25 + "完整 API 端点测试套件")
    print(" " * 30 + f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80 + "\n")

    # 测试结果汇总
    all_results = []

    # 定义所有测试类
    test_classes = [
        ("租户管理API", TenantAPITest),
        ("客服账号管理API", KfAccountAPITest),
        ("消息API", MessageAPITest),
        ("素材管理API", MediaAPITest),
        ("联系人管理API", ContactAPITest),
        ("回调API", CallbackAPITest)
    ]

    # 运行所有测试
    for module_name, test_class in test_classes:
        print(f"\n开始运行{module_name}测试...")
        test_instance = test_class()
        success = test_instance.run_all_tests()
        all_results.append((module_name, success))

    # 打印总体结果
    print("\n" + "="*80)
    print("总体测试结果")
    print("="*80)

    total_modules = len(all_results)
    passed_modules = sum(1 for _, success in all_results if success)

    print("\n模块测试结果:")
    for module_name, success in all_results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  - {module_name}: {status}")

    print(f"\n总计: {passed_modules}/{total_modules} 个模块测试通过")

    # 统计总的端点测试数
    total_endpoints = 0
    passed_endpoints = 0
    for module_name, _ in test_classes:
        test_instance = test_classes[[x[0] for x in test_classes].index(module_name)][1]()
        total_endpoints += len(test_instance.results)
        passed_endpoints += sum(1 for _, success, _ in test_instance.results if success)

    print(f"\n端点测试统计: {passed_endpoints}/{total_endpoints} 个端点测试通过")

    if passed_modules == total_modules:
        print("\n🎉 所有模块测试通过！")
        exit_code = 0
    else:
        print(f"\n⚠️ {total_modules - passed_modules} 个模块测试失败")
        print("\n💡 提示：")
        print("  - 某些测试失败可能是由于配置、权限或依赖服务的限制")
        print("  - 请检查 .env 配置文件中的设置")
        print("  - 确保相关服务（如微信API）可访问")
        exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()