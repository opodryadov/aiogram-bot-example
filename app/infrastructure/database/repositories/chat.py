from datetime import datetime
from typing import Dict, Optional, Sequence

from sqlalchemy.sql import select

from app.infrastructure.cache.storages import ChatRedisStorage
from app.infrastructure.database.models.chat import ChatModel, Role
from app.infrastructure.database.repositories.base import BaseRepository
from app.tgbot.dispatcher import redis


class ChatRepository(BaseRepository):
    storage: ChatRedisStorage = ChatRedisStorage(redis=redis)

    async def add_chat(
        self, chat_id: int, chat_title: str, chat_type: str
    ) -> ChatModel:
        new_chat: ChatModel = ChatModel(
            chat_id=chat_id, chat_title=chat_title, chat_type=chat_type
        )
        await self.commit(new_chat)
        return new_chat

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

    async def auth_chat(self, data: Dict) -> None:
        chat: ChatModel = await self.session.scalar(
            select(ChatModel).where(ChatModel.chat_id == data["chat_id"])
        )

        for key, value in data.items():
            if key == "access_until":
                value = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")

            setattr(chat, key, value)

        chat.role = Role.AUTHORIZED

        await self.commit()

    async def get_all_chats(self) -> Sequence[ChatModel]:
        chats = await self.session.scalars(select(ChatModel))
        return chats.all()
