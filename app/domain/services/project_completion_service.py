from app.domain.entities.project import Project
from app.domain.entities.task import Task


class ProjectCompletionService:
    def __init__(self, auto_complete_enabled: bool) -> None:
        self.auto_complete_enabled = auto_complete_enabled

    def handle_task_completed(
        self, project: Project, all_project_tasks: list[Task]
    ) -> None:
        if project.should_auto_complete(all_project_tasks, self.auto_complete_enabled):
            project.mark_as_completed(all_project_tasks)

    @staticmethod
    def handle_task_reopened(project: Project) -> None:
        if project.is_completed:
            project.reopen()
