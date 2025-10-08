from copy import deepcopy

from app.application.use_cases.task_use_cases.task_use_case import TaskUseCase
from app.domain.repositories.task_repository import TaskRepository
from app.application.dto.task_dto import TaskDTO, TaskFilterDTO


class GetFilteredTasksUseCase(TaskUseCase):

    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    def execute(self, filters: TaskFilterDTO) -> list[TaskDTO]:
        tasks = self._task_repository.get_all()
        filtered_tasks = deepcopy(tasks)
        if filters.project_id is not None:
            filtered_tasks = [
                t for t in filtered_tasks if t.project_id == filters.project_id
            ]
        if filters.is_completed is not None:
            filtered_tasks = [
                t for t in filtered_tasks if t.is_completed == filters.is_completed
            ]
        if filters.is_overdue is not None:
            if filters.is_overdue:
                filtered_tasks = [t for t in filtered_tasks if t.is_overdue()]
            else:
                filtered_tasks = [t for t in filtered_tasks if not t.is_overdue()]
        return [self._to_dto(task) for task in filtered_tasks]
