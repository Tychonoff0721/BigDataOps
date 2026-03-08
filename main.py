"""
BigDataOps - AstrBot 大数据分析插件

支持 Hadoop、Spark、Flink、Kafka 等大数据组件的指标查询、性能分析和健康状态评估。
"""

import asyncio
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
from .src.services import BigDataService
from .src.utils import EnvManager


@register(
    "astrbot_plugin_bigdataops",
    "YourName",
    "AstrBot 大数据分析助手：输入大数据组件名称，自动分析并返回各项重要指标、性能评估和使用建议。",
    "v1.0.0",
    "https://github.com/yourusername/astrbot_plugin_bigdataops",
)
class BigDataOpsPlugin(Star):
    """
    BigDataOps 插件类，提供大数据分析功能。
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
        self.service: BigDataService | None = None
        self.renderer: ComponentRenderer | None = None
        self.env_manager: EnvManager | None = None

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

        # 3. 初始化核心服务
        try:
            self.service = BigDataService(
                config_manager=self.config_manager,
                session=self.session,
            )
            logger.info("大数据服务初始化成功")
        except (RuntimeError, ValueError) as e:
            logger.error(f"服务初始化失败：{e}")

        # 4. 初始化渲染器
        render_server_url = self.config_manager.get_render_server_url()
        self.renderer = ComponentRenderer(render_server_url=render_server_url)

        # 5. 初始化环境管理器
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
        分析指定大数据组件的各项指标。

        支持的组件：spark, hadoop, flink, kafka, hdfs, yarn 等

        Args:
            event: 事件对象
            component: 组件名称
        """
        if not self.service:
            yield event.plain_result("❌ 服务未初始化，请检查配置")
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
            # 获取组件指标
            metrics = await self.service.analyze_component(component)

            # 保存历史记录
            if self.storage:
                user_id = event.get_sender_id()
                self.storage.save_query(
                    user_id=user_id,
                    component=component,
                    query_type="metrics",
                )
                self.storage.save_metrics(
                    component=component,
                    metrics=metrics.metrics,
                    health_status=metrics.health,
                    score=None,
                )

            # 渲染文本报告
            report_text = await self.renderer.render_text({
                "component": metrics.component,
                "health": metrics.health,
                "metrics": metrics.metrics,
            })

            # 发送结果
            yield event.plain_result(report_text)

        except Exception as e:
            logger.error(f"分析组件 {component} 时出错：{e}")
            yield event.plain_result(f"❌ 分析失败：{str(e)}")

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
        if not self.service:
            yield event.plain_result("❌ 服务未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        try:
            # 获取健康状态
            health = await self.service.get_health_status(component)

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
                "component": health.component,
                "status": health.status,
                "score": health.score,
                "issues": health.issues,
                "recommendations": health.recommendations,
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
        if not self.service:
            yield event.plain_result("❌ 服务未初始化")
            return

        if not self.renderer:
            yield event.plain_result("❌ 渲染器未初始化")
            return

        try:
            # 获取汇总信息
            summary = await self.service.get_all_components_summary()

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
📊 BigDataOps 大数据分析助手

可用命令:
  /bigdata <组件名>     - 查看组件详细指标
  /bigdata-status <组件> - 查看组件健康状态
  /bigdata-summary      - 查看所有组件汇总
  /bigdata-help         - 显示此帮助信息

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

示例:
  /bigdata spark
  /bigdata-status hadoop
  /bigdata-summary

💡 提示：首次使用请在配置中设置 API 端点地址
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

        # 清理服务资源
        if self.service:
            await self.service.close()

        logger.info("BigDataOps 插件已停止")

        await super().terminate()
