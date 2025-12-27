import asyncio
import logging

from .exceptions import EntityNotFound
from .config import settings

from .users.service import UserService
from .users.schemas import UserCreate, UserUpdate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_data():
    logger.info("Checking if superuser exists...")

    try:
        superuser = await UserService.get_user_by_email(settings.FIRST_SUPERUSER_EMAIL)
    except EntityNotFound:
        superuser = None

    if superuser:
        logger.info("Superuser already exists — nothing to initialize.")
        return

    logger.info("Initializing system data...")

    logger.info("Creating superuser...")

    superuser_data = UserCreate(
        email=settings.FIRST_SUPERUSER_EMAIL,
        name="admin",
        surname="admin",
        patronymic="admin",
        password=settings.FIRST_SUPERUSER_PASSWORD,
        password_repeat=settings.FIRST_SUPERUSER_PASSWORD,
    )

    superuser = await UserService.register_new_user(superuser_data)

    update_data = UserUpdate(is_superuser=True)

    await UserService.update_user_from_superuser(superuser.id, update_data)

    logger.info(f"Superuser created: {superuser.email}")

    logger.info("Initial data creation completed successfully!")


if __name__ == "__main__":
    asyncio.run(init_data())
