from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionFactory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yields a db session from the pool"""
    async with AsyncSessionFactory() as session:
        session: AsyncSession
        try:
            yield session
        except SQLAlchemyError as e:
            raise e


""" Annotated Dependency """
dbDep = Annotated[AsyncSession, Depends(get_db)]
