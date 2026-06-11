from pydantic import BaseModel, ConfigDict
from datetime import datetime

class HabitBase(BaseModel):
    name: str

class HabitCreate(HabitBase):
    user_id: int

class HabitUpdate(BaseModel):
    streak: int

class HabitInDB(HabitBase):
    id: int
    user_id: int
    streak: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
