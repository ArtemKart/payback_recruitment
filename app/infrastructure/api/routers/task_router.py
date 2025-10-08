from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.application.use_cases.task_use_cases.reopen_task import ReopenTaskUseCase
from app.application.use_cases.task_use_cases.update_task import UpdateTaskUseCase
from app.domain.repositories.task_repository import TaskRepository
from app.infrastructure.api.schemas.task_schemas import (
    TaskCreate,
    TaskRead,
    TaskUpdate,
)
from app.infrastructure.api.dependencies import (
    get_create_task_use_case,
    get_complete_task_use_case,
    get_filtered_tasks_use_case,
    get_task_repository,
    get_update_task_use_case,
    get_reopen_task_use_case,
)
from app.application.use_cases.task_use_cases.create_task import CreateTaskUseCase
from app.application.use_cases.task_use_cases.complete_task import CompleteTaskUseCase
from app.application.use_cases.task_use_cases.get_filtered_tasks import (
    GetFilteredTasksUseCase,
)
from app.application.dto.task_dto import CreateTaskDTO, TaskFilterDTO, UpdateTaskDTO

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskRead])
async def get_tasks(
    use_case: Annotated[GetFilteredTasksUseCase, Depends(get_filtered_tasks_use_case)],
    is_completed: bool | None = Query(None),
    is_overdue: bool | None = Query(None),
    project_id: UUID | None = Query(None),
):
    filters = TaskFilterDTO(
        is_completed=is_completed, is_overdue=is_overdue, project_id=project_id
    )
    return use_case.execute(filters)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: UUID, repo: Annotated[TaskRepository, Depends(get_task_repository)]
):
    task = repo.get_by_id(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: TaskCreate,
    use_case: Annotated[CreateTaskUseCase, Depends(get_create_task_use_case)],
):
    dto = CreateTaskDTO(
        title=request.title,
        description=request.description,
        deadline=request.deadline,
    )
    return use_case.execute(dto=dto)


@router.put("/{task_id}", response_model=TaskRead)
async def update_existing_task(
    task_id: UUID,
    task: TaskUpdate,
    use_case: Annotated[UpdateTaskUseCase, Depends(get_update_task_use_case)],
):
    dto = UpdateTaskDTO(
        title=task.title,
        description=task.description,
        deadline=task.deadline,
    )
    return use_case.execute(dto, task_id)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID, repo: Annotated[TaskRepository, Depends(get_task_repository)]
):
    task = repo.get_by_id(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    repo.delete(task_id)


@router.patch("/{task_id}/complete", response_model=TaskRead)
async def complete_task(
    task_id: UUID,
    use_case: Annotated[CompleteTaskUseCase, Depends(get_complete_task_use_case)],
):
    return use_case.execute(task_id=task_id)


@router.patch("/{task_id}/reopen", response_model=TaskRead)
async def reopen_task(
    task_id: UUID,
    use_case: Annotated[ReopenTaskUseCase, Depends(get_reopen_task_use_case)],
):
    return use_case.execute(task_id=task_id)
