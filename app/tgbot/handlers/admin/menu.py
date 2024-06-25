# isort: skip_file
from datetime import datetime
from typing import List

from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.fsm.state import any_state
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from aiogram_dialog import (
    Dialog,
    DialogManager,
    StartMode,
    Window,
    setup_dialogs,
)
from aiogram_dialog.widgets.kbd import Button, Cancel, Start
from aiogram_dialog.widgets.text import Const

from app.infrastructure.common.chats_csv import export_chats_to_csv
from app.infrastructure.database.models.chat import ChatModel, Role
from app.infrastructure.database.repositories import Repository
from app.tgbot.filters.role import RoleFilter
from app.tgbot.handlers.admin.add import add_chat_dialog
from app.tgbot.lexicon.lexicon_ru import LEXICON
from app.tgbot.states import AddChat, AdminMenu, DeleteChat, EditChat


async def export_chats(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
):
    repository: Repository = dialog_manager.middleware_data.get("repository")
    chats: List[ChatModel] = await repository.chat.get_all_chats()

    csv = export_chats_to_csv(chats)
    await callback.message.answer_document(
        BufferedInputFile(
            csv,
            filename=f"chats_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv",
        )
    )


admin_menu_dialog = Dialog(
    Window(
        Const(LEXICON["select_action"]),
        Start(
            Const(LEXICON["add_chat"]),
            id="add_chat",
            state=AddChat.chat_id,
            mode=StartMode.NORMAL,
        ),
        Button(
            Const(LEXICON["export_chats"]),
            id="export_chats",
            on_click=export_chats,
        ),
        Start(
            Const(LEXICON["edit_chat"]),
            id="edit_chat",
            state=EditChat.select_chat,
            mode=StartMode.NORMAL,
        ),
        Start(
            Const(LEXICON["delete_chat"]),
            id="delete_chat",
            state=DeleteChat.select_chat,
            mode=StartMode.NORMAL,
        ),
        Cancel(Const(LEXICON["close"])),
        state=AdminMenu.action,
    ),
)


async def admin_menu_entry(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminMenu.action, mode=StartMode.RESET_STACK)


def register_admin_menu(dp: Dispatcher):
    dp.include_router(admin_menu_dialog)
    dp.include_router(add_chat_dialog)
    dp.message.register(
        admin_menu_entry,
        Command("admin"),
        any_state,
        RoleFilter(roles=[Role.ADMIN]),
    )
    setup_dialogs(dp)
