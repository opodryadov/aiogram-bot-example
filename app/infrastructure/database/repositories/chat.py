# isort:skip_file
from typing import Dict, Optional, Sequence

from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import select

from app.infrastructure.cache.storages import ChatRedisStorage
from app.infrastructure.database.exceptions import (
    ChatIdAlreadyExists,
    DataDuplicationError,
)
from app.infrastructure.database.models.chat import ChatModel, Role
from app.infrastructure.database.repositories.base import BaseRepository
from app.tgbot.dispatcher import redis


class ChatRepository(BaseRepository):
    storage: ChatRedisStorage = ChatRedisStorage(redis=redis)

    async def set_chat_auth(self, chat: ChatModel) -> None:
        chat.role = Role.AUTHORIZED
        await self.commit()

    async def add_chat(
        self, chat_id: int, chat_title: str, chat_type: str
    ) -> ChatModel:
        try:
            new_chat: ChatModel = ChatModel(
                chat_id=chat_id, chat_title=chat_title, chat_type=chat_type
            )
            await self.commit(new_chat)
            return new_chat
        except IntegrityError as err:
            raise ChatIdAlreadyExists(
                f"Chat with id {chat_id} already exists in database"
            ) from err

    async def get_chat(self, chat_id: int) -> Optional[ChatModel]:
        key = self.storage.get_key(chat_id)
        chat: Optional[ChatModel] = await self.storage.get_from_cache(key)
        if chat:
            return chat

        chat = await self.session.scalar(
            select(ChatModel).where(ChatModel.chat_id == chat_id)
        )
        await self.storage.put_to_cache(key=key, value=chat)

        return chat

    async def edit_chat(self, chat_id: int, data: Dict) -> ChatModel:
        chat: ChatModel = await self.session.scalar(
            select(ChatModel).where(ChatModel.chat_id == chat_id)
        )

        try:
            for key, value in data.items():
                setattr(chat, key, value)
            await self.commit()
        except IntegrityError as err:
            raise DataDuplicationError(
                "Chat id or phone or email already exists in database"
            ) from err

        return chat

    async def get_all_chats(self) -> Sequence[ChatModel]:
        chats = await self.session.scalars(select(ChatModel))
        return chats.all()

    async def get_all_auth_chats(self) -> Sequence[ChatModel]:
        auth_chats = await self.session.scalars(
            select(ChatModel).where(ChatModel.role != Role.UNAUTHORIZED)
        )
        return auth_chats.all()
