from abc import ABC
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel
from app.schemas.base import BaseSchema


class BaseRepo[ModelType: BaseModel, CreateSchemaType: BaseSchema](ABC):
    """
    Base repository class with default CRUD operations
    """

    def __init__(self, model: type[ModelType]) -> None:
        """Initialize repository with model"""
        self.model = model

    async def get(
        self,
        db: AsyncSession,
        *,
        id: UUID | str | int,
    ) -> ModelType | None:
        """Get model by id"""
        query = sa.select(self.model).filter(self.model.id == id)
        return await db.scalar(query)

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new model.

        Returns:
            Created model
        """
        db_obj = self.model.create_from(obj_in)
        db.add(db_obj)
        return db_obj

    async def bulk_create(self, db: AsyncSession, *, objs_in: list[CreateSchemaType]) -> list[ModelType]:
        """
        Bulk create new models.

        Returns:
            Created models
        """
        db_objs = [self.model.create_from(obj_in) for obj_in in objs_in]
        db.add_all(db_objs)
        return db_objs
