"""测试渲染器模块"""

import pytest


class TestComponentRendererText:
    """测试组件文本渲染器。"""

    @pytest.mark.asyncio
    async def test_render_analyze_report(self):
        """测试渲染分析报告。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        data = {
            "component": "Spark",
            "health": "healthy",
            "metrics": {
                "workers": 10,
                "active_workers": 9,
                "cores": 80,
                "memory": 131072,
                "running_apps": 5,
            },
        }
        
        result = await renderer.render_text(data)
        
        assert "Spark" in result
        assert "健康状态" in result or "HEALTHY" in result
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_render_health_report(self):
        """测试渲染健康报告。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        data = {
            "component": "Hadoop",
            "status": "warning",
            "score": 70,
            "issues": ["有节点离线", "内存使用率过高"],
            "recommendations": ["检查节点状态", "优化资源配置"],
        }
        
        result = await renderer.render_health_text(data)
        
        assert "Hadoop" in result
        assert "健康检查报告" in result
        assert "70" in result
        assert "节点离线" in result

    @pytest.mark.asyncio
    async def test_render_summary_report(self):
        """测试渲染汇总报告。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        data = {
            "total_components": 6,
            "healthy_count": 4,
            "warning_count": 1,
            "critical_count": 1,
            "components": [
                {"name": "SPARK", "status": "healthy", "score": 95},
                {"name": "HADOOP", "status": "warning", "score": 65},
                {"name": "FLINK", "status": "healthy", "score": 90},
            ],
        }
        
        result = await renderer.render_summary_text(data)
        
        assert "大数据组件总览" in result
        assert "组件总数：6" in result
        assert "健康：4" in result


class TestBaseRendererHelpers:
    """测试基础渲染器辅助方法。"""

    def test_format_number_small(self):
        """测试小数字格式化。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._format_number(100) == "100"
        assert renderer._format_number(999) == "999"

    def test_format_number_large(self):
        """测试大数字格式化。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._format_number(1500) == "1.5K"
        assert renderer._format_number(2500000) == "2.5M"
        assert renderer._format_number(3500000000) == "3.5B"

    def test_format_number_with_suffix(self):
        """测试带单位的数字格式化。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._format_number(1024, " MB") == "1.0K MB"
        assert renderer._format_number(5000, " GB") == "5.0K GB"

    def test_health_emoji(self):
        """测试健康状态 Emoji。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._get_health_emoji("healthy") == "✅"
        assert renderer._get_health_emoji("warning") == "⚠️"
        assert renderer._get_health_emoji("critical") == "❌"
        assert renderer._get_health_emoji("unknown") == "❓"

    def test_health_color(self):
        """测试健康状态颜色。"""
        from src.render import ComponentRenderer
        
        renderer = ComponentRenderer()
        
        assert renderer._get_health_color("healthy") == "🟢"
        assert renderer._get_health_color("warning") == "🟡"
        assert renderer._get_health_color("critical") == "🔴"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
