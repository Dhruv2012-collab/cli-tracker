from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.models.focus_session import FocusSession
from src.repositories.base import BaseRepository


class FocusSessionRepository(BaseRepository[FocusSession]):
    def __init__(self):
        super().__init__(FocusSession)

    def get_by_task_id(self, db: Session, task_id: int) -> List[FocusSession]:
        stmt = select(FocusSession).options(selectinload(FocusSession.task)).where(FocusSession.task_id == task_id)
        return list(db.scalars(stmt).all())

    def get_active_session(self, db: Session, task_id: int) -> Optional[FocusSession]:
        stmt = select(FocusSession).options(selectinload(FocusSession.task)).where(
            FocusSession.task_id == task_id,
            FocusSession.end_time.is_(None)
        )
        return db.scalar(stmt)

focus_session_repo = FocusSessionRepository()
