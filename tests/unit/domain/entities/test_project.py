import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.domain.entities.project import Project
from app.domain.entities.task import Task
from app.domain.exceptions import ConflictError, ValidationError
from app.domain.events import ProjectDeadlineChangedEvent


@pytest.fixture
def project() -> Project:
    return Project(
        id=uuid4(),
        title="Test Project",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def completed_project() -> Project:
    return Project(
        id=uuid4(),
        title="Completed Project",
        deadline=datetime.now(timezone.utc) + timedelta(days=30),
        is_completed=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def completed_task() -> Task:
    return Task(
        id=uuid4(),
        project_id=uuid4(),
        description="test_description",
        deadline=datetime.now(timezone.utc) + timedelta(days=10),
        title="Completed Task",
        is_completed=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def incomplete_task() -> Task:
    return Task(
        id=uuid4(),
        project_id=uuid4(),
        description="test_description",
        title="Incomplete Task",
        deadline=datetime.now(timezone.utc) + timedelta(days=10),
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def test_create_project_with_valid_data() -> None:
    project_id = uuid4()
    title = "Test Project"
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=30)

    project = Project(
        id=project_id,
        title=title,
        deadline=deadline,
        is_completed=False,
        created_at=now,
        updated_at=now,
    )

    assert project.id == project_id
    assert project.title == title
    assert project.deadline == deadline
    assert project.is_completed is False
    assert project.created_at == now
    assert project.updated_at == now
    assert project._domain_events == []


def test_post_init_initializes_empty_events_list():
    project = Project(
        id=uuid4(),
        title="Test",
        deadline=datetime.now(timezone.utc),
        is_completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    assert isinstance(project._domain_events, list)
    assert len(project._domain_events) == 0


def test_mark_as_completed_with_all_tasks_completed(
    project: Project, completed_task: Task
) -> None:
    before_update = project.updated_at
    tasks = [completed_task]

    project.mark_as_completed(tasks)

    assert project.is_completed is True
    assert project.updated_at > before_update


def test_mark_as_completed_with_empty_task_list(project: Project) -> None:
    project.mark_as_completed([])

    assert project.is_completed is True


def test_mark_as_completed_with_incomplete_tasks_raises_error(
    project: Project, completed_task: Task, incomplete_task: Task
) -> None:
    tasks = [completed_task, incomplete_task]

    with pytest.raises(ValidationError) as exc_info:
        project.mark_as_completed(tasks)

    assert (
        str(exc_info.value) == "Cannot complete project. Task(s) are still incomplete"
    )
    assert project.is_completed is False


def test_mark_as_completed_when_already_completed_raises_error(
    completed_project: Project,
    completed_task: Task,
) -> None:
    with pytest.raises(ConflictError) as exc_info:
        completed_project.mark_as_completed([completed_task])

    assert str(exc_info.value) == "Project is already completed"


def test_mark_as_completed_with_multiple_completed_tasks(project: Project) -> None:
    tasks = [
        Task(
            id=uuid4(),
            project_id=project.id,
            description="test_descr",
            deadline=datetime.now(timezone.utc) + timedelta(days=10),
            title=f"Task {i}",
            is_completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(3)
    ]

    project.mark_as_completed(tasks)

    assert project.is_completed is True


def test_reopen_completed_project(completed_project: Project) -> None:
    before_update = completed_project.updated_at

    completed_project.reopen()

    assert completed_project.is_completed is False
    assert completed_project.updated_at > before_update


def test_reopen_already_opened_project_raises_error(project: Project) -> None:
    assert project.is_completed == False
    with pytest.raises(ConflictError) as exc_info:
        project.reopen()

    assert str(exc_info.value) == "Project is already opened"
    assert project.is_completed is False


def test_update_deadline_with_new_date(project: Project) -> None:
    old_deadline = project.deadline
    new_deadline = project.deadline + timedelta(days=60)
    before_update = project.updated_at

    project.update_deadline(new_deadline)

    assert project.deadline == new_deadline
    assert project.updated_at > before_update
    assert len(project._domain_events) == 1

    event = project._domain_events[0]
    assert isinstance(event, ProjectDeadlineChangedEvent)
    assert event.project_id == project.id
    assert event.old_deadline == old_deadline
    assert event.new_deadline == new_deadline


def test_update_deadline_with_same_date_no_event(project: Project) -> None:
    same_deadline = project.deadline

    project.update_deadline(same_deadline)

    assert project.deadline == same_deadline
    assert len(project._domain_events) == 0


def test_update_deadline_multiple_times(project: Project) -> None:
    first_deadline = datetime.now(timezone.utc) + timedelta(days=45)
    second_deadline = datetime.now(timezone.utc) + timedelta(days=60)

    project.update_deadline(first_deadline)
    project.update_deadline(second_deadline)

    assert project.deadline == second_deadline
    assert len(project._domain_events) == 2


def test_update_deadline_updates_timestamp(project: Project) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=60)
    old_updated_at = project.updated_at

    project.update_deadline(new_deadline)

    assert project.updated_at > old_updated_at


def test_update_deadline_to_past_date(project: Project) -> None:
    past_deadline = datetime.now(timezone.utc) - timedelta(days=10)

    project.update_deadline(past_deadline)

    assert project.deadline == past_deadline
    assert len(project._domain_events) == 1


def test_should_auto_complete_all_conditions_met(
    project: Project,
    completed_task: Task,
) -> None:
    result = project.should_auto_complete([completed_task], auto_complete_enabled=True)
    assert result is True


def test_should_auto_complete_feature_disabled(
    project: Project, completed_task: Task
) -> None:
    result = project.should_auto_complete([completed_task], auto_complete_enabled=False)
    assert result is False


def test_should_auto_complete_project_already_completed(
    completed_project: Project,
    completed_task: Task,
) -> None:
    result = completed_project.should_auto_complete(
        [completed_task], auto_complete_enabled=True
    )

    assert result is False


def test_should_auto_complete_with_incomplete_tasks(
    project: Project, completed_task: Task, incomplete_task: Task
) -> None:
    tasks = [completed_task, incomplete_task]
    result = project.should_auto_complete(tasks, auto_complete_enabled=True)
    assert result is False


def test_should_auto_complete_with_empty_task_list(project: Project) -> None:
    result = project.should_auto_complete([], auto_complete_enabled=True)
    assert result is False


def test_should_auto_complete_with_multiple_completed_tasks(project: Project) -> None:
    tasks = [
        Task(
            id=uuid4(),
            project_id=project.id,
            description="test_descr",
            deadline=datetime.now(timezone.utc) + timedelta(days=10),
            title=f"Task {i}",
            is_completed=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(5)
    ]

    result = project.should_auto_complete(tasks, auto_complete_enabled=True)

    assert result is True


def test_should_auto_complete_with_one_incomplete_task_among_many(
    project: Project,
) -> None:
    tasks = [
        Task(
            id=uuid4(),
            project_id=project.id,
            description="test_descr",
            deadline=datetime.now(timezone.utc) + timedelta(days=10),
            title=f"Task {i}",
            is_completed=True if i != 2 else False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        for i in range(5)
    ]

    result = project.should_auto_complete(tasks, auto_complete_enabled=True)

    assert result is False


def test_collect_domain_events_returns_events_and_clears_list(project: Project) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=60)
    project.update_deadline(new_deadline)

    assert len(project._domain_events) == 1

    events = project.collect_domain_events()

    assert len(events) == 1
    assert isinstance(events[0], ProjectDeadlineChangedEvent)
    assert len(project._domain_events) == 0


def test_collect_domain_events_with_no_events(project: Project) -> None:
    events = project.collect_domain_events()

    assert events == []
    assert len(project._domain_events) == 0


def test_collect_domain_events_multiple_times(project: Project) -> None:
    project.update_deadline(datetime.now(timezone.utc) + timedelta(days=60))

    first_collection = project.collect_domain_events()
    second_collection = project.collect_domain_events()

    assert len(first_collection) == 1
    assert len(second_collection) == 0


def test_collect_domain_events_returns_copy(project: Project) -> None:
    new_deadline = datetime.now(timezone.utc) + timedelta(days=60)
    project.update_deadline(new_deadline)

    events = project.collect_domain_events()
    events.append("modified")  # noqa

    assert len(project._domain_events) == 0


def test_collect_domain_events_with_multiple_deadline_changes(project: Project) -> None:
    project.update_deadline(datetime.now(timezone.utc) + timedelta(days=60))
    project.update_deadline(datetime.now(timezone.utc) + timedelta(days=90))
    project.update_deadline(datetime.now(timezone.utc) + timedelta(days=120))

    events = project.collect_domain_events()

    assert len(events) == 3
    assert all(isinstance(e, ProjectDeadlineChangedEvent) for e in events)
    assert len(project._domain_events) == 0
