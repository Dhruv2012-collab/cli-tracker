from typing import List, Optional
from sqlalchemy.orm import Session
from src.repositories.habit import habit_repo
from src.schemas.habit import HabitCreate, HabitInDB
from src.config.logging import logger

class HabitService:
    def create_habit(self, db: Session, habit_in: HabitCreate) -> HabitInDB:
        existing = habit_repo.get_by_name(db, habit_in.user_id, habit_in.name)
        if existing:
            raise ValueError("Habit already exists")
        
        try:
            habit = habit_repo.create(db, habit_in.model_dump())
            return HabitInDB.model_validate(habit)
        except Exception:
            logger.exception("Failed to create habit")
            raise

    def get_user_habits(self, db: Session, user_id: int) -> List[HabitInDB]:
        habits = habit_repo.get_by_user_id(db, user_id)
        return [HabitInDB.model_validate(h) for h in habits]

    def mark_habit(self, db: Session, habit_id: int) -> Optional[HabitInDB]:
        habit = habit_repo.get(db, habit_id)
        if not habit:
            return None
        
        try:
            habit = habit_repo.update(db, habit, {"streak": habit.streak + 1})
            return HabitInDB.model_validate(habit)
        except Exception:
            logger.exception("Failed to mark habit")
            raise

habit_service = HabitService()
