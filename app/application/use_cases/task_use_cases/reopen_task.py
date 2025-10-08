from uuid import UUID

from app.application.dto.task_dto import TaskDTO
from app.application.use_cases.task_use_cases.task_use_case import TaskUseCase
from app.domain.exceptions import DomainError, NotFoundError
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskRepository


class ReopenTaskUseCase(TaskUseCase):
    def __init__(
        self, task_repository: TaskRepository, project_repository: ProjectRepository
    ) -> None:
        self._task_repository = task_repository
        self._project_repository = project_repository

    def execute(self, task_id: UUID) -> TaskDTO:
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        task.reopen()
        if task.project_id:
            project = self._project_repository.get_by_id(task.project_id)
            if not project:
                raise NotFoundError("The project associated with task not found")
            if not project.is_completed:
                return self._to_dto(task)
            project.reopen()
            self._project_repository.update(project)
        return self._to_dto(self._task_repository.update(task))
