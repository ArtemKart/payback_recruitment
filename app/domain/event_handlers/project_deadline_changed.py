from app.domain.events import ProjectDeadlineChangedEvent, DomainEvent
from app.domain.repositories.task_repository import TaskRepository
from app.domain.services.deadline_enforcement_service import DeadlineEnforcementService


class ProjectDeadlineChangedHandler:
    def __init__(
        self,
        task_repository: TaskRepository,
        deadline_service: DeadlineEnforcementService,
    ) -> None:
        self._task_repository = task_repository
        self._deadline_service = deadline_service

    def handle(
        self, event: ProjectDeadlineChangedEvent, auto_adjust: bool = False
    ) -> None:
        tasks = self._task_repository.get_by_project_id(event.project_id)
        if not tasks:
            return
        self._deadline_service.handle_project_deadline_changed(
            event, tasks, auto_adjust
        )
        for task in tasks:
            self._task_repository.update(task)
