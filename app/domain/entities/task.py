from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from app.domain.exceptions import ConflictError, ValidationError


@dataclass
class Task:

    id: UUID
    title: str
    description: str | None
    deadline: datetime | None
    is_completed: bool
    project_id: UUID | None
    created_at: datetime
    updated_at: datetime

    def mark_as_completed(self) -> None:
        self.is_completed = True
        self.updated_at = datetime.now(timezone.utc)

    def reopen(self) -> None:
        self.is_completed = False
        self.updated_at = datetime.now(timezone.utc)

    def assign_to_project(
        self, project_id: UUID, project_deadline: datetime | None
    ) -> None:
        if self.project_id is not None:
            raise ConflictError("Task is already assigned")

        self._validate_deadline_against_project(project_deadline)
        self.project_id = project_id
        self.updated_at = datetime.now(timezone.utc)

    def unassign_from_project(self) -> None:
        self.project_id = None
        self.updated_at = datetime.now(timezone.utc)

    def update_deadline(
        self, new_deadline: datetime | None, project_deadline: datetime | None = None
    ) -> None:
        if self.project_id and project_deadline:
            self._validate_deadline_against_project_deadline(
                new_deadline, project_deadline
            )
        self.deadline = new_deadline
        self.updated_at = datetime.now(timezone.utc)

    def adjust_deadline_to_project(self, project_deadline: datetime) -> None:
        if self.deadline and self.deadline > project_deadline:
            self.deadline = project_deadline
            self.updated_at = datetime.now(timezone.utc)

    def is_overdue(self) -> bool:
        if not self.deadline or self.is_completed:
            return False
        return datetime.now(timezone.utc) > self.deadline

    def _validate_deadline_against_project(
        self, project_deadline: datetime | None
    ) -> None:
        if self.deadline and project_deadline:
            self._validate_deadline_against_project_deadline(
                self.deadline, project_deadline
            )

    @staticmethod
    def _validate_deadline_against_project_deadline(
        task_deadline: datetime | None, project_deadline: datetime
    ) -> None:
        if task_deadline and task_deadline > project_deadline:
            raise ValidationError("Task deadline cannot be later than project deadline")
