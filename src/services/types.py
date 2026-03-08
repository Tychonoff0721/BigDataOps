"""类型定义模块"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ComponentType(Enum):
    """大数据组件类型枚举。"""

    SPARK = "spark"
    HADOOP = "hadoop"
    FLINK = "flink"
    KAFKA = "kafka"
    HDFS = "hdfs"
    YARN = "yarn"
    HIVE = "hive"
    PRESTO = "presto"
    CLICKHOUSE = "clickhouse"
    STORM = "storm"
    HBASE = "hbase"
    CASSANDRA = "cassandra"
    RABBITMQ = "rabbitmq"
    ROCKETMQ = "rocketmq"
    KUBERNETES = "kubernetes"


@dataclass
class ComponentMetrics:
    """组件指标数据类。"""

    component: str
    health: str  # healthy, unhealthy, unknown
    metrics: dict[str, Any]
    timestamp: float
    extra_info: dict[str, Any] | None = None


@dataclass
class HealthStatus:
    """健康状态数据类。"""

    component: str
    status: str  # healthy, warning, critical, unknown
    score: int  # 0-100
    issues: list[str]
    recommendations: list[str]


@dataclass
class MessageResult:
    """消息结果数据类。"""

    success: bool
    message: str
    data: Any | None = None
    image_url: str | None = None
