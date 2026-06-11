from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_, desc

from src.models.task import Task, TaskStatus
from src.models.focus_session import FocusSession
from src.models.habit import Habit
from src.repositories.base import BaseRepository

class AnalyticsRepository(BaseRepository[Task]):
    def __init__(self):
        super().__init__(Task)

    def get_task_count_by_date_and_status(
        self, db: Session, user_id: int, target_date: date, status: Optional[TaskStatus] = None
    ) -> int:
        """Count tasks created/completed on a specific date."""
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            func.date(Task.created_at) == target_date
        )
        if status:
            query = query.where(Task.status == status)
        return db.scalar(query) or 0
        
    def get_completed_tasks_in_range(self, db: Session, user_id: int, start: datetime, end: datetime) -> int:
        """Count tasks completed within a datetime range (using updated_at as proxy for completion time)."""
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.COMPLETED,
            Task.updated_at >= start,
            Task.updated_at <= end
        )
        return db.scalar(query) or 0

    def get_total_tasks_in_range(self, db: Session, user_id: int, start: datetime, end: datetime) -> int:
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.created_at >= start,
            Task.created_at <= end
        )
        return db.scalar(query) or 0

    def get_pending_tasks_count(self, db: Session, user_id: int) -> int:
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status != TaskStatus.COMPLETED
        )
        return db.scalar(query) or 0

    def get_focus_stats_in_range(self, db: Session, user_id: int, start: datetime, end: datetime) -> Dict[str, Any]:
        """Aggregate focus session stats for a date range."""
        query = select(
            func.sum(FocusSession.duration).label("total_duration"),
            func.avg(FocusSession.duration).label("avg_duration"),
            func.max(FocusSession.duration).label("max_duration")
        ).join(Task).where(
            Task.user_id == user_id,
            FocusSession.start_time >= start,
            FocusSession.start_time <= end,
            FocusSession.duration.is_not(None)
        )
        result = db.execute(query).first()
        return {
            "total": result.total_duration or 0,
            "avg": float(result.avg_duration or 0),
            "max": result.max_duration or 0
        }

    def get_missed_deadlines(self, db: Session, user_id: int, target_date: date) -> int:
        query = select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.status != TaskStatus.COMPLETED,
            Task.due_date < target_date
        )
        return db.scalar(query) or 0

    def get_most_productive_category(self, db: Session, user_id: int, start: datetime, end: datetime) -> Optional[str]:
        query = select(
            Task.category,
            func.count(Task.id).label('completed_count')
        ).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.COMPLETED,
            Task.updated_at >= start,
            Task.updated_at <= end,
            Task.category.is_not(None)
        ).group_by(Task.category).order_by(desc('completed_count')).limit(1)
        
        result = db.execute(query).first()
        return result.category if result else None
        
    def get_top_categories(self, db: Session, user_id: int, start: datetime, end: datetime, limit: int = 3) -> List[str]:
        query = select(
            Task.category
        ).where(
            Task.user_id == user_id,
            Task.status == TaskStatus.COMPLETED,
            Task.updated_at >= start,
            Task.updated_at <= end,
            Task.category.is_not(None)
        ).group_by(Task.category).order_by(desc(func.count(Task.id))).limit(limit)
        
        return list(db.scalars(query).all())

analytics_repo = AnalyticsRepository()
