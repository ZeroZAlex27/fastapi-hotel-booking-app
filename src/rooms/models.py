from uuid import UUID, uuid4

from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from ..database import Base


class RoomModel(Base):
    __tablename__ = "rooms"

    id: Mapped[UUID] = mapped_column(
        pgUUID, primary_key=True, index=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String, index=True)
    price_per_day: Mapped[float] = mapped_column(Numeric(10, 2))
    places: Mapped[int] = mapped_column(Integer)

    bookings = relationship(
        "BookingModel", back_populates="room", cascade="all, delete"
    )
