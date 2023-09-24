from functools import lru_cache
from typing import Any, Self

import pydantic
from sqlalchemy import MetaData, inspect
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapper, as_declarative

from app.utils.regex import camel_to_snake

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=naming_convention)


@as_declarative(metadata=metadata)
class BaseModel:
    id: Any
    __name__: str

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Automatically generates a snake case table name"""
        return camel_to_snake(cls.__name__)

    @classmethod
    @lru_cache
    def table_name(cls) -> str:
        """Returns the table name

        If the model is a sub-class of another model in a single table inheritance,
        the table name of the parent model is returned instead
        """
        insp: Mapper = inspect(cls, raiseerr=True)
        return insp.tables[-1].name if insp else cls.__tablename__

    @classmethod
    def create_from(cls, obj: pydantic.BaseModel) -> Self:
        """Creates a new instance of the model from a Pydantic schema instance"""
        model = cls()
        model.import_from(obj)
        return model

    @classmethod
    @lru_cache
    def uq_attrs(cls) -> tuple[str, ...]:
        """Returns a tuple of the model's unique attributes names"""
        insp: Mapper = inspect(cls, raiseerr=True)
        uq_attrs = tuple(attr.name for attr in insp.columns if attr.unique) if insp else ()
        return uq_attrs

    def uq_kwargs(self) -> dict:
        """Returns a dict of the model's unique attributes names and values"""
        return {attr: getattr(self, attr) for attr in self.uq_attrs()}

    def import_from(self, obj: pydantic.BaseModel, **kwargs) -> None:
        """
        Imports values from a Pydantic schema instance to the model instance

        Args:
            obj (BaseSchema): Pydantic schema instance.
            **kwargs: Additional keyword arguments to pass to the Pydantic schema's dict method.

        kwargs:
            include: A list of fields to include in the output.
            exclude: A list of fields to exclude from the output.
            by_alias: Whether to use the field's alias in the dictionary key if defined.
            exclude_unset: Whether to exclude fields that are unset or None from the output.
            exclude_defaults: Whether to exclude fields that are set to their default value from the output.
            exclude_none: Whether to exclude fields that have a value of `None` from the output.
            round_trip: Whether to enable serialization and deserialization round-trip support.
            warnings: Whether to log warnings when invalid fields are encountered.

        Exceptions:
            AttributeError: if schema has an attribute that the model doesn't have
        """
        kwargs.setdefault("by_alias", True)
        d = obj.model_dump(**kwargs)
        for k, v in d.items():
            if hasattr(self, k):
                setattr(self, k, v)
            else:
                raise AttributeError(f"{self.__class__.__name__} has no attribute {k}")

    def __repr__(self) -> str:
        """
        Returns:
            String representation of the model instance

        Examples:
            >>> from app.models import Auction
            >>> auction = Auction(title="test", description="test")
            >>> auction
            <Auction(title='test', description='test')>
        """
        # fmt: off
        columns = ", ".join(
            [
                f"{k}={repr(v)}" for k, v in self.__dict__.items()
                if not k.startswith("_")
            ]
        )
        # fmt: on
        return f"<{self.__class__.__name__}({columns})>"
