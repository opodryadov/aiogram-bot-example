# isort: skip_file
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import DBSettings


def make_connection_string(db: DBSettings) -> str:
    return f"postgresql+asyncpg://{db.user}:{db.password}@{db.host}:{db.port}/{db.name}"


def sa_sessionmaker(
    db: DBSettings, enable_logging: bool = False
) -> async_sessionmaker[AsyncSession]:
    engine: AsyncEngine = create_async_engine(
        url=make_connection_string(db=db), echo=enable_logging
    )
    return async_sessionmaker(bind=engine, expire_on_commit=False)
