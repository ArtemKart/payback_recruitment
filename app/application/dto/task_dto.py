from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class CreateTaskDTO:
    title: str
    description: str | None
    deadline: datetime | None


@dataclass
class UpdateTaskDTO:
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None


@dataclass
class TaskDTO:
    id: UUID
    title: str
    description: str | None
    deadline: datetime | None
    is_completed: bool
    project_id: UUID | None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool


@dataclass
class TaskFilterDTO:
    is_completed: bool | None = None
    is_overdue: bool | None = None
    project_id: UUID | None = None
