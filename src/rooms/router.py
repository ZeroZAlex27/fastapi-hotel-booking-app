from datetime import date
from uuid import UUID

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, status

from src.database import Message

from .schemas import Room, RoomCreate, RoomUpdate, Rooms
from .service import RoomService, SortOptions
from ..auth.dependencies import get_current_superuser

room_router = APIRouter(prefix="/rooms", tags=["room"])


@room_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)],
    response_model=Room,
)
async def add_room(
    room: RoomCreate,
) -> Room:
    return await RoomService.add_room(room)


@room_router.post(
    "/bulk",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_superuser)],
    response_model=list[Room],
)
async def add_rooms(
    rooms: list[RoomCreate],
) -> list[Room]:
    return await RoomService.add_rooms(rooms)


@room_router.get("/{room_id}", response_model=Room)
async def get_room(room_id: UUID = Path(...)) -> Room:
    return await RoomService.get_room(room_id)


@room_router.get("", response_model=Rooms)
async def get_rooms(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    min_price: float | None = None,
    max_price: float | None = None,
    places: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    sort_by_price: SortOptions | None = None,
) -> Rooms:
    return await RoomService.get_rooms(
        offset=offset,
        limit=limit,
        min_price=min_price,
        max_price=max_price,
        places=places,
        date_from=date_from,
        date_to=date_to,
        sort_by_price=sort_by_price,
    )


@room_router.put(
    "/{room_id}", dependencies=[Depends(get_current_superuser)], response_model=Room
)
async def update_room(
    room: RoomUpdate,
    room_id: UUID = Path(...),
) -> Room:
    return await RoomService.update_room(room_id, room)


@room_router.delete(
    "/{room_id}", dependencies=[Depends(get_current_superuser)], response_model=Message
)
async def delete_room(
    room_id: UUID = Path(...),
) -> Message:
    await RoomService.delete_room(room_id)
    return Message(message="Room deleted successfully")
