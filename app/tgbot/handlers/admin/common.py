from typing import Dict, List

from aiogram.types import CallbackQuery
from aiogram.utils.text_decorations import html_decoration
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import Button

from app.tgbot.lexicon.lexicon_ru import LEXICON


def get_chat_fields() -> List[tuple]:
    return [
        (LEXICON["chat_id_button"], "chat_id"),
        (LEXICON["chat_title_button"], "chat_title"),
        (LEXICON["phone_button"], "phone"),
        (LEXICON["email_button"], "email"),
        (LEXICON["commentary_button"], "commentary"),
        (LEXICON["access_until_button"], "access_until"),
    ]


async def get_chat_data(dialog_manager: DialogManager, **kwargs) -> Dict:
    dialog_data = dialog_manager.current_context().dialog_data

    return {
        "chat_id": dialog_data.get("chat_id"),
        "chat_title": (
            html_decoration.quote(dialog_data.get("chat_title"))
            if dialog_data.get("chat_title")
            else None
        ),
        "chat_type": dialog_data.get("chat_type"),
        "phone": dialog_data.get("phone"),
        "email": dialog_data.get("email"),
        "commentary": dialog_data.get("commentary"),
        "access_until": dialog_data.get("access_until"),
    }


async def enable_send_mode(
    event: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    dialog_manager.show_mode = ShowMode.SEND


async def copy_start_data_to_context(_, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update(
        dialog_manager.current_context().start_data
    )


async def get_result(dialog_manager: DialogManager, **kwargs):
    return {
        "result": dialog_manager.current_context().dialog_data["result"],
    }


def if_empty_commentary(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    if "commentary" in dialog_manager.current_context().dialog_data:
        if dialog_manager.current_context().dialog_data["commentary"] is None:
            return True

    return False


def if_access_until_is_unlimited(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    if "access_until" in dialog_manager.current_context().dialog_data:
        if (
            dialog_manager.current_context().dialog_data["access_until"]
            is None
        ):
            return True

    return False
