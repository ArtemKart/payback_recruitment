from datetime import datetime, timezone, timedelta
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, Session
from starlette.testclient import TestClient

from app.infrastructure.api.main import app
from app.infrastructure.persistence.engine import get_session
from app.infrastructure.persistence.models.models import ProjectModel, TaskModel


@pytest.fixture(scope="function")
def test_db(tmp_path: Path):
    db_path = tmp_path / "test.db"

    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(test_db):
    with Session(test_db) as session:
        yield session
        session.rollback()


@pytest.fixture
def client(
    session: Session,
) -> TestClient:
    app.dependency_overrides[get_session] = lambda: session
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def project_model() -> ProjectModel:
    return ProjectModel(
        title="test_model",
        deadline=datetime.now(timezone.utc) + timedelta(days=10),
    )


@pytest.fixture
def task_model() -> TaskModel:
    return TaskModel(
        title="test_task",
        deadline=datetime.now(timezone.utc) + timedelta(days=1),
    )
