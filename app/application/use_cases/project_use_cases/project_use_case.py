from dataclasses import dataclass

from app.application.dto.project_dto import ProjectDTO
from app.domain.entities.project import Project


@dataclass
class ProjectUseCase:
    @staticmethod
    def _to_dto(project: Project) -> ProjectDTO:
        return ProjectDTO(
            id=project.id,
            title=project.title,
            deadline=project.deadline,
            is_completed=project.is_completed,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
