from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateProjectDTO:
    title: str
    deadline: datetime


@dataclass
class UpdateProjectDTO:
    title: str | None = None
    deadline: datetime | None = None


@dataclass
class ProjectDTO:
    id: UUID
    title: str
    deadline: datetime | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
