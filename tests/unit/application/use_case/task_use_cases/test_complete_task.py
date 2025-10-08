import pytest
from uuid import UUID, uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from app.application.use_cases.task_use_cases.complete_task import CompleteTaskUseCase
from app.domain.entities.task import Task
from app.domain.entities.project import Project
from app.domain.exceptions import NotFoundError
from app.domain.services.project_completion_service import ProjectCompletionService


@pytest.fixture
def completion_service() -> Mock:
    return Mock(spec=ProjectCompletionService)


@pytest.fixture
def use_case(
    task_repository: Mock,
    project_repository: Mock,
    completion_service: Mock,
) -> CompleteTaskUseCase:
    return CompleteTaskUseCase(
        task_repository=task_repository,
        project_repository=project_repository,
        completion_service=completion_service,
    )


@pytest.fixture
def sample_task() -> Task:
    return Task(
        id=uuid4(),
        title="Test Task",
        description="Test Description",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=False,
        project_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )


@pytest.fixture
def sample_project() -> Project:
    return Project(
        id=uuid4(),
        title="Test Project",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )


def test_task_not_found(
    use_case: CompleteTaskUseCase,
    task_repository: Mock,
) -> None:
    task_id = uuid4()
    task_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        use_case.execute(task_id)

    assert str(exc_info.value) == "Task not found"
    task_repository.get_by_id.assert_called_once_with(task_id)
    task_repository.update.assert_not_called()


def test_task_without_project(
    use_case: CompleteTaskUseCase,
    task_repository: Mock,
    project_repository: Mock,
    completion_service: Mock,
    sample_task: Task,
) -> None:
    sample_task.project_id = None
    completed_task = Task(
        id=sample_task.id,
        title=sample_task.title,
        description=sample_task.description,
        deadline=sample_task.deadline,
        is_completed=True,
        project_id=None,
        created_at=sample_task.created_at,
        updated_at=sample_task.updated_at,
    )

    task_repository.get_by_id.return_value = sample_task
    task_repository.update.return_value = completed_task

    result = use_case.execute(sample_task.id)

    assert sample_task.is_completed is True
    task_repository.get_by_id.assert_called_once_with(sample_task.id)
    task_repository.update.assert_called_once_with(sample_task)

    project_repository.get_by_id.assert_not_called()

    assert result.id == completed_task.id
    assert result.is_completed is True


def test_task_with_project_not_found(
    use_case: CompleteTaskUseCase,
    task_repository: Mock,
    project_repository: Mock,
    completion_service: Mock,
    sample_task: Task,
) -> None:
    completed_task = Task(
        id=sample_task.id,
        title=sample_task.title,
        description=sample_task.description,
        deadline=sample_task.deadline,
        is_completed=True,
        project_id=sample_task.project_id,
        created_at=sample_task.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    task_repository.get_by_id.return_value = sample_task
    task_repository.update.return_value = completed_task
    project_repository.get_by_id.return_value = None

    result = use_case.execute(sample_task.id)

    task_repository.update.assert_called_once()
    project_repository.get_by_id.assert_called_once_with(sample_task.project_id)
    completion_service.handle_task_completed.assert_not_called()

    assert result.id == completed_task.id
    assert result.is_completed is True


def test_complete_flow(
    use_case: CompleteTaskUseCase,
    task_repository: Mock,
    project_repository: Mock,
    completion_service: Mock,
    sample_task: Task,
    sample_project: Project,
) -> None:
    completed_task = Task(
        id=sample_task.id,
        title=sample_task.title,
        description=sample_task.description,
        deadline=sample_task.deadline,
        is_completed=True,
        project_id=sample_task.project_id,
        created_at=sample_task.created_at,
        updated_at=datetime.now(timezone.utc),
    )

    sample_project.id = sample_task.project_id

    other_tasks = [
        Task(
            id=uuid4(),
            title="Other Task",
            description="desc",
            deadline=datetime.now(timezone.utc) + timedelta(days=30),
            is_completed=False,
            project_id=sample_task.project_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
    ]
    all_tasks = [completed_task] + other_tasks

    task_repository.get_by_id.return_value = sample_task
    task_repository.update.return_value = completed_task
    project_repository.get_by_id.return_value = sample_project
    task_repository.get_by_project_id.return_value = all_tasks

    result = use_case.execute(sample_task.id)

    task_repository.get_by_id.assert_called_once_with(sample_task.id)
    task_repository.update.assert_called_once_with(sample_task)
    project_repository.get_by_id.assert_called_once_with(sample_task.project_id)
    task_repository.get_by_project_id.assert_called_once_with(sample_task.project_id)
    completion_service.handle_task_completed.assert_called_once_with(
        sample_project, all_tasks
    )
    project_repository.update.assert_called_once_with(sample_project)

    assert result.id == completed_task.id
    assert result.is_completed is True
    assert result.project_id == sample_task.project_id


def test_returns_correct_dto_structure(
    use_case: CompleteTaskUseCase,
    task_repository: Mock,
) -> None:
    task = Task(
        id=uuid4(),
        title="Test Task",
        description="Description",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=False,
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )
    completed_task = Task(
        id=task.id,
        title=task.title,
        description=task.description,
        deadline=task.deadline,
        is_completed=True,
        project_id=None,
        created_at=task.created_at,
        updated_at=datetime.now(timezone.utc) + timedelta(minutes=30),
    )

    task_repository.get_by_id.return_value = task
    task_repository.update.return_value = completed_task

    result = use_case.execute(task.id)

    assert result.id == completed_task.id
    assert result.title == completed_task.title
    assert result.description == completed_task.description
    assert result.deadline == completed_task.deadline
    assert result.is_completed is True
    assert result.project_id is None
    assert result.created_at == completed_task.created_at
    assert result.updated_at == completed_task.updated_at
    assert hasattr(result, "is_overdue")
