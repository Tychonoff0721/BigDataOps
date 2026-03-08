"""异步工具函数模块"""

import asyncio
import functools
from typing import Any, Callable, TypeVar

from astrbot.api import logger

T = TypeVar("T")


def async_retry(max_retries: int = 3, delay: float = 1.0):
    """
    异步重试装饰器。

    Args:
        max_retries: 最大重试次数
        delay: 每次重试的延迟（秒）

    Returns:
        装饰后的函数

    Example:
        @async_retry(max_retries=3, delay=2.0)
        async def fetch_data():
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"{func.__name__} 执行失败 (尝试 {attempt + 1}/{max_retries}): {e}"
                        )
                        await asyncio.sleep(delay * (attempt + 1))  # 指数退避
                    else:
                        logger.error(
                            f"{func.__name__} 在 {max_retries} 次尝试后仍然失败：{e}"
                        )
            
            raise last_exception
        
        return wrapper
    
    return decorator
