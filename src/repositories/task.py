from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.task import Task, TaskStatus
from src.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        stmt = select(Task).where(Task.user_id == user_id).options(selectinload(Task.focus_sessions)).offset(skip).limit(limit)
        return list(db.scalars(stmt).all())

    def get_by_status(self, db: Session, user_id: int, status: TaskStatus) -> List[Task]:
        stmt = select(Task).where(Task.user_id == user_id, Task.status == status)
        return list(db.scalars(stmt).all())

    def get_by_date_range(self, db: Session, user_id: int, start_date: date, end_date: date) -> List[Task]:
        stmt = select(Task).where(
            Task.user_id == user_id,
            Task.due_date >= start_date,
            Task.due_date <= end_date
        )
        return list(db.scalars(stmt).all())

task_repo = TaskRepository()
