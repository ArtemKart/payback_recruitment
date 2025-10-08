import pytest
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from app.application.dto.task_dto import TaskFilterDTO
from app.application.use_cases.task_use_cases.get_filtered_tasks import (
    GetFilteredTasksUseCase,
)
from app.domain.entities.task import Task


@pytest.fixture
def use_case(task_repository: Mock) -> GetFilteredTasksUseCase:
    return GetFilteredTasksUseCase(task_repository=task_repository)


@pytest.fixture
def sample_tasks() -> list[Task]:
    project_id_1 = uuid4()
    project_id_2 = uuid4()
    now = datetime.now(timezone.utc)
    past_date = now - timedelta(days=10)
    future_date = now + timedelta(days=10)

    return [
        Task(
            id=uuid4(),
            title="Completed Task in Project 1",
            description="Description 1",
            deadline=future_date,
            is_completed=True,
            project_id=project_id_1,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Incomplete Task in Project 1",
            description="Description 2",
            deadline=future_date,
            is_completed=False,
            project_id=project_id_1,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Overdue Task in Project 2",
            description="Description 3",
            deadline=past_date,
            is_completed=False,
            project_id=project_id_2,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Completed Overdue Task in Project 2",
            description="Description 4",
            deadline=past_date,
            is_completed=True,
            project_id=project_id_2,
            created_at=now,
            updated_at=now,
        ),
        Task(
            id=uuid4(),
            title="Task without Project",
            description="Description 5",
            deadline=future_date,
            is_completed=False,
            project_id=None,
            created_at=now,
            updated_at=now,
        ),
    ]


def test_no_filters_returns_all_tasks(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=None,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    task_repository.get_all.assert_called_once()
    assert len(result) == 5
    assert all(hasattr(task, "id") for task in result)


def test_filter_by_project_id(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    project_id = sample_tasks[0].project_id
    filters = TaskFilterDTO(
        project_id=project_id,
        is_completed=None,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    assert len(result) == 2
    assert all(task.project_id == project_id for task in result)


def test_filter_by_is_completed_true(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters: TaskFilterDTO = TaskFilterDTO(
        project_id=None,
        is_completed=True,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    assert len(result) == 2
    assert all(task.is_completed is True for task in result)


def test_filter_by_is_completed_false(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=False,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    assert len(result) == 3
    assert all(task.is_completed is False for task in result)


def test_filter_by_is_overdue_true(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=None,
        is_overdue=True,
    )

    result = use_case.execute(filters)

    assert len(result) == 1
    assert result[0].is_overdue == True


def test_filter_by_is_overdue_false(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=None,
        is_overdue=False,
    )

    result = use_case.execute(filters)

    assert len(result) == 4
    assert all(not task.is_overdue for task in result)


def test_filter_by_project_and_completed(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    project_id = sample_tasks[0].project_id
    filters = TaskFilterDTO(
        project_id=project_id,
        is_completed=True,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    assert len(result) == 1
    assert result[0].project_id == project_id
    assert result[0].is_completed is True


def test_filter_by_project_and_overdue(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    project_id = sample_tasks[2].project_id
    filters = TaskFilterDTO(
        project_id=project_id,
        is_completed=None,
        is_overdue=True,
    )

    result = use_case.execute(filters)

    assert len(result) == 1
    assert result[0].project_id == project_id
    assert result[0].is_overdue


def test_all_filters_combined(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    project_id = sample_tasks[2].project_id
    filters = TaskFilterDTO(
        project_id=project_id,
        is_completed=False,
        is_overdue=True,
    )

    result = use_case.execute(filters)

    assert len(result) == 1
    assert result[0].project_id == project_id
    assert result[0].is_completed is False
    assert result[0].is_overdue is True


def test_filters_return_empty_list(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    non_existent_project_id = uuid4()
    filters = TaskFilterDTO(
        project_id=non_existent_project_id,
        is_completed=None,
        is_overdue=None,
    )

    result = use_case.execute(filters)
    assert len(result) == 0


def test_empty_repository(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
) -> None:
    task_repository.get_all.return_value = []
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=None,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    task_repository.get_all.assert_called_once()
    assert len(result) == 0


def test_returns_correct_dto_structure(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
) -> None:
    task = Task(
        id=uuid4(),
        title="Test Task",
        description="Description",
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
        is_completed=False,
        project_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    task_repository.get_all.return_value = [task]
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=None,
        is_overdue=None,
    )

    result = use_case.execute(filters)

    assert len(result) == 1
    dto = result[0]
    assert dto.id == task.id
    assert dto.title == task.title
    assert dto.description == task.description
    assert dto.deadline == task.deadline
    assert dto.is_completed == task.is_completed
    assert dto.project_id == task.project_id
    assert dto.created_at == task.created_at
    assert dto.updated_at == task.updated_at
    assert hasattr(dto, "is_overdue")


def test_filter_tasks_without_project(
    use_case: GetFilteredTasksUseCase,
    task_repository: Mock,
    sample_tasks: list[Task],
) -> None:
    task_repository.get_all.return_value = sample_tasks
    filters = TaskFilterDTO(
        project_id=None,
        is_completed=False,
        is_overdue=False,
    )

    result = use_case.execute(filters)

    tasks_without_project = [task for task in result if task.project_id is None]
    assert len(tasks_without_project) == 1
    assert tasks_without_project[0].title == "Task without Project"
