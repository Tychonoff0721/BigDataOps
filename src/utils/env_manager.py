"""环境管理器模块"""

import os
import sys
from pathlib import Path


class EnvManager:
    """环境管理器，用于管理插件运行环境和依赖检查。"""

    def __init__(self, plugin_data_dir: str) -> None:
        """
        初始化环境管理器。

        Args:
            plugin_data_dir: 插件数据目录
        """
        self.plugin_data_dir = Path(plugin_data_dir)
        self.cache_dir = self.plugin_data_dir / "cache"
        
        # 确保目录存在
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """确保必要的目录存在。"""
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def is_playwright_installed(self) -> bool:
        """
        检查 Playwright 是否已安装。

        Returns:
            如果已安装返回 True，否则返回 False
        """
        try:
            import playwright
            return True
        except ImportError:
            return False

    def is_jinja2_installed(self) -> bool:
        """
        检查 Jinja2 是否已安装。

        Returns:
            如果已安装返回 True，否则返回 False
        """
        try:
            import jinja2
            return True
        except ImportError:
            return False

    def get_cache_path(self, filename: str) -> Path:
        """
        获取缓存文件路径。

        Args:
            filename: 文件名

        Returns:
            缓存文件的完整路径
        """
        return self.cache_dir / filename

    def clear_cache(self) -> None:
        """清除所有缓存文件。"""
        if self.cache_dir.exists():
            for file in self.cache_dir.iterdir():
                if file.is_file():
                    file.unlink()

    def get_python_version(self) -> str:
        """
        获取 Python 版本。

        Returns:
            Python 版本字符串
        """
        return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

    def check_requirements(self) -> list[str]:
        """
        检查必需的依赖包。

        Returns:
            缺失的依赖包列表
        """
        missing = []
        
        required_packages = [
            "aiohttp",
            "jinja2",
        ]
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        return missing
