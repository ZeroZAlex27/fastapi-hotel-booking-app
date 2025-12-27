from uuid import UUID

from jose import jwt

from starlette.middleware.base import BaseHTTPMiddleware

from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from fastapi import Request, Response

from .config import settings

from .auth.service import AuthService
from .users.service import UserService

from .users.models import UserModel
from .rooms.models import RoomModel
from .bookings.models import BookingModel


class AdminCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)

        if request.url.path == "/admin/login" and hasattr(request.state, "user_id") and request.state.user_id:
            token = await AuthService.create_token(request.state.user_id)
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

        if request.url.path == "/admin/logout":
            response.delete_cookie("access_token")
            response.delete_cookie("refresh_token")

            refresh_token = request.cookies.get("refresh_token")
            if refresh_token:
                await AuthService.logout(UUID(refresh_token))
        return response


class AdminAuth(AuthenticationBackend):
    def __init__(self):
        super().__init__(secret_key=settings.SECRET_KEY)

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        user = await AuthService.authenticate_user(username, password)
        if user and user.is_superuser:
            request.state.user_id = user.id
            return True
        return False
    
    async def logout(self, request: Request) -> bool:
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.cookies.get("access_token")
        if not token:
            return False
        token = token.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
            user_id = payload.get("sub")
            if not user_id:
                return False
        except Exception:
            return False

        user = await UserService.get_user(UUID(user_id))
        if not user:
            return False

        if not user.is_superuser:
            return False
        return True


class UserAdmin(ModelView, model=UserModel):
    form_excluded_columns = ["created_at", "modified_at", "hashed_password"]

    column_searchable_list = [UserModel.email]
    column_exclude_list = ["bookings", "hashed_password", "created_at", "modified_at"]
    column_details_exclude_list = ["hashed_password"]


class RoomAdmin(ModelView, model=RoomModel):
    form_excluded_columns = ["created_at", "modified_at"]

    column_searchable_list = [RoomModel.name]
    column_exclude_list = ["bookings", "created_at", "modified_at"]
    column_sortable_list = [RoomModel.price_per_day, RoomModel.places]


class BookingAdmin(ModelView, model=BookingModel):
    form_excluded_columns = ["created_at", "modified_at"]

    column_sortable_list = [BookingModel.user_id, BookingModel.room_id]
    column_exclude_list = ["user", "room", "created_at", "modified_at"]
