from aiogram import Dispatcher

from app.tgbot.handlers.admin.setup import register_admin_handlers
from app.tgbot.handlers.chat.setup import register_chat_handlers


def register_handlers(dp: Dispatcher):
    register_admin_handlers(dp)
    register_chat_handlers(dp)
