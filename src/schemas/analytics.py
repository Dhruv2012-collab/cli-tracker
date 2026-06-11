from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class DailyStats(BaseModel):
    tasks_completed: int
    tasks_created: int
    pending_tasks: int
    total_focus_minutes: int
    avg_focus_duration: float
    current_habit_streaks: List[Dict[str, Any]]

class WeeklyStats(BaseModel):
    tasks_completed: int
    completion_percentage: float
    missed_deadlines: int
    most_productive_category: Optional[str]
    longest_focus_session: int
    total_focus_hours: float
    avg_daily_completion: float

class MonthlyStats(BaseModel):
    tasks_completed: int
    focus_hours: float
    top_categories: List[str]
    habit_completion_stats: List[Dict[str, Any]]

class DashboardStats(BaseModel):
    daily: DailyStats
    weekly: WeeklyStats
    active_goals: int # Number of non-completed tasks
