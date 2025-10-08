from datetime import datetime, timezone, timedelta
from typing import Type
from uuid import UUID, uuid4

import pytest
from sqlmodel import Session, SQLModel
from starlette.testclient import TestClient

from app.infrastructure.api.schemas.task_schemas import TaskCreate, TaskUpdate
from app.infrastructure.persistence.models.models import TaskModel, ProjectModel
from tests.utils import cast_datetime_to_sqlite_format, to_task_entity


@pytest.fixture
def task_create_model() -> TaskCreate:
    return TaskCreate(
        title="test_title", deadline=datetime.now(timezone.utc) + timedelta(days=1)
    )


@pytest.fixture
def task_update_model() -> TaskUpdate:
    return TaskUpdate(title="new_title")


def _assert_object_are_equal(tested: dict[str, any], expected: dict[str, any]) -> None:
    assert len(tested) == len(expected)
    assert sorted(tested.keys()) == sorted(expected.keys())
    for attr, t_value in tested.items():
        exp_value = expected.get(attr)
        if isinstance(exp_value, datetime):
            assert t_value == cast_datetime_to_sqlite_format(exp_value)
            continue
        if isinstance(exp_value, UUID):
            assert t_value == exp_value.__str__()
            continue
        assert t_value == exp_value


def test_get_tasks_happy_path(
    client: TestClient, task_model: TaskModel, session: Session
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    expected = [to_task_entity(task_model)]

    r = client.get("/tasks")
    assert r.status_code == 200
    tested = r.json()
    for t, e in zip(tested, expected):
        _assert_object_are_equal(tested=t, expected=e.__dict__)


def test_get_task_happy_path(
    client: TestClient, task_model: TaskModel, session: Session
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    expected = to_task_entity(task_model)

    r = client.get(f"/tasks/{task_model.id}")
    assert r.status_code == 200
    tested = r.json()
    _assert_object_are_equal(tested=tested, expected=expected.__dict__)


def test_get_task_404_not_found(
    client: TestClient,
) -> None:
    r = client.get(f"/tasks/{uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


def test_create_task_happy_path(
    client: TestClient,
    task_create_model: TaskCreate,
    session: Session,
) -> None:
    r = client.post("/tasks", data=task_create_model.model_dump_json())
    assert r.status_code == 201
    tested_response = r.json()
    assert tested_response["id"] is not None
    task_entity = session.get(TaskModel, UUID(tested_response["id"]))
    assert task_entity.title == tested_response["title"] == task_create_model.title
    assert (
        task_entity.description
        == tested_response["description"]
        == task_create_model.description
    )
    assert (
        cast_datetime_to_sqlite_format(task_entity.deadline)
        == tested_response["deadline"]
        == cast_datetime_to_sqlite_format(task_create_model.deadline)
    )


def test_create_task_422_deadline_passed(
    client: TestClient,
    task_create_model: TaskCreate,
) -> None:
    task_create_model.deadline = datetime.now(timezone.utc) + timedelta(days=-1)
    r = client.post("/tasks", data=task_create_model.model_dump_json())
    assert r.status_code == 422
    assert r.json()["detail"] == "The task deadline has passed"


def test_update_existing_task_happy_path(
    client: TestClient,
    task_update_model: TaskUpdate,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    original_snapshot = task_model.model_dump()
    immutable_fields = {
        k: v
        for k, v in original_snapshot.items()
        if k not in task_update_model.model_dump(exclude_unset=True)
    }

    r = client.put(f"/tasks/{task_model.id}", data=task_update_model.model_dump_json())
    assert r.status_code == 200
    tested = r.json()
    assert tested["id"] is not None

    updated_task = session.get(TaskModel, UUID(tested["id"]))
    assert updated_task.title == task_update_model.title
    for field, value in immutable_fields.items():
        if not field == "updated_at":
            assert getattr(updated_task, field) == value
        else:
            assert getattr(updated_task, field) > value


def test_delete_task_happy_path(
    client: TestClient,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    r = client.delete(f"/tasks/{task_model.id}")

    assert r.status_code == 204

    task = session.get(TaskModel, task_model.id)
    assert task is None


def test_delete_task_404_task_not_found(
    client: TestClient,
) -> None:
    r = client.delete(f"/tasks/{uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


def test_complete_task_happy_path(
    client: TestClient,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    assert task_model.is_completed == False
    r = client.patch(f"/tasks/{task_model.id}/complete")

    updated_task = session.get(TaskModel, UUID(r.json()["id"]))
    assert updated_task.is_completed == r.json()["is_completed"] == True


def test_complete_task_with_project_complete_happy_path(
    client: TestClient,
    project_model: ProjectModel,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add(project_model)
    session.commit()
    session.refresh(project_model)

    task_model.project_id = project_model.id

    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    assert task_model.is_completed == False
    assert project_model.is_completed == False
    assert project_model.tasks[0] == task_model

    r = client.patch(f"/tasks/{task_model.id}/complete")
    assert r.status_code == 200

    updated_task = session.get(TaskModel, UUID(r.json()["id"]))
    updated_project = session.get(ProjectModel, project_model.id)

    assert updated_task.is_completed == True
    assert updated_project.is_completed == True


def test_reopen_unassigned_task_happy_path(
    client: TestClient,
    task_model: TaskModel,
    session: Session,
) -> None:
    task_model.is_completed = True
    session.add(task_model)
    session.commit()
    session.refresh(task_model)

    assert task_model.is_completed == True

    r = client.patch(f"/tasks/{task_model.id}/reopen")
    assert r.status_code == 200

    updated_task = session.get(TaskModel, UUID(r.json()["id"]))
    assert updated_task.is_completed == False


def test_reopen_assigned_task_happy_path(
    client: TestClient,
    project_model: ProjectModel,
    task_model: TaskModel,
    session: Session,
) -> None:
    project_model.is_completed = True

    session.add(project_model)
    session.commit()
    session.refresh(project_model)
    assert project_model.is_completed

    task_model.project_id = project_model.id
    task_model.is_completed = True

    session.add(task_model)
    session.commit()
    session.refresh(task_model)
    assert task_model.is_completed

    r = client.patch(f"/tasks/{task_model.id}/reopen")
    assert r.status_code == 200

    updated_task = session.get(TaskModel, UUID(r.json()["id"]))
    updated_project = session.get(ProjectModel, project_model.id)

    assert updated_task.project_id == updated_project.id
    assert updated_task.is_completed == False
    assert updated_project.is_completed == False
