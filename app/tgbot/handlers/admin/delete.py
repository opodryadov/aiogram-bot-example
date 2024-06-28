# isort:skip_file
from operator import attrgetter, itemgetter
from typing import Dict

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Cancel,
    Next,
    Row,
    ScrollingGroup,
    Select,
)
from aiogram_dialog.widgets.text import Const, Format, Multi

from app.infrastructure.database.repositories import Repository
from app.tgbot.handlers.admin.common import (
    chat_id_selection,
    enable_send_mode,
    get_chat,
    get_result,
)
from app.tgbot.lexicon.lexicon_ru import LEXICON
from app.tgbot.states import DeleteChat


chat_deleting_process = Multi(
    Format(f"{LEXICON['chat_id']}: {{{'chat_id'}}}", when="chat_id"),
    Format(f"{LEXICON['chat_title']}: {{{'chat_title'}}}", when="chat_title"),
)


async def delete_chat_yes_no(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    if item_id == "No":
        await callback.answer(LEXICON["chat_deleting_canceled"])
        await dialog_manager.back()
        return

    repository: Repository = dialog_manager.middleware_data.get("repository")
    data = dialog_manager.current_context().dialog_data

    await repository.chat.delete_chat(data["selected_chat"])

    data["result"] = LEXICON["chat_deleting_success"].format(
        data["selected_chat"]
    )

    await dialog_manager.next()
    await callback.answer()


async def get_all_chats(
    dialog_manager: DialogManager, repository: Repository, **kwargs
) -> Dict:
    chats = await repository.chat.get_all_chats()
    return {"chats": chats}


delete_chat_dialog = Dialog(
    Window(
        Const(LEXICON["select_chat_for_deleting"]),
        ScrollingGroup(
            Select(
                Format("{item.chat_id} {item.chat_title}"),
                id="selected_chat",
                item_id_getter=attrgetter("chat_id"),
                items="chats",
                on_click=chat_id_selection,
            ),
            id="chat_scrolling",
            width=1,
            height=10,
        ),
        Cancel(Const(LEXICON["cancel"])),
        getter=get_all_chats,
        state=DeleteChat.select_chat,
        preview_add_transitions=[Next()],
    ),
    Window(
        Format(
            LEXICON["confirm_delete"].format(
                "{chat.chat_id}", "{chat.chat_title}"
            )
        ),
        Select(
            Format("{item[0]}"),
            id="delete_yes_no",
            item_id_getter=itemgetter(1),
            items=[(LEXICON["yes"], "Yes"), (LEXICON["no"], "No")],
            on_click=delete_chat_yes_no,
        ),
        Row(Back(Const(LEXICON["back"])), Cancel(Const(LEXICON["cancel"]))),
        getter=get_chat,
        state=DeleteChat.confirm,
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("{result}"),
        Cancel(Const(LEXICON["go_to_main_menu"]), on_click=enable_send_mode),
        getter=get_result,
        state=DeleteChat.result,
        parse_mode="HTML",
    ),
)
