from fastapi import FastAPI

from app.domain.exceptions import DomainError
from app.infrastructure.api.exception_handler import (
    domain_exception_handler,
    repository_exception_handler,
)
from app.infrastructure.api.routers import project_router, task_router
from app.infrastructure.persistence.engine import create_db_and_tables
from app.infrastructure.persistence.repositories.exceptions import (
    SQLAlchemyRepositoryError,
)

app = FastAPI(title="Task Management API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(project_router.router)
app.include_router(task_router.router)

app.add_exception_handler(DomainError, domain_exception_handler)
app.add_exception_handler(SQLAlchemyRepositoryError, repository_exception_handler)
