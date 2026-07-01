"""My Tasks router — /teacher-tasks/* (standalone teacher task manager).

Distinct prefix from the existing /tasks/* router, which serves unrelated
LLM task helpers (title/tag/emoji completions).
"""

from datetime import datetime
from typing import Annotated, List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from common.exceptions import AuthorizationError, NotFoundError, ValidationError
from data.models import User
from gateway.http.dependencies import get_current_user, get_teacher_task_service
from learning.teacher_tasks.service import TeacherTaskService

router = APIRouter(prefix="/teacher-tasks", tags=["teacher-tasks"])

CurrentUserDep = Annotated[User, Depends(get_current_user)]
TeacherTaskServiceDep = Annotated[TeacherTaskService, Depends(get_teacher_task_service)]

Status = Literal["todo", "in_progress", "completed"]
Priority = Literal["low", "medium", "high", "urgent"]
Category = Literal["teaching", "assessment", "administration", "meetings", "personal"]
SortBy = Literal["due_date", "created_at", "priority"]


def _raise_for(exc: Exception) -> None:
    if isinstance(exc, NotFoundError):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)
    if isinstance(exc, AuthorizationError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=exc.message)
    if isinstance(exc, ValidationError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)
    raise exc


class TeacherTaskCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Priority = "medium"
    category: Category = "personal"
    due_date: Optional[datetime] = None


class TeacherTaskUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    category: Optional[Category] = None
    due_date: Optional[datetime] = None


class TeacherTaskResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    category: str
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("", response_model=List[TeacherTaskResponse])
def list_tasks(
    current_user: CurrentUserDep,
    svc: TeacherTaskServiceDep,
    status: Optional[Status] = Query(None),
    priority: Optional[Priority] = Query(None),
    category: Optional[Category] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: SortBy = Query("created_at"),
):
    return svc.list_for_user(
        current_user.id,
        status=status,
        priority=priority,
        category=category,
        search=search,
        sort_by=sort_by,
    )


@router.post("", response_model=TeacherTaskResponse)
def create_task(
    data: TeacherTaskCreateRequest, current_user: CurrentUserDep, svc: TeacherTaskServiceDep
):
    return svc.create(current_user.id, data.model_dump())


@router.get("/{task_id}", response_model=TeacherTaskResponse)
def get_task(task_id: str, current_user: CurrentUserDep, svc: TeacherTaskServiceDep):
    try:
        return svc.get_owned(current_user.id, task_id)
    except (NotFoundError, AuthorizationError) as exc:
        _raise_for(exc)


@router.patch("/{task_id}", response_model=TeacherTaskResponse)
def update_task(
    task_id: str,
    data: TeacherTaskUpdateRequest,
    current_user: CurrentUserDep,
    svc: TeacherTaskServiceDep,
):
    try:
        return svc.update(current_user.id, task_id, data.model_dump(exclude_unset=True))
    except (NotFoundError, AuthorizationError, ValidationError) as exc:
        _raise_for(exc)


@router.delete("/{task_id}")
def delete_task(task_id: str, current_user: CurrentUserDep, svc: TeacherTaskServiceDep):
    try:
        svc.delete(current_user.id, task_id)
    except (NotFoundError, AuthorizationError) as exc:
        _raise_for(exc)
    return {"status": "success"}


@router.post("/{task_id}/complete", response_model=TeacherTaskResponse)
def complete_task(task_id: str, current_user: CurrentUserDep, svc: TeacherTaskServiceDep):
    try:
        return svc.set_status(current_user.id, task_id, "completed")
    except (NotFoundError, AuthorizationError) as exc:
        _raise_for(exc)


@router.post("/{task_id}/reopen", response_model=TeacherTaskResponse)
def reopen_task(task_id: str, current_user: CurrentUserDep, svc: TeacherTaskServiceDep):
    try:
        return svc.set_status(current_user.id, task_id, "todo")
    except (NotFoundError, AuthorizationError) as exc:
        _raise_for(exc)
