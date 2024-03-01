from app.config import config
from app.infrastructure.cache.redis import RedisCacheBase


class UserRedisStorage(RedisCacheBase):
    cache_prefix = "User"
    default_ttl = config.redis.cache_expires
