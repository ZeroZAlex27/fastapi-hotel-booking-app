from .models import BookingModel
from .schemas import BookingCreate, BookingUpdate

from ..dao import BaseDAO


class BookingDAO(BaseDAO[BookingModel, BookingCreate, BookingUpdate]):
    model = BookingModel
