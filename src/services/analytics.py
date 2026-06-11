import csv
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from src.config.logging import logger
from src.repositories.analytics import analytics_repo
from src.repositories.focus_session import focus_session_repo
from src.repositories.habit import habit_repo
from src.repositories.task import task_repo
from src.schemas.analytics import DailyStats, DashboardStats, MonthlyStats, WeeklyStats


class AnalyticsService:
    def get_daily_stats(self, db: Session, user_id: int) -> DailyStats:
        try:
            today = datetime.now().date()
            start_of_day = datetime.combine(today, datetime.min.time())
            end_of_day = datetime.combine(today, datetime.max.time())

            created = analytics_repo.get_total_tasks_in_range(db, user_id, start_of_day, end_of_day)
            completed = analytics_repo.get_completed_tasks_in_range(db, user_id, start_of_day, end_of_day)
            pending = analytics_repo.get_pending_tasks_count(db, user_id)
            focus = analytics_repo.get_focus_stats_in_range(db, user_id, start_of_day, end_of_day)
            habits = habit_repo.get_by_user_id(db, user_id)

            return DailyStats(
                tasks_completed=completed,
                tasks_created=created,
                pending_tasks=pending,
                total_focus_minutes=focus["total"],
                avg_focus_duration=focus["avg"],
                current_habit_streaks=[{"name": h.name, "streak": h.streak} for h in habits]
            )
        except Exception:
            logger.exception("Failed to get daily stats")
            raise

    def get_weekly_stats(self, db: Session, user_id: int) -> WeeklyStats:
        try:
            today = datetime.now().date()
            start_of_week = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
            end_of_week = datetime.combine(today + timedelta(days=6-today.weekday()), datetime.max.time())

            completed = analytics_repo.get_completed_tasks_in_range(db, user_id, start_of_week, end_of_week)
            total = analytics_repo.get_total_tasks_in_range(db, user_id, start_of_week, end_of_week)
            focus = analytics_repo.get_focus_stats_in_range(db, user_id, start_of_week, end_of_week)
            missed = analytics_repo.get_missed_deadlines(db, user_id, today)
            top_cat = analytics_repo.get_most_productive_category(db, user_id, start_of_week, end_of_week)

            completion_pct = (completed / total * 100) if total > 0 else 0.0

            return WeeklyStats(
                tasks_completed=completed,
                completion_percentage=completion_pct,
                missed_deadlines=missed,
                most_productive_category=top_cat,
                longest_focus_session=focus["max"],
                total_focus_hours=focus["total"] / 60.0,
                avg_daily_completion=completed / 7.0
            )
        except Exception:
            logger.exception("Failed to get weekly stats")
            raise

    def get_monthly_stats(self, db: Session, user_id: int) -> MonthlyStats:
        try:
            today = datetime.now().date()
            start_of_month = datetime.combine(today.replace(day=1), datetime.min.time())

            # naive end of month (approx 31 days)
            next_month = today.replace(day=28) + timedelta(days=4)
            end_of_month = datetime.combine(next_month - timedelta(days=next_month.day), datetime.max.time())

            completed = analytics_repo.get_completed_tasks_in_range(db, user_id, start_of_month, end_of_month)
            focus = analytics_repo.get_focus_stats_in_range(db, user_id, start_of_month, end_of_month)
            top_cats = analytics_repo.get_top_categories(db, user_id, start_of_month, end_of_month, 3)
            habits = habit_repo.get_by_user_id(db, user_id)

            return MonthlyStats(
                tasks_completed=completed,
                focus_hours=focus["total"] / 60.0,
                top_categories=top_cats,
                habit_completion_stats=[{"name": h.name, "streak": h.streak} for h in habits]
            )
        except Exception:
            logger.exception("Failed to get monthly stats")
            raise

    def get_dashboard_stats(self, db: Session, user_id: int) -> DashboardStats:
        try:
            daily = self.get_daily_stats(db, user_id)
            weekly = self.get_weekly_stats(db, user_id)

            return DashboardStats(
                daily=daily,
                weekly=weekly,
                active_goals=daily.pending_tasks
            )
        except Exception:
            logger.exception("Failed to get dashboard stats")
            raise

    def export_data(self, db: Session, user_id: int, format_type: str, out_dir: Optional[str] = None):
        try:
            out_dir = out_dir or "."
            os.makedirs(out_dir, exist_ok=True)

            tasks = task_repo.get_by_user_id(db, user_id)
            habits = habit_repo.get_by_user_id(db, user_id)

            # Fetch all focus sessions for user's tasks
            task_ids = [t.id for t in tasks]
            focus_sessions = []
            for tid in task_ids:
                focus_sessions.extend(focus_session_repo.get_by_task_id(db, tid))

            data = {
                "tasks": [{"id": t.id, "title": t.title, "status": t.status.value, "priority": t.priority.value, "category": t.category, "due_date": str(t.due_date)} for t in tasks],
                "habits": [{"id": h.id, "name": h.name, "streak": h.streak} for h in habits],
                "focus_sessions": [{"id": fs.id, "task_id": fs.task_id, "duration": fs.duration, "start_time": str(fs.start_time)} for fs in focus_sessions]
            }

            if format_type.lower() == "json":
                path = os.path.join(out_dir, "export.json")
                with open(path, "w") as f:
                    json.dump(data, f, indent=2)
                return path
            elif format_type.lower() == "csv":
                tasks_path = os.path.join(out_dir, "tasks.csv")
                habits_path = os.path.join(out_dir, "habits.csv")

                with open(tasks_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "title", "status", "priority", "category", "due_date"])
                    writer.writeheader()
                    writer.writerows(data["tasks"])

                with open(habits_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "name", "streak"])
                    writer.writeheader()
                    writer.writerows(data["habits"])

                return out_dir
            else:
                raise ValueError("Unsupported format type")
        except Exception:
            logger.exception("Failed to export data")
            raise

analytics_service = AnalyticsService()
