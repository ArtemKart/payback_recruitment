from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectBase(BaseModel):
    title: str
    deadline: datetime


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    title: str | None = None
    deadline: datetime | None = None


class ProjectRead(ProjectBase):
    id: UUID
    is_completed: bool
    created_at: datetime
    updated_at: datetime
