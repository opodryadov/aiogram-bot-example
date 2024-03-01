from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repositories.base import BaseRepository
from app.infrastructure.database.repositories.user import UserRepository


class Repository(BaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.user = UserRepository(session=session)
