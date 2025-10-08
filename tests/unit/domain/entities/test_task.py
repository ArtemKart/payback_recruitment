import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.domain.entities.task import Task
from app.domain.exceptions import ConflictError, ValidationError


@pytest.fixture
def task() -> Task:
    return Task(
        id=uuid4(),
        title="Test Task",
        description="Test description",
        deadline=datetime.now(timezone.utc) + timedelta(days=7),
        is_completed=False,
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def completed_task() -> Task:
    return Task(
        id=uuid4(),
        title="Completed Task",
        description="Completed description",
        deadline=datetime.now(timezone.utc) + timedelta(days=7),
        is_completed=True,
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def assigned_task() -> Task:
    return Task(
        id=uuid4(),
        title="Assigned Task",
        description="Task assigned to project",
        deadline=datetime.now(timezone.utc) + timedelta(days=7),
        is_completed=False,
        project_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def task_without_deadline() -> Task:
    return Task(
        id=uuid4(),
        title="Task without deadline",
        description="No deadline set",
        deadline=None,
        is_completed=False,
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_create_task_with_valid_data() -> None:
    task_id = uuid4()
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=7)
    project_id = uuid4()

    task: Task = Task(
        id=task_id,
        title="Test Task",
        description="Test description",
        deadline=deadline,
        is_completed=False,
        project_id=project_id,
        created_at=now,
        updated_at=now,
    )

    assert task.id == task_id
    assert task.title == "Test Task"
    assert task.description == "Test description"
    assert task.deadline == deadline
    assert task.is_completed is False
    assert task.project_id == project_id
    assert task.created_at == now
    assert task.updated_at == now


def test_create_task_with_optional_fields_none() -> None:
    task: Task = Task(
        id=uuid4(),
        title="Minimal Task",
        description=None,
        deadline=None,
        is_completed=False,
        project_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert task.description is None
    assert task.deadline is None
    assert task.project_id is None


def test_mark_as_completed(task: Task) -> None:
    before_update = task.updated_at

    task.mark_as_completed()

    assert task.is_completed is True
    assert task.updated_at > before_update


def test_mark_as_completed_when_already_completed(completed_task: Task) -> None:
    with pytest.raises(ConflictError) as exc_info:
        completed_task.mark_as_completed()

    assert str(exc_info.value) == "Task is already completed"


def test_mark_as_completed_updates_timestamp(task: Task) -> None:
    old_updated_at = task.updated_at
    task.mark_as_completed()
    assert task.updated_at > old_updated_at


def test_reopen_completed_task(completed_task: Task) -> None:
    before_update = completed_task.updated_at

    completed_task.reopen()

    assert completed_task.is_completed is False
    assert completed_task.updated_at > before_update


def test_reopen_already_opened_task_raises_error(task: Task) -> None:
    with pytest.raises(ConflictError) as exc_info:
        task.reopen()

    assert str(exc_info.value) == "Task is already opened"
    assert task.is_completed is False


def test_reopen_updates_timestamp(completed_task: Task) -> None:
    old_updated_at = completed_task.updated_at
    completed_task.reopen()
    assert completed_task.updated_at > old_updated_at


def test_assign_to_project(task: Task) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    before_update = task.updated_at

    task.assign_to_project(project_id, project_deadline)

    assert task.project_id == project_id
    assert task.updated_at > before_update


def test_assign_to_project_when_already_assigned(assigned_task: Task) -> None:
    new_project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)

    with pytest.raises(ConflictError) as exc_info:
        assigned_task.assign_to_project(new_project_id, project_deadline)

    assert str(exc_info.value) == "Task is already assigned"


def test_assign_to_project_with_invalid_task_deadline(task: Task) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=3)
    task.deadline = datetime.now(timezone.utc) + timedelta(days=10)

    with pytest.raises(ValidationError) as exc_info:
        task.assign_to_project(project_id, project_deadline)

    assert str(exc_info.value) == "Task deadline cannot be later than project deadline"
    assert task.project_id is None


def test_assign_to_project_with_no_task_deadline(task_without_deadline: Task) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)

    task_without_deadline.assign_to_project(project_id, project_deadline)
    assert task_without_deadline.project_id == project_id


def test_assign_to_project_with_no_project_deadline(task: Task) -> None:
    project_id = uuid4()
    task.assign_to_project(project_id, None)
    assert task.project_id == project_id


def test_assign_to_project_with_task_d_before_project_d(task: Task) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    task.deadline = datetime.now(timezone.utc) + timedelta(days=5)

    task.assign_to_project(project_id, project_deadline)

    assert task.project_id == project_id


def test_unassign_from_project(assigned_task: Task) -> None:
    before_update = assigned_task.updated_at

    assigned_task.unassign_from_project()
    assert assigned_task.project_id is None
    assert assigned_task.updated_at > before_update


def test_unassign_from_project_when_not_assigned(task: Task) -> None:
    with pytest.raises(ConflictError) as exc_info:
        task.unassign_from_project()
    assert str(exc_info.value) == "Task is not assigned"


def test_unassign_from_project_updates_timestamp(assigned_task: Task) -> None:
    old_updated_at = assigned_task.updated_at
    assigned_task.unassign_from_project()
    assert assigned_task.updated_at > old_updated_at


def test_update_deadline(task: Task) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=14)
    before_update = task.updated_at

    task.update_deadline(new_deadline)
    assert task.deadline == new_deadline
    assert task.updated_at > before_update


def test_update_deadline_to_none(task: Task) -> None:
    task.update_deadline(None)
    assert task.deadline is None


def test_update_deadline_for_assigned_task_with_validation(assigned_task: Task) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=5)
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)

    assigned_task.update_deadline(new_deadline, project_deadline)

    assert assigned_task.deadline == new_deadline


def test_update_deadline_for_assigned_task_exceeding_project_deadline(
    assigned_task: Task,
) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=40)
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)

    with pytest.raises(ValidationError) as exc_info:
        assigned_task.update_deadline(new_deadline, project_deadline)
    assert str(exc_info.value) == "Task deadline cannot be later than project deadline"


def test_update_deadline_for_unassigned_task_without_project_deadline(
    task: Task,
) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=100)
    task.update_deadline(new_deadline)
    assert task.deadline == new_deadline


def test_update_deadline_updates_timestamp(task: Task) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=14)
    old_updated_at = task.updated_at
    task.update_deadline(new_deadline)
    assert task.updated_at > old_updated_at


def test_update_deadline_for_assigned_task_no_project_deadline(
    assigned_task: Task,
) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=100)
    assigned_task.update_deadline(new_deadline)
    assert assigned_task.deadline == new_deadline


def test_adjust_task_deadline_to_project_deadline_if_exceed(task: Task) -> None:
    task.deadline = datetime.now(timezone.utc) + timedelta(days=40)
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    before_update = task.updated_at

    task.adjust_deadline_to_project(project_deadline)
    assert task.deadline == project_deadline
    assert task.updated_at > before_update


def test_adjust_task_deadline_to_project_deadline_if_before(task: Task) -> None:
    original_deadline = datetime.now(timezone.utc) + timedelta(days=5)
    task.deadline = original_deadline
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    old_updated_at = task.updated_at

    task.adjust_deadline_to_project(project_deadline)

    assert task.deadline == original_deadline
    assert task.updated_at == old_updated_at


def test_adjust_deadline_to_project_when_task_has_no_deadline(
    task_without_deadline: Task,
) -> None:
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    old_updated_at = task_without_deadline.updated_at

    task_without_deadline.adjust_deadline_to_project(project_deadline)
    assert task_without_deadline.deadline is None
    assert task_without_deadline.updated_at == old_updated_at


def test_adjust_deadline_to_project_when_deadlines_are_equal(task: Task) -> None:
    project_deadline = datetime.now(timezone.utc) + timedelta(days=7)
    task.deadline = project_deadline
    old_updated_at = task.updated_at

    task.adjust_deadline_to_project(project_deadline)
    assert task.deadline == project_deadline
    assert task.updated_at == old_updated_at


def test_is_overdue_when_deadline_passed(task: Task) -> None:
    task.deadline = datetime.now(timezone.utc) - timedelta(days=1)
    assert task.is_overdue() is True


def test_is_overdue_when_deadline_not_passed(task: Task) -> None:
    task.deadline = datetime.now(timezone.utc) + timedelta(days=1)
    assert task.is_overdue() is False


def test_is_overdue_when_no_deadline(task_without_deadline: Task) -> None:
    assert task_without_deadline.is_overdue() is False


def test_is_overdue_when_task_is_completed(completed_task: Task) -> None:
    completed_task.deadline = datetime.now(timezone.utc) - timedelta(days=1)
    assert completed_task.is_overdue() is False


def test_is_overdue_when_completed_with_future_deadline(completed_task: Task) -> None:
    completed_task.deadline = datetime.now(timezone.utc) + timedelta(days=10)
    assert completed_task.is_overdue() is False


def test_is_overdue_when_incomplete_with_past_deadline(task: Task) -> None:
    task.deadline = datetime.now(timezone.utc) - timedelta(hours=1)
    task.is_completed = False

    assert task.is_overdue() is True


def test_validate_deadline_against_project_deadline_with_valid_deadlines(
    task: Task,
) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=30)
    task.deadline = datetime.now(timezone.utc) + timedelta(days=10)

    task.assign_to_project(project_id, project_deadline)
    assert task.project_id == project_id


def test_validate_deadline_against_project_deadline_with_invalid_deadlines(
    task: Task,
) -> None:
    project_id = uuid4()
    project_deadline = datetime.now(timezone.utc) + timedelta(days=5)
    task.deadline = datetime.now(timezone.utc) + timedelta(days=10)

    with pytest.raises(ValidationError) as exc_info:
        task.assign_to_project(project_id, project_deadline)
    assert str(exc_info.value) == "Task deadline cannot be later than project deadline"


def test_validate_deadline_against_project_with_none_deadlines(
    task_without_deadline: Task,
) -> None:
    project_id = uuid4()
    task_without_deadline.assign_to_project(project_id, None)
    assert task_without_deadline.project_id == project_id
