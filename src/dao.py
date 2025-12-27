from typing import Any, Dict, Generic, TypeVar, Union

from sqlalchemy import delete, insert, select, update
from sqlalchemy.sql import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from .database import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseDAO(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    model = None

    @classmethod
    async def find_one_or_none(
        cls,
        session: AsyncSession,
        *filter,
        **filter_by,
    ) -> ModelType | None:
        statement = select(cls.model).filter(*filter).filter_by(**filter_by)
        result = await session.execute(statement)
        return result.scalars().one_or_none()

    @classmethod
    async def find_all(
        cls,
        session: AsyncSession,
        *filter,
        offset: int = 0,
        limit: int = 100,
        order_by=None,
        **filter_by,
    ) -> list[ModelType]:
        statement = select(cls.model).filter(*filter).filter_by(**filter_by)

        if order_by is not None:
            statement = statement.order_by(order_by)

        statement = statement.offset(offset).limit(limit)

        result = await session.execute(statement)
        return result.scalars().all()

    @classmethod
    async def add(
        cls,
        session: AsyncSession,
        object_in: Union[CreateSchemaType, Dict[str, Any]],
    ) -> ModelType | None:
        if isinstance(object_in, dict):
            create_data = object_in
        else:
            create_data = object_in.model_dump(exclude_unset=True)

        try:
            statement = insert(cls.model).values(**create_data).returning(cls.model)
            result = await session.execute(statement)
            return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                message = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                message = "Unknown Exc: Cannot insert data into table"

            print(message)
            return None

    @classmethod
    async def add_default(
        cls,
        session: AsyncSession,
    ) -> ModelType | None:
        try:
            statement = insert(cls.model).returning(cls.model)
            result = await session.execute(statement)
            return result.scalars().first()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                message = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                message = "Unknown Exc: Cannot insert data into table"

            print(message)
            return None

    @classmethod
    async def delete(
        cls,
        session: AsyncSession,
        *filter,
        **filter_by,
    ) -> None:
        statement = delete(cls.model).filter(*filter).filter_by(**filter_by)
        await session.execute(statement)

    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        *where,
        object_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType | None:
        if isinstance(object_in, dict):
            update_data = object_in
        else:
            update_data = object_in.model_dump(exclude_unset=True)

        statement = (
            update(cls.model).where(*where).values(**update_data).returning(cls.model)
        )
        result = await session.execute(statement)
        return result.scalars().one()

    @classmethod
    async def add_bulk(
        cls,
        session: AsyncSession,
        data: list[Dict[str, Any]],
    ):
        try:
            result = await session.execute(insert(cls.model).returning(cls.model), data)
            return result.scalars().all()
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                message = "Database Exc"
            elif isinstance(e, Exception):
                message = "Unknown Exc"
            message += ": Cannot bulk insert data into table"

            return None

    @classmethod
    async def update_bulk(
        cls,
        session: AsyncSession,
        data: list[Dict[str, Any]],
    ):
        try:
            await session.execute(update(cls.model), data)
        except (SQLAlchemyError, Exception) as e:
            if isinstance(e, SQLAlchemyError):
                message = "Database Exc"
            elif isinstance(e, Exception):
                message = "Unknown Exc"
            message += ": Cannot bulk update data into table"
            print(message)

            return None

    @classmethod
    async def count(
        cls,
        session: AsyncSession,
        *filter,
        **filter_by,
    ):
        statement = (
            select(func.count())
            .select_from(cls.model)
            .filter(*filter)
            .filter_by(**filter_by)
        )
        result = await session.execute(statement)
        return result.scalar()
