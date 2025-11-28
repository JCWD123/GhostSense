"""
重试机制工具模块
提供通用的网络请求重试功能，增强系统健壮性
"""

import time
from functools import wraps
from typing import Callable, Any, Tuple
import requests
from loguru import logger

# 尝试导入 OpenAI 异常，以便精确捕获
try:
    from openai import APIConnectionError, APITimeoutError, RateLimitError, InternalServerError, APIError
    OPENAI_EXCEPTIONS = (APIConnectionError, APITimeoutError, RateLimitError, InternalServerError, APIError)
except ImportError:
    OPENAI_EXCEPTIONS = ()

class RetryConfig:
    """重试配置类"""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        max_delay: float = 60.0,
        retry_on_exceptions: Tuple = None
    ):
        """
        初始化重试配置
        
        Args:
            max_retries: 最大重试次数
            initial_delay: 初始延迟秒数
            backoff_factor: 退避因子（每次重试延迟翻倍）
            max_delay: 最大延迟秒数
            retry_on_exceptions: 需要重试的异常类型元组
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        
        # 默认需要重试的异常类型
        if retry_on_exceptions is None:
            self.retry_on_exceptions = (
                requests.exceptions.RequestException,
                requests.exceptions.ConnectionError,
                requests.exceptions.HTTPError,
                requests.exceptions.Timeout,
                requests.exceptions.TooManyRedirects,
                ConnectionError,
                TimeoutError,
                Exception  # 兜底捕获一般异常
            ) + OPENAI_EXCEPTIONS
        else:
            self.retry_on_exceptions = retry_on_exceptions

# 默认配置
DEFAULT_RETRY_CONFIG = RetryConfig()

def with_retry(config: RetryConfig = None):
    """
    重试装饰器
    
    Args:
        config: 重试配置，如果不提供则使用默认配置
    
    Returns:
        装饰器函数
    """
    if config is None:
        config = DEFAULT_RETRY_CONFIG
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):  # +1 因为第一次不算重试
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"函数 {func.__name__} 在第 {attempt + 1} 次尝试后成功")
                    return result
                    
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        # 最后一次尝试也失败了
                        logger.error(f"函数 {func.__name__} 在 {config.max_retries + 1} 次尝试后仍然失败")
                        logger.error(f"最终错误: {str(e)}")
                        raise e
                    
                    # 计算延迟时间
                    delay = min(
                        config.initial_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    logger.info(f"将在 {delay:.1f} 秒后进行第 {attempt + 2} 次尝试...")
                    
                    time.sleep(delay)
                
                except Exception as e:
                    # 不在重试列表中的异常，直接抛出
                    logger.error(f"函数 {func.__name__} 遇到不可重试的异常: {str(e)}")
                    raise e
            
            # 这里不应该到达，但作为安全网
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator

def retry_on_network_error(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0
):
    """
    专门用于网络错误的重试装饰器（简化版）
    """
    config = RetryConfig(
        max_retries=max_retries,
        initial_delay=initial_delay,
        backoff_factor=backoff_factor
    )
    return with_retry(config)

class RetryableError(Exception):
    """自定义的可重试异常"""
    pass

def with_graceful_retry(config: RetryConfig = None, default_return=None):
    """
    优雅重试装饰器 - 用于非关键API调用
    失败后不会抛出异常，而是返回默认值，保证系统继续运行
    """
    if config is None:
        config = SEARCH_API_RETRY_CONFIG
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(config.max_retries + 1):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"非关键API {func.__name__} 在第 {attempt + 1} 次尝试后成功")
                    return result
                    
                except config.retry_on_exceptions as e:
                    last_exception = e
                    
                    if attempt == config.max_retries:
                        logger.warning(f"非关键API {func.__name__} 在 {config.max_retries + 1} 次尝试后仍然失败")
                        logger.warning(f"最终错误: {str(e)}")
                        logger.info(f"返回默认值以保证系统继续运行: {default_return}")
                        return default_return
                    
                    delay = min(
                        config.initial_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )
                    
                    logger.warning(f"非关键API {func.__name__} 第 {attempt + 1} 次尝试失败: {str(e)}")
                    logger.info(f"将在 {delay:.1f} 秒后进行第 {attempt + 2} 次尝试...")
                    
                    time.sleep(delay)
                
                except Exception as e:
                    logger.warning(f"非关键API {func.__name__} 遇到不可重试的异常: {str(e)}")
                    logger.info(f"返回默认值以保证系统继续运行: {default_return}")
                    return default_return
            
            return default_return
            
        return wrapper
    return decorator

def make_retryable_request(
    request_func: Callable,
    *args,
    max_retries: int = 5,
    **kwargs
) -> Any:
    """直接执行可重试的请求（不使用装饰器）"""
    config = RetryConfig(max_retries=max_retries)
    
    @with_retry(config)
    def _execute():
        return request_func(*args, **kwargs)
    
    return _execute()

# 预定义重试配置 - 针对不稳定网络优化
LLM_RETRY_CONFIG = RetryConfig(
    max_retries=10,       # 增加重试次数 (原6次)
    initial_delay=5.0,    # 缩短初始延迟 (原60秒)，应对网络抖动
    backoff_factor=1.5,   # 温和退避
    max_delay=120.0       # 最大等待2分钟
)

SEARCH_API_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=2.0,
    backoff_factor=1.6,
    max_delay=25.0
)

DB_RETRY_CONFIG = RetryConfig(
    max_retries=5,
    initial_delay=1.0,
    backoff_factor=1.5,
    max_delay=10.0
)
