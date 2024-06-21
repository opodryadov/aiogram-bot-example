import asyncio

from loguru import logger

from app.config import config
from app.infrastructure.database.db import sa_sessionmaker
from app.infrastructure.logging import setup_logging
from app.tgbot.dispatcher import bot, dp
from app.tgbot.handlers import register_handlers
from app.tgbot.middlewares import setup_middlewares
from app.tgbot.services.set_menu import set_main_menu


async def on_startup() -> None:
    logger.info("Starting bot '%s'..." % config.bot.name)

    session_factory = sa_sessionmaker(config.db, enable_logging=config.debug)
    register_handlers(dp=dp)
    setup_middlewares(dp=dp, sessionmaker=session_factory)
    await set_main_menu(bot=bot)

    logger.info("Bot '%s' started!" % config.bot.name)


async def on_shutdown() -> None:
    logger.info("Bot '%s' stopping..." % config.bot.name)

    await bot.session.close()


async def main() -> None:
    setup_logging()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot '%s' stopped!" % config.bot.name)
