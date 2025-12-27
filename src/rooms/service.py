from enum import Enum
from datetime import date
from uuid import UUID

from sqlalchemy import and_, exists, not_

from ..exceptions import EntityAlreadyExists, EntityNotFound

from ..database import async_session_maker
from ..bookings.models import BookingModel
from .schemas import Room, RoomCreate, RoomUpdate, Rooms
from .models import RoomModel
from .dao import RoomDAO


class SortOptions(str, Enum):
    asc = "asc"
    desc = "desc"


class RoomService:
    @classmethod
    async def add_room(cls, room: RoomCreate) -> Room:
        async with async_session_maker() as session:
            room_exist = await RoomDAO.find_one_or_none(session, name=room.name)
            if room_exist:
                raise EntityAlreadyExists("room")

            db_room = await RoomDAO.add(session, room)
            await session.commit()
        return db_room

    @classmethod
    async def add_rooms(cls, rooms: list[RoomCreate]) -> list[Room]:
        async with async_session_maker() as session:
            db_rooms = await RoomDAO.add_bulk(session, rooms)
            await session.commit()
        return db_rooms

    @classmethod
    async def get_room(cls, room_id: UUID) -> Room:
        async with async_session_maker() as session:
            db_room = await RoomDAO.find_one_or_none(session, id=room_id)
        if db_room is None:
            raise EntityNotFound("room")
        return db_room

    @classmethod
    async def get_rooms(
        cls,
        offset: int = 0,
        limit: int = 100,
        min_price: float | None = None,
        max_price: float | None = None,
        places: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by_price: SortOptions | None = None,
    ) -> Rooms:
        filters = []

        if min_price is not None:
            filters.append(RoomModel.price_per_day >= min_price)

        if max_price is not None:
            filters.append(RoomModel.price_per_day <= max_price)

        if places is not None:
            filters.append(RoomModel.places == places)

        if date_from and date_to:
            booking_exists = exists().where(
                and_(
                    BookingModel.room_id == RoomModel.id,
                    BookingModel.date_from < date_to,
                    BookingModel.date_to > date_from,
                )
            )
            filters.append(not_(booking_exists))

        order_by = None
        if sort_by_price == "asc":
            order_by = RoomModel.price_per_day.asc()
        elif sort_by_price == "desc":
            order_by = RoomModel.price_per_day.desc()

        async with async_session_maker() as session:
            rooms = await RoomDAO.find_all(
                session,
                *filters,
                order_by=order_by,
                offset=offset,
                limit=limit,
            )
            if not rooms:
                raise EntityNotFound("room")
            count = await RoomDAO.count(session, *filters)
        return Rooms(data=rooms, count=count)

    @classmethod
    async def update_room(cls, room_id: UUID, room: RoomUpdate) -> Room:
        async with async_session_maker() as session:
            db_room = await RoomDAO.find_one_or_none(session, RoomModel.id == room_id)
            if db_room is None:
                raise EntityNotFound("room")

            room_in = room.model_dump(exclude_unset=True)
            room_update = await RoomDAO.update(
                session, RoomModel.id == room_id, object_in=room_in
            )
            await session.commit()
        return room_update

    @classmethod
    async def delete_room(cls, room_id: UUID) -> None:
        async with async_session_maker() as session:
            await RoomDAO.delete(session, RoomModel.id == room_id)
            await session.commit()

    @classmethod
    async def count_rooms(cls) -> int:
        async with async_session_maker() as session:
            count = await RoomDAO.count(session)
        return count or 0
