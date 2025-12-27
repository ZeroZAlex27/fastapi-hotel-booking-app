from uuid import UUID

from pydantic import BaseModel, Field, EmailStr


class RefreshSessionCreate(BaseModel):
    refresh_token: UUID
    expires_in: int
    user_id: UUID


class RefreshSessionUpdate(RefreshSessionCreate):
    user_id: UUID | None = Field(None)


class Token(BaseModel):
    access_token: str
    refresh_token: UUID
    token_type: str


class LoginData(BaseModel):
    email: EmailStr
    password: str
