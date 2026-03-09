"""指标采集器模块

提供抽象的指标采集接口，支持 Mock 数据和真实数据采集。
"""

import random
import time
from abc import ABC, abstractmethod
from typing import Any

import aiohttp

from ..config import ConfigManager
from .exceptions import BigDataAPIError
from .types import ComponentMetrics


class BaseMetricsCollector(ABC):
    """指标采集器抽象基类。"""

    @abstractmethod
    async def collect(self, component: str) -> ComponentMetrics:
        """
        采集指定组件的指标数据。

        Args:
            component: 组件名称

        Returns:
            组件指标数据对象
        """
        pass


class MockMetricsCollector(BaseMetricsCollector):
    """Mock 指标采集器，用于测试环境。"""

    # 各组件的 Mock 数据模板
    MOCK_DATA: dict[str, dict[str, Any]] = {
        "spark": {
            "workers": 10,
            "active_workers": 8,
            "cores": 80,
            "memory": 320,
            "running_apps": 5,
            "completed_apps": 150,
            "pending_apps": 2,
            "failed_apps": 3,
        },
        "hadoop": {
            "nodes_total": 20,
            "nodes_active": 18,
            "memory_used": 1024,
            "memory_total": 2048,
            "vcores_used": 120,
            "vcores_total": 200,
            "running_containers": 45,
            "pending_containers": 10,
        },
        "flink": {
            "taskmanagers": 5,
            "slots_available": 40,
            "slots_total": 50,
            "jobs_running": 8,
            "jobs_finished": 200,
            "jobs_failed": 5,
            "jobs_cancelled": 10,
        },
        "kafka": {
            "brokers_count": 3,
            "topics_count": 50,
            "partitions_total": 200,
            "under_replicated": 2,
            "offline_partitions": 0,
            "messages_per_sec": 15000,
            "bytes_per_sec": 52428800,
        },
        "hdfs": {
            "files_total": 1000000,
            "blocks_total": 500000,
            "capacity": 102400,
            "used": 61440,
            "free": 40960,
            "under_replicated_blocks": 5,
            "corrupt_blocks": 0,
        },
        "yarn": {
            "apps_running": 15,
            "apps_pending": 3,
            "apps_completed": 500,
            "apps_failed": 8,
            "containers_running": 120,
            "containers_pending": 5,
            "memory_allocated": 512,
            "memory_available": 256,
        },
        "hive": {
            "databases": 10,
            "tables": 200,
            "partitions": 5000,
            "active_sessions": 5,
            "queries_running": 3,
            "queries_completed": 1000,
        },
        "clickhouse": {
            "databases": 5,
            "tables": 50,
            "rows_total": 1000000000,
            "queries_per_sec": 500,
            "memory_used": 8192,
            "memory_total": 16384,
        },
    }

    async def collect(self, component: str) -> ComponentMetrics:
        """采集 Mock 数据。"""
        component_lower = component.lower()

        if component_lower not in self.MOCK_DATA:
            raise BigDataAPIError(f"不支持的组件类型：{component}")

        # 复制基础数据
        base_data = self.MOCK_DATA[component_lower].copy()

        # 添加随机波动，模拟真实数据
        metrics = {}
        for key, value in base_data.items():
            if isinstance(value, int):
                # 添加 ±10% 的随机波动
                fluctuation = random.uniform(-0.1, 0.1)
                new_value = int(value * (1 + fluctuation))
                metrics[key] = max(0, new_value)
            elif isinstance(value, float):
                fluctuation = random.uniform(-0.1, 0.1)
                metrics[key] = value * (1 + fluctuation)
            else:
                metrics[key] = value

        # 计算健康状态
        health = self._calculate_health(component_lower, metrics)

        return ComponentMetrics(
            component=component.upper(),
            health=health,
            metrics=metrics,
            timestamp=time.time(),
        )

    def _calculate_health(self, component: str, metrics: dict[str, Any]) -> str:
        """根据指标计算健康状态。"""
        # 通用健康检查
        if component == "spark":
            if metrics["active_workers"] < metrics["workers"] * 0.5:
                return "unhealthy"
            if metrics["failed_apps"] > 10:
                return "warning"
        elif component == "hadoop":
            if metrics["nodes_active"] < metrics["nodes_total"] * 0.5:
                return "unhealthy"
        elif component == "flink":
            if metrics["jobs_failed"] > 10:
                return "warning"
        elif component == "kafka":
            if metrics["offline_partitions"] > 0:
                return "unhealthy"
            if metrics["under_replicated"] > 5:
                return "warning"
        elif component == "hdfs":
            if metrics["corrupt_blocks"] > 0:
                return "unhealthy"
            if metrics["under_replicated_blocks"] > 10:
                return "warning"

        return "healthy"


class RealMetricsCollector(BaseMetricsCollector):
    """真实指标采集器，从实际 API 获取数据。"""

    def __init__(self, config_manager: ConfigManager, session: aiohttp.ClientSession) -> None:
        """
        初始化真实采集器。

        Args:
            config_manager: 配置管理器
            session: HTTP 会话
        """
        self.config_manager = config_manager
        self.session = session

    async def collect(self, component: str) -> ComponentMetrics:
        """从真实 API 采集数据。"""
        component_lower = component.lower()

        # 获取组件特定的端点配置
        component_endpoints = self.config_manager.get_component_endpoints()
        endpoint = component_endpoints.get(component_lower)

        if not endpoint:
            # 使用默认端点
            endpoint = self.config_manager.get_api_endpoint()

        if not endpoint:
            raise BigDataAPIError(f"未配置组件 {component} 的 API 端点")

        # 根据组件类型调用不同的 API
        metrics = await self._fetch_component_metrics(component_lower, endpoint)

        return ComponentMetrics(
            component=component.upper(),
            health=metrics.get("health", "unknown"),
            metrics=metrics,
            timestamp=time.time(),
        )

    async def _fetch_component_metrics(
        self, component: str, endpoint: str
    ) -> dict[str, Any]:
        """从 API 获取组件指标。"""
        # 各组件的 API 路径映射
        api_paths = {
            "spark": "/json/",
            "hadoop": "/ws/v1/cluster/metrics",
            "flink": "/overview",
            "kafka": "/brokers",
            "hdfs": "/jmx?qry=Hadoop:service=NameNode,name=NameNodeInfo",
            "yarn": "/ws/v1/cluster/metrics",
        }

        path = api_paths.get(component, "/metrics")
        url = f"{endpoint.rstrip('/')}{path}"

        try:
            timeout = aiohttp.ClientTimeout(total=self.config_manager.get_timeout_seconds())
            async with self.session.get(url, timeout=timeout) as response:
                if response.status != 200:
                    raise BigDataAPIError(f"API 返回错误状态码：{response.status}")

                data = await response.json()
                return self._parse_response(component, data)

        except aiohttp.ClientError as e:
            raise BigDataAPIError(f"请求 API 失败：{str(e)}") from e

    def _parse_response(self, component: str, data: dict[str, Any]) -> dict[str, Any]:
        """解析 API 响应数据。"""
        if component == "spark":
            return {
                "workers": len(data.get("workers", [])),
                "active_workers": sum(
                    1 for w in data.get("workers", []) if w.get("state") == "ALIVE"
                ),
                "cores": sum(w.get("cores", 0) for w in data.get("workers", [])),
                "memory": sum(w.get("memory", 0) for w in data.get("workers", [])),
                "running_apps": len(data.get("activeapps", [])),
                "completed_apps": len(data.get("completedapps", [])),
                "health": "healthy" if data.get("aliveworkers", 0) > 0 else "unhealthy",
            }
        elif component in ("hadoop", "yarn"):
            cluster_metrics = data.get("clusterMetrics", {})
            return {
                "nodes_total": cluster_metrics.get("totalNodes", 0),
                "nodes_active": cluster_metrics.get("activeNodes", 0),
                "memory_used": cluster_metrics.get("allocatedMB", 0),
                "memory_total": cluster_metrics.get("totalMB", 0),
                "vcores_used": cluster_metrics.get("allocatedVirtualCores", 0),
                "vcores_total": cluster_metrics.get("totalVirtualCores", 0),
                "running_containers": cluster_metrics.get("containersRunning", 0),
                "health": "healthy" if cluster_metrics.get("activeNodes", 0) > 0 else "unhealthy",
            }
        elif component == "flink":
            return {
                "taskmanagers": data.get("taskmanagers", 0),
                "slots_available": data.get("slots-available", 0),
                "slots_total": data.get("slots-total", 0),
                "jobs_running": data.get("jobs-running", 0),
                "jobs_finished": data.get("jobs-finished", 0),
                "jobs_failed": data.get("jobs-failed", 0),
                "health": "healthy" if data.get("taskmanagers", 0) > 0 else "unhealthy",
            }
        else:
            # 默认返回原始数据
            return data


class MetricsCollectorFactory:
    """指标采集器工厂类。"""

    @staticmethod
    def create(
        config_manager: ConfigManager,
        session: aiohttp.ClientSession | None = None,
    ) -> BaseMetricsCollector:
        """
        根据配置创建采集器实例。

        Args:
            config_manager: 配置管理器
            session: HTTP 会话（真实模式需要）

        Returns:
            采集器实例
        """
        if config_manager.is_test_mode():
            return MockMetricsCollector()
        else:
            if session is None:
                session = aiohttp.ClientSession()
            return RealMetricsCollector(config_manager, session)
