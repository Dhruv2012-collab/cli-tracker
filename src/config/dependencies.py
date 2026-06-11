from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import Session

from src.config.database import SessionLocal
from src.services.focus_session import focus_service
from src.services.habit import habit_service
from src.services.task import task_service
from src.services.user import user_service


@contextmanager
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service():
    return user_service

def get_task_service():
    return task_service

def get_focus_service():
    return focus_service

def get_habit_service():
    return habit_service

def get_analytics_service():
    from src.services.analytics import analytics_service
    return analytics_service
