from uuid import UUID

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, status

from src.database import Message
from src.users.schemas import User

from .schemas import Booking, BookingCreate, BookingUpdate, Bookings
from .service import BookingService
from ..auth.dependencies import get_current_active_user, get_current_superuser
from ..exceptions import NotEnoughPrivileges

booking_router = APIRouter(prefix="/bookings", tags=["booking"])


@booking_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Booking,
)
async def add_booking(
    booking: BookingCreate,
    current_user: User = Depends(get_current_active_user),
) -> Booking:
    booking.user_id = current_user.id
    return await BookingService.add_booking(booking)


@booking_router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)],
    response_model=list[Booking],
)
async def add_bookings(
    bookings: list[BookingCreate],
) -> list[Booking]:
    return await BookingService.add_bookings(bookings)


@booking_router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: UUID = Path(...),
    current_user: User = Depends(get_current_active_user),
) -> Booking:
    booking = await BookingService.get_booking(booking_id)
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise NotEnoughPrivileges
    return booking


@booking_router.get("", response_model=Bookings)
async def get_bookings(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    current_user: User = Depends(get_current_active_user),
) -> Bookings:
    return await BookingService.get_bookings(
        offset=offset, limit=limit, user_id=current_user.id
    )


@booking_router.put(
    "/{booking_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=Booking,
)
async def update_booking(
    booking: BookingUpdate,
    booking_id: UUID = Path(...),
) -> Booking:
    return await BookingService.update_booking(booking_id, booking)


@booking_router.delete(
    "/{booking_id}",
    response_model=Message,
)
async def delete_booking(
    booking_id: UUID = Path(...),
    current_user: User = Depends(get_current_active_user),
) -> Message:
    booking = await BookingService.get_booking(booking_id)
    if booking.user_id != current_user.id and not current_user.is_superuser:
        raise NotEnoughPrivileges
    await BookingService.delete_booking(booking_id)
    return Message(message="Booking deleted successfully")
