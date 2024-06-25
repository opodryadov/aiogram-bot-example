from aiogram import Dispatcher

from app.tgbot.handlers.admin.menu import register_admin_menu


def register_admin_handlers(dp: Dispatcher):
    register_admin_menu(dp)
