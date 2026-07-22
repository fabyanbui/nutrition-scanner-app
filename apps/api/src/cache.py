from abc import ABC, abstractmethod
import json

class CacheProvider(ABC):
    @abstractmethod
    async def get(self, key: str) -> str | None:
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        pass

class InMemoryCache(CacheProvider):
    def __init__(self):
        self._cache = {}

    async def get(self, key: str) -> str | None:
        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int = 3600) -> None:
        # TTL not enforced in simple memory cache for MVP
        self._cache[key] = value

_cache_instance = InMemoryCache()

def get_cache() -> CacheProvider:
    # Future: return RedisCache based on settings
    return _cache_instance
