from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.project import Project


class ProjectRepository(ABC):

    @abstractmethod
    def get_by_id(self, project_id: UUID) -> Project | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Project]:
        pass

    @abstractmethod
    def save(self, project: Project) -> Project:
        pass

    @abstractmethod
    def update(self, project: Project) -> Project:
        pass

    @abstractmethod
    def delete(self, project_id: UUID) -> None:
        pass
