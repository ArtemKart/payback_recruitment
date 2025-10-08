from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.infrastructure.persistence.models.base import Base, TimestampMixin
from app.infrastructure.persistence.models.types import AwareDateTime


class ProjectModel(Base, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(nullable=False)
    deadline: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=AwareDateTime,
        nullable=False,
    )
    is_completed: bool | None = Field(default=False)

    tasks: list["TaskModel"] = Relationship(back_populates="project")


class TaskModel(Base, TimestampMixin, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(nullable=False)
    description: str | None = Field(nullable=True, default=None)
    deadline: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=AwareDateTime,
        nullable=False,
    )
    is_completed: bool | None = Field(default=False)
    project_id: UUID | None = Field(default=None, foreign_key="projectmodel.id")

    project: ProjectModel | None = Relationship(back_populates="tasks")
