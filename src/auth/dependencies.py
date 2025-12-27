from uuid import UUID

from jose import jwt
from fastapi import Depends

from ..users.models import UserModel
from ..users.service import UserService
from ..exceptions import NotEnoughPrivileges
from .exceptions import (
    InvalidToken,
    InactiveUser,
)
from ..config import settings
from .utils import CookieToken

cookie_token = CookieToken()


async def get_current_user_id(token: str = Depends(cookie_token)) -> str | None:
    if token:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload.get("sub")
    return None


async def get_current_user(token: str = Depends(cookie_token)) -> UserModel | None:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise InvalidToken
    except Exception:
        raise InvalidToken
    current_user = await UserService.get_user(UUID(user_id))
    return current_user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise InactiveUser
    return current_user


async def get_current_superuser(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_superuser:
        raise NotEnoughPrivileges
    return current_user
