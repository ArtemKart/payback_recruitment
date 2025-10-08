from abc import ABC, abstractmethod
from uuid import UUID
from app.domain.entities.task import Task


class TaskRepository(ABC):

    @abstractmethod
    def get_by_id(self, task_id: UUID) -> Task | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Task]:
        pass

    @abstractmethod
    def get_by_project_id(self, project_id: UUID) -> list[Task]:
        pass

    @abstractmethod
    def save(self, task: Task) -> Task:
        pass

    @abstractmethod
    def update(self, task: Task) -> Task:
        pass

    @abstractmethod
    def delete(self, task_id: UUID) -> None:
        pass
