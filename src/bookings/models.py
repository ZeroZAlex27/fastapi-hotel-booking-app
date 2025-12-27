from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as pgUUID

from ..database import Base


class BookingModel(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        UniqueConstraint("room_id", "date_from", "date_to", name="uq_room_booking"),
    )

    id: Mapped[UUID] = mapped_column(
        pgUUID, primary_key=True, index=True, default=uuid4
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    room_id: Mapped[UUID] = mapped_column(ForeignKey("rooms.id"))

    date_from: Mapped[date] = mapped_column(Date)
    date_to: Mapped[date] = mapped_column(Date)

    user = relationship("UserModel", back_populates="bookings")
    room = relationship("RoomModel", back_populates="bookings")
