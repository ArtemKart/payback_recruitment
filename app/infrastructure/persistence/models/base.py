from datetime import datetime, timezone

from pydantic import ConfigDict
from sqlalchemy.orm import declared_attr
from sqlmodel import SQLModel, Field

from app.infrastructure.persistence.models.types import AwareDateTime


class Base(SQLModel):
    model_config = ConfigDict(
        str_to_lower=False,
        validate_assignment=True,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields with timezone support."""

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=AwareDateTime,
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=AwareDateTime,
        nullable=False,
        sa_column_kwargs={
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )
