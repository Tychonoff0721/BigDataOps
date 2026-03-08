"""测试配置管理模块"""

import pytest


class TestConfigManagerBasic:
    """测试配置管理器基本功能。"""

    def test_init_with_config(self):
        """测试使用配置字典初始化。"""
        from src.config import ConfigManager
        
        config_dict = {
            "api_endpoint": "http://localhost:8088",
            "api_username": "admin",
            "api_password": "secret",
            "max_retries": 5,
        }
        
        manager = ConfigManager(config_dict)
        
        assert manager.get_api_endpoint() == "http://localhost:8088"
        assert manager.get_api_username() == "admin"
        assert manager.get_api_password() == "secret"
        assert manager.get_max_retries() == 5

    def test_init_with_empty_config(self):
        """测试使用空配置初始化。"""
        from src.config import ConfigManager
        
        manager = ConfigManager({})
        
        assert manager.get_api_endpoint() == ""
        assert manager.get_max_retries() == 3  # 默认值
        assert manager.get_timeout_seconds() == 30  # 默认值

    def test_get_generic_config_value(self):
        """测试获取通用配置值。"""
        from src.config import ConfigManager
        
        config = {"custom_key": "custom_value"}
        manager = ConfigManager(config)
        
        assert manager.get_config_value("custom_key") == "custom_value"
        assert manager.get_config_value("nonexistent", "default") == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
