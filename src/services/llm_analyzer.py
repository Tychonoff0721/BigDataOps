"""大模型分析服务模块

使用 AstrBot 官方 API 调用大语言模型对组件指标进行智能分析和预测。
"""

import json
import time
from typing import Any

from astrbot.api import logger
from astrbot.api.star import Context

from .types import AlertItem, AlertLevel, AnalysisResult, NormalizedMetrics


class LLMAnalyzer:
    """大模型分析器，使用 AstrBot 官方 API 进行智能分析。"""

    def __init__(self, context: Context) -> None:
        """
        初始化大模型分析器。

        Args:
            context: AstrBot 插件上下文，用于调用 llm_generate
        """
        self.context = context

    async def analyze(
        self,
        unified_msg_origin: str,
        component: str,
        raw_metrics: dict[str, Any],
        normalized_metrics: NormalizedMetrics,
    ) -> AnalysisResult:
        """
        分析组件指标并生成诊断报告。

        Args:
            unified_msg_origin: 统一消息来源标识，用于获取 provider_id
            component: 组件名称
            raw_metrics: 原始指标数据
            normalized_metrics: 正则化后的指标数据

        Returns:
            分析结果对象
        """
        # 构建 Prompt
        prompt = self._build_analysis_prompt(component, raw_metrics, normalized_metrics)

        try:
            # 获取当前会话使用的聊天模型 ID
            provider_id = await self.context.get_current_chat_provider_id(
                umo=unified_msg_origin
            )

            if not provider_id:
                logger.warning("未获取到 LLM Provider ID，使用降级分析")
                return self._generate_fallback_analysis(
                    component, raw_metrics, normalized_metrics, "未配置大模型服务"
                )

            # 调用 AstrBot 官方的 LLM API
            logger.info(f"正在调用大模型分析组件 {component}...")
            llm_resp = await self.context.llm_generate(
                chat_provider_id=provider_id,
                prompt=prompt,
            )

            # 解析响应
            response_text = llm_resp.completion_text
            return self._parse_analysis_response(component, response_text)

        except Exception as e:
            logger.error(f"大模型分析失败：{e}")
            return self._generate_fallback_analysis(
                component, raw_metrics, normalized_metrics, str(e)
            )

    def _build_analysis_prompt(
        self,
        component: str,
        raw_metrics: dict[str, Any],
        normalized_metrics: NormalizedMetrics,
    ) -> str:
        """构建分析 Prompt。"""
        # 格式化指标数据
        metrics_text = self._format_metrics_for_prompt(raw_metrics, normalized_metrics)

        prompt = f"""你是一个资深的大数据运维专家，请对以下 {component.upper()} 组件的指标数据进行深入分析。

## 组件信息
- 组件名称: {component.upper()}
- 数据采集时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(normalized_metrics.timestamp))}

## 指标数据
{metrics_text}

## 分析要求

请从以下几个维度进行分析：

1. **整体健康评估**
   - 根据各项指标给出整体健康评分（0-100分）
   - 判断当前状态：healthy（健康）、warning（警告）、critical（严重）、unknown（未知）

2. **指标分析**
   - 分析各项指标的当前状态
   - 识别异常或需要关注的指标
   - 解释指标之间的关系

3. **性能预测**
   - 基于当前指标预测未来可能的性能趋势
   - 评估是否存在资源瓶颈风险

4. **故障风险预测**
   - 识别潜在的故障风险点
   - 评估风险发生的可能性和影响

5. **预警信息**
   - 列出需要关注的预警项
   - 每个预警包含：级别（info/warning/critical/emergency）、指标名称、当前值、阈值、描述、建议

6. **改进建议**
   - 提供具体的优化建议
   - 给出运维操作建议

## 输出格式

请严格按照以下 JSON 格式输出，不要包含任何其他内容：

{{
  "health_score": 85,
  "status": "healthy",
  "summary": "一句话总结当前组件状态",
  "details": [
    "详细分析点1",
    "详细分析点2"
  ],
  "alerts": [
    {{
      "level": "warning",
      "metric_name": "memory_used",
      "current_value": "80%",
      "threshold": "90%",
      "description": "内存使用率较高",
      "suggestion": "建议扩容或优化内存使用"
    }}
  ],
  "performance_prediction": "性能预测分析内容",
  "failure_risks": [
    "风险1：xxx",
    "风险2：xxx"
  ],
  "recommendations": [
    "建议1",
    "建议2"
  ]
}}

请确保输出是有效的 JSON 格式，不要包含 markdown 代码块标记。"""
        return prompt

    def _format_metrics_for_prompt(
        self,
        raw_metrics: dict[str, Any],
        normalized_metrics: NormalizedMetrics,
    ) -> str:
        """格式化指标数据用于 Prompt。"""
        lines = []
        lines.append("| 指标名称 | 原始值 | 正则化值 | 单位 | 说明 |")
        lines.append("|----------|--------|----------|------|------|")

        for key, raw_value in raw_metrics.items():
            if key in ("component", "health"):
                continue

            normalized_value = normalized_metrics.normalized_values.get(key, 0)
            unit = normalized_metrics.units.get(key, "")
            desc = normalized_metrics.descriptions.get(key, key)

            lines.append(
                f"| {key} | {raw_value} | {normalized_value:.2f} | {unit} | {desc} |"
            )

        return "\n".join(lines)

    def _parse_analysis_response(
        self, component: str, response: str
    ) -> AnalysisResult:
        """解析大模型响应。"""
        try:
            # 清理可能的 markdown 代码块标记
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.startswith("```"):
                clean_response = clean_response[3:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            data = json.loads(clean_response.strip())

            # 解析预警列表
            alerts = []
            for alert_data in data.get("alerts", []):
                level_str = alert_data.get("level", "info").lower()
                try:
                    level = AlertLevel(level_str)
                except ValueError:
                    level = AlertLevel.INFO

                alerts.append(
                    AlertItem(
                        level=level,
                        metric_name=alert_data.get("metric_name", ""),
                        current_value=alert_data.get("current_value", ""),
                        threshold=alert_data.get("threshold", ""),
                        description=alert_data.get("description", ""),
                        suggestion=alert_data.get("suggestion", ""),
                    )
                )

            return AnalysisResult(
                component=component.upper(),
                health_score=min(100, max(0, data.get("health_score", 50))),
                status=data.get("status", "unknown"),
                summary=data.get("summary", ""),
                details=data.get("details", []),
                alerts=alerts,
                performance_prediction=data.get("performance_prediction", ""),
                failure_risks=data.get("failure_risks", []),
                recommendations=data.get("recommendations", []),
                timestamp=time.time(),
            )

        except json.JSONDecodeError as e:
            logger.error(f"解析大模型响应失败：{e}")
            # 返回一个基于原始响应的简单结果
            return AnalysisResult(
                component=component.upper(),
                health_score=50,
                status="unknown",
                summary="大模型响应解析失败",
                details=[f"原始响应：{response[:500]}..."],
                alerts=[],
                performance_prediction="无法解析",
                failure_risks=[],
                recommendations=["请检查大模型响应格式"],
                timestamp=time.time(),
            )

    def _generate_fallback_analysis(
        self,
        component: str,
        raw_metrics: dict[str, Any],
        normalized_metrics: NormalizedMetrics,
        error: str,
    ) -> AnalysisResult:
        """生成降级分析结果（当大模型调用失败时）。"""
        alerts: list[AlertItem] = []
        details: list[str] = []
        recommendations: list[str] = []

        # 基于规则的简单分析
        health_score = 100
        status = "healthy"

        # 检查常见问题
        component_lower = component.lower()

        if component_lower == "spark":
            workers = raw_metrics.get("workers", 0)
            active = raw_metrics.get("active_workers", 0)
            if workers > 0 and active < workers:
                health_score -= 20
                alerts.append(
                    AlertItem(
                        level=AlertLevel.WARNING,
                        metric_name="active_workers",
                        current_value=str(active),
                        threshold=str(workers),
                        description=f"有 {workers - active} 个 Worker 节点离线",
                        suggestion="检查离线节点的网络和进程状态",
                    )
                )
                details.append(f"工作节点利用率：{active}/{workers}")

        elif component_lower in ("hadoop", "yarn"):
            nodes_total = raw_metrics.get("nodes_total", 0)
            nodes_active = raw_metrics.get("nodes_active", 0)
            if nodes_total > 0 and nodes_active < nodes_total:
                health_score -= 20
                alerts.append(
                    AlertItem(
                        level=AlertLevel.WARNING,
                        metric_name="nodes_active",
                        current_value=str(nodes_active),
                        threshold=str(nodes_total),
                        description=f"有 {nodes_total - nodes_active} 个节点离线",
                        suggestion="检查离线节点的状态",
                    )
                )

            memory_total = raw_metrics.get("memory_total", 0)
            memory_used = raw_metrics.get("memory_used", 0)
            if memory_total > 0:
                mem_ratio = memory_used / memory_total
                details.append(f"内存使用率：{mem_ratio:.1%}")
                if mem_ratio > 0.9:
                    health_score -= 30
                    alerts.append(
                        AlertItem(
                            level=AlertLevel.CRITICAL,
                            metric_name="memory_used",
                            current_value=f"{mem_ratio:.1%}",
                            threshold="90%",
                            description="内存使用率过高",
                            suggestion="扩容内存或优化资源分配",
                        )
                    )

        elif component_lower == "kafka":
            offline = raw_metrics.get("offline_partitions", 0)
            if offline > 0:
                health_score -= 40
                status = "critical"
                alerts.append(
                    AlertItem(
                        level=AlertLevel.EMERGENCY,
                        metric_name="offline_partitions",
                        current_value=str(offline),
                        threshold="0",
                        description=f"有 {offline} 个分区离线",
                        suggestion="立即检查 Broker 状态和副本同步",
                    )
                )

        elif component_lower == "hdfs":
            corrupt = raw_metrics.get("corrupt_blocks", 0)
            if corrupt > 0:
                health_score -= 50
                status = "critical"
                alerts.append(
                    AlertItem(
                        level=AlertLevel.EMERGENCY,
                        metric_name="corrupt_blocks",
                        current_value=str(corrupt),
                        threshold="0",
                        description=f"有 {corrupt} 个损坏的块",
                        suggestion="立即运行 HDFS fsck 检查并修复",
                    )
                )

        # 确定状态
        if health_score >= 80:
            status = "healthy"
        elif health_score >= 60:
            status = "warning"
        elif health_score >= 40:
            status = "critical"
        else:
            status = "critical"

        recommendations.append("建议配置大模型服务以获得更详细的分析")
        recommendations.append(f"错误信息：{error}")

        return AnalysisResult(
            component=component.upper(),
            health_score=max(0, health_score),
            status=status,
            summary=f"{component.upper()} 组件基础健康检查完成（大模型分析不可用）",
            details=details,
            alerts=alerts,
            performance_prediction="需要大模型支持进行性能预测",
            failure_risks=["大模型分析服务不可用"],
            recommendations=recommendations,
            timestamp=time.time(),
        )
