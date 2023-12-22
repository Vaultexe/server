import pydantic
import pytest
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from app.schemas import BaseSchema


class TestSchema(BaseSchema):
    id: int
    email: str
    name: str
    data: str
    model_config = pydantic.ConfigDict(extra="allow")

    __test__ = False  # Prevent pytest from trying to collect this class as a test


class TestModel(BaseModel):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    data: Mapped[str] = mapped_column(String)

    __test__ = False  # Prevent pytest from trying to collect this class as a test


@pytest.fixture
def mock_schema() -> TestSchema:
    return TestSchema(
        id=1,
        data="data",
        name="Test",
        email="email@example.com",
    )


def test_create_from(mock_schema: TestSchema):
    model = TestModel.create_from(mock_schema)
    for attr, value in mock_schema.model_dump().items():
        assert getattr(model, attr) == value


def test_import_from(mock_schema: TestSchema):
    model = TestModel()
    model.import_from(mock_schema)
    for attr, value in mock_schema.model_dump().items():
        assert getattr(model, attr) == value


def test_import_from_attr_error(mock_schema: TestSchema):
    # Add an extra unknown attribute to the schema
    mock_schema.extra_attr = "extra"
    model = TestModel()
    with pytest.raises(AttributeError):
        model.import_from(mock_schema)


def test_uq_attrs():
    assert TestModel.uq_attrs() == ("email",)


def test_uq_kwargs(mock_schema: TestSchema):
    model = TestModel.create_from(mock_schema)
    assert model.uq_kwargs() == mock_schema.model_dump(include={"email"})
