from aiogram import Dispatcher

from app.tgbot.handlers.chat.start import register_start


def register_chat_handlers(dp: Dispatcher):
    register_start(dp)
