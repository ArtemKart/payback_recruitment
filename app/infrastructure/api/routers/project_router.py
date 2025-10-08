from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.use_cases.project_use_cases.update_project import (
    UpdateProjectUseCase,
)
from app.application.use_cases.task_use_cases.link_task_to_project import (
    LinkTaskToProjectUseCase,
)
from app.application.use_cases.task_use_cases.unlink_task_from_project import (
    UnlinkTaskToProjectUseCase,
)
from app.domain.repositories.project_repository import ProjectRepository
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.api.schemas.project_schemas import (
    ProjectCreate,
    ProjectUpdate,
    ProjectRead,
)
from app.infrastructure.api.dependencies import (
    get_create_project_use_case,
    get_project_repository,
    get_update_project_use_case,
    get_task_repository,
    get_link_task_to_project_use_case,
    get_unlink_task_from_project_use_case,
)
from app.application.use_cases.project_use_cases.create_project import (
    CreateProjectUseCase,
)
from app.application.dto.project_dto import CreateProjectDTO, UpdateProjectDTO
from app.infrastructure.api.schemas.task_schemas import TaskRead

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/", response_model=list[ProjectRead])
def get_all_projects(
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
):
    return repo.get_all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID,
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
):
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return project


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    use_case: Annotated[CreateProjectUseCase, Depends(get_create_project_use_case)],
):
    dto = CreateProjectDTO(
        title=project_data.title,
        deadline=project_data.deadline,
    )
    return use_case.execute(dto)


@router.put("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    project_data: ProjectUpdate,
    use_case: Annotated[UpdateProjectUseCase, Depends(get_update_project_use_case)],
):
    dto = UpdateProjectDTO(
        title=project_data.title,
        deadline=project_data.deadline,
    )
    return use_case.execute(dto, project_id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: UUID,
    repo: Annotated[ProjectRepository, Depends(get_project_repository)],
):
    project = repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    repo.delete(project_id)


@router.post(
    "/{project_id}/tasks/{task_id}/link",
    response_model=TaskRead,
)
def link_task(
    project_id: UUID,
    task_id: UUID,
    use_case: Annotated[
        LinkTaskToProjectUseCase, Depends(get_link_task_to_project_use_case)
    ],
):
    return use_case.execute(task_id, project_id)


@router.delete(
    "/{project_id}/tasks/{task_id}/unlink",
    response_model=TaskRead,
)
def unlink_task(
    project_id: UUID,
    task_id: UUID,
    use_case: Annotated[
        UnlinkTaskToProjectUseCase, Depends(get_unlink_task_from_project_use_case)
    ],
):
    return use_case.execute(task_id, project_id)


@router.get("/{project_id}/tasks", response_model=list[TaskRead])
def retrieve_tasks(
    project_id: UUID,
    repo: Annotated[TaskRepository, Depends(get_task_repository)],
):
    return repo.get_by_project_id(project_id)
