from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlmodel import Session, select
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.entities.project import Project
from app.infrastructure.persistence.models.models import ProjectModel
from app.infrastructure.persistence.repositories.exceptions import (
    SQLAlchemyRepositoryError,
)


class SQLAlchemyProjectRepository(ProjectRepository):
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, project_id: UUID) -> Project | None:
        model = self._session.get(ProjectModel, project_id)
        return self._to_entity(model) if model else None

    def get_all(self) -> list[Project]:
        try:
            models = self._session.exec(select(ProjectModel)).all()
            return [self._to_entity(model) for model in models]
        except SQLAlchemyError as e:
            raise SQLAlchemyRepositoryError("Failed to fetch projects") from e

    def save(self, project: Project) -> Project:
        try:
            model = self._to_model(project)
            self._session.add(model)
            self._session.commit()
            self._session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError(
                "Project already exists or constraint violated"
            ) from e
        except SQLAlchemyError as e:
            raise SQLAlchemyRepositoryError("Failed to save project") from e

    def update(self, project: Project) -> Project:
        try:
            model = self._session.get(ProjectModel, project.id)
            self._update_model(model, project)
            self._session.commit()
            self._session.refresh(model)
            return self._to_entity(model)
        except SQLAlchemyError as e:
            raise SQLAlchemyRepositoryError("Failed to update project") from e

    def delete(self, project_id: UUID) -> None:
        try:
            model = self._session.get(ProjectModel, project_id)
            if model:
                self._session.delete(model)
                self._session.commit()
        except SQLAlchemyError as e:
            self._session.rollback()
            raise SQLAlchemyRepositoryError("Failed to delete project") from e

    @staticmethod
    def _to_entity(model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            title=model.title,
            deadline=model.deadline,
            is_completed=model.is_completed,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_model(entity: Project) -> ProjectModel:
        return ProjectModel(
            id=entity.id,
            title=entity.title,
            deadline=entity.deadline,
            is_completed=entity.is_completed,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def _update_model(model: ProjectModel, entity: Project) -> None:
        model.title = entity.title
        model.deadline = entity.deadline
        model.is_completed = entity.is_completed
        model.updated_at = entity.updated_at
