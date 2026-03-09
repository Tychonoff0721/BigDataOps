"""类型定义模块"""

from dataclasses import dataclass, field
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


class AlertLevel(Enum):
    """预警级别枚举。"""

    INFO = "info"           # 信息提示
    WARNING = "warning"     # 警告
    CRITICAL = "critical"   # 严重
    EMERGENCY = "emergency" # 紧急


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


@dataclass
class NormalizedMetrics:
    """正则化后的指标数据类。"""

    component: str
    timestamp: float
    # 正则化后的指标（0-1 范围）
    normalized_values: dict[str, float]
    # 原始值
    raw_values: dict[str, Any]
    # 单位信息
    units: dict[str, str] = field(default_factory=dict)
    # 指标描述
    descriptions: dict[str, str] = field(default_factory=dict)


@dataclass
class AlertItem:
    """单个预警项。"""

    level: AlertLevel
    metric_name: str
    current_value: Any
    threshold: Any
    description: str
    suggestion: str


@dataclass
class AnalysisResult:
    """大模型分析结果。"""

    component: str
    # 整体健康评分 (0-100)
    health_score: int
    # 整体状态评估
    status: str  # healthy, warning, critical, unknown
    # 分析摘要
    summary: str
    # 详细分析
    details: list[str]
    # 预警列表
    alerts: list[AlertItem]
    # 性能预测
    performance_prediction: str
    # 潜在故障预测
    failure_risks: list[str]
    # 改进建议
    recommendations: list[str]
    # 分析时间
    timestamp: float


@dataclass
class AnalysisReport:
    """完整的分析报告。"""

    component: str
    # 原始指标
    raw_metrics: dict[str, Any]
    # 正则化指标
    normalized_metrics: NormalizedMetrics
    # 分析结果
    analysis: AnalysisResult
    # 数据采集模式
    collection_mode: str  # "mock" 或 "real"
    # 报告生成时间
    report_time: float
