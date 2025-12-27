from passlib.context import CryptContext

from fastapi import Request

from .exceptions import NotAuthenticated


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CookieToken:
    def __init__(self, auto_error: bool = False):
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> str | None:
        token = request.cookies.get("access_token")

        if not token or not token.lower().startswith("bearer "):
            if self.auto_error:
                raise NotAuthenticated
            return None

        return token.split(" ", 1)[1]


def is_valid_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_context.hash(password)
