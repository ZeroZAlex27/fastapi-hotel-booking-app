from uuid import UUID

from sqlalchemy import and_

from src.exceptions import EntityAlreadyExists, EntityNotFound

from ..database import async_session_maker
from .schemas import Booking, BookingCreate, BookingUpdate, Bookings
from .models import BookingModel
from .dao import BookingDAO


class BookingService:
    @classmethod
    async def add_booking(cls, booking: BookingCreate) -> Booking:
        async with async_session_maker() as session:
            room_exists = await BookingDAO.find_one_or_none(
                session,
                BookingModel.id == booking.room_id
            )
            if not room_exists:
                raise EntityNotFound("room")
            overlap = await BookingDAO.find_one_or_none(
                session,
                and_(
                    BookingModel.room_id == booking.room_id,
                    BookingModel.date_from < booking.date_to,
                    BookingModel.date_to > booking.date_from,
                )
            )
            if overlap:
                raise EntityAlreadyExists("booking")

            db_booking = await BookingDAO.add(session, booking)
            await session.commit()
        return db_booking

    @classmethod
    async def add_bookings(cls, bookings: list[BookingCreate]) -> list[Booking]:
        async with async_session_maker() as session:
            db_bookings = await BookingDAO.add_bulk(session, bookings)
            await session.commit()
        return db_bookings

    @classmethod
    async def get_booking(cls, booking_id: UUID) -> Booking:
        async with async_session_maker() as session:
            db_booking = await BookingDAO.find_one_or_none(session, id=booking_id)
        if db_booking is None:
            raise EntityNotFound("booking")
        return db_booking

    @classmethod
    async def get_bookings(
        cls,
        user_id: UUID,
        offset: int = 0,
        limit: int = 100,
    ) -> Bookings:
        async with async_session_maker() as session:
            bookings = await BookingDAO.find_all(
                session, offset=offset, limit=limit, user_id=user_id
            )
            if not bookings:
                raise EntityNotFound("booking")
            count = await BookingDAO.count(session, user_id=user_id)
        return Bookings(data=bookings, count=count)

    @classmethod
    async def update_booking(cls, booking_id: UUID, booking: BookingUpdate) -> Booking:
        async with async_session_maker() as session:
            db_booking = await BookingDAO.find_one_or_none(
                session, BookingModel.id == booking_id
            )
            if db_booking is None:
                raise EntityNotFound("booking")

            booking_in = booking.model_dump(exclude_unset=True)
            booking_update = await BookingDAO.update(
                session, BookingModel.id == booking_id, object_in=booking_in
            )
            await session.commit()
        return booking_update

    @classmethod
    async def delete_booking(cls, booking_id: UUID) -> None:
        async with async_session_maker() as session:
            await BookingDAO.delete(session, BookingModel.id == booking_id)
            await session.commit()

    @classmethod
    async def count_bookings(cls) -> int:
        async with async_session_maker() as session:
            count = await BookingDAO.count(session)
        return count or 0
