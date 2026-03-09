"""数据正则化处理模块

将采集的原始指标数据进行正则化处理，统一到 0-1 范围内，
便于大模型分析和跨组件比较。
"""

import time
from typing import Any

from .types import ComponentMetrics, NormalizedMetrics


class DataNormalizer:
    """数据正则化处理器。"""

    # 各组件指标的元数据配置
    METRIC_METADATA: dict[str, dict[str, dict[str, Any]]] = {
        "spark": {
            "workers": {"min": 0, "max": 100, "unit": "个", "desc": "工作节点总数"},
            "active_workers": {"min": 0, "max": 100, "unit": "个", "desc": "活跃工作节点数"},
            "cores": {"min": 0, "max": 1000, "unit": "核", "desc": "CPU 核心总数"},
            "memory": {"min": 0, "max": 10000, "unit": "GB", "desc": "内存总量"},
            "running_apps": {"min": 0, "max": 50, "unit": "个", "desc": "运行中的应用数"},
            "completed_apps": {"min": 0, "max": 10000, "unit": "个", "desc": "已完成应用数"},
            "pending_apps": {"min": 0, "max": 100, "unit": "个", "desc": "等待中的应用数"},
            "failed_apps": {"min": 0, "max": 100, "unit": "个", "desc": "失败的应用数"},
        },
        "hadoop": {
            "nodes_total": {"min": 0, "max": 100, "unit": "个", "desc": "节点总数"},
            "nodes_active": {"min": 0, "max": 100, "unit": "个", "desc": "活跃节点数"},
            "memory_used": {"min": 0, "max": 10000, "unit": "GB", "desc": "已用内存"},
            "memory_total": {"min": 0, "max": 10000, "unit": "GB", "desc": "总内存"},
            "vcores_used": {"min": 0, "max": 1000, "unit": "核", "desc": "已用虚拟核心"},
            "vcores_total": {"min": 0, "max": 1000, "unit": "核", "desc": "总虚拟核心"},
            "running_containers": {"min": 0, "max": 500, "unit": "个", "desc": "运行中的容器"},
            "pending_containers": {"min": 0, "max": 100, "unit": "个", "desc": "等待中的容器"},
        },
        "flink": {
            "taskmanagers": {"min": 0, "max": 50, "unit": "个", "desc": "TaskManager 数量"},
            "slots_available": {"min": 0, "max": 500, "unit": "个", "desc": "可用 Slot 数"},
            "slots_total": {"min": 0, "max": 500, "unit": "个", "desc": "总 Slot 数"},
            "jobs_running": {"min": 0, "max": 100, "unit": "个", "desc": "运行中的作业"},
            "jobs_finished": {"min": 0, "max": 10000, "unit": "个", "desc": "已完成的作业"},
            "jobs_failed": {"min": 0, "max": 100, "unit": "个", "desc": "失败的作业"},
            "jobs_cancelled": {"min": 0, "max": 100, "unit": "个", "desc": "取消的作业"},
        },
        "kafka": {
            "brokers_count": {"min": 0, "max": 20, "unit": "个", "desc": "Broker 数量"},
            "topics_count": {"min": 0, "max": 500, "unit": "个", "desc": "主题数量"},
            "partitions_total": {"min": 0, "max": 5000, "unit": "个", "desc": "分区总数"},
            "under_replicated": {"min": 0, "max": 100, "unit": "个", "desc": "复制不足的分区"},
            "offline_partitions": {"min": 0, "max": 50, "unit": "个", "desc": "离线分区"},
            "messages_per_sec": {"min": 0, "max": 100000, "unit": "条/秒", "desc": "每秒消息数"},
            "bytes_per_sec": {"min": 0, "max": 104857600, "unit": "B/s", "desc": "每秒字节数"},
        },
        "hdfs": {
            "files_total": {"min": 0, "max": 10000000, "unit": "个", "desc": "文件总数"},
            "blocks_total": {"min": 0, "max": 5000000, "unit": "个", "desc": "区块总数"},
            "capacity": {"min": 0, "max": 1000000, "unit": "GB", "desc": "总容量"},
            "used": {"min": 0, "max": 1000000, "unit": "GB", "desc": "已使用容量"},
            "free": {"min": 0, "max": 1000000, "unit": "GB", "desc": "剩余容量"},
            "under_replicated_blocks": {"min": 0, "max": 1000, "unit": "个", "desc": "复制不足的块"},
            "corrupt_blocks": {"min": 0, "max": 100, "unit": "个", "desc": "损坏的块"},
        },
        "yarn": {
            "apps_running": {"min": 0, "max": 200, "unit": "个", "desc": "运行中的应用"},
            "apps_pending": {"min": 0, "max": 100, "unit": "个", "desc": "等待中的应用"},
            "apps_completed": {"min": 0, "max": 10000, "unit": "个", "desc": "完成的应用"},
            "apps_failed": {"min": 0, "max": 100, "unit": "个", "desc": "失败的应用"},
            "containers_running": {"min": 0, "max": 500, "unit": "个", "desc": "运行中的容器"},
            "containers_pending": {"min": 0, "max": 100, "unit": "个", "desc": "等待中的容器"},
            "memory_allocated": {"min": 0, "max": 10000, "unit": "GB", "desc": "已分配内存"},
            "memory_available": {"min": 0, "max": 10000, "unit": "GB", "desc": "可用内存"},
        },
        "hive": {
            "databases": {"min": 0, "max": 100, "unit": "个", "desc": "数据库数量"},
            "tables": {"min": 0, "max": 5000, "unit": "个", "desc": "表数量"},
            "partitions": {"min": 0, "max": 100000, "unit": "个", "desc": "分区数量"},
            "active_sessions": {"min": 0, "max": 50, "unit": "个", "desc": "活跃会话数"},
            "queries_running": {"min": 0, "max": 50, "unit": "个", "desc": "运行中的查询"},
            "queries_completed": {"min": 0, "max": 100000, "unit": "个", "desc": "完成的查询"},
        },
        "clickhouse": {
            "databases": {"min": 0, "max": 50, "unit": "个", "desc": "数据库数量"},
            "tables": {"min": 0, "max": 1000, "unit": "个", "desc": "表数量"},
            "rows_total": {"min": 0, "max": 100000000000, "unit": "行", "desc": "总行数"},
            "queries_per_sec": {"min": 0, "max": 10000, "unit": "次/秒", "desc": "每秒查询数"},
            "memory_used": {"min": 0, "max": 100000, "unit": "MB", "desc": "已用内存"},
            "memory_total": {"min": 0, "max": 100000, "unit": "MB", "desc": "总内存"},
        },
    }

    def normalize(self, metrics: ComponentMetrics) -> NormalizedMetrics:
        """
        对组件指标进行正则化处理。

        Args:
            metrics: 原始组件指标数据

        Returns:
            正则化后的指标数据
        """
        component_lower = metrics.component.lower()
        raw_values = metrics.metrics.copy()

        # 获取该组件的元数据配置
        metadata = self.METRIC_METADATA.get(component_lower, {})

        normalized_values: dict[str, float] = {}
        units: dict[str, str] = {}
        descriptions: dict[str, str] = {}

        for key, value in raw_values.items():
            if key in ("component", "health"):
                continue

            # 获取该指标的元数据
            meta = metadata.get(key, {})

            if isinstance(value, (int, float)):
                # Min-Max 正则化
                min_val = meta.get("min", 0)
                max_val = meta.get("max", max(value * 2, 1))  # 动态计算最大值

                if max_val > min_val:
                    normalized = (value - min_val) / (max_val - min_val)
                else:
                    normalized = 0.0

                # 限制在 0-1 范围内
                normalized_values[key] = max(0.0, min(1.0, normalized))
            else:
                # 非数值类型，跳过正则化
                normalized_values[key] = 0.0

            # 记录单位和描述
            units[key] = meta.get("unit", "")
            descriptions[key] = meta.get("desc", key)

        # 添加计算指标
        self._add_computed_metrics(component_lower, raw_values, normalized_values)

        return NormalizedMetrics(
            component=metrics.component,
            timestamp=time.time(),
            normalized_values=normalized_values,
            raw_values=raw_values,
            units=units,
            descriptions=descriptions,
        )

    def _add_computed_metrics(
        self,
        component: str,
        raw_values: dict[str, Any],
        normalized_values: dict[str, float],
    ) -> None:
        """添加计算得出的衍生指标。"""

        # 资源利用率
        if component == "spark":
            if raw_values.get("workers", 0) > 0:
                utilization = raw_values.get("active_workers", 0) / raw_values["workers"]
                normalized_values["worker_utilization"] = utilization

        elif component in ("hadoop", "yarn"):
            if raw_values.get("nodes_total", 0) > 0:
                utilization = raw_values.get("nodes_active", 0) / raw_values["nodes_total"]
                normalized_values["node_utilization"] = utilization

            if raw_values.get("memory_total", 0) > 0:
                utilization = raw_values.get("memory_used", 0) / raw_values["memory_total"]
                normalized_values["memory_utilization"] = utilization

        elif component == "flink":
            if raw_values.get("slots_total", 0) > 0:
                used_slots = raw_values["slots_total"] - raw_values.get("slots_available", 0)
                utilization = used_slots / raw_values["slots_total"]
                normalized_values["slot_utilization"] = utilization

        elif component == "kafka":
            if raw_values.get("partitions_total", 0) > 0:
                unhealthy_ratio = (
                    raw_values.get("under_replicated", 0) + raw_values.get("offline_partitions", 0)
                ) / raw_values["partitions_total"]
                normalized_values["partition_health"] = 1.0 - unhealthy_ratio

        elif component == "hdfs":
            if raw_values.get("capacity", 0) > 0:
                utilization = raw_values.get("used", 0) / raw_values["capacity"]
                normalized_values["storage_utilization"] = utilization

    def get_metric_metadata(self, component: str, metric_name: str) -> dict[str, Any]:
        """
        获取指定指标的元数据。

        Args:
            component: 组件名称
            metric_name: 指标名称

        Returns:
            指标元数据字典
        """
        return self.METRIC_METADATA.get(component.lower(), {}).get(metric_name, {})
