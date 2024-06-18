from aiogram import Dispatcher
from aiogram.filters.command import CommandStart
from aiogram.fsm.state import any_state
from aiogram.types import Message

from app.config import config
from app.infrastructure.database.models.user import Role
from app.infrastructure.rabbitmq.publishers.telegram import telegram_publisher
from app.tgbot.filters.role import RoleFilter
from app.tgbot.lexicon.lexicon_ru import LEXICON


async def cmd_start_unauthorized_user(message: Message, event_attrs: dict):
    await telegram_publisher.send(
        body=LEXICON["cmd_start_unauthorized_user"].format(
            config.email_support,
            event_attrs.get("chat_id"),
            config.template_link,
        ),
        headers=event_attrs,
    )


def register_start(dp: Dispatcher):
    dp.message.register(
        cmd_start_unauthorized_user,
        CommandStart(),
        any_state,
        RoleFilter(roles=[Role.UNAUTHORIZED]),
    )
