from uuid import UUID

from app.application.use_cases.task_use_cases.task_use_case import TaskUseCase
from app.domain.exceptions import NotFoundError
from app.domain.repositories.task_repository import TaskRepository
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.services.project_completion_service import ProjectCompletionService
from app.application.dto.task_dto import TaskDTO


class CompleteTaskUseCase(TaskUseCase):
    def __init__(
        self,
        task_repository: TaskRepository,
        project_repository: ProjectRepository,
        completion_service: ProjectCompletionService,
    ):
        self._task_repository = task_repository
        self._project_repository = project_repository
        self._completion_service = completion_service

    def execute(self, task_id: UUID) -> TaskDTO:
        task = self._task_repository.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task not found")
        task.mark_as_completed()
        updated_task = self._task_repository.update(task)
        if task.project_id:
            project = self._project_repository.get_by_id(task.project_id)
            if project:
                all_tasks = self._task_repository.get_by_project_id(task.project_id)
                self._completion_service.handle_task_completed(project, all_tasks)
                self._project_repository.update(project)
        return self._to_dto(updated_task)
