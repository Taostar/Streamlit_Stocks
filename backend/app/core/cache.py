from cachetools import TTLCache
from functools import wraps
from typing import Callable, Any
import hashlib
import json


# Cache instances with different TTLs
_holdings_cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes
_performance_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour
_correlation_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour
_exchange_cache = TTLCache(maxsize=100, ttl=86400)  # 1 day
_benchmark_cache = TTLCache(maxsize=100, ttl=86400)  # 1 day


def _make_key(*args, **kwargs) -> str:
    """Create a cache key from function arguments."""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(cache_type: str = "holdings"):
    """
    Decorator for caching function results.

    Args:
        cache_type: Type of cache to use ('holdings', 'performance', 'correlation', 'exchange', 'benchmark')
    """
    cache_map = {
        "holdings": _holdings_cache,
        "performance": _performance_cache,
        "correlation": _correlation_cache,
        "exchange": _exchange_cache,
        "benchmark": _benchmark_cache,
    }

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            cache = cache_map.get(cache_type, _holdings_cache)
            key = f"{func.__name__}:{_make_key(*args, **kwargs)}"

            if key in cache:
                return cache[key]

            result = await func(*args, **kwargs)
            cache[key] = result
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            cache = cache_map.get(cache_type, _holdings_cache)
            key = f"{func.__name__}:{_make_key(*args, **kwargs)}"

            if key in cache:
                return cache[key]

            result = func(*args, **kwargs)
            cache[key] = result
            return result

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def clear_cache(cache_type: str = None):
    """Clear specified cache or all caches if no type specified."""
    cache_map = {
        "holdings": _holdings_cache,
        "performance": _performance_cache,
        "correlation": _correlation_cache,
        "exchange": _exchange_cache,
        "benchmark": _benchmark_cache,
    }

    if cache_type:
        if cache_type in cache_map:
            cache_map[cache_type].clear()
    else:
        for cache in cache_map.values():
            cache.clear()
