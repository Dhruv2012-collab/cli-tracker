from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
from src.models.task import TaskStatus, TaskPriority

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    category: Optional[str] = None
    due_date: Optional[date] = None

class TaskCreate(TaskBase):
    user_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category: Optional[str] = None
    due_date: Optional[date] = None

class TaskInDB(TaskBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
