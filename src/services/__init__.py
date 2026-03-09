"""服务层聚合模块"""

from typing import Any

from .base import BaseService, ComponentMetricsService
from .data_normalizer import DataNormalizer
from .exceptions import (
    BigDataAPIError,
    BigDataError,
    BigDataRateLimitError,
    CacheError,
    ComponentNotFoundError,
    MetricsCollectionError,
)
from .llm_analyzer import LLMAnalyzer
from .metrics_collector import (
    BaseMetricsCollector,
    MockMetricsCollector,
    RealMetricsCollector,
    MetricsCollectorFactory,
)
from .types import (
    AlertItem,
    AlertLevel,
    AnalysisReport,
    AnalysisResult,
    ComponentMetrics,
    ComponentType,
    HealthStatus,
    MessageResult,
    NormalizedMetrics,
)


class BigDataService(ComponentMetricsService, BaseService):
    """
    聚合服务类：继承所有子 Service 的功能。
    提供大数据分析的核心业务能力。
    """

    def __init__(
        self,
        config_manager: Any,
        session: Any | None = None,
    ) -> None:
        """
        初始化大数据服务。

        Args:
            config_manager: 配置管理器实例
            session: aiohttp 会话
        """
        BaseService.__init__(self, config_manager, session)
        ComponentMetricsService.__init__(self)

    async def analyze_component(
        self, component_name: str
    ) -> ComponentMetrics:
        """
        分析指定组件的各项指标。

        Args:
            component_name: 组件名称

        Returns:
            组件指标对象
        """
        import time
        
        try:
            metrics_data = await self.get_component_metrics(component_name)
            
            return ComponentMetrics(
                component=component_name.upper(),
                health=metrics_data.get("health", "unknown"),
                metrics=metrics_data,
                timestamp=time.time(),
                extra_info=None,
            )
        except BigDataAPIError as e:
            raise MetricsCollectionError(f"无法获取组件 {component_name} 的指标：{str(e)}") from e

    async def get_health_status(
        self, component_name: str
    ) -> HealthStatus:
        """
        获取组件的健康状态评估。

        Args:
            component_name: 组件名称

        Returns:
            健康状态对象
        """
        try:
            metrics_data = await self.get_component_metrics(component_name)
        except BigDataAPIError as e:
            return HealthStatus(
                component=component_name.upper(),
                status="unknown",
                score=0,
                issues=[f"无法获取指标数据：{str(e)}"],
                recommendations=["检查 API 端点配置是否正确", "确认组件是否正常运行"],
            )

        # 根据指标计算健康分数和问题
        health = metrics_data.get("health", "unknown")
        
        issues = []
        recommendations = []
        score = 100

        # 通用健康检查逻辑
        if health == "unhealthy":
            score -= 50
            issues.append("组件处于不健康状态")
            recommendations.append("检查组件日志和运行状态")
        elif health == "unknown":
            score -= 30
            issues.append("无法确定组件状态")
            recommendations.append("验证 API 连接性")

        # 特定组件的健康检查
        component_lower = component_name.lower()
        
        if component_lower == "spark":
            workers = metrics_data.get("workers", 0)
            active_workers = metrics_data.get("active_workers", 0)
            if workers > 0 and active_workers < workers:
                score -= 20
                issues.append(f"有 {workers - active_workers} 个 Worker 节点离线")
                recommendations.append("检查离线 Worker 节点的网络和进程状态")
                
        elif component_lower == "hadoop":
            nodes_total = metrics_data.get("nodes_total", 0)
            nodes_active = metrics_data.get("nodes_active", 0)
            if nodes_total > 0 and nodes_active < nodes_total:
                score -= 20
                issues.append(f"有 {nodes_total - nodes_active} 个 NodeManager 离线")
                recommendations.append("检查 NodeManager 进程状态")
                
        elif component_lower == "flink":
            jobs_failed = metrics_data.get("jobs_failed", 0)
            if jobs_failed > 0:
                score -= 30
                issues.append(f"有 {jobs_failed} 个作业失败")
                recommendations.append("检查失败作业的日志和资源配置")

        # 限制分数范围
        score = max(0, min(100, score))

        # 确定状态等级
        if score >= 80:
            status = "healthy"
        elif score >= 60:
            status = "warning"
        elif score >= 40:
            status = "critical"
        else:
            status = "unknown"

        return HealthStatus(
            component=component_name.upper(),
            status=status,
            score=score,
            issues=issues,
            recommendations=recommendations,
        )

    async def get_all_components_summary(self) -> dict[str, Any]:
        """
        获取所有支持组件的摘要信息。

        Returns:
            包含所有组件摘要的字典
        """
        components = [
            "spark", "hadoop", "flink", "kafka",
            "hdfs", "yarn"
        ]
        
        summary = {
            "total_components": len(components),
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "components": [],
        }

        for comp in components:
            try:
                health = await self.get_health_status(comp)
                summary["components"].append({
                    "name": comp.upper(),
                    "status": health.status,
                    "score": health.score,
                })
                
                if health.status == "healthy":
                    summary["healthy_count"] += 1
                elif health.status == "warning":
                    summary["warning_count"] += 1
                else:
                    summary["critical_count"] += 1
            except Exception:
                summary["components"].append({
                    "name": comp.upper(),
                    "status": "unknown",
                    "score": 0,
                })

        return summary


__all__ = [
    # 旧服务类（保留兼容）
    "BigDataService",
    "BaseService",
    "ComponentMetricsService",
    # 新服务类
    "LLMAnalyzer",
    "DataNormalizer",
    "BaseMetricsCollector",
    "MockMetricsCollector",
    "RealMetricsCollector",
    "MetricsCollectorFactory",
    # 异常类
    "BigDataAPIError",
    "BigDataRateLimitError",
    "BigDataError",
    "CacheError",
    "ComponentNotFoundError",
    "MetricsCollectionError",
    # 类型定义
    "AlertItem",
    "AlertLevel",
    "AnalysisReport",
    "AnalysisResult",
    "ComponentMetrics",
    "ComponentType",
    "HealthStatus",
    "MessageResult",
    "NormalizedMetrics",
]
