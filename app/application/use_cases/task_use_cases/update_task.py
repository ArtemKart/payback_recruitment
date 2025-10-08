from datetime import datetime, timezone
from uuid import UUID

from app.application.dto.task_dto import UpdateTaskDTO, TaskDTO
from app.application.use_cases.task_use_cases.task_use_case import TaskUseCase
from app.domain.exceptions import NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskRepository


class UpdateTaskUseCase(TaskUseCase):
    def __init__(
        self, task_repository: TaskRepository, project_repository: ProjectRepository
    ) -> None:
        self._task_repository = task_repository
        self._project_repository = project_repository

    def execute(self, dto: UpdateTaskDTO, task_id: UUID) -> TaskDTO:
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")

        if dto.title:
            task.title = dto.title
        if dto.description:
            task.description = dto.description
        if dto.deadline:
            project_deadline = None
            if task.project_id:
                project = self._project_repository.get_by_id(task.project_id)
                if project:
                    project_deadline = project.deadline
            task.update_deadline(dto.deadline, project_deadline)
        task.updated_at = datetime.now(timezone.utc)
        updated_task = self._task_repository.update(task)
        return self._to_dto(updated_task)
