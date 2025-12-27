from uuid import UUID

from pydantic import BaseModel, Field


class RoomUpdate(BaseModel):
    name: str | None = Field(default=None)
    price_per_day: float | None = Field(default=None)
    places: int | None = Field(default=None)


class RoomCreate(RoomUpdate):
    name: str
    price_per_day: float
    places: int


class Room(RoomCreate):
    id: UUID

    class Config:
        from_attributes = True


class Rooms(BaseModel):
    data: list[Room]
    count: int
