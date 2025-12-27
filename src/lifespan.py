import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI

from sqlalchemy.exc import ProgrammingError
from asyncpg.exceptions import UndefinedTableError

from .initial_data import init_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Running initial data setup...")

    try:
        await init_data()
    except (ProgrammingError, UndefinedTableError):
        logger.warning(
            "Database tables do not exist yet. " "Skipping initial data initialization."
        )

    yield
