# -*- coding: utf-8 -*-
"""简单的数据库初始化脚本"""

import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['PYTHONPATH'] = str(project_root)


def main():
    """初始化数据库"""
    print("="*60)
    print("数据库初始化")
    print("="*60)

    try:
        # 1. 加载配置
        print("\n1. 加载配置...")
        from core.config import WxKfSaasConfig
        config = WxKfSaasConfig()
        print("   ✅ 配置加载成功")

        # 2. 导入并初始化数据库
        print("\n2. 检查数据库状态...")
        from core.database import DatabaseManager

        # 创建数据库管理器
        db_manager = DatabaseManager(config)

        # 检查表是否已存在
        engine = db_manager.sync_engine
        with engine.connect() as conn:
            result = conn.execute("SHOW TABLES")
            existing_tables = [row[0] for row in result]

        # 检查关键表是否存在
        key_tables = ['tenants']
        if all(table in existing_tables for table in key_tables):
            print("   ✅ 数据库已经初始化，跳过创建表")
        else:
            print("   📝 数据库未初始化，开始创建表...")
            db_manager.init_sync()
            print("   ✅ 数据库表结构创建成功")

        # 3. 测试连接
        print("\n3. 测试数据库连接...")
        engine = db_manager.sync_engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            assert result.fetchone()[0] == 1
        print("   ✅ 数据库连接正常")

        # 4. 检查表
        print("\n4. 检查数据表...")
        with engine.connect() as conn:
            result = conn.execute("SHOW TABLES")
            tables = [row[0] for row in result]
            print(f"   已创建的表: {', '.join(tables)}")

        print("\n✅ 数据库初始化完成！")
        print("\n现在可以运行其他测试了：")
        print("  python test_scripts/quick_test.py")

    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()