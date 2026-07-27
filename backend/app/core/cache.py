"""Simple in-memory TTL cache for frequently accessed data.

Works without Redis. Useful for caching vendor lists, forum posts,
knowledge base queries, and other relatively static data.

Usage:
    from app.core.cache import cached

    @cached(ttl_seconds=300)
    async def get_vendors(db, city=None, ...):
        ...
"""

import time
import asyncio
import functools
import hashlib
import json
from typing import Optional, Callable, Any


class SimpleCache:
    """In-memory cache with TTL expiration."""

    def __init__(self):
        self._store: dict[str, tuple[float, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache. Returns None if expired or missing."""
        async with self._lock:
            if key in self._store:
                expires_at, value = self._store[key]
                if time.time() < expires_at:
                    return value
                del self._store[key]
        return None

    async def set(self, key: str, value: Any, ttl_seconds: int = 300) -> None:
        """Store a value with TTL."""
        async with self._lock:
            self._store[key] = (time.time() + ttl_seconds, value)

    async def invalidate(self, key: str) -> None:
        """Remove a specific key from cache."""
        async with self._lock:
            self._store.pop(key, None)

    async def invalidate_pattern(self, pattern: str) -> None:
        """Remove all keys matching a prefix pattern."""
        async with self._lock:
            keys_to_remove = [k for k in self._store if k.startswith(pattern)]
            for k in keys_to_remove:
                del self._store[k]

    async def clear(self) -> None:
        """Clear all cached entries."""
        async with self._lock:
            self._store.clear()

    def stats(self) -> dict:
        """Return cache statistics."""
        total = len(self._store)
        valid = sum(1 for exp, _ in self._store.values() if time.time() < exp)
        return {"total_entries": total, "valid_entries": valid, "expired_entries": total - valid}


# Global cache instance
cache = SimpleCache()


def _make_key(prefix: str, *args, **kwargs) -> str:
    """Generate a cache key from function arguments."""
    key_data = json.dumps({"args": str(args), "kwargs": str(kwargs)}, sort_keys=True)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
    return f"{prefix}:{key_hash}"


def cached(ttl_seconds: int = 300, prefix: Optional[str] = None):
    """Decorator for caching async function results.

    Args:
        ttl_seconds: Time-to-live in seconds (default 5 minutes).
        prefix: Cache key prefix (defaults to function name).
    """
    def decorator(func: Callable) -> Callable:
        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if 'db' is first arg (can't serialize sessions)
            # Build key from all non-db arguments
            filtered_args = args[1:] if args and hasattr(args[0], 'execute') else args
            key = _make_key(cache_prefix, *filtered_args, **kwargs)

            # Try cache
            result = await cache.get(key)
            if result is not None:
                return result

            # Execute and cache
            result = await func(*args, **kwargs)
            if result is not None:
                await cache.set(key, result, ttl_seconds)
            return result

        # Expose cache control methods on the wrapped function
        wrapper.cache_invalidate = lambda: cache.invalidate_pattern(cache_prefix)  # type: ignore
        wrapper.cache_clear = cache.clear  # type: ignore
        return wrapper

    return decorator
