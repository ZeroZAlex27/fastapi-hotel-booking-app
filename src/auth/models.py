from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from ..database import Base


class RefreshSessionModel(Base):
    __tablename__ = "refresh_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[UUID] = mapped_column(pgUUID, index=True)
    expires_in: Mapped[int] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(
        pgUUID, ForeignKey("users.id", ondelete="CASCADE")
    )
