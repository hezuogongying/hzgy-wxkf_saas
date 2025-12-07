# -*- coding: utf-8 -*-
"""数据库初始化脚本"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")

    try:
        # 导入数据库管理器
        from core.database import DatabaseManager, get_db_manager
        from core.config import WxKfSaasConfig

        # 加载配置
        config = WxKfSaasConfig()

        # 创建并初始化数据库管理器
        print("1. 创建数据库管理器...")
        db_manager = DatabaseManager(config)
        print("   ✅ 数据库管理器创建成功")

        # 初始化数据库
        print("2. 创建数据库表结构...")
        db_manager.init_sync()
        print("   ✅ 数据库表结构创建成功")

        # 测试连接
        print("3. 测试数据库连接...")
        engine = db_manager.sync_engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1 as test")
            assert result.fetchone()[0] == 1
        print("   ✅ 数据库连接测试成功")

        # 检查表
        print("4. 检查数据表...")
        with engine.connect() as conn:
            result = conn.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            print(f"   已创建的表: {', '.join(tables)}")

        print("\n✅ 数据库初始化完成！")
        return True

    except Exception as e:
        print(f"\n❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("数据库初始化脚本")
    print("="*60)

    success = init_database()

    if success:
        print("\n🎉 数据库初始化成功！")
        print("\n现在可以运行其他测试：")
        print("  python test_scripts/quick_test.py")
        print("  python test_scripts/test_app_startup.py")
    else:
        print("\n⚠️ 请检查配置并重试")
        sys.exit(1)


if __name__ == "__main__":
    main()