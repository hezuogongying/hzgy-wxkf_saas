# -*- coding: utf-8 -*-
"""快速健康检查脚本"""

import sys
import json
import requests
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def test_config():
    """测试配置"""
    print("\n[配置测试]")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()
        print(f"✅ 配置加载成功")
        print(f"   运行模式: {config.mode}")
        print(f"   服务端口: {config.fastapi_port}")
        return True
    except Exception as e:
        print(f"❌ 配置失败: {e}")
        return False


def test_database():
    """测试数据库"""
    print("\n[数据库测试]")
    try:
        from core.database import get_db_manager
        db_manager = get_db_manager()
        engine = db_manager.sync_engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ 数据库连接正常")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def test_api():
    """测试 API 服务"""
    print("\n[API 服务测试]")
    try:
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()

        # 尝试访问健康检查接口
        url = f"http://localhost:{config.fastapi_port}/health"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            data = response.json()
            print(f"✅ API 服务正常 - 状态: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ API 服务响应异常: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠️ API 服务未运行")
        return False
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False


def main():
    """运行快速测试"""
    print("="*50)
    print("微信客服 SaaS 快速健康检查")
    print("="*50)

    # 运行测试
    tests = [
        ("配置", test_config),
        ("数据库", test_database),
        ("API", test_api),
    ]

    results = []
    for name, test in tests:
        try:
            result = test()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name}测试异常: {e}")
            results.append((name, False))

    # 汇总结果
    print("\n" + "="*50)
    print("测试结果汇总:")
    print("-"*50)

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")

    total = len(results)
    passed = sum(1 for _, r in results if r)

    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有检查通过！")
    else:
        print("⚠️ 部分检查失败，请查看详情")

    print("="*50)


if __name__ == "__main__":
    main()