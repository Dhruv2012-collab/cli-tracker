from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.models.habit import Habit
from src.repositories.base import BaseRepository

class HabitRepository(BaseRepository[Habit]):
    def __init__(self):
        super().__init__(Habit)

    def get_by_user_id(self, db: Session, user_id: int) -> List[Habit]:
        stmt = select(Habit).options(selectinload(Habit.user)).where(Habit.user_id == user_id)
        return list(db.scalars(stmt).all())

    def get_by_name(self, db: Session, user_id: int, name: str) -> Optional[Habit]:
        stmt = select(Habit).where(Habit.user_id == user_id, Habit.name == name)
        return db.scalar(stmt)

habit_repo = HabitRepository()
