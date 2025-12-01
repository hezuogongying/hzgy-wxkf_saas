# -*- coding: utf-8 -*-
"""测试URL构建逻辑"""

import sys
from pathlib import Path
from urllib.parse import quote_plus

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

def build_url_test(db_type, driver, db_user, db_password, db_host, db_port, db_name, db_path=None):
    """测试URL构建"""
    print(f"\n测试: {db_type} + {driver}")

    if db_type == "sqlite":
        print(f"   SQLite URL: sqlite+{driver}:///{db_path}")
        return f"sqlite+{driver}:///{db_path}"

    # MySQL/PostgreSQL
    username = quote_plus(db_user or "")
    password = quote_plus(db_password or "")

    base_url = f"{db_type}+{driver}://{username}:{password}@{db_host}:{db_port}/{db_name}"

    params = []
    if db_type == "mysql":
        params.append("charset=utf8mb4")

    if params:
        base_url += "?" + "&".join(params)

    print(f"   URL: {base_url}")
    return base_url

def test_mysql():
    """测试MySQL URL构建"""
    print("🔗 MySQL URL测试:")

    # 同步
    build_url_test(
        db_type="mysql",
        driver="pymysql",
        db_user="testuser",
        db_password="testpass",
        db_host="localhost",
        db_port=3306,
        db_name="wxkf_saas"
    )

    # 异步
    build_url_test(
        db_type="mysql",
        driver="aiomysql",
        db_user="testuser",
        db_password="testpass",
        db_host="localhost",
        db_port=3306,
        db_name="wxkf_saas"
    )

def test_postgresql():
    """测试PostgreSQL URL构建"""
    print("\n🐘 PostgreSQL URL测试:")

    # 同步
    build_url_test(
        db_type="postgresql",
        driver="psycopg2",
        db_user="postgres",
        db_password="postgres",
        db_host="localhost",
        db_port=5432,
        db_name="wxkf_saas"
    )

    # 异步
    build_url_test(
        db_type="postgresql",
        driver="asyncpg",
        db_user="postgres",
        db_password="postgres",
        db_host="localhost",
        db_port=5432,
        db_name="wxkf_saas"
    )

def test_sqlite():
    """测试SQLite URL构建"""
    print("\n🗄️ SQLite URL测试:")

    # 同步
    build_url_test(
        db_type="sqlite",
        driver="sqlite",
        db_user="",
        db_password="",
        db_host="",
        db_port="",
        db_name="",
        db_path="./data/app.db"
    )

    # 异步
    build_url_test(
        db_type="sqlite",
        driver="aiosqlite",
        db_user="",
        db_password="",
        db_host="",
        db_port="",
        db_name="",
        db_path="./data/app.db"
    )

def test_special_characters():
    """测试特殊字符URL编码"""
    print("\n🔒 特殊字符URL编码测试:")

    special_cases = [
        ("user@domain.com", "p@ss", "特殊字符用户名"),
        ("normal", "p@ssw0rd!", "特殊字符密码"),
        ("中文用户", "中文密码", "中文字符"),
    ]

    for user, password, desc in special_cases:
        print(f"\n   {desc}:")
        username_encoded = quote_plus(user)
        password_encoded = quote_plus(password)
        url = f"mysql+pymysql://{username_encoded}:{password_encoded}@localhost:3306/test"
        print(f"     原始: {user}:{password}")
        print(f"     编码: {username_encoded}:{password_encoded}")
        print(f"     URL: {url}")

if __name__ == "__main__":
    test_mysql()
    test_postgresql()
    test_sqlite()
    test_special_characters()

    print("\n✅ URL构建测试完成")

    print("\n💡 配置建议:")
    print("1. 使用 DATABASE_URL 环境变量（推荐用于生产）")
    print("2. 直接配置完整URL，避免参数化配置的复杂性")
    print("3. 特殊字符（如@、:、#等）会被自动编码")
    print("4. 不同数据库类型需要不同的驱动：")
    print("   - MySQL: pymysql (同步) / aiomysql (异步)")
    print("   - PostgreSQL: psycopg2 (同步) / asyncpg (异步)")
    print("   - SQLite: sqlite (同步) / aiosqlite (异步)")
    print("5. 连接池配置对所有数据库类型通用")