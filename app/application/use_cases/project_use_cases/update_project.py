from datetime import datetime, timezone
from uuid import UUID

from app.application.dto.project_dto import UpdateProjectDTO, ProjectDTO
from app.application.use_cases.project_use_cases.project_use_case import ProjectUseCase
from app.domain.event_handlers import ProjectDeadlineChangedHandler
from app.domain.exceptions import NotFoundError, ValidationError
from app.domain.repositories.project_repository import ProjectRepository


class UpdateProjectUseCase(ProjectUseCase):
    def __init__(
        self,
        project_repository: ProjectRepository,
        deadline_handler: ProjectDeadlineChangedHandler,
        auto_adjust_task_deadlines: bool = True,
    ) -> None:
        self._project_repository = project_repository
        self._deadline_handler = deadline_handler
        self._auto_adjust = auto_adjust_task_deadlines

    def execute(self, dto: UpdateProjectDTO, project_id: UUID) -> ProjectDTO:
        project = self._project_repository.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found")
        if dto.deadline:
            if dto.deadline < datetime.now(timezone.utc):
                raise ValidationError("Project deadline has passed")
            project.update_deadline(dto.deadline)
            events = project.collect_domain_events()
            for event in events:
                self._deadline_handler.handle(event, auto_adjust=self._auto_adjust)
        [setattr(project, k, v) for k, v in dto.__dict__.items() if v is not None]
        self._project_repository.update(project)
        return self._to_dto(project)
