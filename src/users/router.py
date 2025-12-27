from uuid import UUID

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path, Response, Request

from ..database import Message

from .schemas import User, Users, UserUpdate
from .service import UserService
from ..auth.service import AuthService
from ..auth.dependencies import (
    get_current_active_user,
    get_current_superuser,
)

user_router = APIRouter(prefix="/users", tags=["user"])


@user_router.get(
    "",
    dependencies=[Depends(get_current_superuser)],
    response_model=Users,
)
async def get_users(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> Users:
    return await UserService.get_users(offset=offset, limit=limit)


@user_router.get(
    "/me",
    response_model=User,
)
async def get_user_self(
    current_user: User = Depends(get_current_active_user),
) -> User:
    return await UserService.get_user(current_user.id)


@user_router.put(
    "/me",
    response_model=User,
)
async def update_current_user(
    user: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> User:
    return await UserService.update_user(current_user.id, user)


@user_router.delete(
    "/me",
    response_model=Message,
)
async def delete_current_user(
    request: Request,
    response: Response,
    current_user: User = Depends(get_current_active_user),
) -> Message:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthService.logout(request.cookies.get("refresh_token"))
    await UserService.delete_user(current_user.id)
    return Message(message="User deleted successfully")


@user_router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=User,
)
async def get_user(
    user_id: UUID = Path(...),
) -> User:
    return await UserService.get_user(user_id)


@user_router.put(
    "/{user_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=User,
)
async def update_user(
    user: UserUpdate,
    user_id: UUID = Path(...),
) -> User:
    return await UserService.update_user_from_superuser(user_id, user)


@user_router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=Message,
)
async def delete_user(
    user_id: UUID = Path(...),
) -> Message:
    await UserService.delete_user_from_superuser(user_id)
    return Message(message="User was deleted")
