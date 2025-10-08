import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from app.application.dto.project_dto import UpdateProjectDTO
from app.application.use_cases.project_use_cases.update_project import (
    UpdateProjectUseCase,
)
from app.domain.entities.project import Project
from app.domain.event_handlers import ProjectDeadlineChangedHandler
from app.domain.exceptions import NotFoundError, ValidationError


@pytest.fixture
def deadline_handler() -> Mock:
    return Mock(spec=ProjectDeadlineChangedHandler)


@pytest.fixture
def use_case(
    project_repository: Mock,
    deadline_handler: Mock,
) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(
        project_repository=project_repository,
        deadline_handler=deadline_handler,
        auto_adjust_task_deadlines=True,
    )


@pytest.fixture
def sample_project() -> Project:
    return Project(
        id=uuid4(),
        title="Test Project",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_project_not_found(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
) -> None:
    project_id = uuid4()
    project_repository.get_by_id.return_value = None
    dto = UpdateProjectDTO(title="Updated Title")

    with pytest.raises(NotFoundError) as exc_info:
        use_case.execute(dto, project_id)

    assert str(exc_info.value) == "Project not found"
    project_repository.get_by_id.assert_called_once_with(project_id)
    project_repository.update.assert_not_called()


def test_deadline_in_past_raises_validation_error(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
    sample_project: Project,
) -> None:
    project_repository.get_by_id.return_value = sample_project
    past_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    dto = UpdateProjectDTO(deadline=past_deadline)

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(dto, sample_project.id)
    assert str(exc_info.value) == "Project deadline has passed"
    project_repository.update.assert_not_called()


def test_update_title_only(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
    deadline_handler: Mock,
    sample_project: Project,
) -> None:
    project_repository.get_by_id.return_value = sample_project
    dto = UpdateProjectDTO(title="Updated Title")

    result = use_case.execute(dto, sample_project.id)

    project_repository.get_by_id.assert_called_once_with(sample_project.id)
    project_repository.update.assert_called_once_with(sample_project)
    deadline_handler.handle.assert_not_called()

    assert result.id == sample_project.id
    assert result.title == "Updated Title"


def test_update_deadline_triggers_handler(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
    deadline_handler: Mock,
    sample_project: Project,
) -> None:
    project_repository.get_by_id.return_value = sample_project
    new_deadline = datetime.now(timezone.utc) + timedelta(days=60)
    dto = UpdateProjectDTO(deadline=new_deadline)

    result = use_case.execute(dto, sample_project.id)

    project_repository.get_by_id.assert_called_once_with(sample_project.id)
    project_repository.update.assert_called_once_with(sample_project)
    assert deadline_handler.handle.call_count >= 1
    assert result.deadline == new_deadline


def test_update_multiple_fields(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
    sample_project: Project,
) -> None:
    project_repository.get_by_id.return_value = sample_project
    new_deadline = datetime.now(timezone.utc) + timedelta(days=45)
    dto = UpdateProjectDTO(
        title="New Title",
        deadline=new_deadline,
    )

    result = use_case.execute(dto, sample_project.id)

    project_repository.update.assert_called_once_with(sample_project)

    assert result.title == "New Title"
    assert result.deadline == new_deadline
    assert result.is_completed == sample_project.is_completed


def test_returns_correct_dto_structure(
    use_case: UpdateProjectUseCase,
    project_repository: Mock,
    sample_project: Project,
) -> None:
    project_repository.get_by_id.return_value = sample_project
    dto = UpdateProjectDTO(title="Updated")

    result = use_case.execute(dto, sample_project.id)

    assert result.id == sample_project.id
    assert result.title == "Updated"
    assert result.deadline == sample_project.deadline
    assert result.is_completed == sample_project.is_completed
    assert result.created_at == sample_project.created_at
    assert result.updated_at == sample_project.updated_at
