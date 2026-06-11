from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class FocusSessionBase(BaseModel):
    task_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class FocusSessionCreate(FocusSessionBase):
    pass

class FocusSessionUpdate(BaseModel):
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class FocusSessionInDB(FocusSessionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
