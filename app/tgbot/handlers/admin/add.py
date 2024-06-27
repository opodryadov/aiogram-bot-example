# isort:skip_file
import re
from datetime import datetime
from operator import itemgetter
from typing import Dict, Optional

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.common import Whenable
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row, Select
from aiogram_dialog.widgets.text import Const, Format, Multi
from loguru import logger

from app.infrastructure.database.exceptions import DataDuplicationError
from app.infrastructure.database.models.chat import ChatModel, Role
from app.infrastructure.database.repositories import Repository
from app.tgbot.handlers.admin.common import (
    enable_send_mode,
    get_chat_data,
    if_access_until_is_unlimited,
    if_empty_commentary,
)
from app.tgbot.lexicon.lexicon_ru import LEXICON
from app.tgbot.states import AddChat


chat_adding_process = Multi(
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


async def switch_to_chat_title(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    await dialog_manager.switch_to(state=AddChat.chat_title)


async def switch_to_commentary(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    await dialog_manager.switch_to(state=AddChat.commentary)


async def skip_input_commentary(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.current_context().dialog_data["commentary"] = None
    await dialog_manager.next()


async def skip_input_access_until(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.current_context().dialog_data["access_until"] = None
    await dialog_manager.next()


async def request_chat_id(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if not re.match(pattern="^-?\\d+$", string=message.text):
        await message.answer(LEXICON["request_chat_id_error"])
        return

    chat_id = int(message.text)
    repository: Repository = dialog_manager.middleware_data.get("repository")
    chat: Optional[ChatModel] = await repository.chat.get_chat(chat_id=chat_id)
    if not chat:
        await message.answer(LEXICON["chat_id_not_found"])
        return
    if chat.role in [Role.AUTHORIZED, Role.ADMIN, Role.BLOCKED]:
        await message.answer(LEXICON["chat_already_authorized"])
        return

    dialog_manager.current_context().dialog_data["chat_id"] = chat_id
    dialog_manager.current_context().dialog_data["chat_type"] = chat.chat_type
    await dialog_manager.next()


async def request_chat_title(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if len(message.text) > 128:
        await message.answer(LEXICON["request_chat_title_error"])
        return

    dialog_manager.current_context().dialog_data["chat_title"] = message.text

    if dialog_manager.current_context().dialog_data["chat_type"] == "private":
        await dialog_manager.next()
    else:
        await dialog_manager.switch_to(AddChat.commentary)


async def request_phone(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if not re.match(pattern="^79\\d{9}$", string=message.text):
        await message.answer(LEXICON["request_phone_error"])
        return

    dialog_manager.current_context().dialog_data["phone"] = message.text
    await dialog_manager.next()


async def request_email(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if len(message.text) > 64:
        await message.answer(LEXICON["request_email_error"])
        return

    dialog_manager.current_context().dialog_data["email"] = message.text
    await dialog_manager.next()


async def request_commentary(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    if len(message.text) > 256:
        await message.answer(LEXICON["request_commentary_error"])
        return

    dialog_manager.current_context().dialog_data["commentary"] = message.text
    await dialog_manager.next()


async def request_access_until(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    try:
        access_until = datetime.strptime(message.text, "%d.%m.%Y")
        if datetime.now() > access_until:
            await message.answer(LEXICON["request_access_until_time_error"])
            return

        dialog_manager.current_context().dialog_data["access_until"] = str(
            access_until
        )

        await dialog_manager.next()
    except ValueError:
        await message.answer(LEXICON["request_access_until_value_error"])
        return


async def add_chat_yes_no(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    if item_id == "No":
        await callback.answer(LEXICON["chat_adding_cancelled"])
        await dialog_manager.done()
        return

    repository: Repository = dialog_manager.middleware_data.get("repository")
    dialog_data = dialog_manager.current_context().dialog_data

    data: Dict = dict(dialog_data)
    if "access_until" in data:
        if data["access_until"] is not None:
            data["access_until"] = datetime.strptime(
                data["access_until"], "%Y-%m-%d %H:%M:%S"
            )

    try:
        chat = await repository.chat.edit_chat(
            chat_id=data["chat_id"], data=data
        )
        await repository.chat.set_chat_auth(chat=chat)
        dialog_data["result"] = LEXICON["chat_adding_success"]
    except DataDuplicationError as err:
        logger.error(err)
        dialog_data["result"] = LEXICON["data_duplication_error"]
    finally:
        key = repository.chat.storage.get_key(data["chat_id"])
        await repository.chat.storage.delete(key=key)

        await dialog_manager.next()
        await callback.answer()


async def get_result(dialog_manager: DialogManager, **kwargs) -> Dict:
    return {
        "result": dialog_manager.current_context().dialog_data["result"],
    }


def is_private_chat(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    return (
        dialog_manager.current_context().dialog_data["chat_type"] == "private"
    )


def is_public_chat(
    data: Dict, widget: Whenable, dialog_manager: DialogManager
) -> bool:
    return dialog_manager.current_context().dialog_data["chat_type"] in [
        "group",
        "supergroup",
        "channel",
    ]


add_chat_dialog = Dialog(
    Window(
        chat_adding_process,
        Const(LEXICON["input_chat_id"]),
        MessageInput(func=request_chat_id, content_types=ContentType.TEXT),
        Row(
            Cancel(Const(LEXICON["cancel"])),
            Next(Const(LEXICON["next"]), when="chat_id"),
        ),
        getter=get_chat_data,
        state=AddChat.chat_id,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Format(LEXICON["input_chat_title"]),
        MessageInput(request_chat_title),
        Row(
            Back(Const(LEXICON["back"])),
            Cancel(Const(LEXICON["cancel"])),
            Row(
                Next(Const(LEXICON["next"]), when=is_private_chat),
                Button(
                    text=Const(LEXICON["next"]),
                    id="switch_to_commentary_button",
                    on_click=switch_to_commentary,
                    when=is_public_chat,
                ),
                when="chat_title",
            ),
        ),
        getter=get_chat_data,
        state=AddChat.chat_title,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Format(LEXICON["input_phone"]),
        MessageInput(request_phone),
        Row(
            Back(Const(LEXICON["back"])),
            Cancel(Const(LEXICON["cancel"])),
            Next(Const(LEXICON["next"]), when="phone"),
        ),
        getter=get_chat_data,
        state=AddChat.phone,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Format(LEXICON["input_email"]),
        MessageInput(request_email),
        Row(
            Back(Const(LEXICON["back"])),
            Cancel(Const(LEXICON["cancel"])),
            Next(Const(LEXICON["next"]), when="email"),
        ),
        getter=get_chat_data,
        state=AddChat.email,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Format(LEXICON["input_commentary"]),
        MessageInput(request_commentary),
        Row(
            Back(Const(LEXICON["back"]), when=is_private_chat),
            Button(
                text=Const(LEXICON["back"]),
                id="switch_to_chat_title_button",
                on_click=switch_to_chat_title,
                when=is_public_chat,
            ),
            Cancel(Const(LEXICON["cancel"])),
            Button(
                text=Const(LEXICON["next"]),
                id="skip_input_access_until",
                on_click=skip_input_commentary,
            ),
        ),
        getter=get_chat_data,
        state=AddChat.commentary,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Format(LEXICON["input_access_until"]),
        MessageInput(request_access_until),
        Row(
            Back(Const(LEXICON["back"])),
            Cancel(Const(LEXICON["cancel"])),
            Button(
                text=Const(LEXICON["next"]),
                id="skip_input_access_until",
                on_click=skip_input_access_until,
            ),
        ),
        getter=get_chat_data,
        state=AddChat.access_until,
        parse_mode="HTML",
    ),
    Window(
        chat_adding_process,
        Const(LEXICON["confirm"]),
        Select(
            Format("{item[0]}"),
            id="add_yes_no",
            item_id_getter=itemgetter(1),
            items=[(LEXICON["yes"], "Yes"), (LEXICON["no"], "No")],
            on_click=add_chat_yes_no,
        ),
        Back(Const(LEXICON["back"])),
        getter=get_chat_data,
        state=AddChat.confirm,
        parse_mode="HTML",
        preview_add_transitions=[Next()],
    ),
    Window(
        Format("{result}"),
        Cancel(Const(LEXICON["go_to_main_menu"]), on_click=enable_send_mode),
        getter=get_result,
        state=AddChat.result,
        parse_mode="HTML",
    ),
)
