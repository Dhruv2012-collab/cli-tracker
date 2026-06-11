from typing import List, Optional
from sqlalchemy.orm import Session
from src.repositories.task import task_repo
from src.schemas.task import TaskCreate, TaskUpdate, TaskInDB
from src.models.task import TaskStatus
from src.config.logging import logger

class TaskService:
    def create_task(self, db: Session, task_in: TaskCreate) -> TaskInDB:
        try:
            task = task_repo.create(db, task_in.model_dump())
            return TaskInDB.model_validate(task)
        except Exception as e:
            logger.exception("Failed to create task")
            raise

    def get_user_tasks(self, db: Session, user_id: int) -> List[TaskInDB]:
        tasks = task_repo.get_by_user_id(db, user_id)
        return [TaskInDB.model_validate(t) for t in tasks]

    def update_task(self, db: Session, task_id: int, task_in: TaskUpdate) -> Optional[TaskInDB]:
        task = task_repo.get(db, task_id)
        if not task:
            return None
        updated_data = task_in.model_dump(exclude_unset=True)
        try:
            task = task_repo.update(db, task, updated_data)
            return TaskInDB.model_validate(task)
        except Exception as e:
            logger.exception("Failed to update task")
            raise

    def delete_task(self, db: Session, task_id: int) -> bool:
        try:
            return task_repo.delete(db, task_id)
        except Exception as e:
            logger.exception("Failed to delete task")
            raise

    def mark_complete(self, db: Session, task_id: int) -> Optional[TaskInDB]:
        task = task_repo.get(db, task_id)
        if not task:
            return None
        try:
            task = task_repo.update(db, task, {"status": TaskStatus.COMPLETED})
            return TaskInDB.model_validate(task)
        except Exception as e:
            logger.exception("Failed to mark task complete")
            raise

task_service = TaskService()
