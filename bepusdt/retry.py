"""重试机制"""

import time
import logging
from functools import wraps
from typing import Callable, Tuple, Type
from .exceptions import NetworkError, TimeoutError, ServerError

logger = logging.getLogger(__name__)


def retry_on_error(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (NetworkError, TimeoutError, ServerError)
):
    """重试装饰器
    
    Args:
        max_retries: 最大重试次数，默认 3
        delay: 初始延迟时间（秒），默认 1.0
        backoff: 延迟倍数，默认 2.0（指数退避）
        exceptions: 需要重试的异常类型
    
    Example:
        >>> @retry_on_error(max_retries=3, delay=1.0)
        >>> def api_call():
        ...     return requests.get("https://api.example.com")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        logger.warning(
                            f"请求失败 ({type(e).__name__}: {str(e)})，"
                            f"{current_delay:.1f}秒后重试 ({attempt + 1}/{max_retries})..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"请求失败，已达最大重试次数 ({max_retries})")
            
            raise last_exception
        
        return wrapper
    return decorator
