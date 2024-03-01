from typing import Any, Awaitable, Callable, Dict, Optional

from aiogram import BaseMiddleware
from aiogram.types import Chat, Update, User

from app.infrastructure.database.models.user import UserModel
from app.infrastructure.database.repositories import Repository


class UserMiddleware(BaseMiddleware):
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

        if event_chat.type == "private":
            chat_title = " ".join(
                filter(None, [event_chat.first_name, event_chat.last_name])
            )
        else:
            chat_title = event_chat.title

        repository: Repository = data.get("repository")
        user: Optional[UserModel] = await repository.user.get_user(
            chat_id=from_chat_id
        )
        if not user:
            user = await repository.user.add_user(
                chat_id=from_chat_id, chat_title=chat_title
            )

        data["user"] = user

        return await handler(event, data)
