from app.config import config
from app.infrastructure.cache.redis import RedisCacheBase


class ChatRedisStorage(RedisCacheBase):
    cache_prefix = "Chat"
    default_ttl = config.redis.cache_expires
