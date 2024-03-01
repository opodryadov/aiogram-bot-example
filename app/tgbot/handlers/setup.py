from aiogram import Dispatcher

from app.tgbot.handlers.user.setup import register_user_handlers


def register_handlers(dp: Dispatcher):
    register_user_handlers(dp)
