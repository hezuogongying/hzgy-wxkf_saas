# wxkf_saas 测试套件使用说明

## 🚀 快速开始

### 基本命令

```bash
# 运行所有测试
python tests/run_tests_simple.py all

# 运行特定测试
python tests/run_tests_simple.py config
python tests/run_tests_simple.py database
python tests/run_tests_simple.py client
python tests/run_tests_simple.py message
```

### 🔧 配置说明

#### 环境要求

1. **Python 版本**: 3.8+ 或更高
2. **依赖包**: 运行 `pip install -r requirements.txt` 安装
3. **环境变量**: 确保 `.env` 文件包含所有必需配置
4. **数据库**: 确保数据库服务运行

#### 🧪 测试覆盖

测试脚本会生成以下报告文件：

- **HTML报告**: `htmlcov/index.html`
- **XML报告**: `junit.xml`
- **JSON报告**: `coverage.json`

## 📋 测试脚本功能

### 测试模块说明

1. **test_config.py**: 配置验证和测试
2. **test_url_building.py**: URL生成逻辑测试
3. **test_async_db.py**: 异步数据库连接测试
4. **test_database.py**: 数据库基本操作测试
5. **test_client_initialization.py**: 客户端初始化测试
6. **test_message.py**: 消息API测试
7. **test_media.py**: 素材API测试
8. **test_full_api_workflow.py**: 完整API工作流测试
9. **test_all.py**: 完整集成测试

### 使用方法

1. **单独运行**: 直接指定测试模块
2. **批量运行**: 运行所有测试
3. **指定文件**: 只运行指定测试文件

## 🎯 状态检查

运行测试脚本前，请确保：

1. ✅ Python 环境已配置（Python 3.8+）
2. ✅ 依赖包已安装（pytest, pytest-asyncio, mock等）
3. ✅ `.env` 文件已配置且包含所有必需字段
4. ✅ 数据库服务可访问（MySQL/PostgreSQL/SQLite）
5. ✅ Redis 服务可连接（如果使用）

## 📊 测试报告

测试完成后会生成详细的测试报告，包含：

- 📊 测试覆盖率统计
- 🔧 性能指标分析
- 📝 失败信息详情
- 📈 成功/失败统计
- 🔢 测试用例和回归测试

## 🚀 开始测试

运行以下命令开始完整测试：

```bash
# 快速配置验证测试
python tests/run_tests_simple.py config

# 数据库连接测试
python tests/run_tests_simple.py database

# 客服账号管理测试
python tests/run_tests_simple.py client

# 消息发送测试
python tests/run_tests_simple.py message

# 素材上传测试
python tests/run_tests_simple.py media

# 完整API工作流测试
python tests/run_tests_simple.py integration
```

## 🎯 问题排查

如果遇到问题，请按以下顺序检查：

1. **Python 环境**: `python --version`
2. **依赖检查**: `pip list` 或 `pip freeze`
3. **配置验证**: 运行 `python -c "from wxkf_saas.core.config import WxKfSaasConfig; config.validate_config()"`
4. **数据库连接**: 运行特定测试验证数据库连接
5. **日志查看**: 检查测试输出和错误日志

## 📝 部署前检查

在生产环境部署前，请确认：

1. ✅ **Python 版本**: 3.8+ 或更高
2. ✅ **服务器资源**: CPU、内存、存储配置充足
3. ✅ **数据库**: 确保MySQL 8.0+，字符集utf8mb4
4. ✅ **Redis**: 6.0+，连接配置正确
5. ✅ **SSL证书**: HTTPS证书和私钥已配置（如果需要）
6. ✅ **环境变量**: 所有必需配置已设置
7. ✅ **测试文件**: 创建测试数据库并验证

---

**🎉 所有测试准备就绪，可以开始进行完整的测试验证！**