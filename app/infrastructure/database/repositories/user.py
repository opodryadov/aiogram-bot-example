from typing import Optional

from sqlalchemy.sql import select

from app.infrastructure.cache.storages import UserRedisStorage
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.repositories.base import BaseRepository
from app.tgbot.dispatcher import redis


class UserRepository(BaseRepository):
    storage: UserRedisStorage = UserRedisStorage(redis=redis)

    async def add_user(self, chat_id: int, chat_title: str) -> UserModel:
        new_user: UserModel = UserModel(chat_id=chat_id, chat_title=chat_title)
        await self.commit(new_user)
        return new_user

    async def get_user(self, chat_id: int) -> Optional[UserModel]:
        key = self.storage.get_key(chat_id)
        user: Optional[UserModel] = await self.storage.get_from_cache(key)
        if user:
            return user

        user = await self.session.scalar(
            select(UserModel).where(UserModel.chat_id == chat_id)
        )
        await self.storage.put_to_cache(key=key, value=user)

        return user
