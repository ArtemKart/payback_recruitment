from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID

import pytest
from sqlmodel import Session
from starlette.testclient import TestClient

from app.infrastructure.api.schemas.project_schemas import ProjectCreate, ProjectUpdate
from app.infrastructure.persistence.models.models import ProjectModel, TaskModel
from tests.integration.infrastructure.api.routers.test_task_router import (
    _assert_object_are_equal,
)
from tests.utils import (
    to_project_entity,
    cast_datetime_to_sqlite_format,
    to_task_entity,
)


@pytest.fixture
def project_create_model() -> ProjectCreate:
    return ProjectCreate(
        title="test_title",
        deadline=datetime.now(timezone.utc) + timedelta(days=10),
    )


@pytest.fixture
def project_update_model() -> ProjectUpdate:
    return ProjectUpdate(title="new_title")


def test_get_all_projects_happy_path(
    client: TestClient, project_model: ProjectModel, session: Session
) -> None:
    session.add(project_model)
    session.commit()
    session.refresh(project_model)

    expected = [to_project_entity(project_model)]

    r = client.get("/projects/")

    assert r.status_code == 200
    tested = r.json()

    for t, e in zip(tested, expected):
        e = {k: v for k, v in asdict(e).items() if not k.startswith("_")}
        _assert_object_are_equal(tested=t, expected=e)


def test_get_project(
    client: TestClient,
    project_model: ProjectModel,
    session: Session,
) -> None:
    session.add(project_model)
    session.commit()
    session.refresh(project_model)

    r = client.get(f"/projects/{project_model.id}")

    assert r.status_code == 200
    tested = r.json()
    project = to_project_entity(project_model)
    expected = {k: v for k, v in asdict(project).items() if not k.startswith("_")}

    _assert_object_are_equal(tested, expected)


def test_get_project_404_not_found(client: TestClient) -> None:
    r = client.get(f"/projects/{uuid4()}")
    assert r.status_code == 404
    assert r.json()["detail"] == "Project not found"


def test_create_project_happy_path(
    client: TestClient,
    project_create_model: ProjectCreate,
    session: Session,
) -> None:
    r = client.post(f"/projects", data=project_create_model.model_dump_json())

    assert r.status_code == 201
    project_response = r.json()
    project = session.get(ProjectModel, UUID(project_response["id"]))

    assert project.id is not None
    assert project.title == project_response["title"] == project_create_model.title
    assert (
        cast_datetime_to_sqlite_format(project.deadline)
        == project_response["deadline"]
        == cast_datetime_to_sqlite_format(project_create_model.deadline)
    )
    assert project.is_completed == project_response["is_completed"]
    assert (
        cast_datetime_to_sqlite_format(project.created_at)
        == project_response["created_at"]
    )
    assert (
        cast_datetime_to_sqlite_format(project.updated_at)
        == project_response["updated_at"]
    )


def test_create_project_422_deadline_passed(
    client: TestClient,
    project_create_model: ProjectCreate,
) -> None:
    project_create_model.deadline = datetime.now(timezone.utc) + timedelta(days=-1)
    r = client.post(f"/projects", data=project_create_model.model_dump_json())
    assert r.status_code == 422
    assert r.json()["detail"] == "Project deadline has passed"


def test_update_project_happy_path(
    client: TestClient,
    project_update_model: ProjectUpdate,
    project_model: ProjectModel,
    session: Session,
) -> None:
    session.add(project_model)
    session.commit()
    session.refresh(project_model)
    assert project_model.title != project_update_model.title

    r = client.put(
        f"/projects/{project_model.id}",
        data=project_update_model.model_dump_json(),
    )

    assert r.status_code == 200
    tested = r.json()
    assert tested["title"] == project_model.title == project_update_model.title


def test_link_task_happy_path(
    client: TestClient,
    project_model: ProjectModel,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add_all([project_model, task_model])
    session.commit()
    session.refresh(project_model)
    session.refresh(task_model)

    assert not project_model.tasks
    assert task_model.project_id is None

    r = client.post(f"/projects/{project_model.id}/tasks/{task_model.id}/link")
    assert r.status_code == 200

    project = session.get(ProjectModel, project_model.id)

    assert task_model.project_id == project.id
    assert project.tasks[0].id == task_model.id


def test_link_task_404_task_not_found(
    client: TestClient,
    project_model: ProjectModel,
    session: Session,
) -> None:
    session.add(project_model)
    session.commit()
    session.refresh(project_model)
    r = client.post(f"/projects/{project_model.id}/tasks/{uuid4()}/link")

    assert r.status_code == 404
    assert r.json()["detail"] == "Task not found"


def test_link_task_404_project_not_found(
    client: TestClient,
    task_model: TaskModel,
    session: Session,
) -> None:
    session.add(task_model)
    session.commit()
    session.refresh(task_model)
    r = client.post(f"/projects/{uuid4()}/tasks/{task_model.id}/link")

    assert r.status_code == 404
    assert r.json()["detail"] == "Project not found"


def test_unlink_task_happy_path(
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

    assert task_model.project_id

    r = client.delete(f"/projects/{project_model.id}/tasks/{task_model.id}/unlink")

    assert r.status_code == 200
    assert r.json()["project_id"] is None
    assert task_model.project_id is None


def test_retrieve_tasks_happy_path(
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

    r = client.get(f"/projects/{project_model.id}/tasks")

    assert r.status_code == 200
    tested = r.json()[0]
    task = to_task_entity(task_model)

    expected = {k: v for k, v in asdict(task).items() if not k.startswith("_")}

    _assert_object_are_equal(tested, expected)
