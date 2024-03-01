from typing import List

from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from sqlalchemy.orm import Session

from app.infrastructure.database.models.user import Role, UserModel


class RoleFilter(BaseFilter):
    def __init__(self, roles: List[Role]):
        self.roles = roles

    async def __call__(
        self, obj: TelegramObject, user: UserModel, session: Session
    ) -> bool:
        if not user:
            if not self.roles:
                return True
            return False

        return user.role in self.roles
