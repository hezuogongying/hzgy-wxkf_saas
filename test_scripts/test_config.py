# -*- coding: utf-8 -*-
"""配置验证测试脚本"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.config import WxKfSaasConfig


def main():
    """测试配置加载和验证"""
    print("\n" + "="*60)
    print("配置验证测试")
    print("="*60)

    try:
        # 1. 尝试加载配置
        print("\n[1/3] 加载配置...")
        config = WxKfSaasConfig()
        print("✅ 配置加载成功")

        # 2. 验证配置完整性
        print("\n[2/3] 验证配置完整性...")
        config.validate_config()
        print("✅ 配置验证通过")

        # 3. 显示关键配置项
        print("\n[3/3] 关键配置项:")
        print(f"   运行模式: {config.mode}")
        print(f"   数据库 URL: {config.database_url[:50]}...")
        print(f"   Redis URL: {config.redis_url}")
        print(f"   服务端口: {config.fastapi_port}")
        print(f"   服务器 URL: {config.server_url or '未配置'}")

        if config.mode == "single":
            print(f"   企业 ID: {config.corp_id}")

        print("\n✅ 所有测试通过！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "="*60)


if __name__ == "__main__":
    main()