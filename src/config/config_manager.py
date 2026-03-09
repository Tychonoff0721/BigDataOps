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

    # ========== 测试模式配置 ==========

    def is_test_mode(self) -> bool:
        """检查是否启用测试模式（使用 Mock 数据）。"""
        return self._config.get("test_mode", True)

    # ========== 大模型 API 配置 ==========

    def get_llm_api_url(self) -> str:
        """获取大模型 API 地址。"""
        return self._config.get("llm_api_url", "https://api.openai.com/v1/chat/completions")

    def get_llm_api_key(self) -> str:
        """获取大模型 API Key。"""
        return self._config.get("llm_api_key", "")

    def get_llm_model(self) -> str:
        """获取大模型名称。"""
        return self._config.get("llm_model", "gpt-3.5-turbo")

    def get_llm_max_tokens(self) -> int:
        """获取大模型最大 token 数。"""
        return self._config.get("llm_max_tokens", 2000)

    def get_llm_temperature(self) -> float:
        """获取大模型温度参数。"""
        return self._config.get("llm_temperature", 0.7)

    # ========== 大数据组件 API 配置 ==========

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

    def get_component_endpoints(self) -> dict[str, str]:
        """
        获取各组件的 API 端点配置。

        Returns:
            组件名称到端点 URL 的映射字典
        """
        return self._config.get("component_endpoints", {})
