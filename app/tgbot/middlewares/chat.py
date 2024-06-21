from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Chat, Update, User

from app.infrastructure.database.models.chat import ChatModel
from app.infrastructure.database.repositories import Repository


class ChatMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        event_from_user: Optional[User] = data.get("event_from_user")
        event_chat: Optional[Chat] = data.get("event_chat")
        if not event_from_user or not event_chat or event_from_user.is_bot:
            return await handler(event, data)

        from_chat_id = event_chat.id
        chat_type = event_chat.type

        if chat_type == "private":
            chat_title = " ".join(
                filter(None, [event_chat.first_name, event_chat.last_name])
            )
        else:
            chat_title = event_chat.title

        repository: Repository = data.get("repository")
        chat: Optional[ChatModel] = await repository.chat.get_chat(
            chat_id=from_chat_id
        )
        if not chat:
            chat = await repository.chat.add_chat(
                chat_id=from_chat_id,
                chat_title=chat_title,
                chat_type=chat_type
            )

        data["chat"] = chat
        data["event_attrs"].update(
            {
                "chat_id": from_chat_id,
                "chat_title": chat_title,
                "chat_type": chat_type,
                "user_phone_number": chat.phone,
                "user_email": chat.email,
                "user_role": chat.role.value,
            }
        )

        return await handler(event, data)
