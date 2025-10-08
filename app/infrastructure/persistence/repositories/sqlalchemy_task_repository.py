from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session, select
from app.domain.repositories.task_repository import TaskRepository
from app.domain.entities.task import Task
from app.infrastructure.persistence.models.models import TaskModel
from app.infrastructure.persistence.repositories.exceptions import (
    SQLAlchemyRepositoryError,
)


class SQLAlchemyTaskRepository(TaskRepository):

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, task_id: UUID) -> Task | None:
        model = self._session.get(TaskModel, task_id)
        return self._to_entity(model) if model else None

    def get_all(self) -> list[Task]:
        try:
            models = self._session.exec(select(TaskModel)).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise SQLAlchemyRepositoryError("Failed to fetch tasks") from e

    def get_by_project_id(self, project_id: UUID) -> list[Task]:
        try:
            statement = select(TaskModel).where(TaskModel.project_id == project_id)
            models = self._session.exec(statement).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise SQLAlchemyRepositoryError("Failed to fetch tasks for project") from e

    def save(self, task: Task) -> Task:
        try:
            model = self._to_model(task)
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError(
                "Task already exists or constraint violated"
            ) from e
        except SQLAlchemyError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError("Failed to save task") from e

    def update(self, task: Task) -> Task:
        try:
            model = self._session.get(TaskModel, task.id)
            self._update_model(model, task)
            self._session.commit()
            self._session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError("Failed to update task") from e

    def delete(self, task_id: UUID) -> None:
        try:
            model = self._session.get(TaskModel, task_id)
            if model:
                self._session.delete(model)
                self._session.commit()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError("Failed to delete task") from e

    @staticmethod
    def _to_entity(model: TaskModel) -> Task:
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

    @staticmethod
    def _to_model(entity: Task) -> TaskModel:
        return TaskModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            deadline=entity.deadline,
            is_completed=entity.is_completed,
            project_id=entity.project_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _update_model(model: TaskModel, entity: Task) -> None:
        model.title = entity.title
        model.description = entity.description
        model.deadline = entity.deadline
        model.is_completed = entity.is_completed
        model.project_id = entity.project_id
        model.updated_at = entity.updated_at
