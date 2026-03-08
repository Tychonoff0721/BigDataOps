"""服务层模块"""

from typing import Any

import aiohttp

from .exceptions import BigDataAPIError, BigDataRateLimitError


class BaseService:
    """大数据服务基类，提供通用的 HTTP 请求和错误处理逻辑。"""

    def __init__(
        self,
        config_manager: Any,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        """
        初始化基础服务。

        Args:
            config_manager: 配置管理器实例
            session: aiohttp 会话
        """
        self.config_manager = config_manager
        self._session = session

    @property
    def session(self) -> aiohttp.ClientSession:
        """获取或创建 aiohttp 会话。"""
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self) -> None:
        """关闭会话。"""
        if self._session and not self._session.closed:
            await self._session.close()

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        发起 HTTP 请求。

        Args:
            method: HTTP 方法
            url: 请求 URL
            params: 查询参数
            data: 请求体数据
            headers: 请求头

        Returns:
            响应数据字典

        Raises:
            BigDataAPIError: API 请求失败
            BigDataRateLimitError: 触发限流
        """
        max_retries = self.config_manager.get_max_retries()
        timeout_seconds = self.config_manager.get_timeout_seconds()
        
        # 构建请求头
        request_headers = headers or {}
        username = self.config_manager.get_api_username()
        password = self.config_manager.get_api_password()
        
        if username and password:
            import base64
            credentials = f"{username}:{password}"
            encoded = base64.b64encode(credentials.encode()).decode()
            request_headers["Authorization"] = f"Basic {encoded}"
        
        request_headers["Content-Type"] = "application/json"
        request_headers["User-Agent"] = "BigDataOps-Plugin/1.0"

        # 配置代理
        proxy_url = None
        proxy_host = self.config_manager.get_proxy_http()
        proxy_port = self.config_manager.get_port()
        if proxy_host and proxy_port:
            proxy_url = f"{proxy_host}:{proxy_port}"

        timeout = aiohttp.ClientTimeout(total=timeout_seconds)

        for attempt in range(max_retries):
            try:
                async with self.session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    headers=request_headers,
                    proxy=proxy_url,
                    timeout=timeout,
                ) as response:
                    if response.status == 429:
                        raise BigDataRateLimitError("API 请求过于频繁，请稍后再试")
                    
                    response.raise_for_status()
                    result = await response.json()
                    return result
                    
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    raise BigDataAPIError(f"请求失败：{str(e)}") from e
                await asyncio.sleep(2 ** attempt)  # 指数退避
                
        raise BigDataAPIError("请求失败，已达最大重试次数")


class ComponentMetricsService(BaseService):
    """组件指标服务，负责收集和分析大数据组件的各项指标。"""

    async def get_component_metrics(self, component_name: str) -> dict[str, Any]:
        """
        获取指定组件的指标数据。

        Args:
            component_name: 组件名称 (spark, hadoop, flink, kafka 等)

        Returns:
            包含组件指标的字典
        """
        api_endpoint = self.config_manager.get_api_endpoint()
        
        if not api_endpoint:
            raise BigDataAPIError("未配置 API 端点地址")
        
        # 根据组件类型构建不同的 API 请求
        component_handlers = {
            "spark": self._get_spark_metrics,
            "hadoop": self._get_hadoop_metrics,
            "flink": self._get_flink_metrics,
            "kafka": self._get_kafka_metrics,
            "hdfs": self._get_hdfs_metrics,
            "yarn": self._get_yarn_metrics,
        }
        
        handler = component_handlers.get(component_name.lower())
        if not handler:
            raise BigDataAPIError(f"不支持的组件类型：{component_name}")
        
        return await handler(api_endpoint)

    async def _get_spark_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 Spark 组件指标。"""
        # Spark Master UI API: http://master:8080/json/
        url = f"{endpoint}/json/"
        data = await self._request("GET", url)
        
        return {
            "component": "Spark",
            "workers": len(data.get("workers", [])),
            "active_workers": sum(1 for w in data.get("workers", []) if w.get("state") == "ALIVE"),
            "cores": sum(w.get("cores", 0) for w in data.get("workers", [])),
            "memory": sum(w.get("memory", 0) for w in data.get("workers", [])),
            "running_apps": len(data.get("activeapps", [])),
            "completed_apps": len(data.get("completedapps", [])),
            "health": "healthy" if data.get("aliveworkers", 0) > 0 else "unhealthy",
        }

    async def _get_hadoop_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 Hadoop 组件指标。"""
        # YARN ResourceManager API
        url = f"{endpoint}/ws/v1/cluster/metrics"
        data = await self._request("GET", url)
        cluster_metrics = data.get("clusterMetrics", {})
        
        return {
            "component": "Hadoop",
            "nodes_total": cluster_metrics.get("totalNodes", 0),
            "nodes_active": cluster_metrics.get("activeNodes", 0),
            "memory_used": cluster_metrics.get("allocatedMB", 0),
            "memory_total": cluster_metrics.get("totalMB", 0),
            "vcores_used": cluster_metrics.get("allocatedVirtualCores", 0),
            "vcores_total": cluster_metrics.get("totalVirtualCores", 0),
            "running_containers": cluster_metrics.get("containersRunning", 0),
            "health": "healthy" if cluster_metrics.get("activeNodes", 0) > 0 else "unhealthy",
        }

    async def _get_flink_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 Flink 组件指标。"""
        # Flink JobManager API
        url = f"{endpoint}/overview"
        data = await self._request("GET", url)
        
        return {
            "component": "Flink",
            "jobmanagers": data.get("taskmanagers", 0),
            "slots_available": data.get("slots-available", 0),
            "slots_total": data.get("slots-total", 0),
            "jobs_running": data.get("jobs-running", 0),
            "jobs_finished": data.get("jobs-finished", 0),
            "jobs_failed": data.get("jobs-failed", 0),
            "health": "healthy" if data.get("taskmanagers", 0) > 0 else "unhealthy",
        }

    async def _get_kafka_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 Kafka 组件指标。"""
        # 需要通过 JMX 或 Kafka REST API 获取
        url = f"{endpoint}/brokers"
        try:
            data = await self._request("GET", url)
            brokers = data if isinstance(data, list) else []
        except BigDataAPIError:
            # 如果直接获取失败，尝试其他端点
            brokers = []
        
        return {
            "component": "Kafka",
            "brokers_count": len(brokers),
            "topics_count": 0,  # 需要额外 API 调用
            "partitions_total": 0,
            "under_replicated": 0,
            "offline_partitions": 0,
            "health": "unknown" if len(brokers) == 0 else "healthy",
        }

    async def _get_hdfs_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 HDFS 组件指标。"""
        url = f"{endpoint}/webhdfs/v1/?op=GETHOMEDIRECTORY"
        try:
            await self._request("GET", url)
            # NameNode WebHDFS API
            nn_url = f"{endpoint}/jmx?qry=Hadoop:service=NameNode,name=NameNodeInfo"
            data = await self._request("GET", nn_url)
            beans = data.get("beans", [{}])[0]
            
            return {
                "component": "HDFS",
                "files_total": beans.get("TotalFiles", 0),
                "blocks_total": beans.get("TotalBlocks", 0),
                "capacity": beans.get("Capacity", 0),
                "used": beans.get("Used", 0),
                "free": beans.get("Free", 0),
                "health": "healthy",
            }
        except BigDataAPIError:
            return {
                "component": "HDFS",
                "files_total": 0,
                "blocks_total": 0,
                "capacity": 0,
                "used": 0,
                "free": 0,
                "health": "unhealthy",
            }

    async def _get_yarn_metrics(self, endpoint: str) -> dict[str, Any]:
        """获取 YARN 组件指标。"""
        return await self._get_hadoop_metrics(endpoint)


# 延迟导入以避免循环依赖
__all__ = ["BaseService", "ComponentMetricsService"]
