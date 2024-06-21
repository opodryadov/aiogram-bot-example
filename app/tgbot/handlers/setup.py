from aiogram import Dispatcher

from app.tgbot.handlers.chat.setup import register_chat_handlers


def register_handlers(dp: Dispatcher):
    register_chat_handlers(dp)
