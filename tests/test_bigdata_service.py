"""测试大数据服务模块"""

import pytest


class TestComponentMetricsService:
    """测试组件指标服务。"""

    def test_service_initialization(self):
        """测试服务初始化。"""
        from src.services import BigDataService
        from src.config import ConfigManager
        
        config = {
            "api_endpoint": "http://localhost:8088",
            "max_retries": 3,
            "timeout_seconds": 30,
        }
        config_manager = ConfigManager(config)
        
        service = BigDataService(config_manager=config_manager)
        
        assert service is not None
        assert service.config_manager == config_manager

    def test_get_health_status_healthy(self):
        """测试健康状态获取 - 健康场景。"""
        from src.services.types import HealthStatus
        
        # 模拟健康数据
        health = HealthStatus(
            component="SPARK",
            status="healthy",
            score=95,
            issues=[],
            recommendations=["保持当前配置"],
        )
        
        assert health.status == "healthy"
        assert health.score >= 80
        assert len(health.issues) == 0

    def test_get_health_status_warning(self):
        """测试健康状态获取 - 警告场景。"""
        from src.services.types import HealthStatus
        
        health = HealthStatus(
            component="HADOOP",
            status="warning",
            score=65,
            issues=["有 2 个节点离线"],
            recommendations=["检查离线节点"],
        )
        
        assert health.status == "warning"
        assert 60 <= health.score < 80
        assert len(health.issues) > 0


class TestConfigManager:
    """测试配置管理器。"""

    def test_get_api_endpoint(self):
        """测试获取 API 端点。"""
        from src.config import ConfigManager
        
        config = {"api_endpoint": "http://test:8088"}
        manager = ConfigManager(config)
        
        assert manager.get_api_endpoint() == "http://test:8088"

    def test_get_max_retries(self):
        """测试获取最大重试次数。"""
        from src.config import ConfigManager
        
        config = {"max_retries": 5}
        manager = ConfigManager(config)
        
        assert manager.get_max_retries() == 5

    def test_default_values(self):
        """测试默认值。"""
        from src.config import ConfigManager
        
        config = {}
        manager = ConfigManager(config)
        
        assert manager.get_max_retries() == 3
        assert manager.get_timeout_seconds() == 30
        assert manager.is_cache_enabled() is True


class TestComponentRenderer:
    """测试组件渲染器。"""

    @pytest.mark.asyncio
    async def test_render_text(self):
        """测试文本渲染。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        data = {
            "component": "Spark",
            "health": "healthy",
            "metrics": {
                "workers": 5,
                "cores": 40,
                "memory": 65536,
            },
        }
        
        result = await renderer.render_text(data)
        
        assert "Spark" in result
        assert "workers" in result or "工作节点" in result
        assert isinstance(result, str)

    def test_health_emoji_mapping(self):
        """测试健康状态 Emoji 映射。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._get_health_emoji("healthy") == "✅"
        assert renderer._get_health_emoji("warning") == "⚠️"
        assert renderer._get_health_emoji("critical") == "❌"


class TestExceptions:
    """测试异常处理。"""

    def test_bigdata_api_error(self):
        """测试 API 错误异常。"""
        from src.services.exceptions import BigDataAPIError
        
        error = BigDataAPIError("测试错误")
        
        assert str(error) == "测试错误"
        assert isinstance(error, Exception)

    def test_component_not_found_error(self):
        """测试组件未找到异常。"""
        from src.services.exceptions import ComponentNotFoundError
        
        with pytest.raises(ComponentNotFoundError):
            raise ComponentNotFoundError("组件不存在")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
