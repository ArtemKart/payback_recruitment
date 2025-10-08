from app.domain.entities.task import Task
from app.domain.events import ProjectDeadlineChangedEvent
from app.domain.exceptions import ValidationError


class DeadlineEnforcementService:
    @staticmethod
    def handle_project_deadline_changed(
        event: ProjectDeadlineChangedEvent, tasks: list[Task], auto_adjust: bool = True
    ) -> None:
        if not event.new_deadline:
            return
        conflicting_tasks = [
            task
            for task in tasks
            if task.deadline and task.deadline > event.new_deadline
        ]
        if not conflicting_tasks:
            return
        if not auto_adjust:
            raise ValidationError("Project contains task(s) with later deadline(s)")
        for task in conflicting_tasks:
            task.adjust_deadline_to_project(event.new_deadline)
