import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy.dialects.postgresql import ENUM, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.types import BigInteger, DateTime, String

from app.infrastructure.database.models.base import BaseModel


class Role(str, Enum):
    ADMIN = "admin"
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    BLOCKED = "blocked"


class ChatModel(BaseModel):
    __tablename__ = "chats"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    chat_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False
    )
    chat_title: Mapped[str] = mapped_column(String(128), nullable=False)
    chat_type: Mapped[str] = mapped_column(String(16), nullable=False)
    phone: Mapped[str] = mapped_column(String(16), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=True)
    role: Mapped[Role] = mapped_column(ENUM(Role), default=Role.UNAUTHORIZED)
    commentary: Mapped[str] = mapped_column(String(256), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    access_until: Mapped[datetime] = mapped_column(DateTime, nullable=True)
