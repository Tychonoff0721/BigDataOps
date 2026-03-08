"""组件渲染器模块"""

from typing import Any

from .base_renderer import BaseRenderer


class ComponentRenderer(BaseRenderer):
    """组件指标渲染器，用于生成美观的分析报告。"""

    async def render_text(self, data: dict[str, Any]) -> str:
        """
        渲染组件指标的文本报告。

        Args:
            data: 包含组件指标数据的字典

        Returns:
            格式化后的文本报告
        """
        component = data.get("component", "Unknown")
        health = data.get("health", "unknown")
        metrics = data.get("metrics", {})

        lines = []
        lines.append(f"📊 {component} 组件分析报告")
        lines.append("=" * 40)
        lines.append("")
        
        # 健康状态
        health_emoji = self._get_health_emoji(health)
        health_color = self._get_health_color(health)
        lines.append(f"{health_emoji} 健康状态：{health_color} {health.upper()}")
        lines.append("")

        # 动态添加各项指标
        for key, value in metrics.items():
            if key in ["component", "health"]:
                continue
            
            # 格式化键名
            formatted_key = self._format_key_name(key)
            
            # 格式化数值
            if isinstance(value, (int, float)):
                if "memory" in key.lower() or "capacity" in key.lower():
                    formatted_value = self._format_number(value, " MB")
                elif "percent" in key.lower() or "%" in key.lower():
                    formatted_value = f"{value}%"
                elif value > 10000:
                    formatted_value = self._format_number(value)
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)

            lines.append(f"• {formatted_key}: {formatted_value}")

        lines.append("")
        lines.append("=" * 40)
        lines.append("💡 提示：使用 /bigdata status <组件> 查看详细健康评估")

        return "\n".join(lines)

    async def render_health_text(self, data: dict[str, Any]) -> str:
        """
        渲染健康状态的文本报告。

        Args:
            data: 包含健康状态数据的字典

        Returns:
            格式化后的文本报告
        """
        component = data.get("component", "Unknown")
        status = data.get("status", "unknown")
        score = data.get("score", 0)
        issues = data.get("issues", [])
        recommendations = data.get("recommendations", [])

        lines = []
        lines.append(f"🏥 {component} 健康检查报告")
        lines.append("=" * 40)
        lines.append("")
        
        # 健康分数
        status_emoji = self._get_health_emoji(status)
        lines.append(f"{status_emoji} 状态：{status.upper()}")
        lines.append(f"📈 健康分数：{score}/100")
        lines.append("")

        # 问题列表
        if issues:
            lines.append("⚠️ 发现的问题:")
            for i, issue in enumerate(issues, 1):
                lines.append(f"  {i}. {issue}")
            lines.append("")

        # 建议列表
        if recommendations:
            lines.append("💡 改进建议:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")

        lines.append("=" * 40)

        return "\n".join(lines)

    async def render_summary_text(self, data: dict[str, Any]) -> str:
        """
        渲染所有组件汇总的文本报告。

        Args:
            data: 包含所有组件摘要的字典

        Returns:
            格式化后的文本报告
        """
        total = data.get("total_components", 0)
        healthy = data.get("healthy_count", 0)
        warning = data.get("warning_count", 0)
        critical = data.get("critical_count", 0)
        components = data.get("components", [])

        lines = []
        lines.append("📊 大数据组件总览")
        lines.append("=" * 40)
        lines.append("")
        lines.append(f"📦 组件总数：{total}")
        lines.append(f"🟢 健康：{healthy}")
        lines.append(f"🟡 警告：{warning}")
        lines.append(f"🔴 严重：{critical}")
        lines.append("")
        lines.append("各组件状态:")
        lines.append("-" * 40)

        for comp in components:
            name = comp.get("name", "Unknown")
            status = comp.get("status", "unknown")
            score = comp.get("score", 0)
            
            status_emoji = self._get_health_emoji(status)
            lines.append(f"{status_emoji} {name}: {score}分 ({status})")

        lines.append("")
        lines.append("=" * 40)
        lines.append("💡 提示：使用 /bigdata <组件名> 查看单个组件详情")

        return "\n".join(lines)

    async def render_image(self, data: dict[str, Any]) -> bytes | None:
        """
        渲染组件指标的图片报告。

        Args:
            data: 包含组件指标数据的字典

        Returns:
            图片二进制数据
        """
        # 尝试使用 RPC 远程渲染
        image_bytes = await self._render_with_rpc("component_report", data)
        if image_bytes:
            return image_bytes

        # 本地渲染暂不实现，返回 None 使用文本报告
        return None

    def _format_key_name(self, key: str) -> str:
        """
        格式化键名为可读的中文名称。

        Args:
            key: 原始键名

        Returns:
            格式化后的中文名称
        """
        key_map = {
            "workers": "工作节点数",
            "active_workers": "活跃工作节点",
            "cores": "CPU 核心数",
            "memory": "内存总量",
            "running_apps": "运行中的应用",
            "completed_apps": "已完成应用",
            "nodes_total": "节点总数",
            "nodes_active": "活跃节点数",
            "memory_used": "已用内存",
            "memory_total": "总内存",
            "vcores_used": "已用虚拟核心",
            "vcores_total": "总虚拟核心",
            "running_containers": "运行中的容器",
            "jobmanagers": "JobManager 数量",
            "slots_available": "可用 Slot 数",
            "slots_total": "总 Slot 数",
            "jobs_running": "运行中的作业",
            "jobs_finished": "已完成的作业",
            "jobs_failed": "失败的作业",
            "brokers_count": "Broker 数量",
            "topics_count": "主题数量",
            "partitions_total": "分区总数",
            "under_replicated": "复制不足的分区",
            "offline_partitions": "离线分区",
            "files_total": "文件总数",
            "blocks_total": "区块总数",
            "capacity": "总容量",
            "used": "已使用",
            "free": "剩余",
        }
        
        return key_map.get(key, key.replace("_", " ").title())
