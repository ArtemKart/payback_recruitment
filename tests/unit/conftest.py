from unittest.mock import Mock

import pytest

from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskRepository


@pytest.fixture
def task_repository() -> Mock:
    return Mock(spec=TaskRepository)


@pytest.fixture
def project_repository() -> Mock:
    return Mock(spec=ProjectRepository)
