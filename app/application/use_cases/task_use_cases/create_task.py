from uuid import uuid4
from datetime import datetime, timezone

from app.application.use_cases.task_use_cases.task_use_case import TaskUseCase
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.entities.task import Task
from app.application.dto.task_dto import CreateTaskDTO, TaskDTO
from app.domain.exceptions import ValidationError


class CreateTaskUseCase(TaskUseCase):

    def __init__(
        self, task_repository: TaskRepository, project_repository: ProjectRepository
    ) -> None:
        self._task_repository = task_repository
        self._project_repository = project_repository

    def execute(self, dto: CreateTaskDTO) -> TaskDTO:
        if dto.deadline < datetime.now(timezone.utc):
            raise ValidationError("The task deadline has passed")

        task = Task(
            id=uuid4(),
            title=dto.title,
            description=dto.description,
            deadline=dto.deadline,
            is_completed=False,
            project_id=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        saved_task = self._task_repository.save(task)
        return self._to_dto(saved_task)
