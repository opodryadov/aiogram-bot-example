# isort: skip_file
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DBSettings


def sa_sessionmaker(db: DBSettings) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = create_async_engine(url=str(db.dsn), echo=db.echo)
    return async_sessionmaker(bind=engine, expire_on_commit=False)
