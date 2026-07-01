"""My Tasks repository — search/filter/sort scoped to the owning teacher."""

from typing import List, Optional

from sqlalchemy import case

from data.models import TeacherTask
from data.repositories import BaseRepository

_PRIORITY_RANK = case(
    (TeacherTask.priority == "urgent", 4),
    (TeacherTask.priority == "high", 3),
    (TeacherTask.priority == "medium", 2),
    (TeacherTask.priority == "low", 1),
    else_=0,
)


class TeacherTaskRepository(BaseRepository[TeacherTask]):
    """Repository for My Tasks operations."""

    def search(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
    ) -> List[TeacherTask]:
        query = self.session.query(TeacherTask).filter(TeacherTask.user_id == user_id)

        if status:
            query = query.filter(TeacherTask.status == status)
        if priority:
            query = query.filter(TeacherTask.priority == priority)
        if category:
            query = query.filter(TeacherTask.category == category)
        if search:
            query = query.filter(TeacherTask.title.ilike(f"%{search}%"))

        if sort_by == "due_date":
            query = query.order_by(
                TeacherTask.due_date.is_(None), TeacherTask.due_date.asc()
            )
        elif sort_by == "priority":
            query = query.order_by(_PRIORITY_RANK.desc())
        else:
            query = query.order_by(TeacherTask.created_at.desc())

        return query.all()
