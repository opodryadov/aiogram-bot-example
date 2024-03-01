from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from redis.asyncio import ConnectionPool, Redis

from app.config import config


bot = Bot(
    token=config.bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

redis = Redis(
    connection_pool=ConnectionPool(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
    ),
)

storage = RedisStorage(
    redis=redis,
    key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
)

dp = Dispatcher(storage=storage)
