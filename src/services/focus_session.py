from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from src.cli.utils import ActiveSessionExists
from src.config.logging import logger
from src.repositories.focus_session import focus_session_repo
from src.schemas.focus_session import FocusSessionCreate, FocusSessionInDB


class FocusService:
    def start_session(self, db: Session, task_id: int) -> FocusSessionInDB:
        active = focus_session_repo.get_active_session(db, task_id)
        if active:
            raise ActiveSessionExists("Task already has an active focus session")

        session_in = FocusSessionCreate(task_id=task_id, start_time=datetime.now())
        try:
            session = focus_session_repo.create(db, session_in.model_dump())
            return FocusSessionInDB.model_validate(session)
        except Exception as e:
            logger.exception("Failed to start focus session")
            raise e

    def stop_session(self, db: Session, task_id: int) -> Optional[FocusSessionInDB]:
        active = focus_session_repo.get_active_session(db, task_id)
        if not active:
            return None

        end_time = datetime.now()
        duration_delta = end_time - active.start_time
        duration_minutes = int(duration_delta.total_seconds() / 60)

        try:
            session = focus_session_repo.update(
                db, active, {"end_time": end_time, "duration": duration_minutes}
            )
            return FocusSessionInDB.model_validate(session)
        except Exception as e:
            logger.exception("Failed to stop focus session")
            raise e

focus_service = FocusService()
