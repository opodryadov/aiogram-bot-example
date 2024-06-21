from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from sqlalchemy.orm import Session

from app.infrastructure.database.models.chat import ChatModel, Role


class RoleFilter(BaseFilter):
    def __init__(self, roles: List[Role]):
        self.roles = roles

    async def __call__(
        self, obj: TelegramObject, chat: ChatModel, session: Session
    ) -> bool:
        if not chat:
            if not self.roles:
                return True
            return False

        return chat.role in self.roles
