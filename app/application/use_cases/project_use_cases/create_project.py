from uuid import uuid4
from datetime import datetime, timezone

from app.application.use_cases.project_use_cases.project_use_case import ProjectUseCase
from app.domain.exceptions import ValidationError
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.entities.project import Project
from app.application.dto.project_dto import CreateProjectDTO, ProjectDTO


class CreateProjectUseCase(ProjectUseCase):
    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    def execute(self, dto: CreateProjectDTO) -> ProjectDTO:
        if dto.deadline < datetime.now(timezone.utc):
            raise ValidationError("Project deadline has passed")
        project = Project(
            id=uuid4(),
            title=dto.title,
            deadline=dto.deadline,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        saved_project = self._project_repository.save(project)
        return self._to_dto(saved_project)
