from uuid import UUID

from fastapi import APIRouter, Depends, Response, Request, status

from src.database import Message
from ..users.schemas import UserCreate, User
from ..users.service import UserService
from .schemas import Token, LoginData
from .service import AuthService
from .dependencies import get_current_user, get_current_active_user
from .exceptions import InvalidCredentials
from ..config import settings

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", status_code=status.HTTP_201_CREATED, response_model=User)
async def register(user: UserCreate) -> User:
    return await UserService.register_new_user(user)


@auth_router.post("/login", response_model=Token)
async def login(
    credentials: LoginData,
    response: Response,
) -> Token:
    user = await AuthService.authenticate_user(credentials.email, credentials.password)
    if not user:
        raise InvalidCredentials

    token = await AuthService.create_token(user.id)

    response.set_cookie(
        "access_token",
        token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True,
    )
    return token


@auth_router.post(
    "/logout",
    dependencies=[Depends(get_current_active_user)],
    response_model=Message,
)
async def logout(request: Request, response: Response) -> Message:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await AuthService.logout(UUID(refresh_token))

    return Message(message="Logged out successfully")


@auth_router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
) -> Token:
    refresh_cookie = request.cookies.get("refresh_token")
    if not refresh_cookie:
        raise InvalidCredentials

    try:
        refresh_token = UUID(refresh_cookie)
    except ValueError:
        raise InvalidCredentials

    new_token = await AuthService.refresh_token(refresh_token)

    response.set_cookie(
        "access_token",
        new_token.access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
    )
    response.set_cookie(
        "refresh_token",
        new_token.refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 30 * 24 * 60,
        httponly=True,
    )
    return new_token


@auth_router.post("/abort", response_model=Message)
async def abort_all_sessions(
    response: Response, user: User = Depends(get_current_user)
) -> Message:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    await AuthService.abort_all_sessions(user.id)
    return Message(message="All sessions was aborted")
