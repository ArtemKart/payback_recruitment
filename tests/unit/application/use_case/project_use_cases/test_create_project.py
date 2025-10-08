import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock

from app.application.dto.project_dto import CreateProjectDTO
from app.application.use_cases.project_use_cases.create_project import (
    CreateProjectUseCase,
)
from app.domain.entities.project import Project
from app.domain.exceptions import ValidationError


@pytest.fixture
def use_case(project_repository: Mock) -> CreateProjectUseCase:
    return CreateProjectUseCase(project_repository=project_repository)


def test_deadline_in_past_raises_validation_error(
    use_case: CreateProjectUseCase,
    project_repository: Mock,
) -> None:
    past_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    dto = CreateProjectDTO(
        title="Test Project",
        deadline=past_deadline,
    )

    with pytest.raises(ValidationError) as exc_info:
        use_case.execute(dto)

    project_repository.save.assert_not_called()
    assert str(exc_info.value) == "Project deadline has passed"


def test_creates_project_successfully(
    use_case: CreateProjectUseCase,
    project_repository: Mock,
) -> None:
    future_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    dto = CreateProjectDTO(
        title="New Project",
        deadline=future_deadline,
    )

    saved_project = Project(
        id=dto.id if hasattr(dto, "id") else Mock(),
        title=dto.title,
        deadline=dto.deadline,
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    project_repository.save.return_value = saved_project

    result = use_case.execute(dto)

    project_repository.save.assert_called_once()
    saved_arg = project_repository.save.call_args[0][0]

    assert saved_arg.title == "New Project"
    assert saved_arg.deadline == future_deadline
    assert saved_arg.is_completed is False
    assert result.title == saved_project.title


def test_returns_correct_dto_structure(
    use_case: CreateProjectUseCase,
    project_repository: Mock,
) -> None:
    future_deadline = datetime.now(timezone.utc) + timedelta(days=15)
    dto = CreateProjectDTO(
        title="Test Project",
        deadline=future_deadline,
    )

    saved_project = Project(
        id=Mock(),
        title=dto.title,
        deadline=dto.deadline,
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    project_repository.save.return_value = saved_project

    result = use_case.execute(dto)

    assert result.id == saved_project.id
    assert result.title == saved_project.title
    assert result.deadline == saved_project.deadline
    assert result.is_completed is False
    assert result.created_at == saved_project.created_at
    assert result.updated_at == saved_project.updated_at
