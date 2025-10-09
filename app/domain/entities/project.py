from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID

from app.domain.entities.task import Task
from app.domain.exceptions import ValidationError
from app.domain.events import DomainEvent, ProjectDeadlineChangedEvent


@dataclass
class Project:

    id: UUID
    title: str
    deadline: datetime
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    _domain_events: list[DomainEvent] = field(default_factory=list, init=False)

    def __post_init__(self):
        if self._domain_events is None:
            self._domain_events = []

    def mark_as_completed(self, tasks: list[Task]) -> None:
        incomplete_tasks = [task for task in tasks if not task.is_completed]
        if incomplete_tasks:
            raise ValidationError(
                "Cannot complete project. Task(s) are still incomplete"
            )

        self.is_completed = True
        self.updated_at = datetime.now(timezone.utc)

    def reopen(self) -> None:
        self.is_completed = False
        self.updated_at = datetime.now(timezone.utc)

    def update_deadline(self, new_deadline: datetime) -> None:
        old_deadline = self.deadline
        self.deadline = new_deadline
        self.updated_at = datetime.now(timezone.utc)

        if old_deadline != new_deadline:
            event = ProjectDeadlineChangedEvent(
                project_id=self.id,
                old_deadline=old_deadline,
                new_deadline=new_deadline,
                occurred_at=datetime.now(timezone.utc),
            )
            self._domain_events.append(event)

    def should_auto_complete(
        self, tasks: list[Task], auto_complete_enabled: bool
    ) -> bool:
        if not auto_complete_enabled or self.is_completed:
            return False
        return all(task.is_completed for task in tasks) and len(tasks) > 0

    def collect_domain_events(self) -> list[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
