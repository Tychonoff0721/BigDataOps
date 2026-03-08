"""配置管理器模块"""

from typing import Any


class ConfigManager:
    """配置管理器类，用于管理和访问插件配置。"""

    def __init__(self, config: dict[str, Any]) -> None:
        """
        初始化配置管理器。

        Args:
            config: 配置字典
        """
        self._config = config

    def get_api_endpoint(self) -> str:
        """获取大数据组件 API 端点地址。"""
        return self._config.get("api_endpoint", "")

    def get_api_username(self) -> str:
        """获取 API 用户名。"""
        return self._config.get("api_username", "")

    def get_api_password(self) -> str:
        """获取 API 密码。"""
        return self._config.get("api_password", "")

    def get_max_retries(self) -> int:
        """获取最大重试次数。"""
        return self._config.get("max_retries", 3)

    def get_timeout_seconds(self) -> int:
        """获取请求超时时间（秒）。"""
        return self._config.get("timeout_seconds", 30)

    def is_cache_enabled(self) -> bool:
        """检查是否启用缓存。"""
        return self._config.get("cache_enabled", True)

    def get_cache_ttl_seconds(self) -> int:
        """获取缓存过期时间（秒）。"""
        return self._config.get("cache_ttl_seconds", 300)

    def get_proxy_http(self) -> str:
        """获取代理地址。"""
        return self._config.get("proxy_http", "")

    def get_port(self) -> str:
        """获取代理端口。"""
        return self._config.get("port", "")

    def get_render_server_url(self) -> str:
        """获取渲染服务器地址。"""
        return self._config.get("render_server_url", "")

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        获取任意配置值。

        Args:
            key: 配置键名
            default: 默认值

        Returns:
            配置值
        """
        return self._config.get(key, default)
