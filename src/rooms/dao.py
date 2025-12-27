from .models import RoomModel
from .schemas import RoomCreate, RoomUpdate

from ..dao import BaseDAO


class RoomDAO(BaseDAO[RoomModel, RoomCreate, RoomUpdate]):
    model = RoomModel
