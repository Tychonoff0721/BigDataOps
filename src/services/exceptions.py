"""异常定义模块"""


class BigDataError(Exception):
    """大数据插件基础异常类。"""

    pass


class BigDataAPIError(BigDataError):
    """API 请求错误。"""

    pass


class BigDataRateLimitError(BigDataAPIError):
    """API 限流错误。"""

    pass


class ComponentNotFoundError(BigDataError):
    """组件未找到错误。"""

    pass


class MetricsCollectionError(BigDataError):
    """指标收集错误。"""

    pass


class CacheError(BigDataError):
    """缓存操作错误。"""

    pass
