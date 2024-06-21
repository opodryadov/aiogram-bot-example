from aiogram import Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.tgbot.middlewares.chat import ChatMiddleware
from app.tgbot.middlewares.database import DatabaseMiddleware
from app.tgbot.middlewares.logging import LoggingMiddleware


def setup_middlewares(dp: Dispatcher, sessionmaker: async_sessionmaker):
    dp.update.outer_middleware(LoggingMiddleware())
    dp.update.outer_middleware(DatabaseMiddleware(session_pool=sessionmaker))
    dp.update.outer_middleware(ChatMiddleware())
