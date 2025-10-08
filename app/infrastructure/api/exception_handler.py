from fastapi import Request
from fastapi.responses import JSONResponse

from app.domain.exceptions import DomainError
from app.infrastructure.persistence.repositories.exceptions import (
    SQLAlchemyRepositoryError,
)


async def domain_exception_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.http_status_code,
        content={"detail": exc.message},
    )


async def repository_exception_handler(
    _request: Request, exc: SQLAlchemyRepositoryError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )
