from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models.base import BaseModel


class BaseRepository:
    session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self, *instances: BaseModel) -> None:
        self.session.add_all(instances)
        await self.session.commit()
