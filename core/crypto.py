# -*- coding: utf-8 -*-
"""微信消息加密解密工具"""

import base64
import hashlib
import random
import struct
import time
from xml.etree import ElementTree
from typing import Tuple, Optional
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import logging
import xml.etree.ElementTree as ET


class WxKfCrypto:
    """微信企业消息加密解密工具类"""

    def __init__(self, token: str, encoding_aes_key: str, corp_id: Optional[str] = None):
        """
        初始化加密工具

        Args:
            token: 用于验证的token
            encoding_aes_key: 消息加密密钥
            corp_id: 企业ID，用于解密验证
        """
        self.token = token
        self.encoding_aes_key = encoding_aes_key + "="  # 补全base64长度

        # 处理AES密钥
        try:
            self.aes_key = base64.b64decode(self.encoding_aes_key)
        except Exception as e:
            # 如果解码失败，尝试使用原始字符串
            self.aes_key = encoding_aes_key.encode('utf-8')

        self.corp_id = corp_id

        # AES密钥长度应该是32字节
        if len(self.aes_key) > 32:
            self.aes_key = self.aes_key[:32]
        elif len(self.aes_key) < 32:
            # 如果密钥太短，进行填充（仅用于测试）
            self.aes_key = self.aes_key.ljust(32, b'\0')

        if len(self.aes_key) != 32:
            logging.warning(f"AES密钥长度异常: {len(self.aes_key)}, 可能导致解密失败")

    def get_sha1(self, token: str, timestamp: str, nonce: str, encrypt_msg: str) -> str:
        """计算SHA1签名"""
        sortlist = [token, timestamp, nonce, encrypt_msg]
        sortlist.sort()
        strtemp = ''.join(sortlist)
        sha1obj = hashlib.sha1(strtemp.encode('utf-8'))
        signature = sha1obj.hexdigest()
        return signature

    def check_signature(self, msg_signature: str, timestamp: str, nonce: str, echostr: str) -> bool:
        """验证回调URL签名"""
        if not msg_signature or not timestamp or not nonce or not echostr:
            return False

        signature = self.get_sha1(self.token, timestamp, nonce, echostr)
        return signature == msg_signature

    def decrypt_msg(self, encrypted_msg: str, msg_signature: str, timestamp: str, nonce: str) -> Tuple[str, int]:
        """
        解密消息

        Args:
            encrypted_msg: 加密的消息内容
            msg_signature: 消息签名
            timestamp: 时间戳
            nonce: 随机字符串

        Returns:
            (解密后的消息, msgid)

        Raises:
            ValueError: 签名验证失败或解密失败
        """
        # 验证签名
        signature = self.get_sha1(self.token, timestamp, nonce, encrypted_msg)
        if signature != msg_signature:
            raise ValueError("签名验证失败")

        # Base64解码
        encrypted_data = base64.b64decode(encrypted_msg)

        # AES解密
        try:
            cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        except Exception as e:
            raise ValueError(f"AES解密失败: {str(e)}")

        # 解析消息格式
        try:
            # 解包：前16字节是随机字符串，接着4字节是msg长度，接着是msg，最后是corp_id
            msg_len = struct.unpack_from('>I', decrypted_data[16:20])[0]
            msg = decrypted_data[20:20+msg_len].decode('utf-8')
            received_corp_id = decrypted_data[20+msg_len:].decode('utf-8')

            # 验证corp_id（如果设置了的话）
            if self.corp_id and received_corp_id != self.corp_id:
                logging.warning(f"Corp ID不匹配: 期望{self.corp_id}, 收到{received_corp_id}")

            # 解析XML获取msgid
            try:
                root = ET.fromstring(msg)
                msgid = root.find('MsgId')
                msgid = int(msgid.text) if msgid is not None else 0
            except:
                msgid = 0

            return msg, msgid

        except Exception as e:
            raise ValueError(f"消息解析失败: {str(e)}")

    def encrypt_msg(self, msg: str, nonce: str = None) -> Tuple[str, str, str]:
        """
        加密消息

        Args:
            msg: 要加密的消息内容
            nonce: 随机字符串，如果为None则自动生成

        Returns:
            (加密后的消息, 时间戳, 随机字符串)
        """
        if nonce is None:
            nonce = ''.join([str(random.randint(0, 9)) for i in range(16)])

        timestamp = str(int(time.time()))

        # 生成16位随机字符串
        random_str = ''.join([str(random.randint(0, 9)) for i in range(16)])
        random_bytes = random_str.encode('utf-8')

        # 消息长度和内容
        msg_bytes = msg.encode('utf-8')
        msg_len = struct.pack('>I', len(msg_bytes))

        # corp_id（如果没有设置则使用默认值）
        corp_id_bytes = (self.corp_id or '').encode('utf-8')

        # 拼接数据：随机字符串 + 消息长度 + 消息内容 + corp_id
        data_to_encrypt = random_bytes + msg_len + msg_bytes + corp_id_bytes

        # AES加密
        try:
            # 填充到16字节的倍数
            padded_data = pad(data_to_encrypt, AES.block_size)
            cipher = AES.new(self.aes_key, AES.MODE_CBC, self.aes_key[:16])
            encrypted_data = cipher.encrypt(padded_data)
        except Exception as e:
            raise ValueError(f"AES加密失败: {str(e)}")

        # Base64编码
        encrypted_msg = base64.b64encode(encrypted_data).decode('utf-8')

        # 生成签名
        signature = self.get_sha1(self.token, timestamp, nonce, encrypted_msg)

        return encrypted_msg, timestamp, nonce

    def extract_xml_field(self, xml_str: str, field_name: str) -> Optional[str]:
        """从XML中提取指定字段的值"""
        try:
            root = ET.fromstring(xml_str)
            element = root.find(field_name)
            return element.text if element is not None else None
        except Exception as e:
            logging.error(f"解析XML失败: {str(e)}")
            return None

    def xml_to_dict(self, xml_str: str) -> dict:
        """将XML转换为字典"""
        try:
            root = ET.fromstring(xml_str)
            result = {}
            for child in root:
                result[child.tag] = child.text
            return result
        except Exception as e:
            logging.error(f"XML转换字典失败: {str(e)}")
            return {}

    def dict_to_xml(self, data: dict, root_tag: str = 'xml') -> str:
        """将字典转换为XML"""
        try:
            root = ET.Element(root_tag)
            for key, value in data.items():
                child = ET.SubElement(root, key)
                child.text = str(value)
            return ET.tostring(root, encoding='utf-8', method='xml').decode('utf-8')
        except Exception as e:
            logging.error(f"字典转换XML失败: {str(e)}")
            return f"<{root_tag}></{root_tag}>"