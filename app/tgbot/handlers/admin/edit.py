# isort:skip_file
import re
import json
from datetime import datetime
from operator import attrgetter, itemgetter
from typing import Any, Dict

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    Next,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger

from app.infrastructure.database.exceptions import DataDuplicationError
from app.infrastructure.database.models import ChatModel
from app.infrastructure.database.repositories import Repository
from app.tgbot.handlers.admin.common import (
    chat_id_selection,
    copy_start_data_to_context,
    enable_send_mode,
    get_chats,
    get_chat_data,
    get_chat_fields,
    get_result,
    if_access_until_is_unlimited,
    if_empty_commentary,
)
from app.tgbot.lexicon.lexicon_ru import LEXICON
from app.tgbot.states import (
    EditAccessUntil,
    EditChat,
    EditChatId,
    EditChatTitle,
    EditCommentary,
    EditEmail,
    EditPhone,
)


def if_changes(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    fields = [
        "chat_id",
        "chat_title",
        "phone",
        "email",
        "commentary",
        "access_until",
    ]
    return any(
        field in dialog_manager.current_context().dialog_data
        for field in fields
    )


chat_editing_process = Multi(
    Format(LEXICON["unsaved_changes"], when=if_changes),
    Format(f"{LEXICON['chat_id']}: {{{'chat_id'}}}", when="chat_id"),
    Format(f"{LEXICON['chat_title']}: {{{'chat_title'}}}", when="chat_title"),
    Format(f"{LEXICON['phone']}: {{{'phone'}}}", when="phone"),
    Format(f"{LEXICON['email']}: {{{'email'}}}", when="email"),
    Format(f"{LEXICON['commentary']}: {{{'commentary'}}}", when="commentary"),
    Format(
        f"{LEXICON['commentary']}: {LEXICON['empty_commentary']}",
        when=if_empty_commentary,
    ),
    Format(
        f"{LEXICON['access_until']}: до {{{'access_until'}}}",
        when="access_until",
    ),
    Format(
        f"{LEXICON['access_until']}: {LEXICON['unlimited']}",
        when=if_access_until_is_unlimited,
    ),
)


async def field_selection(
    callback: CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    column_states = {
        ChatModel.chat_id.key: EditChatId.request,
        ChatModel.chat_title.key: EditChatTitle.request,
        ChatModel.phone.key: EditPhone.request,
        ChatModel.email.key: EditEmail.request,
        ChatModel.commentary.key: EditCommentary.request,
        ChatModel.access_until.key: EditAccessUntil.request,
    }

    await dialog_manager.start(
        state=column_states[item_id],
        data=dialog_manager.current_context().dialog_data.copy(),
    )
    await callback.answer()


async def get_old_chat(
    dialog_manager: DialogManager, repository: Repository, **kwargs
) -> Dict:
    chat_id = dialog_manager.current_context().dialog_data["selected_chat"]
    chat = await repository.chat.get_chat(chat_id)

    return {"chat": chat}


async def get_chat_edit_data(
    dialog_manager: DialogManager,
    repository: Repository,
    **kwargs,
) -> Dict:
    chat_id = dialog_manager.current_context().dialog_data["selected_chat"]
    chat = await repository.chat.get_chat(chat_id)
    data = json.dumps(
        chat.object_as_dict(), default=lambda x: str(x), ensure_ascii=False
    )
    dialog_manager.current_context().dialog_data["chat"] = json.loads(data)
    fields = get_chat_fields()
    if chat.chat_type in ["group", "supergroup", "channel"]:
        fields.remove((LEXICON["phone_button"], "phone"))
        fields.remove((LEXICON["email_button"], "email"))

    chat_data = await get_chat_data(dialog_manager)

    return {"chat": chat, "fields": fields} | chat_data


async def request_chat_id(
    message: Message,
    widget: MessageInput,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    if (
        int(message.text)
        == dialog_manager.current_context().dialog_data["chat"]["chat_id"]
    ):
        await message.answer(LEXICON["same_value_error"])
        return
    if dialog_manager.current_context().dialog_data["chat"]["chat_type"] in [
        "group",
        "supergroup",
        "channel",
    ]:
        if not message.text.startswith("-"):
            await message.answer(LEXICON["request_group_chat_id_error"])
            return
    if not re.match(pattern="^-?\\d+$", string=message.text):
        await message.answer(LEXICON["request_chat_id_error"])
        return

    await dialog_manager.done({"chat_id": message.text})


async def request_chat_title(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if (
        message.text
        == dialog_manager.current_context().dialog_data["chat"]["chat_title"]
    ):
        await message.answer(LEXICON["same_value_error"])
        return
    if len(message.text) > 128:
        await message.answer(LEXICON["request_chat_title_error"])
        return

    await dialog_manager.done({"chat_title": message.text})


async def request_phone(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if (
        message.text
        == dialog_manager.current_context().dialog_data["chat"]["phone"]
    ):
        await message.answer(LEXICON["same_value_error"])
        return
    if not re.match(pattern="^79\\d{9}$", string=message.text):
        await message.answer(LEXICON["request_phone_error"])
        return

    await dialog_manager.done({"phone": message.text})


async def request_email(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if (
        message.text
        == dialog_manager.current_context().dialog_data["chat"]["email"]
    ):
        await message.answer(LEXICON["same_value_error"])
        return
    if len(message.text) > 64:
        await message.answer(LEXICON["request_email_error"])
        return

    await dialog_manager.done({"email": message.text})


async def request_commentary(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if (
        message.text
        == dialog_manager.current_context().dialog_data["chat"]["commentary"]
    ):
        await message.answer(LEXICON["same_value_error"])
        return
    if len(message.text) > 256:
        await message.answer(LEXICON["request_commentary_error"])
        return

    await dialog_manager.done({"commentary": message.text})


async def request_access_until(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    try:
        access_until = datetime.strptime(message.text, "%d.%m.%Y")
        if (
            str(access_until)
            == dialog_manager.current_context().dialog_data["chat"][
                "access_until"
            ]
        ):
            await message.answer(LEXICON["same_value_error"])
            return
        if datetime.now() > access_until:
            await message.answer(LEXICON["request_access_until_time_error"])
            return

        await dialog_manager.done({"access_until": str(access_until)})

    except ValueError:
        await message.answer(LEXICON["request_access_until_value_error"])
        return


async def process_result(
    start_data: Data, result: Any, dialog_manager: DialogManager
) -> None:
    if not result:
        return
    if result.get("chat_id"):
        dialog_manager.current_context().dialog_data["chat_id"] = int(
            result["chat_id"]
        )
    if result.get("chat_title"):
        dialog_manager.current_context().dialog_data["chat_title"] = result[
            "chat_title"
        ]
    if result.get("phone"):
        dialog_manager.current_context().dialog_data["phone"] = result["phone"]
    if result.get("email"):
        dialog_manager.current_context().dialog_data["email"] = result["email"]
    if result.get("commentary"):
        dialog_manager.current_context().dialog_data["commentary"] = result[
            "commentary"
        ]
    if result.get("access_until"):
        dialog_manager.current_context().dialog_data["access_until"] = result[
            "access_until"
        ]


async def set_unlimited_access(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    dialog_manager.current_context().dialog_data["access_until"] = None


async def delete_commentary(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    dialog_manager.current_context().dialog_data["commentary"] = None


def if_access_until(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    return (
        dialog_manager.current_context().dialog_data["chat"]["access_until"]
        is not None
    )


def if_commentary(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    return (
        dialog_manager.current_context().dialog_data["chat"]["commentary"]
        is not None
    )


async def save_edited_chat(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    **kwargs,
) -> None:
    repository: Repository = dialog_manager.middleware_data.get("repository")
    dialog_data = dialog_manager.current_context().dialog_data

    data: Dict = dict(dialog_data)

    access_until = data.get("access_until", None)
    if access_until is not None:
        data["access_until"] = datetime.strptime(
            data["access_until"], "%Y-%m-%d %H:%M:%S"
        )

    try:
        changes = if_changes(data, button, dialog_manager)
        if not changes:
            dialog_data["result"] = LEXICON["nothing_to_change"]
        else:
            await repository.chat.edit_chat(
                chat_id=data["selected_chat"], data=data
            )
            dialog_data["result"] = LEXICON["chat_editing_success"].format(
                data["selected_chat"]
            )
    except DataDuplicationError as err:
        logger.error(err)
        dialog_data["result"] = LEXICON["data_duplication_error"]
    finally:
        key = repository.chat.storage.get_key(data["selected_chat"])
        await repository.chat.storage.delete(key=key)

        await dialog_manager.next()
        await callback.answer()


edit_chat_id_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_chat_id"]),
        MessageInput(request_chat_id),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditChatId.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_chat_title_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_chat_title"]),
        MessageInput(request_chat_title),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditChatTitle.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_phone_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_phone"]),
        MessageInput(request_phone),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditPhone.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_email_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_email"]),
        MessageInput(request_email),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditEmail.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_commentary_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_commentary"]),
        MessageInput(request_commentary),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditCommentary.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_access_until_dialog = Dialog(
    Window(
        Format(LEXICON["input_new_access_until"]),
        MessageInput(request_access_until),
        Cancel(Const(LEXICON["back"])),
        getter=get_old_chat,
        state=EditAccessUntil.request,
    ),
    on_start=copy_start_data_to_context,
)

edit_chat_dialog = Dialog(
    Window(
        Const(LEXICON["select_chat_for_editing"]),
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
        getter=get_chats,
        state=EditChat.select_chat,
        preview_add_transitions=[Next()],
    ),
    Window(
        Multi(
            Format(
                LEXICON["selected_chat"].format(
                    "{chat.chat_id}",
                    "{chat.chat_title}",
                    "{chat.phone}",
                    "{chat.email}",
                    "{chat.commentary}",
                    "{chat.access_until}",
                )
            ),
            chat_editing_process,
        ),
        Column(
            Select(
                Format("{item[0]}"),
                id="field",
                item_id_getter=itemgetter(1),
                items="fields",
                on_click=field_selection,
            ),
            Button(
                Const(LEXICON["delete_commentary"]),
                id="delete_commentary",
                on_click=delete_commentary,
                when=if_commentary,
            ),
            Button(
                Const(LEXICON["set_unlimited_access"]),
                id="unlimited_access",
                on_click=set_unlimited_access,
                when=if_access_until,
            ),
            Button(
                Const(LEXICON["save"]), id="save", on_click=save_edited_chat
            ),
            Cancel(Const(LEXICON["cancel"])),
        ),
        getter=get_chat_edit_data,
        state=EditChat.select_field,
        parse_mode="HTML",
        preview_add_transitions=[
            SwitchTo(Const(""), id="", state=EditChatId.request),
            SwitchTo(Const(""), id="", state=EditChatTitle.request),
            SwitchTo(Const(""), id="", state=EditPhone.request),
            SwitchTo(Const(""), id="", state=EditEmail.request),
            SwitchTo(Const(""), id="", state=EditCommentary.request),
            SwitchTo(Const(""), id="", state=EditAccessUntil.request),
            Next(),
        ],
    ),
    Window(
        Format("{result}"),
        Cancel(Const(LEXICON["close"]), on_click=enable_send_mode),
        getter=get_result,
        state=EditChat.result,
        parse_mode="HTML",
    ),
    on_process_result=process_result,
)
