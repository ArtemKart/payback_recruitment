from datetime import datetime
from uuid import UUID

from fastapi import Query
from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: str | None = None
    description: str | None = None
    deadline: datetime | None = None


class TaskRead(TaskBase):
    id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
    project_id: UUID | None = None
