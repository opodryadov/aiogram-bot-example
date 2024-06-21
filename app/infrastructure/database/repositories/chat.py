from typing import Optional

from sqlalchemy.sql import select

from app.infrastructure.cache.storages import ChatRedisStorage
from app.infrastructure.database.models.chat import ChatModel
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
