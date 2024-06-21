from aiogram import Dispatcher
from aiogram.filters.command import CommandStart
from aiogram.fsm.state import any_state
from aiogram.types import Message

from app.config import config
from app.infrastructure.database.models.chat import ChatModel, Role
from app.tgbot.filters.role import RoleFilter
from app.tgbot.lexicon.lexicon_ru import LEXICON


async def cmd_start_unauthorized_chat(message: Message, chat: ChatModel):
    await message.answer(
        LEXICON["cmd_start_unauthorized_chat"].format(
            config.email_support, chat.chat_id, config.template_link
        )
    )


def register_start(dp: Dispatcher):
    dp.message.register(
        cmd_start_unauthorized_chat,
        CommandStart(),
        any_state,
        RoleFilter(roles=[Role.UNAUTHORIZED]),
    )
