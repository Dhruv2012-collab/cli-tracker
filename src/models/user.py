from typing import List
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.core import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    tasks: Mapped[List["Task"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    habits: Mapped[List["Habit"]] = relationship(back_populates="user", cascade="all, delete-orphan")
