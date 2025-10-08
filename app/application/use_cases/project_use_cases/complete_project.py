from uuid import UUID

from app.application.use_cases.project_use_cases.project_use_case import ProjectUseCase
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskRepository
from app.application.dto.project_dto import ProjectDTO
from app.domain.exceptions import NotFoundError


class CompleteProjectUseCase(ProjectUseCase):

    def __init__(
        self, project_repository: ProjectRepository, task_repository: TaskRepository
    ) -> None:
        self._project_repository = project_repository
        self._task_repository = task_repository

    def execute(self, project_id: UUID) -> ProjectDTO:
        project = self._project_repository.get_by_id(project_id)
        if not project:
            raise NotFoundError(f"Project not found")
        tasks = self._task_repository.get_by_project_id(project_id)
        project.mark_as_completed(tasks)
        updated_project = self._project_repository.save(project)
        return self._to_dto(updated_project)
