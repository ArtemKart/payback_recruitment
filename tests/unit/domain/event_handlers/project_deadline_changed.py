from datetime import datetime, timezone, timedelta
from uuid import uuid4

import pytest
from unittest.mock import Mock

from app.domain.event_handlers import ProjectDeadlineChangedHandler
from app.domain.events import ProjectDeadlineChangedEvent


@pytest.fixture
def deadline_service() -> Mock:
    return Mock()


@pytest.fixture
def handler(
    task_repository: Mock, deadline_service: Mock
) -> ProjectDeadlineChangedHandler:
    return ProjectDeadlineChangedHandler(task_repository, deadline_service)


@pytest.fixture
def event() -> ProjectDeadlineChangedEvent:
    return ProjectDeadlineChangedEvent(
        occurred_at=datetime.now(timezone.utc),
        project_id=uuid4(),
        old_deadline=datetime.now(timezone.utc) + timedelta(days=1),
        new_deadline=datetime.now(timezone.utc) + timedelta(days=30),
    )


def test_returns_early_when_no_tasks(
    handler: ProjectDeadlineChangedHandler,
    task_repository: Mock,
    deadline_service: Mock,
    event: ProjectDeadlineChangedEvent,
) -> None:
    task_repository.get_by_project_id.return_value = []

    handler.handle(event)

    task_repository.get_by_project_id.assert_called_once_with(event.project_id)
    deadline_service.handle_project_deadline_changed.assert_not_called()
    task_repository.update.assert_not_called()


def test_processes_tasks_when_tasks_exist(
    handler: ProjectDeadlineChangedHandler,
    task_repository: Mock,
    deadline_service: Mock,
    event: ProjectDeadlineChangedEvent,
) -> None:
    task1 = Mock()
    task2 = Mock()
    tasks = [task1, task2]
    auto_adjust = True
    task_repository.get_by_project_id.return_value = tasks

    handler.handle(event, auto_adjust=auto_adjust)

    task_repository.get_by_project_id.assert_called_once_with(event.project_id)
    deadline_service.handle_project_deadline_changed.assert_called_once_with(
        event, tasks, auto_adjust
    )
    assert task_repository.update.call_count == 2
    task_repository.update.assert_any_call(task1)
    task_repository.update.assert_any_call(task2)
