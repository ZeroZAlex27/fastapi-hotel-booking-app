from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field


class BookingUpdate(BaseModel):
    user_id: UUID | None = Field(default=None)
    room_id: UUID | None = Field(default=None)
    date_from: date | None = Field(default=None)
    date_to: date | None = Field(default=None)


class BookingCreate(BookingUpdate):
    user_id: UUID
    room_id: UUID
    date_from: date
    date_to: date


class Booking(BookingCreate):
    id: UUID

    class Config:
        from_attributes = True


class Bookings(BaseModel):
    data: list[Booking]
    count: int
