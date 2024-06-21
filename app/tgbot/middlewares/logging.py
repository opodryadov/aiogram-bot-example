# isort:skip_file
from typing import Any, Awaitable, Callable
from uuid import uuid4

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, Update
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.logger = logger
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: dict[str, Any],
    ) -> Any:
        event_attrs: dict[str, Any] = {"uuid": uuid4().hex}

        if event.message:
            message: Message = event.message
            if message.from_user:
                event_attrs["chat_id"] = message.chat.id
            if message.text:
                event_attrs["message_type"] = (
                    message.entities[0].type if message.entities else "text"
                )
                event_attrs["message_text"] = message.text
            if message.caption:
                event_attrs["caption"] = message.caption
            if message.video:
                event_attrs["file_type"] = "video"
                event_attrs["file_id"] = message.video.file_id
            if message.photo:
                event_attrs["file_type"] = "photo"
                event_attrs["file_id"] = message.photo[-1].file_id
            if message.document:
                event_attrs["file_type"] = "document"
                event_attrs["file_id"] = message.document.file_id
        elif event.callback_query:
            callback_query: CallbackQuery = event.callback_query
            event_attrs.update(
                {
                    "query_id": callback_query.id,
                    "callback_query_data": callback_query.data,
                    "user_id": callback_query.from_user.id,
                    "inline_message_id": callback_query.inline_message_id,
                }
            )

        data["event_attrs"] = event_attrs

        await handler(event, data)

        self.logger.info("Received %s: %s" % (event.event_type, event_attrs))
