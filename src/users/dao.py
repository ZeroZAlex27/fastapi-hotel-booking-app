from .models import UserModel
from .schemas import UserCreateDB, UserUpdateDB
from ..dao import BaseDAO


class UserDAO(BaseDAO[UserModel, UserCreateDB, UserUpdateDB]):
    model = UserModel
