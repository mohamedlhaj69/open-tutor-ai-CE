"""My Tasks service — CRUD, ownership enforcement, and quick complete/reopen.

Every task is private to the teacher who created it; every read/write is
scoped to `user_id` and ownership is verified before mutation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from common.exceptions import AuthorizationError, NotFoundError, ValidationError
from data.models import TeacherTask
from learning.teacher_tasks.repository import TeacherTaskRepository

VALID_STATUSES = {"todo", "in_progress", "completed"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_CATEGORIES = {"teaching", "assessment", "administration", "meetings", "personal"}
VALID_SORT_FIELDS = {"due_date", "created_at", "priority"}


class TeacherTaskService:
    """Service for My Tasks operations."""

    def __init__(self, session: Session):
        self.repo = TeacherTaskRepository(session, TeacherTask)

    def list_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> List[TeacherTask]:
        if sort_by not in VALID_SORT_FIELDS:
            raise ValidationError(f"Invalid sort field: {sort_by}", field="sort_by")
        return self.repo.search(
            user_id,
            status=status,
            priority=priority,
            category=category,
            search=search,
            sort_by=sort_by,
        )

    def create(self, user_id: str, data: Dict[str, Any]) -> TeacherTask:
        priority = data.get("priority") or "medium"
        category = data.get("category") or "personal"
        if priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority: {priority}", field="priority")
        if category not in VALID_CATEGORIES:
            raise ValidationError(f"Invalid category: {category}", field="category")
        return self.repo.create(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=data["title"],
            description=data.get("description"),
            status="todo",
            priority=priority,
            category=category,
            due_date=data.get("due_date"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

    def get_owned(self, user_id: str, task_id: str) -> TeacherTask:
        task = self.repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("TeacherTask", task_id)
        if task.user_id != user_id:
            raise AuthorizationError("You do not own this task")
        return task

    def update(self, user_id: str, task_id: str, data: Dict[str, Any]) -> TeacherTask:
        self.get_owned(user_id, task_id)

        status = data.get("status")
        priority = data.get("priority")
        category = data.get("category")
        if status is not None and status not in VALID_STATUSES:
            raise ValidationError(f"Invalid status: {status}", field="status")
        if priority is not None and priority not in VALID_PRIORITIES:
            raise ValidationError(f"Invalid priority: {priority}", field="priority")
        if category is not None and category not in VALID_CATEGORIES:
            raise ValidationError(f"Invalid category: {category}", field="category")

        fields = {k: v for k, v in data.items() if v is not None}
        fields["updated_at"] = datetime.utcnow()
        return self.repo.update(task_id, **fields)

    def set_status(self, user_id: str, task_id: str, status: str) -> TeacherTask:
        self.get_owned(user_id, task_id)
        return self.repo.update(task_id, status=status, updated_at=datetime.utcnow())

    def delete(self, user_id: str, task_id: str) -> None:
        self.get_owned(user_id, task_id)
        self.repo.delete(task_id)
