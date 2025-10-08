from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class DomainEvent:
    occurred_at: datetime


@dataclass
class ProjectDeadlineChangedEvent(DomainEvent):
    project_id: UUID
    old_deadline: datetime | None
    new_deadline: datetime | None
