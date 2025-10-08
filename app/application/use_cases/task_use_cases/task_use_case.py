from dataclasses import dataclass

from app.application.dto.task_dto import TaskDTO
from app.domain.entities.task import Task


@dataclass
class TaskUseCase:

    @staticmethod
    def _to_dto(task: Task) -> TaskDTO:
        return TaskDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            is_completed=task.is_completed,
            project_id=task.project_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_overdue=task.is_overdue(),
        )
