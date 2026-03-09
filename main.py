"""
BigDataOps - AstrBot 大数据分析插件

支持 Hadoop、Spark、Flink、Kafka 等大数据组件的指标采集、智能分析和故障预测。
"""

import time
from collections.abc import AsyncGenerator
from typing import Any

import aiohttp
from astrbot.api import logger
from astrbot.api.all import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star, StarTools, register

from .src.config import ConfigManager
from .src.db import BigDataRepository
from .src.render import ComponentRenderer
from .src.services import (
    AnalysisReport,
    DataNormalizer,
    LLMAnalyzer,
    MetricsCollectorFactory,
    NormalizedMetrics,
)
from .src.utils import EnvManager


@register(
    "astrbot_plugin_bigdataops",
    "YourName",
    "AstrBot 大数据智能分析助手：采集大数据组件指标，使用大模型进行智能分析和故障预测。",
    "v2.0.0",
    "https://github.com/yourusername/astrbot_plugin_bigdataops",
)
class BigDataOpsPlugin(Star):
    """
    BigDataOps 插件类，提供大数据组件的智能分析功能。

    核心流程：
    1. 指标采集 -> 2. 数据正则化 -> 3. 大模型分析 -> 4. 生成报告
    """

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        """
        初始化 BigDataOpsPlugin 插件。

        Args:
            context: 插件上下文
            config: 插件配置
        """
        super().__init__(context)
        self.config = config
        self.config_manager = ConfigManager(config)

        self.session: aiohttp.ClientSession | None = None
        self.storage: BigDataRepository | None = None
        self.renderer: ComponentRenderer | None = None
        self.env_manager: EnvManager | None = None

        # 新增服务组件
        self.metrics_collector = None
        self.data_normalizer: DataNormalizer | None = None
        self.llm_analyzer: LLMAnalyzer | None = None

    async def initialize(self) -> None:
        """
        插件加载时自动运行的初始化方法。
        """
        # 0. 获取插件数据目录
        plugin_data_dir = StarTools.get_data_dir()

        # 1. 初始化数据库
        try:
            db_path = plugin_data_dir / "data.db"
            self.storage = BigDataRepository(db_path=str(db_path))
            logger.info("数据库初始化成功")
        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f"数据库初始化失败：{e}")

        # 2. 初始化网络会话
        self.session = aiohttp.ClientSession()

        # 3. 初始化指标采集器
        self.metrics_collector = MetricsCollectorFactory.create(
            config_manager=self.config_manager,
            session=self.session,
        )
        mode = "测试模式(Mock)" if self.config_manager.is_test_mode() else "生产模式(真实数据)"
        logger.info(f"指标采集器初始化成功 - {mode}")

        # 4. 初始化数据正则化器
        self.data_normalizer = DataNormalizer()
        logger.info("数据正则化器初始化成功")

        # 5. 初始化 LLM 分析器（使用 AstrBot 官方 API）
        self.llm_analyzer = LLMAnalyzer(self.context)
        logger.info("LLM 分析器初始化成功")

        # 6. 初始化渲染器
        render_server_url = self.config_manager.get_render_server_url()
        self.renderer = ComponentRenderer(render_server_url=render_server_url)

        # 7. 初始化环境管理器
        self.env_manager = EnvManager(str(plugin_data_dir))

        # 检查依赖
        missing_deps = self.env_manager.check_requirements()
        if missing_deps:
            logger.warning(f"缺少依赖包：{missing_deps}，请运行 pip install -r requirements.txt")

        logger.info("BigDataOps 插件初始化完成")

    # --- 命令处理区 ---

    @filter.command("bigdata")
    async def analyze_component(
        self, event: AstrMessageEvent, component: str
    ) -> AsyncGenerator[object, None]:
        """
        分析指定大数据组件的指标并进行智能诊断。

        支持的组件：spark, hadoop, flink, kafka, hdfs, yarn 等

        Args:
            event: 事件对象
            component: 组件名称
        """
        if not self.metrics_collector:
            yield event.plain_result("❌ 指标采集器未初始化")
            return

        if not self.data_normalizer:
            yield event.plain_result("❌ 数据正则化器未初始化")
            return

        if not self.llm_analyzer:
            yield event.plain_result("❌ LLM 分析器未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        # 验证组件名称
        valid_components = [
            "spark", "hadoop", "flink", "kafka",
            "hdfs", "yarn", "hive", "presto",
            "clickhouse", "storm", "hbase", "cassandra",
        ]

        if component.lower() not in valid_components:
            yield event.plain_result(
                f"❌ 不支持的组件类型：{component}\n"
                f"支持的组件：{', '.join(valid_components)}"
            )
            return

        try:
            # ========== 第一步：采集指标数据 ==========
            logger.info(f"开始采集组件 {component} 的指标数据...")
            yield event.plain_result(f"⏳ 正在采集 {component.upper()} 的指标数据...")

            metrics = await self.metrics_collector.collect(component)
            logger.info(f"指标采集完成：{metrics.metrics}")

            # ========== 第二步：数据正则化 ==========
            logger.info(f"开始对 {component} 的指标数据进行正则化...")
            normalized_metrics = self.data_normalizer.normalize(metrics)
            logger.info(f"数据正则化完成")

            # ========== 第三步：调用大模型分析 ==========
            logger.info(f"开始调用大模型分析 {component}...")
            yield event.plain_result(f"🤖 正在使用大模型分析 {component.upper()} 的指标...")

            # 获取 unified_msg_origin 用于调用 LLM
            umo = event.unified_msg_origin
            analysis_result = await self.llm_analyzer.analyze(
                unified_msg_origin=umo,
                component=component,
                raw_metrics=metrics.metrics,
                normalized_metrics=normalized_metrics,
            )
            logger.info(f"大模型分析完成：健康评分 {analysis_result.health_score}")

            # ========== 第四步：生成完整报告 ==========
            collection_mode = "mock" if self.config_manager.is_test_mode() else "real"

            report = AnalysisReport(
                component=component.upper(),
                raw_metrics=metrics.metrics,
                normalized_metrics=normalized_metrics,
                analysis=analysis_result,
                collection_mode=collection_mode,
                report_time=time.time(),
            )

            # 保存历史记录
            if self.storage:
                user_id = event.get_sender_id()
                self.storage.save_query(
                    user_id=user_id,
                    component=component,
                    query_type="analysis",
                )
                self.storage.save_metrics(
                    component=component,
                    metrics=metrics.metrics,
                    health_status=analysis_result.status,
                    score=analysis_result.health_score,
                )

            # 渲染报告
            report_text = await self.renderer.render_analysis_report({
                "component": report.component,
                "raw_metrics": report.raw_metrics,
                "normalized_metrics": report.normalized_metrics,
                "analysis": report.analysis,
                "collection_mode": report.collection_mode,
                "report_time": report.report_time,
            })

            # 发送结果
            yield event.plain_result(report_text)

        except Exception as e:
            logger.error(f"分析组件 {component} 时出错：{e}")
            yield event.plain_result(f"❌ 分析失败：{str(e)}")

    @filter.command("bigdata-alerts")
    async def get_alerts(
        self, event: AstrMessageEvent, component: str
    ) -> AsyncGenerator[object, None]:
        """
        获取指定组件的预警信息。

        Args:
            event: 事件对象
            component: 组件名称
        """
        if not self.metrics_collector or not self.llm_analyzer:
            yield event.plain_result("❌ 服务未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        try:
            # 快速采集和分析
            metrics = await self.metrics_collector.collect(component)
            normalized = self.data_normalizer.normalize(metrics)

            umo = event.unified_msg_origin
            analysis = await self.llm_analyzer.analyze(
                unified_msg_origin=umo,
                component=component,
                raw_metrics=metrics.metrics,
                normalized_metrics=normalized,
            )

            # 渲染预警表格
            alert_text = await self.renderer.render_alert_table({
                "component": component.upper(),
                "alerts": analysis.alerts,
            })

            yield event.plain_result(alert_text)

        except Exception as e:
            logger.error(f"获取 {component} 预警信息时出错：{e}")
            yield event.plain_result(f"❌ 获取失败：{str(e)}")

    @filter.command("bigdata-status")
    async def get_health_status(
        self, event: AstrMessageEvent, component: str
    ) -> AsyncGenerator[object, None]:
        """
        获取指定组件的健康状态评估。

        Args:
            event: 事件对象
            component: 组件名称
        """
        if not self.metrics_collector or not self.llm_analyzer:
            yield event.plain_result("❌ 服务未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        try:
            # 获取指标和分析
            metrics = await self.metrics_collector.collect(component)
            normalized = self.data_normalizer.normalize(metrics)

            umo = event.unified_msg_origin
            analysis = await self.llm_analyzer.analyze(
                unified_msg_origin=umo,
                component=component,
                raw_metrics=metrics.metrics,
                normalized_metrics=normalized,
            )

            # 保存记录
            if self.storage:
                user_id = event.get_sender_id()
                self.storage.save_query(
                    user_id=user_id,
                    component=component,
                    query_type="health",
                )

            # 渲染健康报告
            report_text = await self.renderer.render_health_text({
                "component": analysis.component,
                "status": analysis.status,
                "score": analysis.health_score,
                "issues": [alert.description for alert in analysis.alerts],
                "recommendations": analysis.recommendations,
            })

            yield event.plain_result(report_text)

        except Exception as e:
            logger.error(f"获取 {component} 健康状态时出错：{e}")
            yield event.plain_result(f"❌ 获取失败：{str(e)}")

    @filter.command("bigdata-summary")
    async def get_summary(
        self, event: AstrMessageEvent
    ) -> AsyncGenerator[object, None]:
        """
        获取所有大数据组件的汇总信息。

        Args:
            event: 事件对象
        """
        if not self.metrics_collector or not self.llm_analyzer:
            yield event.plain_result("❌ 服务未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        try:
            components = ["spark", "hadoop", "flink", "kafka", "hdfs", "yarn"]

            summary = {
                "total_components": len(components),
                "healthy_count": 0,
                "warning_count": 0,
                "critical_count": 0,
                "components": [],
            }

            yield event.plain_result("⏳ 正在汇总所有组件状态...")

            for comp in components:
                try:
                    metrics = await self.metrics_collector.collect(comp)
                    normalized = self.data_normalizer.normalize(metrics)

                    umo = event.unified_msg_origin
                    analysis = await self.llm_analyzer.analyze(
                        unified_msg_origin=umo,
                        component=comp,
                        raw_metrics=metrics.metrics,
                        normalized_metrics=normalized,
                    )

                    summary["components"].append({
                        "name": comp.upper(),
                        "status": analysis.status,
                        "score": analysis.health_score,
                    })

                    if analysis.status == "healthy":
                        summary["healthy_count"] += 1
                    elif analysis.status == "warning":
                        summary["warning_count"] += 1
                    else:
                        summary["critical_count"] += 1

                except Exception as e:
                    logger.warning(f"获取组件 {comp} 状态失败：{e}")
                    summary["components"].append({
                        "name": comp.upper(),
                        "status": "unknown",
                        "score": 0,
                    })

            # 渲染报告
            report_text = await self.renderer.render_summary_text(summary)
            yield event.plain_result(report_text)

        except Exception as e:
            logger.error(f"获取汇总信息时出错：{e}")
            yield event.plain_result(f"❌ 获取失败：{str(e)}")

    @filter.command("bigdata-help")
    async def show_help(
        self, event: AstrMessageEvent
    ) -> AsyncGenerator[object, None]:
        """
        显示帮助信息。

        Args:
            event: 事件对象
        """
        help_text = """
📊 BigDataOps 大数据智能分析助手

可用命令:
  /bigdata <组件名>        - 采集指标并进行智能分析诊断
  /bigdata-alerts <组件>   - 查看组件预警信息
  /bigdata-status <组件>   - 查看组件健康状态
  /bigdata-summary         - 查看所有组件汇总
  /bigdata-help            - 显示此帮助信息

支持的组件:
  • Spark      - 分布式计算引擎
  • Hadoop     - 分布式存储和计算
  • Flink      - 流式计算引擎
  • Kafka      - 消息队列
  • HDFS       - 分布式文件系统
  • YARN       - 资源调度器
  • Hive       - 数据仓库
  • Presto     - 交互式查询引擎
  • ClickHouse - OLAP 数据库

分析流程:
  1️⃣ 指标采集 - 采集组件的各项运行指标
  2️⃣ 数据正则化 - 将指标数据标准化处理
  3️⃣ 大模型分析 - 使用 AI 进行智能诊断和预测
  4️⃣ 生成报告 - 输出包含指标、分析、预警的完整报告

示例:
  /bigdata spark
  /bigdata-alerts hadoop
  /bigdata-status kafka
  /bigdata-summary

💡 提示：
  - 首次使用请确保已在 AstrBot 中配置大模型服务
  - 可通过配置切换测试模式(Mock数据)或生产模式
"""
        yield event.plain_result(help_text)

    async def terminate(self) -> None:
        """
        插件卸载或停用时的清理方法。
        """
        logger.info("正在清理 BigDataOps 插件资源...")

        # 关闭网络会话
        if self.session and not self.session.closed:
            await self.session.close()
            logger.info("已关闭网络会话")

        logger.info("BigDataOps 插件已停止")

        await super().terminate()
