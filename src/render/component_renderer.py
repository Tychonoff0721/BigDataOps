"""组件渲染器模块"""

import time
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

    async def render_analysis_report(self, data: dict[str, Any]) -> str:
        """
        渲染完整的分析报告。

        Args:
            data: 包含分析报告数据的字典

        Returns:
            格式化后的文本报告
        """
        component = data.get("component", "Unknown")
        raw_metrics = data.get("raw_metrics", {})
        normalized_metrics = data.get("normalized_metrics")
        analysis = data.get("analysis")
        collection_mode = data.get("collection_mode", "unknown")
        report_time = data.get("report_time", time.time())

        lines = []
        
        # 标题
        lines.append(f"📊 {component} 智能分析报告")
        lines.append("=" * 50)
        lines.append("")
        
        # 基本信息
        lines.append(f"🕐 报告时间：{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(report_time))}")
        lines.append(f"📡 数据模式：{'🧪 测试数据' if collection_mode == 'mock' else '🔗 真实数据'}")
        lines.append("")

        # 一、指标概览
        lines.append("━" * 50)
        lines.append("📋 一、指标概览")
        lines.append("━" * 50)
        lines.append("")
        
        if normalized_metrics:
            lines.append("| 指标名称 | 原始值 | 正则化值 | 单位 |")
            lines.append("|----------|--------|----------|------|")
            for key, raw_value in raw_metrics.items():
                if key in ("component", "health"):
                    continue
                norm_value = normalized_metrics.normalized_values.get(key, 0)
                unit = normalized_metrics.units.get(key, "")
                lines.append(f"| {key} | {raw_value} | {norm_value:.2f} | {unit} |")
        lines.append("")

        # 二、健康评估
        if analysis:
            lines.append("━" * 50)
            lines.append("🏥 二、健康评估")
            lines.append("━" * 50)
            lines.append("")
            
            # 健康评分
            health_score = analysis.health_score
            status = analysis.status
            status_emoji = self._get_health_emoji(status)
            
            # 评分条
            score_bar = self._generate_score_bar(health_score)
            lines.append(f"健康评分：{score_bar} {health_score}/100")
            lines.append(f"状态判定：{status_emoji} {status.upper()}")
            lines.append(f"\n📝 摘要：{analysis.summary}")
            lines.append("")

            # 三、详细分析
            if analysis.details:
                lines.append("━" * 50)
                lines.append("🔍 三、详细分析")
                lines.append("━" * 50)
                lines.append("")
                for i, detail in enumerate(analysis.details, 1):
                    lines.append(f"  {i}. {detail}")
                lines.append("")

            # 四、预警信息
            if analysis.alerts:
                lines.append("━" * 50)
                lines.append("⚠️ 四、预警信息")
                lines.append("━" * 50)
                lines.append("")
                lines.append("| 级别 | 指标 | 当前值 | 阈值 | 描述 |")
                lines.append("|------|------|--------|------|------|")
                for alert in analysis.alerts:
                    level_emoji = self._get_alert_emoji(alert.level)
                    lines.append(
                        f"| {level_emoji} {alert.level.value} | {alert.metric_name} | "
                        f"{alert.current_value} | {alert.threshold} | {alert.description} |"
                    )
                lines.append("")
                lines.append("💡 预警建议：")
                for i, alert in enumerate(analysis.alerts, 1):
                    lines.append(f"  {i}. [{alert.metric_name}] {alert.suggestion}")
                lines.append("")

            # 五、性能预测
            lines.append("━" * 50)
            lines.append("📈 五、性能预测")
            lines.append("━" * 50)
            lines.append("")
            lines.append(f"{analysis.performance_prediction}")
            lines.append("")

            # 六、故障风险
            if analysis.failure_risks:
                lines.append("━" * 50)
                lines.append("🚨 六、故障风险")
                lines.append("━" * 50)
                lines.append("")
                for i, risk in enumerate(analysis.failure_risks, 1):
                    lines.append(f"  ⚡ {risk}")
                lines.append("")

            # 七、改进建议
            if analysis.recommendations:
                lines.append("━" * 50)
                lines.append("💡 七、改进建议")
                lines.append("━" * 50)
                lines.append("")
                for i, rec in enumerate(analysis.recommendations, 1):
                    lines.append(f"  {i}. {rec}")
                lines.append("")

        lines.append("=" * 50)
        lines.append("📌 提示：使用 /bigdata-help 查看所有命令")

        return "\n".join(lines)

    def _generate_score_bar(self, score: int, width: int = 10) -> str:
        """
        生成评分进度条。

        Args:
            score: 分数 (0-100)
            width: 进度条宽度

        Returns:
            进度条字符串
        """
        filled = int(score / 100 * width)
        empty = width - filled
        
        if score >= 80:
            bar_char = "🟩"
        elif score >= 60:
            bar_char = "🟨"
        elif score >= 40:
            bar_char = "🟧"
        else:
            bar_char = "🟥"
        
        return bar_char * filled + "⬜" * empty

    def _get_alert_emoji(self, level: Any) -> str:
        """
        获取预警级别对应的 emoji。

        Args:
            level: 预警级别

        Returns:
            对应的 emoji
        """
        from ..services.types import AlertLevel
        
        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🔴",
            AlertLevel.EMERGENCY: "🆘",
        }
        return emoji_map.get(level, "❓")

    async def render_alert_table(self, data: dict[str, Any]) -> str:
        """
        渲染预警表格。

        Args:
            data: 包含预警数据的字典

        Returns:
            格式化后的预警表格
        """
        component = data.get("component", "Unknown")
        alerts = data.get("alerts", [])

        lines = []
        lines.append(f"⚠️ {component} 预警信息")
        lines.append("=" * 50)
        lines.append("")

        if not alerts:
            lines.append("✅ 当前无预警信息")
        else:
            lines.append("| 级别 | 指标名称 | 当前值 | 阈值 | 描述 | 建议 |")
            lines.append("|------|----------|--------|------|------|------|")
            for alert in alerts:
                level_emoji = self._get_alert_emoji(alert.level)
                lines.append(
                    f"| {level_emoji} {alert.level.value} | {alert.metric_name} | "
                    f"{alert.current_value} | {alert.threshold} | {alert.description} | {alert.suggestion} |"
                )

        lines.append("")
        lines.append("=" * 50)
        return "\n".join(lines)
