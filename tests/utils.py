from datetime import datetime

from app.domain.entities.project import Project
from app.domain.entities.task import Task
from app.infrastructure.persistence.models.models import TaskModel, ProjectModel


def to_task_entity(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        title=model.title,
        description=model.description,
        deadline=model.deadline,
        is_completed=model.is_completed,
        project_id=model.project_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_project_entity(model: ProjectModel) -> Project:
    return Project(
        id=model.id,
        title=model.title,
        deadline=model.deadline,
        is_completed=model.is_completed,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def cast_datetime_to_sqlite_format(obj: datetime) -> str:
    return obj.isoformat().replace("+00:00", "Z")
