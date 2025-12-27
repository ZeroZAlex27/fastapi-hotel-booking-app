from .models import RefreshSessionModel
from .schemas import (
    RefreshSessionCreate,
    RefreshSessionUpdate,
)
from ..dao import BaseDAO


class RefreshSessionDAO(
    BaseDAO[RefreshSessionModel, RefreshSessionCreate, RefreshSessionUpdate]
):
    model = RefreshSessionModel
