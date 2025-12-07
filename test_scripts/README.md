# 微信客服 SaaS API 测试套件

## 概述

本目录包含完整的项目测试套件，用于验证微信客服 SaaS 平台的所有 API 端点功能。

## 测试脚本列表

### 基础测试脚本

1. **test_config.py** - 配置验证测试
   - 验证环境变量和配置文件
   - 检查数据库连接

2. **test_app_startup.py** - 应用启动测试
   - 测试 FastAPI 应用启动
   - 验证路由注册

3. **quick_test.py** - 快速检查测试
   - 快速验证系统基本功能
   - 适合开发阶段的快速检查

4. **init_database.py** / **init_db_simple.py** - 数据库初始化
   - 创建数据库表结构
   - 插入初始数据

### API 端点测试脚本

5. **test_api_endpoints.py** - 基础 API 测试
   - 测试健康检查、API 文档
   - 测试基本的租户和客服账号功能
   - **覆盖约 12.5% 的 API 端点**

6. **test_message_api.py** - 消息 API 测试
   - 测试基本消息发送功能
   - 验证消息同步

7. **test_complete_api.py** - 完整 API 测试套件 ⭐
   - **覆盖所有 40+ 个 API 端点**
   - 包含以下模块：
     - 租户管理 API (7个端点)
     - 客服账号管理 API (6个端点)
     - 消息 API (11个端点)
     - 素材管理 API (3个端点)
     - 联系人管理 API (3个端点)
     - 回调 API (7个端点)

8. **test_message_complete_api.py** - 消息完整 API 测试
   - **覆盖 message_complete.py 的 15 个端点**
   - 测试所有消息类型，包括：
     - 基础消息（文本、图片、语音、视频、文件）
     - 特殊消息（位置、小程序、视频号、笔记等）
     - 功能操作（同步、欢迎语、撤回）

### 主运行脚本

9. **run_all_tests.py** - 主测试运行器
   - 按优先级运行所有测试脚本
   - 汇总测试结果
   - 提供清晰的测试报告

## 运行方式

### 运行所有测试
```bash
cd test_scripts
python run_all_tests.py
```

### 运行单个测试
```bash
# 运行快速测试
python quick_test.py

# 运行完整 API 测试
python test_complete_api.py

# 运行消息完整 API 测试
python test_message_complete_api.py
```

### 运行指定模块测试
```bash
# 只运行租户管理 API 测试
python -c "from test_complete_api import TenantAPITest; TenantAPITest().run_all_tests()"

# 只运行消息 API 测试
python -c "from test_complete_api import MessageAPITest; MessageAPITest().run_all_tests()"
```

## 测试覆盖范围

### API 端点覆盖率

| 模块 | 端点数 | 测试文件 | 覆盖状态 |
|------|--------|----------|----------|
| tenant.py | 7 | test_complete_api.py | ✅ 100% |
| kf_account.py | 6 | test_complete_api.py | ✅ 100% |
| message.py | 11 | test_complete_api.py | ✅ 100% |
| message_complete.py | 15 | test_message_complete_api.py | ✅ 100% |
| media.py | 3 | test_complete_api.py | ✅ 100% |
| contact.py | 3 | test_complete_api.py | ✅ 100% |
| callback.py | 7 | test_complete_api.py | ✅ 100% |
| **总计** | **52** | **2个文件** | **✅ 100%** |

## 测试结果示例

```
========================================================
                    完整 API 端点测试套件
                        开始时间: 2024-01-01 12:00:00
========================================================

开始运行租户管理API测试...

================================================================================
租户管理 API 测试
================================================================================

[12:00:01.123] INFO: 测试创建租户...
[12:00:01.456] INFO: POST /tenant/
[12:00:01.789] INFO: 响应状态: 201
[12:00:01.790] INFO: ✅ 创建租户成功
...

================================================================================
总体测试结果
================================================================================

模块测试结果:
  - 租户管理API: ✅ 通过
  - 客服账号管理API: ✅ 通过
  - 消息API: ✅ 通过
  - 素材管理API: ✅ 通过
  - 联系人管理API: ✅ 通过
  - 回调API: ✅ 通过

总计: 6/6 个模块测试通过
端点测试统计: 52/52 个端点测试通过

🎉 所有模块测试通过！
```

## 注意事项

1. **服务状态**：API 测试需要服务运行在 `http://localhost:8083`（或配置的端口）

2. **配置要求**：确保 `.env` 文件包含正确的配置：
   - 数据库连接信息
   - 企业微信 API 凭证
   - 其他必要的环境变量

3. **测试数据**：测试会使用测试数据，不会影响生产环境：
   - 使用 `test_` 前缀的测试 ID
   - 创建的测试数据会在测试后清理

4. **权限要求**：某些测试可能需要：
   - 数据库写入权限
   - 微信 API 访问权限
   - 网络访问权限

5. **失败处理**：
   - 测试失败时会显示详细错误信息
   - 某些测试失败可能是因为外部服务限制
   - 查看日志了解具体原因

## 扩展测试

### 添加新的 API 测试

1. 在相应的测试类中添加测试方法
2. 遵循命名约定 `test_xxx`
3. 使用 `self.make_request()` 发起请求
4. 使用 `self.add_result()` 记录结果

示例：
```python
def test_new_endpoint(self):
    """测试新端点"""
    self.log("测试新端点...")

    data = {"key": "value"}
    success, response = self.make_request("POST", "/new-endpoint", json=data)

    if success:
        self.log("✅ 新端点测试成功")
        self.add_result("新端点测试", True)
    else:
        error = response.get("detail", "未知错误")
        self.log(f"❌ 新端点测试失败: {error}")
        self.add_result("新端点测试", False, error)
```

### 创建新的测试模块

1. 继承 `BaseAPITest` 类
2. 实现 `run_all_tests()` 方法
3. 在 `test_complete_api.py` 的 `main()` 函数中添加

## 性能测试

当前测试套件专注于功能验证，未来可以添加：
- 并发请求测试
- 响应时间测试
- 压力测试
- 负载测试

## 最佳实践

1. **持续集成**：将测试集成到 CI/CD 流程
2. **定期运行**：定期运行完整测试套件
3. **监控结果**：关注测试结果趋势
4. **快速反馈**：失败时立即通知相关人员
5. **文档更新**：API 变更时同步更新测试