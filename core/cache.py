"""
Cache - Provides caching functionality for the FinConnectAI framework.

This module implements caching mechanisms to improve performance by storing
frequently accessed data in memory or using external caching systems.
"""

import functools
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CacheEntry:
    """
    Cache entry with expiration.

    This class represents a cache entry with a value and expiration time.
    """

    def __init__(self, value: Any, ttl: int = 300):
        """
        Initialize a cache entry.

        Args:
            value: The cached value
            ttl: Time to live in seconds
        """
        self.value = value
        self.expiration = datetime.now() + timedelta(seconds=ttl)

    def is_expired(self) -> bool:
        """
        Check if the cache entry is expired.

        Returns:
            True if the entry is expired, False otherwise
        """
        return datetime.now() > self.expiration


class MemoryCache:
    """
    In-memory cache implementation.

    This class implements a simple in-memory cache with expiration.
    """

    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        """
        Initialize an in-memory cache.

        Args:
            default_ttl: Default time to live in seconds
            max_size: Maximum number of entries in the cache
        """
        self.cache = {}
        self.default_ttl = default_ttl
        self.max_size = max_size

        logger.info(f"Initialized in-memory cache with TTL: {default_ttl}s, max size: {max_size}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if not found or expired
        """
        if key not in self.cache:
            return None

        entry = self.cache[key]
        if entry.is_expired():
            self.delete(key)
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Optional time to live in seconds
        """
        # Check if cache is full
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_entries()

        # Set the cache entry
        ttl = ttl if ttl is not None else self.default_ttl
        self.cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            True if the key was deleted, False otherwise
        """
        if key in self.cache:
            del self.cache[key]
            return True

        return False

    def clear(self) -> None:
        """Clear the cache."""
        self.cache.clear()

    def _evict_entries(self) -> None:
        """
        Evict entries from the cache.

        This method evicts expired entries and, if necessary, the oldest entries
        to make room for new entries.
        """
        # First, remove expired entries
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]

        # If still too many entries, remove oldest entries
        if len(self.cache) >= self.max_size:
            # Sort entries by expiration time
            sorted_keys = sorted(self.cache.keys(), key=lambda k: self.cache[k].expiration)

            # Remove oldest entries to get below 90% of max size
            target_size = int(self.max_size * 0.9)
            keys_to_remove = sorted_keys[: len(self.cache) - target_size]

            for key in keys_to_remove:
                del self.cache[key]

        logger.debug(
            f"Evicted {len(expired_keys)} expired entries and {len(self.cache) - self.max_size} oldest entries"
        )


class CacheManager:
    """
    Manager for caching operations.

    This class provides a unified interface for caching operations, supporting
    different cache backends.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize a cache manager.

        Args:
            config: Configuration for the cache manager
        """
        self.config = config
        self.cache_enabled = config.get("cache_enabled", True)
        self.default_ttl = config.get("cache_ttl", 300)
        self.cache_type = config.get("cache_type", "memory")

        # Initialize cache backend
        if self.cache_type == "memory":
            self.cache = MemoryCache(
                default_ttl=self.default_ttl, max_size=config.get("cache_max_size", 1000)
            )
        elif self.cache_type == "redis":
            # In a real implementation, this would use Redis
            # For now, we'll use the in-memory cache
            logger.warning("Redis cache not implemented, using in-memory cache")
            self.cache = MemoryCache(
                default_ttl=self.default_ttl, max_size=config.get("cache_max_size", 1000)
            )
        else:
            logger.warning(f"Unknown cache type: {self.cache_type}, using in-memory cache")
            self.cache = MemoryCache(
                default_ttl=self.default_ttl, max_size=config.get("cache_max_size", 1000)
            )

        logger.info(f"Initialized cache manager with type: {self.cache_type}")

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: The cache key

        Returns:
            The cached value, or None if not found or expired
        """
        if not self.cache_enabled:
            return None

        return self.cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set a value in the cache.

        Args:
            key: The cache key
            value: The value to cache
            ttl: Optional time to live in seconds
        """
        if not self.cache_enabled:
            return

        self.cache.set(key, value, ttl)

    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.

        Args:
            key: The cache key

        Returns:
            True if the key was deleted, False otherwise
        """
        if not self.cache_enabled:
            return False

        return self.cache.delete(key)

    def clear(self) -> None:
        """Clear the cache."""
        if not self.cache_enabled:
            return

        self.cache.clear()

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a cache key from arguments.

        Args:
            prefix: Prefix for the key
            *args: Positional arguments to include in the key
            **kwargs: Keyword arguments to include in the key

        Returns:
            Generated cache key
        """
        # Convert args and kwargs to a string representation
        key_parts = [prefix]

        # Add args
        for arg in args:
            key_parts.append(str(arg))

        # Add kwargs (sorted by key)
        for key in sorted(kwargs.keys()):
            key_parts.append(f"{key}={kwargs[key]}")

        # Join parts and hash
        key_str = ":".join(key_parts)
        hashed_key = hashlib.md5(key_str.encode()).hexdigest()

        return f"{prefix}:{hashed_key}"


def cached(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None,
    cache_manager: Optional[CacheManager] = None,
):
    """
    Decorator for caching function results.

    Args:
        ttl: Optional time to live in seconds
        key_prefix: Optional prefix for the cache key
        cache_manager: Optional cache manager to use

    Returns:
        Decorator function
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching if no cache manager
            if cache_manager is None or not cache_manager.cache_enabled:
                return func(*args, **kwargs)

            # Generate cache key
            prefix = key_prefix or func.__name__
            cache_key = cache_manager.generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key: {cache_key}")
                return cached_value

            # Call function and cache result
            logger.debug(f"Cache miss for key: {cache_key}")
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result, ttl)

            return result

        return wrapper

    return decorator
