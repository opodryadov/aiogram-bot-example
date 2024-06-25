from aiogram.utils.text_decorations import html_decoration
from aiogram_dialog import DialogManager


async def get_chat_data(dialog_manager: DialogManager, **kwargs) -> dict:
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
