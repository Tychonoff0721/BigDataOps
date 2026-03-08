"""
BigDataOps 命令行测试程序

使用 Mock 数据模拟大数据组件的指标查询和分析功能
无需真实的大数据集群即可测试插件功能
"""

import asyncio
import json
from datetime import datetime
from typing import Any


class MockBigDataService:
    """模拟大数据服务，提供假的组件指标数据。"""

    def __init__(self) -> None:
        """初始化 Mock 服务。"""
        self.mock_data = self._init_mock_data()

    def _init_mock_data(self) -> dict[str, dict[str, Any]]:
        """初始化模拟数据。"""
        return {
            "spark": {
                "component": "Spark",
                "workers": 5,
                "active_workers": 5,
                "cores": 40,
                "memory": 65536,  # MB
                "running_apps": 3,
                "completed_apps": 12,
                "health": "healthy",
            },
            "hadoop": {
                "component": "Hadoop",
                "nodes_total": 10,
                "nodes_active": 8,
                "memory_used": 51200,
                "memory_total": 65536,
                "vcores_used": 32,
                "vcores_total": 40,
                "running_containers": 15,
                "health": "warning",
            },
            "flink": {
                "component": "Flink",
                "jobmanagers": 1,
                "slots_available": 8,
                "slots_total": 16,
                "jobs_running": 5,
                "jobs_finished": 23,
                "jobs_failed": 2,
                "health": "healthy",
            },
            "kafka": {
                "component": "Kafka",
                "brokers_count": 3,
                "topics_count": 15,
                "partitions_total": 60,
                "under_replicated": 5,
                "offline_partitions": 0,
                "health": "critical",
            },
            "hdfs": {
                "component": "HDFS",
                "files_total": 125000,
                "blocks_total": 380000,
                "capacity": 1099511627776,  # 1TB in bytes
                "used": 769098940416,  # 716GB
                "free": 330412687360,  # 308GB
                "health": "healthy",
            },
            "yarn": {
                "component": "YARN",
                "nodes_total": 10,
                "nodes_active": 9,
                "memory_used": 49152,
                "memory_total": 65536,
                "vcores_used": 28,
                "vcores_total": 40,
                "running_containers": 12,
                "health": "healthy",
            },
        }

    async def get_component_metrics(self, component_name: str) -> dict[str, Any]:
        """
        获取指定组件的指标数据（Mock 版本）。

        Args:
            component_name: 组件名称

        Returns:
            包含组件指标的字典

        Raises:
            ValueError: 如果组件不支持
        """
        await asyncio.sleep(0.5)  # 模拟网络延迟
        
        component_lower = component_name.lower()
        if component_lower not in self.mock_data:
            raise ValueError(f"不支持的组件类型：{component_name}")
        
        return self.mock_data[component_lower].copy()

    async def get_health_status(self, component_name: str) -> dict[str, Any]:
        """
        获取组件的健康状态评估（Mock 版本）。

        Args:
            component_name: 组件名称

        Returns:
            包含健康状态的字典
        """
        await asyncio.sleep(0.3)  # 模拟计算延迟
        
        metrics = await self.get_component_metrics(component_name)
        health = metrics.get("health", "unknown")
        
        # 根据健康状态生成问题和建议
        issues = []
        recommendations = []
        score = 100

        if health == "healthy":
            score = 95
            recommendations.append("保持当前配置和监控频率")
        elif health == "warning":
            score = 70
            if "nodes_active" in metrics and "nodes_total" in metrics:
                offline = metrics["nodes_total"] - metrics["nodes_active"]
                issues.append(f"有 {offline} 个节点离线")
                recommendations.append("检查离线节点的网络和进程状态")
            if "memory_used" in metrics and "memory_total" in metrics:
                usage = (metrics["memory_used"] / metrics["memory_total"]) * 100
                if usage > 75:
                    issues.append(f"内存使用率过高 ({usage:.1f}%)")
                    recommendations.append("考虑增加集群资源或优化作业配置")
        elif health == "critical":
            score = 35
            if "under_replicated" in metrics and metrics["under_replicated"] > 0:
                issues.append(f"有 {metrics['under_replicated']} 个分区复制不足")
                recommendations.append("立即检查 Broker 节点状态和网络连接")
            if "offline_partitions" in metrics and metrics["offline_partitions"] > 0:
                issues.append(f"有 {metrics['offline_partitions']} 个分区离线")
                recommendations.append("紧急处理离线分区，检查 Controller 状态")
        
        return {
            "component": component_name.upper(),
            "status": health,
            "score": score,
            "issues": issues,
            "recommendations": recommendations,
        }

    async def get_all_components_summary(self) -> dict[str, Any]:
        """
        获取所有组件的汇总信息（Mock 版本）。

        Returns:
            包含汇总信息的字典
        """
        components = list(self.mock_data.keys())
        summary = {
            "total_components": len(components),
            "healthy_count": 0,
            "warning_count": 0,
            "critical_count": 0,
            "components": [],
        }

        for comp in components:
            health_status = await self.get_health_status(comp)
            status = health_status["status"]
            
            summary["components"].append({
                "name": comp.upper(),
                "status": status,
                "score": health_status["score"],
            })
            
            if status == "healthy":
                summary["healthy_count"] += 1
            elif status == "warning":
                summary["warning_count"] += 1
            else:
                summary["critical_count"] += 1

        return summary


class MockRenderer:
    """模拟渲染器，生成美观的文本报告。"""

    def __init__(self) -> None:
        """初始化渲染器。"""
        pass

    def _format_number(self, num: int | float, suffix: str = "") -> str:
        """格式化数字显示。"""
        if num >= 1e9:
            return f"{num / 1e9:.1f}B{suffix}"
        elif num >= 1e6:
            return f"{num / 1e6:.1f}M{suffix}"
        elif num >= 1e3:
            return f"{num / 1e3:.1f}K{suffix}"
        else:
            return f"{num}{suffix}"

    def _get_health_emoji(self, health: str) -> str:
        """获取健康状态对应的 Emoji。"""
        emoji_map = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "unhealthy": "❌",
            "unknown": "❓",
        }
        return emoji_map.get(health, "❓")

    def render_analyze_report(self, data: dict[str, Any]) -> str:
        """渲染组件分析报告。"""
        component = data.get("component", "Unknown")
        health = data.get("health", "unknown")
        metrics = data.get("metrics", {})

        lines = []
        lines.append(f"📊 {component} 组件分析报告")
        lines.append("=" * 40)
        lines.append("")
        
        # 健康状态
        health_emoji = self._get_health_emoji(health)
        lines.append(f"{health_emoji} 健康状态：{health.upper()}")
        lines.append("")

        # 动态添加各项指标
        key_names = {
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

        for key, value in metrics.items():
            if key in ["component", "health"]:
                continue
            
            formatted_key = key_names.get(key, key.replace("_", " ").title())
            
            if isinstance(value, (int, float)):
                if "memory" in key.lower() or "capacity" in key.lower() or "used" in key.lower() or "free" in key.lower():
                    if value > 1e9:
                        formatted_value = self._format_number(value, " B")
                    elif value > 1e6:
                        formatted_value = self._format_number(value, " MB")
                    else:
                        formatted_value = self._format_number(value, " MB")
                elif value > 10000:
                    formatted_value = self._format_number(value)
                else:
                    formatted_value = str(value)
            else:
                formatted_value = str(value)

            lines.append(f"• {formatted_key}: {formatted_value}")

        lines.append("")
        lines.append("=" * 40)
        lines.append("💡 提示：使用 test_cli.py status <组件> 查看详细健康评估")

        return "\n".join(lines)

    def render_health_report(self, data: dict[str, Any]) -> str:
        """渲染健康状态报告。"""
        component = data.get("component", "Unknown")
        status = data.get("status", "unknown")
        score = data.get("score", 0)
        issues = data.get("issues", [])
        recommendations = data.get("recommendations", [])

        lines = []
        lines.append(f"🏥 {component} 健康检查报告")
        lines.append("=" * 40)
        lines.append("")
        
        status_emoji = self._get_health_emoji(status)
        lines.append(f"{status_emoji} 状态：{status.upper()}")
        lines.append(f"📈 健康分数：{score}/100")
        lines.append("")

        if issues:
            lines.append("⚠️ 发现的问题:")
            for i, issue in enumerate(issues, 1):
                lines.append(f"  {i}. {issue}")
            lines.append("")

        if recommendations:
            lines.append("💡 改进建议:")
            for i, rec in enumerate(recommendations, 1):
                lines.append(f"  {i}. {rec}")
            lines.append("")

        lines.append("=" * 40)

        return "\n".join(lines)

    def render_summary_report(self, data: dict[str, Any]) -> str:
        """渲染汇总报告。"""
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
        lines.append("💡 提示：使用 test_cli.py analyze <组件名> 查看单个组件详情")

        return "\n".join(lines)


async def cmd_analyze(service: MockBigDataService, renderer: MockRenderer, component: str) -> None:
    """处理 analyze 命令。"""
    try:
        print(f"\n🔄 正在分析 {component.upper()} 组件...\n")
        metrics = await service.get_component_metrics(component)
        report = renderer.render_analyze_report({
            "component": metrics["component"],
            "health": metrics["health"],
            "metrics": metrics,
        })
        print(report)
    except ValueError as e:
        print(f"❌ 错误：{e}")
        print("\n支持的组件：spark, hadoop, flink, kafka, hdfs, yarn")


async def cmd_status(service: MockBigDataService, renderer: MockRenderer, component: str) -> None:
    """处理 status 命令。"""
    try:
        print(f"\n🔄 正在检查 {component.upper()} 组件健康状态...\n")
        health = await service.get_health_status(component)
        report = renderer.render_health_report(health)
        print(report)
    except ValueError as e:
        print(f"❌ 错误：{e}")
        print("\n支持的组件：spark, hadoop, flink, kafka, hdfs, yarn")


async def cmd_summary(service: MockBigDataService, renderer: MockRenderer) -> None:
    """处理 summary 命令。"""
    print("\n🔄 正在获取所有组件汇总信息...\n")
    summary = await service.get_all_components_summary()
    report = renderer.render_summary_report(summary)
    print(report)


def show_help() -> None:
    """显示帮助信息。"""
    help_text = """
📊 BigDataOps 命令行测试工具

用法：python test_cli.py <命令> [参数]

可用命令:
  analyze <组件名>     - 分析指定组件的各项指标
  status <组件名>      - 查看组件健康状态评估
  summary              - 查看所有组件汇总信息
  help                 - 显示此帮助信息

支持的组件:
  • spark       - Apache Spark (分布式计算引擎)
  • hadoop      - Apache Hadoop (分布式存储和计算)
  • flink       - Apache Flink (流式计算引擎)
  • kafka       - Apache Kafka (消息队列)
  • hdfs        - Hadoop HDFS (分布式文件系统)
  • yarn        - Hadoop YARN (资源调度器)

示例:
  python test_cli.py analyze spark
  python test_cli.py status hadoop
  python test_cli.py summary
  python test_cli.py help

注意：本测试程序使用 Mock 数据，无需真实的大数据集群即可运行。
"""
    print(help_text)


async def main() -> None:
    """主函数。"""
    import sys

    # 创建服务和渲染器
    service = MockBigDataService()
    renderer = MockRenderer()

    # 解析命令行参数
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "help" or command == "-h" or command == "--help":
        show_help()
    
    elif command == "analyze":
        if len(sys.argv) < 3:
            print("❌ 错误：请指定组件名称")
            print("用法：python test_cli.py analyze <组件名>")
            print("\n支持的组件：spark, hadoop, flink, kafka, hdfs, yarn")
            return
        component = sys.argv[2].lower()
        await cmd_analyze(service, renderer, component)
    
    elif command == "status":
        if len(sys.argv) < 3:
            print("❌ 错误：请指定组件名称")
            print("用法：python test_cli.py status <组件名>")
            print("\n支持的组件：spark, hadoop, flink, kafka, hdfs, yarn")
            return
        component = sys.argv[2].lower()
        await cmd_status(service, renderer, component)
    
    elif command == "summary":
        await cmd_summary(service, renderer)
    
    else:
        print(f"❌ 未知命令：{command}")
        print("\n使用 'python test_cli.py help' 查看帮助信息")


if __name__ == "__main__":
    asyncio.run(main())
