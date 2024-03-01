import pickle
from typing import Any

from redis.asyncio import Redis

from app.infrastructure.cache.base import BaseCache
from app.infrastructure.cache.serializer import BaseSerializer


class RedisCacheBase(BaseCache, BaseSerializer):
    cache_prefix: str = None
    default_ttl: int = 600

    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    def get_key(self, *args) -> str:
        params = "::".join([str(arg) for arg in args if arg])
        return f"{self.cache_prefix}::{self.__class__.__name__}::{params}"

    def serialize(self, obj: Any) -> bytes:
        return pickle.dumps(obj)

    def deserialize(self, obj: bytes) -> Any:
        return pickle.loads(obj)

    async def get_from_cache(self, key: str) -> Any | None:
        data = await self.redis.get(key)
        if not data:
            return None

        return self.deserialize(data)

    async def put_to_cache(self, key: str, value: Any) -> None:
        await self.redis.set(
            name=key, value=self.serialize(value), ex=self.default_ttl
        )
