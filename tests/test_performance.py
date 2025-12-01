# -*- coding: utf-8 -*-
"""性能测试"""

import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import AsyncMock
import statistics


@pytest.mark.asyncio
async def test_database_performance(test_database):
    """测试数据库性能"""
    from wxkf_saas.models.tenant import Tenant

    async with test_database['async_session']() as session:
        # 测试批量插入性能
        start_time = time.time()

        tenants = [
            Tenant(corp_id=f"perf_corp_{str(i).zfill(4)}", corp_name=f"性能测试企业{i}")
                 for i in range(1000))
        ]

        session.add_all(tenants)
        await session.commit()

        batch_time = time.time() - start_time

        assert batch_time < 10.0  # 1000条记录应在10秒内完成

        # 测试查询性能
        start_time = time.time()
        result = await session.execute("SELECT COUNT(*) FROM tenants")
        query_time = time.time() - start_time

        assert query_time < 1.0  # 查询应在1秒内完成
        assert result.scalar() == 1000


@pytest.mark.asyncio
async def test_concurrent_requests(test_config):
    """测试并发请求性能"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    async def single_request():
        with client._http_client.get('https://httpbin.org/get') as response:
            return await response.json()

    # 测试100个并发请求
    start_time = time.time()
    tasks = [single_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)

    end_time = time.time()
    total_time = end_time - start_time

    # 验证所有请求都成功
    successful_requests = [r for r in results if r is not None and r.get('status') == 200]
    assert len(successful_requests) >= 90  # 至少90%成功率


@pytest.mark.asyncio
async def test_memory_usage(test_database):
    """测试内存使用"""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    async with test_database['async_session']() as session:
        # 创建大量对象
        tenants = []
        for i in range(10000):
            tenant = Tenant(
                corp_id=f"mem_test_{str(i)}",
                corp_name=f"内存测试企业{i}"
            )
            tenants.append(tenant)

        session.add_all(tenants)
        await session.commit()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 验证内存使用合理 (不超过100MB增长)
        assert memory_increase < 100 * 1024 * 1024  # 100MB


def test_connection_pool_efficiency():
    """测试连接池效率"""
    from wxkf_saas.core.database import DatabaseManager

    db_manager = DatabaseManager(test_config)

    # 测试连接池重用
    start_time = time.time()
    connections = []

    for i in range(100):
        async with db_manager.async_engine.begin() as conn:
            result = await conn.execute("SELECT 1")
            connections.append(conn)

    total_time = time.time() - start_time

    # 验证连接池效率
    assert total_time < 5.0  # 100次连接应在5秒内完成
    assert len(set(connections)) == 1  # 连接应被重用


@pytest.mark.asyncio
async def test_api_response_time():
    """测试API响应时间"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # 模拟快速响应
    async def mock_fast_response():
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.elapsed = 0.1  # 100ms

            def json(self):
                return {"status": "ok", "time": self.elapsed}

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc_val, tb):
                return self

        client._http_client.get = AsyncMock(return_value=mock_fast_response())

    # 测试响应时间
    start_time = time.time()
    result = await client.message.send_text(
        corp_id="test_corp",
        touser="test_user",
        content="测试消息"
    )
    end_time = time.time()

    response_time = end_time - start_time
    assert response_time < 1.0  # API响应应在1秒内
    assert result.errcode == 0


def test_performance_metrics():
    """测试性能指标收集"""
    # 模拟性能指标
    response_times = [0.1, 0.15, 0.2, 0.12, 0.18, 0.25, 0.3, 0.1]

    # 计算性能指标
    avg_response_time = statistics.mean(response_times)
    p95_response_time = statistics.quantiles(response_times, n=20)[4] * 100
    p99_response_time = statistics.quantiles(response_times, n=10)[9] * 100

    assert avg_response_time < 0.5  # 平均响应时间应小于500ms
    assert p95_response_time < 300  # 95%响应时间应小于300ms
    assert p99_response_time < 500  # 99%响应时间应小于500ms


@pytest.mark.asyncio
async def test_load_capacity():
    """测试负载能力"""
    from wxkf_saas.core.client import WxKfSaasClient

    client = WxKfSaasClient(test_config)

    # 测试不同负载级别
    async def test_load_level(load_count):
        start_time = time.time()
        tasks = []
        for i in range(load_count):
            task = client.message.send_text(
                corp_id="load_test_corp",
                touser=f"load_user_{str(i)}",
                content=f"负载测试消息 {str(i)}"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # 成功请求计数
        successful_count = sum(1 for r in results if not isinstance(r, Exception) and r.errcode == 0)
        success_rate = (successful_count / load_count) * 100

        # 验证负载处理能力
        if load_count == 10:
            assert total_time < 2.0  # 10个请求应在2秒内完成
            assert success_rate >= 90  # 成功率应不低于90%

        if load_count == 50:
            assert total_time < 10.0  # 50个请求应在10秒内完成
            assert success_rate >= 80  # 成功率应不低于80%

        if load_count == 100:
            assert total_time < 20.0  # 100个请求应在20秒内完成
            assert success_rate >= 70  # 成功率应不低于70%

    # 测试不同负载级别
    await test_load_level(10)   # 轻负载
    await test_load_level(50)   # 中等负载
    # await test_load_level(100)  # 重负载 - 可选，避免太长时间