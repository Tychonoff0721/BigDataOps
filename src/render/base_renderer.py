"""基础渲染器模块"""

import asyncio
from abc import ABC, abstractmethod
from typing import Any


class BaseRenderer(ABC):
    """渲染器基类，提供文本和图片渲染的通用接口。"""

    def __init__(self, render_server_url: str | None = None) -> None:
        """
        初始化渲染器。

        Args:
            render_server_url: 远程渲染服务器地址
        """
        self.render_server_url = render_server_url

    @abstractmethod
    async def render_text(self, data: dict[str, Any]) -> str:
        """
        渲染文本报告。

        Args:
            data: 要渲染的数据

        Returns:
            渲染后的文本字符串
        """
        pass

    @abstractmethod
    async def render_image(self, data: dict[str, Any]) -> bytes | None:
        """
        渲染图片报告。

        Args:
            data: 要渲染的数据

        Returns:
            图片二进制数据
        """
        pass

    async def _render_with_rpc(self, template_name: str, data: dict[str, Any]) -> bytes | None:
        """
        使用 RPC 远程渲染服务生成图片。

        Args:
            template_name: 模板名称
            data: 渲染数据

        Returns:
            图片二进制数据
        """
        if not self.render_server_url:
            return None

        try:
            import aiohttp
            
            payload = {
                "template": template_name,
                "data": data,
            }

            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.render_server_url}/render",
                    json=payload,
                ) as response:
                    if response.status == 200:
                        return await response.read()
        except Exception:
            # RPC 渲染失败，返回 None 使用本地渲染
            pass

        return None

    def _format_number(self, num: int | float, suffix: str = "") -> str:
        """
        格式化数字显示。

        Args:
            num: 数字
            suffix: 后缀单位

        Returns:
            格式化后的字符串
        """
        if num >= 1e9:
            return f"{num / 1e9:.1f}B{suffix}"
        elif num >= 1e6:
            return f"{num / 1e6:.1f}M{suffix}"
        elif num >= 1e3:
            return f"{num / 1e3:.1f}K{suffix}"
        else:
            return f"{num}{suffix}"

    def _get_health_emoji(self, health: str) -> str:
        """
        获取健康状态对应的 Emoji。

        Args:
            health: 健康状态 (healthy, warning, critical, unknown)

        Returns:
            Emoji 字符串
        """
        emoji_map = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "❌",
            "unhealthy": "❌",
            "unknown": "❓",
        }
        return emoji_map.get(health, "❓")

    def _get_health_color(self, health: str) -> str:
        """
        获取健康状态对应的颜色。

        Args:
            health: 健康状态

        Returns:
            颜色名称
        """
        color_map = {
            "healthy": "🟢",
            "warning": "🟡",
            "critical": "🔴",
            "unhealthy": "🔴",
            "unknown": "⚪",
        }
        return color_map.get(health, "⚪")
