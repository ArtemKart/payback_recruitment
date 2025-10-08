from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

from app.application.use_cases.project_use_cases.update_project import (
    UpdateProjectUseCase,
)
from app.application.use_cases.task_use_cases.link_task_to_project import (
    LinkTaskToProjectUseCase,
)
from app.application.use_cases.task_use_cases.reopen_task import ReopenTaskUseCase
from app.application.use_cases.task_use_cases.unlink_task_from_project import (
    UnlinkTaskToProjectUseCase,
)
from app.application.use_cases.task_use_cases.update_task import UpdateTaskUseCase
from app.domain.event_handlers import ProjectDeadlineChangedHandler
from app.infrastructure.persistence.engine import get_session
from app.infrastructure.persistence.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from app.infrastructure.persistence.repositories.sqlalchemy_task_repository import (
    SQLAlchemyTaskRepository,
)
from app.domain.services.project_completion_service import ProjectCompletionService
from app.domain.services.deadline_enforcement_service import DeadlineEnforcementService
from app.infrastructure.config import get_settings

from app.application.use_cases.project_use_cases.create_project import (
    CreateProjectUseCase,
)
from app.application.use_cases.project_use_cases.complete_project import (
    CompleteProjectUseCase,
)
from app.application.use_cases.task_use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.task_use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.task_use_cases.get_filtered_tasks import (
    GetFilteredTasksUseCase,
)

SessionDep = Annotated[Session, Depends(get_session)]


def get_project_repository(
    session: SessionDep,
) -> SQLAlchemyProjectRepository:
    return SQLAlchemyProjectRepository(session=session)


def get_task_repository(
    session: SessionDep,
) -> SQLAlchemyTaskRepository:
    return SQLAlchemyTaskRepository(session=session)


ProjectRepositoryDep = Annotated[
    SQLAlchemyProjectRepository, Depends(get_project_repository)
]
TaskRepositoryDep = Annotated[SQLAlchemyTaskRepository, Depends(get_task_repository)]


def get_completion_service() -> ProjectCompletionService:
    settings = get_settings()
    return ProjectCompletionService(
        auto_complete_enabled=settings.AUTO_COMPLETE_PROJECTS
    )


def get_deadline_service() -> DeadlineEnforcementService:
    return DeadlineEnforcementService()


def get_create_project_use_case(
    project_repo: ProjectRepositoryDep,
) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repository=project_repo)


def get_complete_project_use_case(
    project_repo: ProjectRepositoryDep,
    task_repo: TaskRepositoryDep,
) -> CompleteProjectUseCase:
    return CompleteProjectUseCase(
        project_repository=project_repo, task_repository=task_repo
    )


def get_project_deadline_changed_handler(
    task_repo: TaskRepositoryDep,
    deadline_service: Annotated[
        DeadlineEnforcementService, Depends(get_deadline_service)
    ],
) -> ProjectDeadlineChangedHandler:
    return ProjectDeadlineChangedHandler(
        task_repository=task_repo, deadline_service=deadline_service
    )


def get_update_project_use_case(
    project_repo: ProjectRepositoryDep,
    deadline_handler: Annotated[
        ProjectDeadlineChangedHandler, Depends(get_project_deadline_changed_handler)
    ],
) -> UpdateProjectUseCase:
    settings = get_settings()
    return UpdateProjectUseCase(
        project_repository=project_repo,
        deadline_handler=deadline_handler,
        auto_adjust_task_deadlines=settings.AUTO_ADJUST_TASK_DEADLINES,
    )


def get_create_task_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
) -> CreateTaskUseCase:
    return CreateTaskUseCase(task_repository=task_repo, project_repository=project_repo)


def get_complete_task_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
    completion_service: Annotated[
        ProjectCompletionService, Depends(get_completion_service)
    ],
) -> CompleteTaskUseCase:
    return CompleteTaskUseCase(
        task_repository=task_repo,
        project_repository=project_repo,
        completion_service=completion_service,
    )


def get_filtered_tasks_use_case(
    task_repo: TaskRepositoryDep,
) -> GetFilteredTasksUseCase:
    return GetFilteredTasksUseCase(task_repository=task_repo)


def get_update_task_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
) -> UpdateTaskUseCase:
    return UpdateTaskUseCase(task_repository=task_repo, project_repository=project_repo)


def get_link_task_to_project_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
) -> LinkTaskToProjectUseCase:
    return LinkTaskToProjectUseCase(
        task_repository=task_repo, project_repository=project_repo
    )


def get_unlink_task_from_project_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
) -> UnlinkTaskToProjectUseCase:
    return UnlinkTaskToProjectUseCase(
        task_repository=task_repo, project_repository=project_repo
    )


def get_reopen_task_use_case(
    task_repo: TaskRepositoryDep,
    project_repo: ProjectRepositoryDep,
) -> ReopenTaskUseCase:
    return ReopenTaskUseCase(task_repository=task_repo, project_repository=project_repo)
